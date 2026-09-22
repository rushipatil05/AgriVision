import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
import json
from typing import Dict, Any
import joblib
import numpy as np

from ml.yield_forecasting.preprocessing import (
    load_and_clean_yield_data,
    prepare_yield_splits,
    build_and_fit_preprocessor,
    FEATURE_COLUMNS,
    COL_YIELD
)
from ml.yield_forecasting.model.baseline import (
    MedianYieldRegressor,
    LinearYieldRegressor,
    RandomForestYieldRegressor,
    GradientBoostingYieldRegressor
)
from ml.yield_forecasting.model.model_utils import (
    set_seed,
    compute_regression_metrics
)
from ml.common.paths import YIELD_DIR

MODEL_DIR = YIELD_DIR / "model"
RESULTS_DIR = YIELD_DIR / "results"
METRICS_DIR = RESULTS_DIR / "metrics"


def train_and_evaluate_yield_baselines() -> Dict[str, Any]:
    """
    Fits and evaluates Median, Ridge Linear Regression, Random Forest, and Gradient Boosting
    regressors on the chronological crop yield dataset partitions.
    """
    set_seed(42)
    print("=" * 65)
    print("  EVALUATING CROP YIELD REGRESSION BASELINE MODELS")
    print("=" * 65)
    
    # 1. Load data & prepare chronological splits
    df_clean = load_and_clean_yield_data()
    train_df, val_df, test_df = prepare_yield_splits(df_clean)
    
    print(f"Chronological Partitions -> Train: {len(train_df):,}, Val: {len(val_df):,}, Test: {len(test_df):,}")
    
    # 2. Fit preprocessor ONLY on training partition (Prevent temporal leakage)
    preprocessor = build_and_fit_preprocessor(train_df)
    
    X_train = preprocessor.transform(train_df[FEATURE_COLUMNS])
    X_val = preprocessor.transform(val_df[FEATURE_COLUMNS])
    X_test = preprocessor.transform(test_df[FEATURE_COLUMNS])
    
    y_train = train_df[COL_YIELD].values
    y_val = val_df[COL_YIELD].values
    y_test = test_df[COL_YIELD].values
    
    print(f"Encoded Feature Dimensions: {X_train.shape[1]} columns (Zero Target Leakage: Production Excluded)")
    
    # 3. Fit and evaluate all baselines
    models = [
        MedianYieldRegressor(),
        LinearYieldRegressor(alpha=1.0),
        GradientBoostingYieldRegressor(max_iter=150, learning_rate=0.08, max_depth=12, random_state=42),
        RandomForestYieldRegressor(n_estimators=100, max_depth=18, random_state=42)
    ]
    
    results = {}
    best_model_obj = None
    best_val_mae = float("inf")
    
    for m in models:
        print(f"\nTraining {m.name}...")
        t0 = time.time()
        m.fit(X_train, y_train)
        fit_time = round(time.time() - t0, 2)
        
        # Predictions
        val_preds = m.predict(X_val)
        test_preds = m.predict(X_test)
        
        # Metrics
        val_metrics = compute_regression_metrics(y_val, val_preds, m.name)
        test_metrics = compute_regression_metrics(y_test, test_preds, m.name)
        
        print(f"  [Val]  MAE: {val_metrics['mae']:.3f} Tonnes/ha | RMSE: {val_metrics['rmse']:.3f} | R2: {val_metrics['r2_score']:.4f} | MedAE: {val_metrics['medae']:.3f}")
        print(f"  [Test] MAE: {test_metrics['mae']:.3f} Tonnes/ha | RMSE: {test_metrics['rmse']:.3f} | R2: {test_metrics['r2_score']:.4f} | MedAE: {test_metrics['medae']:.3f} (Fit Time: {fit_time}s)")
        
        results[m.name] = {
            "fit_time_seconds": fit_time,
            "validation": val_metrics,
            "test": test_metrics
        }
        
        if val_metrics["mae"] < best_val_mae:
            best_val_mae = val_metrics["mae"]
            best_model_obj = m
            
    # 4. Save results & preprocessor
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    metrics_path = METRICS_DIR / "baseline_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved baseline metrics to: {metrics_path.name}")
    
    # Save fitted preprocessor
    preprocessor_path = MODEL_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"Saved fitted ColumnTransformer to: {preprocessor_path.name}")
    
    # Save best tree/tabular model
    if best_model_obj is not None:
        best_baseline_path = MODEL_DIR / "gradient_boosting_yield.joblib"
        joblib.dump(best_model_obj, best_baseline_path)
        print(f"Saved best tree model ({best_model_obj.name}) to: {best_baseline_path.name}")
        
    return results


if __name__ == "__main__":
    train_and_evaluate_yield_baselines()
