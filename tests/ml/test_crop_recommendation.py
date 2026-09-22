import sys
from pathlib import Path
import pytest
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.crop_recommendation.preprocessing import load_raw_data, prepare_crop_splits
from ml.crop_recommendation.model.model_utils import reshape_tabular_to_sequence, calculate_top_k_accuracy
from ml.crop_recommendation.model.predict import (
    load_inference_artifacts,
    validate_crop_inputs,
    predict_crop_recommendation
)
from ml.common.paths import RAW_CROP_REC_CSV, PROCESSED_CROP_REC_CSV


class TestCropRecommendationPipeline:
    """
    Automated test suite verifying the integrity of the Crop Recommendation ML pipeline.
    """

    def test_dataset_files_exist(self):
        """Verify raw and processed dataset files exist on disk."""
        assert RAW_CROP_REC_CSV.exists(), "Raw dataset file missing"
        assert PROCESSED_CROP_REC_CSV.exists(), "Processed dataset file missing"

    def test_preprocessing_splits_and_shapes(self):
        """Verify 70/15/15 stratified partition sizes and feature dimensions."""
        df = load_raw_data()
        assert len(df) == 2200, f"Expected 2200 records, found {len(df)}"

        X_train, X_val, X_test, y_train, y_val, y_test, scaler, le = prepare_crop_splits(df)
        assert len(X_train) == 1540, f"Expected 1540 train samples, got {len(X_train)}"
        assert len(X_val) == 330, f"Expected 330 val samples, got {len(X_val)}"
        assert len(X_test) == 330, f"Expected 330 test samples, got {len(X_test)}"
        assert X_train.shape[1] == 7, "Expected 7 input features"
        assert len(le.classes_) == 22, "Expected 22 unique crop classes"

    def test_sequence_reshaping(self):
        """Verify tabular-to-sequence transformation produces (N, 7, 1)."""
        dummy_data = np.random.randn(10, 7)
        seq_data = reshape_tabular_to_sequence(dummy_data)
        assert seq_data.shape == (10, 7, 1), f"Expected shape (10, 7, 1), got {seq_data.shape}"

    def test_artifacts_loading_without_retraining(self):
        """Verify serialized model, scaler, and metadata load cleanly from disk."""
        artifacts = load_inference_artifacts()
        assert artifacts["model"] is not None, "Model failed to load"
        assert artifacts["scaler"] is not None, "Scaler failed to load"
        assert artifacts["class_names"] is not None, "Class names failed to load"
        assert len(artifacts["class_names"]) == 22, "Expected 22 class names in metadata"

    def test_prediction_output_structure_and_sorting(self):
        """Verify inference returns valid top-k list sorted descending by probability."""
        recommendations = predict_crop_recommendation(
            n=90, p=42, k=43,
            temperature=20.87, humidity=82.00, ph=6.50, rainfall=202.93,
            top_k=5
        )
        assert len(recommendations) == 5, f"Expected 5 recommendations, got {len(recommendations)}"
        
        # Check keys and probability types
        for item in recommendations:
            assert "crop" in item, "Missing 'crop' key in recommendation"
            assert "probability" in item, "Missing 'probability' key in recommendation"
            assert 0.0 <= item["probability"] <= 1.0, f"Invalid probability value {item['probability']}"

        # Check descending order
        probs = [item["probability"] for item in recommendations]
        assert probs == sorted(probs, reverse=True), "Recommendations must be sorted descending by probability"

    def test_input_validation_rejection(self):
        """Verify input validation rejects missing, non-numeric, NaN, and impossible values."""
        # 1. Non-numeric
        with pytest.raises(ValueError, match="must be a valid real number"):
            validate_crop_inputs(n="invalid", p=40, k=40, temperature=25, humidity=70, ph=6.5, rainfall=100)

        # 2. None
        with pytest.raises(ValueError, match="cannot be None"):
            validate_crop_inputs(n=None, p=40, k=40, temperature=25, humidity=70, ph=6.5, rainfall=100)

        # 3. NaN
        with pytest.raises(ValueError, match="cannot be NaN"):
            validate_crop_inputs(n=float("nan"), p=40, k=40, temperature=25, humidity=70, ph=6.5, rainfall=100)

        # 4. Out-of-bounds pH (e.g. pH 15 is impossible)
        with pytest.raises(ValueError, match="outside acceptable range"):
            validate_crop_inputs(n=50, p=40, k=40, temperature=25, humidity=70, ph=15.0, rainfall=100)

        # 5. Out-of-bounds humidity (>100%)
        with pytest.raises(ValueError, match="outside acceptable range"):
            validate_crop_inputs(n=50, p=40, k=40, temperature=25, humidity=120.0, ph=6.5, rainfall=100)

    def test_top_k_accuracy_helper(self):
        """Verify top_k_accuracy calculation logic."""
        y_true = np.array([0, 1, 2])
        # 3 samples, 4 classes
        y_prob = np.array([
            [0.7, 0.2, 0.1, 0.0],  # true label 0 is rank 1 -> top 1, 3, 5
            [0.1, 0.6, 0.2, 0.1],  # true label 1 is rank 1 -> top 1, 3, 5
            [0.4, 0.3, 0.2, 0.1]   # true label 2 is rank 3 -> top 3, 5 (not top 1)
        ])
        assert calculate_top_k_accuracy(y_true, y_prob, k=1) == pytest.approx(2/3, 0.01)
        assert calculate_top_k_accuracy(y_true, y_prob, k=3) == pytest.approx(1.0, 0.01)
