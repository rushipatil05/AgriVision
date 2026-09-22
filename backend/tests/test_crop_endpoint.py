def test_crop_recommendation_success(client):
    """Verify /api/v1/crop/recommend returns valid top-k recommendations with real probabilities."""
    payload = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.87,
        "humidity": 82.00,
        "ph": 6.50,
        "rainfall": 202.93,
        "top_k": 5
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert "recommended_crop" in data
    assert "confidence" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) == 5
    assert data["recommendations"][0]["crop"] == "rice"
    assert data["confidence"] > 0.8
    assert data["execution_time_ms"] > 0


def test_crop_recommendation_invalid_inputs(client):
    """Verify invalid soil/climatic inputs are rejected with 422."""
    # Negative Nitrogen
    res1 = client.post("/api/v1/crop/recommend", json={
        "N": -10.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 100.0
    })
    assert res1.status_code == 422
    assert res1.json()["success"] is False

    # Out-of-bounds pH (> 10)
    res2 = client.post("/api/v1/crop/recommend", json={
        "N": 50.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 12.5,
        "rainfall": 100.0
    })
    assert res2.status_code == 422
