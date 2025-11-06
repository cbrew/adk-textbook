# Chapter 9: Code Execution with MCP

This chapter demonstrates advanced patterns for using the Model Context Protocol (MCP) with code execution, based on [Anthropic's engineering blog post](https://www.anthropic.com/engineering/code-execution-with-mcp).

## Key Concepts

### The Core Problem
When agents connect to numerous MCP servers, two efficiency challenges emerge:
1. **Context Token Consumption**: Tool definitions consume excessive tokens as collections grow
2. **Data Transfer Overhead**: Intermediate results pass repeatedly through the model

### The Solution: Code Execution
Instead of calling tools directly, agents write code to interact with MCP servers. This enables:
- Loading only necessary tool definitions on-demand
- Processing data locally before returning results to the model
- Up to 98.7% reduction in token usage (150,000 → 2,000 tokens)

## Patterns Demonstrated

### 1. Progressive Disclosure
Models navigate and discover tools on-demand rather than loading all definitions upfront.
- `search_tools` capability for finding relevant definitions
- Context conservation through selective loading
- Dynamic tool discovery based on task requirements

### 2. Data Filtering
Process large datasets locally before returning to the model.
- Filter 10,000+ rows locally, return only relevant data
- Transform and aggregate data in the execution environment
- Reduce token consumption dramatically

### 3. Control Flow Efficiency
Implement loops, conditionals, and error handling through code.
- Reduce latency by avoiding tool call chains
- Execute complex workflows in single code blocks
- Handle retries and error recovery locally

### 4. Privacy Preservation
Keep intermediate results in the execution environment.
- Sensitive data stays local by default
- Automatic tokenization before reaching the model
- Controlled data exposure while allowing tool interactions

### 5. State Management and Skills
Persist results and build reusable capabilities.
- Save intermediate results to files
- Build libraries of reusable functions
- Evolve agent capabilities over time

## Agent Implementations

### Basic MCP Code Execution Agent
Located in `mcp_code_agent/`, this demonstrates:
- Python code execution with MCP tool integration
- Progressive tool discovery patterns
- Data filtering and transformation
- State persistence across sessions

### Examples
Located in `examples/`, including:
- `progressive_disclosure.py` - On-demand tool loading demonstration
- `data_filtering.py` - Large dataset processing with local filtering
- `control_flow.py` - Complex workflows with loops and conditionals
- `privacy_demo.py` - Intermediate result handling and tokenization
- `skills_builder.py` - Building reusable code functions

## Running the Demos

### Basic Agent
```bash
# CLI interface
uv run adk run textbook-adk-ch09-mcp-code-execution/mcp_code_agent/

# Web interface
uv run adk web textbook-adk-ch09-mcp-code-execution/mcp_code_agent/
```

### Standalone Examples
```bash
# Progressive disclosure demo
python textbook-adk-ch09-mcp-code-execution/examples/progressive_disclosure.py

# Data filtering demo
python textbook-adk-ch09-mcp-code-execution/examples/data_filtering.py

# Control flow demo
python textbook-adk-ch09-mcp-code-execution/examples/control_flow.py
```

## Key Takeaways

1. **Code execution is more efficient than tool chaining** for complex workflows
2. **Progressive disclosure conserves context** by loading only needed tools
3. **Local data processing** dramatically reduces token consumption
4. **Privacy is enhanced** by keeping intermediate results local
5. **Skills accumulate** as agents build reusable code libraries

## Token Usage Comparison

| Pattern | Traditional Tool Calls | Code Execution | Reduction |
|---------|----------------------|----------------|-----------|
| Large Dataset | 150,000 tokens | 2,000 tokens | 98.7% |
| Tool Discovery | 50,000 tokens | 5,000 tokens | 90% |
| Complex Workflow | 30,000 tokens | 3,000 tokens | 90% |

## Prerequisites

- Python 3.13+
- Agent SDK with code execution support
- MCP server configuration (examples use mock servers for demonstration)

## Architecture

```
textbook-adk-ch09-mcp-code-execution/
├── README.md                          # This file
├── mcp_code_agent/                    # Main agent implementation
│   ├── __init__.py
│   ├── agent.py                       # Agent with code execution
│   ├── config.py                      # Configuration
│   ├── prompts.py                     # System prompts
│   └── tools/
│       ├── __init__.py
│       ├── code_executor.py           # Code execution tool
│       ├── mcp_tools.py               # MCP integration tools
│       └── progressive_discovery.py   # Tool discovery helpers
├── examples/                          # Standalone demonstrations
│   ├── progressive_disclosure.py
│   ├── data_filtering.py
│   ├── control_flow.py
│   ├── privacy_demo.py
│   └── skills_builder.py
└── tests/                             # Test suite
    ├── test_code_executor.py
    ├── test_progressive_disclosure.py
    └── test_data_filtering.py
```

## Learning Objectives

After completing this chapter, you will understand:
- How to implement code execution in ADK agents
- When to use code execution vs direct tool calls
- Patterns for efficient MCP server interaction
- Privacy-preserving data handling techniques
- Building evolving agent capabilities through skills

## References

- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Agent SDK Documentation](https://cloud.google.com/adk)
