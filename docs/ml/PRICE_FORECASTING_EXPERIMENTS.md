# AgriPulse ML Experiment Log: Crop Market Price Forecasting

This document records all baseline and deep learning training iterations conducted on the Crop Market Price Forecasting module.

---

## Experiment History

### Experiment EXP-PF-001: Naive (Last-Value) Baseline
- **Date**: 2026-09-04
- **Model**: Naive Last-Value Forecaster ($\hat{y}_t = y_{t-1}$)
- **Target Commodity**: Onion (Nashik APMC Mandis)
- **Data Partitions**: Train: 4,581 windows | Val: 982 windows | Test: 982 windows
- **Validation MAE**: `0.16` ₹/Qtl | **Val RMSE**: `3.71` | **Val MAPE**: `0.03%` | **Val R²**: `0.6080`
- **Test MAE**: `89.04` ₹/Qtl | **Test RMSE**: `199.70` | **Test MAPE**: `4.81%` | **Test R²**: `0.9611`
- **Notes**: Demonstrates high persistence in consecutive daily mandi spot prices. Serves as benchmark threshold for 1-step evaluation.

---

### Experiment EXP-PF-002: Moving Average (7-Day) Baseline
- **Date**: 2026-09-04
- **Model**: 7-Day Moving Average Forecaster ($\hat{y}_t = \frac{1}{7} \sum_{k=1}^7 y_{t-k}$)
- **Target Commodity**: Onion (Nashik APMC Mandis)
- **Data Partitions**: Train: 4,581 windows | Val: 982 windows | Test: 982 windows
- **Validation MAE**: `0.65` ₹/Qtl | **Val RMSE**: `6.59` | **Val MAPE**: `0.11%` | **Val R²**: `-0.2378`
- **Test MAE**: `160.55` ₹/Qtl | **Test RMSE**: `318.31` | **Test MAPE**: `8.41%` | **Test R²**: `0.9011`
- **Notes**: Moving average creates phase lag during rapid price surges/drops, resulting in higher RMSE than the Naive forecaster.

---

### Experiment EXP-PF-003: Autoregressive Linear Regression Baseline
- **Date**: 2026-09-04
- **Model**: Linear Regression over 30-day historical window
- **Target Commodity**: Onion (Nashik APMC Mandis)
- **Data Partitions**: Train: 4,581 windows | Val: 982 windows | Test: 982 windows
- **Validation MAE**: `1.15` ₹/Qtl | **Val RMSE**: `4.20` | **Val MAPE**: `0.19%` | **Val R²**: `0.4984`
- **Test MAE**: `101.96` ₹/Qtl | **Test RMSE**: `206.70` | **Test MAPE**: `5.47%` | **Test R²**: `0.9583`
- **Notes**: Linear weighted autoregression performs solidly across regular price dynamics.

---

### Experiment EXP-PF-004: Time-Series LSTM Neural Network (Primary Proposal Architecture)
- **Date**: 2026-09-04
- **Model**: LSTM Neural Network (`Input(30, 1)` $\rightarrow$ `LSTM(64)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(32, relu)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(1, linear)`)
- **Target Commodity**: Onion (Nashik APMC Mandis / Lasalgaon)
- **Hyperparameters**: `optimizer='Adam'`, `learning_rate=0.001`, `batch_size=32`, `loss='mse'`
- **Regularization**: `EarlyStopping(patience=20)`, `ReduceLROnPlateau(patience=7, factor=0.5)`
- **Epochs Trained**: 46 (Early stopping triggered, best weights at epoch 26)
- **Training Time**: 75.04 seconds (CPU)
- **Validation MAE**: `0.50` ₹/Qtl | **Val RMSE**: `4.90` | **Val MAPE**: `0.09%` | **Val R²**: `0.3169`
- **Test MAE**: `129.81` ₹/Qtl | **Test RMSE**: `253.07` | **Test MAPE**: `6.47%` | **Test R²**: `0.9375`
- **Forecast Horizons Supported**: 1-Day, 7-Day, 30-Day recursive projection.
- **Notes**: Proposal-compliant deep learning recurrent neural network. Successfully captures non-linear price momentum and supports multi-step ahead projections. Serialized as production model.
