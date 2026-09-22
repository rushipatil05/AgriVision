# LEVEL 8 SYSTEM ARCHITECTURE: MLOps, PRODUCTION MONITORING & TELEMETRY

**Project**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Status**: Level 8 Production Architecture Specification  

---

## 1. Architectural Overview

Level 8 establishes enterprise-grade MLOps observability, statistical data drift monitoring, automated endpoint telemetry profiling, prediction output distribution tracking, and centralized model registry governance for AgriPulse.

```mermaid
graph TD
    Client[Angular 18+ SPA Client] -->|HTTP / REST + Bearer JWT| APIGateway[FastAPI Telemetry Middleware]
    
    subgraph "FastAPI Backend In-Memory Layer"
        APIGateway --> TelemetryCollector[MetricsCollector Singleton]
        APIGateway --> ModelRegistry[ModelRegistryService]
        APIGateway --> InferenceRouter[Inference Pipelines 3A, 3B, 3C, 7]
    end

    subgraph "ML Inference Engines (Preloaded Singletons)"
        InferenceRouter --> CropLSTM[Crop Recommendation LSTM]
        InferenceRouter --> PriceLSTM[Price Forecasting LSTM]
        InferenceRouter --> YieldDNN[Yield Forecasting DNN]
        InferenceRouter --> DecisionDSS[Decision Support System]
    end

    subgraph "Statistical Monitoring & Governance"
        DriftEngine[DriftService] -->|Z-Score & KS Proxy| BaselineData[(ICAR / Kaggle Baselines)]
        DriftEngine -->|Live Inference Queries| HistoryDB[(PostgreSQL / SQLite)]
        DistEngine[DistributionService] -->|Aggregations| HistoryDB
        TelemetryCollector --> MetricsEndpoint[/api/v1/monitoring/metrics]
        ModelRegistry --> ModelsEndpoint[/api/v1/monitoring/models]
    end

    subgraph "Persistence & Audit"
        InferenceRouter -->|Async Audit Log| HistoryDB
    end
```

---

## 2. Telemetry & Latency Profiling Subsystem

### 2.1 Thread-Safe Metrics Collector
The `MetricsCollector` (`backend/app/services/metrics_service.py`) operates as an in-memory singleton protected by a thread lock (`threading.Lock`). It records:
- **System Uptime**: Initialized at application lifespan startup.
- **Request Counters**: Total requests, successful requests (HTTP 2xx), failed requests (HTTP 4xx/5xx).
- **Latency Tracking**: Min, max, average, and rolling window latencies per API endpoint.
- **Prediction Inferences**: Categorized by pipeline (`CROP_RECOMMENDATION`, `PRICE_FORECAST`, `YIELD_FORECAST`, `DECISION_SUPPORT`).

### 2.2 FastAPI Telemetry Middleware
The middleware intercepts every inbound HTTP request:
1. Captures high-precision timestamp before request execution ($t_{\text{start}}$).
2. Passes request downstream to route handler.
3. Captures completion timestamp ($t_{\text{end}}$) and computes latency in milliseconds:
   $$\Delta t = (t_{\text{end}} - t_{\text{start}}) \times 1000$$
4. Records endpoint path, HTTP status code, and latency to `MetricsCollector`.
5. Injects `X-Process-Time-Ms` response header for client-side diagnostics.

---

## 3. Statistical Data Drift Monitoring Subsystem

### 3.1 Feature Drift Engine
The `DriftService` (`backend/app/services/drift_service.py`) continuously compares live user-submitted soil and climate parameters ($N, P, K, \text{temperature}, \text{humidity}, \text{pH}, \text{rainfall}$) against the baseline distribution computed from the ICAR/Kaggle training dataset ($N = 2,200$ samples).

### 3.2 Drift Metric Formulation
For each feature $i \in \{N, P, K, T, H, pH, R\}$:
$$\text{Drift Score}_i = \frac{|\mu_{\text{current}, i} - \mu_{\text{baseline}, i}|}{\sigma_{\text{baseline}, i}}$$

### 3.3 Drift Classification Thresholds
- $\text{Drift Score} < 0.5 \implies \mathbf{HEALTHY}$ (Distribution matches training parameters)
- $0.5 \le \text{Drift Score} < 1.0 \implies \mathbf{MODERATE\_DRIFT}$ (Slight variance, monitor closely)
- $\text{Drift Score} \ge 1.0 \implies \mathbf{DRIFT\_DETECTED}$ (Significant deviation, potential retraining trigger)

### 3.4 Zero-Fabrication Minimum Sample Policy
To ensure scientific integrity:
- When live sample size $N_{\text{live}} < 5$, the drift engine strictly reports:
  $$\text{Status} = \mathbf{INSUFFICIENT\_DATA}$$
- Zero simulated or synthetic drift values are generated.

---

## 4. Output Distribution Monitoring Subsystem

The `DistributionService` (`backend/app/services/distribution_service.py`) aggregates historical predictions stored in PostgreSQL:
1. **Crop Recommendation**: Computes percentage frequency for all 22 crop classes.
2. **Price Forecasting**: Computes ratio of upward vs downward market price trajectories.
3. **Yield Forecasting**: Computes sample mean, median, minimum, and maximum yield (Tonnes/Hectare).
4. **Decision Support**: Computes composite decision score distribution ($0 \text{ to } 100$).

---

## 5. Model Registry & Governance Subsystem

The `ModelRegistryService` (`backend/app/services/model_registry_service.py`) provides an immutable catalog of production models:

| Model ID | Model Name | Architecture | Framework | Target Metric | Preload Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `crop_recommendation_lstm` | Crop Recommendation Model | Deep Learning LSTM | TensorFlow 2.15+ | **98.79% Accuracy** | Preloaded |
| `price_forecasting_lstm` | Price Forecasting Model | Time-Series LSTM | TensorFlow 2.15+ | **$R^2 = 0.9375$** | Preloaded |
| `yield_forecasting_dnn` | Crop Yield Regressor | Deep Neural Network | TensorFlow 2.15+ | **$R^2 = 0.9165$** | Preloaded |
| `decision_support_system` | AI Decision Support System | Multi-Modal Optimizer | Python / DL Composite | **Composite Score** | Active |

**Security Constraint**: Model internal filesystem paths (e.g. `saved_models/model.keras`) are strictly isolated within the backend runtime and never exposed through API responses or Angular UI schemas.