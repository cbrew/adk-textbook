# Chapter 7: Custom ADK Runtime with PostgreSQL Persistence

This chapter implements a production-grade ADK runtime with local PostgreSQL persistence, providing an alternative to Google Cloud services while maintaining full ADK compatibility.

## 🚀 Quick Start

**Want to jump right in?** Here's the fastest way to get the PostgreSQL Chat Agent running:

```bash
# From the textbook root directory:
cd textbook-adk-ch07-runtime

# Complete setup (requires Podman/Docker):
make dev-setup

# Run the academic research assistant with event sourcing:
python postgres_chat_agent/main.py --interactive

# Try the comprehensive driver demo:
python postgres_chat_agent/driver.py --interactive
```

**Features you'll get immediately:**
- 🎓 Academic research assistant optimized for professional academics  
- 💾 Persistent conversation memory across sessions
- 🔍 Semantic search of research discussions
- 📄 Research artifact storage and management
- ⚡ Event sourcing with proper ADK events and state_delta actions

## Overview

Build a custom ADK runtime that provides:
- Local PostgreSQL database storage
- Full ADK service interface compliance  
- Event-driven asynchronous execution
- State persistence and memory management
- Development and production deployment options

## Architecture

```
adk-textbook/                 # Project root
├── adk_runtime/              # Main runtime package (installed via pyproject.toml)
│   ├── __init__.py
│   ├── services/             # Core ADK services
│   │   ├── __init__.py
│   │   ├── session_service.py    # PostgreSQL SessionService
│   │   ├── artifact_service.py   # Binary data storage
│   │   └── memory_service.py     # Semantic memory with pgvector
│   ├── database/             # Database layer
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── migrations.py     # Database schema migrations
│   │   └── connection.py     # Connection management
│   └── runtime/              # Core runtime logic  
│       ├── __init__.py
│       └── adk_runtime.py    # PostgreSQL ADK runtime implementation
├── textbook-adk-ch07-runtime/ # Chapter 7 content
│   ├── tests/                # Test suite
│   │   ├── unit/             # Unit tests
│   │   ├── integration/      # Integration tests
│   │   └── fixtures/         # Test data
│   ├── examples/             # Example usage
│   │   ├── setup_database.py     # Database setup and testing
│   │   ├── test_services.py      # Service integration tests
│   │   ├── basic_agent.py        # Complete runnable agent example
│   │   ├── run_examples.py       # Easy script to run all examples
│   │   └── persistent_chat_agent/ # ADK YAML agent with PostgreSQL
│   │       ├── root_agent.yaml   # Agent configuration
│   │       └── agent.py          # Tool implementations
│   ├── scripts/              # Utility scripts
│   │   ├── check_migration_status.py  # Check database migration status
│   │   └── reset_database.py     # Reset database (development only)
│   ├── docker/               # Development environment
│   │   └── docker-compose.yml    # PostgreSQL + development setup
│   ├── Makefile             # Development commands
│   └── README.md            # This file
├── pyproject.toml           # Project configuration and dependencies
└── uv.lock                  # Lockfile for reproducible builds
```

## Key Features

### PostgreSQL-Backed Services  
- **SessionService**: JSONB state storage with full transaction support
- **ArtifactService**: Binary data management with file system backing
- **MemoryService**: Semantic memory with pgvector extension support

### ADK Compliance
- Event-driven execution model
- State commitment semantics
- Cooperative yield/pause/resume cycles
- Full compatibility with existing ADK agents

### Development Tools
- Docker Compose V2 for local PostgreSQL
- Database migration management
- Comprehensive testing suite
- Example agents and usage patterns

## Prerequisites

