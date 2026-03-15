"""Advanced search endpoint using improved AI and hybrid ranking."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import CarListing
from app.search_engine import SearchEngine, simple_spell_correction
from app.ai import expand_query_with_similar_terms

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class AdvancedSearchRequest(BaseModel):
    prompt: str = Field(..., max_length=1000)
    limit: int = Field(default=20, ge=1, le=100)
    use_hybrid: bool = True
    use_spell_check: bool = False
    expand_query: bool = False


class CarResultWithScore(BaseModel):
    id: int
    title: str
    make: str
    model: str
    year: int
    price: float
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    body_type: Optional[str] = None
    location: Optional[str] = None
    images: Optional[str] = None
    score: float = Field(..., ge=0, le=1)
    scoring_factors: dict
    explanation: str

    class Config:
        from_attributes = True


@router.post("/advanced")
@limiter.limit("30/minute")
async def search_cars_advanced(
    search_request: AdvancedSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Advanced car search with improved AI understanding and hybrid ranking.

    Features:
    - Better prompt parsing with contextual understanding
    - Hybrid search (vector + keyword + filters)
    - Relevance scoring with multiple factors
    - Query expansion and spell correction
    - Detailed scoring explanations
    """

    try:
        # Apply spell correction if requested
        processed_prompt = search_request.prompt
        if search_request.use_spell_check:
            processed_prompt = simple_spell_correction(processed_prompt)

        # Expand query if requested
        expanded_terms = []
        if search_request.expand_query:
            expanded_terms = await expand_query_with_similar_terms(processed_prompt)

        # Initialize search engine
        engine = SearchEngine(db)

        # Perform search
        result = await engine.search(
            prompt=processed_prompt,
            limit=search_request.limit,
            use_hybrid=search_request.use_hybrid,
            use_spell_check=search_request.use_spell_check,
        )

        # Add metadata about processing
        result["metadata"]["spell_corrected"] = search_request.use_spell_check and (
            processed_prompt != search_request.prompt
        )
        result["metadata"]["query_expanded"] = bool(expanded_terms)
        result["metadata"]["expanded_terms"] = expanded_terms

        return result

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Search failed. Please try again.",
        )


@router.post("/compare")
@limiter.limit("10/minute")
async def compare_search_algorithms(
    search_request: AdvancedSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Compare different search algorithms on the same query.
    Useful for testing and algorithm evaluation.
    """

    results = {}

    # Test 1: Basic filter-only search
    from app.ai import parse_prompt
    from app.search_engine import build_filter_conditions, apply_sort_order

    try:
        basic_filters = await parse_prompt(search_request.prompt)
        conditions = build_filter_conditions(basic_filters)
        basic_query = select(CarListing)
        if conditions:
            basic_query = basic_query.where(and_(*conditions))
        basic_query = apply_sort_order(basic_query, basic_filters).limit(search_request.limit)
        basic_result = await db.execute(basic_query)
        basic_cars = basic_result.scalars().all()
        results["basic"] = {
            "count": len(basic_cars),
            "filters": basic_filters,
            "algorithm": "filter_only",
        }
    except Exception:
        results["basic"] = {"error": "Basic search failed"}

    # Test 2: Advanced hybrid search
    engine = SearchEngine(db)
    try:
        advanced_result = await engine.search(
            prompt=search_request.prompt,
            limit=search_request.limit,
            use_hybrid=True,
        )
        results["advanced_hybrid"] = {
            "count": advanced_result["count"],
            "filters": advanced_result["filters"],
            "algorithm": "hybrid",
            "avg_score": (
                sum(r["score"] for r in advanced_result["results"])
                / max(1, len(advanced_result["results"]))
                if advanced_result["results"]
                else 0
            ),
        }
    except Exception:
        results["advanced_hybrid"] = {"error": "Advanced search failed"}

    # Test 3: Vector-only search (semantic)
    try:
        vector_result = await engine.search(
            prompt=search_request.prompt,
            limit=search_request.limit,
            use_hybrid=False,
        )
        results["vector_only"] = {
            "count": vector_result["count"],
            "algorithm": "vector_only",
            "avg_score": (
                sum(r["score"] for r in vector_result["results"])
                / max(1, len(vector_result["results"]))
                if vector_result["results"]
                else 0
            ),
        }
    except Exception:
        results["vector_only"] = {"error": "Vector search failed"}

    return {
        "prompt": search_request.prompt,
        "comparison": results,
        "recommendation": _recommend_algorithm(results),
    }


def _recommend_algorithm(comparison_results: dict) -> dict:
    """Recommend best algorithm based on comparison results."""

    basic_count = comparison_results.get("basic", {}).get("count", 0)
    hybrid_count = comparison_results.get("advanced_hybrid", {}).get("count", 0)
    vector_count = comparison_results.get("vector_only", {}).get("count", 0)

    if hybrid_count >= basic_count and hybrid_count >= vector_count:
        return {
            "algorithm": "hybrid",
            "reason": "Hybrid search found the most or equally relevant results",
        }
    elif basic_count >= hybrid_count and basic_count >= vector_count:
        return {
            "algorithm": "basic",
            "reason": "Basic filter search performed best for this query",
        }
    else:
        return {
            "algorithm": "vector",
            "reason": "Semantic search performed best for this descriptive query",
        }


@router.get("/test-queries")
async def get_test_queries():
    """Get sample test queries for evaluating search algorithms."""

    return {
        "test_queries": [
            {
                "query": "reliable Japanese family car under £15k",
                "description": "Clear filters with budget constraint",
            },
            {
                "query": "fast sporty convertible for weekend drives",
                "description": "Descriptive with emphasis on experience",
            },
            {
                "query": "cheap to run commuter car with good mpg",
                "description": "Emphasis on running costs",
            },
            {
                "query": "luxury SUV with low mileage",
                "description": "Combination of luxury and condition",
            },
            {
                "query": "first car for new driver, cheap insurance",
                "description": "Specific use case with insurance consideration",
            },
            {
                "query": "electric car with 200+ mile range",
                "description": "Technical specification focus",
            },
            {
                "query": "7 seater for large family, reliable",
                "description": "Capacity requirement with reliability",
            },
            {
                "query": "classic British car for restoration",
                "description": "Niche/vintage focus",
            },
        ],
        "usage": "Use these queries with /compare endpoint to test algorithms",
    }