import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.price_forecasting.preprocessing import (
    load_and_clean_price_data,
    prepare_commodity_timeseries,
    create_sliding_windows,
    chronological_split
)
from ml.price_forecasting.model.predict import (
    load_price_inference_artifacts,
    validate_price_sequence_input,
    predict_crop_price
)
from ml.price_forecasting.config import SEQUENCE_LENGTH, TRAIN_RATIO, VAL_RATIO
from ml.common.paths import RAW_PRICE_CSV, PROCESSED_PRICE_CSV


class TestPriceForecastingPipeline:
    """
    Automated test suite verifying the integrity of the Crop Market Price Forecasting ML pipeline.
    """

    def test_price_dataset_files_exist(self):
        """Verify raw and processed price dataset files exist on disk."""
        assert RAW_PRICE_CSV.exists(), "Raw price dataset CSV missing"
        assert PROCESSED_PRICE_CSV.exists(), "Processed price dataset CSV missing"

    def test_raw_data_cleaning_and_chronology(self):
        """Verify date parsing, price validity filtering, and strict chronological sort."""
        df_clean = load_and_clean_price_data()
        assert len(df_clean) > 0, "Cleaned price dataset should not be empty"
        assert "date" in df_clean.columns, "Parsed date column missing"
        assert df_clean["date"].is_monotonic_increasing, "Dataset must be sorted chronologically"
        assert (df_clean["Modal_Price"] > 0).all(), "Modal prices must be strictly positive"
        assert (df_clean["Max_Price"] >= df_clean["Min_Price"]).all(), "Max price must be >= Min price"

    def test_continuous_series_and_chronological_splits(self):
        """Verify time-series preparation and non-overlapping chronological partitions."""
        df_clean = load_and_clean_price_data()
        ts = prepare_commodity_timeseries(df_clean, commodity="Onion")
        assert len(ts) == 6575, f"Expected 6575 daily points, got {len(ts)}"
        assert ts["date"].is_monotonic_increasing, "Time series dates must be chronological"

        # Create windows
        raw_prices = ts[["Modal_Price"]].values
        X, y = create_sliding_windows(raw_prices, seq_length=SEQUENCE_LENGTH, horizon=1)
        assert X.shape[1] == SEQUENCE_LENGTH, f"Expected window length {SEQUENCE_LENGTH}"
        assert X.shape[2] == 1, "Expected single feature dimension"

        # Chronological splits
        X_tr, X_val, X_te, y_tr, y_val, y_te = chronological_split(X, y)
        assert len(X_tr) == 4581, f"Expected 4581 train sequences, got {len(X_tr)}"
        assert len(X_val) == 982, f"Expected 982 val sequences, got {len(X_val)}"
        assert len(X_te) == 982, f"Expected 982 test sequences, got {len(X_te)}"

        # Temporal boundary verification: Train dates < Val dates < Test dates
        train_end_idx = len(X_tr) + SEQUENCE_LENGTH
        val_end_idx = train_end_idx + len(X_val)
        train_max_date = ts["date"].iloc[train_end_idx - 1]
        val_min_date = ts["date"].iloc[train_end_idx]
        val_max_date = ts["date"].iloc[val_end_idx - 1]
        test_min_date = ts["date"].iloc[val_end_idx]

        assert train_max_date < val_min_date, "Temporal leakage: Train date overlaps Val date"
        assert val_max_date < test_min_date, "Temporal leakage: Val date overlaps Test date"

    def test_artifacts_loading_without_retraining(self):
        """Verify serialized LSTM model and MinMaxScaler load cleanly from disk."""
        artifacts = load_price_inference_artifacts()
        assert artifacts["model"] is not None, "Price LSTM model failed to load"
        assert artifacts["scaler"] is not None, "Price Scaler failed to load"
        assert artifacts["metadata"] is not None, "Metadata failed to load"
        assert artifacts["metadata"]["commodity"] == "Onion", "Expected Onion metadata"

    def test_prediction_output_structure_and_horizons(self):
        """Verify multi-step recursive forecasting produces valid structured output."""
        sample_prices = [1500.0 + i * 10 for i in range(35)]
        
        # Test 1-day forecast
        res_1 = predict_crop_price(sample_prices, commodity="Onion", market="Lasalgaon", forecast_horizon=1)
        assert res_1["forecast_horizon_days"] == 1
        assert len(res_1["forecasts"]) == 1
        assert res_1["trend_direction"] in ["UPWARD", "DOWNWARD", "STABLE"]

        # Test 7-day forecast
        res_7 = predict_crop_price(sample_prices, commodity="Onion", market="Lasalgaon", forecast_horizon=7)
        assert res_7["forecast_horizon_days"] == 7
        assert len(res_7["forecasts"]) == 7

        # Test 30-day forecast
        res_30 = predict_crop_price(sample_prices, commodity="Onion", market="Lasalgaon", forecast_horizon=30)
        assert res_30["forecast_horizon_days"] == 30
        assert len(res_30["forecasts"]) == 30

        # Verify no NaN or non-positive predictions
        for f in res_30["forecasts"]:
            assert not np.isnan(f["predicted_modal_price"]), "Forecast contains NaN"
            assert f["predicted_modal_price"] > 0, "Forecast must be strictly positive"

    def test_input_validation_rejection(self):
        """Verify input validation rejects insufficient length, non-numeric, NaN, and negative prices."""
        # 1. Insufficient length (<30)
        with pytest.raises(ValueError, match="insufficient"):
            validate_price_sequence_input([1000.0] * 20)

        # 2. Non-numeric
        with pytest.raises(ValueError, match="not a valid number"):
            validate_price_sequence_input(["invalid"] + [1000.0] * 29)

        # 3. None
        with pytest.raises(ValueError, match="cannot be None"):
            validate_price_sequence_input([None] + [1000.0] * 29)

        # 4. NaN
        with pytest.raises(ValueError, match="cannot be NaN"):
            validate_price_sequence_input([float("nan")] + [1000.0] * 29)

        # 5. Negative price
        with pytest.raises(ValueError, match="strictly positive"):
            validate_price_sequence_input([-50.0] + [1000.0] * 29)

        # 6. Invalid horizon (>60)
        with pytest.raises(ValueError, match="forecast_horizon must be an integer"):
            validate_price_sequence_input([1000.0] * 30, horizon=100)
