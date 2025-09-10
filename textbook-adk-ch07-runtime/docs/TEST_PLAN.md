# PostgreSQL Runtime Test Plan

This comprehensive test plan validates the PostgreSQL-backed ADK runtime system before merging to main branch. It combines automated testing with human-guided validation of web UI components.

## Test Environment Setup

### Prerequisites
```bash
# 1. Clean environment
make dev-down
rm -rf docker/data/
git status  # Ensure clean working directory

# 2. Fresh setup
make dev-setup  # Dependencies + containers + migrations
make status     # Verify migrations applied
```

### Environment Verification
- [ ] Both PostgreSQL instances running (ports 5432, 5433)
- [ ] Database schemas migrated successfully
- [ ] Data directories created with proper .gitignore coverage
- [ ] No database files in git status

---

## Phase 1: Automated Core Services Testing

### 1.1 Database Infrastructure
```bash
# Test database connectivity and schema
uv run python examples/setup_database.py
uv run python scripts/check_migration_status.py
```

**Expected Results:**
- [ ] All 6 migrations applied successfully
- [ ] Database ready status: `true`
- [ ] Both main and vector databases accessible

### 1.2 Service Integration Tests
```bash
# Core service functionality
uv run python examples/test_services.py
```

**Expected Results:**
- [ ] ✅ Session service: CRUD operations work correctly
- [ ] ✅ Memory service: Indexing and search functional  
- [ ] ✅ Artifact service: PostgreSQL BYTEA storage (up to 25MB)
- [ ] No connection failures or service initialization errors

### 1.3 Plugin System Tests
```bash
# Web UI plugin system
uv run python examples/test_web_plugin_system.py
```

**Expected Results:**
- [ ] Service loader resolves `postgres-runtime:` URLs correctly
- [ ] Plugin registration works for all three service types
- [ ] Factory functions create proper service instances
- [ ] URL parsing handles query parameters correctly

### 1.4 Event Sourcing Validation
```bash
# Test event creation and memory indexing
uv run python postgres_chat_agent/driver.py --test-memory
```

**Expected Results:**
- [ ] ADK events created with proper structure (`Event`, `EventActions`)
- [ ] State delta information captured in events
- [ ] Memory indexes reference events without duplication
- [ ] Searchable content includes both text and state information

---

## Phase 2: CLI Agent Testing (Human-Guided)

### 2.1 Basic Agent Functionality
```bash
# Start interactive agent
uv run python postgres_chat_agent/main.py
```

**Test Scenarios:**
- [ ] Agent starts without errors
- [ ] Session created and persisted to PostgreSQL
- [ ] Basic conversation works (test with simple question)
- [ ] Session state maintained across interactions

### 2.2 Slash Commands Testing
**Test each slash command systematically:**

```bash
# Memory commands
/save machine learning research
/save academic writing best practices
/memory machine learning
/memory academic

# Session management
/session
/help

# Artifact operations
/artifacts
```

**Expected Results:**
- [ ] `/save`: Successfully stores content to memory service
- [ ] `/memory`: Returns relevant search results
- [ ] `/session`: Shows session info without errors
- [ ] `/artifacts`: Lists artifacts (may be empty initially)
- [ ] `/help`: Shows comprehensive command reference

### 2.3 Data Persistence Testing
```bash
# Test 1: Stop and restart agent
# 1. Create some memory entries with /save
# 2. Exit agent (Ctrl+C)
# 3. Restart agent
# 4. Search for previously saved content

# Test 2: Container restart persistence
make dev-down
make dev-up
# Restart agent and verify data still exists
```

**Expected Results:**
- [ ] Memory persists across agent restarts
- [ ] Session continuity maintained
- [ ] Data survives container restarts
- [ ] No data loss or corruption

---

## Phase 3: Web UI Testing (Human-Guided)

### 3.1 Web UI Startup Testing
**Test all three startup methods:**

#### Method 1: Shell Script
```bash
./scripts/run_postgres_web_ui.sh postgres_chat_agent
```

#### Method 2: Python Script  
```bash
python scripts/run_postgres_web_ui.py postgres_chat_agent
```

#### Method 3: Direct CLI
```bash
adk-webx \
  --agent-dir postgres_chat_agent \
  --session-service "postgres-runtime:" \
  --memory-service "postgres-runtime:" \
  --artifact-service "postgres-runtime:" \
  --plugin python:examples.web_ui_plugins.postgres_runtime_plugin \
  --host 127.0.0.1 --port 8000
```

**Expected Results for Each Method:**
- [ ] Prerequisites check passes (PostgreSQL connectivity)
- [ ] Plugin system installs successfully
- [ ] Web server starts on specified port
- [ ] No startup errors or service failures
- [ ] Browser accessible at `http://localhost:8000` (or specified port)

### 3.2 Web UI Functionality Testing

#### Basic Interface Testing
- [ ] **Page loads correctly**: No JavaScript errors in browser console
- [ ] **Agent selection**: Can select `postgres_chat_agent` 
- [ ] **Chat interface**: Input field and send button functional
- [ ] **Visual layout**: Professional appearance, no broken styling

#### Conversation Flow Testing
- [ ] **Send message**: Text messages send and receive responses
- [ ] **Session persistence**: Refresh page, conversation history maintained
- [ ] **Multiple conversations**: Can have extended back-and-forth dialog
- [ ] **Error handling**: Graceful handling of long response times

