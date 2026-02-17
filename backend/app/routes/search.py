"""Search endpoint — the core feature."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from app.database import get_db
from app.models import CarListing, SearchLog
from app.ai import parse_prompt, get_embedding
import json

router = APIRouter()


class SearchRequest(BaseModel):
    prompt: str


class CarResult(BaseModel):
    id: int
    title: str
    make: str
    model: str
    year: int
    price: float
    mileage: int | None
    fuel_type: str | None
    transmission: str | None
    body_type: str | None
    location: str | None
    images: str | None

    class Config:
        from_attributes = True


@router.post("/")
async def search_cars(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Parse a natural language prompt and return matching cars."""

    # 1. Parse the prompt into filters
    filters = await parse_prompt(request.prompt)

    # 2. Build the query
    conditions = []

    if makes := filters.get("makes"):
        conditions.append(CarListing.make.in_([m.lower() for m in makes]))
    if models := filters.get("models"):
        conditions.append(CarListing.model.in_([m.lower() for m in models]))
    if min_year := filters.get("min_year"):
        conditions.append(CarListing.year >= min_year)
    if max_year := filters.get("max_year"):
        conditions.append(CarListing.year <= max_year)
    if min_price := filters.get("min_price"):
        conditions.append(CarListing.price >= min_price)
    if max_price := filters.get("max_price"):
        conditions.append(CarListing.price <= max_price)
    if max_mileage := filters.get("max_mileage"):
        conditions.append(CarListing.mileage <= max_mileage)
    if fuel_types := filters.get("fuel_types"):
        conditions.append(CarListing.fuel_type.in_([f.lower() for f in fuel_types]))
    if transmissions := filters.get("transmissions"):
        conditions.append(CarListing.transmission.in_([t.lower() for t in transmissions]))
    if body_types := filters.get("body_types"):
        conditions.append(CarListing.body_type.in_([b.lower() for b in body_types]))

    query = select(CarListing)
    if conditions:
        query = query.where(and_(*conditions))

    # 3. If there are semantic keywords, also do vector search
    keywords = filters.get("keywords", [])
    if keywords:
        embedding = await get_embedding(" ".join(keywords))
        # Order by vector similarity (closest first)
        query = query.order_by(CarListing.embedding.cosine_distance(embedding))
    else:
        # Default sort
        sort = filters.get("sort_by", "price_asc")
        if sort == "price_asc":
            query = query.order_by(CarListing.price.asc())
        elif sort == "price_desc":
            query = query.order_by(CarListing.price.desc())
        elif sort == "year_desc":
            query = query.order_by(CarListing.year.desc())
        elif sort == "mileage_asc":
            query = query.order_by(CarListing.mileage.asc())

    query = query.limit(20)

    # 4. Execute
    result = await db.execute(query)
    cars = result.scalars().all()

    # 5. Log the search (this data is valuable)
    log = SearchLog(
        user_prompt=request.prompt,
        parsed_filters=json.dumps(filters),
        results_count=len(cars),
    )
    db.add(log)
    await db.commit()

    return {
        "prompt": request.prompt,
        "filters": filters,
        "results": [CarResult.from_orm(car) for car in cars],
        "count": len(cars),
    }
