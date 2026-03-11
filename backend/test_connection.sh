#!/bin/bash
set -e

echo "🔍 CarPrompt Database Connection Test"
echo "======================================"

# Check for DATABASE_URL
if [[ -z "$DATABASE_URL" ]]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo "   Make sure you're running this in Railway: railway run bash backend/test_connection.sh"
    exit 1
fi

echo "📊 Using database: $(echo $DATABASE_URL | sed 's/.*@//' | cut -d'/' -f1)"

# Check for psql
if ! command -v psql &> /dev/null; then
    echo "❌ psql command not found"
    exit 1
fi

# Parse DATABASE_URL using Python
echo "🔧 Parsing connection details..."
python3 << 'EOF'
import os
from urllib.parse import urlparse

url = os.environ['DATABASE_URL']
# Remove +asyncpg if present
url = url.replace('+asyncpg', '')

parsed = urlparse(url)
if parsed.scheme != 'postgresql':
    print("❌ Unsupported database scheme:", parsed.scheme)
    exit(1)

username = parsed.username or ''
password = parsed.password or ''
hostname = parsed.hostname or ''
port = parsed.port or 5432
database = parsed.path.lstrip('/') or ''

if not all([username, password, hostname, database]):
    print("❌ Could not parse DATABASE_URL")
    exit(1)

# Write to environment for bash
with open('/tmp/pg_vars_test', 'w') as f:
    f.write(f'export PGUSER="{username}"\n')
    f.write(f'export PGPASSWORD="{password}"\n')
    f.write(f'export PGHOST="{hostname}"\n')
    f.write(f'export PGPORT="{port}"\n')
    f.write(f'export PGDATABASE="{database}"\n')
    
print(f"✅ Parsed: {username}@{hostname}:{port}/{database}")
EOF

# Load the variables
source /tmp/pg_vars_test

# Test connection with a simple query
echo "🔌 Testing database connection..."
if psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT 1;" &> /dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Get listing count
echo "📊 Checking car listings..."
TOTAL=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -A -c "SELECT COUNT(*) FROM car_listings;")
echo "   Total car listings: $TOTAL"

# Check embeddings
echo "🔍 Checking embeddings..."
REAL_EMBEDDINGS=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -A -c "
    SELECT COUNT(*) FROM car_listings 
    WHERE embedding IS NOT NULL 
    AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);
")
echo "   Listings with real embeddings: $REAL_EMBEDDINGS/$TOTAL"

# Show sample listings
if [[ "$TOTAL" -gt 0 ]]; then
    echo "📋 Sample listings (first 5):"
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -A -F " | " -c "
        SELECT id, LEFT(title, 40) || '...' as title, make, year, price 
        FROM car_listings 
        ORDER BY id 
        LIMIT 5;
    "
fi

echo "======================================"
echo "✅ Connection test complete!"
if [[ "$REAL_EMBEDDINGS" -eq 0 ]]; then
    echo "⚠️  No real embeddings found. Run: railway run bash backend/apply_embeddings.sh"
elif [[ "$REAL_EMBEDDINGS" -eq "$TOTAL" ]]; then
    echo "🎉 All listings have embeddings! Semantic search is ready."
else
    echo "⚠️  Only $REAL_EMBEDDINGS/$TOTAL listings have embeddings."
fi