import os
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf


def set_seed(seed: int = 42) -> None:
    """
    Ensures strict determinism across Python, NumPy, and TensorFlow.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def compute_forecast_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, Any]:
    """
    Computes time-series forecasting metrics:
    - MAE: Mean Absolute Error (in original price units: ₹/Quintal)
    - RMSE: Root Mean Squared Error (₹/Quintal)
    - MAPE: Mean Absolute Percentage Error (%)
    - R²: Coefficient of Determination
    """
    y_true_flat = np.array(y_true).ravel()
    y_pred_flat = np.array(y_pred).ravel()
    
    mae = float(mean_absolute_error(y_true_flat, y_pred_flat))
    mse = float(mean_squared_error(y_true_flat, y_pred_flat))
    rmse = float(np.sqrt(mse))
    
    # Avoid zero-division in MAPE
    mask = y_true_flat > 0
    if np.any(mask):
        mape = float(np.mean(np.abs((y_true_flat[mask] - y_pred_flat[mask]) / y_true_flat[mask])) * 100.0)
    else:
        mape = 0.0
        
    r2 = float(r2_score(y_true_flat, y_pred_flat))
    
    return {
        "model": model_name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "r2_score": round(r2, 4)
    }


def plot_forecast_timeline(
    dates: pd.Series,
    y_true_full: np.ndarray,
    train_size: int,
    val_size: int,
    y_train_pred: np.ndarray,
    y_val_pred: np.ndarray,
    y_test_pred: np.ndarray,
    seq_length: int,
    commodity: str,
    output_path: Path
) -> None:
    """
    Plots the full continuous timeline showing Training, Validation, and Test actual prices
    aligned with their corresponding forecasted values.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # Align date indices: first prediction corresponds to index `seq_length`
    pred_dates = dates.iloc[seq_length:].reset_index(drop=True)
    
    train_end = train_size
    val_end = train_size + val_size
    
    plt.figure(figsize=(15, 6))
    plt.plot(dates, y_true_full, label="Actual Modal Price", color="#94a3b8", alpha=0.7, linewidth=1.2)
    
    # Train predictions
    plt.plot(
        pred_dates.iloc[:train_end],
        y_train_pred,
        label="Train Fitted (LSTM)",
        color="#2563eb",
        linewidth=1.2
    )
    # Val predictions
    plt.plot(
        pred_dates.iloc[train_end:val_end],
        y_val_pred,
        label="Validation Forecast (LSTM)",
        color="#d97706",
        linewidth=1.5
    )
    # Test predictions
    plt.plot(
        pred_dates.iloc[val_end:],
        y_test_pred,
        label="Test Forecast (LSTM)",
        color="#16a34a",
        linewidth=1.5
    )
    
    plt.title(f"Agricultural Commodity Price Forecasting Timeline: {commodity} (2004–2021)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Date Timeline", fontsize=11)
    plt.ylabel("Modal Price (₹ / Quintal)", fontsize=11)
    plt.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")


def plot_test_forecast_zoom(
    test_dates: pd.Series,
    y_test_true: np.ndarray,
    y_test_pred: np.ndarray,
    commodity: str,
    output_path: Path
) -> None:
    """
    Generates a detailed visual comparison of actual vs forecasted prices on the untouched test partition.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(14, 5))
    
    plt.plot(test_dates, y_test_true, label="Actual Test Price", color="#1e293b", linewidth=2.0)
    plt.plot(test_dates, y_test_pred, label="LSTM Predicted Price", color="#10b981", linestyle="--", linewidth=2.0)
    
    plt.title(f"Out-of-Sample Test Evaluation: {commodity} Modal Price Forecast", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Test Period (Chronological Timeline)", fontsize=11)
    plt.ylabel("Price (₹ / Quintal)", fontsize=11)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")


def plot_residual_diagnostics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    commodity: str,
    output_path: Path
) -> None:
    """
    Generates residual diagnostics plots:
    1. Residual distribution histogram with KDE.
    2. Residual error sequence over chronological test steps.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    residuals = (y_true.ravel() - y_pred.ravel())
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residual Distribution
    sns.histplot(residuals, kde=True, ax=ax1, color="#6366f1", bins=30)
    ax1.axvline(x=0, color="#ef4444", linestyle="--", linewidth=1.5)
    ax1.set_title(f"Residual Error Distribution (Actual - Predicted)\nMean: {np.mean(residuals):.2f}, Std: {np.std(residuals):.2f}", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Residual (₹ / Quintal)", fontsize=10)
    ax1.set_ylabel("Frequency", fontsize=10)
    
    # Residuals Over Time
    ax2.plot(residuals, color="#8b5cf6", linewidth=1.2)
    ax2.axhline(y=0, color="#ef4444", linestyle="--", linewidth=1.5)
    ax2.set_title("Residual Errors Over Chronological Test Sequence", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Test Time Step", fontsize=10)
    ax2.set_ylabel("Residual Error (₹ / Quintal)", fontsize=10)
    
    plt.suptitle(f"Residual Diagnostics: {commodity} Price Forecasting", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")
