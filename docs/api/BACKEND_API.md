# AgriPulse Backend REST API & Service Layer Architecture

**Project**: AgriPulse — Precision Agriculture Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Framework**: FastAPI (Python 3.13) + Uvicorn + SQLAlchemy + Pydantic v2 + PostgreSQL + PyJWT + bcrypt  

---

## 1. System Architecture

The AgriPulse Backend serves as the central orchestration engine connecting client applications (Angular frontend, web clients) with machine learning inference pipelines and persistent transactional databases.

```
┌────────────────────────────────────────────────────────┐
│               Client Applications / UI                 │
│              (Angular Material Frontend)               │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON REST
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Application                  │
│       - CORS Middleware & Request Validation           │
│       - Bearer JWT Security & User Dependencies        │
│       - Centralized Exception Handlers (400, 422, 500) │
│       - Lifespan Startup Model Pre-loading             │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  /api/v1/auth        /api/v1/predictions  /api/v1/crop /price /yield
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌───────────────────────────────┐
│ AuthService  │    │PredictionSvc │    │ Unified ML Service Orchestrtr │
│ (JWT+bcrypt) │    │(User History)│    │(app.services.ml_service)      │
└───────┬──────┘    └──────┬───────┘    └───────┬───────────────┬───────┘
        │                  │                    │               │
        │                  │                    ▼               ▼
        │                  │            ┌──────────────┐ ┌──────────────┐
        │                  │            │  Crop Rec.   │ │ Price Frcst. │
        │                  │            │  (LSTM Model)│ │ (LSTM Model) │
        │                  │            └──────────────┘ └──────────────┘
        │                  │                    │
        │                  │                    ▼
        │                  │            ┌──────────────┐
        │                  │            │ Yield Frcst. │
        │                  │            │ (DNN Model)  │
        │                  │            └──────────────┘
        │                  │                    │
        └──────────────────┼────────────────────┘
                           ▼
    ┌───────────────────────────────────────────────┐
    │       Database Persistence (SQLAlchemy)       │
    │        - users (Registered accounts)          │
    │        - prediction_history (Audit Trail)     │
    └───────────────────────────────────────────────┘
```

---

## 2. API Endpoints

### 2.1 Authentication & User Management

#### `POST /api/v1/auth/register`
- **Description**: Registers a new user account with secure bcrypt password hashing.
- **Request Body**:
```json
{
  "name": "Kisan Sharma",
  "email": "kisan.sharma@example.com",
  "password": "StrongPassword123!"
}
```
- **Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Kisan Sharma",
    "email": "kisan.sharma@example.com",
    "is_active": true,
    "created_at": "2026-09-04T23:36:25.037000",
    "updated_at": "2026-09-04T23:36:25.037000"
  },
  "error": null
}
```

#### `POST /api/v1/auth/login`
- **Description**: Authenticates user credentials and issues a signed JWT access token.
- **Request Body**:
```json
{
  "email": "kisan.sharma@example.com",
  "password": "StrongPassword123!"
}
```
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "name": "Kisan Sharma",
      "email": "kisan.sharma@example.com",
      "is_active": true,
      "created_at": "2026-09-04T23:36:25.037000",
      "updated_at": "2026-09-04T23:36:25.037000"
    }
  },
  "error": null
}
```

#### `GET /api/v1/auth/me`
- **Description**: Retrieves current authenticated user profile.
- **Header**: `Authorization: Bearer <token>`
- **Response**: `200 OK`

#### `POST /api/v1/auth/logout`
- **Description**: Stateless logout confirming client token removal.
- **Header**: `Authorization: Bearer <token>`
- **Response**: `200 OK`

---

### 2.2 System & Health Endpoints

#### `GET /api/v1/health`
- **Description**: System health check.

#### `GET /api/v1/models/status`
- **Description**: Returns memory load status and artifact paths for all 3 ML subsystems.

---

### 2.3 Machine Learning Inference Endpoints

#### `POST /api/v1/crop/recommend`
- **Description**: Recommends top-k ranked suitable crops based on soil and weather conditions using LSTM.
- **Header (Optional)**: `Authorization: Bearer <token>` (associates prediction with user account).

#### `POST /api/v1/price/forecast`
- **Description**: Multi-step spot market price forecasting using Time-Series LSTM.
- **Header (Optional)**: `Authorization: Bearer <token>`.

#### `POST /api/v1/yield/predict`
- **Description**: Regional crop yield and total harvest volume estimation using Deep Neural Network regression.
- **Header (Optional)**: `Authorization: Bearer <token>`.

---

### 2.4 Prediction History & Audit Trail

#### `GET /api/v1/predictions/history`
- **Description**: Returns paginated historical inference records belonging strictly to the authenticated user.
- **Header**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page` (default: 1)
  - `page_size` (default: 20, max: 100)
  - `prediction_type` (optional: `CROP_RECOMMENDATION`, `PRICE_FORECAST`, `YIELD_FORECAST`)

#### `DELETE /api/v1/predictions/history/{prediction_id}`
- **Description**: Deletes a specific prediction history record belonging to the authenticated user. Returns 404 if not found or belongs to another user.
- **Header**: `Authorization: Bearer <token>`

---

## 3. Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

-- Prediction History Audit Trail
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    prediction_type VARCHAR(50) NOT NULL,
    input_data JSON NOT NULL,
    prediction_result JSON NOT NULL,
    latency_ms FLOAT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
```

---

## 4. Error Handling Architecture

All API endpoints return standard structured error JSON responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR | BAD_REQUEST | HTTP_401 | HTTP_404 | HTTP_409 | INTERNAL_SERVER_ERROR",
    "message": "Human-readable explanation",
    "details": [...]
  }
}
```
