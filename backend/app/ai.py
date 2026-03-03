"""AI module for CarPrompt — handles prompt parsing, embeddings, and conversational car search."""

import json
import os
import re
from typing import Dict, Any, List, Optional, Union, Literal
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

# ============================================================================
# Legacy parsing functions (for backward compatibility)
# ============================================================================

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

# ============================================================================
# Improved parsing (from ai_improved.py)
# ============================================================================

IMPROVED_PARSE_SYSTEM_PROMPT = """You are an expert car search assistant with deep knowledge of automotive markets, 
consumer preferences, and practical car-buying considerations.

Parse the user's natural language car query into structured filters with nuanced understanding.

Return a JSON object with these fields (omit any that aren't mentioned or implied):

{
    "makes": ["Toyota", "Honda"],                    // car manufacturers (expanded based on region/nationality)
    "models": ["Corolla", "Civic"],                  // specific models
    "min_year": 2015,                                // minimum year (inferred from "new", "recent", etc.)
    "max_year": 2023,                                // maximum year
    "min_price": 0,                                  // minimum price
    "max_price": 10000,                              // maximum price (inferred from "budget", "cheap", "luxury")
    "max_mileage": 50000,                            // maximum mileage
    "fuel_types": ["petrol", "diesel", "electric", "hybrid", "plug-in hybrid"],
    "transmissions": ["manual", "automatic", "semi-automatic", "CVT"],
    "body_types": ["hatchback", "saloon", "suv", "estate", "coupe", "convertible", "van", "pickup", "mpv"],
    "min_doors": 4,                                  // inferred from "family", "practical"
    "keywords": ["reliable", "fuel efficient"],      // qualities for semantic search
    "sort_by": "relevance",                          // relevance, price_asc, price_desc, mileage_asc, year_desc, value
    "priority_factors": ["reliability", "economy"],  // what matters most to user
    "use_case": ["daily commute", "family", "weekend"] // inferred use case
}

BE SMART ABOUT INFERENCES AND IMPLICATIONS:

PRICE & BUDGET:
- "cheap" → max_price: 8000 (UK used car market)
- "budget" → max_price: 5000-10000 depending on other cues
- "affordable" → max_price: 12000
- "mid-range" → min_price: 10000, max_price: 25000
- "luxury" → min_price: 30000, max_price: unlimited
- "good value" → sort_by: "value" (balance of price vs features)
- "under £10k" → max_price: 10000

YEAR & AGE:
- "new" → min_year: current_year - 3
- "recent" → min_year: current_year - 5
- "older" → max_year: current_year - 10
- "classic" → max_year: 2000 (adjust based on context)
- "modern" → min_year: 2015

MILEAGE:
- "low mileage" → max_mileage: 30000
- "high mileage okay" → max_mileage: 100000
- "average miles" → max_mileage: 60000

FUEL & RUNNING COSTS:
- "cheap to run" → fuel_types: ["petrol", "diesel", "hybrid"] (most economical)
- "fuel efficient" → keywords: ["fuel efficient", "economical"]
- "good mpg" → keywords: ["fuel efficient"]
- "low tax" → engine_size <= 1.6 (UK road tax bands)
- "ULEZ compliant" → year >= 2015 (for diesel), 2006 (for petrol) in London
- "electric only" → fuel_types: ["electric"]

NATIONALITIES & BRANDS:
- "Japanese" → makes: ["Toyota", "Honda", "Mazda", "Nissan", "Subaru", "Mitsubishi", "Suzuki", "Lexus"]
- "German" → makes: ["BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Porsche"]
- "British" → makes: ["Mini", "Land Rover", "Jaguar", "Vauxhall", "Bentley", "Rolls-Royce"]
- "American" → makes: ["Ford", "Chevrolet", "Tesla", "Jeep", "Cadillac"]
- "Korean" → makes: ["Hyundai", "Kia"]
- "French" → makes: ["Peugeot", "Renault", "Citroën"]
- "Italian" → makes: ["Fiat", "Alfa Romeo", "Ferrari", "Lamborghini", "Maserati"]
- "Swedish" → makes: ["Volvo", "Saab"]

USE CASES:
- "first car" → max_price: 5000, max_mileage: 60000, engine_size <= 1.4, keywords: ["reliable", "cheap insurance"]
- "family car" → min_doors: 4, body_types: ["suv", "estate", "mpv"], keywords: ["spacious", "safe", "practical"]
- "commuter" → fuel_types: ["diesel", "hybrid", "electric"], keywords: ["fuel efficient", "comfortable"]
- "weekend car" → body_types: ["convertible", "coupe"], keywords: ["fun", "sporty"]
- "work van" → body_types: ["van"], makes: ["Ford", "Mercedes-Benz", "Volkswagen"]
- "off-road" → body_types: ["suv"], keywords: ["4x4", "off-road"], makes: ["Land Rover", "Jeep", "Toyota"]

PERFORMANCE & STYLE:
- "sporty" → keywords: ["sporty", "fast", "performance"], transmissions: ["manual", "automatic"]
- "fast" → min_engine_size: 2.0, keywords: ["performance"]
- "comfortable" → keywords: ["comfortable", "quiet", "smooth"]
- "reliable" → makes: ["Toyota", "Honda", "Lexus", "Subaru"], keywords: ["reliable"]
- "premium" → makes: ["BMW", "Mercedes-Benz", "Aud\"i\", "Lexus\", \"Volvo\"]
- "practical" → body_types: ["hatchback", "estate", "suv"], keywords: ["practical", "spacious"]

GEOGRAPHIC CONTEXT (UK-SPECIFIC):
- Assume UK market unless specified
- Prices in GBP (£)
- Fuel types common in UK: petrol, diesel, hybrid, electric
- Popular UK brands: Ford, Vauxhall, Volkswagen, BMW, Mercedes, Audi

SORTING PREFERENCES:
- "best value" → sort_by: "value"
- "cheapest" → sort_by: "price_asc"
- "newest" → sort_by: "year_desc"
- "lowest mileage" → sort_by: "mileage_asc"
- "most relevant" → sort_by: "relevance"

Always return valid JSON only. No explanation. Use current year 2026 as reference."""


