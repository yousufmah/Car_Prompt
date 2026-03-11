#!/bin/bash
set -e

echo "🚀 CarPrompt Embedding Application Script"
echo "=========================================="

# Check for DATABASE_URL
if [[ -z "$DATABASE_URL" ]]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo "   Make sure you're running this in Railway: railway run bash backend/apply_embeddings.sh"
    exit 1
fi

echo "📊 Using database: $(echo $DATABASE_URL | sed 's/.*@//' | cut -d'/' -f1)"

# Check for psql
if ! command -v psql &> /dev/null; then
    echo "❌ psql command not found. Installing postgresql-client..."
    apt-get update && apt-get install -y postgresql-client
fi

# Check for Python (for URL parsing)
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found"
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
with open('/tmp/pg_vars', 'w') as f:
    f.write(f'export PGUSER="{username}"\n')
    f.write(f'export PGPASSWORD="{password}"\n')
    f.write(f'export PGHOST="{hostname}"\n')
    f.write(f'export PGPORT="{port}"\n')
    f.write(f'export PGDATABASE="{database}"\n')
    
print(f"✅ Parsed: {username}@{hostname}:{port}/{database}")
EOF

# Load the variables
source /tmp/pg_vars

# Check if SQL file exists
SQL_FILE="embeddings.sql"
if [[ ! -f "$SQL_FILE" ]]; then
    echo "❌ SQL file not found: $SQL_FILE"
    echo "   Current directory: $(pwd)"
    echo "   Files: $(ls -la)"
    exit 1
fi

echo "📄 Found SQL file: $SQL_FILE ($(wc -l < $SQL_FILE) lines)"
echo "📊 Applying embeddings to database..."

# Count UPDATE statements in SQL file
UPDATE_COUNT=$(grep -c "^UPDATE" "$SQL_FILE")
echo "📊 Found $UPDATE_COUNT UPDATE statements"

# Apply the SQL
echo "🚀 Executing SQL..."
if psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f "$SQL_FILE"; then
    echo "✅ Successfully applied embeddings!"
    
    # Verify
    echo "🔍 Verifying application..."
    VERIFY_QUERY="SELECT COUNT(*) FROM car_listings WHERE embedding IS NOT NULL AND embedding != ARRAY_FILL(0::float, ARRAY[1536]);"
    REAL_COUNT=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -A -c "$VERIFY_QUERY")
    echo "📊 Listings with real embeddings: $REAL_COUNT/$UPDATE_COUNT"
    
    if [[ "$REAL_COUNT" -eq "$UPDATE_COUNT" ]]; then
        echo "🎉 All embeddings applied successfully!"
    else
        echo "⚠️  Some embeddings may not have been applied."
    fi
else
    echo "❌ Failed to apply embeddings"
    exit 1
fi

echo "=========================================="
echo "✅ Embedding application complete!"
echo "🔗 Test semantic search at: https://carprompt.co.uk"