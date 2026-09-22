# AgriPulse V1.0: End-to-End System Walkthrough & Architectural Trace

**Platform**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Execution Timestamp**: 2026-09-12 IST  
**Document Version**: 1.0 (Production-Ready Academic Release)

---

## 1. Executive System Walkthrough

AgriPulse is an enterprise-grade precision agriculture intelligence platform that leverages deep learning, time-series forecasting, multi-criteria decision optimization, and comprehensive MLOps telemetry.

```
USER INTERACTION
       │
       ▼
ANGULAR 18+ SPA FRONTEND (Signals + Standalone Components + Chart.js)
       │  (HTTP / JSON with JWT Bearer Token via HttpInterceptor)
       ▼
FASTAPI API GATEWAY (Asynchronous ASGI + Telemetry Middleware + CORS)
       │
       ├──────────────────────────────────────────────────────┐
       ▼                                                      ▼
AUTHENTICATION & AUDIT LAYER                          AI MODEL INFERENCE ENGINES
(Bcrypt 12 Rounds + HS256 JWT)                     (Preloaded TensorFlow & Scikit-Learn)
       │                                                      │
       │  ┌───────────────────────┬───────────────────────────┤
       │  ▼                       ▼                           ▼
       │ [Crop Rec LSTM]      [Price Forecaster LSTM]     [Yield DNN Regressor]
       │ (98.79% Acc)         (R² = 0.9375)               (R² = 0.9165)
       │  │                       │                           │
       │  └───────────────────────┼───────────────────────────┘
       │                          ▼
       │           [AI Decision Support System (Level 7)]
       │           (Multi-Criteria Normalized Optimization)
       │                          │
       ▼                          ▼
POSTGRESQL 15 DATABASE (Users, PredictionHistory, Audit Trail)
       │
       ▼
MLOPS TELEMETRY & MONITORING ENGINE (Level 8)
       ├── Thread-Safe MetricsCollector (Latency Profiling, Error Rates, RPS)
       ├── Statistical Data Drift Engine (Z-Shift & KS Divergence vs ICAR Baseline)
       ├── Prediction Output Distribution Analyzer (Crop, Price, Yield, DSS Stats)
       └── Model Registry Catalog (Immutable Metadata & Architecture Specs)
```

---

## 2. Detailed Layer-by-Layer Architectural Trace

### Layer 1: Angular 18+ Frontend SPA
- **Core Technology**: Angular 18+ standalone components, Angular Signals (`signal`, `computed`, `input`, `output`), RxJS reactive streams, Chart.js / `ng2-charts`.
- **User Journey**:
  1. **Authentication**: User logs in or registers via `/login` or `/register`. The JWT access token is stored securely in browser `localStorage`.
  2. **Interception**: `AuthInterceptor` automatically intercepts all outgoing HTTP requests to the `/api/v1` backend, attaching `Authorization: Bearer <jwt_token>`.
  3. **Guards**: `authGuard` verifies active authentication state; unauthenticated requests are redirected to `/login`.
  4. **Visualizations**: Interactive dashboards, probability bar charts, time-series line graphs, and multi-criteria comparison charts.

### Layer 2: FastAPI API Gateway & Middleware
- **Framework**: FastAPI (Python 3.10+) running over Uvicorn ASGI server.
- **Middleware Pipeline**:
  - **CORS Middleware**: Manages allowed origins (`http://localhost:4200`, `http://localhost:80`).
  - **Telemetry Middleware**: Calculates execution latency per request ($\Delta t$), records HTTP status codes, updates the in-memory `MetricsCollector`, and sets the `X-Process-Time-Ms` response header.
- **Dependency Injection**: SQLAlchemy `Session` management via `get_db()`, OAuth2 Bearer token extraction via `get_current_user()` and `get_optional_current_user()`.

### Layer 3: AI Deep Learning Model Inference Engines
- **Model Preloading**: In `app/main.py` lifespan handler, `ModelManager` initializes and preloads all neural weights into memory on startup, avoiding on-demand inference latency.
- **Inference Pipelines**:
  1. **Level 3A (Crop Recommendation)**: Receives $N, P, K, \text{temperature}, \text{humidity}, \text{pH}, \text{rainfall}$. Applies standard scaling, executes Bidirectional LSTM, and outputs top-5 crops with softmax probabilities.
  2. **Level 3B (Price Forecasting)**: Receives commodity, mandi market name, and minimum 30-day historical wholesale prices. Executes recursive multi-step LSTM lookback and outputs 1, 7, or 30-day projected prices with trend direction.
  3. **Level 3C (Yield Forecasting)**: Receives state, district, crop, season, acreage, and crop year. One-hot encodes categoricals, standard scales area/year, executes Deep Neural Network (DNN), and outputs predicted yield ($t/\text{ha}$) and total production ($t$).
  4. **Level 7 (Integrated Decision Support)**: Coordinates all 3 models concurrently. Generates candidate crops, forecasts expected yields and market prices, calculates a normalized composite **Decision Score** ($0 \le D \le 100$), and generates dynamic plain-English explainability rationale.

### Layer 4: PostgreSQL Persistence & Audit Trail
- **Tables**: `users` and `prediction_history`.
- **Auditing**: Every inference executed by an authenticated user is recorded with:
  - Input JSON parameters
  - Output prediction payload
  - Execution latency ($\text{ms}$)
  - User ID and timestamp
- **Isolation**: History queries are strictly filtered by `user_id = current_user.id`.

### Layer 5: MLOps Telemetry, Data Drift & Governance
- **Metrics Telemetry**: In-memory ring buffer tracking uptime, request counters, success/failure counts, and min/max/avg latency per route.
- **Data Drift**: Computes Z-score feature deviation against training baseline ($N=2,200$). If live sample size $< 5$, reports `INSUFFICIENT_DATA`.
- **Output Distributions**: Aggregates live database records to compute historical crop class percentages, price trend distributions, and yield statistics.
- **Model Registry**: Exposes immutable metadata for all 4 models without leaking internal server paths.