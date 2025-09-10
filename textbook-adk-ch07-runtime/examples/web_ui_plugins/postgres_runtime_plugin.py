#!/usr/bin/env python3
"""
PostgreSQL runtime services plugin for ADK web UI.

Registers custom schemes to wire PostgreSQL-based session, memory, and artifact
services from our Chapter 7 runtime into the ADK web UI plugin system.

Usage:
    adk-webx --agent-dir ./postgres_chat_agent \
             --session-service "postgres-runtime:" \
             --memory-service "postgres-runtime:" \
             --artifact-service "postgres-runtime:" \
             --plugin python:examples.postgres_runtime_plugin
"""

import logging
from typing import Any
from urllib.parse import ParseResult

from adk_webx.service_loader import register_scheme

logger = logging.getLogger(__name__)


# Global runtime instance (shared across services)
_runtime_instance = None


def _get_or_create_runtime():
    """Get or create the shared runtime instance (synchronous)."""
    global _runtime_instance
    if _runtime_instance is None:
        try:
            # Import here to avoid import errors if adk_runtime not available
            import asyncio
            import os

            from adk_runtime.database.connection import DatabaseConfig
            from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

            # Create database config from environment
            db_config = DatabaseConfig(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                username=os.getenv("POSTGRES_USER", "adk_user"),
                password=os.getenv("POSTGRES_PASSWORD", "adk_password"),
                database=os.getenv("POSTGRES_DB", "adk_runtime"),
            )

            # Create runtime instance
            _runtime_instance = PostgreSQLADKRuntime(
                database_config=db_config,
                artifact_storage_path=os.getenv("ARTIFACT_STORAGE_PATH", "./artifacts"),
            )

            # Initialize the runtime synchronously
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(_runtime_instance.initialize())
            logger.info("✅ PostgreSQL ADK runtime instance created and initialized")

        except ImportError as e:
            raise ValueError(
                "PostgreSQL ADK runtime not available. "
                "Make sure adk_runtime is installed and accessible."
            ) from e
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL runtime: {e}")
            raise

    return _runtime_instance


def _postgres_session_factory(parsed: ParseResult, kwargs: dict[str, Any]):
    """Factory function for PostgreSQL session service."""
    runtime = _get_or_create_runtime()
    return runtime.get_session_service()


def _postgres_memory_factory(parsed: ParseResult, kwargs: dict[str, Any]):
    """Factory function for PostgreSQL memory service."""
    runtime = _get_or_create_runtime()
    return runtime.get_memory_service()


def _postgres_artifact_factory(parsed: ParseResult, kwargs: dict[str, Any]):
    """Factory function for PostgreSQL artifact service."""
    runtime = _get_or_create_runtime()
    return runtime.get_artifact_service()


# Register the PostgreSQL runtime scheme for all service types
register_scheme("session", "postgres-runtime", _postgres_session_factory)
register_scheme("memory", "postgres-runtime", _postgres_memory_factory)
register_scheme("artifact", "postgres-runtime", _postgres_artifact_factory)

logger.info(
    "🔌 PostgreSQL runtime plugin registered for session, memory, and artifact services"
)
