# Search Algorithm Improvements

## Overview
Significant improvements to CarPrompt's AI and search algorithms, implementing hybrid search with relevance scoring.

## New Features

### 1. Improved AI Prompt Parsing (`ai_improved.py`)
- **Contextual Understanding**: Better inference of user intent
- **UK Market Awareness**: Price ranges, tax bands, ULEZ compliance
- **Use Case Detection**: First car, family car, commuter, weekend car
- **Brand Nationality Mapping**: Japanese, German, British, etc.
- **Smart Defaults**: Reasonable defaults based on query context

### 2. Advanced Search Engine (`search_engine.py`)
- **Hybrid Search**: Combines vector similarity, keyword matching, and filters
- **Relevance Scoring**: Multi-factor scoring system:
  - Vector similarity (40%)
  - Price relevance (20%)
  - Year relevance (15%)
  - Mileage relevance (15%)
  - Keyword match (10%)
- **Query Expansion**: Synonym mapping for car-related terms
- **Scoring Explanations**: Human-readable explanations for each result

### 3. New API Endpoints

#### `/api/search/advanced` (POST)
**Features:**
- Improved prompt parsing
- Hybrid search with relevance scoring
- Optional spell correction
- Optional query expansion
- Detailed scoring factors and explanations

**Request:**
```json
{
  "prompt": "reliable Japanese family car under £15k",
  "limit": 20,
  "use_hybrid": true,
  "use_spell_check": false,
  "expand_query": false
}
```

**Response:**
```json
{
  "prompt": "reliable Japanese family car under £15k",
  "filters": { ... },
  "results": [
    {
      "id": 1,
      "title": "2019 Toyota Yaris 1.5 VVT-i Icon",
      ...,
      "score": 0.85,
      "scoring_factors": {
        "vector_similarity": 0.7,
        "price_relevance": 0.9,
        "year_relevance": 0.8,
        "mileage_relevance": 0.9,
        "keyword_match": 0.8
      },
      "explanation": "Highly matches your description; Great price for your budget; Right age range; Low mileage"
    }
  ],
  "count": 5,
  "metadata": { ... }
}
```

#### `/api/search/compare` (POST)
**Compare different search algorithms:**
- Basic filter-only search
- Advanced hybrid search  
- Vector-only semantic search
- Algorithm recommendation

#### `/api/search/test-queries` (GET)
**Get sample queries for testing and evaluation.**

## Technical Implementation

### Dependencies Added
- `numpy==1.26.0`: For vector operations and scoring calculations

### Scoring Algorithm Details

#### Vector Similarity (40%)
- Uses OpenAI text-embedding-ada-002
- Cosine similarity between query embedding and listing embedding
- Query expansion with synonyms improves vector search

#### Price Relevance (20%)
- Scores how close price is to ideal range
- Ideal price = midpoint of min/max filters
- Linear decay from ideal price

#### Year Relevance (15%)
- Newer cars score higher within filter bounds
- Linear normalization between min_year and max_year

#### Mileage Relevance (15%)
- Lower mileage scores higher
- Exponential decay as mileage approaches max_mileage

#### Keyword Match (10%)
- Simple text matching in title/description
- Word boundary matching for accuracy

### Query Expansion
**Synonym Mapping Examples:**
- "suv" → ["4x4", "crossover", "off-road"]
- "fuel efficient" → ["economical", "good mpg", "low fuel consumption"]
- "reliable" → ["dependable", "trustworthy", "durable"]
- "manual" → ["stick shift", "standard"]

### Spell Correction
Basic correction for common car brand misspellings:
- "toyta" → "toyota"
- "bmww" → "bmw"
- "mercedez" → "mercedes"

## Performance Considerations

### Caching Strategy
- Vector embeddings can be cached (not yet implemented)
- Frequently used filters can be cached
- Search results with same filters can be cached with TTL

### Cost Optimization
- Query expansion optional (adds LLM call)
- Spell correction lightweight (dictionary-based)
- Vector search only when keywords present

## Testing

### Sample Test Queries
1. "reliable Japanese family car under £15k" - Clear filters with budget
2. "fast sporty convertible for weekend drives" - Descriptive, experience-focused
3. "cheap to run commuter car with good mpg" - Running costs emphasis
4. "luxury SUV with low mileage" - Combination of luxury and condition
5. "first car for new driver, cheap insurance" - Specific use case

### Evaluation Metrics
- **Result Count**: Number of matching cars
- **Average Score**: Quality of matches (0-1)
- **Score Distribution**: How well algorithm ranks relevant cars
- **Algorithm Comparison**: Which approach works best for different query types

## Future Improvements

### Short-term
1. **Real Embeddings**: Generate actual OpenAI embeddings for mock data
2. **Caching Layer**: Redis for embeddings and frequent searches
3. **A/B Testing**: Compare old vs new algorithm in production
4. **Personalization**: Learn from user interactions and search logs

### Medium-term
1. **BM25 Integration**: Traditional text search for better keyword matching
2. **Learning to Rank**: ML model to improve scoring weights
3. **Multi-modal Search**: Combine image similarity with text search
4. **Conversational Refinement**: Follow-up questions to refine search

### Long-term
1. **Marketcheck Integration**: Real listing data with improved search
2. **Price Prediction**: "Good deal" scoring based on market data
3. **Personalized Ranking**: User-specific preferences and history
4. **Federated Search**: Multiple data sources with unified ranking

## Migration Guide

### From Old to New API
1. **Basic Search**: `/api/search/` remains unchanged (backward compatible)
2. **Advanced Features**: Use `/api/search/advanced` for new features
3. **Testing**: Use `/api/search/compare` to evaluate before switching
4. **Gradual Rollout**: Run both algorithms and compare results

### Database Updates
No schema changes required. Existing embeddings (zero vectors) will work but won't provide semantic search benefits.

### Configuration
Add `OPENAI_API_KEY` to environment for:
- Improved prompt parsing
- Real embeddings generation
- Query expansion

## Conclusion
The new search algorithms provide significantly better relevance and user experience while maintaining backward compatibility. The hybrid approach balances precision (filters) with recall (semantic search) for optimal results.