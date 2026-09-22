import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any
import pandas as pd
from ml.common.paths import PRICE_DIR

METRICS_DIR = PRICE_DIR / "results" / "metrics"


def generate_price_comparison_report() -> pd.DataFrame:
    """
    Loads metrics from baseline models and LSTM, constructs a unified comparative table,
    identifies the best model, and saves the comparison artifact.
    """
    baseline_path = METRICS_DIR / "baseline_metrics.json"
    lstm_path = METRICS_DIR / "lstm_metrics.json"
    
    if not baseline_path.exists() or not lstm_path.exists():
        raise FileNotFoundError("Baseline or LSTM metrics not found. Run train_baseline.py and train_lstm.py first.")
        
    with open(baseline_path, "r") as f:
        baseline_data = json.load(f)
        
    with open(lstm_path, "r") as f:
        lstm_data = json.load(f)
        
    commodity = baseline_data.get("commodity", "Onion")
    models_summary = []
    
    # 1. Naive (Last-Value)
    naive_val = baseline_data["naive_last_value"]["validation"]
    naive_test = baseline_data["naive_last_value"]["test"]
    models_summary.append({
        "Model": "Naive (Last-Value Baseline)",
        "Val MAE (INR/Qtl)": naive_val["mae"],
        "Val RMSE (INR/Qtl)": naive_val["rmse"],
        "Val MAPE (%)": naive_val["mape"],
        "Test MAE (INR/Qtl)": naive_test["mae"],
        "Test RMSE (INR/Qtl)": naive_test["rmse"],
        "Test MAPE (%)": naive_test["mape"],
        "Test R2": naive_test["r2_score"]
    })
    
    # 2. Moving Average (7-Day)
    ma_val = baseline_data["moving_average_7d"]["validation"]
    ma_test = baseline_data["moving_average_7d"]["test"]
    models_summary.append({
        "Model": "Moving Average (7-Day Baseline)",
        "Val MAE (INR/Qtl)": ma_val["mae"],
        "Val RMSE (INR/Qtl)": ma_val["rmse"],
        "Val MAPE (%)": ma_val["mape"],
        "Test MAE (INR/Qtl)": ma_test["mae"],
        "Test RMSE (INR/Qtl)": ma_test["rmse"],
        "Test MAPE (%)": ma_test["mape"],
        "Test R2": ma_test["r2_score"]
    })
    
    # 3. Linear Regression
    lr_val = baseline_data["linear_regression"]["validation"]
    lr_test = baseline_data["linear_regression"]["test"]
    models_summary.append({
        "Model": "Linear Regression (Autoregressive)",
        "Val MAE (INR/Qtl)": lr_val["mae"],
        "Val RMSE (INR/Qtl)": lr_val["rmse"],
        "Val MAPE (%)": lr_val["mape"],
        "Test MAE (INR/Qtl)": lr_test["mae"],
        "Test RMSE (INR/Qtl)": lr_test["rmse"],
        "Test MAPE (%)": lr_test["mape"],
        "Test R2": lr_test["r2_score"]
    })
    
    # 4. LSTM Neural Network
    lstm_val = lstm_data["validation"]
    lstm_test = lstm_data["test"]
    models_summary.append({
        "Model": "LSTM Neural Network (Primary)",
        "Val MAE (INR/Qtl)": lstm_val["mae"],
        "Val RMSE (INR/Qtl)": lstm_val["rmse"],
        "Val MAPE (%)": lstm_val["mape"],
        "Test MAE (INR/Qtl)": lstm_test["mae"],
        "Test RMSE (INR/Qtl)": lstm_test["rmse"],
        "Test MAPE (%)": lstm_test["mape"],
        "Test R2": lstm_test["r2_score"]
    })
    
    comparison_df = pd.DataFrame(models_summary)
    
    print("\n" + "=" * 105)
    print(f"  CROP MARKET PRICE FORECASTING MODEL COMPARISON ({commodity.upper()} - ON UNTOUCHED TEST SET)")
    print("=" * 105)
    print(comparison_df.to_string(index=False))
    print("=" * 105 + "\n")
    
    # Identify best model based on Test MAE / RMSE
    best_row = comparison_df.sort_values(by="Test MAE (INR/Qtl)").iloc[0]
    print(f"Best Performing Model by Test MAE: {best_row['Model']} (MAE: INR {best_row['Test MAE (INR/Qtl)']}/Qtl, RMSE: INR {best_row['Test RMSE (INR/Qtl)']}, MAPE: {best_row['Test MAPE (%)']}%)")
    
    # Save comparison report
    comparison_json_path = METRICS_DIR / "model_comparison.json"
    with open(comparison_json_path, "w") as f:
        json.dump(models_summary, f, indent=2)
    print(f"Comparison metrics saved to: {comparison_json_path.name}")
    
    return comparison_df


if __name__ == "__main__":
    generate_price_comparison_report()
