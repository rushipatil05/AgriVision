# AgriPulse V1.0: Complete Project File Structure & Repository Index

**Platform**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Version**: 1.0 (Production-Ready Academic Release)

---

## 1. High-Level Repository Layout

```
D:\FINAL FINAL YEAR PROJECT
├── .github/                  # CI/CD Workflows
│   └── workflows/
│       └── ci.yml            # GitHub Actions Pipeline (Pytest + Vitest + Docker)
├── backend/                  # FastAPI Application & ML Services
│   ├── app/
│   │   ├── config/           # Database engine & settings
│   │   ├── models/           # SQLAlchemy ORM entity models
│   │   ├── routes/           # REST API endpoints
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   ├── services/         # ML services, telemetry collectors, drift engines
│   │   └── main.py           # Application lifespan & entrypoint
│   ├── tests/                # 86 automated Pytest backend unit/integration tests
│   ├── pytest.ini            # Pytest configuration
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Angular 18+ SPA Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/         # Guards, interceptors, models, services
│   │   │   ├── features/     # Feature components (Auth, Dashboard, ML, History, Monitoring)
│   │   │   ├── layout/       # Navbar, sidebar, footer layout components
│   │   │   ├── shared/       # Reusable components (charts, spinners, empty states)
│   │   │   ├── app.config.ts # Angular application config & providers
│   │   │   └── app.routes.ts # App route routing table
│   │   ├── environments/     # Environment configurations (dev, prod)
│   │   ├── index.html        # SPA root HTML
│   │   └── main.ts           # Application bootstrap
│   ├── angular.json          # Angular CLI workspace configuration
│   ├── package.json          # Node dependencies and test scripts
│   └── tsconfig.json         # TypeScript configuration
├── datasets/                 # Agricultural Training & Evaluation Datasets
│   ├── crop_recommendation/  # ICAR soil dataset
│   ├── price_forecasting/    # AGMARKNET mandi historical prices
│   └── yield_forecasting/    # DES district crop yield statistics
├── docker/                   # Containerization & Orchestration
│   ├── backend.Dockerfile    # Python 3.10 production container
│   ├── frontend.Dockerfile   # Multi-stage Angular/Nginx container
│   ├── docker-compose.yml    # Full-stack composition (Postgres + Backend + Frontend)
│   └── nginx.conf            # Nginx reverse proxy configuration
├── docs/                     # Technical & Milestone Documentation
│   ├── final/                # V1.0 Release Audit Documentation Suite
│   ├── level7/               # Level 7 Decision Support Documentation
│   ├── level8/               # Level 8 MLOps & Monitoring Documentation
│   └── PROJECT_STATUS.md     # Milestone tracking ledger
├── ml/                       # Machine Learning Training & Evaluation Scripts
│   ├── crop_recommendation/  # Level 3A LSTM training scripts
│   ├── price_forecasting/    # Level 3B LSTM training scripts
│   └── yield_forecasting/    # Level 3C DNN training scripts
├── saved_models/             # Pretrained Production Neural Weights
│   ├── crop_recommendation/  # LSTM weights & StandardScaler
│   ├── price_forecasting/    # LSTM weights & MinMaxScaler
│   └── yield_forecasting/    # DNN weights & ColumnTransformer
├── scripts/                  # Operational Automation & Verification Scripts
│   ├── benchmark_latency.py  # Latency & throughput benchmark suite
│   ├── verify_system.py      # End-to-end full system sanity harness
│   └── start_system.ps1      # Single-command system launcher
└── README.md                 # Project README and quickstart guide
```

---

## 2. Core Backend Modules Map

| Module Path | Primary Responsibility |
| :--- | :--- |
| `backend/app/main.py` | FastAPI application factory, CORS, telemetry middleware, lifespan model loader |
| `backend/app/config/database.py` | SQLAlchemy database engine, session factory (`get_db`), declarative Base |
| `backend/app/config/settings.py` | Pydantic Settings loading environment variables (`DATABASE_URL`, `SECRET_KEY`) |
| `backend/app/models/user.py` | User entity schema with Bcrypt password hash and active flag |
| `backend/app/models/prediction_history.py` | Prediction audit history schema storing input/output JSON and latency |
| `backend/app/routes/auth.py` | User registration, login, `/auth/me`, and logout endpoints |
| `backend/app/routes/crop.py` | Level 3A crop recommendation REST endpoint |
| `backend/app/routes/price.py` | Level 3B market price forecasting REST endpoint |
| `backend/app/routes/yield_.py` | Level 3C district yield forecasting REST endpoint |
| `backend/app/routes/decision.py` | Level 7 AI decision support recommendation REST endpoint |
| `backend/app/routes/prediction_history.py`| Paginated prediction history retrieval and deletion REST endpoints |
| `backend/app/routes/monitoring.py` | Level 8 MLOps health, model registry, telemetry, drift, distributions endpoints |
| `backend/app/services/crop_service.py` | BiLSTM crop inference logic & probability extraction |
| `backend/app/services/price_service.py` | Autoregressive multi-step recursive LSTM lookback inference |
| `backend/app/services/yield_service.py` | Deep Neural Network district yield regression inference |
| `backend/app/services/decision_service.py`| Multi-model orchestration, normalized composite scoring, dynamic explainability |
| `backend/app/services/metrics_service.py` | Thread-safe in-memory API telemetry and latency profiling |
| `backend/app/services/drift_service.py` | Statistical Z-score data drift monitoring engine |
| `backend/app/services/distribution_service.py`| Prediction output distribution aggregation service |
| `backend/app/services/model_registry_service.py`| Safe model metadata provider (zero filesystem path exposure) |

---

## 3. Core Frontend Modules Map

| Module Path | Primary Responsibility |
| :--- | :--- |
| `frontend/src/app/core/guards/auth.guard.ts` | Functional client-side route guard enforcing authentication |
| `frontend/src/app/core/interceptors/auth.interceptor.ts` | Functional HTTP interceptor attaching Bearer JWT token |
| `frontend/src/app/core/services/auth.service.ts` | Authentication state, signals, token decoding, login/register HTTP calls |
| `frontend/src/app/core/services/decision.service.ts` | AI decision support API communication service |
| `frontend/src/app/core/services/monitoring.service.ts` | MLOps telemetry, health, drift, and model registry HTTP client service |
| `frontend/src/app/features/dashboard/dashboard.component.ts` | Executive dashboard, stat cards, prediction distribution charts |
| `frontend/src/app/features/crop-recommendation/` | Crop recommendation UI, nutrient inputs, radar chart, probability bars |
| `frontend/src/app/features/price-forecast/` | Price forecasting UI, commodity selectors, 7-day trajectory chart |
| `frontend/src/app/features/yield-forecast/` | Yield forecasting UI, cascading district dropdowns, density cards |
| `frontend/src/app/features/decision-support/` | Level 7 AI Decision UI, 13-parameter form, multi-bar chart, dynamic rationale |
| `frontend/src/app/features/monitoring/` | Level 8 MLOps UI, 5 tabs, pulse indicators, drift tables, inspection modals |
| `frontend/src/app/features/history/` | Prediction history UI, pagination, filter chips, JSON modals, delete dialog |