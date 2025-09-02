# Chapter 7: Custom ADK Runtime with PostgreSQL Persistence

This chapter implements a production-grade ADK runtime with local PostgreSQL persistence, providing an alternative to Google Cloud services while maintaining full ADK compatibility.

## Overview

Build a custom ADK runtime that provides:
- Local PostgreSQL database storage
- Full ADK service interface compliance  
- Event-driven asynchronous execution
- State persistence and memory management
- Development and production deployment options

## Architecture

```
textbook-adk-ch07-runtime/
├── adk_runtime/              # Main runtime package
│   ├── __init__.py
│   ├── services/             # Core ADK services
│   │   ├── __init__.py
│   │   ├── session_service.py    # PostgreSQL SessionService
│   │   ├── artifact_service.py   # Binary data storage
│   │   └── memory_service.py     # Semantic memory with pgvector
│   ├── database/             # Database layer
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── migrations/       # Database schema migrations
│   │   └── connection.py     # Connection management
│   ├── runtime/              # Core runtime logic  
│   │   ├── __init__.py
│   │   ├── runner.py         # Event loop and orchestration
│   │   └── events.py         # Event handling
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── logging.py        # Logging setup
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data
├── examples/                 # Example usage
│   ├── basic_agent.py        # Simple agent example
│   └── persistent_chat.py    # Persistent conversation demo
├── docker/                   # Development environment
│   ├── docker-compose.yml    # PostgreSQL + development setup
│   └── Dockerfile            # Runtime container
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Key Features

### PostgreSQL-Backed Services
- **SessionService**: JSONB state storage with full transaction support
- **ArtifactService**: Binary data management with file system backing
- **MemoryService**: Vector storage using pgvector extension

### ADK Compliance
- Event-driven execution model
- State commitment semantics
- Cooperative yield/pause/resume cycles
- Full compatibility with existing ADK agents

### Development Tools
- Docker Compose for local PostgreSQL
- Database migration management
- Comprehensive testing suite
- Example agents and usage patterns

## Prerequisites

- **Python 3.11+**
- **Docker Desktop** - Must be running for local PostgreSQL containers
- **Make** - For development commands (or run commands manually)
- **API Keys** - OpenAI, Anthropic, or Google for agent models (optional for database layer)

## Quick Start

⚠️  **Important**: Make sure Docker Desktop is running before starting!

```bash
# Complete development setup
make dev-setup

# Or step by step:
make setup           # Install dependencies  
make dev-up          # Start PostgreSQL containers (requires Docker)
make migrate         # Run database migrations
make test            # Verify everything works

# Run database setup example
python examples/setup_database.py
```

### Manual Setup (without Make)

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL containers (Docker Desktop must be running)
docker-compose -f docker/docker-compose.yml up -d

# Wait for containers to start, then run migrations
sleep 10
python examples/setup_database.py
```

## Learning Objectives

By completing this chapter, you'll understand:

- **Custom Runtime Development**: Building production-grade ADK runtimes
- **Database Integration**: PostgreSQL with JSONB and vector extensions
- **Event Sourcing**: Implementing audit trails and state recovery
- **Service Architecture**: Designing modular, testable service layers
- **Production Deployment**: Docker, migrations, monitoring, and scaling

## Status

🚧 **In Development** - This chapter is currently being implemented on the `feature/postgresql-runtime` branch.

## Next Steps

1. Implement core database models and migrations
2. Build PostgreSQL-backed service implementations
3. Create event-driven runner and orchestration logic
4. Add comprehensive testing and examples
5. Document deployment and operational considerations