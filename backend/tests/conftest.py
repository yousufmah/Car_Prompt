import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database import get_db
from app.models import Base


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for a test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client with overridden database dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    
    # Mock the AI functions to avoid OpenAI API calls
    with patch("app.ai.parse_prompt", new_callable=AsyncMock) as mock_parse, \
         patch("app.ai.get_embedding", new_callable=AsyncMock) as mock_embed:
        
        # Setup default mock responses
        mock_parse.return_value = {
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
            "keywords": [],
            "sort_by": "price_asc"
        }
        
        mock_embed.return_value = [0.0] * 1536  # Mock embedding vector
        
        with TestClient(app) as client:
            yield client
    
    app.dependency_overrides.clear()