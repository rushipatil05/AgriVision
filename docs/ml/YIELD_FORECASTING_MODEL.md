# AgriPulse Model Card: Crop Yield Forecasting (Deep Neural Network & Baselines)

## 1. Problem Definition
The **Crop Yield Forecasting Subsystem** provides predictive agricultural estimation of crop output per unit area (productivity) given historical regional, geographic, seasonal, and acreage attributes.

- **Task**: Tabular Regression for Crop Yield Estimation
- **Target Variable**: `Yield = Production / Area` (measured in **Tonnes per Hectare: Tonnes/ha**)
- **Target Leakage Prevention**: `Production` is **strictly excluded** from input features.
- **Primary Model Architecture**: Deep Neural Network (DNN) Regressor
- **Baseline Comparative Models**: Global Median Baseline, Ridge Linear Regression, Histogram Gradient Boosting Regressor, Random Forest Regressor

---

## 2. Dataset & Features
- **Source**: Directorate of Economics & Statistics (DES), Ministry of Agriculture and Farmers Welfare, Government of India (Crop Production in India, 1997–2015).
- **Total Raw Records**: $246,091$ agricultural district records across 33 Indian States/UTs and 646 districts.
- **Cleaned Benchmark Records**: $84,183$ records across the 10 major national benchmark crops: `Rice`, `Wheat`, `Maize`, `Sugarcane`, `Cotton(lint)`, `Bajra`, `Jowar`, `Gram`, `Groundnut`, `Potato`.
- **Target Outlier Rule**: Filtered unit recording anomalies ($\text{Yield} \le 250\text{ Tonnes/ha}$, removing 53 severe unit-recording errors such as kilograms entered instead of tonnes).
- **Features Used**:
  - Categorical: `State_Name` (33 categories), `District_Name` (646 categories), `Crop` (10 benchmark classes), `Season` (6 classes)
  - Numerical: `Area` (cultivated hectares), `Crop_Year` (chronological year)
- **Encoded Feature Dimensions**: $662$ columns via `ColumnTransformer` (StandardScaler + OneHotEncoder with `handle_unknown='ignore'`).

---

## 3. Chronological Splits & Leakage Prevention
- **Temporal Split (Zero Random Shuffling)**:
  - **Training Partition ($\le 2011$)**: $71,209$ records (1997–2011)
  - **Validation Partition ($2012\text{--}2013$)**: $9,003$ records (2012–2013)
  - **Untouched Test Partition ($\ge 2014$)**: $3,971$ records (2014–2015)
- **Temporal Rule**: $\max(\text{train\_year}) \le 2011 < \min(\text{val\_year}) = 2012 \le \max(\text{val\_year}) = 2013 < \min(\text{test\_year}) = 2014$.
- **Leakage Prevention**: Preprocessor fitted **strictly on training partition ($X_{\text{train}}$)**; validation and test sets transformed without refitting.

---

## 4. Deep Neural Network Architecture

```
Input Layer: Shape (662 features)
  │
  ▼
Dense Layer (128 units, ReLU activation, L2 kernel regularization=1e-4)
  │
  ▼
Dropout (rate=0.20)
  │
  ▼
Dense Layer (64 units, ReLU activation, L2 kernel regularization=1e-4)
  │
  ▼
Dropout (rate=0.20)
  │
  ▼
Dense Layer (32 units, ReLU activation, L2 kernel regularization=1e-4)
  │
  ▼
Dense Output Layer (1 unit, Linear activation -> Predicted Yield in Tonnes/ha)
```

- **Loss Function**: Mean Squared Error (MSE)
- **Optimizer**: Adam ($\text{learning\_rate} = 0.001$)
- **Callbacks**: `EarlyStopping(patience=15, restore_best_weights=True)`, `ReduceLROnPlateau(patience=5, factor=0.5)`
- **Epochs**: 100 (Early stopping triggered at epoch 19, best weights restored from epoch 4)
- **Batch Size**: 64
- **Training Duration**: 64.88 seconds (CPU)

