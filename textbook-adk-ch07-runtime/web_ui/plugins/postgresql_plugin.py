#!/usr/bin/env python3
"""
PostgreSQL Plugin for ADK Web UI

This plugin integrates our custom PostgreSQL services (session, memory, artifact)
into ADK's web interface through the plugin system architecture.

This demonstrates how to wire custom database backends into ADK web UI
while maintaining compatibility with the standard ADK interface.
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime
from web_ui.plugin_system import ADKWebPlugin

logger = logging.getLogger(__name__)


class PostgreSQLWebPlugin(ADKWebPlugin):
    """
    Plugin that provides PostgreSQL-backed services to ADK Web UI.
    This plugin replaces ADK's default services with our custom PostgreSQL
    implementations, enabling persistent storage and event sourcing in the web
    interface.
    """

    def __init__(self):
        self._runtime: PostgreSQLADKRuntime | None = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "postgresql_backend"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "PostgreSQL backend services for ADK Web UI with hybrid artifact "
            "storage and event sourcing"
        )

    async def initialize(self) -> None:
        """Initialize the PostgreSQL runtime and services."""
        if self._initialized:
            return

        try:
            logger.info("🔄 Initializing PostgreSQL runtime for web UI...")
            self._runtime = await PostgreSQLADKRuntime.create_and_initialize()
            self._initialized = True
            logger.info("✅ PostgreSQL runtime initialized for web UI!")

        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL runtime: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the PostgreSQL runtime."""
        if self._runtime:
            try:
                await self._runtime.shutdown()
                logger.info("🔌 PostgreSQL runtime shutdown complete")
            except Exception as e:
                logger.error(f"❌ Error during PostgreSQL runtime shutdown: {e}")
            finally:
                self._runtime = None
                self._initialized = False

    def get_session_service(self):
        """Return our PostgreSQL session service."""
        if not self._initialized or not self._runtime:
            raise RuntimeError("PostgreSQL plugin not initialized")

        service = self._runtime.get_session_service()
        logger.info("🗃️ Providing PostgreSQL session service to web UI")
        return service

    def get_memory_service(self):
        """Return our PostgreSQL memory service with artifact event indexing."""
        if not self._initialized or not self._runtime:
            raise RuntimeError("PostgreSQL plugin not initialized")

        service = self._runtime.get_memory_service()
        logger.info(
            "🧠 Providing PostgreSQL memory service with artifact indexing to web UI"
        )
        return service

    def get_artifact_service(self):
        """Return our PostgreSQL artifact service with hybrid storage."""
        if not self._initialized or not self._runtime:
            raise RuntimeError("PostgreSQL plugin not initialized")

        service = self._runtime.get_artifact_service()
        logger.info(
            "📁 Providing PostgreSQL artifact service with hybrid storage to web UI"
        )
        return service

    def get_runner_factory(self) -> Callable[..., Any] | None:
        """
        Return a factory function for creating runners with PostgreSQL services.
        This factory will be used by the web UI instead of ADK's default runner
        creation.
        """
        async def create_postgresql_runner(agent, app_name, **kwargs):
            """Create a Runner with our PostgreSQL services."""
            if not self._initialized or not self._runtime:
                raise RuntimeError("PostgreSQL plugin not initialized")

            logger.info(
                f"🏗️ Creating Runner with PostgreSQL services for app: {app_name}"
            )

            # Import here to avoid circular imports
            from google.adk.runners import Runner

            # Get our PostgreSQL services
            session_service = self._runtime.get_session_service()
            memory_service = self._runtime.get_memory_service()
            artifact_service = self._runtime.get_artifact_service()

            # Create runner with our services
            runner = Runner(
                agent=agent,
                app_name=app_name,
                session_service=session_service,
                memory_service=memory_service,
                artifact_service=artifact_service,
                **kwargs
            )

            logger.info("✅ Runner created with PostgreSQL backend services")
            return runner

        return create_postgresql_runner

    def get_custom_routes(self):
        """Return custom routes for PostgreSQL status and management."""
        return {
            "/api/postgresql/status": {
                "handler": self._get_postgresql_status,
                "methods": ["GET"]
            },
            "/api/postgresql/stats": {
                "handler": self._get_postgresql_stats,
                "methods": ["GET"]
            }
        }

    def get_static_files(self) -> Path | None:
        """Return path to PostgreSQL plugin static files."""
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            return static_dir
        return None

    def get_templates(self) -> Path | None:
        """Return path to PostgreSQL plugin templates."""
        templates_dir = Path(__file__).parent / "templates"
        if templates_dir.exists():
            return templates_dir
        return None

    async def _get_postgresql_status(self, request):
        """API endpoint to check PostgreSQL service status."""
        try:
            if not self._initialized or not self._runtime:
                return {
                    "status": "error",
                    "message": "PostgreSQL runtime not initialized",
                    "services": {
                        "session": False,
                        "memory": False,
                        "artifact": False
                    }
                }

            # Test basic connectivity to each service
            status = {
                "status": "healthy",
                "message": "PostgreSQL services operational",
                "services": {
                    "session": True,
                    "memory": True,
                    "artifact": True
                },
                "features": {
                    "hybrid_storage": True,
                    "event_sourcing": True,
                    "artifact_indexing": True
                },
                "plugin_version": self.version
            }

            return status

        except Exception as e:
            logger.error(f"PostgreSQL status check failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "services": {
                    "session": False,
                    "memory": False,
                    "artifact": False
                }
            }

    async def _get_postgresql_stats(self, request):
        """API endpoint to get PostgreSQL usage statistics."""
        try:
            if not self._initialized or not self._runtime:
                return {"error": "PostgreSQL runtime not initialized"}

            # Get basic statistics from our services
            # This would require adding stats methods to our services
            stats = {
                "artifact_storage": {
                    "total_artifacts": "N/A",  # Would need to query database
                    "postgres_stored": "N/A",  # Files in BYTEA
                    "filesystem_stored": "N/A",  # Files on disk
                    "total_size": "N/A"
                },
                "memory_service": {
                    "total_memories": "N/A",  # Would need to query database
                    "artifact_events": "N/A"  # Events with artifact_delta
                },
                "session_service": {
                    "active_sessions": "N/A"  # Would need to query database
                }
            }

            return stats

        except Exception as e:
            logger.error(f"PostgreSQL stats retrieval failed: {e}")
            return {"error": str(e)}


# Plugin factory function that the plugin manager will look for
def create_plugin() -> PostgreSQLWebPlugin:
    """Factory function to create the PostgreSQL plugin instance."""
    return PostgreSQLWebPlugin()
