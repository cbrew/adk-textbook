# PostgreSQL Web UI Integration

This document explains how to run the ADK Web UI with PostgreSQL-backed services using the plugin system from Chapter 7.

## Overview

The PostgreSQL Web UI integration provides:
- **Session persistence** using PostgreSQL database
- **Memory service** with vector embeddings for semantic search
- **Artifact storage** with hybrid database + filesystem approach
- **Web UI plugin system** for flexible service configuration

## Prerequisites

### 1. PostgreSQL Services
Ensure PostgreSQL services are running:

```bash
# Start PostgreSQL containers
make dev-up

# Check services are running
make status

# Apply database migrations
make migrate
```

This starts two PostgreSQL instances:
- **Port 5432**: Main database for sessions and artifacts
- **Port 5433**: Vector database for memory/embeddings

### 2. Environment Configuration
Ensure your `.env` file contains:

```bash
# Database Configuration
DATABASE_URL=postgresql://adk_user:adk_password@localhost:5432/adk_runtime
DATABASE_VECTOR_URL=postgresql://adk_user:adk_password@localhost:5433/adk_runtime

# Runtime Configuration
ARTIFACT_STORAGE_PATH=./artifacts
MAX_SESSION_HISTORY=1000
MEMORY_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 3. Dependencies
The system will automatically install the plugin system, but you can install manually:

```bash
cd adk_web_ui
pip install -e .
```

## Running the Web UI

### Method 1: Shell Script (Unix/macOS/Linux)

```bash
# Basic usage with default postgres_chat_agent
./run_postgres_web_ui.sh

# Specify different agent directory
./run_postgres_web_ui.sh my_agent

# Custom host and port
./run_postgres_web_ui.sh postgres_chat_agent --host 0.0.0.0 --port 8080
```

### Method 2: Python Script (Cross-platform)

```bash
# Basic usage
python run_postgres_web_ui.py

# With custom configuration
python run_postgres_web_ui.py postgres_chat_agent --host 127.0.0.1 --port 8000

# Help and options
python run_postgres_web_ui.py --help
```

### Method 3: Direct CLI (Advanced)

After installing the plugin system:

```bash
adk-webx \
  --agent-dir postgres_chat_agent \
  --session-service "postgres-runtime:" \
  --memory-service "postgres-runtime:" \
  --artifact-service "postgres-runtime:" \
  --plugin python:examples.postgres_runtime_plugin \
  --host 127.0.0.1 \
  --port 8000
```

## What Happens During Startup

1. **Prerequisites Check**: Verifies PostgreSQL connectivity on ports 5432 and 5433
2. **Environment Loading**: Reads database configuration from `.env`
3. **Plugin Installation**: Installs `adk-service-plugins` in development mode
4. **Service Registration**: Registers PostgreSQL services via plugin system
5. **Web Server Launch**: Starts FastAPI server with configured services

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if services are running
make status

# Restart services if needed
make dev-down && make dev-up

# Check database connectivity
psql -h localhost -p 5432 -U adk_user -d adk_runtime
```

### Plugin System Issues

```bash
# Reinstall plugin system
cd adk_web_ui && pip install -e . --force-reinstall

# Check adk-webx command is available
which adk-webx
```

### Agent Directory Issues

```bash
# List available agents
ls -la | grep -E "(agent\.py|\.yaml)"

# Ensure agent directory exists and contains valid agent files
ls postgres_chat_agent/
```

## Architecture Details

### Service URLs
The plugin system uses these URL schemes:
- `postgres-runtime:` - PostgreSQL-backed services from Chapter 7 runtime

### Plugin Registration
The `postgres_runtime_plugin.py` registers factory functions for:
- **Session Service**: `PostgreSQLSessionService`
- **Memory Service**: `PostgreSQLMemoryService` 
- **Artifact Service**: `PostgreSQLArtifactService`

### Service Sharing
All services share a single `PostgreSQLADKRuntime` instance for:
- Connection pooling efficiency
- Consistent configuration
- Reduced resource usage

## Configuration Options

### Environment Variables
Override default database settings:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=adk_user
export POSTGRES_PASSWORD=adk_password
export POSTGRES_DB=adk_runtime
export ARTIFACT_STORAGE_PATH=./artifacts
```

### Web Server Options
All standard `adk-webx` options are supported:

```bash
--host HOST              # Bind address (default: 127.0.0.1)
--port PORT              # Bind port (default: 8000)
--agent-dir DIR          # Agent directory (default: postgres_chat_agent)
```

## Development

### Testing the Integration

```bash
# Test PostgreSQL services directly
python examples/test_services.py

# Test web UI plugin system
python examples/test_web_plugin_system.py
```

### Adding Custom Services

Create your own plugin following the pattern in `examples/postgres_runtime_plugin.py`:

```python
from adk_service_plugins.service_loader import register_scheme

def my_custom_factory(parsed, kwargs):
    # Your service implementation
    return MyCustomService(**kwargs)

register_scheme("memory", "mycustom", my_custom_factory)
```

## Integration with Standard ADK

This plugin system is designed for easy integration into the main ADK codebase:

1. Copy `service_loader.py` into ADK CLI module
2. Extend ADK's web command with `*_service_url` parameters  
3. Use the same URL resolution precedence logic
4. Maintain backward compatibility with existing flags

The plugin architecture demonstrates how ADK's web UI can be extended with custom service implementations while preserving the clean separation of concerns.