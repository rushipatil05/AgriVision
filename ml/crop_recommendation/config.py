from ml.common.paths import (
    RAW_CROP_REC_CSV,
    PROCESSED_CROP_REC_CSV,
    EDA_CROP_REC_DIR
)

MODULE_NAME = "crop_recommendation"
RAW_DATA_PATH = RAW_CROP_REC_CSV
PROCESSED_DATA_PATH = PROCESSED_CROP_REC_CSV
EDA_OUTPUT_DIR = EDA_CROP_REC_DIR

# Feature definitions
FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN = "label"

# Agronomic range constraints for validation
RANGE_CONSTRAINTS = {
    "N": {"min": 0.0, "max": 200.0},
    "P": {"min": 0.0, "max": 200.0},
    "K": {"min": 0.0, "max": 250.0},
    "temperature": {"min": 0.0, "max": 60.0},
    "humidity": {"min": 0.0, "max": 100.0},
    "ph": {"min": 3.0, "max": 10.0},
    "rainfall": {"min": 0.0, "max": 500.0}
}

# Split Ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_STATE = 42
