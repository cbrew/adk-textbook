# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Philosophy

We develop with **small, focused commits** that make incremental progress. Each commit should:
- Address a specific issue or implement a single feature
- Include proper testing and code quality checks
- Have a clear, descriptive commit message
- Leave the codebase in a working state

This approach enables easier debugging, cleaner git history, and better collaboration.

## Project Overview

This repository hosts a multi-chapter demo-driven textbook for Google's Agent Development Kit (ADK) in the academic research domain. The running theme is evaluation, exploring how to build and evaluate academic research agents.

## Core Commands

### Package Management
- **Install dependencies**: `uv add <package>` - Fast Python package management with uv

### Running Agents
- **CLI interface**: `uv run adk run <agent_path>` - Terminal-based agent interaction
- **Web interface**: `uv run adk web <agent_path>` - Browser-based agent interaction

### Testing & Quality Assurance
- **Run all tests**: `pytest` - Execute complete pytest test suite
- **Unit tests**: `pytest tests/unit` - Component-level testing
- **Evaluation tests**: `pytest eval` - End-to-end agent behavior testing
- **Chapter-specific**: `pytest textbook-adk-ch01/` - Test individual chapters
- **Run evaluations**: `uv run adk eval <test_path>` - Execute ADK evaluation framework

### Chapter-Specific Commands

#### Chapter 1: Config-Only Agents
```bash
# Run basic YAML-configured agent
uv run adk run textbook-adk-ch01/first_agent/
uv run adk web textbook-adk-ch01/first_agent/
```

#### Chapter 2: Python-Based Agents
```bash
# Run paper finding agent with custom tools
uv run adk run textbook-adk-ch02/paper_finding
uv run adk web textbook-adk-ch02/paper_finding
```

#### Chapter 6: ADK Runtime Fundamentals
```bash
# FastAPI server with ADK UI Contract compliance
cd textbook-adk-ch06-runtime
python fastapi_starter.py

# Interactive state management demonstrations
python demo_state_delta.py
python demo_enhanced_state.py

# Server-sent events streaming test
python test_sse_client.py

# Run state-aware agents directly
uv run adk run research_state_agent.py
uv run adk run enhanced_research_agent.py
```

#### Chapter 7: PostgreSQL Runtime & Web UI Plugin System
```bash
# Setup and start PostgreSQL services
cd textbook-adk-ch07-runtime
make dev-setup && make dev-up && make migrate

# Test the implementation
python examples/test_services.py
python examples/test_web_plugin_system.py

# Run PostgreSQL-backed agent
uv run adk run postgres_chat_agent

# PostgreSQL Web UI (Plugin System)
./run_postgres_web_ui.sh                    # Shell script launcher
python run_postgres_web_ui.py               # Python launcher  
./run_postgres_web_ui.sh postgres_chat_agent --port 8080  # Custom config

# Service management
make status      # Check service status  
make dev-down    # Stop services
```

## Repository Architecture

### Chapter Structure
The textbook follows a progressive learning approach with increasingly sophisticated implementations:

| Chapter | Focus | Technology Stack |
|---------|-------|------------------|
| **Chapter 1** | Config-only agents | YAML configuration files |
| **Chapter 2** | Python-based agents | Custom tools, evaluation frameworks |
| **Chapter 6** | ADK Runtime fundamentals | FastAPI, state management, UI contracts |
| **Chapter 7** | Database persistence | PostgreSQL runtime, web UI plugins |

### Agent Architecture Patterns

#### Configuration-Based Agents (Chapter 1)
- Entry point: `root_agent.yaml`
- Declarative agent behavior through YAML
- Minimal code, maximum configurability

#### Python Agents (Chapter 2)
```
textbook-adk-ch02/paper_finding/
├── agent.py              # Main Agent class and configuration
├── config.py             # Environment and runtime configuration
├── prompts.py            # Agent instructions and behavior
├── tools/tools.py        # Custom academic research tools
└── shared_libraries/     # Reusable components
    └── callbacks.py      # Agent lifecycle and monitoring
```

#### ADK Runtime Fundamentals (Chapter 6)
```
textbook-adk-ch06-runtime/
├── fastapi_starter.py         # Complete ADK UI Contract implementation
├── adk_ui_contract.md         # Contract documentation and patterns
├── research_state_agent.py    # Basic state-aware agent
├── research_state_tools.py    # Simple state management tools
├── enhanced_research_agent.py # Advanced state management
├── enhanced_research_tools.py # EventActions.state_delta demonstrations
├── demo_state_delta.py        # Interactive state management demos
├── demo_enhanced_state.py     # Advanced state patterns
└── test_sse_client.py         # SSE streaming client
```

#### Database-Backed Agents (Chapter 7)
- Custom ADK runtime with PostgreSQL persistence
- Hybrid artifact storage (BYTEA + filesystem)
- Event sourcing for complete audit trails
- Web UI plugin system for service injection

### Environment & Dependencies
- **Python 3.13+** (enforced in pyproject.toml)
- **uv** for fast package management
- **pytest** with asyncio support for testing
- **Google ADK[eval]** framework with evaluation extras
- Environment variables in `.env` files (API keys, database connections)

## Development Standards

### Code Quality Requirements
- **Type annotations everywhere**: Surface assumptions about variables, functions, and methods
- **Zero tolerance for errors**: Fix issues immediately, investigate root causes
- **Ruff + Pyright**: Run code quality checks before testing, even for smallest changes
- **No sys.path manipulations**: Use pyproject.toml for all import configuration
- **Descriptive language**: No error is "minor" - address all issues completely

### Testing Philosophy
- **No acceptance of failures**: Debug and fix rather than marking "expected"
- **Comprehensive coverage**: Unit tests, integration tests, evaluation tests
- **Mock external dependencies**: Chapter 2 uses mocked academic APIs
- **End-to-end validation**: Each chapter includes complete test suites
- we don't do over general greps in unlikely places to find files. we reason carefully about where things are likely to be
- in ADK tool functions, one must not document the tool_context argument. Make sure this is not done, and put a NOQA annotation to stop ruff from complaining
- and ToolContext arguments have to be called, exactly tool_context, or they don't work