async def parse_prompt_improved(user_prompt: str) -> Dict[str, Any]:
    """Parse natural language car search with improved understanding."""
    client = _get_client()
    if client is None:
        print("⚠️  OpenAI API key not set — using basic parser")
        return await parse_prompt_basic(user_prompt)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Consider gpt-4o for better understanding
            messages=[
                {"role": "system", "content": IMPROVED_PARSE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Post-process to ensure consistency
        result = _post_process_filters(result)
        
        return result
        
    except Exception as e:
        # Fallback to basic parsing
        print(f"Improved parsing failed: {e}, falling back")
        return await parse_prompt_basic(user_prompt)


async def parse_prompt_basic(user_prompt: str) -> Dict[str, Any]:
    """Basic fallback parser."""
    # This would be the original parse_prompt function
    # For now, return a simple structure
    return {
        "makes": [],
        "models": [],
        "min_year": None,
        "max_year": None,
        "min_price": None,
        "max_price": None,
        "max_mileage": None,
        "fuel_types": [],
        "transmissions": [],
        "body_types": [],
        "min_doors": None,
        "keywords": _extract_keywords_basic(user_prompt),
        "sort_by": "relevance",
        "priority_factors": [],
        "use_case": []
    }


def _extract_keywords_basic(text: str) -> List[str]:
    """Basic keyword extraction as fallback."""
    # Common car-related keywords
    car_keywords = [
        "reliable", "fuel efficient", "economical", "cheap", "affordable",
        "luxury", "premium", "sporty", "fast", "comfortable", "spacious",
        "practical", "family", "first car", "commuter", "weekend", "fun",
        "low mileage", "good condition", "full service history", "one owner",
        "automatic", "manual", "petrol", "diesel", "electric", "hybrid",
        "suv", "hatchback", "saloon", "estate", "convertible", "coupe",
        "japanese", "german", "british", "american", "korean", "french",
        "new", "used", "recent", "old", "classic", "modern"
    ]
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in car_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def _post_process_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process filters to ensure consistency and add defaults."""
    
    # Ensure lists are lists
    list_fields = ["makes", "models", "fuel_types", "transmissions", "body_types", "keywords", "priority_factors", "use_case"]
    for field in list_fields:
        if field not in filters or not isinstance(filters.get(field), list):
            filters[field] = []
    
    # Normalize strings to lowercase for database matching
    for field in ["makes", "models", "fuel_types", "transmissions", "body_types"]:
        filters[field] = [item.lower() for item in filters[field] if item]
    
    # Set reasonable defaults for numerical fields if not provided
    current_year = 2026
    
    if not filters.get("min_year"):
        filters["min_year"] = 1990  # Reasonable minimum
    
    if not filters.get("max_year"):
        filters["max_year"] = current_year
    
    if not filters.get("min_price"):
        filters["min_price"] = 0
    
    if not filters.get("max_price"):
        # Default to a reasonable maximum based on UK market
        filters["max_price"] = 50000
    
    if not filters.get("max_mileage"):
        filters["max_mileage"] = 150000  # Reasonable maximum
    
    # Ensure sort_by has a valid value
    valid_sort_options = ["relevance", "price_asc", "price_desc", "mileage_asc", "year_desc", "value"]
    if filters.get("sort_by") not in valid_sort_options:
        filters["sort_by"] = "relevance"
    
    return filters


async def get_contextual_embedding(text: str, context: str = "car_search") -> List[float]:
    """Generate embedding with context awareness."""
    client = _get_client()
    if client is None:
        # Mock embedding: return zeros (dimension 1536 for ada‑002)
        print("⚠️  OpenAI API key not set — using mock embedding")
        return [0.0] * 1536
    
    # For car search, we might want to prepend context
    if context == "car_search":
        text = f"car vehicle automobile search: {text}"
    elif context == "car_description":
        text = f"car listing description: {text}"
    
    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response.data[0].embedding


async def expand_query_with_similar_terms(query: str) -> List[str]:
    """Use LLM to expand query with similar/relevant terms."""
    client = _get_client()
    if client is None:
        print("⚠️  OpenAI API key not set — skipping query expansion")
        return [query]
    
    try:
        expansion_prompt = f"""
        Given the car search query: "{query}"
        
        Generate a list of 5-10 similar or related search terms that might help find relevant cars.
        Include synonyms, related concepts, and alternative phrasings.
        
        Return as a JSON array of strings.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a car search query expansion assistant."},
                {"role": "user", "content": expansion_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, dict) and "terms" in result:
            return result["terms"]
        elif isinstance(result, list):
            return result
        else:
            return [query]
            
    except Exception as e:
        print(f"Query expansion failed: {e}")
        return [query]

# ============================================================================
# Conversational Car Search AI
# ============================================================================

CHAT_SYSTEM_PROMPT = """You are a helpful car search assistant. You engage in natural conversation to help users find their ideal car.

When a user describes what they're looking for, you should ask clarifying questions to gather missing information before performing a search. Important information to collect includes:

1. Budget (price range)
2. Make/model preferences (any specific brands?)
3. Urgency (how soon they need the car)
4. Vehicle type (SUV, saloon, hatchback, estate, etc.)
5. Fuel type (petrol, diesel, electric, hybrid)
6. Transmission (manual/automatic)
7. Year and mileage preferences
8. Number of doors/seats needed
9. Primary use case (family, commute, weekend, etc.)

Ask questions in a friendly, conversational manner. You can ask 1-3 related questions at a time, but don't overwhelm the user.

Once you have enough information to perform a meaningful search, output a JSON object with the structured filters below. Do not include any other text when outputting JSON.

**Output format**:
- If you need more info: output plain text (your response as the assistant).
- If you have enough info: output a JSON object with the following structure:

{
    "makes": [],
    "models": [],
    "min_year": null,
    "max_year": null,
    "min_price": null,
    "max_price": null,
    "max_mileage": null,
    "fuel_types": [],
    "transmissions": [],
    "body_types": [],
    "min_doors": null,
    "keywords": [],
    "sort_by": "relevance",
    "priority_factors": [],
    "use_case": []
}

Fill in the fields based on the conversation. Use null for unspecified numeric fields, empty arrays for unspecified lists.

Assume UK market unless indicated otherwise. Be concise and personable."""


async def chat_car_search(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Handle conversational car search.
    
    Args:
        messages: List of dicts with keys "role" (user/assistant) and "content".
                  The last message is the most recent user input.
    
    Returns:
        Dict with keys:
        - "type": "response" or "search"
        - "content": assistant response text (if type="response")
        - "filters": structured filters dict (if type="search")
    """
    client = _get_client()
    if client is None:
        # Mock mode: simulate a simple chat that asks one question then returns dummy filters
        print("⚠️  OpenAI API key not set — using mock chat")
        if len(messages) == 1:
            # First user message, ask about budget
            return {
                "type": "response",
                "content": "Sure, I can help you find a great car! Could you tell me your budget range?"
            }
        else:
            # Second message, return dummy filters
            return {
                "type": "search",
                "filters": {
                    "makes": [],
                    "models": [],
                    "min_year": None,
                    "max_year": None,
                    "min_price": None,
                    "max_price": 15000,
                    "max_mileage": None,
                    "fuel_types": [],
                    "transmissions": [],
                    "body_types": [],
                    "min_doors": None,
                    "keywords": [],
                    "sort_by": "relevance",
                    "priority_factors": [],
                    "use_case": []
                }
            }
    
    # Prepare conversation for LLM
    conversation = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}] + messages
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.3,
        )
        assistant_message = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            filters = json.loads(assistant_message)
            # Validate that it's a dict (might be the filter structure)
            if isinstance(filters, dict):
                # Post-process filters
                filters = _post_process_filters(filters)
                return {"type": "search", "filters": filters}
        except json.JSONDecodeError:
            # Not JSON, treat as text response
            pass
        
        # If we got here, it's a text response
        return {"type": "response", "content": assistant_message}
        
    except Exception as e:
        print(f"Chat car search failed: {e}")
        # Fallback: ask for more info
        return {
            "type": "response",
            "content": "I'm having trouble processing your request. Could you clarify what you're looking for in a car?"
        }