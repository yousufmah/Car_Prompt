#!/bin/bash
set -e

echo "🔍 Debug Database Connection"
echo "============================"

echo "📋 Environment variables:"
env | grep -i "database\|postgres\|pg" | sort

echo ""
echo "🔧 Testing connection methods..."

# Method 1: Direct DATABASE_URL with psql (clean +asyncpg)
if [[ -n "$DATABASE_URL" ]]; then
    echo "Method 1: Using DATABASE_URL directly"
    CLEAN_URL=$(echo "$DATABASE_URL" | sed 's/+asyncpg//')
    echo "Clean URL: $CLEAN_URL"
    
    if psql "$CLEAN_URL" -c "SELECT 1;" 2>/dev/null; then
        echo "✅ Method 1 works!"
        exit 0
    else
        echo "❌ Method 1 failed"
    fi
fi

# Method 2: Parse and use individual variables
echo ""
echo "Method 2: Parsing DATABASE_URL"
python3 << 'EOF'
import os
from urllib.parse import urlparse

url = os.environ.get('DATABASE_URL', '')
print(f"Original URL: {url}")

# Remove +asyncpg if present
url = url.replace('+asyncpg', '')

try:
    parsed = urlparse(url)
    print(f"Scheme: {parsed.scheme}")
    print(f"Username: {parsed.username}")
    print(f"Hostname: {parsed.hostname}")
    print(f"Port: {parsed.port or 5432}")
    print(f"Database: {parsed.path.lstrip('/')}")
    
    # Try to resolve hostname
    import socket
    try:
        ip = socket.gethostbyname(parsed.hostname)
        print(f"Resolved IP: {ip}")
    except:
        print(f"Could not resolve: {parsed.hostname}")
        
except Exception as e:
    print(f"Parse error: {e}")
EOF

# Method 3: Try Railway's internal host resolution
echo ""
echo "Method 3: Testing host resolution"
if command -v nslookup &> /dev/null; then
    if [[ -n "$DATABASE_URL" ]]; then
        HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:/]*\).*/\1/p')
        echo "Trying to resolve: $HOST"
        nslookup "$HOST" 2>&1 || echo "nslookup failed"
    fi
fi

if command -v getent &> /dev/null; then
    if [[ -n "$DATABASE_URL" ]]; then
        HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:/]*\).*/\1/p')
        echo "Trying getent hosts: $HOST"
        getent hosts "$HOST" 2>&1 || echo "getent failed"
    fi
fi

# Method 4: Try connecting with possible hostnames
echo ""
echo "Method 4: Testing common Railway hostnames"
for host in "localhost" "127.0.0.1" "postgres" "pgvector"; do
    echo "Trying host: $host"
    if PGHOST="$host" psql -U postgres -c "SELECT 1;" 2>/dev/null; then
        echo "✅ Connected to $host"
        exit 0
    fi
done

echo ""
echo "❌ All connection methods failed"
echo "============================"
echo "Possible solutions:"
echo "1. Use Railway web SQL console (recommended)"
echo "2. Check if pgvector service is running"
echo "3. Verify DATABASE_URL is correct"
exit 1