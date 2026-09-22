import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any
import numpy as np

from ml.crop_recommendation.preprocessing import load_raw_data, prepare_crop_splits
from ml.crop_recommendation.model.baseline import get_logistic_regression_model, get_random_forest_model
from ml.crop_recommendation.model.model_utils import (
    set_seed,
    compute_comprehensive_metrics,
    plot_and_save_confusion_matrix
)
from ml.common.paths import CROP_REC_DIR

RESULTS_DIR = CROP_REC_DIR / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
CM_DIR = RESULTS_DIR / "confusion_matrix"


def train_and_evaluate_baselines() -> Dict[str, Any]:
    """
    Trains Logistic Regression and Random Forest models on training split, validates on val split,
    and calculates complete test evaluation metrics.
    """
    set_seed(42)
    print("=" * 60)
    print("  TRAINING BASELINE MODELS (LOGISTIC REGRESSION & RANDOM FOREST)")
    print("=" * 60)
    
    # 1. Load data and obtain leakage-free splits
    df = load_raw_data()
    X_train, X_val, X_test, y_train, y_val, y_test, scaler, le = prepare_crop_splits(df)
    class_names = list(le.classes_)
    
    print(f"Data Partitions -> Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # 2. Train Logistic Regression
    print("\nTraining Logistic Regression...")
    lr_model = get_logistic_regression_model(random_state=42)
    lr_model.fit(X_train, y_train)
    
    # Val evaluation
    lr_val_preds = lr_model.predict(X_val)
    lr_val_probs = lr_model.predict_proba(X_val)
    lr_val_metrics = compute_comprehensive_metrics(y_val, lr_val_preds, lr_val_probs, class_names)
    
    # Test evaluation
    lr_test_preds = lr_model.predict(X_test)
    lr_test_probs = lr_model.predict_proba(X_test)
    lr_test_metrics = compute_comprehensive_metrics(y_test, lr_test_preds, lr_test_probs, class_names)
    
    print(f"  -> Logistic Regression Val Accuracy: {lr_val_metrics['accuracy']:.4f} | Test Accuracy: {lr_test_metrics['accuracy']:.4f}")
    print(f"  -> Top-3 Accuracy: {lr_test_metrics['top_3_accuracy']:.4f} | Top-5 Accuracy: {lr_test_metrics['top_5_accuracy']:.4f}")
    
    # 3. Train Random Forest Classifier
    print("\nTraining Random Forest Classifier...")
    rf_model = get_random_forest_model(random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Val evaluation
    rf_val_preds = rf_model.predict(X_val)
    rf_val_probs = rf_model.predict_proba(X_val)
    rf_val_metrics = compute_comprehensive_metrics(y_val, rf_val_preds, rf_val_probs, class_names)
    
    # Test evaluation
    rf_test_preds = rf_model.predict(X_test)
    rf_test_probs = rf_model.predict_proba(X_test)
    rf_test_metrics = compute_comprehensive_metrics(y_test, rf_test_preds, rf_test_probs, class_names)
    
    print(f"  -> Random Forest Val Accuracy: {rf_val_metrics['accuracy']:.4f} | Test Accuracy: {rf_test_metrics['accuracy']:.4f}")
    print(f"  -> Top-3 Accuracy: {rf_test_metrics['top_3_accuracy']:.4f} | Top-5 Accuracy: {rf_test_metrics['top_5_accuracy']:.4f}")
    
    # 4. Model Selection between Baselines
    if rf_val_metrics["f1_macro"] >= lr_val_metrics["f1_macro"]:
        best_baseline_name = "Random Forest"
        best_baseline_test_preds = rf_test_preds
    else:
        best_baseline_name = "Logistic Regression"
        best_baseline_test_preds = lr_test_preds
        
    print(f"\nSelected Best Baseline (by Validation F1-Macro): {best_baseline_name}")
    
    # 5. Save Confusion Matrix for Best Baseline
    cm_path = CM_DIR / "best_baseline_confusion_matrix.png"
    plot_and_save_confusion_matrix(
        y_true=y_test,
        y_pred=best_baseline_test_preds,
        class_names=class_names,
        title=f"Best Baseline ({best_baseline_name}) Confusion Matrix",
        output_path=cm_path
    )
    
    # 6. Save baseline metrics JSON
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    baseline_results = {
        "logistic_regression": {
            "validation": lr_val_metrics,
            "test": lr_test_metrics
        },
        "random_forest": {
            "validation": rf_val_metrics,
            "test": rf_test_metrics
        },
        "best_baseline": best_baseline_name
    }
    
    metrics_path = METRICS_DIR / "baseline_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(baseline_results, f, indent=2)
        
    print(f"Baseline metrics saved to: {metrics_path.name}")
    return baseline_results


if __name__ == "__main__":
    train_and_evaluate_baselines()
