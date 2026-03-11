#!/usr/bin/env python3
"""
Apply embeddings to CarPrompt database from embeddings.sql file.
Run this in Railway: railway run python3 backend/apply_embeddings.py
"""

import os
import sys
import re
from sqlalchemy import create_engine, text

# Configuration
SQL_FILE = "embeddings.sql"  # Path relative to this script
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set", file=sys.stderr)
    print("Make sure you're running this in Railway: railway run python3 backend/apply_embeddings.py", file=sys.stderr)
    sys.exit(1)

print(f"📊 Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL[:50]}...")

def parse_sql_file(filepath):
    """Parse SQL file and extract UPDATE statements."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all UPDATE statements (simple regex, works for our generated file)
    # Pattern matches UPDATE ... WHERE id = X;
    update_pattern = r"(UPDATE\s+car_listings\s+SET\s+embedding\s*=\s*'\{[^']+\}'::vector\(1536\)\s+WHERE\s+id\s*=\s*\d+\s*;)"
    updates = re.findall(update_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if not updates:
        print("❌ No UPDATE statements found in SQL file", file=sys.stderr)
        # Fallback: split by semicolons and filter for UPDATE
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
        updates = [stmt + ';' for stmt in statements if stmt.upper().startswith('UPDATE')]
    
    return updates

def main():
    # Check if SQL file exists
    if not os.path.exists(SQL_FILE):
        print(f"❌ SQL file not found: {SQL_FILE}", file=sys.stderr)
        print(f"Current directory: {os.getcwd()}", file=sys.stderr)
        print(f"Files: {os.listdir('.')}", file=sys.stderr)
        sys.exit(1)
    
    # Parse SQL file
    updates = parse_sql_file(SQL_FILE)
    print(f"📊 Found {len(updates)} UPDATE statements in {SQL_FILE}")
    
    if not updates:
        print("❌ No valid UPDATE statements to execute", file=sys.stderr)
        sys.exit(1)
    
    # Create database engine (use synchronous version)
    # Replace asyncpg with psycopg2 in URL for synchronous engine
    sync_url = DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    
    # Execute each UPDATE statement
    successful = 0
    failed = 0
    
    with engine.connect() as conn:
        for i, sql in enumerate(updates, 1):
            # Extract listing ID for logging
            match = re.search(r"WHERE\s+id\s*=\s*(\d+)", sql, re.IGNORECASE)
            listing_id = match.group(1) if match else f"#{i}"
            
            print(f"[{i}/{len(updates)}] Applying embedding for listing {listing_id}...", end=" ", flush=True)
            
            try:
                # Execute SQL
                conn.execute(text(sql))
                conn.commit()  # Commit after each statement
                print("✅")
                successful += 1
            except Exception as e:
                print(f"❌ Failed: {e}")
                failed += 1
                # Continue with next statement
                conn.rollback()
    
    print(f"\n🎉 Embedding application complete!")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total: {len(updates)}")
    
    if successful > 0:
        print("\n🔧 Verification query:")
        print("   Run: railway run psql -c \"SELECT COUNT(*) FROM car_listings WHERE embedding IS NOT NULL AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);\"")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())