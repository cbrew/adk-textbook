.
"""
CLI: `adk-webx` — a minimal FastAPI server using pluggable runtime services.
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Optional

import click
import uvicorn

from .fast_api import get_fast_api_app

@click.command("adk-webx")
@click.option("--agent-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True,
              help="Directory containing your agent(s) or config.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Bind host for the HTTP server.")
@click.option("--port", default=8000, show_default=True, type=int, help="Bind port for the HTTP server.")
@click.option("--session-service", default=None,
              help="Session service URL (db+postgresql://…, inmemory:, python:pkg.mod:Class?...)")
@click.option("--memory-service", default=None,
              help="Memory service URL (memorybank://…, rag://…, inmemory:, python:...)")
@click.option("--artifact-service", default=None,
              help="Artifact service URL (gcs://bucket/prefix, inmemory:, python:...)")
@click.option("--plugin", multiple=True,
              help="Optional plugin imports: python:package.module[:Class]?kw=v. Imported for side-effects.")
def web(
    agent_dir: Path,
    host: str,
    port: int,
    session_service: Optional[str],
    memory_service: Optional[str],
    artifact_service: Optional[str],
    plugin: tuple[str, ...],
) -> None:
    # Import optional plugins for side-effects (e.g., register_scheme(...)).
    for p in plugin or ():
        if p.startswith("python:"):
            spec = p[7:]
            mod_name = spec.split(":")[0]
            importlib.import_module(mod_name)

    app = get_fast_api_app(
        agent_dir=agent_dir,
        session_service_url=session_service,
        memory_service_url=memory_service,
        artifact_service_url=artifact_service,
    )

    uvicorn.run(app, host=host, port=port)
