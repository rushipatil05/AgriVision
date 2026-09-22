import pytest
from app.models.user import User
from app.auth.password import hash_password


@pytest.fixture
def auth_header(client, db_session):
    """Creates a test user and returns an Authorization Bearer header."""
    user = User(
        name="Decision Researcher",
        email="researcher.decision@agripulse.com",
        password_hash=hash_password("securepassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "researcher.decision@agripulse.com", "password": "securepassword123"}
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, user


def test_01_decision_recommendation_success(client):
    """Verifies successful end-to-end Agricultural Decision Support orchestration."""
    payload = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.87,
        "humidity": 82.00,
        "ph": 6.50,
        "rainfall": 202.93,
        "state": "Punjab",
        "district": "Ludhiana",
        "season": "Rabi",
        "area": 10.0,
        "crop_year": 2024,
        "market": "Azadpur",
        "forecast_horizon": 7
    }

    response = client.post("/api/v1/decision/recommend", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True

    data = json_data["data"]
    assert "recommended_crop" in data
    assert data["recommended_crop"] is not None
    assert 0.0 <= data["decision_score"] <= 100.0
    assert 0.0 <= data["suitability_score"] <= 100.0
    assert 0.0 <= data["yield_score"] <= 100.0
    assert 0.0 <= data["market_score"] <= 100.0
    assert data["predicted_yield"] > 0.0
    assert data["estimated_production_tonnes"] > 0.0
    assert data["forecast_price"] > 0.0
    assert data["price_trend"] in ["UPWARD", "DOWNWARD", "STABLE"]

    # Verify Explanation
    explanation = data["explanation"]
    assert len(explanation["summary"]) > 20
    assert len(explanation["soil_compatibility"]) > 10
    assert len(explanation["climatic_suitability"]) > 10
    assert len(explanation["yield_potential"]) > 10
    assert len(explanation["market_outlook"]) > 10
    assert len(explanation["key_advantages"]) >= 1

    # Verify Alternatives Ranking
    alternatives = data["alternatives"]
    assert len(alternatives) >= 1
    # Check monotonic rank and descending decision score
    for i in range(len(alternatives) - 1):
        assert alternatives[i]["decision_score"] >= alternatives[i + 1]["decision_score"]
        assert alternatives[i]["rank"] < alternatives[i + 1]["rank"]


def test_02_decision_with_custom_historical_prices(client):
    """Verifies decision recommendation with user-supplied 30-day price series."""
    hist = [2100.0 + i * 10 for i in range(30)]
    payload = {
        "N": 71.0,
        "P": 54.0,
        "K": 20.0,
        "temperature": 22.6,
        "humidity": 65.4,
        "ph": 5.7,
        "rainfall": 82.3,
        "state": "Maharashtra",
        "district": "Nashik",
        "season": "Kharif",
        "area": 15.0,
        "crop_year": 2024,
        "market": "Lasalgaon",
        "forecast_horizon": 7,
        "historical_prices": hist
    }

    response = client.post("/api/v1/decision/recommend", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["market"] == "Lasalgaon"


def test_03_decision_validation_errors(client):
    """Verifies 422 Unprocessable Entity on out-of-range inputs."""
    # Negative Nitrogen
    res1 = client.post("/api/v1/decision/recommend", json={
        "N": -10.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 100.0
    })
    assert res1.status_code == 422

    # Zero or negative area
    res2 = client.post("/api/v1/decision/recommend", json={
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 100.0,
        "area": 0.0
    })
    assert res2.status_code == 422


def test_04_authenticated_decision_persists_history(client, auth_header):
    """Verifies that an authenticated decision recommendation binds to user history."""
    headers, user = auth_header

    payload = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.87,
        "humidity": 82.00,
        "ph": 6.50,
        "rainfall": 202.93,
        "state": "Punjab",
        "district": "Ludhiana",
        "season": "Rabi",
        "area": 5.0
    }

    response = client.post("/api/v1/decision/recommend", json=payload, headers=headers)
    assert response.status_code == 200

    # Query prediction history
    hist_res = client.get("/api/v1/predictions/history?prediction_type=DECISION", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert hist_data["total"] >= 1
    assert hist_data["records"][0]["prediction_type"] == "DECISION"
    assert hist_data["records"][0]["user_id"] == user.id
