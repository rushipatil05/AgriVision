from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes total missing count and percentage for each column.
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    report = pd.DataFrame({
        "Missing_Count": missing_count,
        "Missing_Percentage": missing_pct.round(2)
    })
    return report[report["Missing_Count"] > 0]


def check_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> int:
    """
    Returns the total count of duplicate rows.
    """
    return int(df.duplicated(subset=subset).sum())


def validate_datatypes(df: pd.DataFrame) -> Dict[str, str]:
    """
    Returns mapping of column names to their data types.
    """
    return {col: str(dtype) for col, dtype in df.dtypes.items()}


def validate_numerical_ranges(
    df: pd.DataFrame,
    bounds: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[str, Any]]:
    """
    Validates whether numeric columns fall within expected bounds.
    bounds example: {"ph": {"min": 0.0, "max": 14.0}}
    """
    violations = {}
    for col, limits in bounds.items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            min_val = limits.get("min", -np.inf)
            max_val = limits.get("max", np.inf)
            
            below_min = int((df[col] < min_val).sum())
            above_max = int((df[col] > max_val).sum())
            
            violations[col] = {
                "expected_min": min_val,
                "expected_max": max_val,
                "actual_min": float(df[col].min()),
                "actual_max": float(df[col].max()),
                "actual_mean": float(df[col].mean()),
                "actual_std": float(df[col].std()),
                "below_min_count": below_min,
                "above_max_count": above_max,
                "is_valid": (below_min == 0 and above_max == 0)
            }
    return violations


def detect_outliers_iqr(
    df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    factor: float = 1.5
) -> Dict[str, Dict[str, Any]]:
    """
    Detects outliers using the Interquartile Range (IQR) method.
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
    outlier_report = {}
    for col in numeric_cols:
        series = df[col].dropna()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (factor * iqr)
        upper_bound = q3 + (factor * iqr)
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_report[col] = {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "outlier_count": int(len(outliers)),
            "outlier_percentage": round((len(outliers) / len(df)) * 100, 2)
        }
    return outlier_report


def analyze_categorical_distribution(
    df: pd.DataFrame,
    cat_cols: Optional[List[str]] = None,
    top_n: int = 10
) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes frequency distribution and distinct cardinalities of categorical columns.
    """
    if cat_cols is None:
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
    distribution = {}
    for col in cat_cols:
        distribution[col] = {
            "unique_count": int(df[col].nunique()),
            "top_classes": df[col].value_counts().head(top_n).to_dict()
        }
    return distribution


def generate_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Produces high-level statistical and structural summary of dataset.
    """
    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "memory_usage_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
        "total_missing_cells": int(df.isnull().sum().sum()),
        "total_duplicate_rows": int(df.duplicated().sum())
    }
