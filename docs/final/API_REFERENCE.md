# AgriPulse V1.0: REST API Reference Manual

**Base URL**: `http://localhost:8000/api/v1`  
**Interactive Swagger UI**: `http://localhost:8000/docs`  
**OpenAPI Specification**: `http://localhost:8000/openapi.json`  
**Version**: 1.0 (Production-Ready Academic Release)

---

## 1. Authentication Endpoints

### 1.1 User Registration
- **Method**: `POST`
- **URL**: `/api/v1/auth/register`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "name": "Dr. Ramesh Patel",
    "email": "ramesh.patel@agripulse.ai",
    "password": "SecurePassword123!"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "name": "Dr. Ramesh Patel",
      "email": "ramesh.patel@agripulse.ai",
      "is_active": true,
      "created_at": "2026-09-12T12:00:00Z",
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    },
    "message": "User registered successfully"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Email already registered.
  - `422 Unprocessable Content`: Weak password (less than 8 chars, missing uppercase, digit, or special char) or invalid email format.

---

### 1.2 User Login
- **Method**: `POST`
- **URL**: `/api/v1/auth/login`
- **Auth Required**: No
- **Request Content-Type**: `application/x-www-form-urlencoded`
- **Request Body**:
  ```
  username=ramesh.patel@agripulse.ai&password=SecurePassword123!
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "name": "Dr. Ramesh Patel",
        "email": "ramesh.patel@agripulse.ai",
        "is_active": true
      }
    },
    "message": "Login successful"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Invalid email or password credentials.

---

### 1.3 Get Current User Profile
- **Method**: `GET`
- **URL**: `/api/v1/auth/me`
- **Auth Required**: Bearer JWT (`Authorization: Bearer <token>`)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "name": "Dr. Ramesh Patel",
      "email": "ramesh.patel@agripulse.ai",
      "is_active": true,
      "created_at": "2026-09-12T12:00:00Z"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Token missing, expired, or invalid.

---

### 1.4 User Logout
- **Method**: `POST`
- **URL**: `/api/v1/auth/logout`
- **Auth Required**: Bearer JWT
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "Successfully logged out. Please remove token from client storage."
    }
  }
  ```

---

## 2. Machine Learning Inference Endpoints

### 2.1 Crop Recommendation (Level 3A)
- **Method**: `POST`
- **URL**: `/api/v1/crop/recommend`
- **Auth Required**: Optional (If authenticated, persists record to `prediction_history`)
- **Request Body**:
  ```json
  {
    "N": 90.0,
    "P": 42.0,
    "K": 43.0,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.93,
    "top_k": 5
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "recommended_crop": "rice",
      "confidence": 0.9966,
      "top_recommendations": [
        { "crop": "rice", "probability": 0.9966, "rank": 1 },
        { "crop": "jute", "probability": 0.0021, "rank": 2 },
        { "crop": "coffee", "probability": 0.0008, "rank": 3 },
        { "crop": "cotton", "probability": 0.0003, "rank": 4 },
        { "crop": "maize", "probability": 0.0001, "rank": 5 }
      ],
      "input_parameters": { "N": 90.0, "P": 42.0, "K": 43.0, "temperature": 20.87, "humidity": 82.0, "ph": 6.5, "rainfall": 202.93 },
      "execution_time_ms": 57.57,
      "model_type": "Bidirectional LSTM"
    }
  }
  ```

---

### 2.2 Market Price Forecasting (Level 3B)
- **Method**: `POST`
- **URL**: `/api/v1/price/forecast`
- **Auth Required**: Optional
- **Request Body**:
  ```json
  {
    "commodity": "Wheat",
    "market": "Azadpur",
    "historical_prices": [
      2100.0, 2110.0, 2105.0, 2120.0, 2130.0,
      2125.0, 2140.0, 2150.0, 2145.0, 2160.0,
      2170.0, 2165.0, 2180.0, 2190.0, 2185.0,
      2200.0, 2210.0, 2205.0, 2220.0, 2230.0,
      2225.0, 2240.0, 2250.0, 2245.0, 2260.0,
      2270.0, 2265.0, 2280.0, 2290.0, 2300.0
    ],
    "forecast_horizon": 7
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "commodity": "Wheat",
      "market": "Azadpur",
      "forecast_horizon_days": 7,
      "current_price": 2300.0,
      "forecasted_end_price": 2345.50,
      "price_change_absolute": 45.50,
      "price_change_percentage": 1.98,
      "trend_direction": "UPWARD",
      "forecasts": [
        { "day": 1, "forecasted_price": 2308.20 },
        { "day": 2, "forecasted_price": 2314.50 },
        { "day": 3, "forecasted_price": 2322.00 },
        { "day": 4, "forecasted_price": 2328.70 },
        { "day": 5, "forecasted_price": 2335.10 },
        { "day": 6, "forecasted_price": 2340.80 },
        { "day": 7, "forecasted_price": 2345.50 }
      ],
      "execution_time_ms": 401.94,
      "model_type": "Time-Series Multi-Step LSTM"
    }
  }
  ```

