# AgriPulse Frontend UI Application

Interactive web application for **AgriPulse: Precision Agriculture Platform Using Deep Learning**. Built with **Angular 18+**, **Standalone Components**, **Chart.js**, and styled with modern responsive design.

---

## Features
- **Dashboard**: System health status, live model metrics, recent prediction audit activity, and prediction distribution doughnut chart.
- **Crop Recommendation**: 7-parameter environmental input form with quick presets (Rice, Maize, Cotton, Coffee, Apple), top-1 hero recommendation banner, top-5 ranked probability bar chart, and normalized soil radar chart.
- **Price Forecasting**: Multi-step recursive LSTM lookback form, realistic sequence generator, 1/7/14/30-day forecast selector, and historical vs. forecast multi-line trajectory chart.
- **Yield Forecasting**: Geographic (State & District), crop, season, and acreage inputs with DNN harvest productivity gauges and quintal production converters.
- **Prediction History**: Audited prediction logs with subsystem filtering (All, Crop, Price, Yield), pagination controls, full input/output JSON payload inspector modal, and single-click record deletion.
- **Authentication & Security**: Complete JWT login and registration with validation, auto Bearer header injection via HttpInterceptor, and route guards.

---

## Build & Test Commands

```bash
# Install dependencies
npm install --legacy-peer-deps

# Start development server (http://localhost:4200)
npm start

# Run unit tests
npm test

# Build production distribution
npm run build
```
