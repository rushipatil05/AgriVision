def test_prediction_history_audit_trail(client):
    """Verify that predictions from all 3 endpoints are persisted and retrievable via history endpoint for authenticated user."""
    # 0. Register & login user
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Audit Tester",
        "email": "audit.tester@example.com",
        "password": "Password123!"
    })
    assert reg_res.status_code == 201

    login_res = client.post("/api/v1/auth/login", json={
        "email": "audit.tester@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Trigger Crop Recommendation
    client.post("/api/v1/crop/recommend", json={
        "N": 90.0, "P": 42.0, "K": 43.0,
        "temperature": 20.87, "humidity": 82.00,
        "ph": 6.50, "rainfall": 202.93, "top_k": 3
    }, headers=headers)

    # 2. Trigger Price Forecast
    client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": [1500.0 + i * 5 for i in range(30)],
        "forecast_horizon": 7
    }, headers=headers)

    # 3. Trigger Yield Forecast
    client.post("/api/v1/yield/predict", json={
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Wheat",
        "season": "Rabi",
        "area": 25.0,
        "crop_year": 2024
    }, headers=headers)

    # 4. Fetch all history
    res = client.get("/api/v1/predictions/history", headers=headers)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["total"] >= 3
    assert len(data["records"]) >= 3

    # Verify types exist
    types_found = {r["prediction_type"] for r in data["records"]}
    assert "CROP_RECOMMENDATION" in types_found
    assert "PRICE_FORECAST" in types_found
    assert "YIELD_FORECAST" in types_found

    # 5. Filter by type
    res_crop_only = client.get("/api/v1/predictions/history?prediction_type=CROP_RECOMMENDATION", headers=headers)
    assert res_crop_only.status_code == 200
    crop_records = res_crop_only.json()["data"]["records"]
    assert all(r["prediction_type"] == "CROP_RECOMMENDATION" for r in crop_records)
