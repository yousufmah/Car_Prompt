from fastapi import APIRouter, HTTPException, Depends, Query
from app.database import get_db
from app.models import CarListing, Garage
from sqlalchemy.orm import Session
import sys
import os
import asyncio
import subprocess

router = APIRouter()

# Simple secret key for seeding (should be changed in production)
SEED_SECRET = os.getenv("SEED_SECRET", "dev-secret-123")

@router.post("/seed")
async def seed_database(
    secret: str = Query(..., description="Secret key to authorize seeding"),
    db: Session = Depends(get_db)
):
    """Seed the database with mock data"""
    if secret != SEED_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    try:
        # Run the async seed function
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from seed import seed as seed_async
        
        # Run async function in event loop
        await seed_async()
        return {"message": "Database seeded successfully", "count": 20}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")

@router.get("/health-check")
async def health_check(db: Session = Depends(get_db)):
    """Check database connection and basic counts"""
    try:
        car_count = db.query(CarListing).count()
        garage_count = db.query(Garage).count()
        return {
            "database": "connected",
            "car_listings": car_count,
            "garages": garage_count
        }
    except Exception as e:
        return {"database": "error", "error": str(e)}