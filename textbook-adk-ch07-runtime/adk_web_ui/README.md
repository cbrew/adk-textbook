
# adk-service-plugins (standalone)

A tiny, **drop-in** package that lets you specify ADK runtime services (session, memory, artifacts) via **URLs** or **python-import strings**, plus a simple `adk-webx` CLI to boot a FastAPI server using those services.

> This is intentionally minimal and meant as a starting point you can place in any directory and `pip install -e .` or add to your PYTHONPATH.

## Install (local dir)
```bash
pip install -e /path/to/adk-service-plugins-pkg
# or just run without installing:
python -m adk_service_plugins.cli --help
```

## CLI quickstart
```bash
adk-webx --agent-dir ./my-agent   --session-service "db+postgresql://user:pass@host:5432/app"   --memory-service  "memorybank://projects/myproj/locations/us-central1?store=mybank"   --artifact-service "gcs://my-bucket/adk"
```

- Use `python:` to load your own classes without a registry:
```bash
adk-webx --memory-service "python:my_pkg.memory:MyMemoryService?region=us&ttl=300"
```

## Library usage
```python
from adk_service_plugins.service_loader import load_service, register_scheme

session = load_service("db+postgresql://user:pass@host/db", "session")
memory  = load_service("inmemory:", "memory")
artifact= load_service("gcs://my-bucket/prefix", "artifact")
```

To wire into your app factory:
```python
from adk_service_plugins.fast_api import get_fast_api_app

app = get_fast_api_app(
    agent_dir=Path("./my-agent"),
    session_service_url="db+sqlite:///./sessions.db",
    memory_service_url="inmemory:",
    artifact_service_url="gcs://bucket/prefix",
)
```

## Extensibility via simple registration
```python
from adk_service_plugins.service_loader import register_scheme

def make_redis_memory(parsed, qs):
    from my_pkg.redis_memory import RedisMemoryService
    return RedisMemoryService(url=parsed.geturl(), **qs)

register_scheme("memory", "redis", make_redis_memory)
```

## Notes
- This package **expects ADK** to be importable for built-in services (e.g., `google.adk.sessions.DatabaseSessionService`). If you don't have those extras installed, `load_service` will raise a clear `ValueError` telling you what's missing.
- The included `get_fast_api_app` is a lightweight factory that resolves services and exposes them on `app.state`. Adjust it to thread services into your own runner if needed.


See also: [DESIGN_NOTE.md](DESIGN_NOTE.md)
