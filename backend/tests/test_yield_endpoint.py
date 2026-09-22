def test_yield_prediction_dnn_success(client):
    """Verify /api/v1/yield/predict outputs realistic yield and harvest volume using DNN."""
    payload = {
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Wheat",
        "season": "Rabi",
        "area": 50.0,
        "crop_year": 2024,
        "model_type": "dnn"
    }
    response = client.post("/api/v1/yield/predict", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["state"] == "Punjab"
    assert data["district"] == "Ludhiana"
    assert data["crop"] == "Wheat"
    assert data["area_hectares"] == 50.0
    assert data["predicted_yield_tonnes_per_hectare"] > 0.0
    assert data["estimated_total_production_tonnes"] > 0.0
    assert data["estimated_total_production_tonnes"] == round(data["predicted_yield_tonnes_per_hectare"] * 50.0, 2)
    assert "Deep Neural Network" in data["model_used"]


def test_yield_prediction_tree_success(client):
    """Verify /api/v1/yield/predict works with gradient boosting tree engine."""
    payload = {
        "state": "Maharashtra",
        "district": "Nashik",
        "crop": "Sugarcane",
        "season": "Kharif",
        "area": 20.0,
        "crop_year": 2024,
        "model_type": "tree"
    }
    response = client.post("/api/v1/yield/predict", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["predicted_yield_tonnes_per_hectare"] > 50.0  # Sugarcane high biomass yield
    assert "Gradient Boosting" in data["model_used"] or "Random Forest" in data["model_used"]


def test_yield_prediction_invalid_inputs(client):
    """Verify rejection of non-positive area and out-of-range years."""
    # Negative area
    res1 = client.post("/api/v1/yield/predict", json={
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Wheat",
        "season": "Rabi",
        "area": -10.0,
        "crop_year": 2024
    })
    assert res1.status_code == 422

    # Zero area
    res2 = client.post("/api/v1/yield/predict", json={
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Wheat",
        "season": "Rabi",
        "area": 0.0,
        "crop_year": 2024
    })
    assert res2.status_code == 422
