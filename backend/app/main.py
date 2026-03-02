# Deployment trigger 2026-03-02 17:00 UTC
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import search, listings, garages, search_advanced, admin, analytics
from datetime import datetime
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base
from sqlalchemy import text

# Analytics endpoints added for garage dashboard (2026-03-02)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables if they don't exist
    print("Creating database tables if they don't exist...")
    async with engine.begin() as conn:
        # Enable pgvector extension for PostgreSQL
        if str(engine.url).startswith('postgresql'):
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("Database tables ready.")
    yield
    # Shutdown: close connections
    await engine.dispose()

app = FastAPI(title="Car Prompt API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(search_advanced.router, prefix="/api/search", tags=["search"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(garages.router, prefix="/api/garages", tags=["garages"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/")
async def root():
    return {"message": "Car Prompt API", "version": "0.2.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
