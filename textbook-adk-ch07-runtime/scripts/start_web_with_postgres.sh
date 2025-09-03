#!/bin/bash
# Start ADK web server with PostgreSQL session service integration
# This script demonstrates partial integration with ADK's built-in services

set -e

# Configuration
DATABASE_URL="postgresql://adk_user:adk_password@localhost:5432/adk_runtime"
PORT=8000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting ADK Web Server with PostgreSQL Integration${NC}"
echo

# Check if PostgreSQL is running
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
if ! pg_isready -h localhost -p 5432 -U adk_user -d adk_runtime >/dev/null 2>&1; then
    echo -e "${RED}❌ PostgreSQL is not running or not accessible${NC}"
    echo -e "${YELLOW}💡 Run 'make dev-up' to start PostgreSQL services${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Check if migrations are applied
echo -e "${BLUE}📋 Checking database migrations...${NC}"
MIGRATION_CHECK=$(uv run python -c "
import psycopg2
conn = psycopg2.connect('$DATABASE_URL')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM schema_migrations WHERE version IN (\'006\', \'007\')')
count = cur.fetchone()[0]
cur.close()
conn.close()
print(count)
" 2>/dev/null || echo "0")

if [ "$MIGRATION_CHECK" -lt 2 ]; then
    echo -e "${YELLOW}⚠️  ADK compatibility migrations not found${NC}"
    echo -e "${BLUE}🔄 Applying required migrations...${NC}"
    
    # Apply migrations 006 and 007 if they don't exist
    uv run python -c "
import psycopg2
conn = psycopg2.connect('$DATABASE_URL')
cur = conn.cursor()

# Check and apply migration 006
cur.execute('SELECT COUNT(*) FROM schema_migrations WHERE version = \'006\'')
if cur.fetchone()[0] == 0:
    print('Applying migration 006_adk_compatibility.sql...')
    with open('migrations/006_adk_compatibility.sql', 'r') as f:
        cur.execute(f.read())
    cur.execute('INSERT INTO schema_migrations (version, applied_at) VALUES (\'006\', NOW())')

# Check and apply migration 007  
cur.execute('SELECT COUNT(*) FROM schema_migrations WHERE version = \'007\'')
if cur.fetchone()[0] == 0:
    print('Applying migration 007_id_column_type_fix.sql...')
    with open('migrations/007_id_column_type_fix.sql', 'r') as f:
        cur.execute(f.read())
    cur.execute('INSERT INTO schema_migrations (version, applied_at) VALUES (\'007\', NOW())')

conn.commit()
cur.close()
conn.close()
print('Migrations applied successfully!')
"
fi
echo -e "${GREEN}✅ Database migrations are up to date${NC}"

echo
echo -e "${BLUE}🔧 ADK Web Integration Status:${NC}"
echo -e "${GREEN}  ✅ Session Service: PostgreSQL (--session_service_uri)${NC}"
echo -e "${YELLOW}  ⚠️  Memory Service: Custom PostgreSQL (not integrated with web UI)${NC}"
echo -e "${YELLOW}  ⚠️  Artifact Service: Custom PostgreSQL (not integrated with web UI)${NC}"

echo
echo -e "${BLUE}📝 Note:${NC}"
echo -e "${YELLOW}  • Session state from agent tools will be visible in the web UI${NC}"
echo -e "${YELLOW}  • Memory and artifact operations will use our custom services${NC}"
echo -e "${YELLOW}  • This provides partial integration - sessions work, but memory/artifacts don't appear in UI${NC}"

echo
echo -e "${BLUE}🌐 Starting ADK web server...${NC}"
echo -e "${BLUE}   URL: http://127.0.0.1:$PORT${NC}"
echo -e "${BLUE}   Agent: postgres_chat_agent${NC}"
echo

# Start the ADK web server with PostgreSQL session service
exec uv run adk web postgres_chat_agent \
    --session_service_uri "$DATABASE_URL" \
    --port "$PORT" \
    --host "127.0.0.1"