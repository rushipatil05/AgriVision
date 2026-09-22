import pytest
from fastapi.testclient import TestClient
from app.models.prediction_history import PredictionHistory
from app.models.user import User


def test_01_models_metadata_endpoint(client: TestClient):
    """
    Verifies GET /api/v1/monitoring/models returns registry metadata for all models without leaking internal filepaths.
    """
    response = client.get("/api/v1/monitoring/models")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    models = data["data"]["models"]
    assert len(models) == 4

    model_ids = [m["model_id"] for m in models]
    assert "crop-recommendation-lstm-v1" in model_ids
    assert "price-forecasting-lstm-v1" in model_ids
    assert "yield-forecasting-dnn-v1" in model_ids
    assert "decision-support-synthesizer-v1" in model_ids

    # Verify no local filesystem path leakage
    for m in models:
        assert "D:\\" not in str(m)
        assert "C:\\" not in str(m)
        assert "/app/" not in str(m)
        assert m["version"] == "1.0.0"


def test_02_performance_metrics_endpoint(client: TestClient):
    """
    Verifies GET /api/v1/monitoring/metrics returns live telemetry.
    """
    # Trigger a request first
    client.get("/api/health")
    
    response = client.get("/api/v1/monitoring/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    metrics = data["data"]
    assert metrics["total_requests"] >= 1
    assert metrics["uptime_seconds"] >= 0.0
    assert metrics["success_rate_percentage"] >= 0.0
    assert isinstance(metrics["endpoint_breakdown"], list)


def test_03_monitoring_health_endpoint(client: TestClient):
    """
    Verifies GET /api/v1/monitoring/health consolidates DB ping and model readiness.
    """
    response = client.get("/api/v1/monitoring/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    health = data["data"]
    assert health["status"] in ["healthy", "degraded"]
    assert health["database"]["status"] == "connected"
    assert "crop_recommendation" in health["models"]
    assert "price_forecasting" in health["models"]
    assert "yield_forecasting" in health["models"]


def test_04_data_drift_endpoint(client: TestClient, db_session):
    """
    Verifies GET /api/v1/monitoring/drift handles insufficient data and calculates drift when samples exist.
    """
    # Clear history first
    db_session.query(PredictionHistory).delete()
    db_session.commit()

    # 1. Insufficient data test
    res = client.get("/api/v1/monitoring/drift?min_samples=5")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "INSUFFICIENT_DATA"
    assert data["sample_size"] == 0

    # 2. Inject sample predictions
    for i in range(6):
        rec = PredictionHistory(
            user_id=None,
            prediction_type="CROP_RECOMMENDATION",
            input_data={
                "N": 85.0 + i * 2,
                "P": 45.0 + i,
                "K": 40.0 + i,
                "temperature": 24.0 + i * 0.5,
                "humidity": 80.0,
                "ph": 6.5,
                "rainfall": 150.0
            },
            prediction_result={"recommended_crop": "rice", "confidence": 0.95},
            latency_ms=15.0
        )
        db_session.add(rec)
    db_session.commit()

    # 3. Test with samples present
    res_after = client.get("/api/v1/monitoring/drift?min_samples=5")
    assert res_after.status_code == 200
    data_after = res_after.json()["data"]
    assert data_after["sample_size"] >= 6
    assert data_after["status"] in ["HEALTHY", "MODERATE_DRIFT", "DRIFT_DETECTED"]
    assert len(data_after["features"]) == 7


def test_05_prediction_distributions_endpoint(client: TestClient, db_session):
    """
    Verifies GET /api/v1/monitoring/distributions returns aggregated output distributions.
    """
    # Inject diverse predictions
    db_session.add(PredictionHistory(
        prediction_type="CROP_RECOMMENDATION",
        input_data={"N": 90},
        prediction_result={"recommended_crop": "rice", "confidence": 0.98},
        latency_ms=10.0
    ))
    db_session.add(PredictionHistory(
        prediction_type="PRICE_FORECAST",
        input_data={"commodity": "Wheat"},
        prediction_result={"commodity": "Wheat", "forecasted_end_price": 2240.0, "trend_direction": "UPWARD"},
        latency_ms=12.0
    ))
    db_session.add(PredictionHistory(
        prediction_type="YIELD_FORECAST",
        input_data={"crop": "Wheat"},
        prediction_result={"crop": "Wheat", "predicted_yield_tonnes_per_hectare": 4.8},
        latency_ms=8.0
    ))
    db_session.add(PredictionHistory(
        prediction_type="DECISION",
        input_data={"crop": "Wheat"},
        prediction_result={"recommended_crop": "wheat", "decision_score": 87.5, "predicted_yield": 4.8, "forecast_price": 2240.0, "price_trend": "UPWARD"},
        latency_ms=25.0
    ))
    db_session.commit()

    res = client.get("/api/v1/monitoring/distributions")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "DATA_AVAILABLE"
    assert data["total_predictions"] >= 4
    assert data["crop_recommendations"] is not None
    assert data["yield_forecasting"] is not None
    assert data["price_forecasting"] is not None
    assert data["decision_support"] is not None
