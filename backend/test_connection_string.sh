#!/bin/bash
set -e

echo "🔌 Test Database Connection String"
echo "=================================="
echo "Use this script to test a PostgreSQL connection string from Railway."
echo "Get the connection string from Railway dashboard:"
echo "1. Click your PostgreSQL service"
echo "2. Click 'Connect' or 'Connection'"
echo "3. Copy 'External Connection' or 'Connection URL'"
echo ""

if [[ -z "$1" ]]; then
    echo "Usage: $0 'postgresql://user:pass@host:port/db'"
    echo ""
    echo "Example:"
    echo "  $0 'postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway'"
    exit 1
fi

CONN_STR="$1"
echo "Testing connection: $(echo "$CONN_STR" | sed 's/:[^:]*@/:***@/')"
echo ""

# Test connection
if psql "$CONN_STR" -c "SELECT 1;" 2>/dev/null; then
    echo "✅ Connection successful!"
    
    # Check for car_listings table
    if psql "$CONN_STR" -c "SELECT COUNT(*) FROM car_listings;" 2>/dev/null; then
        COUNT=$(psql "$CONN_STR" -t -A -c "SELECT COUNT(*) FROM car_listings;" 2>/dev/null)
        echo "📊 Found $COUNT car listings"
        
        # Check embeddings
        EMBEDDINGS=$(psql "$CONN_STR" -t -A -c "
            SELECT COUNT(*) FROM car_listings 
            WHERE embedding IS NOT NULL 
            AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);
        " 2>/dev/null || echo "0")
        echo "📊 Listings with real embeddings: $EMBEDDINGS/$COUNT"
        
        if [[ "$EMBEDDINGS" -eq 0 ]]; then
            echo ""
            echo "🚀 To apply embeddings, run:"
            echo "   psql '$CONN_STR' -f embeddings.sql"
        fi
    else
        echo "⚠️  No car_listings table found. Is this the correct database?"
    fi
else
    echo "❌ Connection failed"
    echo ""
    echo "Possible issues:"
    echo "1. Connection string is incorrect"
    echo "2. Database is not accessible from your network (check IP whitelist)"
    echo "3. Password is wrong"
    echo ""
    echo "Tip: Use the 'Connection URL' from Railway, not 'Internal Connection'"
fi