---

### 2.3 Crop Yield Forecasting (Level 3C)
- **Method**: `POST`
- **URL**: `/api/v1/yield/predict`
- **Auth Required**: Optional
- **Request Body**:
  ```json
  {
    "state": "Punjab",
    "district": "Ludhiana",
    "crop": "Wheat",
    "season": "Rabi",
    "area": 10.0,
    "crop_year": 2024
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "state": "Punjab",
      "district": "Ludhiana",
      "crop": "Wheat",
      "season": "Rabi",
      "area_hectares": 10.0,
      "crop_year": 2024,
      "predicted_yield_tonnes_per_hectare": 5.625,
      "estimated_total_production_tonnes": 56.25,
      "unit": "Tonnes/Hectare",
      "model_used": "Deep Neural Network",
      "execution_time_ms": 97.25
    }
  }
  ```

---

### 2.4 AI Agricultural Decision Support System (Level 7)
- **Method**: `POST`
- **URL**: `/api/v1/decision/recommend`
- **Auth Required**: Optional
- **Request Body**:
  ```json
  {
    "N": 90.0,
    "P": 42.0,
    "K": 43.0,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.93,
    "state": "Punjab",
    "district": "Ludhiana",
    "season": "Rabi",
    "area": 10.0,
    "crop_year": 2024,
    "market": "Azadpur",
    "forecast_horizon": 7
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "recommended_crop": "rice",
      "decision_score": 83.04,
      "crop_confidence": 0.997,
      "suitability_score": 99.7,
      "predicted_yield": 5.60,
      "yield_score": 100.0,
      "estimated_production_tonnes": 55.98,
      "market": "Azadpur",
      "forecast_price": 2454.30,
      "market_score": 32.7,
      "price_trend": "DOWNWARD",
      "forecast_horizon_days": 7,
      "alternatives": [
        {
          "rank": 1,
          "crop": "rice",
          "decision_score": 83.04,
          "suitability_probability": 0.997,
          "suitability_score": 99.7,
          "predicted_yield_tonnes_per_hectare": 5.60,
          "yield_score": 100.0,
          "forecasted_market_price": 2454.30,
          "market_score": 32.7,
          "price_trend": "DOWNWARD"
        }
      ],
      "explanation": {
        "summary": "Rice achieved the highest overall Agricultural Decision Score (83.04/100)...",
        "soil_compatibility": "Optimal soil N-P-K nutrient composition...",
        "climatic_suitability": "Climatic temperature and rainfall parameters are ideal...",
        "yield_potential": "High expected productivity (5.60 t/ha)...",
        "market_outlook": "Moderate wholesale mandi return (₹2454.30/qtl)...",
        "key_advantages": [
          "Soil nutrient suitability exceeds 95%",
          "Projected yield density is in top agricultural quintile"
        ]
      },
      "execution_time_ms": 1681.64
    }
  }
  ```

---

## 3. Prediction History Endpoints

### 3.1 Get Paginated Prediction History
- **Method**: `GET`
- **URL**: `/api/v1/predictions/history?page=1&page_size=10&prediction_type=ALL`
- **Auth Required**: Bearer JWT
- **Query Parameters**:
  - `page` (int, default: 1)
  - `page_size` (int, default: 10, max: 100)
  - `prediction_type` (string: `ALL`, `CROP_RECOMMENDATION`, `PRICE_FORECAST`, `YIELD_FORECAST`, `DECISION`)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "total": 4,
      "page": 1,
      "page_size": 10,
      "total_pages": 1,
      "records": [
        {
          "id": 4,
          "prediction_type": "DECISION",
          "input_data": { "N": 90.0, "state": "Punjab" },
          "prediction_result": { "recommended_crop": "rice", "decision_score": 83.04 },
          "latency_ms": 1681.64,
          "created_at": "2026-09-12T12:54:35Z"
        }
      ]
    }
  }
  ```

---

### 3.2 Delete Prediction Record
- **Method**: `DELETE`
- **URL**: `/api/v1/predictions/history/{prediction_id}`
- **Auth Required**: Bearer JWT
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "Prediction record deleted successfully.",
      "deleted_id": 4
    }
  }
  ```

