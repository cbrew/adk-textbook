# ADK Web Architecture Analysis

This document analyzes the Google ADK web CLI implementation to understand how it handles agent execution, streaming tools, and real-time communication patterns.

## Frontend Architecture

### Technology Stack
- **Framework**: Angular application with Material Design
- **Structure**: Single-page app with modular JavaScript chunks
- **Entry Point**: `<app-root>` element in `index.html`
- **Styling**: Dark theme with Google Fonts and Material icons

### File Structure
```
src/google/adk/cli/browser/
├── index.html                 # Main HTML entry point
├── main-W7QZBYAR.js          # Angular application bundle
├── polyfills-B6TNHZQ6.js     # Browser compatibility
├── styles-4VDSPQ37.css       # Application styles
└── adk_favicon.svg           # ADK favicon
```

## Backend API Endpoints

### Core Agent Execution
- **`POST /run`** - Synchronous agent execution, returns all events at completion
- **`GET /run_sse`** - Server-Sent Events streaming responses for real-time updates
- **`WebSocket /run_live`** - Bidirectional live agent interaction

### Session Management
- **`POST /sessions`** - Create new session with optional initial state
- **`GET /sessions`** - List all sessions for current user
- **`GET /sessions/{session_id}`** - Retrieve specific session with events
- **`DELETE /sessions/{session_id}`** - Delete session and associated data
- **`PUT /sessions/{session_id}/state`** - Update session state incrementally

### Agent Configuration (Work in Progress)
- **`POST /builder/save`** - Save agent configuration files
- **`GET /builder/app/{app_name}`** - Retrieve agent configuration files

### Agent-to-Agent Communication
- **`/a2a/{app_name}`** - Dynamic RPC endpoints for inter-agent communication
- **`/a2a/{app_name}/agent-card`** - Agent metadata and capabilities

## ADK Streaming Tools Architecture

### Understanding Streaming Tools

ADK streaming tools are async functions that return `AsyncGenerator`, allowing them to yield intermediate results in real-time:

```python
async def streaming_stock_monitor() -> AsyncGenerator[str, None]:
    while True:
        current_price = get_stock_price()
        yield f"Current price: ${current_price}"
        await asyncio.sleep(1)
```

#### Key Characteristics
- **Continuous Generation**: Tools yield results over time rather than single responses
- **Real-time Updates**: Agents can react to intermediate results as they arrive
- **Interruptible**: Streaming can be stopped or modified based on agent decisions
- **Event-driven**: Each yielded result becomes an ADK Event

## Web Server Streaming Patterns

### 1. `/run` - Batch Processing
```python
# Synchronous execution, returns all events at once
events = await runner.run_async(request.user_message, session=session)
return {"events": events}
```

**Characteristics:**
- **Use Case**: Simple request/response, no streaming needed
- **Client Interaction**: Single HTTP POST, complete response returned
- **Tool Execution**: All tools (streaming and non-streaming) run to completion
- **Session Handling**: Final state updated after all events processed

### 2. `/run_sse` - Server-Sent Events Streaming
```python
# Streams events as they're generated
async for event in runner.run_stream_async(...):
    yield f"data: {event.model_dump_json()}\n\n"
```

**Characteristics:**
- **Use Case**: Real-time updates from server to client (unidirectional)
- **Client Interaction**: Listens to event stream, cannot send messages during execution
- **Tool Execution**: Streaming tools yield intermediate results pushed to frontend
- **Session Handling**: Events accumulated in session as they're generated

### 3. `/run_live` - Bidirectional WebSocket
```python
# Concurrent processing of incoming/outgoing messages
async with queue.run_agent_async(...) as event_stream:
    async for event in event_stream:
        await websocket.send_json(event.model_dump())
```

**Characteristics:**
- **Use Case**: Interactive conversations, real-time tool interaction
- **Client Interaction**: Send/receive messages simultaneously
- **Tool Execution**: Streaming tools can be interrupted, modified, or continued
- **Session Handling**: Full bidirectional session state management

## Communication Flow Patterns

### Event Flow Architecture
```
Frontend -> POST /run -> Agent Runner -> Complete Response -> Frontend
Frontend -> GET /run_sse -> Agent Runner -> Event Stream -> Frontend  
Frontend -> WebSocket /run_live <-> Agent Runner <-> Real-time Updates
```

### Streaming Tool Execution Flow
```
1. Agent calls streaming tool (e.g., stock price monitor)
2. Tool yields intermediate results: $100 -> $101 -> $102...
3. Each yield becomes an ADK Event
4. Web server streams Events to frontend via chosen endpoint
5. Frontend updates UI in real-time
6. User can interact or interrupt via WebSocket
```

### WebSocket Message Structure
- Uses `LiveRequest.model_validate_json()` for parsing incoming messages
- Sends events as JSON-serialized ADK Event objects
- Supports multiple modalities (TEXT, AUDIO)
- Includes validation and error handling during transmission

## Session State Management

### State Persistence During Streaming
- **Session Context**: Maintained throughout all streaming operations
- **Event Accumulation**: All events (including intermediate results) stored in session
- **State Deltas**: Session state can be updated incrementally during execution
- **Tool Interruption**: WebSocket allows stopping streaming tools mid-execution
- **User Scoping**: Sessions are isolated per user for security

### Session Lifecycle
```
1. Create Session -> Initial state set
2. Start Agent Run -> Events begin accumulating  
3. Streaming Tools Execute -> Intermediate events stored
4. User Interaction -> State deltas applied
5. Completion/Interruption -> Final state persisted
```

## Key Architectural Insights

### Progressive Enhancement Model
The three endpoints represent increasing levels of interactivity:
- **Basic**: `/run` for simple request/response
- **Enhanced**: `/run_sse` for real-time updates
- **Full**: `/run_live` for complete interactivity

### Event-Driven Architecture
- Everything becomes an ADK Event that gets streamed to frontend
- Consistent event structure across all communication patterns
- Events include metadata for proper UI rendering and state management

### Tool Execution Flexibility
- Same streaming mechanism works for any `AsyncGenerator` tool
- Tools can be streaming or non-streaming without changing server architecture  
- Allows building UIs from simple chatbots to real-time monitoring dashboards

### Session-Centric Design
- All communication patterns preserve full conversation context
- State management is consistent across streaming and non-streaming operations
- Supports complex agent workflows with persistent memory

## Implementation Considerations for Custom UIs

### Choosing Communication Pattern
- **`/run`**: Simple agents with deterministic, fast responses
- **`/run_sse`**: Agents with long-running tasks or streaming tools (unidirectional)
- **`/run_live`**: Interactive agents requiring user feedback during execution

### Frontend Integration
- Angular-based reference implementation provides patterns for:
  - Event stream handling
  - Session state synchronization  
  - Real-time UI updates
  - Error handling and recovery

### Backend Customization
- FastAPI-based server allows easy extension with custom endpoints
- Service injection pattern supports different storage backends
- Plugin architecture enables custom tool integration

This architecture provides a flexible foundation for building custom UIs that can leverage ADK's agent execution, session management, and real-time communication capabilities.