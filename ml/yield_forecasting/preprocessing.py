import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.yield_forecasting.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    COL_STATE,
    COL_DISTRICT,
    COL_YEAR,
    COL_SEASON,
    COL_CROP,
    COL_AREA,
    COL_PRODUCTION,
    COL_YIELD,
    BENCHMARK_CROPS,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR
)

# Explicit Feature Definitions - Production is STRICTLY EXCLUDED to prevent target leakage
CATEGORICAL_FEATURES = [COL_STATE, COL_DISTRICT, COL_CROP, COL_SEASON]
NUMERICAL_FEATURES = [COL_AREA, COL_YEAR]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES


def load_and_clean_yield_data(file_path=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw crop production dataset and applies agronomic cleaning rules:
    1. Removes rows where Production is NaN (1.5% of raw records).
    2. Filters out zero or negative Area entries (Area > 0).
    3. Trims whitespace from string columns.
    4. Computes Yield = Production / Area (Tonnes per Hectare).
    5. Filters unit recording anomalies (Yield <= 250 Tonnes/ha, removing 0.06% corrupt outliers).
    6. Filters to the 10 major benchmark agricultural crops.
    """
    df = pd.read_csv(file_path)
    
    # 1. Clean string categorical columns
    for col in [COL_STATE, COL_DISTRICT, COL_SEASON, COL_CROP]:
        df[col] = df[col].astype(str).str.strip()
        
    # 2. Filter valid physical area and non-null production
    valid_mask = (df[COL_AREA] > 0) & (df[COL_PRODUCTION].notnull()) & (df[COL_PRODUCTION] >= 0)
    df_clean = df[valid_mask].copy()
    
    # 3. Compute Yield (Tonnes / Hectare)
    df_clean[COL_YIELD] = df_clean[COL_PRODUCTION] / df_clean[COL_AREA]
    
    # 4. Filter benchmark crops and unit recording anomalies
    df_clean = df_clean[
        (df_clean[COL_CROP].isin(BENCHMARK_CROPS)) &
        (df_clean[COL_YIELD] <= 250.0)
    ].copy()
    
    # 5. Sort strictly chronologically by Crop_Year
    df_clean = df_clean.sort_values(by=[COL_YEAR, COL_STATE, COL_CROP]).reset_index(drop=True)
    return df_clean


def prepare_yield_splits(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the crop yield dataset strictly chronologically based on Crop_Year:
    - Train: Crop_Year <= 2011 (1997-2011)
    - Validation: 2012 <= Crop_Year <= 2013 (2012-2013)
    - Test: Crop_Year >= 2014 (2014-2015)
    """
    train_df = df[df[COL_YEAR] <= TRAIN_MAX_YEAR].copy()
    val_df = df[(df[COL_YEAR] > TRAIN_MAX_YEAR) & (df[COL_YEAR] <= VAL_MAX_YEAR)].copy()
    test_df = df[df[COL_YEAR] > VAL_MAX_YEAR].copy()
    
    return train_df, val_df, test_df


def build_and_fit_preprocessor(
    train_df: pd.DataFrame
) -> ColumnTransformer:
    """
    Builds and fits a ColumnTransformer ONLY on the training partition:
    - StandardScaler on numerical features [Area, Crop_Year]
    - OneHotEncoder on categorical features [State_Name, District_Name, Crop, Season]
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=10), CATEGORICAL_FEATURES)
        ]
    )
    preprocessor.fit(train_df[FEATURE_COLUMNS])
    return preprocessor


def process_and_save_yield(
    raw_path=RAW_DATA_PATH,
    processed_path=PROCESSED_DATA_PATH
) -> Dict[str, Any]:
    """
    Executes end-to-end yield dataset preprocessing and saves cleaned dataset.
    """
    df_clean = load_and_clean_yield_data(raw_path)
    
    # Save processed dataset
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    
    train_df, val_df, test_df = prepare_yield_splits(df_clean)
    preprocessor = build_and_fit_preprocessor(train_df)
    
    metadata = {
        "raw_total_records": 246091,
        "cleaned_benchmark_records": len(df_clean),
        "benchmark_crops": BENCHMARK_CROPS,
        "features_used": FEATURE_COLUMNS,
        "leakage_check_production_excluded": True,
        "train_records": len(train_df),
        "val_records": len(val_df),
        "test_records": len(test_df),
        "year_splits": {
            "train_years": f"<= {TRAIN_MAX_YEAR} (1997-{TRAIN_MAX_YEAR})",
            "val_years": f"{TRAIN_MAX_YEAR + 1} - {VAL_MAX_YEAR}",
            "test_years": f">= {VAL_MAX_YEAR + 1} (2014-2015)"
        },
        "encoded_feature_dimensions": int(preprocessor.transform(train_df[FEATURE_COLUMNS][:5]).shape[1]),
        "processed_file": str(processed_path)
    }
    
    print(f"Crop Yield preprocessing complete: {len(df_clean):,} cleaned benchmark records.")
    print(f"Partitions (Chronological) -> Train: {len(train_df):,}, Val: {len(val_df):,}, Test: {len(test_df):,}")
    print(f"Features Encoded: {metadata['encoded_feature_dimensions']} columns (Production strictly excluded).")
    print(f"Processed dataset saved to: {processed_path.name}")
    return metadata


if __name__ == "__main__":
    process_and_save_yield()
