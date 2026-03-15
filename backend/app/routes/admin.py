from fastapi import APIRouter, HTTPException, Depends, Header
from app.database import get_db
from app.models import CarListing, Garage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import os

router = APIRouter()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


async def verify_admin_key(x_admin_key: str = Header(..., description="Admin API key")):
    """Verify admin API key from request header."""
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are not configured. Set ADMIN_API_KEY env var.",
        )
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")


@router.post("/seed")
async def seed_database(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin_key),
):
    """Seed the database with mock data."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from seed import seed as seed_async

        await seed_async()
        return {"message": "Database seeded successfully", "count": 20}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Seeding failed")


@router.get("/health-check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check database connection and basic counts."""
    try:
        car_result = await db.execute(select(func.count(CarListing.id)))
        car_count = car_result.scalar() or 0
        garage_result = await db.execute(select(func.count(Garage.id)))
        garage_count = garage_result.scalar() or 0
        return {
            "database": "connected",
            "car_listings": car_count,
            "garages": garage_count,
        }
    except Exception:
        return {"database": "error", "error": "Connection failed"}