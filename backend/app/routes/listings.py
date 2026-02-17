"""Listings CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models import CarListing
from app.ai import get_embedding

router = APIRouter()


class ListingCreate(BaseModel):
    title: str
    description: str | None = None
    make: str
    model: str
    variant: str | None = None
    year: int
    price: float
    mileage: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    body_type: str | None = None
    doors: int | None = None
    colour: str | None = None
    engine_size: float | None = None
    location: str | None = None
    postcode: str | None = None
    images: str | None = None
    garage_id: int | None = None


@router.get("/")
async def get_listings(
    skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CarListing).offset(skip).limit(limit).order_by(CarListing.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{listing_id}")
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CarListing).where(CarListing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("/")
async def create_listing(data: ListingCreate, db: AsyncSession = Depends(get_db)):
    # Generate embedding from the listing description for semantic search
    embed_text = f"{data.make} {data.model} {data.year} {data.description or ''} {data.body_type or ''} {data.fuel_type or ''}"
    embedding = await get_embedding(embed_text)

    listing = CarListing(
        **data.model_dump(),
        embedding=embedding,
    )
    # Normalise make/model to lowercase for consistent filtering
    listing.make = listing.make.lower()
    listing.model = listing.model.lower()
    if listing.fuel_type:
        listing.fuel_type = listing.fuel_type.lower()
    if listing.transmission:
        listing.transmission = listing.transmission.lower()
    if listing.body_type:
        listing.body_type = listing.body_type.lower()

    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return listing
