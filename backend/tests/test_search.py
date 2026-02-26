import pytest
from unittest.mock import AsyncMock


def test_search_endpoint_exists(test_client):
    """Test that the search endpoint exists and returns correct structure."""
    response = test_client.post("/api/search/", json={"prompt": "test car"})
    
    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "filters" in data
    assert "results" in data
    assert "count" in data
    assert data["prompt"] == "test car"


def test_search_with_mocked_filters(test_client):
    """Test search with mocked filter parsing."""
    # We need to mock parse_prompt with specific filters
    from app.routes import search
    original_parse = search.parse_prompt
    
    try:
        search.parse_prompt = AsyncMock(return_value={
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
            "sort_by": "price_asc"
        })
        
        response = test_client.post("/api/search/", json={"prompt": "reliable toyota corolla 2015-2023"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["makes"] == ["toyota"]
        assert data["filters"]["min_year"] == 2015
        # Results should be empty since database is empty
        assert data["results"] == []
        assert data["count"] == 0
    finally:
        search.parse_prompt = original_parse


def test_search_logs_created(test_client, db_session):
    """Test that search logs are created in the database."""
    from app.models import SearchLog
    import asyncio
    
    response = test_client.post("/api/search/", json={"prompt": "test search log"})
    assert response.status_code == 200
    
    # Check if log was created
    async def check_log():
        from sqlalchemy import select
        result = await db_session.execute(select(SearchLog))
        logs = result.scalars().all()
        return logs
    
    logs = asyncio.run(check_log())
    assert len(logs) == 1
    assert logs[0].user_prompt == "test search log"
    assert logs[0].results_count == 0


def test_search_error_handling(test_client):
    """Test error handling for invalid requests."""
    # Missing prompt field
    response = test_client.post("/api/search/", json={})
    assert response.status_code == 422  # Validation error
    
    # Invalid JSON
    response = test_client.post("/api/search/", data="invalid json")
    assert response.status_code == 422