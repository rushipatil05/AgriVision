def test_root_endpoint(client):
    """Verify API root endpoint metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "AgriPulse"
    assert "docs" in data
    assert "health" in data


def test_legacy_health_endpoint(client):
    """Verify legacy /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "AgriPulse"


def test_v1_health_endpoint(client):
    """Verify standard /api/v1/health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "AgriPulse"
    assert "version" in data
