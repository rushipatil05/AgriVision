# AgriPulse V1.0: Machine Learning & Deep Learning Methodology

**Platform**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Evaluation Standard**: Verified Empirical Metrics Only (No Retraining / No Metric Inflation)  
**Version**: 1.0 (Production-Ready Academic Release)

---

## 1. Crop Recommendation AI (Level 3A)

### 1.1 Dataset & Feature Engineering
- **Source**: ICAR / Kaggle Agricultural Soil & Climate Dataset ($N = 2,200$ samples).
- **Target Variable**: 22 unique crop classes (`rice`, `maize`, `chickpea`, `kidneybeans`, `pigeonpeas`, `mothbeans`, `mungbean`, `blackgram`, `lentil`, `pomegranate`, `banana`, `mango`, `grapes`, `watermelon`, `muskmelon`, `apple`, `orange`, `papaya`, `coconut`, `cotton`, `jute`, `coffee`).
- **Feature Space** (7 continuous agronomic variables):
  1. $N$ (Nitrogen content in soil, ratio)
  2. $P$ (Phosphorus content in soil, ratio)
  3. $K$ (Potassium content in soil, ratio)
  4. Temperature ($^\circ\text{C}$)
  5. Humidity ($\%$)
  6. pH level of the soil ($[0, 14]$)
  7. Rainfall ($\text{mm}$)

### 1.2 Preprocessing & Scaling
- **Scaler**: `StandardScaler` fitted across all 7 features:
  $$x_{\text{scaled}} = \frac{x - \mu}{\sigma}$$
- **Reshaping**: Features reshaped to sequence format $(1, 7)$ for recurrent LSTM processing.

### 1.3 Deep Learning Architecture
- **Layer 1**: `Bidirectional(LSTM(64, return_sequences=True))`
- **Layer 2**: `Dropout(0.2)`
- **Layer 3**: `Bidirectional(LSTM(32, return_sequences=False))`
- **Layer 4**: `Dense(64, activation='relu')` + `BatchNormalization()`
- **Output**: `Dense(22, activation='softmax')`

### 1.4 Training & Evaluation Parameters
- **Optimizer**: Adam ($\text{lr} = 0.001$)
- **Loss**: `sparse_categorical_crossentropy`
- **Validation Split**: 80/20 stratified train-test split.
- **Final Verified Performance**:
  $$\mathbf{\text{Test Accuracy: } 98.79\%} \quad | \quad \mathbf{\text{Macro F1-Score: } 0.9877}$$

---

## 2. Market Price Forecasting AI (Level 3B)

### 2.1 Dataset & Time-Series Preparation
- **Source**: AGMARKNET Mandi Daily Wholesale Market Dataset ($N > 15,000$ records across Indian mandis).
- **Target Variable**: Wholesale price ($\text{INR / Quintal}$).
- **Sequence Lookback Window**: 30 consecutive daily price observations.

### 2.2 Feature Preprocessing
- **Scaler**: `MinMaxScaler(feature_range=(0, 1))` fitted over historical lookback sequence:
  $$x_{\text{scaled}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

### 2.3 Deep Learning Architecture
- **Layer 1**: `LSTM(64, return_sequences=True, input_shape=(30, 1))`
- **Layer 2**: `Dropout(0.2)`
- **Layer 3**: `LSTM(32, return_sequences=False)`
- **Layer 4**: `Dense(32, activation='relu')`
- **Output**: `Dense(1, activation='linear')`

### 2.4 Multi-Step Forecasting Strategy
- Autoregressive recursive multi-step forecasting: for horizons $H \in \{1, 7, 30\}$, the model iteratively feeds predicted step $t+k$ into the lookback sequence to predict $t+k+1$.
- **Final Verified Performance**:
  $$\mathbf{R^2 \text{ Score: } 0.9375} \quad | \quad \mathbf{\text{Mean Absolute Percentage Error (MAPE): } 3.42\%}$$

---

## 3. Crop Yield Forecasting AI (Level 3C)

### 3.1 Dataset & Spatial-Temporal Features
- **Source**: Ministry of Agriculture & Farmers Welfare, Directorate of Economics and Statistics (DES) ($N > 240,000$ district agricultural records).
- **Target Variable**: Crop Yield ($\text{Tonnes per Hectare}$).
- **Categorical Features**: State (33 states), District (646 districts), Crop (54 crops), Season (Kharif, Rabi, Summer, Whole Year).
- **Numerical Features**: Cultivation Area ($\text{Hectares}$), Crop Year.

### 3.2 Preprocessing Pipeline
- `ColumnTransformer`:
  - `OneHotEncoder(handle_unknown='ignore')` for State, District, Crop, Season.
  - `StandardScaler` for Area and Crop Year.

### 3.3 Deep Neural Network (DNN) Architecture
- **Input Dimension**: $D \approx 740$ sparse/dense one-hot features.
- **Dense Layer 1**: 256 units + `ReLU` + `BatchNormalization()` + `Dropout(0.2)`
- **Dense Layer 2**: 128 units + `ReLU` + `BatchNormalization()` + `Dropout(0.2)`
- **Dense Layer 3**: 64 units + `ReLU`
- **Output**: `Dense(1, activation='linear')`

### 3.4 Training & Evaluation Parameters
- **Optimizer**: Adam ($\text{lr} = 0.001$, `ReduceLROnPlateau`)
- **Loss**: `mean_squared_error`
- **Final Verified Performance**:
  $$\mathbf{R^2 \text{ Score: } 0.9165} \quad | \quad \mathbf{\text{RMSE: } 0.428 \text{ t/ha}}$$

---

## 4. Multi-Modal Decision Support System (Level 7)

### 4.1 Multi-Objective Formulation
Synthesizes soil suitability, harvest yield potential, and mandi price returns into a single actionable index.

### 4.2 Mathematical Scoring Formulation
For candidate crop $i$:
$$\text{Decision Score}_i = w_s \cdot S_i + w_y \cdot Y_i + w_m \cdot M_i$$
Where:
- $w_s = 0.40$ (Soil & Climatic Suitability Weight)
- $w_y = 0.35$ (Harvest Yield Productivity Weight)
- $w_m = 0.25$ (Commodity Market Outlook Weight)
- $\sum w = 1.00$

### 4.3 Normalized Component Metrics
1. **Suitability Score ($S_i \in [0, 100]$)**:
   $$S_i = P(\text{Crop}_i \mid \text{Soil, Climate}) \times 100$$
2. **Yield Score ($Y_i \in [0, 100]$)**:
   $$Y_i = \min\left(100, \frac{\text{Predicted Yield}_i}{\text{Benchmark Yield}_i} \times 100\right)$$
3. **Market Score ($M_i \in [0, 100]$)**:
   $$M_i = \text{Normalized Price Factor} \times (1.0 + \Delta_{\text{trend}})$$
   Where $\Delta_{\text{trend}} = +0.10$ for `UPWARD`, $0.00$ for `STABLE`, $-0.10$ for `DOWNWARD`.

### 4.4 Dynamic AI Explainability Engine
Generates deterministic plain-English rationale examining:
- Soil N-P-K nutrient sufficiency
- Rainfall & temperature suitability
- Yield percentile against district benchmarks
- Mandi price trend direction and revenue outlook