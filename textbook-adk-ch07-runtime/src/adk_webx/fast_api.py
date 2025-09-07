"""
FastAPI app factory with pluggable runtime services (standalone).

- Resolves session/memory/artifact using URL strings or explicit instances.
- Exposes resolved services on `app.state`.
- Serves ADK web UI frontend assets for debugging interface.
- Does not depend on ADK internals beyond optional service classes for defaults.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional, Any

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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
    app.state.agent_dir = agent_dir  # type: ignore
    app.state.session_service = session_service  # type: ignore
    app.state.memory_service = memory_service  # type: ignore
    app.state.artifact_service = artifact_service  # type: ignore
    app.state.extra_kwargs = kwargs  # type: ignore

    @app.get("/healthz")
    def health():
        return {"ok": True}

    @app.get("/list-apps")
    def list_apps(relative_path: str = "./"):
        """List available agents/apps in the specified directory."""
        try:
            agents = []

            # If agent_dir is a specific agent, return it as the single app
            if agent_dir.exists():
                has_agent_py = (agent_dir / "agent.py").exists()
                has_yaml = any(agent_dir.glob("*.yaml")) or any(agent_dir.glob("*.yml"))

                if has_agent_py or has_yaml:
                    agents.append(agent_dir.name)
                else:
                    # Look for agent directories within this directory
                    for item in agent_dir.iterdir():
                        if item.is_dir():
                            has_agent_py = (item / "agent.py").exists()
                            has_yaml = any(item.glob("*.yaml")) or any(
                                item.glob("*.yml")
                            )

                            if has_agent_py or has_yaml:
                                agents.append(item.name)

            print(f"✅ Found {len(agents)} agents: {agents}")
            return agents
        except Exception as e:
            print(f"❌ Error listing agents: {e}")
            return []

    # Find ADK browser assets directory
    try:
        # Try to find the ADK CLI module and locate browser assets
        import google.adk.cli

        adk_cli_path = Path(google.adk.cli.__file__).parent
        browser_assets_dir = adk_cli_path / "browser"

        if browser_assets_dir.exists() and (browser_assets_dir / "index.html").exists():
            # Set up MIME types for JavaScript files
            import mimetypes

            mimetypes.add_type("application/javascript", ".js", True)
            mimetypes.add_type("text/javascript", ".js", True)

            # Redirect root to dev UI
            @app.get("/")
            async def redirect_root_to_dev_ui():
                return RedirectResponse("/dev-ui/")

            @app.get("/dev-ui")
            async def redirect_dev_ui_add_slash():
                return RedirectResponse("/dev-ui/")

            # Mount static assets
            app.mount(
                "/dev-ui/",
                StaticFiles(
                    directory=str(browser_assets_dir), html=True, follow_symlink=True
                ),
                name="static",
            )
            print(f"✅ Mounted ADK web UI assets from: {browser_assets_dir}")
        else:
            print(f"❌ ADK browser assets not found at: {browser_assets_dir}")
    except Exception as e:
        print(f"❌ Could not locate ADK browser assets: {e}")
        # If we can't find browser assets, just continue without them
        pass

    return app
