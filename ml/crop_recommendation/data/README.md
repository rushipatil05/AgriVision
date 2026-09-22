# Crop Recommendation Dataset

## 1. Overview
- **Dataset Name**: Crop Recommendation Dataset
- **Domain**: Precision Agriculture / Soil & Environmental Agronomy
- **Source**: Open Agricultural Benchmark / Harvestify Repository
- **Download Location**: `https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv`
- **Date Acquired**: 2026-08-26
- **License**: Open Access / Public Educational Research

## 2. Dataset Schema
- **Total Records**: 2,200 observations
- **Total Features**: 7 numerical input features + 1 categorical target label
- **Input Features**:
  1. `N` (Integer/Float): Nitrogen level in soil (ratio / kg/ha)
  2. `P` (Integer/Float): Phosphorus level in soil (ratio / kg/ha)
  3. `K` (Integer/Float): Potassium level in soil (ratio / kg/ha)
  4. `temperature` (Float): Environmental temperature in degrees Celsius (°C)
  5. `humidity` (Float): Relative environmental humidity percentage (%)
  6. `ph` (Float): Soil pH value (0.0 to 14.0 scale)
  7. `rainfall` (Float): Precipitation/rainfall level in millimeters (mm)
- **Target Feature**:
  - `label` (String): Crop name classification (22 classes, 100 observations per class: rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee).

## 3. Directory Layout
- `raw/crop_recommendation.csv`: Immutable original raw dataset.
- `processed/`: Validated, encoded, and preprocessed datasets for model consumption.

## 4. Known Characteristics & Limitations
- Perfectly balanced multiclass dataset with 100 samples per crop class.
- Zero missing values in the raw dataset.
- Soil and weather values reflect optimal/cultivation conditions; extreme drought or soil degradation scenarios require out-of-distribution handling.
