import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from ml.crop_recommendation.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    RANDOM_STATE
)


def load_raw_data(filepath=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw Crop Recommendation dataset from disk.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Raw data not found at: {filepath}")
    return pd.read_csv(filepath)


def prepare_crop_splits(
    df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, LabelEncoder]:
    """
    Preprocesses the crop recommendation dataset with strict separation to prevent data leakage:
    1. Splits dataset into Train (70%), Validation (15%), and Test (15%) stratified by crop label.
    2. Encodes target labels into numerical integers.
    3. Fits StandardScaler ONLY on training features (X_train), then transforms X_val and X_test.
    
    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder
    """
    # 1. Feature / Target extraction
    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values
    
    # 2. Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 3. Stratified Train / (Val + Test) split
    val_test_ratio = VAL_RATIO + TEST_RATIO
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_encoded,
        test_size=val_test_ratio,
        random_state=RANDOM_STATE,
        stratify=y_encoded
    )
    
    # 4. Stratified Val / Test split (50/50 split of the remaining 30%)
    relative_test_ratio = TEST_RATIO / val_test_ratio
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=relative_test_ratio,
        random_state=RANDOM_STATE,
        stratify=y_temp
    )
    
    # 5. Fit StandardScaler ONLY on Training Data (Prevent Data Leakage)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, scaler, label_encoder


def process_and_save(
    raw_path=RAW_DATA_PATH,
    processed_path=PROCESSED_DATA_PATH
) -> Dict[str, Any]:
    """
    Executes end-to-end preprocessing pipeline and saves processed dataset with split tags.
    """
    df = load_raw_data(raw_path)
    
    # Perform reproducible stratified split assignment
    label_encoder = LabelEncoder()
    df_proc = df.copy()
    df_proc["label_encoded"] = label_encoder.fit_transform(df_proc[TARGET_COLUMN])
    
    X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, scaler, le = prepare_crop_splits(df)
    
    # Save a reference processed dataset
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_proc.to_csv(processed_path, index=False)
    
    metadata = {
        "total_records": len(df),
        "train_samples": len(X_train_scaled),
        "val_samples": len(X_val_scaled),
        "test_samples": len(X_test_scaled),
        "features": FEATURE_COLUMNS,
        "classes_count": len(label_encoder.classes_),
        "classes": list(label_encoder.classes_),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "processed_file": str(processed_path)
    }
    
    print(f"Crop Recommendation preprocessing complete: {len(df)} rows processed.")
    print(f"Splits -> Train: {len(X_train_scaled)}, Val: {len(X_val_scaled)}, Test: {len(X_test_scaled)}")
    print(f"Processed dataset saved to: {processed_path.name}")
    return metadata


if __name__ == "__main__":
    process_and_save()
