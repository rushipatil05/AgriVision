def test_models_status_endpoint(client):
    """Verify /api/v1/models/status returns operational status of all 3 ML models."""
    response = client.get("/api/v1/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "crop_recommendation" in data
    assert "price_forecasting" in data
    assert "yield_forecasting" in data
    assert "details" in data

    # Verify all models are loaded
    assert data["crop_recommendation"] == "loaded"
    assert data["price_forecasting"] == "loaded"
    assert data["yield_forecasting"] == "loaded"
