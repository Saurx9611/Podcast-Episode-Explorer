def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "ok"]
    assert "version" in data
    assert "database" in data
    assert "timestamp" in data

def test_top_level_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
