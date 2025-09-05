#!/usr/bin/env python3
"""
Enhanced ADK Web Server with Plugin System

This is a modified version of ADK's web interface that supports plugins
for injecting custom services. It demonstrates how to integrate our PostgreSQL
services into the web UI through the plugin architecture.

Usage:
    python web_ui/adk_web_with_plugins.py postgres_chat_agent
    
Then open: http://127.0.0.1:8000
"""

import asyncio
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

# Module imports configured via pyproject.toml
from web_ui.plugin_system import initialize_plugin_system, plugin_manager

logger = logging.getLogger(__name__)


class PluginAwareADKWeb:
    """
    Enhanced ADK Web server that integrates with the plugin system.
    
    This server loads plugins and uses them to override ADK's default services,
    enabling custom database backends and other service implementations.
    """

    def __init__(self, agent_path: str, plugins_dir: Path | None = None):
        self.agent_path = agent_path
        self.plugins_dir = plugins_dir or Path("./web_ui/plugins")
        self.app = FastAPI(title="ADK Web with Plugin Support", version="1.0.0")
        self.runner = None
        self._setup_routes()

    async def initialize(self):
        """Initialize the web server and plugin system."""
        try:
            logger.info("🚀 Initializing ADK Web server with plugin support...")

            # Initialize plugin system
            await initialize_plugin_system(self.plugins_dir)
            logger.info(f"✅ Loaded {len(plugin_manager.get_active_plugins())} plugins")

            # Load the agent
            await self._load_agent()

            # Setup plugin routes
            self._setup_plugin_routes()

            logger.info("✅ ADK Web server with plugins ready!")

        except Exception as e:
            logger.error(f"❌ Failed to initialize ADK Web server: {e}")
            raise

    async def _load_agent(self):
        """Load the agent and create runner with plugin services."""
        try:
            # Import the agent module (configured via pyproject.toml)

            # Try to import the agent
            if Path(self.agent_path, "agent.py").exists():
                from postgres_chat_agent.agent import root_agent as agent
            else:
                raise ImportError(f"No agent.py found in {self.agent_path}")

            # Get service overrides from plugins
            service_overrides = plugin_manager.get_service_overrides()

            if "runner_factory" in service_overrides:
                # Use plugin's runner factory
                logger.info("🔌 Using plugin runner factory")
                runner_factory = service_overrides["runner_factory"]
                self.runner = await runner_factory(agent, self.agent_path)
            else:
                # Use default runner creation
                logger.info("📦 Using default runner creation")
                from google.adk.runners import Runner

                # Apply service overrides if available
                runner_kwargs = {}
                if "session_service" in service_overrides:
                    runner_kwargs["session_service"] = service_overrides["session_service"]
                if "memory_service" in service_overrides:
                    runner_kwargs["memory_service"] = service_overrides["memory_service"]
                if "artifact_service" in service_overrides:
                    runner_kwargs["artifact_service"] = service_overrides["artifact_service"]

                self.runner = Runner(
                    agent=agent,
                    app_name=self.agent_path,
                    **runner_kwargs
                )

            logger.info("✅ Agent loaded and runner created with plugin services")

        except Exception as e:
            logger.error(f"❌ Failed to load agent: {e}")
            raise

    def _setup_routes(self):
        """Setup basic web UI routes."""

        @self.app.get("/")
        async def root():
            """Main chat interface."""
            return {
                "message": "ADK Web with Plugin Support",
                "agent_path": self.agent_path,
                "plugins": list(plugin_manager.get_active_plugins().keys()),
                "services": list(plugin_manager.get_service_overrides().keys())
            }

        @self.app.post("/api/chat")
        async def chat(message: dict):
            """Handle chat messages through the runner."""
            if not self.runner:
                raise HTTPException(status_code=500, detail="Runner not initialized")

            try:
                # Extract message content
                user_message = message.get("message", "")
                session_id = message.get("session_id", "web-session")
                user_id = message.get("user_id", "web-user")

                logger.info(f"💬 Processing chat message: {user_message[:50]}...")

                # Create content for the runner
                from google.genai import types
                content = types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)]
                )

                # Run through our plugin-enhanced runner
                events = []
                async for event in self.runner.run_async(
                    new_message=content,
                    user_id=user_id,
                    session_id=session_id
                ):
                    events.append(event)

                # Extract response text
                response_text = ""
                for event in events:
                    if event.content and event.content.role == "assistant":
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text

                return {
                    "response": response_text,
                    "session_id": session_id,
                    "service_info": {
                        "using_postgresql": "postgresql_backend" in plugin_manager.get_active_plugins(),
                        "services": list(plugin_manager.get_service_overrides().keys())
                    }
                }

            except Exception as e:
                logger.error(f"❌ Chat processing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/status")
        async def status():
            """Get server and plugin status."""
            return {
                "status": "running",
                "agent_path": self.agent_path,
                "plugins": {
                    name: {
                        "version": plugin.version,
                        "description": plugin.description
                    }
                    for name, plugin in plugin_manager.get_active_plugins().items()
                },
                "services": list(plugin_manager.get_service_overrides().keys())
            }

    def _setup_plugin_routes(self):
        """Setup routes provided by plugins."""
        # Add custom routes from plugins
        custom_routes = plugin_manager.get_custom_routes()
        for route_path, route_config in custom_routes.items():
            handler = route_config["handler"]
            methods = route_config.get("methods", ["GET"])
            plugin_name = route_config.get("plugin", "unknown")

            logger.info(f"📡 Adding plugin route: {route_path} [{', '.join(methods)}] from {plugin_name}")

            # Add the route to FastAPI
            for method in methods:
                if method.upper() == "GET":
                    self.app.get(route_path)(handler)
                elif method.upper() == "POST":
                    self.app.post(route_path)(handler)
                # Add other methods as needed

        # Mount static files from plugins
        static_dirs = plugin_manager.get_static_directories()
        for plugin_name, static_dir in static_dirs.items():
            mount_path = f"/static/{plugin_name}"
            logger.info(f"📁 Mounting static files: {mount_path} -> {static_dir}")
            self.app.mount(mount_path, StaticFiles(directory=str(static_dir)), name=f"static_{plugin_name}")

    async def shutdown(self):
        """Shutdown the web server and plugins."""
        try:
            logger.info("🔌 Shutting down ADK Web server...")
            await plugin_manager.shutdown_all()
            logger.info("✅ ADK Web server shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


async def run_adk_web_with_plugins(agent_path: str, host: str = "127.0.0.1", port: int = 8000):
    """
    Run the ADK web server with plugin support.
    
    Args:
        agent_path: Path to the agent to load
        host: Host to bind to
        port: Port to bind to
    """
    web_server = PluginAwareADKWeb(agent_path)

    try:
        # Initialize the server and plugins
        await web_server.initialize()

        # Create uvicorn config
        config = uvicorn.Config(
            web_server.app,
            host=host,
            port=port,
            log_level="info"
        )

        # Start the server
        server = uvicorn.Server(config)

        logger.info(f"🌐 ADK Web server starting on http://{host}:{port}")
        logger.info("📁 Features enabled:")
        logger.info("  • Plugin system for service injection")
        logger.info("  • PostgreSQL backend services")
        logger.info("  • Hybrid artifact storage")
        logger.info("  • Event sourcing and memory indexing")
        logger.info("🚀 Open your browser to start chatting!")

        await server.serve()

    except KeyboardInterrupt:
        logger.info("⏹️ Shutting down server...")
    finally:
        await web_server.shutdown()


async def main():
    """Main entry point for the enhanced ADK web server."""
    import sys

    if len(sys.argv) < 2:
        logger.error("Usage: python adk_web_with_plugins.py <agent_path>")
        sys.exit(1)

    agent_path = sys.argv[1]

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run the web server
    await run_adk_web_with_plugins(agent_path)


if __name__ == "__main__":
    asyncio.run(main())
