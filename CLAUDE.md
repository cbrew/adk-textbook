# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository hosts a multi-chapter demo-driven textbook for Google's Agent Development Kit (ADK) in the academic research domain. The running theme is evaluation, exploring how to build and evaluate academic research agents.

## Commands

### Development Commands
- **Install dependencies**: `uv add <package>` - Uses uv for fast Python package management
- **Run agent (CLI)**: `uv run adk run <agent_path>` - Run ADK agent in terminal
- **Run agent (Web UI)**: `uv run adk web <agent_path>` - Launch web interface for agent interaction
- **Run evaluations**: `uv run adk eval <test_path>` - Execute evaluation tests

### Testing Commands
- **Run all tests**: `pytest` - Execute pytest test suite
- **Run unit tests**: `pytest tests/unit` - Run unit tests specifically
- **Run evaluation tests**: `pytest eval` - Run agent evaluation tests
- **Test specific chapter**: `pytest textbook-adk-ch01/` or `pytest textbook-adk-ch02/`

### Chapter-Specific Commands

#### Chapter 1 (Config-Only Agents)
- **Run basic agent**: `uv run adk run textbook-adk-ch01/first_agent/`
- **Run academic agent**: `uv run adk web textbook-adk-ch01/first_agent/`

#### Chapter 2 (Python Agents)
- **Run paper finding agent**: `uv run adk run textbook-adk-ch02/paper_finding`
- **Web interface**: `uv run adk web` (then select paper_finding)

#### Chapter 7 (PostgreSQL Runtime)
- **Setup PostgreSQL runtime**: `cd textbook-adk-ch07-runtime && make dev-setup`
- **Start PostgreSQL services**: `cd textbook-adk-ch07-runtime && make dev-up`
- **Run database migrations**: `cd textbook-adk-ch07-runtime && make migrate`
- **Test PostgreSQL services**: `uv run python textbook-adk-ch07-runtime/examples/test_services.py`
- **Run agent examples**: `uv run python textbook-adk-ch07-runtime/examples/run_examples.py`
- **Interactive agent demo**: `uv run python textbook-adk-ch07-runtime/examples/run_examples.py --interactive`
- **Run with ADK CLI**: `cd textbook-adk-ch07-runtime && uv run adk run postgres_chat_agent`
- **Run with ADK Web**: `cd textbook-adk-ch07-runtime && uv run adk web postgres_chat_agent` (then open http://127.0.0.1:8000)
- **Check services status**: `uv run python textbook-adk-ch07-runtime/examples/run_examples.py --check`
- **Check migration status**: `cd textbook-adk-ch07-runtime && make status`
- **Stop services**: `cd textbook-adk-ch07-runtime && make dev-down`

## Architecture Overview

### Project Structure
The repository contains multiple chapters, each demonstrating increasingly complex agent implementations:

- **Chapter 1** (`textbook-adk-ch01/`): Config-only agents using YAML configuration
- **Chapter 2** (`textbook-adk-ch02/`): Python-based agents with custom tools and evaluation
- **Chapter 7** (`textbook-adk-ch07-runtime/`): Custom ADK runtime with PostgreSQL persistence

### ADK Agent Architecture
Agents follow a consistent pattern:
- **Configuration-based agents**: Use YAML files with `root_agent.yaml` as entry point
- **Python agents**: Implement `Agent` class with custom tools, prompts, and callbacks
- **Tools**: Custom functions that extend agent capabilities (search, data management, etc.)
- **Prompts**: Separated instruction and global instruction for agent behavior
- **Callbacks**: Rate limiting, logging, and monitoring hooks

### Chapter 2 Agent Components
The paper finding agent demonstrates production-ready patterns:

```
textbook-adk-ch02/paper_finding/
├── agent.py          # Main Agent configuration
├── config.py         # Configuration management
├── prompts.py        # Agent instructions
├── tools/
│   └── tools.py      # Custom academic tools
└── shared_libraries/
    └── callbacks.py  # Agent lifecycle callbacks
```

### Testing Strategy
- **Unit tests**: Individual component testing in `tests/unit/`
- **Evaluation tests**: End-to-end agent behavior testing in `eval/`
- **Mock tools**: Chapter 2 uses mocked academic APIs for demonstration

### Environment Configuration
- Uses `.env` files for API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- Google Cloud integration requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION
- LiteLLM for model provider abstraction

### Key Development Patterns
- **Tools are mocked**: Academic APIs in Chapter 2 return mock data for demonstration
- **Agent state**: Default user ID ("user123") used for demo purposes
- **Evaluation-driven**: Each chapter includes comprehensive test suites
- **Modular design**: Tools, prompts, and configuration are cleanly separated

### Python Environment
- **Python 3.11+** required (configured in pyproject.toml as ">=3.11")
- **uv package manager** for dependency management
- **pytest** with asyncio support for testing
- **Google ADK[eval]** as core framework with evaluation extras