---

## 4. MLOps & Monitoring Endpoints (Level 8)

### 4.1 System Health Check
- **Method**: `GET`
- **URL**: `/api/v1/monitoring/health`
- **Auth Required**: No
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "status": "healthy",
      "uptime_seconds": 3600,
      "timestamp": "2026-09-12T12:00:00Z",
      "database": { "status": "connected", "latency_ms": 1.25 },
      "models": {
        "crop_recommendation_lstm": { "status": "LOADED", "model_type": "Deep Learning LSTM" },
        "price_forecasting_lstm": { "status": "LOADED", "model_type": "Time-Series LSTM" },
        "yield_forecasting_dnn": { "status": "LOADED", "model_type": "Deep Neural Network" },
        "decision_support_system": { "status": "ACTIVE", "model_type": "Multi-Modal Optimizer" }
      }
    }
  }
  ```

---

### 4.2 Model Registry Metadata
- **Method**: `GET`
- **URL**: `/api/v1/monitoring/models`
- **Auth Required**: No
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "total_models": 4,
      "models": [
        {
          "model_id": "crop_recommendation_lstm",
          "model_name": "Crop Recommendation Model",
          "version": "v1.0.0-prod",
          "model_type": "Deep Learning LSTM",
          "framework": "TensorFlow 2.15+",
          "status": "active",
          "dataset_source": "ICAR & Kaggle Soil Dataset",
          "input_features": ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
          "metrics": { "accuracy": "98.79%", "val_loss": "0.041" }
        }
      ]
    }
  }
  ```

---

### 4.3 API Performance Metrics Telemetry
- **Method**: `GET`
- **URL**: `/api/v1/monitoring/metrics`
- **Auth Required**: No
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "uptime_seconds": 3600,
      "total_requests": 240,
      "successful_requests": 240,
      "failed_requests": 0,
      "success_rate_percentage": 100.0,
      "overall_avg_latency_ms": 285.4,
      "total_predictions": 120,
      "predictions_by_type": {
        "CROP_RECOMMENDATION": 30,
        "PRICE_FORECAST": 30,
        "YIELD_FORECAST": 30,
        "DECISION": 30
      },
      "endpoint_breakdown": [
        {
          "endpoint": "/api/v1/crop/recommend",
          "total_requests": 30,
          "successful_requests": 30,
          "failed_requests": 0,
          "avg_latency_ms": 57.57,
          "min_latency_ms": 52.92,
          "max_latency_ms": 66.69
        }
      ]
    }
  }
  ```

---

### 4.4 Data Drift Statistical Monitor
- **Method**: `GET`
- **URL**: `/api/v1/monitoring/drift?min_samples=5`
- **Auth Required**: No
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "status": "HEALTHY",
      "sample_size": 30,
      "method": "Z-shift and statistical parameter divergence analysis",
      "evaluated_at": "2026-09-12T12:00:00Z",
      "features": [
        {
          "feature": "N",
          "drift_score": 0.12,
          "status": "HEALTHY",
          "baseline_stats": { "mean": 50.55, "std": 36.92, "min": 0.0, "max": 140.0 },
          "current_stats": { "mean": 54.20, "std": 34.10, "min": 10.0, "max": 120.0 }
        }
      ],
      "message": "All evaluated features within acceptable statistical divergence bounds."
    }
  }
  ```

---

### 4.5 Prediction Output Distributions
- **Method**: `GET`
- **URL**: `/api/v1/monitoring/distributions`
- **Auth Required**: No
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "status": "success",
      "total_predictions": 120,
      "crop_recommendations": [
        { "crop": "rice", "count": 60, "percentage": 50.0 },
        { "crop": "wheat", "count": 30, "percentage": 25.0 }
      ],
      "price_forecasting": [
        { "trend": "UPWARD", "count": 80, "percentage": 66.7 },
        { "trend": "DOWNWARD", "count": 40, "percentage": 33.3 }
      ],
      "yield_forecasting": {
        "count": 30,
        "mean_yield_tonnes_per_ha": 5.62,
        "min_yield_tonnes_per_ha": 2.10,
        "max_yield_tonnes_per_ha": 26.59,
        "median_yield_tonnes_per_ha": 4.52
      },
      "decision_support": {
        "count": 30,
        "mean_score": 83.04,
        "min_score": 71.20,
        "max_score": 92.40,
        "median_score": 84.10
      },
      "message": "Output distributions successfully aggregated from prediction history."
    }
  }
  ```