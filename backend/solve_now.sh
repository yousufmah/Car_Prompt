#!/bin/bash
set -e

echo "🔧 CarPrompt Embedding Solution"
echo "================================"
echo "This script will help you apply OpenAI embeddings to enable semantic search."
echo ""

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
SQL_FILE="embeddings.sql"
if [[ ! -f "$SQL_FILE" ]]; then
    echo "❌ Missing: $SQL_FILE"
    echo "   Make sure you're in the Car_Prompt directory"
    exit 1
fi

UPDATE_COUNT=$(grep -c "^UPDATE" "$SQL_FILE")
echo "✅ Found $UPDATE_COUNT UPDATE statements in $SQL_FILE"
echo ""

# Step 2: Try to find working database automatically
echo "🔍 Step 2: Searching for working database connection..."
bash backend/find_database.sh
echo ""

# If the above found a database, it would have exited with success.
# If we're still here, automatic discovery failed.

echo "⚠️  Automatic database discovery failed."
echo ""
echo "📋 Step 3: Manual Solution Required"
echo "==================================="
echo ""
echo "Your DATABASE_URL points to: pgvector.railway.internal"
echo "This hostname is not resolvable, which means:"
echo "• The pgvector service might be stopped"
echo "• Or it's in a different network"
echo "• Or the hostname is incorrect"
echo ""
echo "However, your CarPrompt backend IS running and connected to SOME database."
echo "We need to find that database and apply embeddings there."
echo ""

echo "🔧 Option 1: Find the Correct Database in Railway Dashboard"
echo "------------------------------------------------------------"
echo "1. Go to https://railway.app/"
echo "2. Select your CarPrompt project"
echo "3. Look for database services (usually named 'PostgreSQL' or 'postgres')"
echo "4. Click on the database service"
echo "5. Look for a 'Query' tab (sometimes under 'Data' or 'Console')"
echo "6. If you see a SQL editor, paste the contents of embeddings.sql and run it"
echo ""

echo "🔧 Option 2: Get Correct Connection Details"
echo "-------------------------------------------"
echo "1. In Railway dashboard, click on your database service"
echo "2. Look for 'Connection' or 'Connect' tab"
echo "3. Find the 'External Connection' or 'Connection URL'"
echo "4. It should look like: postgresql://user:pass@host:port/db"
echo "5. Update your environment variable:"
echo "   railway variables set DATABASE_URL 'postgresql://...'"
echo "6. Then re-run this script"
echo ""

echo "🔧 Option 3: Check Which Database Your Backend Uses"
echo "----------------------------------------------------"
echo "Run these commands to see if there are other database variables:"
echo "  railway run env | grep -i url"
echo "  railway run env | grep -i host"
echo "  railway run env | grep -i postgres"
echo ""
echo "Look for variables like: POSTGRES_URL, PGHOST, etc."
echo ""

echo "🔧 Option 4: Direct SQL Execution"
echo "---------------------------------"
echo "If you find the correct database connection string, run:"
echo "  psql 'postgresql://user:pass@host:port/db' -f embeddings.sql"
echo ""
echo "Or use Railway's CLI:"
echo "  railway run psql 'postgresql://...' -f embeddings.sql"
echo ""

echo "🔧 Option 5: Quick Test - Is pgvector Service Running?"
echo "-------------------------------------------------------"
echo "Check if the pgvector service exists:"
echo "  railway logs pgvector 2>&1 | head -20"
echo ""
echo "If it says 'service not found', you might need to:"
echo "1. Restart the pgvector service"
echo "2. Or switch to using the original postgres service"
echo ""

echo "📋 The SQL You Need to Run (embeddings.sql)"
echo "==========================================="
echo "Here are the first 3 lines (of $UPDATE_COUNT total):"
head -3 "$SQL_FILE"
echo "..."
echo ""
echo "Full file at: $(pwd)/$SQL_FILE"
echo ""
echo "Once embeddings are applied, test semantic search at:"
echo "  https://carprompt.co.uk"
echo "  Try: 'reliable family car under £10k'"
echo ""

exit 1