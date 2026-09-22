# AgriPulse ML Experiment Log: Crop Yield Forecasting

This document tracks all baseline and deep learning experiments conducted for the Crop Yield Forecasting subsystem.

---

## Experiment History

### Experiment EXP-YLD-001: Median Baseline Regressor
- **Date**: 2026-09-04
- **Model**: Global Median Yield Baseline
- **Data Partitions**: Train: 71,209 | Val: 9,003 | Test: 3,971
- **Validation MAE**: `7.108` t/ha | **Val RMSE**: `20.046` | **Val R²**: `-0.1256` | **Val MedAE**: `0.861`
- **Test MAE**: `7.130` t/ha | **Test RMSE**: `20.099` | **Test R²**: `-0.1247` | **Test MedAE**: `0.827`
- **Notes**: Serves as the naive central tendency benchmark.

---

### Experiment EXP-YLD-002: Ridge Linear Regression Baseline
- **Date**: 2026-09-04
- **Model**: Ridge Linear Regression ($\alpha = 1.0$)
- **Data Partitions**: Train: 71,209 | Val: 9,003 | Test: 3,971
- **Validation MAE**: `3.896` t/ha | **Val RMSE**: `8.889` | **Val R²**: `0.7786` | **Val MedAE**: `1.578`
- **Test MAE**: `3.605` t/ha | **Test RMSE**: `8.706` | **Test R²**: `0.7890` | **Test MedAE**: `1.522`
- **Notes**: Captures linear main effects of crop, state, and area.

---

### Experiment EXP-YLD-003: Histogram Gradient Boosting Regressor
- **Date**: 2026-09-04
- **Model**: HistGradientBoostingRegressor (`max_iter=150`, `learning_rate=0.08`, `max_depth=12`)
- **Data Partitions**: Train: 71,209 | Val: 9,003 | Test: 3,971
- **Validation MAE**: `2.042` t/ha | **Val RMSE**: `6.635` | **Val R²**: `0.8767` | **Val MedAE**: `0.575`
- **Test MAE**: `1.884` t/ha | **Test RMSE**: `6.208` | **Test R²**: `0.8927` | **Test MedAE**: `0.567`
- **Training Time**: 11.23 seconds
- **Notes**: Fast, robust non-linear interaction modeling across 662 sparse features.

---

### Experiment EXP-YLD-004: Random Forest Regressor
- **Date**: 2026-09-04
- **Model**: RandomForestRegressor (`n_estimators=100`, `max_depth=18`)
- **Data Partitions**: Train: 71,209 | Val: 9,003 | Test: 3,971
- **Validation MAE**: `1.857` t/ha | **Val RMSE**: `6.163` | **Val R²**: `0.8936` | **Val MedAE**: `0.436`
- **Test MAE**: `1.783` t/ha | **Test RMSE**: `5.901` | **Test R²**: `0.9031` | **Test MedAE**: `0.467`
- **Training Time**: 94.48 seconds
- **Notes**: Very strong performance across non-linear geographical and seasonal boundaries.

---

### Experiment EXP-YLD-005: Deep Neural Network Regressor (Primary Proposal Architecture)
- **Date**: 2026-09-04
- **Model**: Deep Neural Network (`Input(662)` $\rightarrow$ `Dense(128, relu)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(64, relu)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(32, relu)` $\rightarrow$ `Dense(1, linear)`)
- **Hyperparameters**: `optimizer='Adam'`, `learning_rate=0.001`, `batch_size=64`, `loss='mse'`
- **Callbacks**: `EarlyStopping(patience=15)`, `ReduceLROnPlateau(patience=5, factor=0.5)`
- **Epochs Trained**: 19 (Early stopping triggered, best weights at epoch 4)
- **Training Time**: 64.88 seconds
- **Validation MAE**: `1.781` t/ha | **Val RMSE**: `5.866` | **Val R²**: `0.9036` | **Val MedAE**: `0.512`
- **Test MAE**: `1.697` t/ha | **Test RMSE**: `5.478` | **Test R²**: `0.9165` | **Test MedAE**: `0.537`
- **Notes**: Best overall generalization on untouched test partition. Selected as production yield engine.
