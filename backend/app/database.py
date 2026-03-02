from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/carprompt")
print(f"[DEBUG] Database URL: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True)
print(f"[DEBUG] Engine created with dialect: {engine.url.drivername}")

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
