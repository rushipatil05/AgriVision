import pytest
from app.models.user import User
from app.auth.password import hash_password


@pytest.fixture
def auth_header(client, db_session):
    """Creates a test user and returns an Authorization Bearer header."""
    user = User(
        name="Decision Researcher Mirror",
        email="mirror.decision@agripulse.com",
        password_hash=hash_password("securepassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "mirror.decision@agripulse.com", "password": "securepassword123"}
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, user


def test_01_decision_recommendation_success(client):
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
    assert 0.0 <= data["decision_score"] <= 100.0
    assert data["predicted_yield"] > 0.0
    assert data["forecast_price"] > 0.0
    assert len(data["alternatives"]) >= 1


def test_02_decision_validation_errors(client):
    res1 = client.post("/api/v1/decision/recommend", json={
        "N": -5.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 100.0
    })
    assert res1.status_code == 422


def test_03_authenticated_decision_persists_history(client, auth_header):
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

    hist_res = client.get("/api/v1/predictions/history?prediction_type=DECISION", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert hist_data["total"] >= 1
    assert hist_data["records"][0]["prediction_type"] == "DECISION"