---

## 5. Measured Experimental Results (On Untouched Test Set: $N=3,971$ records)

All metrics are evaluated in true agricultural units (**Tonnes / Hectare**):

| Model | Val MAE (t/ha) | Val RMSE (t/ha) | Val $R^2$ | Test MAE (t/ha) | Test RMSE (t/ha) | Test $R^2$ | Test MedAE (t/ha) | Test MAPE (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Median Yield Baseline** | 7.108 | 20.046 | -0.1256 | 7.130 | 20.099 | -0.1247 | 0.827 | 70.16% |
| **Ridge Linear Regression** | 3.896 | 8.889 | 0.7786 | 3.605 | 8.706 | 0.7890 | 1.522 | 122.33% |
| **Histogram Gradient Boosting** | 2.042 | 6.635 | 0.8767 | 1.884 | 6.208 | 0.8927 | 0.567 | 53.92% |
| **Random Forest Regressor** | 1.857 | 6.163 | 0.8936 | 1.783 | 5.901 | 0.9031 | **0.467** | **44.45%** |
| **Deep Neural Network (Primary)**| **1.781** | **5.866** | **0.9036** | **1.697** | **5.478** | **0.9165** | 0.537 | 49.78% |

### Key Findings:
1. **DNN Superiority**: The Deep Neural Network achieved the best generalization on the untouched test partition with **MAE = 1.697 Tonnes/ha**, **RMSE = 5.478 Tonnes/ha**, and **$R^2 = 0.9165$**.
2. **Robust Error Metric**: Median Absolute Error (MedAE) is **~0.537 Tonnes/ha**, demonstrating that typical estimation error for staple grains (Rice, Wheat, Maize) is around half a tonne per hectare. Higher RMSE values are driven by high-yield crops like Sugarcane (70–85 t/ha) and Potato (20–25 t/ha).

---

## 6. Generated Visualizations
Saved under `ml/yield_forecasting/results/plots/`:
- `actual_vs_predicted.png`: Scatter comparison against ideal $y = x$ fit line.
- `residual_diagnostics.png`: Residual error distribution histogram & residual vs predicted scatter.
- `deep_training_curves.png`: Training vs validation loss over epochs.
- `yield_distribution.png`: Empirical distribution of agricultural crop yields.
- `crop_level_performance.png`: MAE broken down by individual agricultural crops.
- `state_level_performance.png`: MAE broken down across top agricultural states.

---

## 7. Serialized Model Artifacts
Saved in `ml/yield_forecasting/model/`:
- `crop_yield_dnn.keras`: Trained deep neural network model.
- `gradient_boosting_yield.joblib`: Trained ensemble model.
- `preprocessor.joblib`: Pre-fitted ColumnTransformer.
- `metadata.json`: Full training configuration, hyperparameters, and split metrics.

---

## 8. Inference Example
```python
from ml.yield_forecasting.model.predict import predict_crop_yield

result = predict_crop_yield(
    state="Punjab",
    district="Ludhiana",
    crop="Wheat",
    season="Rabi",
    area=50.0,
    crop_year=2024
)
# Output:
# {
#   "state": "Punjab",
#   "district": "Ludhiana",
#   "crop": "Wheat",
#   "season": "Rabi",
#   "area_hectares": 50.0,
#   "crop_year": 2024,
#   "predicted_yield_tonnes_per_hectare": 5.625,
#   "estimated_total_production_tonnes": 281.25,
#   "unit": "Tonnes / Hectare",
#   "model_used": "Deep Neural Network"
# }
```

---

## 9. Limitations & Intended Use
- **Dataset Horizon**: Historical data spans up to 2015. Yield predictions for future seasons serve as baseline agronomic expectations and should be interpreted as historical-trend projections.
- **Exogenous Factors**: Unseasonal micro-climate flash floods or localized pest infestations are not captured in macroscopic annual district acreage records.
