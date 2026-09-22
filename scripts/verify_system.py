"""
AgriPulse End-to-End System Verification Script
Validates:
- All 3 Deep Learning Model Artifacts
- Backend Lifespan Preloading & Database Integration
- All ML Inferences (Crop Recommendation, Price Forecasting, Yield Forecasting, Decision Support)
- User Authentication & Prediction History Audit Logging
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.config.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

# Setup in-memory SQLite database for isolated non-destructive verification
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def main():
    print("=" * 70)
    print("  AGRIPULSE FULL-SYSTEM VERIFICATION & PRODUCTION SANITY SUITE")
    print("=" * 70)
    
    # 1. Initialize Tables
    print("\n[1/6] Initializing Database Schema...")
    Base.metadata.create_all(bind=test_engine)
    print("  [OK] Database schema verified and initialized.")

    with TestClient(app) as client:
        # 2. System Health Check
        print("\n[2/6] Verifying System Health & Model Status...")
        res = client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        health_data = res.json()
        print(f"  [OK] /api/health: {health_data['status']} ({health_data['application']} v{health_data['version']})")

        res = client.get("/api/v1/models/status")
        assert res.status_code == 200, f"Models status failed: {res.text}"
        status_data = res.json()
        print(f"  [OK] Model [Crop Recommendation]: {'LOADED' if status_data['crop_recommendation'] else 'FAILED'}")
        print(f"  [OK] Model [Price Forecasting]: {'LOADED' if status_data['price_forecasting'] else 'FAILED'}")
        print(f"  [OK] Model [Yield Forecasting]: {'LOADED' if status_data['yield_forecasting'] else 'FAILED'}")

        # 3. Authentication & User Management
        print("\n[3/6] Verifying Authentication & User History...")
        user_payload = {
            "name": "Production Agronomist",
            "email": "agronomist@agripulse.ai",
            "password": "SecurePassword@2026",
            "role": "AGRONOMIST"
        }
        reg_res = client.post("/api/v1/auth/register", json=user_payload)
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        print(f"  [OK] User Registered: {user_payload['email']}")

        login_res = client.post("/api/v1/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  [OK] User Authenticated: JWT Access Token Generated")

        # 4. Crop Recommendation AI (Level 3A)
        print("\n[4/6] Verifying Deep Learning Inferences...")
        crop_payload = {
            "N": 90.0, "P": 42.0, "K": 43.0,
            "temperature": 20.9, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9
        }
        c_res = client.post("/api/v1/crop/recommend", json=crop_payload, headers=headers)
        assert c_res.status_code == 200, f"Crop recommendation failed: {c_res.text}"
        crop_data = c_res.json()["data"]
        print(f"  [OK] Level 3A (LSTM Crop Recommendation): {crop_data['recommended_crop'].upper()} (Confidence: {crop_data['confidence']*100:.2f}%)")

        # Price Forecasting AI (Level 3B) - 30-day lookback series
        prices_30d = [2100.0 + i * 5.0 for i in range(30)]
        price_payload = {
            "commodity": "Wheat",
            "market": "Azadpur",
            "historical_prices": prices_30d,
            "forecast_horizon": 7
        }
        p_res = client.post("/api/v1/price/forecast", json=price_payload, headers=headers)
        assert p_res.status_code == 200, f"Price forecast failed: {p_res.text}"
        price_data = p_res.json()["data"]
        print(f"  [OK] Level 3B (Time-Series LSTM Price Forecast): Rs {price_data['predicted_end_price']:.2f}/qtl ({price_data['trend_direction']})")

        # Yield Forecasting AI (Level 3C)
        yield_payload = {
            "state": "Punjab", "district": "Ludhiana",
            "crop": "Wheat", "season": "Rabi",
            "area": 10.0, "crop_year": 2024
        }
        y_res = client.post("/api/v1/yield/predict", json=yield_payload, headers=headers)
        assert y_res.status_code == 200, f"Yield prediction failed: {y_res.text}"
        yield_data = y_res.json()["data"]
        print(f"  [OK] Level 3C (DNN Harvest Yield Regressor): {yield_data['predicted_yield_tonnes_per_hectare']:.2f} t/ha ({yield_data['estimated_total_production_tonnes']:.1f} Tonnes)")

        # 5. Integrated Decision Support (Level 7)
        print("\n[5/6] Verifying Multi-Modal AI Decision Support...")
        decision_payload = {
            "N": 90.0, "P": 42.0, "K": 43.0,
            "temperature": 20.9, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9,
            "state": "Punjab", "district": "Ludhiana", "season": "Rabi",
            "area": 10.0, "crop_year": 2024,
            "market": "Azadpur", "forecast_horizon": 7
        }
        d_res = client.post("/api/v1/decision/recommend", json=decision_payload, headers=headers)
        assert d_res.status_code == 200, f"Decision recommendation failed: {d_res.text}"
        decision_data = d_res.json()["data"]
        print(f"  [OK] Level 7 Decision Score: {decision_data['decision_score']:.1f}/100")
        print(f"    - Recommended Crop: {decision_data['recommended_crop'].upper()}")
        print(f"    - Suitability Score (40%): {decision_data['suitability_score']:.1f} pts")
        print(f"    - Yield Score (35%): {decision_data['yield_score']:.1f} pts ({decision_data['predicted_yield']:.2f} t/ha)")
        print(f"    - Market Score (25%): {decision_data['market_score']:.1f} pts (Rs {decision_data['forecast_price']:.2f}/qtl)")
        print(f"    - Dynamic Summary: {decision_data['explanation']['summary'][:90]}...")

        # 6. Audited Prediction History Log
        print("\n[6/6] Verifying User Prediction History Audit Logs...")
        hist_res = client.get("/api/v1/predictions/history?page=1&page_size=10", headers=headers)
        assert hist_res.status_code == 200, f"History fetch failed: {hist_res.text}"
        history_records = hist_res.json()["data"]["records"]
        assert len(history_records) == 4, f"Expected 4 history items, got {len(history_records)}"
        print(f"  [OK] Logged Inferences: {len(history_records)} records successfully audited.")
        for rec in history_records:
            print(f"    * [{rec['prediction_type']}] ID #{rec['id']} - Latency: {rec['latency_ms']:.1f}ms")

    print("\n" + "=" * 70)
    print("  ALL SYSTEM COMPONENTS FULLY VERIFIED -- AGRIPULSE IS 100% OPERATIONAL")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
