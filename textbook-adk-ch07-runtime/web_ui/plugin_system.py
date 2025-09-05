#!/usr/bin/env python3
"""
ADK Web Plugin System

A plugin system that allows injecting custom services into ADK's web interface.
This enables custom database backends, storage solutions, and other service overrides
while maintaining compatibility with ADK's standard web UI.
"""

import asyncio
import importlib.util
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.runners import Runner
    from google.adk.sessions import BaseSessionService
    from google.adk.memory import BaseMemoryService
    from google.adk.artifacts import BaseArtifactService

logger = logging.getLogger(__name__)


class ADKWebPlugin(ABC):
    """
    Base class for ADK Web plugins.
    
    Plugins can provide custom services that override ADK's default implementations.
    This enables features like PostgreSQL backends, custom storage solutions, etc.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name for identification."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this plugin provides."""
        pass
    
    async def initialize(self) -> None:
        """
        Initialize the plugin.
        Called once when the plugin is loaded.
        """
        pass
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        Called when the web server is stopping.
        """
        pass
    
    def get_session_service(self) -> Optional["BaseSessionService"]:
        """
        Return a custom session service implementation.
        Return None to use ADK's default.
        """
        return None
    
    def get_memory_service(self) -> Optional["BaseMemoryService"]:
        """
        Return a custom memory service implementation.
        Return None to use ADK's default.
        """
        return None
    
    def get_artifact_service(self) -> Optional["BaseArtifactService"]:
        """
        Return a custom artifact service implementation.
        Return None to use ADK's default.
        """
        return None
    
    def get_runner_factory(self) -> Optional[callable]:
        """
        Return a custom runner factory function.
        Function signature: async def create_runner(agent, app_name, **kwargs) -> Runner
        Return None to use ADK's default runner creation.
        """
        return None
    
    def get_custom_routes(self) -> Dict[str, Any]:
        """
        Return custom FastAPI routes to add to the web interface.
        Format: {"/custom/route": {"handler": async_function, "methods": ["GET", "POST"]}}
        """
        return {}
    
    def get_static_files(self) -> Optional[Path]:
        """
        Return path to static files directory for custom UI components.
        Return None if no custom static files.
        """
        return None
    
    def get_templates(self) -> Optional[Path]:
        """
        Return path to custom Jinja2 templates directory.
        Return None if no custom templates.
        """
        return None


class PluginManager:
    """
    Manages ADK Web plugins and service injection.
    """
    
    def __init__(self):
        self.plugins: Dict[str, ADKWebPlugin] = {}
        self._initialized = False
        
    async def load_plugin(self, plugin_path: Path) -> None:
        """
        Load a plugin from a Python file.
        
        Args:
            plugin_path: Path to the plugin file
        """
        try:
            plugin_name = plugin_path.stem
            
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load plugin spec from {plugin_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a plugin class or factory function
            plugin_instance = None
            
            # Try to find a class that inherits from ADKWebPlugin
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, ADKWebPlugin) and 
                    attr != ADKWebPlugin):
                    plugin_instance = attr()
                    break
            
            # Try to find a create_plugin factory function
            if plugin_instance is None and hasattr(module, 'create_plugin'):
                plugin_instance = module.create_plugin()
            
            if plugin_instance is None:
                raise ValueError(f"No valid plugin found in {plugin_path}")
            
            if not isinstance(plugin_instance, ADKWebPlugin):
                raise ValueError(f"Plugin must inherit from ADKWebPlugin")
            
            # Initialize the plugin
            await plugin_instance.initialize()
            
            self.plugins[plugin_instance.name] = plugin_instance
            logger.info(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            raise
    
    async def load_plugins_from_directory(self, plugins_dir: Path) -> None:
        """
        Load all plugins from a directory.
        
        Args:
            plugins_dir: Directory containing plugin files
        """
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory does not exist: {plugins_dir}")
            return
        
        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip private files
            
            try:
                await self.load_plugin(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    async def initialize_all(self) -> None:
        """Initialize all loaded plugins."""
        for plugin in self.plugins.values():
            try:
                await plugin.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin.name}: {e}")
        
        self._initialized = True
        logger.info(f"Initialized {len(self.plugins)} plugins")
    
    async def shutdown_all(self) -> None:
        """Shutdown all loaded plugins."""
        for plugin in self.plugins.values():
            try:
                await plugin.shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown plugin {plugin.name}: {e}")
        
        self._initialized = False
        logger.info("Shutdown all plugins")
    
    def get_active_plugins(self) -> Dict[str, ADKWebPlugin]:
        """Get all active plugins."""
        return self.plugins.copy()
    
    def get_service_overrides(self) -> Dict[str, Any]:
        """
        Get service overrides from all plugins.
        Later plugins take precedence over earlier ones.
        """
        services = {}
        
        for plugin in self.plugins.values():
            session_service = plugin.get_session_service()
            if session_service is not None:
                services["session_service"] = session_service
                logger.info(f"Using session service from plugin: {plugin.name}")
            
            memory_service = plugin.get_memory_service()
            if memory_service is not None:
                services["memory_service"] = memory_service
                logger.info(f"Using memory service from plugin: {plugin.name}")
            
            artifact_service = plugin.get_artifact_service()
            if artifact_service is not None:
                services["artifact_service"] = artifact_service
                logger.info(f"Using artifact service from plugin: {plugin.name}")
            
            runner_factory = plugin.get_runner_factory()
            if runner_factory is not None:
                services["runner_factory"] = runner_factory
                logger.info(f"Using runner factory from plugin: {plugin.name}")
        
        return services
    
    def get_custom_routes(self) -> Dict[str, Any]:
        """Get all custom routes from plugins."""
        routes = {}
        
        for plugin in self.plugins.values():
            plugin_routes = plugin.get_custom_routes()
            for route, config in plugin_routes.items():
                if route in routes:
                    logger.warning(f"Route {route} already exists, overriding with plugin {plugin.name}")
                routes[route] = {
                    **config,
                    "plugin": plugin.name
                }
        
        return routes
    
    def get_static_directories(self) -> Dict[str, Path]:
        """Get static file directories from all plugins."""
        static_dirs = {}
        
        for plugin in self.plugins.values():
            static_dir = plugin.get_static_files()
            if static_dir and static_dir.exists():
                static_dirs[plugin.name] = static_dir
        
        return static_dirs
    
    def get_template_directories(self) -> list[Path]:
        """Get template directories from all plugins."""
        template_dirs = []
        
        for plugin in self.plugins.values():
            template_dir = plugin.get_templates()
            if template_dir and template_dir.exists():
                template_dirs.append(template_dir)
        
        return template_dirs


# Global plugin manager instance
plugin_manager = PluginManager()


async def initialize_plugin_system(plugins_dir: Optional[Path] = None) -> PluginManager:
    """
    Initialize the plugin system.
    
    Args:
        plugins_dir: Directory containing plugins (defaults to ./plugins)
    
    Returns:
        The initialized plugin manager
    """
    if plugins_dir is None:
        plugins_dir = Path("./plugins")
    
    await plugin_manager.load_plugins_from_directory(plugins_dir)
    await plugin_manager.initialize_all()
    
    return plugin_manager