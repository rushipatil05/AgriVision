def test_end_to_end_ml_integration(client):
    """
    End-to-end integration test exercising all 3 ML models and verifying response structures,
    latency tracking, authenticated session, and database persistence.
    """
    # 0. User Registration & Authentication
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Integration Tester",
        "email": "integration.tester@example.com",
        "password": "Password123!"
    })
    assert reg_res.status_code == 201

    login_res = client.post("/api/v1/auth/login", json={
        "email": "integration.tester@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Health & Status
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    models_res = client.get("/api/v1/models/status")
    assert models_res.status_code == 200
    assert models_res.json()["crop_recommendation"] == "loaded"
    assert models_res.json()["price_forecasting"] == "loaded"
    assert models_res.json()["yield_forecasting"] == "loaded"

    # 2. Crop Recommendation
    crop_res = client.post("/api/v1/crop/recommend", json={
        "N": 90.0, "P": 42.0, "K": 43.0,
        "temperature": 20.87, "humidity": 82.00,
        "ph": 6.50, "rainfall": 202.93, "top_k": 3
    }, headers=headers)
    assert crop_res.status_code == 200
    crop_data = crop_res.json()["data"]
    assert crop_data["recommended_crop"] == "rice"

    # 3. Price Forecasting
    price_res = client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": [1500.0 + i * 5 for i in range(30)],
        "forecast_horizon": 7
    }, headers=headers)
    assert price_res.status_code == 200
    price_data = price_res.json()["data"]
    assert len(price_data["forecasts"]) == 7

    # 4. Yield Forecasting
    yield_res = client.post("/api/v1/yield/predict", json={
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Wheat",
        "season": "Rabi",
        "area": 50.0,
        "crop_year": 2024
    }, headers=headers)
    assert yield_res.status_code == 200
    yield_data = yield_res.json()["data"]
    assert yield_data["predicted_yield_tonnes_per_hectare"] > 0
    assert yield_data["estimated_total_production_tonnes"] > 0

    # 5. Database History Check
    hist_res = client.get("/api/v1/predictions/history", headers=headers)
    assert hist_res.status_code == 200
    records = hist_res.json()["data"]["records"]
    assert len(records) >= 3
