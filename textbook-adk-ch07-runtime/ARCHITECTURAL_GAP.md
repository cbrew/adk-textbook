# ADK Web UI Integration Gap: Custom PostgreSQL Services

## Problem Statement

The postgres_chat_agent successfully demonstrates proper ADK service integration at the **infrastructure level** (wired into ADK Runner), but artifacts and state changes made via agent tools do not appear in the ADK web UI. This creates a broken user experience compared to Google's built-in services.

## Root Cause Analysis

### The Two-Service Architecture Problem

**ADK Web Server and Agent Runtime use completely separate service instances:**

#### Agent Runtime (✅ Working)
```python
# Our postgres_chat_agent does this correctly:
runtime = await PostgreSQLADKRuntime.create_and_initialize()
runner = Runner(
    agent=agent,
    session_service=runtime.get_session_service(),    # PostgreSQL
    memory_service=runtime.get_memory_service(),      # PostgreSQL
    artifact_service=runtime.get_artifact_service(),  # PostgreSQL
)
```

#### ADK Web Server (❌ Problem)
```python
# fast_api.py creates separate services:
session_service = InMemorySessionService()           # Default
artifact_service = InMemoryArtifactService()         # Default
memory_service = InMemoryMemoryService()             # Default

adk_web_server = AdkWebServer(
    session_service=session_service,      # Different instance!
    artifact_service=artifact_service,    # Different instance!
    memory_service=memory_service,        # Different instance!
)
```

### Consequence: Service Isolation

1. **Agent saves artifact** → PostgreSQL database ✅
2. **Web UI queries artifacts** → InMemory service (empty) ❌
3. **User sees no artifacts** in web interface ❌

The same issue affects session state and memory updates.

## Technical Details

### ADK Web Server Architecture

The ADK web server (`adk_web_server.py`) provides RESTful API endpoints that directly call service methods:

```python
async def list_artifact_names(app_name, user_id, session_id):
    return await self.artifact_service.list_artifact_keys(...)

async def load_artifact(app_name, user_id, session_id, artifact_name):
    return await self.artifact_service.load_artifact(...)
```

### Service Initialization in CLI

The `adk web` command (`fast_api.py`) creates service instances based on optional URI parameters:

```python
# Session service selection
if session_service_uri:
    if session_service_uri.startswith("agentengine://"):
        session_service = VertexAiSessionService(...)
    else:
        session_service = DatabaseSessionService(db_url=session_service_uri)
else:
    session_service = InMemorySessionService()  # Default
```

Similar logic exists for artifact and memory services, but **PostgreSQL URI support is missing**.

### Current URI Support Status

**Supported:**
- `agentengine://` - Vertex AI services
- `gs://` - Google Cloud Storage (artifacts)
- Database URLs for session service (generic DB)

**Missing:**
- PostgreSQL-specific URI handling for memory service
- PostgreSQL-specific URI handling for artifact service
- Unified PostgreSQL runtime integration

## Expected vs Actual Behavior

### Expected (with Google's built-in services)
1. User runs `adk web agent_name`
2. Agent tool saves artifact → appears immediately in UI
3. Session state updates → reflected in real-time
4. Memory saves → searchable through UI
5. Seamless user experience ✅

### Actual (with our PostgreSQL services)
1. User runs `adk web postgres_chat_agent`  
2. Agent tool saves artifact → stored in PostgreSQL ✅
3. Web UI shows no artifacts (queries InMemory service) ❌
4. Session state isolated between agent and UI ❌
5. Memory operations invisible to UI ❌
6. Broken user experience ❌

## Impact on Pedagogical Goals

This architectural gap undermines the chapter's educational objectives:

### What Students Should Learn ✅
- How to build custom ADK runtimes
- Proper service implementation extending base classes
- PostgreSQL integration with ADK infrastructure
- Event-driven agent architecture

### What's Currently Broken ❌
- End-to-end workflow demonstration
- Real-time UI feedback from custom services  
- Convenient development experience with `adk web`
- Production-ready deployment patterns

## Solution Requirements

Any solution must address:

1. **Service Consistency**: Web UI and agent runtime must use the same service instances
2. **URI Support**: Standard `--service-uri` flags should work for PostgreSQL
3. **Zero Configuration**: Default setup should "just work" for development
4. **Production Ready**: Should scale to real deployment scenarios
5. **Pedagogical Value**: Students should understand the integration pattern

## Potential Solution Approaches

### Option 1: URI-Based Integration
Extend ADK CLI to support PostgreSQL URIs:
```bash
uv run adk web postgres_chat_agent \
  --session-service-uri "postgresql://user:pass@localhost:5432/adk_runtime" \
  --memory-service-uri "postgresql://user:pass@localhost:5432/adk_runtime" \
  --artifact-service-uri "postgresql://user:pass@localhost:5432/adk_runtime"
```

### Option 2: Environment Variable Configuration
Use environment variables to configure services:
```bash
export ADK_SESSION_SERVICE_URI="postgresql://..."
export ADK_MEMORY_SERVICE_URI="postgresql://..."
export ADK_ARTIFACT_SERVICE_URI="postgresql://..."
uv run adk web postgres_chat_agent
```

### Option 3: Agent-Level Service Declaration
Allow agents to declare their preferred services:
```python
# In agent.py
preferred_services = {
    "session_service": runtime.get_session_service(),
    "memory_service": runtime.get_memory_service(), 
    "artifact_service": runtime.get_artifact_service(),
}
```

### Option 4: Runtime Integration
Modify ADK web server to detect and use agent-declared runtimes automatically.

## Related Resources

- **GitHub Discussion**: https://github.com/google/adk-python/discussions/2548
- **ADK Sessions Documentation**: https://google.github.io/adk-docs/sessions/
- **ADK Memory Documentation**: https://google.github.io/adk-docs/sessions/memory/
- **Service URI Examples**: ADK CLI `--help` output

## Impact on Chapter 7

This gap currently prevents Chapter 7 from delivering its full pedagogical value. Students can build the PostgreSQL runtime successfully, but cannot experience the complete end-to-end workflow that makes custom runtimes valuable in practice.

The gap should be addressed to provide students with a complete, working example of custom ADK runtime integration.

---

**Status**: Documented architectural gap, awaiting implementation decision.  
**Date**: 2025-01-03  
**Context**: Chapter 7 PostgreSQL Runtime Development