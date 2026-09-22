import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any, List
import pandas as pd
from ml.common.paths import YIELD_DIR

METRICS_DIR = YIELD_DIR / "results" / "metrics"


def generate_yield_comparison_report() -> pd.DataFrame:
    """
    Loads performance metrics across baseline and deep neural models,
    creates a unified comparative table, and saves the comparison artifact.
    """
    baseline_path = METRICS_DIR / "baseline_metrics.json"
    deep_path = METRICS_DIR / "deep_model_metrics.json"
    
    if not baseline_path.exists() or not deep_path.exists():
        raise FileNotFoundError("Baseline or Deep model metrics not found. Run train_baseline.py and train_deep.py first.")
        
    with open(baseline_path, "r") as f:
        baseline_data = json.load(f)
        
    with open(deep_path, "r") as f:
        deep_data = json.load(f)
        
    models_summary: List[Dict[str, Any]] = []
    
    # Add Baselines
    for model_name, data in baseline_data.items():
        val = data["validation"]
        test = data["test"]
        models_summary.append({
            "Model": model_name,
            "Val MAE (t/ha)": val["mae"],
            "Val RMSE (t/ha)": val["rmse"],
            "Val R2": val["r2_score"],
            "Test MAE (t/ha)": test["mae"],
            "Test RMSE (t/ha)": test["rmse"],
            "Test R2": test["r2_score"],
            "Test MedAE (t/ha)": test["medae"],
            "Test MAPE (%)": test["mape"]
        })
        
    # Add Deep Neural Network
    dnn_val = deep_data["validation"]
    dnn_test = deep_data["test"]
    models_summary.append({
        "Model": "Deep Neural Network (DNN)",
        "Val MAE (t/ha)": dnn_val["mae"],
        "Val RMSE (t/ha)": dnn_val["rmse"],
        "Val R2": dnn_val["r2_score"],
        "Test MAE (t/ha)": dnn_test["mae"],
        "Test RMSE (t/ha)": dnn_test["rmse"],
        "Test R2": dnn_test["r2_score"],
        "Test MedAE (t/ha)": dnn_test["medae"],
        "Test MAPE (%)": dnn_test["mape"]
    })
    
    comparison_df = pd.DataFrame(models_summary)
    
    print("\n" + "=" * 115)
    print("  CROP YIELD FORECASTING MODEL COMPARISON (CHRONOLOGICAL VALIDATION & UNTOUCHED TEST SET)")
    print("=" * 115)
    print(comparison_df.to_string(index=False))
    print("=" * 115 + "\n")
    
    # Identify best model based on Validation MAE
    best_row = comparison_df.sort_values(by="Val MAE (t/ha)").iloc[0]
    print(f"Best Selected Model (by Validation MAE): {best_row['Model']}")
    print(f"  -> Validation MAE: {best_row['Val MAE (t/ha)']} Tonnes/ha, Validation R2: {best_row['Val R2']}")
    print(f"  -> Final Test MAE: {best_row['Test MAE (t/ha)']} Tonnes/ha, Final Test R2: {best_row['Test R2']}, Test MedAE: {best_row['Test MedAE (t/ha)']} Tonnes/ha")
    
    # Save comparison report
    comparison_json_path = METRICS_DIR / "model_comparison.json"
    with open(comparison_json_path, "w") as f:
        json.dump(models_summary, f, indent=2)
    print(f"\nComparison metrics saved to: {comparison_json_path.name}")
    
    return comparison_df


if __name__ == "__main__":
    generate_yield_comparison_report()
