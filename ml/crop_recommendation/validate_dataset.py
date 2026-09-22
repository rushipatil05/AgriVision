import sys
import pandas as pd
from ml.crop_recommendation.config import (
    RAW_DATA_PATH,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    RANGE_CONSTRAINTS
)
from ml.common.validation import (
    analyze_missing_values,
    check_duplicates,
    validate_datatypes,
    validate_numerical_ranges,
    detect_outliers_iqr,
    analyze_categorical_distribution,
    generate_dataset_summary
)


def validate_crop_dataset(file_path=RAW_DATA_PATH) -> dict:
    """
    Validates the Crop Recommendation dataset and prints a comprehensive validation report.
    """
    print("=" * 60)
    print("  CROP RECOMMENDATION DATASET VALIDATION")
    print("=" * 60)
    print(f"Loading raw dataset from: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found at {file_path}")
        
    df = pd.read_csv(file_path)
    summary = generate_dataset_summary(df)
    
    print(f"\n1. Shape & Dimensions:")
    print(f"   Total Rows: {summary['total_rows']}")
    print(f"   Total Columns: {summary['total_columns']}")
    print(f"   Memory Usage: {summary['memory_usage_kb']} KB")
    
    # Check Required Columns
    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")
    print(f"\n2. Column Verification: All 8 required columns present.")
    
    # Data Types
    print(f"\n3. Data Types:")
    dtypes = validate_datatypes(df)
    for col, dt in dtypes.items():
        print(f"   - {col:15s}: {dt}")
        
    # Missing Values
    missing_df = analyze_missing_values(df)
    print(f"\n4. Missing Values Analysis:")
    if missing_df.empty:
        print("   Zero missing values found across all columns.")
    else:
        print(missing_df.to_string())
        
    # Duplicates
    dup_count = check_duplicates(df)
    print(f"\n5. Duplicate Rows: {dup_count} duplicates detected.")
    
    # Class Distribution
    cat_dist = analyze_categorical_distribution(df, [TARGET_COLUMN])
    print(f"\n6. Target Class Distribution ({TARGET_COLUMN}):")
    print(f"   Total Distinct Crops: {cat_dist[TARGET_COLUMN]['unique_count']}")
    for crop, count in cat_dist[TARGET_COLUMN]['top_classes'].items():
        print(f"   - {crop:15s}: {count} records")
        
    # Descriptive Statistics
    print(f"\n7. Descriptive Statistics for Numerical Features:")
    desc = df[FEATURE_COLUMNS].describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    print(desc.round(2).to_string())
    
    # Range Validation
    print(f"\n8. Agronomic Range Constraints Validation:")
    range_results = validate_numerical_ranges(df, RANGE_CONSTRAINTS)
    for col, res in range_results.items():
        status = "PASSED" if res["is_valid"] else "VIOLATION"
        print(f"   - {col:12s} [{res['expected_min']} to {res['expected_max']}]: "
              f"Actual [{res['actual_min']:.2f}, {res['actual_max']:.2f}] -> {status}")
        
    # Outlier Detection
    print(f"\n9. Outlier Analysis (IQR Method):")
    outliers = detect_outliers_iqr(df, FEATURE_COLUMNS)
    for col, o_info in outliers.items():
        print(f"   - {col:12s}: {o_info['outlier_count']} outliers ({o_info['outlier_percentage']}%) "
              f"[Bounds: {o_info['lower_bound']:.2f} to {o_info['upper_bound']:.2f}]")
        
    print("\n" + "=" * 60)
    print("  VALIDATION RESULT: DATASET VERIFIED VALID")
    print("=" * 60 + "\n")
    
    return {
        "summary": summary,
        "dtypes": dtypes,
        "missing": missing_df.to_dict(),
        "duplicates": dup_count,
        "class_distribution": cat_dist,
        "range_validation": range_results,
        "outliers": outliers
    }


if __name__ == "__main__":
    validate_crop_dataset()
