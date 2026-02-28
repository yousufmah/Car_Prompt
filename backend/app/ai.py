"""AI module — handles prompt parsing and embedding generation."""

import json
import os
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Client will be initialized lazily only when a real API key is present
_client: Optional[AsyncOpenAI] = None

def _get_client() -> Optional[AsyncOpenAI]:
    """Get OpenAI client if API key is valid, otherwise None."""
    global _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "mock":
        return None
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client

PARSE_SYSTEM_PROMPT = """You are a car search assistant. Parse the user's natural language car query into structured filters.

Return a JSON object with these fields (omit any that aren't mentioned or implied):
{
    "makes": ["Toyota", "Honda"],       // car manufacturers
    "models": ["Corolla"],              // specific models
    "min_year": 2015,
    "max_year": 2023,
    "min_price": 0,
    "max_price": 10000,
    "max_mileage": 50000,
    "fuel_types": ["petrol", "diesel", "electric", "hybrid"],
    "transmissions": ["manual", "automatic"],
    "body_types": ["hatchback", "saloon", "suv", "estate", "coupe", "convertible", "van"],
    "min_doors": 4,
    "keywords": ["reliable", "fuel efficient"],  // qualities to match semantically
    "sort_by": "price_asc"  // price_asc, price_desc, mileage_asc, year_desc
}

Be smart about implications:
- "cheap to run" → fuel efficient, low tax bracket
- "family car" → 4+ doors, estate/suv/hatchback, reliable
- "Japanese" → Toyota, Honda, Mazda, Nissan, Subaru, Mitsubishi, Suzuki, Lexus
- "first car" → low insurance group, small engine, cheap

Always return valid JSON only. No explanation."""


async def parse_prompt(user_prompt: str) -> dict:
    """Parse a natural language car search into structured filters."""
    client = _get_client()
    if client is None:
        # Mock mode: return empty filters (still allows filter‑based search)
        print("⚠️  OpenAI API key not set — using mock parser")
        return {}

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for semantic search."""
    client = _get_client()
    if client is None:
        # Mock embedding: return zeros (dimension 1536 for ada‑002)
        print("⚠️  OpenAI API key not set — using mock embedding")
        return [0.0] * 1536

    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response.data[0].embedding
