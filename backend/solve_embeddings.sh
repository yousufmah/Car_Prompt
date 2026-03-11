#!/bin/bash
set -e

echo "🔧 CarPrompt Embedding Solution Script"
echo "======================================"
echo "This script will help you apply embeddings to the correct database."
echo ""

# Step 1: Check what we have
echo "📋 Step 1: Checking environment..."
echo "DATABASE_URL: $(echo ${DATABASE_URL:-not set} | sed 's/:[^:]*@/:***@/')"
echo ""

# Check for SQL file
SQL_FILE="embeddings.sql"
if [[ ! -f "$SQL_FILE" ]]; then
    echo "❌ SQL file not found: $SQL_FILE"
    echo "   Run from the Car_Prompt directory: cd ~/.openclaw/workspace/Car_Prompt"
    exit 1
fi

UPDATE_COUNT=$(grep -c "^UPDATE" "$SQL_FILE")
echo "📄 Found $UPDATE_COUNT UPDATE statements in $SQL_FILE"
echo ""

# Step 2: Try the direct approach first
echo "🚀 Step 2: Trying direct connection..."
if [[ -n "$DATABASE_URL" ]]; then
    CLEAN_URL=$(echo "$DATABASE_URL" | sed 's/+asyncpg//')
    echo "Trying: psql \"$CLEAN_URL\" -f embeddings.sql"
    echo "(Hostname: $(echo "$CLEAN_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p'))"
    
    if psql "$CLEAN_URL" -c "SELECT 1;" 2>/dev/null; then
        echo "✅ Can connect to database!"
        if psql "$CLEAN_URL" -f "$SQL_FILE"; then
            echo "🎉 Successfully applied embeddings!"
            verify_success "$CLEAN_URL"
            exit 0
        fi
    else
        echo "❌ Cannot connect using DATABASE_URL"
        echo "   Error: Hostname might not be resolvable from this container"
    fi
fi

echo ""
echo "⚠️  Direct connection failed. This is common with Railway's internal DNS."
echo ""

# Step 3: Provide solutions
echo "🔧 Step 3: Choose a solution below"
echo ""
echo "=== OPTION A: Railway Web Console (RECOMMENDED) ==="
echo "1. Go to https://railway.app/"
echo "2. Navigate to your CarPrompt project"
echo "3. Look for your PostgreSQL service (might be named 'postgres' or similar)"
echo "4. Click on it, then click 'Query' tab"
echo "5. Paste the entire contents of embeddings.sql"
echo "6. Click 'Run'"
echo "7. Done in 2 minutes!"
echo ""
echo "=== OPTION B: Find Correct Database ==="
echo "Run these commands to discover your database:"
echo "  railway run env | grep -i database"
echo "  railway run env | grep -i postgres"
echo "  railway run env | grep -i pg"
echo ""
echo "Look for environment variables like:"
echo "  - DATABASE_URL (might point to different service)"
echo "  - POSTGRES_URL, POSTGRES_HOST, etc."
echo "  - PGHOST, PGPORT, PGDATABASE, PGUSER"
echo ""
echo "=== OPTION C: Check Current Database ==="
echo "Your backend is running at: https://carprompt-production.up.railway.app"
echo "Test if it's connected to pgvector or postgres:"
echo "  curl -s https://carprompt-production.up.railway.app/api/listings | head -5"
echo ""
echo "=== OPTION D: Manual Debug ==="
echo "1. List your Railway services:"
echo "   railway services"
echo "2. Check which has data:"
echo "   railway run psql -c \"SELECT COUNT(*) FROM car_listings;\""
echo "   (If this works, note which service it connects to)"
echo ""
echo "=== OPTION E: Create Simple Fix ==="
echo "If the database is actually 'postgres' not 'pgvector':"
echo "1. Update DATABASE_URL to point to postgres service"
echo "2. Run: railway variables set DATABASE_URL 'postgresql://...'"
echo "   (Get the correct URL from Railway dashboard)"
echo ""

# Function to verify success
verify_success() {
    local conn_str="$1"
    echo ""
    echo "🔍 Verifying embeddings..."
    VERIFY_QUERY="SELECT COUNT(*) FROM car_listings WHERE embedding IS NOT NULL AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);"
    REAL_COUNT=$(psql "$conn_str" -t -A -c "$VERIFY_QUERY" 2>/dev/null || echo "0")
    echo "📊 Listings with real embeddings: $REAL_COUNT/$UPDATE_COUNT"
    
    if [[ "$REAL_COUNT" -eq "$UPDATE_COUNT" ]]; then
        echo "🎉 All embeddings applied successfully!"
        echo "🔗 Test semantic search at: https://carprompt.co.uk"
        echo "   Try queries like: 'reliable family car under £10k'"
    else
        echo "⚠️  Only $REAL_COUNT/$UPDATE_COUNT embeddings applied."
    fi
}

echo "======================================"
echo "Recommendation: Use OPTION A (Web Console)"
echo "It's the fastest and most reliable method."
exit 1