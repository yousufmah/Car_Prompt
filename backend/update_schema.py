#!/usr/bin/env python3
"""
Update database schema with new tables.
Run this after adding new models to models.py.
"""

import asyncio
import sys
import os
from app.database import engine
from app.models import Base


async def update_schema():
    """Create any missing tables and extensions."""
    print("Creating missing tables and extensions...")
    
    async with engine.begin() as conn:
        # Create pgvector extension for PostgreSQL if needed
        DATABASE_URL = os.getenv("DATABASE_URL", "")
        if DATABASE_URL and "postgresql" in DATABASE_URL:
            try:
                print("Creating pgvector extension for PostgreSQL...")
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print("pgvector extension created or already exists.")
            except Exception as e:
                print(f"Note: Could not create pgvector extension: {e}")
                print("This is okay if extension already exists or you're using SQLite.")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    
    print("Schema updated successfully.")


if __name__ == "__main__":
    asyncio.run(update_schema())