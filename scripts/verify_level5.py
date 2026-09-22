import time
import sys
from pathlib import Path

# Add paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config.database import Base, get_db
from app.main import app

# Create in-memory SQLite for verification test run
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def run_verification():
    print("=" * 70)
    print("LEVEL 5 -- AUTHENTICATION & PREDICTION HISTORY VERIFICATION & BENCHMARKS")
    print("=" * 70)

    client = TestClient(app)

    # 1. Measure Registration Performance
    t0 = time.time()
    reg1_res = client.post("/api/v1/auth/register", json={
        "name": "Kisan Farmer Alpha",
        "email": "kisan.alpha@agripulse.io",
        "password": "SecurePassword123!"
    })
    reg1_time_ms = (time.time() - t0) * 1000.0
    assert reg1_res.status_code == 201, f"Registration failed: {reg1_res.text}"
    user1 = reg1_res.json()["data"]
    print(f"[OK] Step 1: Registered User 1 (id={user1['id']}, email={user1['email']}) in {reg1_time_ms:.2f}ms")

    # 2. Measure Login Performance
    t0 = time.time()
    login1_res = client.post("/api/v1/auth/login", json={
        "email": "kisan.alpha@agripulse.io",
        "password": "SecurePassword123!"
    })
    login1_time_ms = (time.time() - t0) * 1000.0
    assert login1_res.status_code == 200, f"Login failed: {login1_res.text}"
    token1 = login1_res.json()["data"]["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    print(f"[OK] Step 2: Logged in User 1 & Issued JWT in {login1_time_ms:.2f}ms")

    # 3. Call /auth/me (Authenticated Profile)
    t0 = time.time()
    me1_res = client.get("/api/v1/auth/me", headers=headers1)
    me1_time_ms = (time.time() - t0) * 1000.0
    assert me1_res.status_code == 200, f"Get /auth/me failed: {me1_res.text}"
    print(f"[OK] Step 3: Verified /auth/me profile for User 1 in {me1_time_ms:.2f}ms")

    # 4. Create Predictions as User 1
    t0 = time.time()
    crop1_res = client.post("/api/v1/crop/recommend", json={
        "N": 90.0, "P": 42.0, "K": 43.0,
        "temperature": 20.87, "humidity": 82.00,
        "ph": 6.50, "rainfall": 202.93, "top_k": 3
    }, headers=headers1)
    crop1_time_ms = (time.time() - t0) * 1000.0
    assert crop1_res.status_code == 200
    rec_crop = crop1_res.json()["data"]["recommended_crop"]
    print(f"[OK] Step 4: User 1 executed Crop Recommendation -> {rec_crop} in {crop1_time_ms:.2f}ms")

    # 5. Check User 1 History
    t0 = time.time()
    hist1_res = client.get("/api/v1/predictions/history", headers=headers1)
    hist1_time_ms = (time.time() - t0) * 1000.0
    assert hist1_res.status_code == 200
    hist1_data = hist1_res.json()["data"]
    assert hist1_data["total"] == 1
    pred1_id = hist1_data["records"][0]["id"]
    print(f"[OK] Step 5: User 1 Prediction History retrieved ({hist1_data['total']} records) in {hist1_time_ms:.2f}ms")

    # 6. Register Second User
    reg2_res = client.post("/api/v1/auth/register", json={
        "name": "Kisan Farmer Beta",
        "email": "kisan.beta@agripulse.io",
        "password": "SecurePassword456!"
    })
    assert reg2_res.status_code == 201
    user2 = reg2_res.json()["data"]
    print(f"[OK] Step 6: Registered User 2 (id={user2['id']}, email={user2['email']})")

    # 7. Login as Second User
    login2_res = client.post("/api/v1/auth/login", json={
        "email": "kisan.beta@agripulse.io",
        "password": "SecurePassword456!"
    })
    assert login2_res.status_code == 200
    token2 = login2_res.json()["data"]["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    print(f"[OK] Step 7: Logged in User 2")

    # 8. Verify User 2 CANNOT see User 1's History
    hist2_res = client.get("/api/v1/predictions/history", headers=headers2)
    assert hist2_res.status_code == 200
    hist2_data = hist2_res.json()["data"]
    assert hist2_data["total"] == 0, "Security Failure: User 2 saw records!"
    assert len(hist2_data["records"]) == 0
    print(f"[OK] Step 8: User Data Isolation Verified: User 2 history is strictly empty (total=0)")

    # 9. Verify User 2 CANNOT delete User 1's prediction
    del_attempt = client.delete(f"/api/v1/predictions/history/{pred1_id}", headers=headers2)
    assert del_attempt.status_code == 404, "Security Failure: Unauthorized deletion allowed!"
    print(f"[OK] Step 9: Unauthorized deletion blocked with HTTP 404 (zero existence leakage)")

    # 10. User 1 deletes their own prediction
    del_res = client.delete(f"/api/v1/predictions/history/{pred1_id}", headers=headers1)
    assert del_res.status_code == 200
    print(f"[OK] Step 10: User 1 successfully deleted their own prediction record")

    # 11. User 1 logs out
    logout_res = client.post("/api/v1/auth/logout", headers=headers1)
    assert logout_res.status_code == 200
    print(f"[OK] Step 11: User 1 logged out successfully: {logout_res.json()['message']}")

    print("\n" + "=" * 70)
    print("BENCHMARK & PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"  * User Registration Response Time:    {reg1_time_ms:.2f} ms (includes bcrypt salt & 12 rounds hashing)")
    print(f"  * User Authentication / Login Time:   {login1_time_ms:.2f} ms (includes bcrypt check & JWT signing)")
    print(f"  * Authenticated /auth/me Profile:     {me1_time_ms:.2f} ms")
    print(f"  * Prediction History Query Time:      {hist1_time_ms:.2f} ms")
    print("=" * 70)
    print("ALL LEVEL 5 VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_verification()
