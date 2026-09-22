# AgriPulse: Precision Agriculture Platform Using Deep Learning

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular](https://img.shields.io/badge/Angular-18+-DD0031.svg?logo=angular&logoColor=white)](https://angular.dev)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-FF6F00.svg?logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Pytest](https://img.shields.io/badge/Pytest-86%2F86%20Passed-green.svg)](https://pytest.org)
[![Angular Tests](https://img.shields.io/badge/Angular%20Tests-34%2F34%20Passed-green.svg)](https://angular.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg?logo=githubactions&logoColor=white)](https://github.com)

**AgriPulse** is an enterprise-grade precision agriculture intelligence platform that synthesizes deep learning, time-series forecasting, and multi-criteria decision optimization into actionable agronomic guidance. The platform unifies **Crop Recommendation (LSTM)**, **Market Price Trajectories (Time-Series LSTM)**, and **Harvest Yield Forecasting (Deep Neural Network)** into a composite **Decision Support System (DSS)** supported by full **MLOps Telemetry, Data Drift Monitoring, and Model Registry Governance**.

---

## 🌟 Machine Learning Architecture & Verified Metrics

| Subsystem | Architecture | Input Modalities | Verified Performance Metric |
| :--- | :--- | :--- | :--- |
| **Level 3A: Crop Recommendation** | Bidirectional LSTM + Softmax | Soil Nutrients ($N, P, K$), pH, Temperature, Humidity, Rainfall | **98.79% Test Accuracy** across 22 crop classes |
| **Level 3B: Price Forecasting** | Multi-Step Recursive LSTM | 30-Day Mandi Historical Modal Prices, Commodity, Market Location | **$R^2 = 0.9375$** across 1, 7, 30-day forecast horizons |
| **Level 3C: Yield Forecasting** | Deep Neural Network Regressor | State (33), District (646), Crop, Season, Acreage, Year | **$R^2 = 0.9165$** ($t/\text{ha}$ productivity) |
| **Level 7: Decision Support Engine** | Multi-Criteria Weighted Synthesis | Integrated 13 Soil, Regional & Mandi Price Inputs | **Composite Decision Score (0–100) + AI Rationale** |

$$\text{Composite Decision Score} = 0.40 \times \text{Suitability Score} + 0.35 \times \text{Yield Score} + 0.25 \times \text{Market Score}$$

---

## 🏗️ System Architecture & Technology Stack

```
Angular 18+ SPA (Signals, Chart.js, Dark Theme)
       │ (REST JSON with Bearer JWT)
FastAPI Backend (Async ASGI + Telemetry Middleware)
       │
       ├── Preloaded Neural Inference Engines (Crop LSTM, Price LSTM, Yield DNN, DSS)
       ├── Authentication & Tenant Isolation (Bcrypt 12 Rounds + HS256 JWT)
       ├── PostgreSQL 15 Database (Users, PredictionHistory, Audit Trail)
       └── MLOps & Telemetry Hub (Thread-Safe Metrics, Z-Shift Data Drift, Registry)
```

- **Frontend**: Angular 18+, TypeScript, Angular Signals, RxJS, Chart.js, HTML5/CSS3.
- **Backend**: FastAPI, Python 3.10+, Uvicorn, Pydantic v2, SQLAlchemy 2.0, Passlib.
- **Machine Learning**: TensorFlow 2.15+, Keras, Scikit-Learn, NumPy, Pandas.
- **Database**: PostgreSQL 15 / SQLite (in-memory test isolation).
- **MLOps & DevOps**: Docker, Docker Compose, Nginx, GitHub Actions CI/CD.

---

## 📱 Screens & Core Capabilities

1. **AI Decision Support (`/decision-support`)**: 13-parameter interactive agronomic form with 5 regional presets, Rank #1 recommendation hero card, multi-bar criteria comparison chart, alternative crops ranking table, and dynamic explainability rationale.
2. **Crop Recommendation (`/crop-recommendation`)**: Soil nutrient sliders, climate inputs, top-5 probability rankings, and radar soil composition profile.
3. **Market Price Forecasting (`/price-forecast`)**: Multi-horizon commodity price projections (1, 7, 30 days) with interactive historical vs forecasted trajectory graphs.
4. **Crop Yield Forecasting (`/yield-forecast`)**: Cascading state-to-district selector covering 33 states and 646 districts with density and total production estimates.
5. **System Monitoring & MLOps (`/monitoring`)**: 5-tab observability dashboard with live pulse indicators, model registry catalog, API latency telemetry breakdown, statistical feature drift monitor, and prediction output distribution stats.
6. **Prediction History (`/history`)**: User-isolated chronological audit trail with pagination, type filtering, detailed JSON inspection, and deletion modals.
7. **User Authentication (`/login`, `/register`, `/profile`)**: Bcrypt password hashing, JWT session lifecycle, and responsive profile management.

---

## ⚡ Quickstart & Development Instructions

### Prerequisites
- Python 3.10+ & `pip`
- Node.js 20+ & `npm`
- PostgreSQL 15+ (or automated SQLite in test mode)
- Docker & Docker Compose (Optional for containerized run)

### Method 1: Local Development Launch
```powershell
# 1. Setup Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Setup Frontend (in a separate terminal)
cd frontend
npm install
npm start
```
- **Web UI**: `http://localhost:4200`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

### Method 2: Docker Container Launch
```bash
# Build and run all services in detached mode
docker-compose -f docker/docker-compose.yml up -d --build
```

---

## 🧪 Comprehensive Testing & Verification

Execute all verification test suites across the repository:

```powershell
# Backend Pytest Suite (86 tests)
cd backend
pytest tests/ -v

# Frontend Unit Tests (34 tests across 12 suites)
cd frontend
npm test -- --watch=false

# Production AOT Build Verification
npm run build

# End-to-End System Harness
python scripts/verify_system.py

# Latency & Throughput Benchmark Suite
python scripts/benchmark_latency.py
```

---

## 📁 Project Structure

```
D:\FINAL FINAL YEAR PROJECT
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── config/           # Database, settings & security config
│   │   ├── models/           # SQLAlchemy entity models (User, PredictionHistory)
│   │   ├── routes/           # REST API endpoints (Auth, Crop, Price, Yield, DSS, Monitoring)
│   │   ├── schemas/          # Pydantic v2 validation schemas
│   │   ├── services/         # ML services, telemetry collectors, drift engines
│   │   └── main.py           # Application entrypoint & lifespan handler
│   ├── tests/                # 86 automated Pytest test cases
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Angular 18+ SPA Application
│   ├── src/app/
│   │   ├── core/             # Services, models, guards, interceptors
│   │   ├── features/         # Standalone feature components (Auth, Dashboard, ML, Monitoring)
│   │   ├── layout/           # Navbar, sidebar, footer components
│   │   └── shared/           # Reusable UI components (charts, spinners, empty states)
│   └── package.json          # Node dependencies & test scripts
├── saved_models/             # Pretrained neural weights (LSTM, DNN, Scalers, Encoders)
├── docker/                   # Dockerfiles & docker-compose.yml
├── .github/workflows/        # CI/CD pipeline (ci.yml)
├── docs/                     # Full technical documentation suite
└── scripts/                  # Automated verification & benchmark scripts
```

---

## ⚠️ Academic Release Notice & Scope

- **Academic Classification**: AgriPulse V1.0 is an academic precision agriculture platform designed for decision support and predictive analytics.
- **Data Reliance**: Forecasts depend on statistical correlations from historical ICAR, AGMARKNET, and DES datasets. Unforeseen climate events or sudden policy shifts should be verified with local agricultural extension services.