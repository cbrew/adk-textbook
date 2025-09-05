# How to Run Chapter 7: PostgreSQL Runtime with Event Sourcing

## 🚀 Quick Start (5 minutes)

```bash
# 1. Setup PostgreSQL services
cd textbook-adk-ch07-runtime
make dev-setup

# 2. Run the academic research assistant
python postgres_chat_agent/main.py --interactive
```

## 🎯 Main Applications

### 1. Academic Research Assistant (Recommended) ⭐
**Features**: Event sourcing, persistent memory, academic workflows
```bash
python postgres_chat_agent/main.py --interactive

# Slash commands in chat:
# /memory <query>   - Search research memory
# /save <topic>     - Save discussion to memory  
# /artifacts        - List saved research files
# /session          - Show session info
```

### 2. Comprehensive PostgreSQL Driver Demo
**Features**: All PostgreSQL services, testing, management tools
```bash
python postgres_chat_agent/driver.py --interactive

# Command line options:
python postgres_chat_agent/driver.py --test-memory      # Test memory service
python postgres_chat_agent/driver.py --test-artifacts   # Test artifact service
python postgres_chat_agent/driver.py --list-sessions    # List all sessions
python postgres_chat_agent/driver.py --search-memory "machine learning"
```

### 3. Basic Examples
**Features**: Simple demonstrations of PostgreSQL integration
```bash
# Automated demo
python examples/run_examples.py

# Interactive demo
python examples/run_examples.py --interactive

# Service checks
python examples/run_examples.py --check
```

## 🔧 Development Setup

### Prerequisites
- **Python 3.11+**
- **uv package manager** ([install here](https://docs.astral.sh/uv/))
- **Podman** (`brew install podman` on Mac)

### Setup Commands
```bash
# Complete setup
make dev-setup

# Or step by step:
make setup           # Install Python dependencies
make podman-setup    # Initialize Podman (Mac only)
make dev-up          # Start PostgreSQL containers
make migrate         # Run database migrations
make test            # Verify everything works
```

### Manual Setup
```bash
# Install Podman
brew install podman

# Install dependencies (from textbook root)
cd /path/to/adk-textbook
uv sync

# Start Podman machine (Mac only)
podman machine init --now

# Start PostgreSQL
cd textbook-adk-ch07-runtime/docker
podman compose up -d

# Run migrations
cd .. && python examples/setup_database.py
```

## 🧪 Testing

### Quick Tests
```bash
# Test memory service functionality
python postgres_chat_agent/driver.py --test-memory

# Test artifact service functionality  
python postgres_chat_agent/driver.py --test-artifacts

# Check all services are working
python examples/run_examples.py --check
```

### Full Test Suite
```bash
# Run all tests
make test

# Or manually:
uv run pytest tests/ -v
```

## 🗂️ Management Commands

### Session Management
```bash
# List all persistent sessions
python postgres_chat_agent/driver.py --list-sessions

# Clear all sessions (development only)
python postgres_chat_agent/driver.py --clear-all-sessions
```

### Memory Management
```bash
# Search memory
python postgres_chat_agent/driver.py --search-memory "your search query"

# List all memories
python postgres_chat_agent/driver.py --list-memories
```

### Database Management
```bash
# Check migration status
make status

# Reset database (development only!)
make reset

# Clean up containers
make clean
```

## 🎓 Key Features

### Event Sourcing Implementation
- ✅ **Proper ADK Events**: Uses `Event` objects with `state_delta` actions
- ✅ **Memory Indexing**: Events indexed without content duplication
- ✅ **State Tracking**: Conversation topics and metadata captured
- ✅ **Search Integration**: Both content and state information searchable

### Academic Research Tools
- 🎓 **Academic Focus**: Optimized for professional research workflows
- 💾 **Persistent Memory**: Conversations saved and searchable across sessions
- 📄 **Artifact Management**: Research files and documents storage
- ⚡ **Slash Commands**: Direct access to PostgreSQL services

### PostgreSQL Integration
- 🗃️ **Three Services**: Session, Memory, and Artifact services using PostgreSQL
- 🔍 **Vector Search**: pgvector support for semantic memory
- 📊 **JSONB Storage**: Efficient storage of session state and metadata
- 🔐 **Type Safety**: Full pyright type checking compliance

## 🚫 What NOT to Use

### Limited ADK Integration
```bash
# These DON'T use PostgreSQL services:
uv run adk run postgres_chat_agent   # Uses ADK's default services
uv run adk web postgres_chat_agent   # Uses ADK's default services

# Use these instead for full PostgreSQL integration:
python postgres_chat_agent/main.py           # Uses PostgreSQL services
python postgres_chat_agent/driver.py        # Uses PostgreSQL services
```

## 🆘 Troubleshooting

### Common Issues

**"Podman machine not running"**
```bash
podman machine start
```

**"docker-credential-desktop not found"**
```bash
make podman-setup
```

**Database connection errors**
```bash
# Check containers are running:
podman ps

# Restart PostgreSQL:
make dev-down && make dev-up
```

**Permission errors**
```bash
podman unshare chown 999:999 ~/.local/share/containers/storage/volumes/
```

## 📚 Documentation

- **README.md**: Complete documentation and architecture
- **HOW_TO_RUN.md**: This file - quick start guide
- **postgres_chat_agent/**: Event sourcing implementation
- **examples/**: Basic integration examples
- **tests/**: Test suite and validation

## ✅ Success Criteria

You'll know everything is working when:
1. PostgreSQL containers start without errors
2. Database migrations complete successfully
3. `python postgres_chat_agent/main.py --interactive` starts the chat agent
4. Memory searches return results: `python postgres_chat_agent/driver.py --test-memory`
5. Conversations persist across sessions

**Happy researching!** 🎓