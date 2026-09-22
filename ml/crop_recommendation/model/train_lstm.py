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
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from ml.crop_recommendation.preprocessing import load_raw_data, prepare_crop_splits
from ml.crop_recommendation.model.lstm_model import build_crop_lstm_model
from ml.crop_recommendation.model.model_utils import (
    set_seed,
    reshape_tabular_to_sequence,
    compute_comprehensive_metrics,
    plot_and_save_confusion_matrix
)
from ml.common.paths import CROP_REC_DIR

MODEL_DIR = CROP_REC_DIR / "model"
RESULTS_DIR = CROP_REC_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
METRICS_DIR = RESULTS_DIR / "metrics"
CM_DIR = RESULTS_DIR / "confusion_matrix"


def train_lstm_model(
    epochs: int = 150,
    batch_size: int = 32,
    learning_rate: float = 0.001
) -> Dict[str, Any]:
    """
    Trains the Crop Recommendation LSTM Neural Network with strict reproducibility,
    callbacks for regularization, artifact serialization, and evaluation.
    """
    set_seed(42)
    print("=" * 60)
    print("  TRAINING CROP RECOMMENDATION LSTM NEURAL NETWORK")
    print("=" * 60)
    
    # 1. Load data and obtain leakage-free splits
    df = load_raw_data()
    X_train, X_val, X_test, y_train, y_val, y_test, scaler, le = prepare_crop_splits(df)
    class_names = list(le.classes_)
    
    # 2. Reshape into 3D Sequence Format: (samples, timesteps=7, features=1)
    X_train_seq = reshape_tabular_to_sequence(X_train)
    X_val_seq = reshape_tabular_to_sequence(X_val)
    X_test_seq = reshape_tabular_to_sequence(X_test)
    
    print(f"LSTM Sequence Input Shape: {X_train_seq.shape[1:]} (timesteps=7, features=1)")
    print(f"Partitions -> Train: {len(X_train_seq)}, Val: {len(X_val_seq)}, Test: {len(X_test_seq)}")
    
    # 3. Instantiate Architecture
    model = build_crop_lstm_model(
        input_shape=(7, 1),
        num_classes=len(class_names),
        lstm_units=64,
        dense_units=64,
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
        X_train_seq,
        y_train,
        validation_data=(X_val_seq, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    training_duration = round(time.time() - start_time, 2)
    print(f"\nLSTM Training completed in {training_duration} seconds ({len(history.epoch)} epochs).")
    
    # 6. Evaluate on Untouched Test Set
    test_probs = model.predict(X_test_seq)
    test_preds = np.argmax(test_probs, axis=1)
    test_metrics = compute_comprehensive_metrics(y_test, test_preds, test_probs, class_names)
    
    val_probs = model.predict(X_val_seq)
    val_preds = np.argmax(val_probs, axis=1)
    val_metrics = compute_comprehensive_metrics(y_val, val_preds, val_probs, class_names)
    
    print("\n" + "-" * 50)
    print(f"LSTM Validation Accuracy: {val_metrics['accuracy']:.4f} | Macro F1: {val_metrics['f1_macro']:.4f}")
    print(f"LSTM Test Accuracy:       {test_metrics['accuracy']:.4f} | Macro F1: {test_metrics['f1_macro']:.4f}")
    print(f"LSTM Top-3 Accuracy:      {test_metrics['top_3_accuracy']:.4f}")
    print(f"LSTM Top-5 Accuracy:      {test_metrics['top_5_accuracy']:.4f}")
    print("-" * 50)
    
    # 7. Generate & Save Training Curves Plot
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy curve
    ax1.plot(history.history["accuracy"], label="Training Accuracy", color="#2563eb", linewidth=2)
    ax1.plot(history.history["val_accuracy"], label="Validation Accuracy", color="#16a34a", linewidth=2)
    ax1.set_title("LSTM Model Accuracy over Epochs", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=10)
    ax1.set_ylabel("Accuracy", fontsize=10)
    ax1.legend(loc="lower right")
    ax1.grid(True, linestyle="--", alpha=0.6)
    
    # Loss curve
    ax2.plot(history.history["loss"], label="Training Loss", color="#dc2626", linewidth=2)
    ax2.plot(history.history["val_loss"], label="Validation Loss", color="#ea580c", linewidth=2)
    ax2.set_title("LSTM Model Loss over Epochs", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=10)
    ax2.set_ylabel("Loss (Sparse Categorical Crossentropy)", fontsize=10)
    ax2.legend(loc="upper right")
    ax2.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    curves_plot_path = PLOTS_DIR / "lstm_training_curves.png"
    plt.savefig(curves_plot_path, dpi=200)
    plt.close()
    print(f"Training curves saved to: {curves_plot_path.name}")
    
    # 8. Save LSTM Confusion Matrix
    cm_path = CM_DIR / "lstm_confusion_matrix.png"
    plot_and_save_confusion_matrix(
        y_true=y_test,
        y_pred=test_preds,
        class_names=class_names,
        title="Crop Recommendation LSTM Confusion Matrix (Test Set)",
        output_path=cm_path
    )
    
    # 9. Save Model Artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_save_path = MODEL_DIR / "crop_recommendation_lstm.keras"
    model.save(model_save_path)
    print(f"Saved Keras model to: {model_save_path.name}")
    
    scaler_path = MODEL_DIR / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"Saved fitted StandardScaler to: {scaler_path.name}")
    
    le_path = MODEL_DIR / "label_encoder.joblib"
    joblib.dump(le, le_path)
    print(f"Saved LabelEncoder to: {le_path.name}")
    
    classes_path = MODEL_DIR / "classes.json"
    with open(classes_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Saved crop class names to: {classes_path.name}")
    
    metadata = {
        "model_type": "LSTM",
        "keras_version": tf.keras.__version__,
        "tensorflow_version": tf.__version__,
        "input_shape": [7, 1],
        "features": ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
        "num_classes": len(class_names),
        "classes": class_names,
        "epochs_trained": len(history.epoch),
        "training_time_seconds": training_duration,
        "hyperparameters": {
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "lstm_units": 64,
            "dense_units": 64,
            "dropout_rate": 0.2
        },
        "metrics": {
            "validation": val_metrics,
            "test": test_metrics
        }
    }
    
    metadata_path = MODEL_DIR / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to: {metadata_path.name}")
    
    # Also save test metrics JSON to results
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    lstm_metrics_path = METRICS_DIR / "lstm_metrics.json"
    with open(lstm_metrics_path, "w") as f:
        json.dump(metadata["metrics"], f, indent=2)
        
    return metadata


if __name__ == "__main__":
    train_lstm_model()
