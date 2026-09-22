from pathlib import Path

# Compute project root dynamically (assumes paths.py is in ml/common/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ML Subsystem Roots
ML_DIR = PROJECT_ROOT / "ml"
DOCS_DIR = PROJECT_ROOT / "docs"

# Module Data Paths
CROP_REC_DIR = ML_DIR / "crop_recommendation"
PRICE_DIR = ML_DIR / "price_forecasting"
YIELD_DIR = ML_DIR / "yield_forecasting"

# Raw Data Paths
RAW_CROP_REC_CSV = CROP_REC_DIR / "data" / "raw" / "crop_recommendation.csv"
RAW_PRICE_CSV = PRICE_DIR / "data" / "raw" / "agmarknet_commodity_prices.csv"
RAW_YIELD_CSV = YIELD_DIR / "data" / "raw" / "crop_production.csv"

# Processed Data Paths
PROCESSED_CROP_REC_CSV = CROP_REC_DIR / "data" / "processed" / "crop_recommendation_processed.csv"
PROCESSED_PRICE_CSV = PRICE_DIR / "data" / "processed" / "price_forecasting_processed.csv"
PROCESSED_YIELD_CSV = YIELD_DIR / "data" / "processed" / "yield_forecasting_processed.csv"

# EDA Output Paths
EDA_CROP_REC_DIR = CROP_REC_DIR / "results" / "eda"
EDA_PRICE_DIR = PRICE_DIR / "results" / "eda"
EDA_YIELD_DIR = YIELD_DIR / "results" / "eda"
