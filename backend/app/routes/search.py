"""Search endpoint — the core feature."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from app.database import get_db
from app.models import CarListing, SearchLog, ImpressionLog
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
    import numpy as np
    
    # 1. Parse the prompt into filters
    filters = await parse_prompt(request.prompt)

    # Determine if we need vector sorting
    needs_vector_sorting = False
    embedding = None
    keywords = filters.get("keywords", [])
    if keywords:
        # Generate embedding from the prompt (or from keywords)
        try:
            embedding = await get_embedding(request.prompt)
            needs_vector_sorting = True
        except Exception as e:
            print(f"Failed to generate embedding: {e}")
            embedding = None

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

    # Select CarListing entity for vector search
    query = select(CarListing)
    if conditions:
        query = query.where(and_(*conditions))

    # 3. Vector search disabled (pgvector extension unavailable)
    keywords = filters.get("keywords", [])
    # Keywords are ignored for vector sorting; they are already used in parsing
    
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

    limit = 20
    # Vector sorting enabled when we have embedding
    if needs_vector_sorting and embedding is not None:
        query = query.limit(limit * 3)  # fetch more for ranking
    else:
        query = query.limit(limit)

    # 4. Execute
    result = await db.execute(query)
    cars = result.scalars().all()

    # 5. If we need vector sorting, compute similarity and sort
    if needs_vector_sorting and embedding is not None:
        # Compute cosine similarity for each car
        car_similarities = []
        for car in cars:
            if car.embedding:
                # Ensure both are numpy arrays
                vec1 = np.array(embedding)
                vec2 = np.array(car.embedding)
                if vec1.shape == vec2.shape:
                    dot = np.dot(vec1, vec2)
                    norm1 = np.linalg.norm(vec1)
                    norm2 = np.linalg.norm(vec2)
                    if norm1 > 0 and norm2 > 0:
                        similarity = dot / (norm1 * norm2)
                    else:
                        similarity = 0.0
                else:
                    similarity = 0.0
            else:
                similarity = 0.0
            car_similarities.append((similarity, car))
        # Sort by similarity descending (higher similarity first)
        car_similarities.sort(key=lambda x: x[0], reverse=True)
        cars = [car for _, car in car_similarities[:limit]]
    else:
        # Already sorted by SQL
        pass

    # 6. Log the search (this data is valuable)
    log = SearchLog(
        user_prompt=request.prompt,
        parsed_filters=json.dumps(filters),
        results_count=len(cars),
    )
    db.add(log)
    # Flush to get the log ID for impression logging
    await db.flush()

    # 7. Log impressions for each car in results
    for position, car in enumerate(cars, start=1):
        if car.garage_id:
            impression = ImpressionLog(
                garage_id=car.garage_id,
                listing_id=car.id,
                search_id=log.id,
                position=position,
            )
            db.add(impression)

    await db.commit()

    return {
        "prompt": request.prompt,
        "filters": filters,
        "results": [CarResult.from_orm(car) for car in cars],
        "count": len(cars),
    }
