"""
Advanced search engine for CarPrompt.
Implements hybrid search (vector + keyword + filters) with relevance scoring.
Provides shared filter-building utilities used across all search routes.
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import numpy as np

from app.models import CarListing
from app.ai import parse_prompt, get_embedding


# ============================================================================
# Shared filter builder — used by search.py, chat.py, and search_engine
# ============================================================================

def build_filter_conditions(filters: Dict[str, Any]) -> list:
    """
    Build a list of SQLAlchemy filter conditions from parsed filters.

    Uses explicit `is not None` checks to avoid the walrus-operator bug
    where falsy values like 0 would be silently skipped.
    """
    conditions = []

    makes = filters.get("makes")
    if makes:
        conditions.append(CarListing.make.in_([m.lower() for m in makes]))

    models = filters.get("models")
    if models:
        conditions.append(CarListing.model.in_([m.lower() for m in models]))

    min_year = filters.get("min_year")
    if min_year is not None:
        conditions.append(CarListing.year >= min_year)

    max_year = filters.get("max_year")
    if max_year is not None:
        conditions.append(CarListing.year <= max_year)

    min_price = filters.get("min_price")
    if min_price is not None:
        conditions.append(CarListing.price >= min_price)

    max_price = filters.get("max_price")
    if max_price is not None:
        conditions.append(CarListing.price <= max_price)

    max_mileage = filters.get("max_mileage")
    if max_mileage is not None:
        conditions.append(CarListing.mileage <= max_mileage)

    fuel_types = filters.get("fuel_types")
    if fuel_types:
        conditions.append(CarListing.fuel_type.in_([f.lower() for f in fuel_types]))

    transmissions = filters.get("transmissions")
    if transmissions:
        conditions.append(CarListing.transmission.in_([t.lower() for t in transmissions]))

    body_types = filters.get("body_types")
    if body_types:
        conditions.append(CarListing.body_type.in_([b.lower() for b in body_types]))

    min_doors = filters.get("min_doors")
    if min_doors is not None:
        conditions.append(CarListing.doors >= min_doors)

    return conditions


def apply_sort_order(query, filters: Dict[str, Any]):
    """Apply sort ordering to a query based on parsed filters."""
    sort = filters.get("sort_by", "price_asc")
    if sort == "price_asc":
        query = query.order_by(CarListing.price.asc())
    elif sort == "price_desc":
        query = query.order_by(CarListing.price.desc())
    elif sort == "year_desc":
        query = query.order_by(CarListing.year.desc())
    elif sort == "mileage_asc":
        query = query.order_by(CarListing.mileage.asc())
    return query


def apply_vector_order(query, embedding: List[float]):
    """
    Apply pgvector cosine distance ordering.
    Only works with PostgreSQL + pgvector.
    """
    return query.order_by(CarListing.embedding.cosine_distance(embedding))


# ============================================================================
# Search Engine class — advanced hybrid search
# ============================================================================

class SearchEngine:
    """Advanced search engine with hybrid ranking algorithms."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        prompt: str,
        limit: int = 20,
        use_hybrid: bool = True,
        use_spell_check: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform advanced search with hybrid ranking.

        Args:
            prompt: Natural language search query
            limit: Maximum number of results
            use_hybrid: Use hybrid vector+keyword search
            use_spell_check: Attempt spell correction (basic)

        Returns:
            Dictionary with results, scores, and metadata
        """

        # 1. Parse the prompt with improved understanding
        filters = await parse_prompt(prompt)

        # 2. Expand query with synonyms and related terms
        expanded_keywords = self._expand_keywords(filters.get("keywords", []))

        # 3. Build base query with filters
        conditions = build_filter_conditions(filters)
        query = select(CarListing)
        if conditions:
            query = query.where(and_(*conditions))

        # 4. If hybrid search enabled, get embedding and use pgvector
        vector_scores = {}
        embedding = None
        if use_hybrid and expanded_keywords:
            embedding_text = " ".join(expanded_keywords)
            try:
                embedding = await get_embedding(embedding_text)
            except Exception:
                embedding = None

        # 5. Apply ordering — pgvector if we have an embedding, else default sort
        if embedding is not None:
            try:
                query = apply_vector_order(query, embedding)
            except Exception:
                # Fallback if pgvector not available (e.g. SQLite in tests)
                query = apply_sort_order(query, filters)
        else:
            query = apply_sort_order(query, filters)

        # 6. Execute query
        query = query.limit(limit)
        result = await self.db.execute(query)
        results = result.scalars().all()

        # 7. Score and rank results
        ranked_results = self._score_and_rank(
            results, filters, embedding, prompt
        )

        # 8. Log search for future learning
        await self._log_search(prompt, filters, len(ranked_results))

        return {
            "prompt": prompt,
            "filters": filters,
            "results": ranked_results[:limit],
            "count": len(ranked_results),
            "metadata": {
                "search_type": "hybrid" if use_hybrid else "filter_only",
                "keywords_expanded": expanded_keywords,
                "vector_search_used": embedding is not None,
            },
        }

    def _expand_keywords(self, keywords: List[str]) -> List[str]:
        """Expand keywords with synonyms and related terms."""
        expanded = set(keywords)

        synonym_map = {
            "reliable": ["dependable", "trustworthy", "durable"],
            "fuel efficient": ["economical", "good mpg", "low fuel consumption"],
            "cheap": ["affordable", "inexpensive", "budget"],
            "luxury": ["premium", "high-end", "luxurious"],
            "sporty": ["fast", "performance", "quick"],
            "family": ["practical", "spacious", "roomy"],
            "suv": ["4x4", "crossover", "off-road"],
            "hatchback": ["5-door", "estate" if "large" in keywords else ""],
            "saloon": ["sedan", "4-door"],
            "estate": ["wagon", "station wagon"],
            "convertible": ["cabriolet", "drophead"],
            "manual": ["stick shift", "standard"],
            "automatic": ["auto", "self-shifting"],
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in synonym_map:
                expanded.update(synonym_map[keyword_lower])
            if "economy" in keyword_lower:
                expanded.add("fuel efficient")
            if "mpg" in keyword_lower:
                expanded.add("fuel efficient")
            if "4x4" in keyword_lower:
                expanded.add("suv")
                expanded.add("off-road")

        # Remove empty strings
        expanded.discard("")
        return list(expanded)

    def _score_and_rank(
        self,
        results: List[CarListing],
        filters: Dict[str, Any],
        query_embedding: Optional[List[float]],
        original_prompt: str,
    ) -> List[Dict[str, Any]]:
        """Score and rank results based on multiple factors."""

        scored_results = []

        for listing in results:
            score = 0.0
            scoring_factors = {}

            # 1. Vector similarity score (0-1 scale)
            vector_score = 0.0
            if query_embedding and listing.embedding:
                vector_score = self._cosine_similarity(query_embedding, listing.embedding)
            score += vector_score * 0.4
            scoring_factors["vector_similarity"] = vector_score

            # 2. Price relevance
            price_score = self._calculate_price_score(listing.price, filters)
            score += price_score * 0.2
            scoring_factors["price_relevance"] = price_score

            # 3. Year relevance
            year_score = self._calculate_year_score(listing.year, filters)
            score += year_score * 0.15
            scoring_factors["year_relevance"] = year_score

            # 4. Mileage relevance
            mileage_score = self._calculate_mileage_score(listing.mileage, filters)
            score += mileage_score * 0.15
            scoring_factors["mileage_relevance"] = mileage_score

            # 5. Keyword match
            keyword_score = self._calculate_keyword_score(listing, filters.get("keywords", []))
            score += keyword_score * 0.1
            scoring_factors["keyword_match"] = keyword_score

            score = min(1.0, max(0.0, score))

            result_dict = {
                "id": listing.id,
                "title": listing.title,
                "make": listing.make,
                "model": listing.model,
                "year": listing.year,
                "price": listing.price,
                "mileage": listing.mileage,
                "fuel_type": listing.fuel_type,
                "transmission": listing.transmission,
                "body_type": listing.body_type,
                "location": listing.location,
                "images": listing.images,
                "score": score,
                "scoring_factors": scoring_factors,
                "explanation": self._generate_explanation(scoring_factors),
            }

            scored_results.append((score, result_dict))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for _, result in scored_results]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _calculate_price_score(self, price: float, filters: Dict[str, Any]) -> float:
        """Calculate price relevance score (0-1)."""
        min_price = filters.get("min_price") or 0
        max_price = filters.get("max_price") or 1000000

        if max_price == 1000000:
            max_price = price * 2 if price > 0 else 50000

        ideal_price = (min_price + max_price) / 2
        if ideal_price == 0:
            return 0.5

        price_range = max_price - min_price
        if price_range == 0:
            return 1.0 if price == ideal_price else 0.0

        distance = abs(price - ideal_price) / price_range
        return max(0.0, 1.0 - distance)

    def _calculate_year_score(self, year: int, filters: Dict[str, Any]) -> float:
        """Calculate year relevance score (0-1)."""
        min_year = filters.get("min_year") or 1990
        max_year = filters.get("max_year") or 2026

        if max_year <= min_year:
            return 1.0 if min_year <= year <= max_year else 0.0

        normalized = (year - min_year) / (max_year - min_year)
        return max(0.0, min(1.0, normalized))

    def _calculate_mileage_score(self, mileage: Optional[int], filters: Dict[str, Any]) -> float:
        """Calculate mileage relevance score (0-1, lower mileage is better)."""
        if mileage is None:
            return 0.5

        max_mileage = filters.get("max_mileage") or 200000

        if mileage <= 0:
            return 1.0

        normalized = 1 - (min(mileage, max_mileage) / max_mileage)
        return max(0.0, normalized)

    def _calculate_keyword_score(self, listing: CarListing, keywords: List[str]) -> float:
        """Calculate keyword match score in title/description."""
        if not keywords:
            return 0.0

        text_to_search = f"{listing.title} {listing.description or ''}".lower()

        matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if re.search(rf'\b{re.escape(keyword_lower)}\b', text_to_search):
                matches += 1

        return matches / len(keywords) if keywords else 0.0

    def _generate_explanation(self, scoring_factors: Dict[str, float]) -> str:
        """Generate human-readable explanation of score."""
        explanations = []

        if scoring_factors.get("vector_similarity", 0) > 0.7:
            explanations.append("Highly matches your description")
        elif scoring_factors.get("vector_similarity", 0) > 0.4:
            explanations.append("Matches your description")

        if scoring_factors.get("price_relevance", 0) > 0.8:
            explanations.append("Great price for your budget")

        if scoring_factors.get("year_relevance", 0) > 0.8:
            explanations.append("Right age range")

        if scoring_factors.get("mileage_relevance", 0) > 0.8:
            explanations.append("Low mileage")

        if scoring_factors.get("keyword_match", 0) > 0.5:
            explanations.append("Matches your keywords")

        if not explanations:
            return "Matches your basic criteria"

        return "; ".join(explanations)

    async def _log_search(self, prompt: str, filters: Dict[str, Any], results_count: int):
        """Log search for future learning and improvement."""
        from app.models import SearchLog
        import json

        log = SearchLog(
            user_prompt=prompt,
            parsed_filters=json.dumps(filters),
            results_count=results_count,
        )
        self.db.add(log)
        await self.db.commit()


# Simple spell correction (basic implementation)
def simple_spell_correction(text: str) -> str:
    """Basic spell correction for common car terms."""
    corrections = {
        "toyta": "toyota",
        "fordd": "ford",
        "bmww": "bmw",
        "vw": "volkswagen",
        "vauxhal": "vauxhall",
        "mercedez": "mercedes",
        "nissann": "nissan",
        "mazdaa": "mazda",
        "subaruu": "subaru",
        "hyunda": "hyundai",
        "kiaa": "kia",
        "audii": "audi",
        "lexuss": "lexus",
        "teslla": "tesla",
        "jagaur": "jaguar",
        "landrover": "land rover",
        "volvoo": "volvo",
        "peugot": "peugeot",
        "renaultt": "renault",
        "citreon": "citroen",
        "alfaromeo": "alfa romeo",
    }

    words = text.split()
    corrected_words = []

    for word in words:
        lower_word = word.lower()
        if lower_word in corrections:
            corrected_words.append(corrections[lower_word])
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)