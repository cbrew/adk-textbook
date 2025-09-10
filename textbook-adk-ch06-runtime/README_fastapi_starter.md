# Enhanced ADK FastAPI Starter

This enhanced FastAPI starter is fully compliant with the ADK Web UI contract and demonstrates advanced state management capabilities, particularly **external state mutation via state_delta**.

## Key Features

✅ **Full ADK UI Contract Compliance**
- `/run` and `/run_sse` endpoints with proper Event streaming
- Complete session management endpoints with app_name path parameters
- Optional artifacts endpoints for UI compatibility
- Proper error handling and HTTP status codes

✅ **State Delta Support (Point 4)**
- External systems can inject state changes without breaking contracts
- State-only updates with empty message parts
- Event sourcing maintained for all state mutations
- Demonstrates real-world use case with Research State Agent

## Architecture

### Core Components

1. **Research State Agent** (`research_state_agent.py`)
   - Tracks research topics, priorities, deadlines, and sources in session state
   - Responds to state changes from both user interactions and external systems
   - Perfect example of state-aware agent design

2. **FastAPI Server** (`fastapi_starter.py`)
   - Contract-compliant REST endpoints
   - External state mutation endpoints
   - Proper ADK Runner integration

3. **Demo Script** (`demo_state_delta.py`)
   - Interactive demonstration of state_delta capabilities
   - Shows external system integration patterns

## API Endpoints

### Core ADK Contract Endpoints

```bash
# Run endpoints (contract-required)
POST /run                    # Non-streaming execution
POST /run_sse               # Server-sent events streaming

# Session management (contract-required)
GET    /apps/{app}/users/{user}/sessions                 # List sessions
POST   /apps/{app}/users/{user}/sessions/{session}      # Create session  
DELETE /apps/{app}/users/{user}/sessions/{session}      # Delete session

# Artifacts (optional for UI compatibility)
GET /apps/{app}/users/{user}/sessions/{session}/artifacts           # List artifacts
GET /apps/{app}/users/{user}/sessions/{session}/artifacts/{filename} # Get artifact
```

### Research Management Endpoints (State Delta Demos)

```bash
# External state mutation examples
POST /apps/{app}/users/{user}/sessions/{session}/research/priority  # Set priority
POST /apps/{app}/users/{user}/sessions/{session}/research/deadline  # Set deadline  
POST /apps/{app}/users/{user}/sessions/{session}/research/sources   # Add source
```

## State Delta Usage Patterns

### 1. Direct state_delta in `/run` or `/run_sse`

```json
POST /run_sse
{
  "app_name": "research_app",
  "user_id": "u_123", 
  "session_id": "s_123",
  "new_message": {"role": "system", "parts": []},
  "state_delta": {"priority_level": "High", "deadline": "2024-02-15"}
}
```

### 2. External System Integration

```python
# Research management dashboard can update agent state
async def update_research_priority(session_id: str, priority: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"/apps/research/users/researcher/sessions/{session_id}/research/priority",
            json={"priority_level": priority}
        )
```

### 3. State-Only Updates

The contract allows "state-only updates" by sending:
- `role: "system"` with empty `parts: []`
- `state_delta` with the changes
- This commits state changes without user interaction

## Running the Demo

1. **Start the server:**
   ```bash
   cd textbook-adk-ch07-runtime
   python fastapi_starter.py
   ```

2. **Run the demo:**
   ```bash
   python demo_state_delta.py
   ```

3. **Try manual API calls:**
   ```bash
   # Create session
   curl -X POST "http://localhost:8000/apps/research/users/demo/sessions/test001" \
        -H "Content-Type: application/json" \
        -d '{"current_topic": "AI Research"}'

   # User interaction
   curl -X POST "http://localhost:8000/run" \
        -H "Content-Type: application/json" \
        -d '{
          "app_name": "research",
          "user_id": "demo", 
          "session_id": "test001",
          "new_message": {
            "role": "user",
            "parts": [{"text": "Hello, tell me about my research status"}]
          }
        }'

   # External state update
   curl -X POST "http://localhost:8000/apps/research/users/demo/sessions/test001/research/priority" \
        -H "Content-Type: application/json" \
        -d '{"priority_level": "High"}'
   ```

## Why State Delta Matters

**Point 4 from the ADK UI Contract** is crucial for real-world applications:

1. **External Orchestration**: Management dashboards can update agent state
2. **Multi-System Integration**: Other services can inject relevant state changes  
3. **UI Controls**: Frontend components can modify state without full conversation turns
4. **Event Sourcing**: All changes are properly logged and auditable
5. **Contract Compliance**: Changes appear as standard Events to the UI

This pattern enables sophisticated agent systems where state can be influenced by multiple sources while maintaining consistency and auditability.

## Agent State Visibility: Critical Understanding

**Key Discovery**: Agents do NOT automatically see state changes. Based on ADK source code analysis:

### What Happens with state_delta:
1. `state_delta` updates are processed and stored in session state
2. ADK creates a "user" event with `EventActions(state_delta=state_delta)`  
3. **This event is NOT yielded to the agent conversation flow**
4. Agents remain unaware of state changes unless explicitly informed

### How Agents CAN See State:
- **Template Variables**: Use `{state_key}` in agent instructions for automatic injection
- **Tool Access**: Tools can read state via `ToolContext.get_state()`
- **Explicit Messages**: Tell agent about changes via system/user messages
- **Conversation History**: Agent sees previous messages that mentioned state

### Implications for Agent Design:
```python
# ❌ Agent won't automatically know about this
state_delta = {"priority": "High"}

# ✅ Agent instructions with template injection  
instruction = "Current priority: {priority}"

# ✅ Explicit notification
system_message = "Priority has been updated to High"
```

Our FastAPI implementation correctly handles this by sending system messages to notify agents of external state changes, ensuring they can respond appropriately.

## Implementation Notes

- **Event Sourcing**: All state changes generate proper ADK Events
- **Contract Intact**: UI sees consistent Event streams regardless of state change origin
- **Error Handling**: Proper HTTP status codes and error messages
- **Backward Compatibility**: Legacy endpoints maintained during transition
- **Type Safety**: Pydantic models for all request/response schemas

## Next Steps

- Replace `InMemorySessionService` with persistent storage
- Add authentication and authorization
- Implement custom `MemoryService` for long-term agent memory
- Add webhook endpoints for external system notifications
- Scale with multiple runner instances