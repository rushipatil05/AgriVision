import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import math
import json
from typing import Dict, List, Any, Union, Optional
import numpy as np
import joblib
import tensorflow as tf

from ml.price_forecasting.config import SEQUENCE_LENGTH
from ml.common.paths import PRICE_DIR

MODEL_DIR = PRICE_DIR / "model"

# Global artifact cache for inference performance
_PRICE_CACHE: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "metadata": None
}


def load_price_inference_artifacts(model_dir: Path = MODEL_DIR) -> Dict[str, Any]:
    """
    Loads and caches the serialized price forecasting LSTM model, scaler, and metadata.
    """
    global _PRICE_CACHE
    if _PRICE_CACHE["model"] is not None:
        return _PRICE_CACHE

    model_path = model_dir / "crop_price_lstm.keras"
    scaler_path = model_dir / "scaler.joblib"
    meta_path = model_dir / "metadata.json"

    if not model_path.exists() or not scaler_path.exists():
        raise FileNotFoundError(
            f"Trained price model artifacts not found in {model_dir}. "
            f"Please run train_lstm.py first."
        )

    _PRICE_CACHE["model"] = tf.keras.models.load_model(model_path)
    _PRICE_CACHE["scaler"] = joblib.load(scaler_path)
    if meta_path.exists():
        with open(meta_path, "r") as f:
            _PRICE_CACHE["metadata"] = json.load(f)

    return _PRICE_CACHE


def validate_price_sequence_input(
    historical_prices: List[Union[int, float]],
    horizon: int = 7,
    min_length: int = SEQUENCE_LENGTH
) -> List[float]:
    """
    Validates input price sequences:
    - Verifies sufficient historical length (>= 30 days).
    - Rejects None, NaN, Infinity, negative, or non-numeric values.
    - Validates forecast horizon bounds (1 to 60 days).
    """
    if not isinstance(historical_prices, (list, tuple, np.ndarray)):
        raise TypeError(f"historical_prices must be a list or array, got {type(historical_prices).__name__}")

    if len(historical_prices) < min_length:
        raise ValueError(
            f"historical_prices sequence length ({len(historical_prices)}) is insufficient. "
            f"Minimum required historical lookback is {min_length} continuous daily points."
        )

    if not isinstance(horizon, int) or horizon < 1 or horizon > 60:
        raise ValueError(f"forecast_horizon must be an integer between 1 and 60 days, got: {horizon}")

    validated = []
    for i, p in enumerate(historical_prices):
        if p is None:
            raise ValueError(f"Price at index {i} cannot be None.")
        try:
            val = float(p)
        except (ValueError, TypeError):
            raise ValueError(f"Price at index {i} is not a valid number: {p}")

        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Price at index {i} cannot be NaN or Infinite.")

        if val <= 0:
            raise ValueError(f"Price at index {i} must be strictly positive (got: {val}).")

        validated.append(val)

    return validated


def predict_crop_price(
    historical_prices: List[Union[int, float]],
    commodity: str = "Onion",
    market: str = "Lasalgaon",
    forecast_horizon: int = 7
) -> Dict[str, Any]:
    """
    Generates multi-step crop market price forecasts using the trained LSTM model.
    
    Parameters:
        historical_prices: List of at least 30 historical daily modal prices (INR/Quintal).
        commodity: Target agricultural crop name (default: Onion).
        market: Target APMC wholesale mandi (default: Lasalgaon).
        forecast_horizon: Number of days ahead to forecast (1 to 60 days, default: 7).
        
    Returns:
        Structured forecast dictionary with predicted daily prices, trend direction,
        and projected percentage change.
    """
    # 1. Validate inputs
    clean_series = validate_price_sequence_input(historical_prices, horizon=forecast_horizon)
    
    # 2. Load model & scaler
    artifacts = load_price_inference_artifacts()
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    
    # Extract the most recent 30-day window
    current_window = np.array(clean_series[-SEQUENCE_LENGTH:]).reshape(-1, 1)
    
    # 3. Multi-Step Recursive Forecasting
    predictions = []
    working_window = current_window.copy()
    
    for day in range(1, forecast_horizon + 1):
        # Scale working window
        scaled_window = scaler.transform(working_window[-SEQUENCE_LENGTH:])
        seq_input = scaled_window.reshape(1, SEQUENCE_LENGTH, 1)
        
        # Predict 1-step ahead
        pred_scaled = model.predict(seq_input, verbose=0)
        pred_actual = float(scaler.inverse_transform(pred_scaled)[0, 0])
        
        # Guard against negative / degenerate outputs
        pred_actual = max(1.0, round(pred_actual, 2))
        predictions.append({
            "day": day,
            "predicted_modal_price": pred_actual,
            "unit": "INR/Quintal"
        })
        
        # Append predicted value for recursive multi-step forecasting
        working_window = np.vstack([working_window, [[pred_actual]]])
        
    last_price = clean_series[-1]
    final_pred_price = predictions[-1]["predicted_modal_price"]
    pct_change = round(((final_pred_price - last_price) / last_price) * 100.0, 2)
    
    if pct_change > 1.5:
        trend = "UPWARD"
    elif pct_change < -1.5:
        trend = "DOWNWARD"
    else:
        trend = "STABLE"
        
    return {
        "commodity": commodity,
        "market": market,
        "forecast_horizon_days": forecast_horizon,
        "last_observed_price": round(float(last_price), 2),
        "predicted_end_price": final_pred_price,
        "projected_percentage_change": pct_change,
        "trend_direction": trend,
        "forecasts": predictions
    }


if __name__ == "__main__":
    # Test sample with 30 synthetic test points
    sample_prices = [
        1200, 1220, 1210, 1250, 1270, 1300, 1290, 1310, 1340, 1360,
        1380, 1370, 1390, 1420, 1450, 1430, 1460, 1490, 1510, 1500,
        1530, 1550, 1540, 1580, 1600, 1620, 1610, 1640, 1670, 1700
    ]
    print(f"Sample Input: {len(sample_prices)} historical daily prices, Last Price = INR {sample_prices[-1]}")
    res = predict_crop_price(sample_prices, commodity="Onion", market="Lasalgaon", forecast_horizon=7)
    print("\n--- 7-DAY PRICE FORECAST RESULT ---")
    print(f"Commodity: {res['commodity']} | Market: {res['market']}")
    print(f"Last Price: INR {res['last_observed_price']}/Qtl -> Day 7 Forecast: INR {res['predicted_end_price']}/Qtl ({res['projected_percentage_change']:+0.2f}%)")
    print(f"Trend Direction: {res['trend_direction']}")
    for f in res["forecasts"]:
        print(f"  Day {f['day']:2d}: INR {f['predicted_modal_price']:7.2f} / Quintal")
