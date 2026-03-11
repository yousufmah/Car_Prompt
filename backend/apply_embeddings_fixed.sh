#!/bin/bash
set -e

echo "🚀 CarPrompt Embedding Application (Fixed)"
echo "=========================================="

# Check for DATABASE_URL
if [[ -z "$DATABASE_URL" ]]; then
    echo "❌ DATABASE_URL environment variable not set"
    exit 1
fi

echo "📊 Original DATABASE_URL: $(echo $DATABASE_URL | sed 's/:[^:]*@/:***@/')"

# Clean the URL for psql (remove +asyncpg)
CLEAN_URL=$(echo "$DATABASE_URL" | sed 's/+asyncpg//')
echo "🔧 Clean URL for psql: $(echo $CLEAN_URL | sed 's/:[^:]*@/:***@/')"

# Check if SQL file exists
SQL_FILE="embeddings.sql"
if [[ ! -f "$SQL_FILE" ]]; then
    echo "❌ SQL file not found: $SQL_FILE"
    echo "   Current directory: $(pwd)"
    echo "   Files: $(ls -la)"
    exit 1
fi

echo "📄 Found SQL file: $SQL_FILE ($(wc -l < $SQL_FILE) lines)"
UPDATE_COUNT=$(grep -c "^UPDATE" "$SQL_FILE")
echo "📊 Found $UPDATE_COUNT UPDATE statements"

# Try Method 1: Direct connection with cleaned URL
echo "🚀 Method 1: Using psql with cleaned URL..."
if psql "$CLEAN_URL" -f "$SQL_FILE"; then
    echo "✅ Successfully applied embeddings with Method 1!"
    verify_embeddings
    exit 0
fi

echo "❌ Method 1 failed, trying Method 2..."

# Method 2: Parse URL and try with host IP resolution
parse_and_connect() {
    python3 << 'EOF'
import os
import re
import subprocess
import sys

url = os.environ['DATABASE_URL']
# Remove +asyncpg
url = url.replace('+asyncpg', '')

# Simple regex parsing (avoid urllib.parse which might not handle all cases)
match = re.match(r'postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)', url)
if not match:
    print("❌ Could not parse DATABASE_URL")
    sys.exit(1)
    
user, password, host, port, database = match.groups()
port = port or '5432'

print(f"Parsed: {user}@{host}:{port}/{database}")

# Try to resolve host to IP
try:
    import socket
    ip = socket.gethostbyname(host)
    print(f"Resolved {host} -> {ip}")
    
    # Build connection string with IP
    conn_str = f"postgresql://{user}:{password}@{ip}:{port}/{database}"
    
    # Try to connect
    cmd = ["psql", conn_str, "-f", "embeddings.sql"]
    print(f"Running: psql postgresql://{user}:***@{ip}:{port}/{database}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success!")
        sys.exit(0)
    else:
        print(f"❌ Failed: {result.stderr[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF
}

# Run Method 2
if parse_and_connect; then
    verify_embeddings
    exit 0
fi

echo "❌ Method 2 failed, trying Method 3..."

# Method 3: Try with localhost (if database is in same container)
echo "🔧 Method 3: Trying localhost connection..."
# Extract just the database name and credentials from URL
DB_NAME=$(echo "$CLEAN_URL" | sed -n 's|.*/||p')
DB_USER=$(echo "$CLEAN_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo "$CLEAN_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')

if [[ -n "$DB_USER" && -n "$DB_PASS" && -n "$DB_NAME" ]]; then
    export PGPASSWORD="$DB_PASS"
    if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"; then
        echo "✅ Successfully applied embeddings with Method 3 (localhost)!"
        verify_embeddings
        exit 0
    fi
fi

echo "❌ All methods failed."
echo ""
echo "🔧 Next steps:"
echo "1. Use Railway web SQL console (recommended):"
echo "   - Go to https://railway.app/"
echo "   - Navigate to CarPrompt project"
echo "   - Click on your PostgreSQL service"
echo "   - Click 'Query' tab"
echo "   - Paste the contents of embeddings.sql"
echo "   - Click 'Run'"
echo ""
echo "2. Check which database service your backend is actually using:"
echo "   - Run: railway run env | grep DATABASE"
echo ""
echo "3. Verify the database has the car_listings table:"
echo "   - railway run psql \"\$DATABASE_URL\" -c \"SELECT COUNT(*) FROM car_listings;\""
exit 1

verify_embeddings() {
    echo ""
    echo "🔍 Verifying embeddings..."
    VERIFY_QUERY="SELECT COUNT(*) FROM car_listings WHERE embedding IS NOT NULL AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);"
    
    if [[ -n "$CLEAN_URL" ]]; then
        REAL_COUNT=$(psql "$CLEAN_URL" -t -A -c "$VERIFY_QUERY" 2>/dev/null || echo "0")
    else
        REAL_COUNT="0"
    fi
    
    echo "📊 Listings with real embeddings: $REAL_COUNT/$UPDATE_COUNT"
    
    if [[ "$REAL_COUNT" -eq "$UPDATE_COUNT" ]]; then
        echo "🎉 All embeddings applied successfully!"
        echo "🔗 Test semantic search at: https://carprompt.co.uk"
    else
        echo "⚠️  Some embeddings may not have been applied."
    fi
}