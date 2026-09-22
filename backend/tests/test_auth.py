import pytest
import datetime
from app.auth.jwt import create_access_token, decode_access_token
from app.auth.password import hash_password, verify_password
from fastapi import HTTPException


# ==========================================
# 1-4: Registration Tests
# ==========================================

def test_01_registration_success(client):
    """1. Test successful user registration."""
    response = client.post("/api/v1/auth/register", json={
        "name": "Ramesh Kumar",
        "email": "ramesh.kumar@example.com",
        "password": "StrongPassword123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] is not None
    assert data["data"]["name"] == "Ramesh Kumar"
    assert data["data"]["email"] == "ramesh.kumar@example.com"
    assert "password" not in data["data"]
    assert "password_hash" not in data["data"]


def test_02_duplicate_email_registration(client):
    """2. Test registration conflict with duplicate email returns HTTP 409."""
    client.post("/api/v1/auth/register", json={
        "name": "First Farmer",
        "email": "duplicate@example.com",
        "password": "Password123!"
    })

    response = client.post("/api/v1/auth/register", json={
        "name": "Second Farmer",
        "email": "duplicate@example.com",
        "password": "AnotherPassword123!"
    })
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["error"]["message"].lower()


def test_03_weak_password_registration(client):
    """3. Test registration with password shorter than 8 characters returns 422."""
    response = client.post("/api/v1/auth/register", json={
        "name": "Weak Pass User",
        "email": "weakpass@example.com",
        "password": "short"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_04_invalid_email_registration(client):
    """4. Test registration with invalid email format returns 422."""
    response = client.post("/api/v1/auth/register", json={
        "name": "Bad Email User",
        "email": "not-an-email-address",
        "password": "StrongPassword123!"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


# ==========================================
# 5-7: Login Tests
# ==========================================

def test_05_login_success(client):
    """5. Test successful user login returns JWT token."""
    client.post("/api/v1/auth/register", json={
        "name": "Login Tester",
        "email": "login.tester@example.com",
        "password": "CorrectPassword123!"
    })

    response = client.post("/api/v1/auth/login", json={
        "email": "login.tester@example.com",
        "password": "CorrectPassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] > 0
    assert data["data"]["user"]["email"] == "login.tester@example.com"


def test_06_invalid_password_login(client):
    """6. Test login with wrong password returns 401 with generic error."""
    client.post("/api/v1/auth/register", json={
        "name": "Wrong Pass User",
        "email": "wrongpass@example.com",
        "password": "CorrectPassword123!"
    })

    response = client.post("/api/v1/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "IncorrectPassword999!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "invalid email or password" in data["error"]["message"].lower()


def test_07_nonexistent_email_login(client):
    """7. Test login with non-existent email returns generic 401."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent.user@example.com",
        "password": "AnyPassword123!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "invalid email or password" in data["error"]["message"].lower()


# ==========================================
# 8-11: JWT Lifecycle Tests
# ==========================================

def test_08_jwt_generation():
    """8. Test JWT token encoding with claims."""
    token = create_access_token({"sub": "42", "email": "test@example.com"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_09_jwt_validation():
    """9. Test JWT token decoding and payload verification."""
    token = create_access_token({"sub": "42", "email": "test@example.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload


def test_10_expired_jwt():
    """10. Test expired JWT token raises 401."""
    expired_delta = datetime.timedelta(seconds=-10)
    token = create_access_token({"sub": "42"}, expires_delta=expired_delta)

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_11_malformed_jwt():
    """11. Test malformed/garbage JWT token raises 401."""
    garbage_token = "invalid.token.payload.xyz"
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(garbage_token)
    assert exc_info.value.status_code == 401


# ==========================================
# 12-13: /auth/me Tests
# ==========================================

def test_12_auth_me_without_token(client):
    """12. Test GET /auth/me without authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_13_auth_me_with_valid_token(client):
    """13. Test GET /auth/me with valid Bearer token returns current user profile."""
    client.post("/api/v1/auth/register", json={
        "name": "Me User",
        "email": "me.user@example.com",
        "password": "Password123!"
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "me.user@example.com",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "me.user@example.com"
    assert data["data"]["name"] == "Me User"
    assert "password_hash" not in data["data"]


# ==========================================
# 14-17: Prediction History User Isolation Tests
# ==========================================

def test_14_prediction_history_ownership(client):
    """14. Test predictions made by user are assigned to their history."""
    client.post("/api/v1/auth/register", json={
        "name": "Farmer Alpha",
        "email": "alpha@example.com",
        "password": "Password123!"
    })
    token_a = client.post("/api/v1/auth/login", json={
        "email": "alpha@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    crop_res = client.post("/api/v1/crop/recommend", json={
        "N": 80.0, "P": 40.0, "K": 40.0,
        "temperature": 25.0, "humidity": 70.0,
        "ph": 6.5, "rainfall": 150.0, "top_k": 3
    }, headers=headers_a)
    assert crop_res.status_code == 200

    hist_res = client.get("/api/v1/predictions/history", headers=headers_a)
    assert hist_res.status_code == 200
    records = hist_res.json()["data"]["records"]
    assert len(records) >= 1
    assert records[0]["prediction_type"] == "CROP_RECOMMENDATION"


def test_15_user_cannot_access_another_users_history(client):
    """15. Test User B cannot view predictions created by User A."""
    client.post("/api/v1/auth/register", json={
        "name": "User Alpha",
        "email": "user.alpha@example.com",
        "password": "Password123!"
    })
    token_a = client.post("/api/v1/auth/login", json={
        "email": "user.alpha@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post("/api/v1/auth/register", json={
        "name": "User Beta",
        "email": "user.beta@example.com",
        "password": "Password123!"
    })
    token_b = client.post("/api/v1/auth/login", json={
        "email": "user.beta@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.post("/api/v1/crop/recommend", json={
        "N": 90.0, "P": 42.0, "K": 43.0,
        "temperature": 20.87, "humidity": 82.00,
        "ph": 6.50, "rainfall": 202.93, "top_k": 3
    }, headers=headers_a)

    hist_b = client.get("/api/v1/predictions/history", headers=headers_b)
    assert hist_b.status_code == 200
    assert hist_b.json()["data"]["total"] == 0
    assert len(hist_b.json()["data"]["records"]) == 0


def test_16_delete_own_prediction(client):
    """16. Test User can delete their own prediction record."""
    client.post("/api/v1/auth/register", json={
        "name": "Deleter User",
        "email": "deleter@example.com",
        "password": "Password123!"
    })
    token = client.post("/api/v1/auth/login", json={
        "email": "deleter@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/crop/recommend", json={
        "N": 50.0, "P": 50.0, "K": 50.0,
        "temperature": 22.0, "humidity": 60.0,
        "ph": 6.0, "rainfall": 100.0, "top_k": 2
    }, headers=headers)

    hist = client.get("/api/v1/predictions/history", headers=headers).json()["data"]
    pred_id = hist["records"][0]["id"]

    del_res = client.delete(f"/api/v1/predictions/history/{pred_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    hist_after = client.get("/api/v1/predictions/history", headers=headers).json()["data"]
    assert hist_after["total"] == 0


def test_17_cannot_delete_another_users_prediction(client):
    """17. Test User cannot delete another user's prediction record (returns 404)."""
    client.post("/api/v1/auth/register", json={
        "name": "Owner A",
        "email": "owner.a@example.com",
        "password": "Password123!"
    })
    token_a = client.post("/api/v1/auth/login", json={
        "email": "owner.a@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post("/api/v1/crop/recommend", json={
        "N": 50.0, "P": 50.0, "K": 50.0,
        "temperature": 22.0, "humidity": 60.0,
        "ph": 6.0, "rainfall": 100.0, "top_k": 2
    }, headers=headers_a)
    record_id = client.get("/api/v1/predictions/history", headers=headers_a).json()["data"]["records"][0]["id"]

    client.post("/api/v1/auth/register", json={
        "name": "Attacker B",
        "email": "attacker.b@example.com",
        "password": "Password123!"
    })
    token_b = client.post("/api/v1/auth/login", json={
        "email": "attacker.b@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    del_res = client.delete(f"/api/v1/predictions/history/{record_id}", headers=headers_b)
    assert del_res.status_code == 404
    assert "not found" in del_res.json()["error"]["message"].lower()

    hist_a = client.get("/api/v1/predictions/history", headers=headers_a).json()["data"]
    assert hist_a["total"] == 1


# ==========================================
# 18-20: History Features & Logout Tests
# ==========================================

def test_18_prediction_history_pagination(client):
    """18. Test prediction history pagination with page and page_size."""
    client.post("/api/v1/auth/register", json={
        "name": "Paginator User",
        "email": "paginator@example.com",
        "password": "Password123!"
    })
    token = client.post("/api/v1/auth/login", json={
        "email": "paginator@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(5):
        client.post("/api/v1/crop/recommend", json={
            "N": 40.0 + i, "P": 40.0, "K": 40.0,
            "temperature": 25.0, "humidity": 70.0,
            "ph": 6.5, "rainfall": 100.0, "top_k": 1
        }, headers=headers)

    res_p1 = client.get("/api/v1/predictions/history?page=1&page_size=2", headers=headers)
    assert res_p1.status_code == 200
    d1 = res_p1.json()["data"]
    assert d1["total"] == 5
    assert len(d1["records"]) == 2
    assert d1["page"] == 1
    assert d1["total_pages"] == 3

    res_p3 = client.get("/api/v1/predictions/history?page=3&page_size=2", headers=headers)
    assert res_p3.status_code == 200
    d3 = res_p3.json()["data"]
    assert len(d3["records"]) == 1


def test_19_prediction_history_type_filtering(client):
    """19. Test filtering prediction history by prediction_type."""
    client.post("/api/v1/auth/register", json={
        "name": "Filter User",
        "email": "filter.user@example.com",
        "password": "Password123!"
    })
    token = client.post("/api/v1/auth/login", json={
        "email": "filter.user@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/crop/recommend", json={
        "N": 80.0, "P": 40.0, "K": 40.0,
        "temperature": 25.0, "humidity": 70.0,
        "ph": 6.5, "rainfall": 150.0, "top_k": 2
    }, headers=headers)

    client.post("/api/v1/price/forecast", json={
        "commodity": "Wheat",
        "market": "Khanna",
        "historical_prices": [2100.0 + i for i in range(30)],
        "forecast_horizon": 7
    }, headers=headers)

    res_crop = client.get("/api/v1/predictions/history?prediction_type=CROP_RECOMMENDATION", headers=headers)
    assert res_crop.status_code == 200
    crop_data = res_crop.json()["data"]
    assert crop_data["total"] == 1
    assert all(r["prediction_type"] == "CROP_RECOMMENDATION" for r in crop_data["records"])

    res_price = client.get("/api/v1/predictions/history?prediction_type=PRICE_FORECAST", headers=headers)
    assert res_price.status_code == 200
    price_data = res_price.json()["data"]
    assert price_data["total"] == 1
    assert all(r["prediction_type"] == "PRICE_FORECAST" for r in price_data["records"])


def test_20_logout_response(client):
    """20. Test logout endpoint response."""
    client.post("/api/v1/auth/register", json={
        "name": "Logout User",
        "email": "logout.user@example.com",
        "password": "Password123!"
    })
    token = client.post("/api/v1/auth/login", json={
        "email": "logout.user@example.com",
        "password": "Password123!"
    }).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "logged out" in data["message"].lower()
