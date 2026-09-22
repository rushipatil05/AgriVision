# AgriPulse: System Architecture Design Document

## 1. System Topology Overview

AgriPulse is built as a cloud-ready, software-only precision agriculture platform utilizing a decoupled 3-tier architectural model:

```
+-------------------------------------------------------------------------+
|                              CLIENT TIER                                |
|  Angular 17+ Single Page Application (SPA)                              |
|  - Farmer Dashboard | Admin Dashboard | Charts | Material UI            |
+------------------------------------+------------------------------------+
                                     |
                          HTTPS / REST API / JWT
                                     |
+------------------------------------v------------------------------------+
|                            APPLICATION TIER                             |
|  FastAPI Application Server (Uvicorn / Asynchronous ASGI)                |
|  +---------------------------+  +-------------------------------------+ |
|  | Auth & Security Layer     |  | Business Logic Layer                | |
|  | - JWT Handler (OAuth2)    |  | - Recommendation Engine             | |
|  | - Role Guards (RBAC)      |  | - Profitability & Harvest Logic     | |
|  | - Password Hasher (Bcrypt)|  | - Weather Proxy Client (Async)      | |
|  +---------------------------+  +-------------------------------------+ |
|  +--------------------------------------------------------------------+ |
|  | Deep Learning Inference Subsystem (TensorFlow / Keras / Sklearn)   | |
|  | - Crop Recommendation LSTM Model                                   | |
|  | - Commodity Price Time-Series LSTM Model                           | |
|  | - Crop Yield Forecasting Model                                     | |
|  | - Model Explainability Layer (SHAP)                                | |
|  +--------------------------------------------------------------------+ |
+------------------+------------------------------------+-----------------+
                   |                                    |
            SQL / SQLAlchemy                     External REST
                   |                                    |
+------------------v--------------+       +-------------v-----------------+
|          PERSISTENCE TIER       |       |       EXTERNAL SERVICES       |
|  PostgreSQL Relational Database |       |  External Weather Provider    |
|  - Users, Farms, Crops          |       |  (e.g., OpenWeatherMap API)   |
|  - Predictions, Historical Logs |       +-------------------------------+
+---------------------------------+
```

---

## 2. Component Design & Responsibilities

### 2.1 Frontend Client (`frontend/agripulse-ui`)
- **Framework**: Angular 17+ with TypeScript.
- **Component Library**: Angular Material for UI components.
- **Visual Analytics**: Chart.js / `ng2-charts` for time-series forecasting curves, yield bar charts, and top-5 probability radars.
- **Architecture**:
  - `core/`: Global singleton services, HTTP interceptors (JWT auth injection, error interception), base guards.
  - `shared/`: Reusable UI widgets, alert modals, pipes, and data table components.
  - `features/auth/`: Login, registration, token storage.
  - `features/farmer/`: Crop recommendation workflow, price forecasting view, yield & profit calculator, weather dashboard, history explorer.
  - `features/admin/`: System telemetry, user management, crop catalog administration.

### 2.2 Backend Application (`backend/`)
- **Framework**: FastAPI (Python 3.11+).
- **Structure**:
  - `app/config/`: Pydantic settings loading from `.env`.
  - `app/auth/`: JWT token lifecycle, hashing, role dependencies.
  - `app/models/`: SQLAlchemy 2.0 ORM database declarations.
  - `app/schemas/`: Pydantic input validation and response serialization schemas.
  - `app/services/`: Dedicated business logic handlers (ML model inference loaders, profitability calculators, weather integration).
  - `app/routes/`: Versioned API endpoint routers (`/api/v1/auth`, `/api/v1/recommendations`, `/api/v1/forecasts`, `/api/v1/weather`, `/api/v1/farmer`, `/api/v1/admin`).

### 2.3 Machine Learning & Deep Learning Subsystem (`ml/`)
- **Crop Recommendation**:
  - Recurrent neural network (LSTM) processing normalized agricultural feature vectors: $[N, P, K, \text{Temp}, \text{Humidity}, \text{pH}, \text{Rainfall}]$.
  - Softmax classification output producing ranked probabilities across eligible crops.
