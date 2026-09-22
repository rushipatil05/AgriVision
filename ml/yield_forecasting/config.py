from ml.common.paths import (
    RAW_YIELD_CSV,
    PROCESSED_YIELD_CSV,
    EDA_YIELD_DIR
)

MODULE_NAME = "yield_forecasting"
RAW_DATA_PATH = RAW_YIELD_CSV
PROCESSED_DATA_PATH = PROCESSED_YIELD_CSV
EDA_OUTPUT_DIR = EDA_YIELD_DIR

# Column names in DES Crop Production dataset
COL_STATE = "State_Name"
COL_DISTRICT = "District_Name"
COL_YEAR = "Crop_Year"
COL_SEASON = "Season"
COL_CROP = "Crop"
COL_AREA = "Area"
COL_PRODUCTION = "Production"
COL_YIELD = "Yield"   # Computed feature: Production / Area

REQUIRED_COLUMNS = [COL_STATE, COL_DISTRICT, COL_YEAR, COL_SEASON, COL_CROP, COL_AREA, COL_PRODUCTION]

# Major benchmark crops
BENCHMARK_CROPS = ["Rice", "Wheat", "Maize", "Sugarcane", "Cotton(lint)", "Bajra", "Jowar", "Gram", "Groundnut", "Potato"]

# Temporal train/val/test threshold years (Chronological Split)
TRAIN_MAX_YEAR = 2011   # <= 2011 (~70%)
VAL_MAX_YEAR = 2013     # 2012-2013 (~15%)
# Test set: >= 2014 (~15%)
