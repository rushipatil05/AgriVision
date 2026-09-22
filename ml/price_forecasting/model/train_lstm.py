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
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler

from ml.price_forecasting.preprocessing import (
    load_and_clean_price_data,
    prepare_commodity_timeseries,
    create_sliding_windows,
    chronological_split
)
from ml.price_forecasting.model.lstm_model import build_price_lstm_model
from ml.price_forecasting.model.model_utils import (
    set_seed,
    compute_forecast_metrics,
    plot_forecast_timeline,
    plot_test_forecast_zoom,
    plot_residual_diagnostics
)
from ml.price_forecasting.config import (
    COL_MODAL_PRICE,
    SEQUENCE_LENGTH,
    FORECAST_HORIZON,
    TRAIN_RATIO,
    VAL_RATIO
)
from ml.common.paths import PRICE_DIR

MODEL_DIR = PRICE_DIR / "model"
RESULTS_DIR = PRICE_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
METRICS_DIR = RESULTS_DIR / "metrics"


def train_price_lstm_model(
    commodity: str = "Onion",
    epochs: int = 150,
    batch_size: int = 32,
    learning_rate: float = 0.001
) -> Dict[str, Any]:
    """
    Trains the Crop Market Price Forecasting LSTM Neural Network with strict temporal
    isolation, callbacks for regularization, artifact serialization, and evaluation.
    """
    set_seed(42)
    print("=" * 65)
    print(f"  TRAINING TIME-SERIES LSTM PRICE FORECASTER FOR {commodity.upper()}")
    print("=" * 65)
    
    # 1. Load dataset & prepare continuous daily series
    df_clean = load_and_clean_price_data()
    ts = prepare_commodity_timeseries(df_clean, commodity=commodity)
    print(f"Continuous Timeline: {len(ts)} daily points ({ts['date'].min().date()} to {ts['date'].max().date()})")
    
    # 2. Scaler fitted ONLY on the training period (Prevent temporal leakage)
    n_train_pts = int(len(ts) * TRAIN_RATIO)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(ts[[COL_MODAL_PRICE]].values[:n_train_pts])
    
    # Scale series & create sliding window sequences
    raw_prices = ts[[COL_MODAL_PRICE]].values
    scaled_series = scaler.transform(raw_prices)
    X, y = create_sliding_windows(scaled_series, seq_length=SEQUENCE_LENGTH, horizon=FORECAST_HORIZON)
    
    # Strictly chronological split (No random shuffle)
    X_train, X_val, X_test, y_train, y_val, y_test = chronological_split(X, y)
    
    print(f"Sequence Windows (Length={SEQUENCE_LENGTH}) -> Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # 3. Instantiate Architecture
    model = build_price_lstm_model(
        input_shape=(SEQUENCE_LENGTH, 1),
        lstm_units=64,
        dense_units=32,
        dropout_rate=0.2,
        learning_rate=learning_rate
    )
    model.summary()
    
    # 4. Configure Callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=20,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=7,
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
    print(f"\nLSTM Training completed in {training_duration}s ({len(history.epoch)} epochs).")
    
    # 6. Predict on all splits & inverse transform to real currency scale (INR/Quintal)
    train_preds_scaled = model.predict(X_train)
    val_preds_scaled = model.predict(X_val)
    test_preds_scaled = model.predict(X_test)
    
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_val_actual = scaler.inverse_transform(y_val.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    y_train_pred = scaler.inverse_transform(train_preds_scaled)
    y_val_pred = scaler.inverse_transform(val_preds_scaled)
    y_test_pred = scaler.inverse_transform(test_preds_scaled)
    
    # 7. Compute Metrics
    train_metrics = compute_forecast_metrics(y_train_actual, y_train_pred, f"LSTM (Train - {commodity})")
    val_metrics = compute_forecast_metrics(y_val_actual, y_val_pred, f"LSTM (Validation - {commodity})")
    test_metrics = compute_forecast_metrics(y_test_actual, y_test_pred, f"LSTM (Test - {commodity})")
    
    print("\n" + "-" * 60)
    print(f"LSTM Validation: MAE = INR {val_metrics['mae']:.2f}/Qtl | RMSE = INR {val_metrics['rmse']:.2f} | MAPE = {val_metrics['mape']:.2f}% | R2 = {val_metrics['r2_score']:.4f}")
    print(f"LSTM Test:       MAE = INR {test_metrics['mae']:.2f}/Qtl | RMSE = INR {test_metrics['rmse']:.2f} | MAPE = {test_metrics['mape']:.2f}% | R2 = {test_metrics['r2_score']:.4f}")
    print("-" * 60)
    
    # 8. Generate & Save Visualizations
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Plot 1: Training Loss Curve
    plt.figure(figsize=(9, 4.5))
    plt.plot(history.history["loss"], label="Training Loss (MSE)", color="#2563eb", linewidth=2)
    plt.plot(history.history["val_loss"], label="Validation Loss (MSE)", color="#ea580c", linewidth=2)
    plt.title(f"LSTM Price Forecaster: Training vs Validation Loss ({commodity})", fontsize=12, fontweight="bold")
    plt.xlabel("Epoch", fontsize=10)
    plt.ylabel("Loss (MSE on Scaled Prices)", fontsize=10)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    curves_plot_path = PLOTS_DIR / "lstm_training_curves.png"
    plt.savefig(curves_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {curves_plot_path.name}")
    
    # Plot 2: Full Timeline Actual vs Forecast
    timeline_plot_path = PLOTS_DIR / "actual_vs_predicted_all_splits.png"
    plot_forecast_timeline(
        dates=ts["date"],
        y_true_full=raw_prices.ravel(),
        train_size=len(X_train),
        val_size=len(X_val),
        y_train_pred=y_train_pred.ravel(),
        y_val_pred=y_val_pred.ravel(),
        y_test_pred=y_test_pred.ravel(),
        seq_length=SEQUENCE_LENGTH,
        commodity=commodity,
        output_path=timeline_plot_path
    )
    
    # Plot 3: Out-of-sample Test Forecast Zoom
    test_dates = ts["date"].iloc[SEQUENCE_LENGTH + len(X_train) + len(X_val):].reset_index(drop=True)
    test_zoom_path = PLOTS_DIR / "test_forecast_vs_actual.png"
    plot_test_forecast_zoom(
        test_dates=test_dates,
        y_test_true=y_test_actual.ravel(),
        y_test_pred=y_test_pred.ravel(),
        commodity=commodity,
        output_path=test_zoom_path
    )
    
    # Plot 4: Residual Diagnostics
    residuals_path = PLOTS_DIR / "residual_analysis.png"
    plot_residual_diagnostics(
        y_true=y_test_actual,
        y_pred=y_test_pred,
        commodity=commodity,
        output_path=residuals_path
    )
    
    # 9. Save Model & Scaler Artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_save_path = MODEL_DIR / "crop_price_lstm.keras"
    model.save(model_save_path)
    print(f"Saved Keras model to: {model_save_path.name}")
    
    scaler_path = MODEL_DIR / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"Saved fitted MinMaxScaler to: {scaler_path.name}")
    
    metadata = {
        "model_type": "LSTM_Time_Series",
        "keras_version": tf.keras.__version__,
        "tensorflow_version": tf.__version__,
        "commodity": commodity,
        "sequence_length": SEQUENCE_LENGTH,
        "forecast_horizon": FORECAST_HORIZON,
        "total_days_in_series": len(ts),
        "date_range": {
            "start": str(ts["date"].min().date()),
            "end": str(ts["date"].max().date())
        },
        "splits": {
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test)
        },
        "epochs_trained": len(history.epoch),
        "training_time_seconds": training_duration,
        "hyperparameters": {
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "lstm_units": 64,
            "dense_units": 32,
            "dropout_rate": 0.2
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
    
    # Save test metrics JSON to results
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    lstm_metrics_path = METRICS_DIR / "lstm_metrics.json"
    with open(lstm_metrics_path, "w") as f:
        json.dump(metadata["metrics"], f, indent=2)
        
    return metadata


if __name__ == "__main__":
    train_price_lstm_model()
