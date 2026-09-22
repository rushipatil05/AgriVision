from ml.common.paths import (
    RAW_PRICE_CSV,
    PROCESSED_PRICE_CSV,
    EDA_PRICE_DIR
)

MODULE_NAME = "price_forecasting"
RAW_DATA_PATH = RAW_PRICE_CSV
PROCESSED_DATA_PATH = PROCESSED_PRICE_CSV
EDA_OUTPUT_DIR = EDA_PRICE_DIR

# Expected Column Names in Agmarknet dataset
COL_DATE = "Arrival_Date"
COL_STATE = "State"
COL_DISTRICT = "District"
COL_MARKET = "Market"
COL_COMMODITY = "Commodity"
COL_VARIETY = "Variety"
COL_GRADE = "Grade"
COL_MIN_PRICE = "Min_Price"
COL_MAX_PRICE = "Max_Price"
COL_MODAL_PRICE = "Modal_Price"

REQUIRED_COLUMNS = [
    COL_DATE, COL_STATE, COL_DISTRICT, COL_MARKET,
    COL_COMMODITY, COL_MIN_PRICE, COL_MAX_PRICE, COL_MODAL_PRICE
]

# Benchmark crops for time-series modeling
TARGET_COMMODITIES = ["Onion", "Tomato", "Wheat", "Maize", "Bajra", "Mataki", "Gram"]

# Primary Market focus
PRIMARY_MARKETS = ["Lasalgaon", "Pimpalgaon", "Yeola", "Kalvan", "Nashik"]

# Time-series sequence parameters
SEQUENCE_LENGTH = 30   # 30-day historical lookback window
FORECAST_HORIZON = 1   # 1-day ahead forecast (configurable for multi-step)

# Split Ratios (Strictly Chronological)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
