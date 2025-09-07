#!/usr/bin/env python3
"""
ADK Web server with PostgreSQL services (copied from ADK cli_tools_click.py).

This is a direct copy of the ADK web command that we can modify to inject
our PostgreSQL services instead of using the broken URL parsing.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import click
import uvicorn
from fastapi import FastAPI


# Copy the exact ADK web command logic
@click.command()
@click.argument(
    "agents_dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
    default=os.getcwd(),
)
@click.option(
    "--host", default="127.0.0.1", help="Optional. The binding host of the server"
)
@click.option("--port", type=int, default=8000, help="Optional. The port of the server")
@click.option(
    "--allow_origins", help="Optional. Any additional origins to allow for CORS."
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose (DEBUG) logging")
@click.option(
    "--log_level",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    default="info",
)
@click.option(
    "--reload/--no-reload", default=False, help="Whether to enable auto reload"
)
@click.option("--trace_to_cloud", is_flag=True, help="Whether to enable cloud trace")
@click.option("--eval_storage_uri", help="The evals storage URI")
@click.option("--session_service_uri", help="The URI of the session service")
@click.option("--artifact_service_uri", help="The URI of the artifact service")
@click.option("--memory_service_uri", help="The URI of the memory service")
def web(
    agents_dir: str,
    host: str = "127.0.0.1",
    port: int = 8000,
    allow_origins: Optional[str] = None,
    verbose: bool = False,
    log_level: str = "info",
    reload: bool = False,
    trace_to_cloud: bool = False,
    eval_storage_uri: Optional[str] = None,
    session_service_uri: Optional[str] = None,
    artifact_service_uri: Optional[str] = None,
    memory_service_uri: Optional[str] = None,
):
    """Starts a FastAPI server with Web UI for agents using PostgreSQL services.

    AGENTS_DIR: The directory of agents, where each sub-directory is a single
    agent, containing at least `__init__.py` and `agent.py` files.
    """

    # Set up logging
    log_level_upper = log_level.upper() if not verbose else "DEBUG"
    logging.basicConfig(level=getattr(logging, log_level_upper))

    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        click.secho(
            f"""
+-----------------------------------------------------------------------------+
| ADK Web Server with PostgreSQL Services                                    |
|                                                                             |
| For local testing, access at http://{host}:{port}.{" " * (29 - len(str(port)))}|
+-----------------------------------------------------------------------------+
""",
            fg="green",
        )
        yield  # Startup is done, now app is running
        click.secho(
            """
+-----------------------------------------------------------------------------+
| ADK Web Server shutting down...                                             |
+-----------------------------------------------------------------------------+
""",
            fg="green",
        )

    # Import the ADK fast_api module
    try:
        from .fast_api import get_fast_api_app
    except ImportError as e:
        click.secho(f"Error importing ADK: {e}", fg="red")
        return

    # Use the standard ADK get_fast_api_app function with our service URIs
    app = get_fast_api_app(
        agents_dir=agents_dir,
        session_service_uri=session_service_uri,
        artifact_service_uri=artifact_service_uri,
        memory_service_uri=memory_service_uri,
        eval_storage_uri=eval_storage_uri,
        allow_origins=allow_origins.split(",") if allow_origins else None,
        web=True,
        trace_to_cloud=trace_to_cloud,
        lifespan=_lifespan,
        a2a=False,
        host=host,
        port=port,
        reload_agents=False,
    )

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
    )

    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    web()
