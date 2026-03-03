"""Conversational car search endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

from app.database import get_db
from app.models import CarListing, SearchLog, ImpressionLog
from app.ai import chat_car_search, parse_prompt_improved, get_embedding

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


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
    """Perform search using filters (copied from search.py)."""
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

    # If there are semantic keywords, also do vector search
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

    result = await db.execute(query)
    cars = result.scalars().all()
    return cars


@router.post("/", response_model=ChatResponse)
async def chat_search(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Conversational car search.
    
    Takes a conversation history and returns either a clarifying question
    or search results with matching cars.
    """
    # Convert messages to list of dicts for AI module
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Call chat AI
    chat_result = await chat_car_search(messages)
    
    if chat_result["type"] == "response":
        # Just return the assistant's response
        return ChatResponse(
            type="response",
            assistant_message=chat_result["content"],
            filters=None,
            results=None,
            count=None
        )
    
    # Otherwise we have filters, perform search
    filters = chat_result["filters"]
    
    # Log the search (using the last user message as prompt)
    last_user_message = next(
        (msg["content"] for msg in reversed(messages) if msg["role"] == "user"),
        ""
    )
    log = SearchLog(
        user_prompt=last_user_message,
        parsed_filters=json.dumps(filters),
        results_count=0  # will update after search
    )
    db.add(log)
    await db.flush()
    
    # Perform search
    cars = await _search_with_filters(filters, db)
    
    # Update log with result count
    log.results_count = len(cars)
    
    # Log impressions
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
    
    # Convert cars to result objects
    results = [CarResult.from_orm(car) for car in cars]
    
    return ChatResponse(
        type="search",
        assistant_message="Here are some cars that match your criteria:",
        filters=filters,
        results=results,
        count=len(results)
    )