"""Advanced search endpoint using improved AI and hybrid ranking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
import json

from app.database import get_db
from app.search_engine import SearchEngine, simple_spell_correction
from app.ai_improved import parse_prompt_improved, expand_query_with_similar_terms

router = APIRouter()


class AdvancedSearchRequest(BaseModel):
    prompt: str
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
async def search_cars_advanced(
    request: AdvancedSearchRequest, 
    db: AsyncSession = Depends(get_db)
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
        processed_prompt = request.prompt
        if request.use_spell_check:
            processed_prompt = simple_spell_correction(processed_prompt)
        
        # Expand query if requested
        expanded_terms = []
        if request.expand_query:
            expanded_terms = await expand_query_with_similar_terms(processed_prompt)
            # Could use expanded terms in search, but for now just log
        
        # Initialize search engine
        engine = SearchEngine(db)
        
        # Perform search
        result = await engine.search(
            prompt=processed_prompt,
            limit=request.limit,
            use_hybrid=request.use_hybrid,
            use_spell_check=request.use_spell_check
        )
        
        # Add metadata about processing
        result["metadata"]["spell_corrected"] = request.use_spell_check and (processed_prompt != request.prompt)
        result["metadata"]["query_expanded"] = bool(expanded_terms)
        result["metadata"]["expanded_terms"] = expanded_terms
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Search failed: {str(e)}"
        )


@router.post("/compare")
async def compare_search_algorithms(
    request: AdvancedSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare different search algorithms on the same query.
    Useful for testing and algorithm evaluation.
    """
    
    results = {}
    
    # Test 1: Basic filter-only search (like original)
    from app.routes.search import search_cars as basic_search
    from app.routes.search import SearchRequest
    
    basic_request = SearchRequest(prompt=request.prompt)
    try:
        basic_result = await basic_search(basic_request, db)
        results["basic"] = {
            "count": basic_result["count"],
            "filters": basic_result["filters"],
            "algorithm": "filter_only"
        }
    except Exception as e:
        results["basic"] = {"error": str(e)}
    
    # Test 2: Advanced hybrid search
    engine = SearchEngine(db)
    try:
        advanced_result = await engine.search(
            prompt=request.prompt,
            limit=request.limit,
            use_hybrid=True
        )
        results["advanced_hybrid"] = {
            "count": advanced_result["count"],
            "filters": advanced_result["filters"],
            "algorithm": "hybrid",
            "avg_score": sum(r["score"] for r in advanced_result["results"]) / max(1, len(advanced_result["results"])) if advanced_result["results"] else 0
        }
    except Exception as e:
        results["advanced_hybrid"] = {"error": str(e)}
    
    # Test 3: Vector-only search (semantic)
    try:
        vector_result = await engine.search(
            prompt=request.prompt,
            limit=request.limit,
            use_hybrid=False
        )
        results["vector_only"] = {
            "count": vector_result["count"],
            "algorithm": "vector_only",
            "avg_score": sum(r["score"] for r in vector_result["results"]) / max(1, len(vector_result["results"])) if vector_result["results"] else 0
        }
    except Exception as e:
        results["vector_only"] = {"error": str(e)}
    
    return {
        "prompt": request.prompt,
        "comparison": results,
        "recommendation": _recommend_algorithm(results)
    }


def _recommend_algorithm(comparison_results: dict) -> dict:
    """Recommend best algorithm based on comparison results."""
    
    basic_count = comparison_results.get("basic", {}).get("count", 0)
    hybrid_count = comparison_results.get("advanced_hybrid", {}).get("count", 0)
    vector_count = comparison_results.get("vector_only", {}).get("count", 0)
    
    # Simple recommendation logic
    if hybrid_count >= basic_count and hybrid_count >= vector_count:
        return {
            "algorithm": "hybrid",
            "reason": "Hybrid search found the most or equally relevant results"
        }
    elif basic_count >= hybrid_count and basic_count >= vector_count:
        return {
            "algorithm": "basic",
            "reason": "Basic filter search performed best for this query"
        }
    else:
        return {
            "algorithm": "vector",
            "reason": "Semantic search performed best for this descriptive query"
        }


@router.get("/test-queries")
async def get_test_queries():
    """
    Get sample test queries for evaluating search algorithms.
    """
    
    return {
        "test_queries": [
            {
                "query": "reliable Japanese family car under £15k",
                "description": "Clear filters with budget constraint"
            },
            {
                "query": "fast sporty convertible for weekend drives",
                "description": "Descriptive with emphasis on experience"
            },
            {
                "query": "cheap to run commuter car with good mpg",
                "description": "Emphasis on running costs"
            },
            {
                "query": "luxury SUV with low mileage",
                "description": "Combination of luxury and condition"
            },
            {
                "query": "first car for new driver, cheap insurance",
                "description": "Specific use case with insurance consideration"
            },
            {
                "query": "electric car with 200+ mile range",
                "description": "Technical specification focus"
            },
            {
                "query": "7 seater for large family, reliable",
                "description": "Capacity requirement with reliability"
            },
            {
                "query": "classic British car for restoration",
                "description": "Niche/vintage focus"
            }
        ],
        "usage": "Use these queries with /compare endpoint to test algorithms"
    }