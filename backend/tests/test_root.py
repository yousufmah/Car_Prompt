def test_root_endpoint(test_client):
    """Test the root endpoint returns API info."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Car Prompt API"
    assert data["version"] == "0.1.0"