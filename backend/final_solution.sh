#!/bin/bash
set -e

echo "🎯 CarPrompt Embeddings - Final Solution"
echo "========================================"
echo "This guide will help you apply OpenAI embeddings to enable semantic search."
echo ""

# Step 1: Verify we have the SQL file
SQL_FILE="embeddings.sql"
if [[ ! -f "$SQL_FILE" ]]; then
    echo "❌ Missing $SQL_FILE"
    exit 1
fi

UPDATE_COUNT=$(grep -c "^UPDATE" "$SQL_FILE")
echo "✅ Ready: $UPDATE_COUNT UPDATE statements in $SQL_FILE"
echo ""

# Step 2: The Problem
echo "🔍 The Problem"
echo "--------------"
echo "Your DATABASE_URL points to: pgvector.railway.internal"
echo "This hostname is not resolvable, meaning:"
echo "• The pgvector service doesn't exist or is stopped"
echo "• Your backend is using a DIFFERENT database"
echo ""
echo "But your backend IS working (health check passes), so it must be"
echo "connected to SOME database. We need to find that database."
echo ""

# Step 3: Find the Correct Database
echo "🔧 Step 1: Find Your Database in Railway Dashboard"
echo "---------------------------------------------------"
echo ""
echo "A. Go to https://railway.app/"
echo "B. Select your CarPrompt project"
echo "C. Look for database services:"
echo "   - PostgreSQL (elephant icon)"
echo "   - Might be named 'postgres', 'database', or similar"
echo "   - NOT 'pgvector' (that's the broken one)"
echo ""
echo "D. Click the PostgreSQL service"
echo "E. Look for tabs:"
echo "   1. 'Query' (most common) - if you see a SQL editor,"
echo "      paste the entire $SQL_FILE content and click 'Run'"
echo "      → DONE!"
echo ""
echo "   2. 'Data' → then 'Query'"
echo "   3. 'Console' or 'SQL Editor'"
echo "   4. 'Connect' → 'Query'"
echo ""
echo "F. If you find the Query tab, run the SQL and you're done!"
echo ""

# Step 4: Alternative - Get External Connection String
echo "🔧 Step 2: Get External Connection String"
echo "------------------------------------------"
echo "If you can't find the Query tab, get the external connection string:"
echo ""
echo "A. In the PostgreSQL service page, click 'Connect' or 'Connection'"
echo "B. Look for 'External Connection' or 'Connection URL'"
echo "C. Copy the URL (looks like):"
echo "   postgresql://postgres:password@host.railway.app:5432/railway"
echo "   (NOTE: ends with .railway.app, NOT .railway.internal)"
echo ""
echo "D. Test the connection:"
echo "   bash backend/test_connection_string.sh 'your-connection-url'"
echo ""
echo "E. If it works, apply embeddings:"
echo "   psql 'your-connection-url' -f $SQL_FILE"
echo ""

# Step 5: Check for Other Database Services
echo "🔧 Step 3: List All Services"
echo "----------------------------"
echo "Run this command to see all services in your project:"
echo "  railway service 2>&1"
echo ""
echo "Look for services with type 'postgres' or similar."
echo ""

# Step 6: What if No Database Service Exists?
echo "🔧 Step 4: No Database Found?"
echo "-----------------------------"
echo "If you don't see ANY PostgreSQL service, your backend might be:"
echo "• Using SQLite (unlikely)"
echo "• Using a different project's database"
echo "• Connected to pgvector but it's hidden/stopped"
echo ""
echo "Check your backend logs for database connection errors:"
echo "  railway logs Car_Prompt 2>&1 | tail -20"
echo ""

# Step 7: Last Resort - Update DATABASE_URL
echo "🔧 Step 5: Update DATABASE_URL"
echo "------------------------------"
echo "If you find a working PostgreSQL service with a different hostname:"
echo ""
echo "1. Get the INTERNAL connection string (ends with .railway.internal)"
echo "2. Update your environment:"
echo "   railway variables set DATABASE_URL 'postgresql://...@postgres.railway.internal:5432/railway'"
echo "3. Redeploy: railway up"
echo "4. Run embeddings: railway run bash backend/apply_embeddings.sh"
echo ""

# Step 8: The SQL
echo "📋 The SQL to Run"
echo "-----------------"
echo "File: $SQL_FILE"
echo "First 3 UPDATE statements:"
grep "^UPDATE" "$SQL_FILE" | head -3
echo "... (total: $UPDATE_COUNT statements)"
echo ""
echo "Once applied, test semantic search at: https://carprompt.co.uk"
echo "Try: 'reliable family car under £10k'"
echo ""

exit 0