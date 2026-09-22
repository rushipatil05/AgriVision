import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.yield_forecasting.preprocessing import (
    load_and_clean_yield_data,
    prepare_yield_splits,
    build_and_fit_preprocessor,
    FEATURE_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    COL_PRODUCTION,
    COL_YIELD,
    COL_AREA
)
from ml.yield_forecasting.model.predict import (
    load_yield_inference_artifacts,
    validate_yield_input,
    predict_crop_yield
)
from ml.common.paths import RAW_YIELD_CSV, PROCESSED_YIELD_CSV


class TestYieldForecastingPipeline:
    """
    Automated test suite verifying the integrity of the Crop Yield Forecasting ML subsystem.
    """

    def test_dataset_files_exist(self):
        """Verify raw and processed dataset files exist on disk."""
        assert RAW_YIELD_CSV.exists(), "Raw crop production CSV missing"
        assert PROCESSED_YIELD_CSV.exists(), "Processed crop production CSV missing"

    def test_yield_calculation_and_cleaning(self):
        """Verify Yield = Production / Area formula and outlier filtering."""
        df_clean = load_and_clean_yield_data()
        assert len(df_clean) > 0, "Cleaned dataset should not be empty"
        assert COL_YIELD in df_clean.columns, "Yield column missing"
        assert (df_clean[COL_YIELD] >= 0).all(), "Yield must be non-negative"
        assert (df_clean[COL_YIELD] <= 250.0).all(), "Extreme unit recording outliers (>250 t/ha) must be filtered"
        assert (df_clean[COL_AREA] > 0).all(), "Cultivated area must be strictly positive"

    def test_zero_target_leakage_production_excluded(self):
        """CRITICAL: Explicitly verify Production is NEVER used as an input feature."""
        assert COL_PRODUCTION not in FEATURE_COLUMNS, "TARGET LEAKAGE: Production found in FEATURE_COLUMNS"
        assert COL_PRODUCTION not in CATEGORICAL_FEATURES, "TARGET LEAKAGE: Production in CATEGORICAL_FEATURES"
        assert COL_PRODUCTION not in NUMERICAL_FEATURES, "TARGET LEAKAGE: Production in NUMERICAL_FEATURES"

    def test_chronological_splits_and_temporal_isolation(self):
        """Verify strict chronological partitions: Train (<=2011), Val (2012-2013), Test (>=2014)."""
        df_clean = load_and_clean_yield_data()
        train_df, val_df, test_df = prepare_yield_splits(df_clean)

        assert len(train_df) == 71209, f"Expected 71,209 train records, got {len(train_df)}"
        assert len(val_df) == 9003, f"Expected 9,003 val records, got {len(val_df)}"
        assert len(test_df) == 3971, f"Expected 3,971 test records, got {len(test_df)}"

        # Verify temporal boundaries
        train_max_year = train_df["Crop_Year"].max()
        val_min_year = val_df["Crop_Year"].min()
        val_max_year = val_df["Crop_Year"].max()
        test_min_year = test_df["Crop_Year"].min()

        assert train_max_year <= 2011, "Train max year exceeds 2011"
        assert val_min_year == 2012, "Val min year must be 2012"
        assert val_max_year == 2013, "Val max year must be 2013"
        assert test_min_year >= 2014, "Test min year must be >= 2014"

        assert train_max_year < val_min_year, "Temporal Leakage: Train overlaps Validation"
        assert val_max_year < test_min_year, "Temporal Leakage: Validation overlaps Test"

    def test_artifacts_loading_without_retraining(self):
        """Verify preprocessor, DNN model, and tree model load from disk without retraining."""
        artifacts = load_yield_inference_artifacts()
        assert artifacts["preprocessor"] is not None, "Preprocessor failed to load"
        assert artifacts["dnn_model"] is not None, "DNN model failed to load"
        assert artifacts["tree_model"] is not None, "Tree model failed to load"
        assert artifacts["metadata"] is not None, "Metadata failed to load"

    def test_prediction_output_structure_and_sanity(self):
        """Verify yield inference returns valid non-negative, finite predictions."""
        res = predict_crop_yield(
            state="Punjab",
            district="Ludhiana",
            crop="Wheat",
            season="Rabi",
            area=40.0,
            crop_year=2024
        )
        assert isinstance(res, dict)
        assert "predicted_yield_tonnes_per_hectare" in res
        assert "estimated_total_production_tonnes" in res
        assert res["predicted_yield_tonnes_per_hectare"] > 0
        assert not np.isnan(res["predicted_yield_tonnes_per_hectare"])
        assert not np.isinf(res["predicted_yield_tonnes_per_hectare"])
        assert res["estimated_total_production_tonnes"] == round(res["predicted_yield_tonnes_per_hectare"] * 40.0, 2)

    def test_input_validation_rejection(self):
        """Verify invalid agricultural inputs are strictly rejected."""
        # 1. Missing state
        with pytest.raises(ValueError, match="State name"):
            validate_yield_input("", "Ludhiana", "Wheat", "Rabi", 10.0)

        # 2. Negative area
        with pytest.raises(ValueError, match="strictly positive"):
            validate_yield_input("Punjab", "Ludhiana", "Wheat", "Rabi", -5.0)

        # 3. NaN area
        with pytest.raises(ValueError, match="cannot be NaN"):
            validate_yield_input("Punjab", "Ludhiana", "Wheat", "Rabi", float("nan"))

        # 4. Out-of-range year
        with pytest.raises(ValueError, match="Crop Year out of valid range"):
            validate_yield_input("Punjab", "Ludhiana", "Wheat", "Rabi", 10.0, crop_year=1950)