#### PostgreSQL Integration Testing
**Test that web UI uses PostgreSQL services:**
- [ ] **Session service**: New web sessions appear in PostgreSQL
- [ ] **Memory service**: Conversations indexed for future search
- [ ] **Artifact service**: File uploads/downloads work (if implemented)

**Validation Method:**
```sql
-- Connect to database and verify data
psql -h localhost -p 5432 -U adk_user -d adk_runtime
\dt -- List tables
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM memory;  
SELECT COUNT(*) FROM artifacts;
```

#### Performance Testing
- [ ] **Response time**: Web responses within reasonable time (< 30s)
- [ ] **Concurrent users**: Multiple browser tabs work simultaneously
- [ ] **Large conversations**: Handle conversations with 20+ exchanges
- [ ] **Memory usage**: No obvious memory leaks during extended use

### 3.3 Error Scenario Testing
**Test system resilience:**

#### Database Connectivity Issues
```bash
# Simulate database downtime
make dev-down
# Try to use web UI - should show graceful error messages
make dev-up
# System should recover automatically
```

- [ ] **Graceful degradation**: Clear error messages, no crashes
- [ ] **Recovery**: System works normally after database restart
- [ ] **User feedback**: Informative error messages in web UI

#### Invalid Configurations
- [ ] **Wrong ports**: Test with incorrect database ports
- [ ] **Missing agent**: Test with non-existent agent directory
- [ ] **Permission issues**: Test file permission problems

---

## Phase 4: Integration & Cross-Platform Testing

### 4.1 Multi-Database Testing
**Verify both PostgreSQL instances work correctly:**
- [ ] **Main DB (5432)**: Sessions and artifacts
- [ ] **Vector DB (5433)**: Memory/embeddings
- [ ] **Data separation**: Each database handles appropriate data types
- [ ] **Connection pooling**: No connection exhaustion

### 4.2 Artifact Storage Testing
**Test PostgreSQL BYTEA storage limits:**
- [ ] **Small files** (< 1MB): Upload/download works
- [ ] **Medium files** (5-15MB): Proper handling
- [ ] **Large files** (> 25MB): Clear error message about size limit
- [ ] **Binary files**: PDFs, images handle correctly

### 4.3 Event Sourcing Validation
**Verify event sourcing implementation:**
- [ ] **Event structure**: Proper ADK Event and EventActions format
- [ ] **State deltas**: Conversation state changes captured
- [ ] **Audit trail**: Complete history available
- [ ] **Search integration**: State information searchable

---

## Phase 5: Production Readiness Testing

### 5.1 Data Safety Testing
- [ ] **Backup/restore**: Data directories can be backed up
- [ ] **Container recreation**: `docker-compose down && docker-compose up`
- [ ] **Volume permissions**: Proper ownership and permissions
- [ ] **Git safety**: No database files in repository

### 5.2 Documentation Testing
**Verify all documentation is accurate:**
- [ ] **README_POSTGRES_WEB_UI.md**: Instructions work as written
- [ ] **Agent README**: Reflects current BYTEA storage
- [ ] **Script help text**: `--help` options accurate
- [ ] **Error messages**: Helpful troubleshooting information

### 5.3 Code Quality Testing
```bash
# Run all quality checks
ruff check textbook-adk-ch07-runtime/
pyright textbook-adk-ch07-runtime/
pytest textbook-adk-ch07-runtime/tests/ -v
```

**Expected Results:**
- [ ] No linting errors
- [ ] No type checking errors  
- [ ] All unit tests pass
- [ ] Test coverage adequate

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Clean git working directory
- [ ] Fresh database setup (`make dev-setup`)
- [ ] All dependencies installed (`uv sync`)

### Automated Tests (Prerequisite for manual testing)
- [ ] Phase 1: Core services pass
- [ ] Plugin system tests pass
- [ ] Code quality checks pass

### Manual Testing (Human-guided)
- [ ] Phase 2: CLI agent functionality
- [ ] Phase 3: Web UI testing (all three startup methods)
- [ ] Phase 4: Integration testing
- [ ] Phase 5: Production readiness

### Post-Test Cleanup
- [ ] Document any issues found
- [ ] Verify data persistence across restarts
- [ ] Confirm .gitignore working (no database files committed)

---

## Success Criteria

The system is ready for merge when:

✅ **All automated tests pass** without errors
✅ **Web UI accessible** via all three startup methods  
✅ **Data persistence** confirmed across restarts
✅ **PostgreSQL integration** validated (both databases)
✅ **Event sourcing** working correctly
✅ **Error handling** graceful and informative
✅ **Documentation** accurate and complete
✅ **Code quality** meets standards (ruff, pyright, tests)

## Risk Areas Requiring Extra Attention

⚠️ **Database connectivity**: Ensure both 5432 and 5433 ports working
⚠️ **Web UI plugin loading**: Complex service resolution logic
⚠️ **Event sourcing**: ADK compliance and data integrity
⚠️ **Artifact size limits**: 25MB PostgreSQL BYTEA constraints
⚠️ **Container persistence**: Volume mount reliability
⚠️ **Cross-platform compatibility**: Podman vs Docker behavior

---

*This test plan ensures comprehensive validation of the PostgreSQL runtime system before production deployment.*