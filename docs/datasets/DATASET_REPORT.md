# AgriPulse: Comprehensive Dataset Report

**Project**: AgriPulse — Precision Agriculture Using Deep Learning  
**Milestone**: LEVEL 2 — Dataset Acquisition, Validation & Preprocessing  
**Status**: Completed & Verified  

---

## Executive Summary

To support the three software-only AI modules in AgriPulse, three distinct real-world agricultural datasets were acquired, rigorously validated, and preprocessed:

1. **Crop Recommendation Dataset**: Agronomic soil nutrient ($N, P, K$, pH) and climatic ($T, H, R$) multiclass dataset.
2. **Crop Price Forecasting Dataset**: Official Agmarknet historical daily wholesale market prices spanning multiple commodities and APMC mandis.
3. **Crop Yield Forecasting Dataset**: Directorate of Economics and Statistics (DES) historical district-level agricultural production and acreage dataset covering 33 Indian states from 1997 to 2015.

---

## 1. Crop Recommendation Dataset (Dataset A)

### 1.1 Metadata & Provenance
- **Dataset Name**: Crop Recommendation Dataset
- **Source**: Open Agricultural Repository / Harvestify Agronomy Benchmark
- **Primary Purpose**: Multi-class crop classification and top-5 ranking based on real soil nutrient and meteorological parameters.
- **Acquisition URL**: `https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv`
- **License**: Public Educational & Research Use

### 1.2 Quantitative Profile & Statistics
- **Total Records**: $2,200$ samples
- **Total Columns**: $8$ ($7$ numerical inputs, $1$ categorical target)
- **Missing Values**: $0$ missing cells across all columns ($0.0\%$)
- **Duplicate Rows**: $0$ duplicate records
- **Target Classes**: $22$ distinct crop classes, perfectly balanced with $100$ samples per class:
  - *Cereals & Pulses*: `rice`, `maize`, `chickpea`, `kidneybeans`, `pigeonpeas`, `mothbeans`, `mungbean`, `blackgram`, `lentil`
  - *Fruits*: `banana`, `mango`, `grapes`, `watermelon`, `muskmelon`, `apple`, `orange`, `papaya`, `pomegranate`, `coconut`
  - *Cash Crops*: `cotton`, `jute`, `coffee`

### 1.3 Feature Specifications & Empirical Distribution

| Feature | Description | Unit | Min | Mean | Median | Max | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `N` | Soil Nitrogen Ratio | kg/ha | 0.00 | 50.55 | 37.00 | 140.00 | 36.92 |
| `P` | Soil Phosphorus Ratio | kg/ha | 5.00 | 53.36 | 51.00 | 145.00 | 32.99 |
| `K` | Soil Potassium Ratio | kg/ha | 5.00 | 48.15 | 32.00 | 205.00 | 50.65 |
| `temperature` | Environmental Temp | °C | 8.83 | 25.62 | 25.60 | 43.68 | 5.06 |
| `humidity` | Relative Humidity | % | 14.26 | 71.48 | 80.47 | 99.98 | 22.26 |
| `ph` | Soil Acidity/Alkalinity | pH scale | 3.50 | 6.47 | 6.43 | 9.94 | 0.77 |
| `rainfall` | Total Precipitation | mm | 20.21 | 103.46 | 94.87 | 298.56 | 54.96 |

### 1.4 Preprocessing Strategy
- **Stratified Partitioning**: 70% Train ($1,540$ samples), 15% Validation ($330$ samples), 15% Test ($330$ samples).
- **Target Encoding**: `LabelEncoder` transforming 22 string labels into indices $[0, 21]$.
- **Leakage-Free Feature Scaling**: `StandardScaler` fitted **strictly on the training partition ($X_{\text{train}}$)** and subsequently applied to transform $X_{\text{val}}$ and $X_{\text{test}}$.
- **Output Artifact**: `ml/crop_recommendation/data/processed/crop_recommendation_processed.csv`.

