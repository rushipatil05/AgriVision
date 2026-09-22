import sys
import pandas as pd
import numpy as np
from ml.price_forecasting.config import (
    RAW_DATA_PATH,
    COL_DATE,
    COL_STATE,
    COL_DISTRICT,
    COL_MARKET,
    COL_COMMODITY,
    COL_VARIETY,
    COL_MIN_PRICE,
    COL_MAX_PRICE,
    COL_MODAL_PRICE,
    REQUIRED_COLUMNS
)
from ml.common.validation import (
    analyze_missing_values,
    check_duplicates,
    validate_datatypes,
    generate_dataset_summary
)


def validate_price_dataset(file_path=RAW_DATA_PATH) -> dict:
    """
    Validates the Agmarknet Commodity Price dataset and generates a comprehensive report.
    """
    print("=" * 60)
    print("  CROP PRICE FORECASTING DATASET VALIDATION (AGMARKNET)")
    print("=" * 60)
    print(f"Loading raw dataset from: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Price dataset file not found at {file_path}")
        
    df = pd.read_csv(file_path)
    summary = generate_dataset_summary(df)
    
    print(f"\n1. Shape & Dimensions:")
    print(f"   Total Records: {summary['total_rows']}")
    print(f"   Total Columns: {summary['total_columns']}")
    print(f"   Memory Usage: {summary['memory_usage_kb']} KB")
    
    # Check Required Columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")
    print(f"\n2. Column Verification: All required columns present -> {REQUIRED_COLUMNS}")
    
    # Missing Values
    missing_df = analyze_missing_values(df)
    print(f"\n3. Missing Values Analysis:")
    if missing_df.empty:
        print("   Zero missing values found across all columns.")
    else:
        print(missing_df.to_string())
        
    # Duplicates
    dup_count = check_duplicates(df)
    print(f"\n4. Duplicate Records: {dup_count} full-row duplicates detected.")
    
    # Date Parsing & Range
    print(f"\n5. Temporal / Date Analysis ({COL_DATE}):")
    # Handle multiple date formats safely
    parsed_dates = pd.to_datetime(df[COL_DATE], format="%d/%m/%Y", errors="coerce")
    invalid_dates = parsed_dates.isna().sum()
    print(f"   - Invalid/Unparseable Dates: {invalid_dates}")
    valid_dates = parsed_dates.dropna()
    min_date = valid_dates.min().strftime("%Y-%m-%d")
    max_date = valid_dates.max().strftime("%Y-%m-%d")
    total_days = (valid_dates.max() - valid_dates.min()).days
    print(f"   - Date Range: {min_date} to {max_date} (Span: {total_days} days)")
    
    # Commodity & Market Cardinalities
    print(f"\n6. Geographical & Commodity Scope:")
    unique_commodities = df[COL_COMMODITY].dropna().unique()
    unique_markets = df[COL_MARKET].dropna().unique()
    unique_districts = df[COL_DISTRICT].dropna().unique()
    unique_states = df[COL_STATE].dropna().unique()
    print(f"   - Number of Commodities: {len(unique_commodities)}")
    print(f"     Top Commodities: {list(unique_commodities[:8])}")
    print(f"   - Number of Markets (Mandis): {len(unique_markets)}")
    print(f"     Top Markets: {list(unique_markets[:8])}")
    print(f"   - Number of Districts: {len(unique_districts)}")
    print(f"   - Number of States: {len(unique_states)}")
    
    # Price Invariant Checks
    print(f"\n7. Price Invariants & Economic Integrity Checks:")
    negative_min = int((df[COL_MIN_PRICE] < 0).sum())
    negative_max = int((df[COL_MAX_PRICE] < 0).sum())
    negative_modal = int((df[COL_MODAL_PRICE] < 0).sum())
    min_gt_max = int((df[COL_MIN_PRICE] > df[COL_MAX_PRICE]).sum())
    modal_lt_min = int((df[COL_MODAL_PRICE] < df[COL_MIN_PRICE]).sum())
    modal_gt_max = int((df[COL_MODAL_PRICE] > df[COL_MAX_PRICE]).sum())
    zero_prices = int((df[COL_MODAL_PRICE] == 0).sum())
    
    print(f"   - Negative Prices (Min/Max/Modal): {negative_min} / {negative_max} / {negative_modal}")
    print(f"   - Invariant Violation (Min > Max): {min_gt_max} records")
    print(f"   - Invariant Violation (Modal < Min): {modal_lt_min} records")
    print(f"   - Invariant Violation (Modal > Max): {modal_gt_max} records")
    print(f"   - Zero Modal Prices: {zero_prices} records")
    
    # Price Descriptive Statistics
    print(f"\n8. Modal Price Descriptive Statistics (INR / Quintal):")
    price_desc = df[[COL_MIN_PRICE, COL_MAX_PRICE, COL_MODAL_PRICE]].describe().T
    print(price_desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]].round(2).to_string())
    
    is_valid = (invalid_dates == 0 and negative_modal == 0 and min_gt_max == 0)
    print("\n" + "=" * 60)
    print(f"  VALIDATION RESULT: {'PASSED (DATA INTEGRITY SOUND)' if is_valid else 'REQUIRES CLEANING IN PREPROCESSING'}")
    print("=" * 60 + "\n")
    
    return {
        "summary": summary,
        "date_range": {"min": min_date, "max": max_date, "total_days": total_days},
        "commodities_count": len(unique_commodities),
        "markets_count": len(unique_markets),
        "missing_values": missing_df.to_dict(),
        "duplicates": dup_count,
        "price_anomalies": {
            "min_gt_max": min_gt_max,
            "modal_outside_bounds": modal_lt_min + modal_gt_max,
            "negative_prices": negative_min + negative_max + negative_modal,
            "zero_prices": zero_prices
        }
    }


if __name__ == "__main__":
    validate_price_dataset()
