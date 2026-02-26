import pytest
import asyncio
from datetime import datetime


def test_get_listings_empty(test_client):
    """Test GET /api/listings/ returns empty list when no listings."""
    response = test_client.get("/api/listings/")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_create_listing(test_client, db_session):
    """Test POST /api/listings/ creates a new listing."""
    from app.models import CarListing
    from sqlalchemy import select
    
    listing_data = {
        "title": "Toyota Corolla 2020",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "price": 15000.0,
        "mileage": 25000,
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "body_type": "Hatchback",
        "location": "London"
    }
    
    response = test_client.post("/api/listings/", json=listing_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == listing_data["title"]
    assert data["make"] == "toyota"  # Should be lowercased
    assert data["model"] == "corolla"
    assert data["price"] == listing_data["price"]
    assert data["id"] is not None
    
    # Verify in database
    async def check_db():
        result = await db_session.execute(select(CarListing))
        listings = result.scalars().all()
        return listings
    
    listings = asyncio.run(check_db())
    assert len(listings) == 1
    assert listings[0].title == listing_data["title"]


def test_get_listing_by_id(test_client, db_session):
    """Test GET /api/listings/{id} returns a specific listing."""
    from app.models import CarListing
    from sqlalchemy import select
    
    # First create a listing
    listing = CarListing(
        title="Test Car",
        make="honda",
        model="civic",
        year=2018,
        price=12000.0,
        embedding=[0.0] * 1536
    )
    
    async def create_and_get():
        db_session.add(listing)
        await db_session.commit()
        await db_session.refresh(listing)
        return listing.id
    
    listing_id = asyncio.run(create_and_get())
    
    # Now fetch it
    response = test_client.get(f"/api/listings/{listing_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == listing_id
    assert data["title"] == "Test Car"
    assert data["make"] == "honda"


def test_get_listing_not_found(test_client):
    """Test GET /api/listings/{id} returns 404 for non-existent listing."""
    response = test_client.get("/api/listings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"


def test_get_listings_pagination(test_client, db_session):
    """Test GET /api/listings/ with skip and limit parameters."""
    from app.models import CarListing
    import asyncio
    
    # Create multiple listings
    async def create_listings():
        for i in range(5):
            listing = CarListing(
                title=f"Car {i}",
                make="test",
                model="model",
                year=2020 + i,
                price=10000.0 + i * 1000,
                embedding=[0.0] * 1536
            )
            db_session.add(listing)
        await db_session.commit()
    
    asyncio.run(create_listings())
    
    # Test with skip and limit
    response = test_client.get("/api/listings/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Should be sorted by created_at descending, but our test doesn't set created_at
    # So we just check we got 2 items


def test_listing_validation(test_client):
    """Test validation for required fields in listing creation."""
    # Missing required fields
    response = test_client.post("/api/listings/", json={
        "title": "Missing fields"
    })
    assert response.status_code == 422  # Validation error
    
    # Invalid data types
    response = test_client.post("/api/listings/", json={
        "title": "Test",
        "make": "Toyota",
        "model": "Corolla",
        "year": "not a number",  # Should be int
        "price": 10000
    })
    assert response.status_code == 422