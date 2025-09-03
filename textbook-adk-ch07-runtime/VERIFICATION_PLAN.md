# ADK PostgreSQL Integration Verification Plan

This plan verifies that our complete ADK PostgreSQL integration works perfectly from agent tools to web UI display.

## Phase 1: Infrastructure Verification ✅

### 1.1 Database Status
```bash
# Check PostgreSQL is running
make status

# Verify migrations are applied
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 5')
print('Recent migrations:', [row[0] for row in cur.fetchall()])
cur.close()
conn.close()
"
```

### 1.2 Schema Compatibility
```bash
# Verify ADK-compatible schema
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()

# Check sessions table structure
cur.execute(\"\"\"
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'sessions' ORDER BY ordinal_position
\"\"\")
print('Sessions columns:', [row[0] for row in cur.fetchall()])

# Check primary key
cur.execute(\"\"\"
SELECT a.attname FROM pg_index i
JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid = 'sessions'::regclass AND i.indisprimary
ORDER BY a.attname
\"\"\")
print('Sessions PK:', [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
"
```

**Expected Results:**
- ✅ Migrations 008 and 009 applied
- ✅ Sessions columns: `['app_name', 'create_time', 'id', 'state', 'update_time', 'user_id']`
- ✅ Sessions PK: `['app_name', 'id', 'user_id']`

## Phase 2: Agent CLI Functionality

### 2.1 Basic Agent Operation
```bash
# Test agent via CLI (should work with our custom services)
echo "Test message via CLI" | uv run adk run postgres_chat_agent --user-id cli_test_user
```

**Expected Results:**
- ✅ Agent responds successfully
- ✅ Session data saved to PostgreSQL
- ✅ Custom PostgreSQL services working

### 2.2 Verify CLI Session Creation
```bash
# Check that CLI created sessions in database
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT app_name, user_id, id FROM sessions')
sessions = cur.fetchall()
print(f'Found {len(sessions)} sessions:')
for session in sessions:
    print(f'  App: {session[0]}, User: {session[1]}, ID: {session[2]}')
cur.close()
conn.close()
"
```

**Expected Results:**
- ✅ At least 1 session found
- ✅ App name: `postgres_chat_agent`
- ✅ User ID: `cli_test_user`

## Phase 3: Web UI Integration Testing

### 3.1 Start Web Server
```bash
# Start web server with PostgreSQL integration
./scripts/start_web_with_postgres.sh
```

**Expected Results:**
- ✅ PostgreSQL connectivity check passes
- ✅ Migration check passes  
- ✅ Web server starts on http://127.0.0.1:8000
- ✅ No errors in startup logs

### 3.2 Web UI Basic Access
**Manual Steps:**
1. Open browser to http://127.0.0.1:8000
2. Select `postgres_chat_agent`
3. Verify UI loads without errors

**Expected Results:**
- ✅ Agent selection page loads
- ✅ Chat interface appears
- ✅ No JavaScript errors in browser console

### 3.3 Session State Integration Test

**Test Scenario:** Agent tool saves state → verify it appears in web UI

**Manual Steps:**
1. In web UI, send message: "Save a note about testing the integration"
2. Agent should respond and use tools to save state
3. Check the **State** tab in web UI
4. Verify state shows the saved information

**Expected Results:**
- ✅ Agent responds to message
- ✅ State tab shows session data
- ✅ State includes conversation history
- ✅ State updates in real-time

### 3.4 Session Persistence Test

**Test Scenario:** Refresh browser → verify session state persists

**Manual Steps:**  
1. Note the current session ID in web UI
2. Refresh the browser page
3. Check if session state is preserved
4. Send another message to verify continued functionality

**Expected Results:**
- ✅ Session state preserved after refresh
- ✅ Conversation history intact
- ✅ Can continue conversation seamlessly

## Phase 4: Cross-Interface Consistency

### 4.1 CLI → Web UI State Sharing

**Test Scenario:** Create session via CLI → verify visible in web UI

**Steps:**
1. Create session via CLI:
```bash
echo "CLI session for web UI test" | uv run adk run postgres_chat_agent --user-id web_test_user --session-id cli-created-session
```

2. Check database:
```bash
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT id, state FROM sessions WHERE user_id = %s', ('web_test_user',))
session = cur.fetchone()
print(f'CLI Session ID: {session[0]}')
print(f'State keys: {list(session[1].keys()) if session[1] else \"None\"}')
cur.close()
conn.close()
"
```

3. In web UI:
   - Create new session with same user ID (`web_test_user`)
   - Check if CLI-created session data is accessible

**Expected Results:**
- ✅ CLI creates session in database
- ✅ Web UI can access same user's sessions
- ✅ Cross-interface data sharing works

### 4.2 Memory Service Integration

