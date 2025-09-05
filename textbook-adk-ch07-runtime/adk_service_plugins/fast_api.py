
"""
FastAPI app factory with pluggable runtime services (standalone).

- Resolves session/memory/artifact using URL strings or explicit instances.
- Exposes resolved services on `app.state`.
- Does not depend on ADK internals beyond optional service classes for defaults.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from fastapi import FastAPI
from .service_loader import load_service

def _try_import_inmemory():
    sess = mem = art = None
    try:
        from google.adk.sessions import InMemorySessionService  # type: ignore
        sess = InMemorySessionService()
    except Exception:
        pass
    try:
        from google.adk.memory import InMemoryMemoryService  # type: ignore
        mem = InMemoryMemoryService()
    except Exception:
        pass
    try:
        from google.adk.artifacts import InMemoryArtifactService  # type: ignore
        art = InMemoryArtifactService()
    except Exception:
        pass
    return sess, mem, art

def get_fast_api_app(
    *,
    agent_dir: Path,
    # Explicit instances
    session_service: Any | None = None,
    memory_service: Any | None = None,
    artifact_service: Any | None = None,
    # URL-based configuration
    session_service_url: Optional[str] = None,
    memory_service_url: Optional[str] = None,
    artifact_service_url: Optional[str] = None,
    **kwargs: Any,
) -> FastAPI:
    """Construct a FastAPI app and attach resolved services to app.state.*"""
    inm_sess, inm_mem, inm_art = _try_import_inmemory()

    if session_service is None:
        if session_service_url:
            session_service = load_service(session_service_url, "session")
        else:
            session_service = inm_sess

    if memory_service is None:
        if memory_service_url:
            memory_service = load_service(memory_service_url, "memory")
        else:
            memory_service = inm_mem

    if artifact_service is None:
        if artifact_service_url:
            artifact_service = load_service(artifact_service_url, "artifact")
        else:
            artifact_service = inm_art

    app = FastAPI()
    app.state.agent_dir = agent_dir
    app.state.session_service = session_service
    app.state.memory_service = memory_service
    app.state.artifact_service = artifact_service
    app.state.extra_kwargs = kwargs

    @app.get("/healthz")
    def health():
        return {"ok": True}

    return app
