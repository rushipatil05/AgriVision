import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.crop_recommendation.validate_dataset import validate_crop_dataset
from ml.crop_recommendation.preprocessing import process_and_save as process_crop
from ml.crop_recommendation.eda import generate_crop_eda

from ml.price_forecasting.validate_dataset import validate_price_dataset
from ml.price_forecasting.preprocessing import process_and_save_prices as process_price
from ml.price_forecasting.eda import generate_price_eda

from ml.yield_forecasting.validate_dataset import validate_yield_dataset
from ml.yield_forecasting.preprocessing import process_and_save_yield as process_yield
from ml.yield_forecasting.eda import generate_yield_eda


def run_all_level2():
    print("\n" + "#" * 70)
    print("  AGRIPULSE LEVEL 2: DATASET ACQUISITION, VALIDATION & PREPROCESSING")
    print("#" * 70 + "\n")
    
    # 1. Module A: Crop Recommendation
    print("\n>>> [MODULE 1: CROP RECOMMENDATION] <<<")
    crop_val = validate_crop_dataset()
    crop_meta = process_crop()
    generate_crop_eda()
    
    # 2. Module B: Price Forecasting
    print("\n>>> [MODULE 2: PRICE FORECASTING] <<<")
    price_val = validate_price_dataset()
    price_meta = process_price()
    generate_price_eda()
    
    # 3. Module C: Yield Forecasting
    print("\n>>> [MODULE 3: YIELD FORECASTING] <<<")
    yield_val = validate_yield_dataset()
    yield_meta = process_yield()
    generate_yield_eda()
    
    print("\n" + "#" * 70)
    print("  ALL LEVEL 2 VALIDATION, PREPROCESSING & EDA SUITES COMPLETED!")
    print("#" * 70 + "\n")


if __name__ == "__main__":
    run_all_level2()
