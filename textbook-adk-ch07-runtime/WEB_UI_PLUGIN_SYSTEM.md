# ADK Web UI Plugin System

This implementation provides a solution to [Google ADK Issue #2865](https://github.com/google/adk-python/issues/2865) by creating a plugin system that enables custom service injection into ADK's web interface.

## Problem Solved

The standard `adk web` command doesn't support custom database backends or services. Our PostgreSQL-backed ADK services couldn't be used with the web UI, limiting the system to CLI-only usage.

## Solution Architecture

### Plugin System Components

1. **Base Plugin Class (`ADKWebPlugin`)**
   - Abstract interface for web UI plugins
   - Provides service override methods (session, memory, artifact, runner factory)
   - Supports custom routes, static files, and templates

2. **Plugin Manager (`PluginManager`)**
   - Loads plugins from directory
   - Manages plugin lifecycle (initialize, shutdown)
   - Collects service overrides from all plugins
   - Handles plugin route and static file registration

3. **PostgreSQL Plugin (`PostgreSQLWebPlugin`)**
   - Implements `ADKWebPlugin` interface
   - Wires our `PostgreSQLADKRuntime` services into web UI
   - Provides status and stats API endpoints
   - Enables hybrid artifact storage and event sourcing in web interface

4. **Enhanced Web Server (`PluginAwareADKWeb`)**
   - Modified ADK web server with plugin support
   - Loads plugins at startup
   - Uses plugin services instead of defaults
   - Provides plugin-aware chat API

## Key Features

### Service Injection
- **Session Service**: PostgreSQL-backed session persistence
- **Memory Service**: PostgreSQL memory with artifact event indexing
- **Artifact Service**: Hybrid PostgreSQL BYTEA + filesystem storage
- **Runner Factory**: Custom runner creation with PostgreSQL services

### Web Interface Integration
- Chat API that uses PostgreSQL services transparently
- Status endpoints to monitor PostgreSQL backend health
- Plugin information exposed in API responses
- Maintains full ADK web UI compatibility

### Architecture Benefits
- **No ADK Core Changes**: Plugin system works with existing ADK
- **Hot-Pluggable**: Different database backends via plugins
- **Extensible**: Support for custom routes, static files, templates
- **Modular**: Clean separation between plugin and core web UI

## Usage

### 1. Start PostgreSQL Services
```bash
make dev-up
make migrate
```

### 2. Test Plugin System
```bash
python examples/test_web_plugin_system.py
```

### 3. Run Web UI with PostgreSQL Backend
```bash
python web_ui/adk_web_with_plugins.py postgres_chat_agent
```

### 4. Access Web Interface
Open: http://127.0.0.1:8000

## File Structure

```
web_ui/
├── plugin_system.py           # Core plugin architecture
├── adk_web_with_plugins.py    # Enhanced web server
└── plugins/
    └── postgresql_plugin.py   # PostgreSQL service plugin

examples/
└── test_web_plugin_system.py # Plugin system test
```

## API Endpoints

### Standard ADK Endpoints
- `GET /` - Main interface with plugin information
- `POST /api/chat` - Chat with PostgreSQL-backed agent
- `GET /api/status` - Server and plugin status

### PostgreSQL Plugin Endpoints
- `GET /api/postgresql/status` - PostgreSQL service health
- `GET /api/postgresql/stats` - Usage statistics

## Technical Implementation

### Plugin Loading
```python
# Load plugins from directory
await initialize_plugin_system(plugins_dir)

# Get service overrides
service_overrides = plugin_manager.get_service_overrides()

# Create runner with plugin services
if "runner_factory" in service_overrides:
    runner = await service_overrides["runner_factory"](agent, app_name)
```

### Service Override Pattern
```python
class PostgreSQLWebPlugin(ADKWebPlugin):
    def get_session_service(self):
        return self._runtime.get_session_service()
    
    def get_memory_service(self):
        return self._runtime.get_memory_service()
    
    def get_artifact_service(self):
        return self._runtime.get_artifact_service()
```

### Runner Factory Integration
```python
def get_runner_factory(self):
    async def create_postgresql_runner(agent, app_name, **kwargs):
        return Runner(
            agent=agent,
            app_name=app_name,
            session_service=self._runtime.get_session_service(),
            memory_service=self._runtime.get_memory_service(),
            artifact_service=self._runtime.get_artifact_service(),
            **kwargs
        )
    return create_postgresql_runner
```

## Benefits for Academic Research

### Web-Based Research Workflow
- **Persistent Sessions**: Research conversations saved in PostgreSQL
- **Artifact Management**: Bibliography and research notes via web UI
- **Memory Search**: Semantic search across research history
- **Event Sourcing**: Complete audit trail of research activities

### Professional Features
- **Hybrid Storage**: Efficient handling of small and large research files
- **Cross-Session Continuity**: Resume research projects via web interface
- **Academic Tool Integration**: All PostgreSQL chat agent tools accessible via web
- **Collaborative Potential**: Multi-user research via PostgreSQL backend

## Comparison with Standard ADK Web

| Feature | Standard ADK Web | PostgreSQL Plugin Web |
|---------|-----------------|----------------------|
| Session Persistence | Memory-only | PostgreSQL Database |
| Artifact Storage | Local/Cloud only | Hybrid PostgreSQL+FS |
| Memory Service | Default/Cloud | PostgreSQL with Events |
| Research Continuity | Session-based | Cross-session |
| Event Sourcing | Basic | Full audit trail |
| Custom Backends | Not supported | Plugin architecture |

## Future Extensions

### Additional Plugins
- **Redis Plugin**: In-memory caching backend
- **Cloud Plugin**: Cloud storage integration
- **Analytics Plugin**: Usage analytics and insights
- **Multi-tenant Plugin**: Organizational research management

### Enhanced Features
- **Plugin Hot-Reload**: Dynamic plugin loading/unloading
- **Plugin Configuration**: Runtime plugin configuration
- **Plugin Dependencies**: Plugin dependency management
- **Plugin Marketplace**: Community plugin ecosystem

This plugin system provides a production-ready solution for integrating custom database backends into ADK's web interface, enabling sophisticated academic research workflows while maintaining full compatibility with the existing ADK ecosystem.