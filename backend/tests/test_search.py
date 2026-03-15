import pytest


@pytest.mark.asyncio
async def test_search_endpoint_exists(test_client):
    """Test that the search endpoint exists and returns correct structure."""
    response = await test_client.post("/api/search/", json={"prompt": "test car"})

    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "filters" in data
    assert "results" in data
    assert "count" in data
    assert data["prompt"] == "test car"


@pytest.mark.asyncio
async def test_search_with_mocked_filters(test_client):
    """Test search with mocked filter parsing."""
    from unittest.mock import AsyncMock, patch

    with patch("app.routes.search.parse_prompt", new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = {
            "makes": ["toyota"],
            "models": ["corolla"],
            "min_year": 2015,
            "max_year": 2023,
            "min_price": 5000,
            "max_price": 15000,
            "max_mileage": 50000,
            "fuel_types": ["petrol"],
            "transmissions": ["manual"],
            "body_types": ["hatchback"],
            "min_doors": 4,
            "keywords": ["reliable"],
            "sort_by": "price_asc",
        }

        response = await test_client.post(
            "/api/search/", json={"prompt": "reliable toyota corolla 2015-2023"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["makes"] == ["toyota"]
        assert data["filters"]["min_year"] == 2015
        # Results should be empty since database is empty
        assert data["results"] == []
        assert data["count"] == 0


@pytest.mark.asyncio
async def test_search_error_handling(test_client):
    """Test error handling for invalid requests."""
    # Missing prompt field
    response = await test_client.post("/api/search/", json={})
    assert response.status_code == 422  # Validation error

    # Invalid JSON
    response = await test_client.post(
        "/api/search/",
        content="invalid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422