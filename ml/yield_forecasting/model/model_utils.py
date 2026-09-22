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
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
import tensorflow as tf


def set_seed(seed: int = 42) -> None:
    """
    Ensures determinism across Python, NumPy, and TensorFlow.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, Any]:
    """
    Computes regression performance metrics for yield estimation:
    - MAE: Mean Absolute Error (Tonnes/ha)
    - RMSE: Root Mean Squared Error (Tonnes/ha)
    - R²: Coefficient of Determination
    - MedAE: Median Absolute Error (robust to extreme yield variations)
    - MAPE: Mean Absolute Percentage Error (computed safely on positive non-zero entries)
    """
    y_true_flat = np.array(y_true).ravel()
    y_pred_flat = np.array(y_pred).ravel()
    
    # Clip any negative predictions to zero (yield cannot be negative)
    y_pred_clipped = np.maximum(0.0, y_pred_flat)
    
    mae = float(mean_absolute_error(y_true_flat, y_pred_clipped))
    mse = float(mean_squared_error(y_true_flat, y_pred_clipped))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true_flat, y_pred_clipped))
    medae = float(median_absolute_error(y_true_flat, y_pred_clipped))
    
    # Safe MAPE on non-zero true yields (> 0.05 Tonnes/ha to prevent division artifacts)
    valid_mask = y_true_flat > 0.05
    if np.any(valid_mask):
        mape = float(np.mean(np.abs((y_true_flat[valid_mask] - y_pred_clipped[valid_mask]) / y_true_flat[valid_mask])) * 100.0)
    else:
        mape = 0.0
        
    return {
        "model": model_name,
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2_score": round(r2, 4),
        "medae": round(medae, 3),
        "mape": round(mape, 2)
    }


def plot_actual_vs_predicted(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    output_path: Path
) -> None:
    """
    Plots Actual vs Predicted Yield with the 1:1 identity reference line.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    y_true_flat = np.array(y_true).ravel()
    y_pred_flat = np.maximum(0.0, np.array(y_pred).ravel())
    
    plt.figure(figsize=(7, 6.5))
    plt.scatter(y_true_flat, y_pred_flat, alpha=0.35, color="#2563eb", edgecolors="none", s=20)
    
    max_val = min(150.0, max(np.percentile(y_true_flat, 99.5), np.percentile(y_pred_flat, 99.5)))
    plt.plot([0, max_val], [0, max_val], color="#ef4444", linestyle="--", linewidth=2.0, label="Ideal Fit (y = x)")
    
    plt.title(f"Actual vs Predicted Crop Yield: {model_name}", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Actual Yield (Tonnes / Hectare)", fontsize=10)
    plt.ylabel("Predicted Yield (Tonnes / Hectare)", fontsize=10)
    plt.xlim(0, max_val)
    plt.ylim(0, max_val)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")


def plot_residual_diagnostics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    output_path: Path
) -> None:
    """
    Generates residual diagnostics plots:
    1. Residual distribution histogram with KDE.
    2. Residual vs Predicted Yield scatter plot.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    y_true_flat = np.array(y_true).ravel()
    y_pred_flat = np.maximum(0.0, np.array(y_pred).ravel())
    residuals = y_true_flat - y_pred_flat
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residual Distribution
    sns.histplot(residuals, kde=True, ax=ax1, color="#6366f1", bins=40)
    ax1.axvline(x=0, color="#ef4444", linestyle="--", linewidth=1.5)
    ax1.set_title(f"Residual Error Distribution ({model_name})\nMean: {np.mean(residuals):.2f}, Std: {np.std(residuals):.2f}", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Residual Error (Actual - Predicted) [Tonnes/ha]", fontsize=10)
    ax1.set_ylabel("Count", fontsize=10)
    
    # Residual vs Predicted
    ax2.scatter(y_pred_flat, residuals, alpha=0.3, color="#8b5cf6", s=18)
    ax2.axhline(y=0, color="#ef4444", linestyle="--", linewidth=1.5)
    ax2.set_title("Residual Error vs Predicted Yield", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Predicted Yield (Tonnes/ha)", fontsize=10)
    ax2.set_ylabel("Residual Error (Tonnes/ha)", fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")


def plot_crop_level_performance(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    output_path: Path
) -> None:
    """
    Plots MAE and RMSE performance broken down across individual major crops.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_eval = test_df.copy()
    df_eval["Predicted_Yield"] = np.maximum(0.0, np.array(y_pred).ravel())
    df_eval["Abs_Error"] = np.abs(df_eval["Yield"] - df_eval["Predicted_Yield"])
    
    crop_stats = df_eval.groupby("Crop")["Abs_Error"].mean().sort_values(ascending=False).reset_index()
    
    plt.figure(figsize=(10, 5))
    sns.barplot(data=crop_stats, x="Crop", y="Abs_Error", palette="viridis")
    plt.title("Yield Forecasting MAE by Agricultural Crop (Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Crop", fontsize=10)
    plt.ylabel("Mean Absolute Error (Tonnes / Hectare)", fontsize=10)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")


def plot_state_level_performance(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    output_path: Path
) -> None:
    """
    Plots MAE performance broken down across top agricultural states.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_eval = test_df.copy()
    df_eval["Predicted_Yield"] = np.maximum(0.0, np.array(y_pred).ravel())
    df_eval["Abs_Error"] = np.abs(df_eval["Yield"] - df_eval["Predicted_Yield"])
    
    # Top 12 states by test sample count
    top_states = df_eval["State_Name"].value_counts().head(12).index
    state_stats = df_eval[df_eval["State_Name"].isin(top_states)].groupby("State_Name")["Abs_Error"].mean().sort_values(ascending=False).reset_index()
    
    plt.figure(figsize=(12, 5))
    sns.barplot(data=state_stats, x="State_Name", y="Abs_Error", palette="mako")
    plt.title("Yield Forecasting MAE Across Top Agricultural States (Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("State", fontsize=10)
    plt.ylabel("Mean Absolute Error (Tonnes / Hectare)", fontsize=10)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path.name}")
