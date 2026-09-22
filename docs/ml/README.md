# AgriPulse: Master Machine Learning & AI System Overview

**Project**: AgriPulse — Precision Agriculture Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  

---

## AI Subsystem Status Dashboard

| Module | Model Family | Task | Current Status | Validation Status | Production Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Crop Recommendation** | **LSTM Neural Network** | Multiclass Classification & Top-5 Ranking | **IMPLEMENTED (COMPLETE)** | 98.48% Test Accuracy, 100% Top-5 Acc | `crop_recommendation_lstm.keras` |
| **2. Crop Price Forecasting** | **Time-Series LSTM** | Multi-Step Mandi Spot Price Forecasting | **IMPLEMENTED (COMPLETE)** | 6.47% Test MAPE, $R^2 = 0.9375$ | `crop_price_lstm.keras` |
| **3. Crop Yield Forecasting** | **Deep Neural Network Regressor** | Regional Acreage & Yield (Tonnes/ha) Estimation | **IMPLEMENTED (COMPLETE)** | 1.697 Test MAE, $R^2 = 0.9165$ | `crop_yield_dnn.keras` |

---

## 1. Crop Recommendation AI Module (Implemented)

- **Dataset**: `ml/crop_recommendation/data/raw/crop_recommendation.csv` ($2,200$ samples, 22 balanced classes)
- **Features**: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`
- **Architecture**: LSTM Neural Network (`Input(7, 1)` $\rightarrow$ `LSTM(64)` $\rightarrow$ `Dense(64)` $\rightarrow$ `Softmax(22)`)
- **Performance**:
  - Test Accuracy: **$98.48\%$**
  - Top-3 Accuracy: **$100.00\%$**
  - Top-5 Accuracy: **$100.00\%$**
- **Inference Module**: `ml/crop_recommendation/model/predict.py`
- **Documentation**:
  - [Model Card](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/CROP_RECOMMENDATION_MODEL.md)
  - [Experiment Log](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/CROP_RECOMMENDATION_EXPERIMENTS.md)

---

## 2. Crop Market Price Forecasting AI Module (Implemented)

- **Dataset**: `ml/price_forecasting/data/raw/agmarknet_commodity_prices.csv` ($20,500$ Agmarknet mandi records)
- **Primary Benchmark Series**: **Onion (Nashik APMC Mandis / Lasalgaon Hub)** ($6,575$ continuous daily points, $4,581$ Train, $982$ Val, $982$ Test)
- **Target**: `Modal_Price` (INR / Quintal)
- **Architecture**: Time-Series LSTM (`Input(30, 1)` $\rightarrow$ `LSTM(64)` $\rightarrow$ `Dense(32)` $\rightarrow$ `Dense(1)`)
- **Performance**:
  - Test MAE: **₹129.81 / Quintal**
  - Test RMSE: **₹253.07 / Quintal**
  - Test MAPE: **6.47%**
  - Test $R^2$: **0.9375**
- **Forecast Horizons**: 1-Day, 7-Day, 30-Day recursive projection with trend direction and percentage change.
- **Inference Module**: `ml/price_forecasting/model/predict.py`
- **Documentation**:
  - [Model Card](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/PRICE_FORECASTING_MODEL.md)
  - [Experiment Log](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/PRICE_FORECASTING_EXPERIMENTS.md)

---

## 3. Crop Yield Forecasting AI Module (Implemented)

- **Dataset**: `ml/yield_forecasting/data/raw/crop_production.csv` ($242,361$ cleaned historical district-level records; $84,183$ benchmark records across 10 major crops)
- **Target**: `Yield = Production / Area` (Tonnes / Hectare)
- **Features**: `State_Name`, `District_Name`, `Crop`, `Season`, `Area`, `Crop_Year` (**Zero Leakage: `Production` strictly excluded from inputs**)
- **Architecture**: Deep Neural Network Regressor (`Input(662)` $\rightarrow$ `Dense(128)` $\rightarrow$ `Dense(64)` $\rightarrow$ `Dense(32)` $\rightarrow$ `Dense(1)`)
- **Performance**:
  - Test MAE: **1.697 Tonnes / Hectare**
  - Test RMSE: **5.478 Tonnes / Hectare**
  - Test $R^2$: **0.9165**
  - Test MedAE: **0.537 Tonnes / Hectare**
- **Inference Module**: `ml/yield_forecasting/model/predict.py`
- **Documentation**:
  - [Model Card](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/YIELD_FORECASTING_MODEL.md)
  - [Experiment Log](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/YIELD_FORECASTING_EXPERIMENTS.md)
