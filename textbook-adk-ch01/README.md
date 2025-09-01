# Chapter 1: Agents Without Code

This chapter introduces the fundamentals of Google's Agent Development Kit (ADK) by building functional agents using only configuration files—no Python coding required.

## Overview

Learn to create AI agents that can:
- Answer academic research questions
- Use Google search tools
- Detect potential homework cheating
- Operate through both CLI and web interfaces

## What You'll Build

1. **Basic Agent** - A simple conversational assistant
2. **Academic Research Advisor** - A specialized agent for academic research queries
3. **Anti-Cheating System** - An agent that detects homework assignment attempts

## Prerequisites

- Python 3.11+
- uv package manager
- Google Cloud account (for API access)
- ADK installed with evaluation extras

## Quick Start

From the project root:

```bash
# Run the basic agent
uv run adk run textbook-adk-ch01/first_agent/

# Launch web interface
uv run adk web textbook-adk-ch01/first_agent/
```

## Key Files

- `first_agent/root_agent.yaml` - Main agent configuration
- `chapter1.md` - Complete tutorial walkthrough
- `first_agent/.env` - API keys and environment variables

## Learning Objectives

By completing this chapter, you'll understand:

- **Agent Architecture**: Core components of ADK agents
- **Configuration-Driven Development**: Building agents without writing code
- **Tool Integration**: Adding external capabilities (Google search)
- **Personification vs. Functionality**: Design philosophy considerations
- **Developer Tools**: Using `adk run` and `adk web` for testing

## Configuration Examples

### Basic Agent
```yaml
name: root_agent
description: A helpful assistant for user questions
instruction: Answer user questions to the best of your knowledge
model: gemini-2.5-flash
```

### Academic Research Agent
```yaml
name: academic_research_advisor
description: A basic support agent for academic researchers
instruction: Concisely answer questions about academic research practices using Google search
model: gemini-2.5-pro
tools:
  - name: google_search
```

## Testing Your Agent

1. **Interactive Testing**: Use `adk web` for rich UI experience
2. **CLI Testing**: Use `adk run` for command-line interaction
3. **Save Test Cases**: Export interactions from web UI for evaluation

## Common Issues

- **Model Authentication**: Ensure Google API keys are properly configured
- **Tool Access**: Verify search tools have appropriate API access
- **Environment Setup**: Check that uv and ADK are correctly installed

## Next Steps

After mastering config-only agents, proceed to Chapter 2 to learn:
- Python-based agent development
- Custom tool creation
- Advanced evaluation techniques
- Production deployment patterns

## Philosophy Notes

This chapter explores the tension between personification of AI agents and their actual capabilities. The academic research focus demonstrates practical applications while the anti-cheating system shows real-world deployment considerations.