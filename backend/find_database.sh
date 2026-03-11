#!/bin/bash
set -e

echo "🔍 Finding CarPrompt Database"
echo "============================="

# Extract credentials from DATABASE_URL
URL="${DATABASE_URL}"
if [[ -z "$URL" ]]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Parse credentials (same for all hostnames)
CLEAN_URL=$(echo "$URL" | sed 's/+asyncpg//')
USER=$(echo "$CLEAN_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
PASS=$(echo "$CLEAN_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
PORT=$(echo "$CLEAN_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
PORT=${PORT:-5432}
DB=$(echo "$CLEAN_URL" | sed -n 's|.*/||p')

if [[ -z "$USER" || -z "$PASS" || -z "$DB" ]]; then
    echo "❌ Could not parse DATABASE_URL"
    exit 1
fi

echo "🔑 Using credentials: $USER:***@[host]:$PORT/$DB"
echo ""

# List of possible Railway hostnames to try
HOSTS=(
    "localhost"
    "127.0.0.1"
    "postgres.railway.internal"
    "postgres"
    "pgvector"
    "db.railway.internal"
    "database.railway.internal"
    "$(echo "$CLEAN_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p')"  # Original host
)

# Also try to get IP from Railway's internal DNS if possible
echo "🌐 Testing hostname resolution..."
for host in "${HOSTS[@]}"; do
    echo -n "  $host: "
    if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$host/$PORT 2>/dev/null"; then
        echo "✅ Reachable"
    else
        echo "❌ Not reachable"
    fi
done

echo ""
echo "🔌 Testing connections..."

FOUND_HOST=""
for host in "${HOSTS[@]}"; do
    echo -n "Testing $host... "
    export PGPASSWORD="$PASS"
    if psql -h "$host" -p "$PORT" -U "$USER" -d "$DB" -c "SELECT 1;" 2>/dev/null; then
        echo "✅ Connected!"
        FOUND_HOST="$host"
        break
    else
        echo "❌ Failed"
    fi
done

if [[ -n "$FOUND_HOST" ]]; then
    echo ""
    echo "🎉 Found working database at: $FOUND_HOST"
    echo ""
    
    # Check if car_listings table exists
    echo "📊 Checking database contents..."
    export PGPASSWORD="$PASS"
    LISTING_COUNT=$(psql -h "$FOUND_HOST" -p "$PORT" -U "$USER" -d "$DB" -t -A -c "SELECT COUNT(*) FROM car_listings;" 2>/dev/null || echo "0")
    echo "   Car listings: $LISTING_COUNT"
    
    if [[ "$LISTING_COUNT" -gt 0 ]]; then
        echo "✅ This is the correct database!"
        echo ""
        echo "🚀 To apply embeddings, run:"
        echo "   export PGPASSWORD=\"$PASS\""
        echo "   psql -h \"$FOUND_HOST\" -p \"$PORT\" -U \"$USER\" -d \"$DB\" -f embeddings.sql"
        echo ""
        echo "Or use this one-liner:"
        CONN_STR="postgresql://$USER:$PASS@$FOUND_HOST:$PORT/$DB"
        echo "   psql \"$CONN_STR\" -f embeddings.sql"
    else
        echo "⚠️  No car listings found. This might not be the right database."
    fi
else
    echo ""
    echo "❌ Could not connect to any database host."
    echo ""
    echo "🔧 Next steps:"
    echo "1. Check if your PostgreSQL service is running in Railway"
    echo "2. Look for a service named 'postgres' or similar"
    echo "3. Click on the service to find its connection details"
    echo "4. Update DATABASE_URL environment variable with correct hostname"
    echo ""
    echo "📋 Current DATABASE_URL:"
    echo "   $(echo "$DATABASE_URL" | sed 's/:[^:]*@/:***@/')"
fi