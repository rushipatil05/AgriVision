# Crop Market Price Forecasting Dataset

## 1. Overview
- **Dataset Name**: AGMARKNET Agricultural Commodity Market Prices Dataset
- **Domain**: Agricultural Commodity Economics & Time-Series Forecasting
- **Source**: AGMARKNET (Agricultural Marketing Information Network), Directorate of Marketing & Inspection (DMI), Ministry of Agriculture and Farmers Welfare, Govt of India (curated via AgriPrice Intelligence)
- **Download Location**: `https://raw.githubusercontent.com/Neti-Geethika/AgriPrice-Intelligence/main/data/raw/maharashtra_nashik_all.csv`
- **Date Acquired**: 2026-08-26
- **License**: Government Open Data / Public Research

## 2. Dataset Schema
- **Total Records**: 20,500 historical market arrival observations
- **Columns**:
  1. `Arrival_Date` (String / Date): Date of transaction/market arrival (DD/MM/YYYY)
  2. `State` (String): Indian State (e.g., Maharashtra)
  3. `District` (String): District name (e.g., Nashik)
  4. `Market` (String): APMC wholesale mandi / market name (e.g., Lasalgaon, Pimpalgaon, Yeola, Kalvan, Malegaon)
  5. `Commodity` (String): Agricultural commodity (e.g., Onion, Tomato, Mataki, Gram, Bajra, Wheat, Maize)
  6. `Commodity_Code` (Integer): Official government commodity identifier
  7. `Variety` (String): Commodity variety/subtype (e.g., Red, Local, Hybrid, Pol)
  8. `Grade` (String): Quality grade categorization (e.g., FAQ, Small, Medium, Large)
  9. `Min_Price` (Float/Integer): Minimum wholesale price (₹ per Quintal)
  10. `Max_Price` (Float/Integer): Maximum wholesale price (₹ per Quintal)
  11. `Modal_Price` (Float/Integer): Most frequent / modal wholesale trading price (₹ per Quintal) - Primary Forecasting Target

## 3. Directory Layout
- `raw/agmarknet_commodity_prices.csv`: Immutable original raw market price records.
- `processed/`: Chronologically sorted, filtered, windowed time-series data.

## 4. Known Characteristics & Limitations
- Market closed dates (Sundays, national holidays, strikes) introduce natural non-consecutive date gaps in raw transaction streams.
- Preprocessing standardizes chronological sorting and forward-filling/interpolation for daily sequence windows without shuffling.
- Extreme seasonality and price spikes (e.g., onion supply shocks during monsoon or unseasonal rains) exist in the data.
