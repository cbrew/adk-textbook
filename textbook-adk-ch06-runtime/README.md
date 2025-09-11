# Chapter 6: ADK Runtime Fundamentals

Learn how to integrate agents with web UIs, implement the ADK UI Contract, and master both simple and advanced state management patterns.

## What You'll Learn

- **ADK UI Contract Implementation**: Build FastAPI servers that are fully compatible with ADK Web UI
- **State Management Patterns**: Master both simple updates and EventActions.state_delta approaches
- **Agent State Visibility**: Understand how agents receive state information and notifications
- **Server-Sent Events**: Implement real-time streaming with proper ADK Event handling
- **External State Mutation**: Enable external systems to modify agent state via REST APIs

## Key Learning Objectives

1. **Runtime Integration**: Connect agents to web UIs using the ADK UI Contract
2. **Event Sourcing**: Understand how ADK maintains audit trails and state consistency
3. **State Management**: Choose between simple tools and EventActions.state_delta for different use cases
4. **External Orchestration**: Enable multi-system agent coordination through state mutations
5. **Production Patterns**: Build scalable, contract-compliant agent systems

## Chapter Structure

### 6.1 - Introduction to ADK Runtime Architecture
- How ADK Runner connects agents to UIs
- Event sourcing and the ADK Event model
- Session, Memory, and Artifact services overview

### 6.2 - ADK UI Contract Implementation
- **fastapi_starter.py** - Complete contract implementation with FastAPI
- Core endpoints: `/run`, `/run_sse`, session management
- Error handling and HTTP status codes
- **adk_ui_contract.md** - Detailed contract documentation

### 6.3 - State Management Fundamentals
- Simple state updates with `tool_context.update_state()`
- **research_state_tools.py** - Basic state management examples
- **research_state_agent.py** - State-aware agent implementation
- State key naming conventions and best practices

### 6.4 - Advanced State Management: EventActions.state_delta
- "The Standard Way" for complex state updates from ADK docs
- **enhanced_research_tools.py** - EventActions.state_delta demonstrations
- **enhanced_research_agent.py** - Agent with both simple and advanced tools
- External state mutation patterns and use cases

### 6.5 - Agent State Visibility and Notifications
- **Critical Discovery**: Agents don't automatically see state changes
- Template variables, tool access, and explicit notifications
- **demo_state_delta.py** - Comprehensive state visibility examples
- **demo_enhanced_state.py** - Advanced notification patterns

### 6.6 - Server-Sent Events and Real-Time Streaming
- **test_sse_client.py** - Event stream parsing and classification
- Real-time UI updates via ADK Events
- Event types and processing patterns

## Key Files and Their Purpose

| File/Directory | Purpose | Key Concepts |
|----------------|---------|--------------|
| `fastapi_starter.py` | Complete ADK UI Contract implementation | Contract compliance, external state mutation |
| `adk_ui_contract.md` | Contract documentation and patterns | Point 4 (state_delta), API specifications |
| `research_state_agent/` | Basic state-aware agent (ADK structure) | Simple state management, tool integration |
| `enhanced_research_agent/` | Advanced state management agent (ADK structure) | Both simple and EventActions.state_delta |
| `demo_state_delta.py` | Interactive state management demo | External API integration, agent responses |
| `demo_enhanced_state.py` | Advanced state patterns demo | Complex state updates, notification patterns |
| `test_sse_client.py` | SSE streaming client | Event parsing, real-time communication |

### Agent Directory Structure (ADK Conventions)

Both agents now follow ADK best practices:

```
research_state_agent/
├── agent.py              # Main agent definition
├── prompts.py            # Agent instructions and behavior
├── __init__.py           # Exports root_agent
├── .env                  # Environment configuration
├── .env.sample          # Environment template
└── tools/
    ├── __init__.py
    └── research_state_tools.py

enhanced_research_agent/
├── agent.py              # Main agent definition  
├── prompts.py            # Agent instructions and behavior
├── __init__.py           # Exports root_agent
├── .env                  # Environment configuration
├── .env.sample          # Environment template
└── tools/
    ├── __init__.py
    ├── research_state_tools.py      # Simple state tools
    └── enhanced_research_tools.py   # EventActions.state_delta tools
```

## Running the Examples

### Basic FastAPI Server
```bash
cd textbook-adk-ch06-runtime
python fastapi_starter.py
```

### Interactive State Management Demo
```bash
python demo_state_delta.py
```

### SSE Streaming Test
```bash
# Start server first
python fastapi_starter.py

# In another terminal
python test_sse_client.py
```

### Individual Agent Testing
```bash
# Simple state management
uv run adk run research_state_agent/

# Advanced state management
uv run adk run enhanced_research_agent/
```

## Key Discoveries and Best Practices

### Agent State Visibility
**Critical Understanding**: Agents do NOT automatically see state changes from state_delta updates. Our implementation correctly handles this by:

1. **Template Variables**: Use `{state_key}` in agent instructions for automatic injection
2. **Tool Access**: Tools can read state via `ToolContext.get_state()`
3. **Explicit Notifications**: Send system/user messages about state changes
4. **Conversation Context**: Agents see previous messages that mentioned state

### When to Use Each State Management Approach

**Simple Updates** (`tool_context.update_state()`):
- Single field changes (priority, deadline, topic)
- Basic tool interactions
- Straightforward state modifications

**EventActions.state_delta**:
- Complex multi-field updates
- Batch state changes
- External system integration
- When event sourcing details matter

### Production Considerations

1. **Contract Compliance**: All endpoints follow ADK UI Contract specifications
2. **Error Handling**: Proper HTTP status codes and error messages
3. **Event Sourcing**: All state changes generate proper ADK Events
4. **Scalability**: Patterns support multiple runner instances
5. **Security**: Authentication and authorization ready for implementation

## Next Steps

After mastering these fundamentals, proceed to **Chapter 7: Custom PostgreSQL Runtime Implementation** to learn how to replace ADK's default services with persistent, scalable database backends.

This chapter provides the foundation for understanding how ADK works internally, enabling you to build sophisticated agent systems that integrate seamlessly with web UIs and external systems.