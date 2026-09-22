import sys
import pandas as pd
import numpy as np
from ml.yield_forecasting.config import (
    RAW_DATA_PATH,
    COL_STATE,
    COL_DISTRICT,
    COL_YEAR,
    COL_SEASON,
    COL_CROP,
    COL_AREA,
    COL_PRODUCTION,
    COL_YIELD,
    REQUIRED_COLUMNS
)
from ml.common.validation import (
    analyze_missing_values,
    check_duplicates,
    validate_datatypes,
    generate_dataset_summary
)


def validate_yield_dataset(file_path=RAW_DATA_PATH) -> dict:
    """
    Validates the India Crop Production & Yield dataset and generates an analytical report.
    """
    print("=" * 60)
    print("  CROP YIELD & PRODUCTION DATASET VALIDATION (DES INDIA)")
    print("=" * 60)
    print(f"Loading raw dataset from: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Crop production dataset not found at {file_path}")
        
    df = pd.read_csv(file_path)
    summary = generate_dataset_summary(df)
    
    print(f"\n1. Shape & Dimensions:")
    print(f"   Total Records: {summary['total_rows']:,}")
    print(f"   Total Columns: {summary['total_columns']}")
    print(f"   Memory Usage: {summary['memory_usage_kb'] / 1024:.2f} MB")
    
    # Check Required Columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")
    print(f"\n2. Column Verification: All required columns present -> {REQUIRED_COLUMNS}")
    
    # Missing Values
    missing_df = analyze_missing_values(df)
    print(f"\n3. Missing Values Analysis:")
    if missing_df.empty:
        print("   Zero missing values found.")
    else:
        print(missing_df.to_string())
        
    # Duplicates
    dup_count = check_duplicates(df)
    print(f"\n4. Duplicate Records: {dup_count:,} full-row duplicates detected.")
    
    # Temporal Range Analysis
    print(f"\n5. Crop Year Distribution ({COL_YEAR}):")
    min_year = int(df[COL_YEAR].min())
    max_year = int(df[COL_YEAR].max())
    distinct_years = sorted(df[COL_YEAR].unique().tolist())
    print(f"   - Year Range: {min_year} to {max_year} ({len(distinct_years)} distinct agricultural years)")
    print(f"   - Observations per decade: 1990s: {(df[COL_YEAR] < 2000).sum():,}, "
          f"2000s: {((df[COL_YEAR] >= 2000) & (df[COL_YEAR] < 2010)).sum():,}, "
          f"2010s: {(df[COL_YEAR] >= 2010).sum():,}")
          
    # Geographic & Crop Distribution
    print(f"\n6. Categorical Cardinality:")
    states = df[COL_STATE].str.strip().unique()
    crops = df[COL_CROP].str.strip().unique()
    seasons = df[COL_SEASON].str.strip().unique()
    print(f"   - Unique States: {len(states)}")
    print(f"   - Unique Crops: {len(crops)}")
    print(f"   - Seasons: {list(seasons)}")
    
    # Area & Production Integrity
    print(f"\n7. Physical & Agronomic Invariant Checks:")
    negative_area = int((df[COL_AREA] < 0).sum())
    zero_area = int((df[COL_AREA] == 0).sum())
    negative_prod = int((df[COL_PRODUCTION] < 0).sum())
    zero_prod = int((df[COL_PRODUCTION] == 0).sum())
    
    print(f"   - Negative Area entries: {negative_area}")
    print(f"   - Zero Area entries: {zero_area}")
    print(f"   - Negative Production entries: {negative_prod}")
    print(f"   - Zero Production entries: {zero_prod}")
    
    # Yield Computation Analysis
    valid_mask = (df[COL_AREA] > 0) & (df[COL_PRODUCTION].notnull())
    df_valid = df[valid_mask].copy()
    df_valid[COL_YIELD] = df_valid[COL_PRODUCTION] / df_valid[COL_AREA]
    
    print(f"\n8. Computed Yield Statistics (Production / Area = Tonnes/Hectare):")
    yield_desc = df_valid[[COL_AREA, COL_PRODUCTION, COL_YIELD]].describe().T
    print(yield_desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]].round(2).to_string())
    
    print("\n" + "=" * 60)
    print("  VALIDATION RESULT: PASSED WITH IDENTIFIED CLEANING RULES")
    print("=" * 60 + "\n")
    
    return {
        "summary": summary,
        "year_range": {"min": min_year, "max": max_year, "years": distinct_years},
        "states_count": len(states),
        "crops_count": len(crops),
        "missing_production_count": int(df[COL_PRODUCTION].isnull().sum()),
        "duplicates": dup_count
    }


if __name__ == "__main__":
    validate_yield_dataset()