---

## 2. Crop Market Price Forecasting Dataset (Dataset B)

### 2.1 Metadata & Provenance
- **Dataset Name**: AGMARKNET Commodity Wholesale Market Price Dataset
- **Source**: Directorate of Marketing & Inspection (DMI), Ministry of Agriculture and Farmers Welfare, Govt of India (curated via AgriPrice Intelligence)
- **Primary Purpose**: Sequential multi-step time-series forecasting of agricultural commodity spot prices and trend direction classification.
- **Acquisition URL**: `https://raw.githubusercontent.com/Neti-Geethika/AgriPrice-Intelligence/main/data/raw/maharashtra_nashik_all.csv`
- **License**: Government Open Data (OGD India)

### 2.2 Quantitative Profile & Statistics
- **Total Records**: $20,500$ market transaction records
- **Total Columns**: $11$ features
- **Missing Values**: $0$ missing entries
- **Duplicate Records**: $0$ duplicate records
- **Date Range**: `2004-01-01` to `2022-12-31` (Spanning $6,939$ chronological days / 18 years)
- **Commodity Scope**: $78$ distinct commodities (including Onion, Tomato, Wheat, Maize, Bajra, Gram, Mataki, Green Peas)
- **Mandi (Market) Scope**: $22$ APMC wholesale markets (including Lasalgaon, Pimpalgaon, Malegaon, Nandgaon, Sinner, Devala, Kalvan, Yeola)

### 2.3 Price Metrics & Invariant Checks

| Price Metric | Description | Min (₹/Qtl) | Mean (₹/Qtl) | Median (₹/Qtl) | Max (₹/Qtl) | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Min_Price` | Minimum Wholesale Price | 1.00 | 1,534.16 | 1,200.00 | 20,000.00 | 1,461.91 |
| `Max_Price` | Maximum Wholesale Price | 2.00 | 2,534.46 | 1,825.00 | 36,488.00 | 2,286.11 |
| `Modal_Price` | Modal (Most Frequent) Price | 2.00 | 2,136.42 | 1,600.00 | 25,000.00 | 1,850.88 |

- **Economic Invariant Checks**: Zero negative prices, zero $\text{Min\_Price} > \text{Max\_Price}$ violations, zero unparseable dates.

### 2.4 Preprocessing & Time-Series Sequence Strategy
- **Date Parsing & Chronological Ordering**: Datetime parsing and strict chronological sort by `date`.
- **Continuous Daily Resampling**: Resampling to daily frequency (`D`) with forward/backward fill for non-trading holidays/Sundays.
- **Sliding Window Generation**: Lookback sequence window of $T = 30$ days to predict $T+1$ modal price.
- **Chronological Split (Zero Random Shuffling)**:
  - *Training Set*: First 70% of chronological timeline ($4,581$ sequence windows)
  - *Validation Set*: Next 15% ($982$ sequence windows)
  - *Test Set*: Final 15% ($982$ sequence windows)
- **Scaler Isolation**: `MinMaxScaler(0, 1)` fitted **strictly on the training partition** of the series.
- **Output Artifact**: `ml/price_forecasting/data/processed/price_forecasting_processed.csv`.

---

## 3. Crop Yield Forecasting Dataset (Dataset C)

### 3.1 Metadata & Provenance
- **Dataset Name**: India District-Wise Crop Production Statistics
- **Source**: Directorate of Economics and Statistics (DES), Ministry of Agriculture and Farmers Welfare, Govt of India
- **Primary Purpose**: Macro-level crop yield regression ($\text{Tonnes/Hectare}$) and production forecasting.
- **Acquisition URL**: `https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India-using-ML/main/crop_production.csv`
- **License**: Open Government Data (OGD India)

### 3.2 Quantitative Profile & Statistics
- **Total Raw Records**: $246,091$ district-season observations
- **Total Columns**: $7$ columns (`State_Name`, `District_Name`, `Crop_Year`, `Season`, `Crop`, `Area`, `Production`)
- **Missing Values**: $3,730$ entries ($1.52\%$) in `Production` column.
- **Duplicate Records**: $0$ full-row duplicates.
- **Temporal Horizon**: $1997$ to $2015$ ($19$ continuous agricultural crop years)
- **Geographic Coverage**: $33$ Indian States & Union Territories across $646$ administrative districts.
- **Crop Variety**: $124$ distinct agricultural crops across 6 seasons (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`).

