
# Design Note — adk-service-plugins (standalone)

**Owner:** Chris Brew  
**Version:** 0.1.0  
**Scope:** Standalone helper package + CLI. No changes to ADK source required.

## Problem
`adk web` wiring is currently rigid: session, memory, and artifact services are hard-coded or only configurable via ad‑hoc parameters (e.g., `session_db_url`). This makes it difficult to experiment with custom or third‑party services without patching ADK itself.

## Goals
- Provide a **small, uniform** way to specify runtime services using **URLs** or **python-import strings**.
- Keep it **drop-in and standalone**, so it can live in its own directory and run today.
- Offer a minimal **CLI** (`adk-webx`) to exercise the loader without touching ADK code.
- Remain **compatible** with existing ADK service classes if present, but not require them.

## Non-Goals
- No heavy plugin framework or discovery (`entry_points`) yet.
- No refactors to ADK internals.
- No new service semantics beyond basic resolution/instantiation.

## Public Surface
### Library
```python
from adk_service_plugins.service_loader import load_service, register_scheme

inst = load_service("inmemory:", "memory")
register_scheme("memory", "redis", lambda parsed, qs: RedisMemory(parsed.geturl(), **qs))
```

### FastAPI App Factory
```python
from adk_service_plugins.fast_api import get_fast_api_app

app = get_fast_api_app(
    agent_dir=Path("./agent"),
    session_service_url="db+sqlite:///./sessions.db",
    memory_service_url="inmemory:",
    artifact_service_url="gcs://bucket/prefix",
)
```
- Services are exposed on `app.state.session_service`, `app.state.memory_service`, `app.state.artifact_service`.

### CLI
```
adk-webx --agent-dir ./agent   --session-service "db+postgresql://user:pass@host:5432/app"   --memory-service  "memorybank://projects/p/locations/us?store=mybank"   --artifact-service "gcs://my-bucket/adk"   --plugin python:examples.redis_memory_plugin
```

## URL Formats
- `python:package.module:Class?kw=v&flag=true` → import and instantiate class/callable with query params.
- `inmemory:` → in-memory implementations (session/memory/artifact) **if ADK is installed**.
- `db+postgresql://...`, `db+mysql://...`, `db+sqlite://...` → `DatabaseSessionService` (session).
- `gcs://bucket/prefix?param=...` → `GcsArtifactService` (artifact).
- `memorybank://...?...`, `rag://...?...` → Vertex memory services (memory).

If the corresponding ADK extra is missing, `load_service` raises a clear `ValueError` (actionable message).

## Precedence Rules
1. Explicit instances passed to `get_fast_api_app`.
2. URL parameters (`*_service_url`).
3. In-memory defaults if available (when ADK is installed).
4. Otherwise `None` (callers can validate or fail fast).

## Error Handling
- Unknown kind/scheme → `ValueError("Unsupported <kind> service URL ...")`.
- Missing ADK extras → `ValueError` suggesting what to install.
- `python:` targets must be a class or callable to accept query params; otherwise an error is raised.

## Security
- `python:` imports execute code during construction. Use in trusted environments only.
- The CLI is intended for local development and single‑tenant scenarios.

## Minimal Integration Path into ADK (later)
1. Copy the `service_loader.py` into `google/adk/cli/` (or depend on this package).
2. Extend ADK’s `get_fast_api_app`/runner to accept `*_service_url` arguments.
3. Use the loader to resolve services with the **same precedence** as above.
4. (Optional) Add CLI flags mirroring `adk-webx`.

This keeps the blast radius tiny and preserves backward compatibility (legacy flags remain).

## Future Work (non-blocking)
- Config file support: `adk-webx --config services.toml`.
- Entry-point based plugin discovery.
- Multiple memory providers via a composite service.
- Better typing stubs for service interfaces.
