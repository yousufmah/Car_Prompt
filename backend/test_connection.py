#!/usr/bin/env python3
"""
Test database connection and check current embeddings.
Run: railway run python3 backend/test_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

# Create engine
sync_url = DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(sync_url)

try:
    with engine.connect() as conn:
        # Test connection
        result = conn.execute(text("SELECT COUNT(*) FROM car_listings"))
        count = result.scalar()
        print(f"✅ Connected to database. Found {count} car listings.")
        
        # Check embeddings
        result = conn.execute(text("""
            SELECT COUNT(*) FROM car_listings 
            WHERE embedding IS NOT NULL 
            AND embedding != ARRAY_FILL(0::float, ARRAY[1536])
        """))
        real_embeddings = result.scalar()
        print(f"📊 Listings with real embeddings: {real_embeddings}/{count}")
        
        # Show a few listing IDs
        if count > 0:
            result = conn.execute(text("SELECT id, title FROM car_listings ORDER BY id LIMIT 5"))
            print("\n📋 Sample listings:")
            for row in result:
                print(f"   ID {row[0]}: {row[1][:50]}...")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)