### 3.3 Yield Formulation & Empirical Distributions

$$\text{Yield} = \frac{\text{Production (Tonnes)}}{\text{Area (Hectares)}} \quad (\text{Tonnes/Hectare})$$

| Variable | Filtered Count | Min | Mean | Median | Max | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Area` (ha) | 242,361 | 0.10 | 12,167.41 | 603.00 | 8,580,100.00 | 50,857.44 |
| `Production` (Tonnes) | 242,361 | 0.00 | 582,503.44 | 729.00 | 1,250,800,000.00 | 17,065,813.17 |
| `Yield` (Tonnes/ha) | 242,361 | 0.00 | 41.65 | 1.00 | 88,000.00 | 817.57 |

### 3.4 Preprocessing & Temporal Partitioning Strategy
- **Quality Cleaning**: Filtered records where $\text{Area} > 0$ and $\text{Production}$ is non-null ($242,361$ high-integrity records retained).
- **Temporal Split (Zero Shuffling)**:
  - *Train Partition*: $\text{Crop\_Year} \le 2011$ ($71,262$ benchmark crop records)
  - *Validation Partition*: $2012 \le \text{Crop\_Year} \le 2013$ ($9,003$ benchmark crop records)
  - *Test Partition*: $\text{Crop\_Year} \ge 2014$ ($3,971$ benchmark crop records)
- **Feature Scaling**: `StandardScaler` fitted **only on the training partition**.
- **Output Artifact**: `ml/yield_forecasting/data/processed/yield_forecasting_processed.csv`.

---

## 4. Generated Exploratory Data Analysis (EDA) Visualizations

All generated visualizations are stored under `ml/*/results/eda/`:

1. **Crop Recommendation**:
   - `ml/crop_recommendation/results/eda/crop_class_distribution.png`: Class balance verification across all 22 crops.
   - `ml/crop_recommendation/results/eda/feature_distributions.png`: KDE and histograms for $N, P, K$, Temp, Humidity, pH, Rainfall.
   - `ml/crop_recommendation/results/eda/correlation_matrix.png`: Heatmap showing correlation between soil nutrients and rainfall.

2. **Price Forecasting**:
   - `ml/price_forecasting/results/eda/price_trends.png`: Multi-year monthly median modal price curves for top commodities.
   - `ml/price_forecasting/results/eda/commodity_distribution.png`: Top 10 traded commodities in Mandi records.
   - `ml/price_forecasting/results/eda/market_distribution.png`: Record distribution across APMC mandis.

3. **Yield Forecasting**:
   - `ml/yield_forecasting/results/eda/yield_trends_over_years.png`: Multi-year median yield trajectories for staple crops.
   - `ml/yield_forecasting/results/eda/crop_distribution.png`: Most frequently cultivated crops across Indian districts.
   - `ml/yield_forecasting/results/eda/state_distribution.png`: State-wise agricultural observation volume.

---

## 5. Compliance & Quality Assurance Checklist

- [x] **Real Data Authenticity**: Zero synthetic or randomized records.
- [x] **No Data Leakage**: Scalers and encoders fitted strictly on training partitions.
- [x] **Chronological Integrity**: Time-series splits maintain exact temporal order with zero shuffling.
- [x] **Portability**: All file references use relative paths resolved through `ml/common/paths.py`.
- [x] **Git Cleanliness**: Large datasets excluded via `.gitignore` with directory structures preserved via `.gitkeep`.