**Test Scenario:** Agent uses memory tools → verify persistence

**Manual Steps:**
1. In web UI, send: "Search for previous conversations about testing"
2. Agent should use memory search tools
3. Send: "Save this conversation to memory"
4. Agent should use memory save tools

**Check Memory Persistence:**
```bash
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM memory')
count = cur.fetchone()[0]
print(f'Memory entries: {count}')
if count > 0:
    cur.execute('SELECT content FROM memory LIMIT 1')
    content = cur.fetchone()[0]
    print(f'Sample content: {content[:100]}...')
cur.close()
conn.close()
"
```

**Expected Results:**
- ✅ Agent responds to memory commands
- ✅ Memory data saved to PostgreSQL
- ✅ Memory search functionality works

### 4.3 Artifact Service Integration

**Test Scenario:** Agent saves artifacts → verify storage

**Manual Steps:**
1. In web UI, send: "Save a text file called 'test.txt' with content 'Hello World'"
2. Agent should use artifact save tools

**Check Artifact Storage:**
```bash
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT filename, file_path FROM artifacts')
artifacts = cur.fetchall()
print(f'Artifacts: {len(artifacts)}')
for artifact in artifacts:
    print(f'  File: {artifact[0]}, Path: {artifact[1]}')
cur.close()
conn.close()
"
```

**Expected Results:**
- ✅ Agent responds to artifact commands  
- ✅ Artifact data saved to PostgreSQL
- ✅ File system storage works

## Phase 5: Performance & Reliability

### 5.1 Session Load Test

**Create Multiple Sessions:**
```bash
for i in {1..5}; do
  echo "Load test session $i" | uv run adk run postgres_chat_agent --user-id load_test_user_$i --session-id load-test-$i
done
```

**Verify All Sessions:**
```bash
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM sessions WHERE user_id LIKE %s', ('load_test_user_%',))
count = cur.fetchone()[0]
print(f'Load test sessions: {count}')
cur.close()
conn.close()
"
```

**Expected Results:**
- ✅ All 5 sessions created successfully
- ✅ No database errors or conflicts
- ✅ Web UI can handle multiple sessions

### 5.2 Concurrent Access Test

**Manual Steps:**
1. Open web UI in 2 different browser tabs
2. Use different user IDs in each tab
3. Send messages simultaneously in both tabs
4. Verify both sessions work independently

**Expected Results:**
- ✅ No session conflicts between tabs
- ✅ Each session maintains separate state
- ✅ Database handles concurrent access

## Phase 6: Error Handling & Edge Cases

### 6.1 Database Reconnection

**Test Steps:**
1. Start web UI session
2. Briefly stop PostgreSQL: `make dev-down`
3. Restart PostgreSQL: `make dev-up`
4. Try to use web UI again

**Expected Results:**
- ✅ Graceful error handling during downtime
- ✅ Automatic reconnection when database returns
- ✅ Session recovery works

### 6.2 Invalid Session Handling

**Test with Non-existent Session:**
```bash
uv run python -c "
import asyncio
from google.adk.sessions import DatabaseSessionService

async def test():
    service = DatabaseSessionService(db_url='postgresql://adk_user:adk_password@localhost:5432/adk_runtime')
    session = await service.get_session('nonexistent_app', 'nonexistent_user', 'nonexistent_session')
    print(f'Result: {session}')

asyncio.run(test())
"
```

**Expected Results:**
- ✅ Returns None for non-existent session
- ✅ No exceptions thrown
- ✅ Graceful handling

## Success Criteria Summary

**✅ All Tests Must Pass:**
- [ ] Database schema correctly migrated
- [ ] Agent CLI functionality works
- [ ] Web UI starts and loads properly  
- [ ] Session state appears in web UI
- [ ] State persists across browser refreshes
- [ ] Cross-interface consistency (CLI ↔ Web)
- [ ] Memory service integration
- [ ] Artifact service integration
- [ ] Multiple session handling
- [ ] Concurrent access support
- [ ] Error handling and recovery

## Troubleshooting Guide

**Common Issues:**

1. **Migration not applied**: Run `uv run python examples/setup_database.py`
2. **Web UI errors**: Check browser console, ensure PostgreSQL running
3. **Session not visible**: Verify user_id and app_name match between interfaces
4. **State not updating**: Check for JavaScript errors, verify database connectivity

**Debug Commands:**
```bash
# Check recent migrations
SELECT * FROM schema_migrations ORDER BY applied_at DESC LIMIT 5;

# Check sessions structure
\d sessions

# View active sessions
SELECT app_name, user_id, id, create_time FROM sessions ORDER BY create_time DESC;
```

This verification plan ensures complete end-to-end functionality of our ADK PostgreSQL integration! 🎯