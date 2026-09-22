def test_price_forecast_7_day_success(client):
    """Verify /api/v1/price/forecast generates 7-day price trajectory."""
    payload = {
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": [1500.0 + i * 10 for i in range(30)],
        "forecast_horizon": 7
    }
    response = client.post("/api/v1/price/forecast", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["commodity"] == "Onion"
    assert data["market"] == "Lasalgaon"
    assert data["forecast_horizon_days"] == 7
    assert len(data["forecasts"]) == 7
    assert data["last_observed_price"] == 1790.0
    assert data["trend_direction"] in ["UPWARD", "DOWNWARD", "STABLE"]
    assert data["execution_time_ms"] > 0


def test_price_forecast_1_day_and_30_day(client):
    """Verify supported horizons: 1 day and 30 days."""
    prices = [1400.0 + (i % 5) * 10 for i in range(35)]

    # 1 Day
    res1 = client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": prices,
        "forecast_horizon": 1
    })
    assert res1.status_code == 200
    assert len(res1.json()["data"]["forecasts"]) == 1

    # 30 Days
    res30 = client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": prices,
        "forecast_horizon": 30
    })
    assert res30.status_code == 200
    assert len(res30.json()["data"]["forecasts"]) == 30


def test_price_forecast_validation_errors(client):
    """Verify rejection of insufficient observations and unsupported horizons."""
    # Insufficient observations (< 30)
    res1 = client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": [1500.0] * 15,
        "forecast_horizon": 7
    })
    assert res1.status_code == 422

    # Unsupported horizon (e.g. 5 days)
    res2 = client.post("/api/v1/price/forecast", json={
        "commodity": "Onion",
        "market": "Lasalgaon",
        "historical_prices": [1500.0] * 30,
        "forecast_horizon": 5
    })
    assert res2.status_code == 422
