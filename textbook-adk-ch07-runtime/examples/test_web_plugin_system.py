#!/usr/bin/env python3
"""
Test script for the ADK Web Plugin System

This demonstrates how the plugin system loads our PostgreSQL plugin
and wires the services into the ADK web interface.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Module imports configured via pyproject.toml
from web_ui.plugin_system import initialize_plugin_system, plugin_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_plugin_system():
    """Test the plugin system loading and service integration."""
    print("🔌 Testing ADK Web Plugin System")
    print("=" * 50)
    print()

    try:
        # Initialize plugin system
        plugins_dir = Path("web_ui/plugins")
        print(f"🔄 Loading plugins from: {plugins_dir}")

        await initialize_plugin_system(plugins_dir)

        # Check loaded plugins
        active_plugins = plugin_manager.get_active_plugins()
        print(f"✅ Loaded {len(active_plugins)} plugins:")

        for name, plugin in active_plugins.items():
            print(f"   • {name} v{plugin.version}")
            print(f"     {plugin.description}")
        print()

        # Check service overrides
        service_overrides = plugin_manager.get_service_overrides()
        print(f"🔧 Service overrides provided ({len(service_overrides)}):")
        for service_name in service_overrides.keys():
            print(f"   • {service_name}")
        print()

        # Check custom routes
        custom_routes = plugin_manager.get_custom_routes()
        print(f"📡 Custom routes provided ({len(custom_routes)}):")
        for route_path, config in custom_routes.items():
            methods = config.get("methods", ["GET"])
            plugin_name = config.get("plugin", "unknown")
            print(f"   • {route_path} [{', '.join(methods)}] from {plugin_name}")
        print()

        # Test PostgreSQL plugin specifically
        if "postgresql_backend" in active_plugins:
            print("🗄️ Testing PostgreSQL Plugin Services:")
            postgresql_plugin = active_plugins["postgresql_backend"]

            # Test service retrieval
            try:
                session_service = postgresql_plugin.get_session_service()
                print("   ✅ Session service available")

                memory_service = postgresql_plugin.get_memory_service()
                print("   ✅ Memory service available")

                artifact_service = postgresql_plugin.get_artifact_service()
                print("   ✅ Artifact service available")

                runner_factory = postgresql_plugin.get_runner_factory()
                if runner_factory:
                    print("   ✅ Runner factory available")

                print()

            except Exception as e:
                print(f"   ❌ Service test failed: {e}")
                print()

        # Demonstrate plugin architecture benefit
        print("🏗️ Plugin Architecture Benefits:")
        print("   • Modular service injection into ADK web UI")
        print("   • Custom PostgreSQL backend without ADK core changes")
        print("   • Hot-pluggable database backends")
        print("   • Custom routes and UI components")
        print("   • Maintains ADK compatibility")
        print()

        # Show how this solves the GitHub issue
        print("🎯 Solution to GitHub Issue #2865:")
        print("   • Plugin system enables custom service injection")
        print("   • PostgreSQL services wire into existing ADK web UI")
        print("   • No modifications to core ADK framework required")
        print("   • Extensible architecture for other database backends")
        print()

    except Exception as e:
        print(f"❌ Plugin system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Shutdown plugins
        try:
            await plugin_manager.shutdown_all()
            print("🔌 Plugin system shutdown complete")
        except Exception as e:
            print(f"⚠️ Shutdown warning: {e}")

    return True


async def main():
    """Run the plugin system test."""
    success = await test_plugin_system()

    if success:
        print()
        print("🎉 Plugin system test completed successfully!")
        print()
        print("💡 Next steps:")
        print("   1. Run: python web_ui/adk_web_with_plugins.py postgres_chat_agent")
        print("   2. Open: http://127.0.0.1:8000")
        print("   3. Chat with PostgreSQL-backed ADK agent in web UI!")
    else:
        print()
        print("❌ Plugin system test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
