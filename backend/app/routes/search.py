"""Search endpoint — the core feature."""

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import CarListing, SearchLog, ImpressionLog
from app.ai import parse_prompt, get_embedding
from app.search_engine import build_filter_conditions, apply_sort_order, apply_vector_order

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class SearchRequest(BaseModel):
    prompt: str = Field(..., max_length=1000)


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


async def _log_search_and_impressions(
    prompt: str,
    filters: dict,
    cars_data: list[dict],
    db: AsyncSession,
):
    """Background task: log search and impressions without blocking the response."""
    log = SearchLog(
        user_prompt=prompt,
        parsed_filters=json.dumps(filters),
        results_count=len(cars_data),
    )
    db.add(log)
    await db.flush()

    for item in cars_data:
        if item.get("garage_id"):
            impression = ImpressionLog(
                garage_id=item["garage_id"],
                listing_id=item["id"],
                search_id=log.id,
                position=item["position"],
            )
            db.add(impression)

    await db.commit()


@router.post("/")
@limiter.limit("30/minute")
async def search_cars(
    search_request: SearchRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Parse a natural language prompt and return matching cars."""

    # 1. Parse prompt and generate embedding concurrently
    filters, embedding = await asyncio.gather(
        parse_prompt(search_request.prompt),
        get_embedding(search_request.prompt),
    )

    # 2. Build the query using shared filter builder
    conditions = build_filter_conditions(filters)
    query = select(CarListing)
    if conditions:
        query = query.where(and_(*conditions))

    # 3. Apply ordering — pgvector if we have a real embedding, else default sort
    keywords = filters.get("keywords", [])
    has_real_embedding = keywords and embedding and any(v != 0.0 for v in embedding[:10])

    if has_real_embedding:
        try:
            query = apply_vector_order(query, embedding)
        except Exception:
            query = apply_sort_order(query, filters)
    else:
        query = apply_sort_order(query, filters)

    query = query.limit(20)

    # 4. Execute
    result = await db.execute(query)
    cars = result.scalars().all()

    # 5. Schedule logging as a background task
    cars_data = [
        {"id": car.id, "garage_id": car.garage_id, "position": pos}
        for pos, car in enumerate(cars, start=1)
    ]
    background_tasks.add_task(
        _log_search_and_impressions,
        search_request.prompt,
        filters,
        cars_data,
        db,
    )

    return {
        "prompt": search_request.prompt,
        "filters": filters,
        "results": [CarResult.from_orm(car) for car in cars],
        "count": len(cars),
    }
