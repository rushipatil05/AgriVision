import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
import json
from typing import Dict, Any
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from ml.yield_forecasting.preprocessing import (
    load_and_clean_yield_data,
    prepare_yield_splits,
    build_and_fit_preprocessor,
    FEATURE_COLUMNS,
    COL_YIELD,
    BENCHMARK_CROPS
)
from ml.yield_forecasting.model.deep_model import build_yield_deep_model
from ml.yield_forecasting.model.model_utils import (
    set_seed,
    compute_regression_metrics,
    plot_actual_vs_predicted,
    plot_residual_diagnostics,
    plot_crop_level_performance,
    plot_state_level_performance
)
from ml.common.paths import YIELD_DIR

MODEL_DIR = YIELD_DIR / "model"
RESULTS_DIR = YIELD_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
METRICS_DIR = RESULTS_DIR / "metrics"


def train_yield_deep_model(
    epochs: int = 100,
    batch_size: int = 64,
    learning_rate: float = 0.001
) -> Dict[str, Any]:
    """
    Trains the Deep Neural Network Regressor for Crop Yield Forecasting with strict
    chronological validation, regularization, diagnostic visualizations, and artifact persistence.
    """
    set_seed(42)
    print("=" * 65)
    print("  TRAINING DEEP NEURAL NETWORK FOR CROP YIELD FORECASTING")
    print("=" * 65)
    
    # 1. Load data & chronological partitions
    df_clean = load_and_clean_yield_data()
    train_df, val_df, test_df = prepare_yield_splits(df_clean)
    
    print(f"Partitions -> Train (<=2011): {len(train_df):,}, Val (2012-2013): {len(val_df):,}, Test (>=2014): {len(test_df):,}")
    
    # 2. Fit preprocessor ONLY on training data (Zero temporal leakage)
    preprocessor = build_and_fit_preprocessor(train_df)
    
    X_train = preprocessor.transform(train_df[FEATURE_COLUMNS])
    X_val = preprocessor.transform(val_df[FEATURE_COLUMNS])
    X_test = preprocessor.transform(test_df[FEATURE_COLUMNS])
    
    y_train = train_df[COL_YIELD].values
    y_val = val_df[COL_YIELD].values
    y_test = test_df[COL_YIELD].values
    
    input_dim = X_train.shape[1]
    print(f"Feature Dimension: {input_dim} columns (Production excluded from inputs)")
    
    # 3. Instantiate DNN Architecture
    model = build_yield_deep_model(
        input_dim=input_dim,
        dense_units_1=128,
        dense_units_2=64,
        dense_units_3=32,
        dropout_rate=0.20,
        learning_rate=learning_rate
    )
    model.summary()
    
    # 4. Configure Callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-5,
            verbose=1
        )
    ]
    
    # 5. Train Model
    start_time = time.time()
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    training_duration = round(time.time() - start_time, 2)
    print(f"\nDNN Training completed in {training_duration}s ({len(history.epoch)} epochs).")
    
    # 6. Predict on all splits
    train_preds = model.predict(X_train).ravel()
    val_preds = model.predict(X_val).ravel()
    test_preds = model.predict(X_test).ravel()
    
    # 7. Compute Metrics
    train_metrics = compute_regression_metrics(y_train, train_preds, "Deep Neural Network (Train)")
    val_metrics = compute_regression_metrics(y_val, val_preds, "Deep Neural Network (Validation)")
    test_metrics = compute_regression_metrics(y_test, test_preds, "Deep Neural Network (Test)")
    
    print("\n" + "-" * 60)
    print(f"DNN Validation: MAE = {val_metrics['mae']:.3f} Tonnes/ha | RMSE = {val_metrics['rmse']:.3f} | R2 = {val_metrics['r2_score']:.4f} | MedAE = {val_metrics['medae']:.3f}")
    print(f"DNN Test:       MAE = {test_metrics['mae']:.3f} Tonnes/ha | RMSE = {test_metrics['rmse']:.3f} | R2 = {test_metrics['r2_score']:.4f} | MedAE = {test_metrics['medae']:.3f}")
    print("-" * 60)
    
    # 8. Generate & Save Diagnostic Plots
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Plot 1: Training & Validation Loss Curves
    plt.figure(figsize=(9, 4.5))
    plt.plot(history.history["loss"], label="Training Loss (MSE)", color="#2563eb", linewidth=2)
    plt.plot(history.history["val_loss"], label="Validation Loss (MSE)", color="#ea580c", linewidth=2)
    plt.title("Deep Neural Network: Training vs Validation Loss (Yield Forecasting)", fontsize=12, fontweight="bold")
    plt.xlabel("Epoch", fontsize=10)
    plt.ylabel("Loss (Mean Squared Error)", fontsize=10)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    loss_plot_path = PLOTS_DIR / "deep_training_curves.png"
    plt.savefig(loss_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {loss_plot_path.name}")
    
    # Plot 2: Actual vs Predicted Yield Scatter
    act_pred_plot_path = PLOTS_DIR / "actual_vs_predicted.png"
    plot_actual_vs_predicted(y_test, test_preds, "Deep Neural Network (Test Set)", act_pred_plot_path)
    
    # Plot 3: Residual Diagnostics
    residuals_plot_path = PLOTS_DIR / "residual_diagnostics.png"
    plot_residual_diagnostics(y_test, test_preds, "DNN", residuals_plot_path)
    
    # Plot 4: Empirical Yield Distribution
    plt.figure(figsize=(9, 4.5))
    sns.histplot(df_clean[COL_YIELD], bins=50, kde=True, color="#059669")
    plt.title("Empirical Distribution of Agricultural Crop Yield (Tonnes / Hectare)", fontsize=12, fontweight="bold")
    plt.xlabel("Yield (Tonnes / Hectare)", fontsize=10)
    plt.ylabel("Count", fontsize=10)
    plt.xlim(0, 100)
    plt.tight_layout()
    dist_plot_path = PLOTS_DIR / "yield_distribution.png"
    plt.savefig(dist_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {dist_plot_path.name}")
    
    # Plot 5: Crop-Level Performance
    crop_perf_plot_path = PLOTS_DIR / "crop_level_performance.png"
    plot_crop_level_performance(test_df, test_preds, crop_perf_plot_path)
    
    # Plot 6: State-Level Performance
    state_perf_plot_path = PLOTS_DIR / "state_level_performance.png"
    plot_state_level_performance(test_df, test_preds, state_perf_plot_path)
    
    # 9. Save Artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_save_path = MODEL_DIR / "crop_yield_dnn.keras"
    model.save(model_save_path)
    print(f"Saved Keras deep model to: {model_save_path.name}")
    
    preprocessor_path = MODEL_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"Saved fitted ColumnTransformer to: {preprocessor_path.name}")
    
    metadata = {
        "model_type": "Deep_Neural_Network_Regressor",
        "keras_version": tf.keras.__version__,
        "tensorflow_version": tf.__version__,
        "features": FEATURE_COLUMNS,
        "leakage_check_production_excluded": True,
        "benchmark_crops": BENCHMARK_CROPS,
        "total_cleaned_records": len(df_clean),
        "splits": {
            "train_records": len(train_df),
            "val_records": len(val_df),
            "test_records": len(test_df)
        },
        "encoded_feature_dimensions": input_dim,
        "epochs_trained": len(history.epoch),
        "training_time_seconds": training_duration,
        "hyperparameters": {
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "dense_units": [128, 64, 32],
            "dropout_rate": 0.20
        },
        "metrics": {
            "train": train_metrics,
            "validation": val_metrics,
            "test": test_metrics
        }
    }
    
    metadata_path = MODEL_DIR / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to: {metadata_path.name}")
    
    # Save deep metrics JSON
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    deep_metrics_path = METRICS_DIR / "deep_model_metrics.json"
    with open(deep_metrics_path, "w") as f:
        json.dump(metadata["metrics"], f, indent=2)
        
    return metadata


if __name__ == "__main__":
    train_yield_deep_model()
