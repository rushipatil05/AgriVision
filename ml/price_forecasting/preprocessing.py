import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional
from sklearn.preprocessing import MinMaxScaler
from ml.price_forecasting.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    COL_DATE,
    COL_STATE,
    COL_DISTRICT,
    COL_MARKET,
    COL_COMMODITY,
    COL_MODAL_PRICE,
    COL_MIN_PRICE,
    COL_MAX_PRICE,
    TARGET_COMMODITIES,
    SEQUENCE_LENGTH,
    FORECAST_HORIZON,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO
)


def load_and_clean_price_data(file_path=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw Agmarknet market price dataset and performs cleaning:
    1. Parses dates to datetime objects.
    2. Drops invalid/negative price rows and min > max violations.
    3. Sorts records chronologically.
    """
    df = pd.read_csv(file_path)
    
    # 1. Parse dates (handles DD/MM/YYYY)
    df["date"] = pd.to_datetime(df[COL_DATE], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    
    # 2. Filter positive and consistent price records
    valid_prices = (
        (df[COL_MODAL_PRICE] > 0) &
        (df[COL_MIN_PRICE] > 0) &
        (df[COL_MAX_PRICE] >= df[COL_MIN_PRICE])
    )
    df_clean = df[valid_prices].copy()
    
    # 3. Sort chronologically
    df_clean = df_clean.sort_values(by="date").reset_index(drop=True)
    return df_clean


def prepare_commodity_timeseries(
    df: pd.DataFrame,
    commodity: str = "Onion",
    market: Optional[str] = None,
    freq: str = "D"
) -> pd.DataFrame:
    """
    Extracts, resamples, and interpolates continuous time-series for a target commodity & market.
    """
    filtered = df[df[COL_COMMODITY].str.lower() == commodity.lower()].copy()
    if market:
        filtered = filtered[filtered[COL_MARKET].str.lower() == market.lower()].copy()
        
    if filtered.empty:
        raise ValueError(f"No records found for commodity '{commodity}' and market '{market}'")
        
    # Aggregate to daily modal price (median/mean across varieties in mandi)
    ts = filtered.groupby("date")[COL_MODAL_PRICE].median().reset_index()
    ts = ts.set_index("date").asfreq(freq)
    
    # Forward-fill and backward-fill natural market closure gaps (weekends, mandi holidays)
    ts[COL_MODAL_PRICE] = ts[COL_MODAL_PRICE].ffill().bfill()
    return ts.reset_index()


def create_sliding_windows(
    data: np.ndarray,
    seq_length: int = SEQUENCE_LENGTH,
    horizon: int = FORECAST_HORIZON
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates time-series input sequences (X) and target outputs (y) using sliding window.
    X: [batch_size, seq_length, 1]
    y: [batch_size, horizon]
    """
    X, y = [], []
    for i in range(len(data) - seq_length - horizon + 1):
        X.append(data[i : i + seq_length])
        y.append(data[i + seq_length : i + seq_length + horizon])
    return np.array(X), np.array(y)


def chronological_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits time-series sequences strictly chronologically without random shuffling:
    - Train: First 70%
    - Validation: Next 15%
    - Test: Final 15%
    """
    n = len(X)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def process_and_save_prices(
    raw_path=RAW_DATA_PATH,
    processed_path=PROCESSED_DATA_PATH
) -> Dict[str, Any]:
    """
    Executes price dataset preprocessing and saves cleaned multi-commodity time-series table.
    """
    df_clean = load_and_clean_price_data(raw_path)
    
    # Save cleaned master time-series
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    
    # Extract representative time-series (e.g. Onion)
    ts_onion = prepare_commodity_timeseries(df_clean, commodity="Onion")
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    # Fit scaler ONLY on the training partition of the series to prevent leakage
    n_train_pts = int(len(ts_onion) * TRAIN_RATIO)
    scaler.fit(ts_onion[[COL_MODAL_PRICE]].values[:n_train_pts])
    
    scaled_series = scaler.transform(ts_onion[[COL_MODAL_PRICE]].values)
    X, y = create_sliding_windows(scaled_series, seq_length=SEQUENCE_LENGTH, horizon=FORECAST_HORIZON)
    X_tr, X_val, X_te, y_tr, y_val, y_te = chronological_split(X, y)
    
    metadata = {
        "total_cleaned_records": len(df_clean),
        "target_commodity": "Onion",
        "time_series_days": len(ts_onion),
        "sequence_length": SEQUENCE_LENGTH,
        "forecast_horizon": FORECAST_HORIZON,
        "train_windows": len(X_tr),
        "val_windows": len(X_val),
        "test_windows": len(X_te),
        "min_date": str(ts_onion["date"].min().date()),
        "max_date": str(ts_onion["date"].max().date()),
        "processed_file": str(processed_path)
    }
    
    print(f"Price Forecasting preprocessing complete: {len(df_clean)} cleaned records.")
    print(f"Sample Time-Series (Onion): {len(ts_onion)} continuous daily records from {metadata['min_date']} to {metadata['max_date']}.")
    print(f"Windows (Seq: {SEQUENCE_LENGTH}) -> Train: {len(X_tr)}, Val: {len(X_val)}, Test: {len(X_te)} (Chronological, No Shuffling)")
    print(f"Processed dataset saved to: {processed_path.name}")
    return metadata


if __name__ == "__main__":
    process_and_save_prices()
