"""Conversational car search endpoint."""

import json
from typing import List, Dict, Any, Optional, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import CarListing, SearchLog, ImpressionLog
from app.ai import chat_car_search, get_embedding
from app.search_engine import build_filter_conditions, apply_sort_order, apply_vector_order

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None


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


class ChatResponse(BaseModel):
    type: str  # "response" or "search"
    assistant_message: str
    filters: Optional[Dict[str, Any]] = None
    results: Optional[List[CarResult]] = None
    count: Optional[int] = None


async def _search_with_filters(filters: Dict[str, Any], db: AsyncSession):
    """Perform search using shared filter builder."""
    conditions = build_filter_conditions(filters)

    query = select(CarListing)
    if conditions:
        query = query.where(and_(*conditions))

    # If there are semantic keywords, also do vector search
    keywords = filters.get("keywords", [])
    if keywords:
        try:
            embedding = await get_embedding(" ".join(keywords))
            has_real_embedding = any(v != 0.0 for v in embedding[:10])
            if has_real_embedding:
                query = apply_vector_order(query, embedding)
            else:
                query = apply_sort_order(query, filters)
        except Exception:
            query = apply_sort_order(query, filters)
    else:
        query = apply_sort_order(query, filters)

    query = query.limit(20)

    result = await db.execute(query)
    cars = result.scalars().all()
    return cars


async def _log_chat_search(
    prompt: str,
    filters: dict,
    cars_data: list[dict],
    db: AsyncSession,
):
    """Background task: log chat search and impressions."""
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


@router.post("/", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat_search(
    chat_request: ChatRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Conversational car search.

    Takes a conversation history and returns either a clarifying question
    or search results with matching cars.
    """
    # Convert messages to list of dicts for AI module
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

    # Call chat AI
    chat_result = await chat_car_search(messages)

    if chat_result["type"] == "response":
        return ChatResponse(
            type="response",
            assistant_message=chat_result["content"],
            filters=None,
            results=None,
            count=None,
        )

    # Otherwise we have filters, perform search
    filters = chat_result["filters"]

    # Get last user message for logging
    last_user_message = next(
        (msg["content"] for msg in reversed(messages) if msg["role"] == "user"),
        "",
    )

    # Perform search
    cars = await _search_with_filters(filters, db)

    # Convert cars to result objects
    results = [CarResult.from_orm(car) for car in cars]

    # Schedule logging as a background task
    cars_data = [
        {"id": car.id, "garage_id": car.garage_id, "position": pos}
        for pos, car in enumerate(cars, start=1)
    ]
    background_tasks.add_task(
        _log_chat_search,
        last_user_message,
        filters,
        cars_data,
        db,
    )

    return ChatResponse(
        type="search",
        assistant_message="Here are some cars that match your criteria:",
        filters=filters,
        results=results,
        count=len(results),
    )