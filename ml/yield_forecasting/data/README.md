# Crop Yield & Production Forecasting Dataset

## 1. Overview
- **Dataset Name**: India Crop Production & Agricultural Statistics Dataset
- **Domain**: Macro Agronomy & Regional Crop Yield Forecasting
- **Source**: Directorate of Economics and Statistics (DES), Department of Agriculture & Cooperation, Ministry of Agriculture and Farmers Welfare, Government of India
- **Download Location**: `https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India-using-ML/main/crop_production.csv`
- **Date Acquired**: 2026-08-26
- **License**: Open Government Data (OGD) India / Public Educational Benchmark

## 2. Dataset Schema
- **Total Records**: 246,091 regional crop production records across India (1997–2015)
- **Columns**:
  1. `State_Name` (String): Indian State / Union Territory (33 states/UTs covered)
  2. `District_Name` (String): Administrative district (646 districts)
  3. `Crop_Year` (Integer): Agricultural crop calendar year (1997 to 2015)
  4. `Season` (String): Cultivation season (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`)
  5. `Crop` (String): Name of the crop (124 distinct crop varieties)
  6. `Area` (Float): Cultivated surface area measured in Hectares (ha)
  7. `Production` (Float): Total agricultural production volume (measured in Metric Tonnes)

## 3. Yield Metric Formulation
- **Yield Calculation**:
  $$\text{Yield} = \frac{\text{Production (Tonnes)}}{\text{Area (Hectares)}} \quad (\text{Tonnes/Hectare})$$

## 4. Directory Layout
- `raw/crop_production.csv`: Immutable original raw district-wise crop statistics.
- `processed/`: Cleaned, validated, yield-computed dataset with temporal train/validation splits.

## 5. Known Characteristics & Limitations
- Approximately 3,738 records (1.5%) have missing `Production` entries in the raw dataset.
- Coconut production is historically recorded in nuts rather than metric tonnes in certain states; preprocessing accounts for crop-specific yield scaling.
- Missing values in `Production` must be explicitly addressed during data validation and cleaning without corrupting historical integrity.