- **Price Forecasting**:
  - Time-series sliding window LSTM trained on sequential commodity spot prices.
  - Generates multi-step lookahead price points and computed trajectory metrics ($\Delta\%$, Trend Direction).
  - Enforces strict chronological splits (train/val/test) without shuffling.
- **Yield Forecasting**:
  - Deep regression model correlating historical yield trends, regional data, and climatic variables.
- **Explainability**:
  - Model feature attribution and importance scoring (SHAP) where applicable.

---

## 3. Database Schema Architecture (`database/`)

PostgreSQL is structured with high relational integrity, foreign key cascades, unique constraints, and B-tree indexes on lookup fields:

```
[users] 1 ──── ∞ [farms]
   │                │
   │ 1              │ 1
   │                │
   │ ∞              │ ∞
[prediction_history] ──────── [crop_predictions]
   │
   ├─────── [price_forecasts]
   ├─────── [yield_forecasts]
   └─────── [weather_records]

[crop_information] (Master reference table: NPK bounds, harvest duration, baseline costs)
[market_prices] (Historical and reference price sequences per market/crop)
```

### Table Summary:
1. `users`: `id`, `email`, `hashed_password`, `full_name`, `role` (`FARMER` | `ADMIN`), `is_active`, `created_at`.
2. `farms`: `id`, `user_id` (FK), `farm_name`, `state`, `district`, `soil_type`, `total_area_hectares`, `created_at`.
3. `crop_information`: `id`, `crop_name`, `min_harvest_days`, `max_harvest_days`, `estimated_cost_per_hectare`, `description`, `created_at`.
4. `market_prices`: `id`, `crop_name`, `market_name`, `state`, `price_per_quintal`, `record_date`.
5. `crop_predictions`: `id`, `user_id` (FK), `farm_id` (FK, nullable), `n`, `p`, `k`, `temperature`, `humidity`, `ph`, `rainfall`, `top_5_results` (JSONB), `best_crop`, `confidence`, `created_at`.
6. `price_forecasts`: `id`, `user_id` (FK), `crop_name`, `market_name`, `current_price`, `predicted_price`, `forecast_horizon_days`, `percentage_change`, `trend`, `created_at`.
7. `yield_forecasts`: `id`, `user_id` (FK), `farm_id` (FK, nullable), `crop_name`, `state`, `area_hectares`, `predicted_yield_per_hectare`, `total_expected_yield`, `created_at`.
8. `weather_records`: `id`, `location_query`, `temperature`, `humidity`, `precipitation`, `weather_condition`, `recorded_at`.
9. `prediction_history`: `id`, `user_id` (FK), `activity_type`, `reference_id`, `summary_json` (JSONB), `created_at`.

---

## 4. Security Architecture

1. **Authentication**: Stateless Bearer tokens using JWT (JSON Web Tokens) signed with HMAC-SHA256.
2. **Password Security**: Cryptographically secure hashing via `bcrypt` with work factor (salt rounds).
3. **Role-Based Access Control (RBAC)**:
   - FastAPI dependency `get_current_active_user` validates token authenticity.
   - Declarative role verification `RoleChecker(["ADMIN"])` protects administrative operations.
4. **Data Isolation**: Farmers can only read and write data associated with their own `user_id`.
5. **CORS & Environment Hygiene**: Restricted origin whitelist via FastAPI CORSMiddleware. Absolute separation of environment secrets via `.env`.

---

## 5. Non-Functional & Operational Requirements

- **Zero-Hardware Dependency**: All telemetry, environmental variables, and inputs are software-driven or API-sourced.
- **Latency Target**: Model inference response times under 250ms per recommendation/forecast request.
- **Maintainability**: Clear separation of data models, schemas, business services, and API controllers.
- **Extensibility**: Pluggable architecture allowing new crop types and market datasets to be seeded without breaking database schema.
