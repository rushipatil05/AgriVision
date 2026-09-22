import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any
import pandas as pd
from ml.common.paths import CROP_REC_DIR

METRICS_DIR = CROP_REC_DIR / "results" / "metrics"


def generate_model_comparison_report() -> pd.DataFrame:
    """
    Loads metrics from baseline models and LSTM, constructs a unified comparative table,
    identifies the best model, and outputs the comparison artifact.
    """
    baseline_path = METRICS_DIR / "baseline_metrics.json"
    lstm_path = METRICS_DIR / "lstm_metrics.json"
    
    if not baseline_path.exists() or not lstm_path.exists():
        raise FileNotFoundError("Baseline or LSTM metrics not found. Run train_baseline.py and train_lstm.py first.")
        
    with open(baseline_path, "r") as f:
        baseline_data = json.load(f)
        
    with open(lstm_path, "r") as f:
        lstm_data = json.load(f)
        
    models_summary = []
    
    # 1. Logistic Regression
    lr_test = baseline_data["logistic_regression"]["test"]
    lr_val = baseline_data["logistic_regression"]["validation"]
    models_summary.append({
        "Model": "Logistic Regression (Baseline)",
        "Val Accuracy": lr_val["accuracy"],
        "Val F1 (Macro)": lr_val["f1_macro"],
        "Test Accuracy": lr_test["accuracy"],
        "Test Precision (Macro)": lr_test["precision_macro"],
        "Test Recall (Macro)": lr_test["recall_macro"],
        "Test F1 (Macro)": lr_test["f1_macro"],
        "Top-1 Accuracy": lr_test["top_1_accuracy"],
        "Top-3 Accuracy": lr_test["top_3_accuracy"],
        "Top-5 Accuracy": lr_test["top_5_accuracy"]
    })
    
    # 2. Random Forest
    rf_test = baseline_data["random_forest"]["test"]
    rf_val = baseline_data["random_forest"]["validation"]
    models_summary.append({
        "Model": "Random Forest (Baseline)",
        "Val Accuracy": rf_val["accuracy"],
        "Val F1 (Macro)": rf_val["f1_macro"],
        "Test Accuracy": rf_test["accuracy"],
        "Test Precision (Macro)": rf_test["precision_macro"],
        "Test Recall (Macro)": rf_test["recall_macro"],
        "Test F1 (Macro)": rf_test["f1_macro"],
        "Top-1 Accuracy": rf_test["top_1_accuracy"],
        "Top-3 Accuracy": rf_test["top_3_accuracy"],
        "Top-5 Accuracy": rf_test["top_5_accuracy"]
    })
    
    # 3. LSTM Neural Network
    lstm_test = lstm_data["test"]
    lstm_val = lstm_data["validation"]
    models_summary.append({
        "Model": "LSTM Neural Network (Primary)",
        "Val Accuracy": lstm_val["accuracy"],
        "Val F1 (Macro)": lstm_val["f1_macro"],
        "Test Accuracy": lstm_test["accuracy"],
        "Test Precision (Macro)": lstm_test["precision_macro"],
        "Test Recall (Macro)": lstm_test["recall_macro"],
        "Test F1 (Macro)": lstm_test["f1_macro"],
        "Top-1 Accuracy": lstm_test["top_1_accuracy"],
        "Top-3 Accuracy": lstm_test["top_3_accuracy"],
        "Top-5 Accuracy": lstm_test["top_5_accuracy"]
    })
    
    comparison_df = pd.DataFrame(models_summary)
    
    print("\n" + "=" * 90)
    print("  CROP RECOMMENDATION MODEL COMPARISON SUMMARY (ON UNTOUCHED TEST SET)")
    print("=" * 90)
    print(comparison_df.to_string(index=False))
    print("=" * 90 + "\n")
    
    # Identify best model based on Test F1 Macro
    best_row = comparison_df.sort_values(by="Test F1 (Macro)", ascending=False).iloc[0]
    print(f"Top Performing Model by Test F1-Macro: {best_row['Model']} (F1: {best_row['Test F1 (Macro)']:.4f}, Accuracy: {best_row['Test Accuracy']:.4f})")
    
    # Save comparison report
    comparison_json_path = METRICS_DIR / "model_comparison.json"
    with open(comparison_json_path, "w") as f:
        json.dump(models_summary, f, indent=2)
    print(f"Comparison metrics saved to: {comparison_json_path.name}")
    
    return comparison_df


if __name__ == "__main__":
    generate_model_comparison_report()
