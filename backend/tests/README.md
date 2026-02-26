# API Tests for CarPrompt

Tests for the FastAPI endpoints using pytest with SQLite in-memory database.

## Setup

1. Install test dependencies:

```bash
cd /path/to/CarPrompt/backend
pip install -r requirements-test.txt
```

Or if using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Main dependencies
pip install -r requirements-test.txt  # Test dependencies
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_search.py -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

## Test Structure

- `conftest.py`: Test fixtures (database setup, mocks, test client)
- `test_search.py`: Tests for `/api/search/` endpoint
- `test_listings.py`: Tests for `/api/listings/` endpoints
- `test_garages.py`: Tests for `/api/garages/` endpoints
- `test_root.py`: Test for root endpoint

## Key Features

- **Mocked AI calls**: `parse_prompt()` and `get_embedding()` are mocked to avoid OpenAI API calls
- **In-memory SQLite database**: Each test gets a fresh database
- **Async test support**: Uses `pytest-asyncio` for async/await tests
- **FastAPI TestClient**: For HTTP request testing

## What's Tested

### Search Endpoint (`/api/search/`)
- ✅ Basic endpoint structure
- ✅ Filter parsing integration
- ✅ Search log creation
- ✅ Error handling for invalid requests

### Listings Endpoints (`/api/listings/`)
- ✅ GET all listings (with pagination)
- ✅ GET single listing by ID
- ✅ POST create new listing
- ✅ Field validation
- ✅ 404 handling for non-existent listings
- ✅ Case normalization (makes/models lowercased)

### Garages Endpoints (`/api/garages/`)
- ✅ GET all garages
- ✅ POST create new garage
- ✅ Field validation
- ✅ Email format validation

### Root Endpoint (`/`)
- ✅ API info response

## Adding More Tests

1. For new endpoints, create a new test file `test_<name>.py`
2. Use the existing fixtures (`test_client`, `db_session`)
3. Mock external API calls using `patch()` from `unittest.mock`
4. Write both happy path and error case tests

## Notes

- Tests assume OpenAI API calls are mocked
- Embedding vectors are mocked as zero vectors
- Database constraints (like unique emails) are not fully tested in SQLite
- For production testing, use PostgreSQL with pgvector