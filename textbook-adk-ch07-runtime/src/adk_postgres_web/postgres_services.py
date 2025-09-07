"""
PostgreSQL service factories for ADK Web UI integration.

Provides factory functions for PostgreSQL-backed session, memory, and artifact
services that can be used with python: URLs in the service_loader system.

Usage:
    adk-postgres-web --session_service_uri "python:adk_postgres_web.postgres_services:create_session_service"
    adk-postgres-web --memory_service_uri "python:adk_postgres_web.postgres_services:create_memory_service"
    adk-postgres-web --artifact_service_uri "python:adk_postgres_web.postgres_services:create_artifact_service"
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Global runtime instance (shared across services)
_runtime_instance = None


def _get_or_create_runtime():
    """Get or create the shared PostgreSQL runtime instance."""
    global _runtime_instance
    if _runtime_instance is None:
        try:
            # Import here to avoid import errors if adk_runtime not available
            import asyncio

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


def create_session_service(**kwargs: Any):
    """Factory function for PostgreSQL session service."""
    runtime = _get_or_create_runtime()
    logger.info("🔗 Created PostgreSQL session service")
    return runtime.get_session_service()


def create_memory_service(**kwargs: Any):
    """Factory function for PostgreSQL memory service."""
    runtime = _get_or_create_runtime()
    logger.info("🧠 Created PostgreSQL memory service")
    return runtime.get_memory_service()


def create_artifact_service(**kwargs: Any):
    """Factory function for PostgreSQL artifact service."""
    runtime = _get_or_create_runtime()
    logger.info("📁 Created PostgreSQL artifact service")
    return runtime.get_artifact_service()