- **Python 3.11+**
- **uv package manager** - Fast Python package installer and resolver ([install here](https://docs.astral.sh/uv/))
- **Podman** - Container engine for local PostgreSQL containers (`brew install podman`)
- **Make** - For development commands (or run commands manually)
- **API Keys** - OpenAI, Anthropic, or Google for agent models (optional for database layer)

## Quick Start

⚠️  **Important**: Make sure Podman is installed and running before starting!

```bash
# Complete development setup
make dev-setup

# Or step by step:
make setup           # Install dependencies with uv
make podman-setup    # Initialize Podman machine (Mac only)
make dev-up          # Start PostgreSQL containers
make migrate         # Run database migrations
make test            # Verify everything works

# Run database setup example (from textbook root)
cd .. && uv run python textbook-adk-ch07-runtime/examples/setup_database.py
```

### Manual Setup (without Make)

```bash
# Install Podman (Mac)
brew install podman

# Install dependencies with uv (from textbook root)
cd /path/to/adk-textbook
uv sync  # This installs the adk_runtime package

# Initialize Podman machine (Mac only)
podman machine init --now

# Start PostgreSQL containers
cd textbook-adk-ch07-runtime/docker && podman compose up -d

# Wait for containers to start, then run migrations
sleep 10
cd .. && uv run python textbook-adk-ch07-runtime/examples/setup_database.py

# Run tests to verify setup
uv run pytest textbook-adk-ch07-runtime/tests/ -v
```

### Development Commands

```bash
make help         # Show all available commands
make setup        # Install dependencies  
make podman-setup # Initialize Podman machine (Mac only)
make dev-up       # Start PostgreSQL containers
make migrate      # Run database migrations
make status       # Check migration status
make test         # Run test suite
make clean        # Clean up containers and data
make reset        # Reset database (development only!)
```

### Podman Installation

**Mac:**
```bash
brew install podman
# Optional: Install podman-compose for better compatibility
pip install podman-compose
```

**Linux:**
See [podman.io](https://podman.io/getting-started/installation) for distribution-specific instructions.

**Note**: The Makefile tries both `podman-compose` and `podman compose` commands for maximum compatibility.

### Troubleshooting

**Error: "docker-credential-desktop: executable file not found"**
This happens when Podman tries to use Docker's credential helper. Fix with:
```bash
make podman-setup  # This creates proper Podman auth config
# OR manually:
mkdir -p ~/.config/containers
echo '{"auths": {}}' > ~/.config/containers/auth.json
```

**Error: "Podman machine not running"**
On Mac, start the Podman machine:
```bash
podman machine start
```

**Permission issues with volumes**
If you see permission errors, try running:
```bash
podman unshare chown 999:999 ~/.local/share/containers/storage/volumes/
```

## Learning Objectives

By completing this chapter, you'll understand:

- **Custom Runtime Development**: Building production-grade ADK runtimes
- **Database Integration**: PostgreSQL with JSONB and vector extensions
- **Event Sourcing**: Implementing audit trails and state recovery
- **Service Architecture**: Designing modular, testable service layers
- **Production Deployment**: Docker, migrations, monitoring, and scaling

## Starting Agents with PostgreSQL Services

Once your PostgreSQL runtime is set up, you can start agents that use the database services for persistence. Here are the key patterns:

### Runnable Examples

The `examples/` directory contains complete, runnable examples:

#### 1. Quick Start - Automated Example
```bash
# From textbook root directory:
uv run python textbook-adk-ch07-runtime/examples/run_examples.py
```

This runs an automated demonstration of PostgreSQL services integration.

#### 2. Interactive Chat Demo
```bash
# Interactive agent with persistent conversations:
uv run python textbook-adk-ch07-runtime/examples/run_examples.py --interactive
```

Features an interactive chat agent that demonstrates:
- Persistent conversation sessions across restarts
- Semantic memory search of past conversations  
- Artifact storage for saving conversations
- Session management and state persistence

#### 3. Direct Agent Example
```bash
# Run the basic agent directly:
uv run python textbook-adk-ch07-runtime/examples/basic_agent.py

# Or interactive mode:
uv run python textbook-adk-ch07-runtime/examples/basic_agent.py --interactive
```

#### 4. Test Tools Integration
```bash
# Test agent tools with PostgreSQL:
uv run python textbook-adk-ch07-runtime/examples/run_examples.py --test-tools
```

#### 5. Service Status Check
```bash
# Verify all services are working:
uv run python textbook-adk-ch07-runtime/examples/run_examples.py --check
```

#### 6. PostgreSQL Chat Agent (Event Sourcing Implementation) ⭐
```bash
# Interactive Academic Research Assistant with PostgreSQL Event Sourcing
cd textbook-adk-ch07-runtime && uv run python postgres_chat_agent/main.py

# Command line options:
python postgres_chat_agent/main.py --interactive          # Interactive chat mode
python postgres_chat_agent/main.py --list-sessions        # List all persistent sessions  
python postgres_chat_agent/main.py --test-memory         # Test memory service functionality
python postgres_chat_agent/main.py --search-memory "ML"  # Search research memory
python postgres_chat_agent/main.py --test-artifacts      # Test artifact service

# Or use the comprehensive driver directly:
python postgres_chat_agent/driver.py --interactive       # Full-featured driver demo
```

**Key Features of the PostgreSQL Chat Agent:**
- ✅ **Event Sourcing Architecture**: Proper ADK events with state_delta actions
- ✅ **Academic Focus**: Research-oriented workflows and memory management
- ✅ **Persistent Memory**: Conversations indexed and searchable across sessions
- ✅ **Slash Commands**: `/memory`, `/save`, `/artifacts`, `/session` for direct service access
- ✅ **State Management**: Session state tracking with conversation topics and metadata
- ✅ **PostgreSQL Integration**: Uses all three custom PostgreSQL services

#### 7. Standard ADK Commands (Limited PostgreSQL Integration)
```bash
# Option B: Standard ADK commands (uses ADK's default services, NOT PostgreSQL)
cd textbook-adk-ch07-runtime && uv run adk run postgres_chat_agent  # Uses ADK defaults
cd textbook-adk-ch07-runtime && uv run adk web postgres_chat_agent   # Uses ADK defaults

# IMPORTANT: Only the Python scripts above use our custom PostgreSQL runtime!
# ADK CLI commands (adk run, adk web) connect their own services, ignoring our custom ones
```

## Event Sourcing Implementation ⭐

The PostgreSQL Chat Agent (`postgres_chat_agent/`) demonstrates a complete **event sourcing architecture** using proper ADK events with state_delta actions:

### Architecture Overview

```python
# Event Creation (postgres_chat_agent/driver.py)
async def _create_conversation_events(self, session, message: str, response: str):
    """Create proper ADK events for user message and agent response with state changes."""
    
    # 1. User message event
    user_event = Event(
        author="user",
        content=types.Content(role="user", parts=[types.Part(text=message)]),
        invocation_id=f"msg_{Event.new_id()}",
        actions=EventActions()  # No actions for user events
    )
    
    # 2. Agent response event with state_delta
    conversation_state = {
        "last_interaction": datetime.now().isoformat(),
        "message_count": len(session.events),
        "conversation_topic": self._extract_topic_from_message(message),
        "agent_response_length": len(response)
    }
    
    agent_event = Event(
        author=self.app_name,
        content=types.Content(role="model", parts=[types.Part(text=response)]),
        invocation_id=f"resp_{Event.new_id()}",
        actions=EventActions(state_delta=conversation_state)  # State changes
    )
```

### Memory Service Event Sourcing

```python
# Memory Indexing (adk_runtime/services/memory_service.py)
async def add_session_to_memory(self, session: "Session") -> None:
    """Creates searchable memory indexes for session events (event sourcing approach)."""
    
    for event in session.events:
        # Create memory index entry that references the event (no content duplication)
        await self._index_event_if_searchable(session, event)

async def _index_event_if_searchable(self, session, event):
    """Create memory index entry for an event if it contains searchable content."""
    
    # Extract keywords and create summary (no full content duplication)
    keywords = self._extract_event_keywords(event)
    content_summary = self._create_event_summary(event)
    
    # Handle state_delta events specially
    if hasattr(event, 'actions') and event.actions and event.actions.state_delta:
        state_info = self._summarize_state_delta(event.actions.state_delta)
        content_summary += f" | State: {state_info}"
        keywords.extend(["state_update", "interaction", "conversation"])
```

### Key Event Sourcing Benefits

- **✅ No Content Duplication**: Memory stores indexes that reference events, not duplicate content
- **✅ Proper ADK Events**: Uses official ADK Event structure with state_delta actions
- **✅ Audit Trail**: Complete history of state changes through events
- **✅ Searchable State**: State information (topics, message counts, timestamps) is indexed
- **✅ Event Classification**: Events classified as `text_message`, `state_update`, etc.
- **✅ Data Integrity**: Single source of truth maintained in event stream

### Testing Event Sourcing

```bash
# Test event creation and indexing
cd textbook-adk-ch07-runtime
python postgres_chat_agent/driver.py --test-memory

# Example output:
# ✅ Created 2 ADK events for conversation
# 📝 Memory indexes created: User message + Agent response with state_delta
# 🔍 Search results show both content and state information
```

### Proper ADK Service Integration

The `postgres_chat_agent` demonstrates the **correct pedagogical approach** for integrating custom PostgreSQL services with ADK:

#### Architecture Overview
```python
from google.adk.runners import Runner

# 1. Initialize PostgreSQL runtime
runtime = await PostgreSQLADKRuntime.create_and_initialize()

# 2. Get service implementations (these extend ADK base classes)
session_service = runtime.get_session_service()    # extends BaseSessionService
memory_service = runtime.get_memory_service()      # extends BaseMemoryService  
artifact_service = runtime.get_artifact_service()  # extends BaseArtifactService

# 3. Wire services into ADK Runner (replaces ADK defaults)
runner = Runner(
    agent=agent,
    app_name="postgres_chat_agent", 
    session_service=session_service,     # Our PostgreSQL implementation
    memory_service=memory_service,       # Our PostgreSQL implementation
    artifact_service=artifact_service,   # Our PostgreSQL implementation
)
```

#### Key Learning Points
- **Proper Integration**: Custom services are wired into ADK's `Runner`, not just used as tools
- **Service Replacement**: Our PostgreSQL services replace ADK's defaults at the infrastructure level
- **Base Class Extension**: Our services extend `BaseSessionService`, `BaseMemoryService`, `BaseArtifactService`
- **True Runtime**: ADK natively uses PostgreSQL for all session/memory/artifact operations

This demonstrates building **custom ADK runtimes** rather than just adding PostgreSQL tools on top of existing services.

### Basic Integration Pattern

For reference, here's the simplified pattern:

### Agent Configuration

For ADK agents using YAML configuration, you can integrate PostgreSQL services by:

1. **Initialize services in agent code:**
```python
# In your agent's __init__ or setup method
from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

class MyAgent:
    def __init__(self):
        self.runtime = None
        self.session_service = None
        self.memory_service = None
        self.artifact_service = None
    
    async def setup(self):
        """Initialize PostgreSQL runtime and services."""
        self.runtime = await PostgreSQLADKRuntime.create_and_initialize()
        self.session_service = self.runtime.get_session_service()
        self.memory_service = self.runtime.get_memory_service()
        self.artifact_service = self.runtime.get_artifact_service()
    
    async def cleanup(self):
        """Shutdown runtime when agent stops."""
        if self.runtime:
            await self.runtime.shutdown()
```

2. **Use services in agent tools:**
```python
async def save_conversation_memory(self, conversation_summary: str):
    """Save conversation to persistent memory."""
    session = await self.session_service.create_session(
        app_name="my_agent",
        user_id=self.user_id,
        state={"summary": conversation_summary}
    )
    
    # Add to semantic memory
    await self.memory_service.add_session_to_memory(session)
    
    return session.id

async def retrieve_relevant_memory(self, query: str):
    """Retrieve relevant past conversations."""
    response = await self.memory_service.search_memory(
        app_name="my_agent",
        user_id=self.user_id,
        query=query
    )
    
    return [memory.content for memory in response.memories]
```

### Development Commands

With PostgreSQL services running, you can use standard ADK commands:

```bash
# Start agent with CLI interface 
uv run adk run postgres_chat_agent

# Start agent with web interface
uv run adk web 

# Run agent evaluations
uv run adk eval path/to/your/tests/
```

### ADK Web UI Integration ✅ **DATABASE COMPATIBILITY ONLY**

The PostgreSQL runtime provides **database schema compatibility** with ADK's built-in web UI, but does not use our custom service implementations:

#### Quick Start with Web UI

```bash
# Use the provided script for easy setup
./scripts/start_web_with_postgres.sh

# Or run manually
uv run adk web postgres_chat_agent \
    --session_service_uri "postgresql://adk_user:adk_password@localhost:5432/adk_runtime" \
    --port 8000
```

#### Integration Status

**Important Distinction:**
- **`adk web` with `--session_service_uri`**: Uses ADK's built-in `DatabaseSessionService`, just pointing to our PostgreSQL database (schema compatible)
- **`python main.py`**: Uses our custom PostgreSQL service implementations with full runtime integration

| Approach | Session Service | Memory Service | Artifact Service |
|----------|----------------|---------------|------------------|
| **ADK Web** | ✅ ADK's DatabaseSessionService → PostgreSQL | ❌ ADK defaults | ❌ ADK defaults |
| **Our main.py** | ✅ Our PostgreSQL SessionService | ✅ Our PostgreSQL MemoryService | ✅ Our PostgreSQL ArtifactService |

#### What Works with ADK Web + PostgreSQL Database

- **Database Schema Compatibility**: PostgreSQL database schema works with ADK's DatabaseSessionService
- **Session Persistence**: ADK web can read/write session data to/from PostgreSQL
- **Basic Web Interface**: Standard ADK web interface functionality operates normally

#### What Does NOT Work

- **Custom Service Integration**: ADK web ignores our PostgreSQL service implementations
- **Memory Service**: ADK web uses default memory service, not our PostgreSQL MemoryService  
- **Artifact Service**: ADK web uses default artifact service, not our PostgreSQL ArtifactService
- **Custom Runtime Features**: PostgreSQL-specific features only available in direct Python execution

#### Technical Implementation

Database schema compatibility achieved through analysis of ADK's `DatabaseSessionService`:
- ✅ Composite primary keys `(app_name, user_id, id)`
- ✅ Events table with required columns  
- ✅ JSONB handling for ADK's `DynamicJSON` type
- ✅ Data migration preserving existing information

#### Technical Details

The database compatibility works through:
- **Shared Database**: Agent runtime and web server use the same PostgreSQL database
- **Schema Compatibility**: Our schema works with ADK's `DatabaseSessionService`
- **Limited Integration**: Only session data is shared; memory and artifact services remain separate

**Database Schema Highlights:**
- `sessions` table: Composite primary key `(app_name, user_id, id)`
- `events` table: All 17 ADK-expected columns with proper data types
- `app_states` & `user_states`: Full support for ADK's state management
- JSONB columns: Compatible with ADK's `DynamicJSON` SQLAlchemy type

#### Scripts

**Unix/Mac:**
```bash
./scripts/start_web_with_postgres.sh
```

**Windows:**
```cmd
scripts\start_web_with_postgres.bat
```

Both scripts:
- Check PostgreSQL connectivity
- Apply required database migrations for ADK compatibility  
- Start the web server pointing to PostgreSQL database
- Enable basic ADK web UI functionality with PostgreSQL storage

### Testing Your Agent

Verify your agent works with PostgreSQL services:

```bash
# Run the service tests to ensure PostgreSQL is working
cd textbook-adk-ch07-runtime
uv run python examples/test_services.py

# Run your agent tests
uv run pytest path/to/your/agent/tests/ -v
```

### Environment Variables

Your agents can use these environment variables for database configuration:

```bash
# Database connection (defaults work with dev setup)
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=adk_runtime
export DB_USER=adk_user
export DB_PASSWORD=adk_password

# Agent configuration
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
```

### Production Deployment

For production deployments:

1. **Use environment-specific database configs:**
```python
from adk_runtime.database.connection import DatabaseConfig

# Production database configuration
config = DatabaseConfig(
    host=os.getenv("PROD_DB_HOST"),
    port=int(os.getenv("PROD_DB_PORT", "5432")),
    database=os.getenv("PROD_DB_NAME"),
    username=os.getenv("PROD_DB_USER"),
    password=os.getenv("PROD_DB_PASSWORD"),
    ssl_require=True  # Enable SSL for production
)

runtime = PostgreSQLADKRuntime(database_config=config)
```

2. **Set up proper database migrations:**
```bash
# Run migrations in production
python textbook-adk-ch07-runtime/examples/setup_database.py
```

3. **Monitor database performance:**
```bash
# Check database status
python textbook-adk-ch07-runtime/scripts/check_migration_status.py
```

## Status

✅ **Complete** - This chapter demonstrates a production-ready ADK runtime with PostgreSQL persistence and event sourcing.

### Completed Features
- ✅ PostgreSQL database schema and migrations
- ✅ SessionService with JSONB state storage  
- ✅ ArtifactService with file system backing
- ✅ MemoryService with pgvector support and event sourcing
- ✅ Development environment with Docker Compose V2
- ✅ Comprehensive testing suite
- ✅ **ADK Web UI integration** with PostgreSQL session service
- ✅ **Event Sourcing Implementation** with proper ADK events and state_delta actions
- ✅ **Academic Research Agent** with persistent memory and slash commands
- ✅ **PostgreSQL Chat Driver** demonstrating complete service integration
- ✅ Automated setup scripts for development and testing

### Key Achievements
- ✅ **Event Sourcing Architecture**: Proper ADK events with state_delta actions for session updates
- ✅ **Memory Service Event Indexing**: No content duplication, references to authoritative events
- ✅ **Academic Research Workflows**: Professional academic tools with persistent research memory
- ✅ **Complete Service Integration**: All three PostgreSQL services (Session, Memory, Artifact) working together
- ✅ **Type Safety**: Full pyright type checking compliance throughout codebase

## Next Steps

1. ✅ ~~Implement core database models and migrations~~
2. ✅ ~~Build PostgreSQL-backed service implementations~~
3. ✅ ~~Create event-driven runner and orchestration logic~~
4. ✅ ~~Add comprehensive agent examples and documentation~~
5. ✅ ~~Document deployment and operational considerations~~
6. ✅ ~~Implement event sourcing architecture with proper ADK events~~

**Chapter 7 is now complete!** 🎉

This implementation provides a fully functional, production-ready ADK runtime with PostgreSQL persistence, event sourcing, and academic research workflows.

### What You've Built

- **Custom ADK Runtime**: PostgreSQL-backed alternative to Google Cloud services
- **Event Sourcing System**: Proper ADK events with state_delta actions and memory indexing
- **Academic Research Tools**: Professional workflows for researchers with persistent memory
- **Production Architecture**: Type-safe, tested, and documented system ready for deployment

### Ready for Production Use

The implementation includes all necessary components for production deployment:
- Database migrations and schema management
- Type-safe service implementations
- Comprehensive test coverage
- Development and deployment documentation
- Event sourcing with audit trails
- Academic-focused user experience