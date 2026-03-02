#!/usr/bin/env python3
"""
Update database schema with new tables.
Run this after adding new models to models.py.
"""

import asyncio
import sys
from app.database import engine
from app.models import Base


async def update_schema():
    """Create any missing tables."""
    print("Creating missing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("Schema updated successfully.")


if __name__ == "__main__":
    asyncio.run(update_schema())