import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from ml.price_forecasting.preprocessing import (
    load_and_clean_price_data,
    prepare_commodity_timeseries,
    create_sliding_windows,
    chronological_split
)
from ml.price_forecasting.model.baseline import (
    NaiveLastValueForecaster,
    MovingAverageForecaster,
    LinearRegressionForecaster
)
from ml.price_forecasting.model.model_utils import (
    set_seed,
    compute_forecast_metrics
)
from ml.price_forecasting.config import (
    COL_MODAL_PRICE,
    SEQUENCE_LENGTH,
    FORECAST_HORIZON,
    TRAIN_RATIO,
    VAL_RATIO
)
from ml.common.paths import PRICE_DIR

RESULTS_DIR = PRICE_DIR / "results"
METRICS_DIR = RESULTS_DIR / "metrics"


def train_and_evaluate_price_baselines(commodity: str = "Onion") -> Dict[str, Any]:
    """
    Evaluates Naive, Moving Average, and Linear Regression baselines on the chronological
    validation and test partitions of the selected commodity price series.
    """
    set_seed(42)
    print("=" * 65)
    print(f"  EVALUATING BASELINE FORECASTING MODELS FOR {commodity.upper()}")
    print("=" * 65)
    
    # 1. Load and extract continuous time-series
    df_clean = load_and_clean_price_data()
    ts = prepare_commodity_timeseries(df_clean, commodity=commodity)
    print(f"Time Series: {len(ts)} daily points from {ts['date'].min().date()} to {ts['date'].max().date()}")
    
    # 2. Scaler fitted ONLY on the training period
    n_train_pts = int(len(ts) * TRAIN_RATIO)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(ts[[COL_MODAL_PRICE]].values[:n_train_pts])
    
    # Scale series & create sliding windows
    scaled_series = scaler.transform(ts[[COL_MODAL_PRICE]].values)
    X, y = create_sliding_windows(scaled_series, seq_length=SEQUENCE_LENGTH, horizon=FORECAST_HORIZON)
    
    # Chronological partition (No random shuffling)
    X_train, X_val, X_test, y_train, y_val, y_test = chronological_split(X, y)
    print(f"Sequence Partitions -> Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Ground truth actuals in original price scale (INR / Quintal)
    y_val_actual = scaler.inverse_transform(y_val.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    # 3. Naive Forecaster
    naive = NaiveLastValueForecaster()
    naive_val_pred_scaled = naive.predict(X_val).reshape(-1, 1)
    naive_test_pred_scaled = naive.predict(X_test).reshape(-1, 1)
    
    naive_val_pred = scaler.inverse_transform(naive_val_pred_scaled)
    naive_test_pred = scaler.inverse_transform(naive_test_pred_scaled)
    
    naive_val_metrics = compute_forecast_metrics(y_val_actual, naive_val_pred, "Naive (Last-Value)")
    naive_test_metrics = compute_forecast_metrics(y_test_actual, naive_test_pred, "Naive (Last-Value)")
    
    # 4. Moving Average (7-Day)
    ma7 = MovingAverageForecaster(window=7)
    ma7_val_pred_scaled = ma7.predict(X_val).reshape(-1, 1)
    ma7_test_pred_scaled = ma7.predict(X_test).reshape(-1, 1)
    
    ma7_val_pred = scaler.inverse_transform(ma7_val_pred_scaled)
    ma7_test_pred = scaler.inverse_transform(ma7_test_pred_scaled)
    
    ma7_val_metrics = compute_forecast_metrics(y_val_actual, ma7_val_pred, "Moving Average (7-Day)")
    ma7_test_metrics = compute_forecast_metrics(y_test_actual, ma7_test_pred, "Moving Average (7-Day)")
    
    # 5. Linear Regression Forecaster
    lr = LinearRegressionForecaster()
    lr.fit(X_train, y_train.reshape(-1, 1))
    
    lr_val_pred_scaled = lr.predict(X_val).reshape(-1, 1)
    lr_test_pred_scaled = lr.predict(X_test).reshape(-1, 1)
    
    lr_val_pred = scaler.inverse_transform(lr_val_pred_scaled)
    lr_test_pred = scaler.inverse_transform(lr_test_pred_scaled)
    
    lr_val_metrics = compute_forecast_metrics(y_val_actual, lr_val_pred, "Linear Regression")
    lr_test_metrics = compute_forecast_metrics(y_test_actual, lr_test_pred, "Linear Regression")
    
    print("\n--- BASELINE VALIDATION METRICS (INR/Quintal) ---")
    print(f"Naive:        MAE={naive_val_metrics['mae']:7.2f}, RMSE={naive_val_metrics['rmse']:7.2f}, MAPE={naive_val_metrics['mape']:5.2f}%, R2={naive_val_metrics['r2_score']:.4f}")
    print(f"Moving Avg:   MAE={ma7_val_metrics['mae']:7.2f}, RMSE={ma7_val_metrics['rmse']:7.2f}, MAPE={ma7_val_metrics['mape']:5.2f}%, R2={ma7_val_metrics['r2_score']:.4f}")
    print(f"Linear Reg:   MAE={lr_val_metrics['mae']:7.2f}, RMSE={lr_val_metrics['rmse']:7.2f}, MAPE={lr_val_metrics['mape']:5.2f}%, R2={lr_val_metrics['r2_score']:.4f}")
    
    print("\n--- BASELINE TEST METRICS (INR/Quintal) ---")
    print(f"Naive:        MAE={naive_test_metrics['mae']:7.2f}, RMSE={naive_test_metrics['rmse']:7.2f}, MAPE={naive_test_metrics['mape']:5.2f}%, R2={naive_test_metrics['r2_score']:.4f}")
    print(f"Moving Avg:   MAE={ma7_test_metrics['mae']:7.2f}, RMSE={ma7_test_metrics['rmse']:7.2f}, MAPE={ma7_test_metrics['mape']:5.2f}%, R2={ma7_test_metrics['r2_score']:.4f}")
    print(f"Linear Reg:   MAE={lr_test_metrics['mae']:7.2f}, RMSE={lr_test_metrics['rmse']:7.2f}, MAPE={lr_test_metrics['mape']:5.2f}%, R2={lr_test_metrics['r2_score']:.4f}")
    
    # Save baseline metrics
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    baseline_results = {
        "commodity": commodity,
        "naive_last_value": {
            "validation": naive_val_metrics,
            "test": naive_test_metrics
        },
        "moving_average_7d": {
            "validation": ma7_val_metrics,
            "test": ma7_test_metrics
        },
        "linear_regression": {
            "validation": lr_val_metrics,
            "test": lr_test_metrics
        }
    }
    
    metrics_path = METRICS_DIR / "baseline_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(baseline_results, f, indent=2)
    print(f"\nSaved baseline metrics to: {metrics_path.name}")
    return baseline_results


if __name__ == "__main__":
    train_and_evaluate_price_baselines()
