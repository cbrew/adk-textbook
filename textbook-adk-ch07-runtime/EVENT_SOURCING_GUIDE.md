# Event Sourcing in ADK: A Complete Guide

## What is Event Sourcing?

**Event Sourcing** is a way of storing data that focuses on recording *what happened* rather than just the current state. Instead of updating a database record to show the current status, you keep a chronological log of all the events that led to that status.

### Real-World Analogy

Think of event sourcing like a bank statement:

- **Traditional Approach**: Your account shows "$1,500 current balance"
- **Event Sourcing Approach**: Your statement shows:
  - Jan 1: Started with $1,000
  - Jan 2: Deposited $200  
  - Jan 3: Withdrew $50
  - Jan 5: Deposited $350
  - **Current Balance**: $1,500 (calculated from events)

The events tell the complete story of how you got to $1,500, not just the final number.

## Why Use Event Sourcing?

### Benefits
- **🔍 Complete Audit Trail**: See exactly what happened and when
- **🔄 Replay Capability**: Recreate any past state by replaying events
- **🐛 Debugging**: Track down exactly where issues occurred
- **📊 Analytics**: Understand patterns in user behavior
- **🔒 Immutability**: Events never change once created (safer than updates)

### Use Cases Perfect for Event Sourcing
- Financial systems (transactions)
- Collaborative editing (Google Docs changes)
- Version control (Git commits)
- **AI Conversations** (our use case!)

## ADK Events: The Foundation

Google's Agent Development Kit (ADK) is built around an **event-driven architecture**. Every interaction in an ADK system generates events that capture what happened.

### ADK Event Structure

According to the [official ADK documentation](https://google.github.io/adk-docs/events/), every ADK event has this structure:

```python
from google.adk.events import Event, EventActions

# Basic ADK Event
event = Event(
    id="unique-event-id",              # Automatically generated
    author="user",                     # Who created this event
    content=Content(...),              # The actual message/data
    timestamp=1234567890.0,            # When it happened
    actions=EventActions(...),         # What actions to take
    invocation_id="conversation-123"   # Groups related events
)
```

### Types of ADK Events

ADK generates different types of events automatically:

1. **User Message Events**: When a user sends a message
2. **Agent Response Events**: When the AI responds  
3. **Function Call Events**: When tools are used
4. **Function Response Events**: Results from tools
5. **State Change Events**: When session state is updated ⭐

## Our Event Sourcing Implementation

### The Problem We Solved

Traditional chat systems store conversations like this:
```sql
-- Traditional approach (data duplication)
CREATE TABLE conversations (
    id UUID,
    user_message TEXT,      -- Duplicate of event data
    agent_response TEXT,    -- Duplicate of event data  
    timestamp TIMESTAMP
);

CREATE TABLE session_events (
    id UUID,
    content TEXT,           -- Same data, stored again!
    timestamp TIMESTAMP
);
```

This creates **data duplication** - the same conversation exists in multiple places and can get out of sync.

### Our Event Sourcing Solution

We use ADK events as the **single source of truth** and create searchable indexes:

```sql
-- Our approach (event sourcing)
CREATE TABLE sessions (
    id UUID,
    events JSONB           -- Complete event history (authoritative)
);

CREATE TABLE memory (
    id UUID,
    content TEXT,          -- Searchable summary (index only)
    metadata JSONB,        -- Event reference + keywords
    -- NO duplication of full event data!
);
```

### How State Changes Become Events

Here's the key innovation: when conversation state changes, we create proper ADK events with **state_delta** actions:

```python
# postgres_chat_agent/driver.py
async def _create_conversation_events(self, session, message: str, response: str):
    """Create proper ADK events for conversation updates."""
    
    # 1. User message event (no state change)
    user_event = Event(
        author="user",
        content=types.Content(role="user", parts=[types.Part(text=message)]),
        actions=EventActions()  # No actions for user messages
    )
    
    # 2. Agent response event WITH state change
    conversation_state = {
        "last_interaction": datetime.now().isoformat(),
        "message_count": len(session.events),
        "conversation_topic": extract_topic_from_message(message),
        "agent_response_length": len(response)
    }
    
    agent_event = Event(
        author="postgres_chat_agent",
        content=types.Content(role="model", parts=[types.Part(text=response)]),
        actions=EventActions(state_delta=conversation_state)  # ⭐ KEY!
    )
    
    # Add both events to session
    session.events.extend([user_event, agent_event])
```

### Memory Indexing Without Duplication

When events are added to memory, we create indexes that reference the events:

```python
# adk_runtime/services/memory_service.py
async def _index_event_if_searchable(self, session, event):
    """Create memory index entry for an event."""
    
    # Extract searchable keywords (NO full content duplication)
    keywords = self._extract_event_keywords(event)
    content_summary = self._create_event_summary(event)  # Brief summary only
    
    # Special handling for state_delta events
    if event.actions and event.actions.state_delta:
        state_info = self._summarize_state_delta(event.actions.state_delta)
        content_summary += f" | State: {state_info}"
        keywords.extend(["state_update", "interaction", "conversation"])
    
    # Store index entry (references event, doesn't duplicate it)
    memory_index = {
        "id": str(uuid.uuid4()),
        "content": content_summary,        # Summary for search
        "metadata": {
            "session_id": session.id,
            "event_id": event.id,          # Reference to actual event
            "event_author": event.author,
            "event_type": self._classify_event_type(event),
            "keywords": keywords,
            "is_index": True               # Flag: this is an index, not original data
        }
    }
```

## Connection to ADK Specification

### ADK's Event-Driven Architecture

According to the [ADK Events documentation](https://google.github.io/adk-docs/events/), ADK is fundamentally event-driven:

> "Events are the core building blocks of the ADK. Every interaction, from user messages to function calls, generates events that capture what happened in your agent system."

Our implementation follows this specification exactly:

1. **✅ Event Structure Compliance**: We use the official `Event` and `EventActions` classes
2. **✅ State Delta Pattern**: We use `actions.state_delta` for state changes as documented
3. **✅ Event Classification**: We classify events by type (`text_message`, `state_update`, etc.)
4. **✅ Immutable Events**: Events are never modified after creation

### ADK Memory Service Integration

The [ADK Memory documentation](https://google.github.io/adk-docs/sessions/memory/) explains:

> "The memory service allows agents to store and retrieve information across conversations, enabling long-term context and learning."

Our PostgreSQL memory service extends the standard `BaseMemoryService` and adds event sourcing:

```python
class PostgreSQLMemoryService(BaseMemoryService):
    """PostgreSQL-backed memory service with event sourcing."""
    
    async def add_session_to_memory(self, session: "Session") -> None:
        """ADK standard method - adds session events to searchable memory."""
        for event in session.events:
            await self._index_event_if_searchable(session, event)
    
    async def search_memory(self, *, app_name: str, user_id: str, query: str) -> SearchMemoryResponse:
        """ADK standard method - searches indexed events."""
        # Search both content and state_delta information
        memories = await self._search_by_text(app_name, user_id, query)
        return SearchMemoryResponse(memories=memories)
```

### ADK Session State Management

The [ADK Sessions documentation](https://google.github.io/adk-docs/sessions/) explains session state:

> "Session state persists across conversations and can be modified by agents through actions."

Our implementation captures state changes as events with `state_delta` actions, following ADK patterns:

```python
# When state changes, create an event with state_delta
event_actions = EventActions()
event_actions.state_delta = {
    "conversation_topic": "machine learning",
    "message_count": 5,
    "last_interaction": "2025-09-05T10:30:00Z"
}

event = Event(
    author="postgres_chat_agent",
    actions=event_actions
)
```

## Practical Benefits in Our Implementation

### 1. **Searchable Conversation History**

Because we index events with their state changes, you can search for:
- **Content**: `"machine learning"` finds messages about ML
- **State**: `"topic: research"` finds conversations about research topics
- **Metadata**: `"msgs: 10"` finds sessions with 10+ messages

### 2. **Complete Audit Trail**

Every conversation interaction creates events with:
- What was said (content)
- When it happened (timestamp)  
- How state changed (state_delta)
- Who was involved (author)

### 3. **No Data Duplication**

- **Events**: Stored once in session.events (authoritative)
- **Memory**: Contains only searchable indexes that reference events
- **Consistency**: Single source of truth prevents sync issues

### 4. **ADK Compliance**

- Uses official ADK Event structure
- Extends standard ADK BaseMemoryService
- Works with ADK Runner and web interface
- Follows ADK patterns for state management

## Example: Complete Event Flow

Let's trace a complete conversation through our event sourcing system:

### Step 1: User Sends Message
```
User: "What are the latest trends in machine learning?"
```

### Step 2: System Creates User Event
```python
user_event = Event(
    id="event-123",
    author="user",
    content=Content(role="user", parts=[Part(text="What are the latest trends in machine learning?")]),
    timestamp=1725518400.0,
    actions=EventActions()  # No state change for user messages
)
```

### Step 3: Agent Responds and Creates Response Event with State Change
```python
# Agent generates response
response = "Current ML trends include large language models, multimodal AI..."

# Create agent event with state_delta
agent_event = Event(
    id="event-124", 
    author="postgres_chat_agent",
    content=Content(role="model", parts=[Part(text=response)]),
    timestamp=1725518405.0,
    actions=EventActions(state_delta={
        "conversation_topic": "machine learning, trends",
        "message_count": 2,
        "last_interaction": "2025-09-05T10:30:05Z"
    })
)
```

### Step 4: Events Added to Session
```python
session.events.extend([user_event, agent_event])
# Session now has authoritative record of what happened
```

### Step 5: Memory Service Creates Searchable Indexes
```python
# For user event
user_index = {
    "content": "From user | Type: text_message | Content: What are the latest trends in machine learning?",
    "metadata": {
        "event_id": "event-123",
        "keywords": ["latest", "trends", "machine", "learning"],
        "is_index": True
    }
}

# For agent event (includes state info)
agent_index = {
    "content": "From postgres_chat_agent | Type: text_message | Content: Current ML trends include... | State: topic: machine learning, trends, msgs: 2",
    "metadata": {
        "event_id": "event-124", 
        "keywords": ["machine", "learning", "trends", "state_update", "conversation"],
        "event_type": "text_message",
        "is_index": True
    }
}
```

### Step 6: Future Searches Work
```python
# Content search
search_memory(query="machine learning")
# Returns: Both user and agent indexes (finds "machine learning" in content)

# State search  
search_memory(query="topic:")
# Returns: Agent index (finds state information)

# Event reconstruction
# Can always get full event details from session.events using event_id
```

## Testing the Implementation

You can see event sourcing in action:

### Test Event Creation
```bash
cd textbook-adk-ch07-runtime
python postgres_chat_agent/driver.py --test-memory

# Output shows:
# ✅ Created 2 ADK events for conversation
# 📝 Memory indexes created: User message + Agent response with state_delta
# 🔍 Search results show both content and state information
```

### Interactive Testing
```bash
python postgres_chat_agent/main.py --interactive

# Try these commands:
# /memory machine learning    # Search indexed events
# /session                   # See session state (built from events)
# /save research topic       # Creates new events with state_delta
```

## Comparison: Traditional vs Event Sourcing

### Traditional Chat Storage
```
❌ Stores final state only: "User asked about ML, agent responded"
❌ Data duplication: Same conversation in multiple tables
❌ No audit trail: Can't see how state evolved
❌ Update conflicts: Race conditions when multiple updates happen
❌ Limited searchability: Only current data is searchable
```

### Our Event Sourcing Approach  
```
✅ Complete history: Every interaction recorded as events
✅ Single source of truth: Events are authoritative, indexes reference them
✅ Full audit trail: See exactly what happened when
✅ Immutable events: No update conflicts, events never change
✅ Rich searchability: Content + state information + metadata all searchable
✅ ADK compliant: Uses official ADK Event structure and patterns
```

## Further Reading

To learn more about ADK's event system:

- **[ADK Events Documentation](https://google.github.io/adk-docs/events/)**: Official event structure and patterns
- **[ADK Sessions Documentation](https://google.github.io/adk-docs/sessions/)**: State management and persistence
- **[ADK Memory Documentation](https://google.github.io/adk-docs/sessions/memory/)**: Memory service integration
- **Our Implementation**: `postgres_chat_agent/driver.py` and `adk_runtime/services/memory_service.py`

## Summary

Event sourcing in our ADK implementation provides:

1. **🎯 Proper ADK Compliance**: Uses official Event and EventActions structures
2. **📚 Complete History**: Every conversation interaction becomes searchable events  
3. **🔍 Rich Search**: Find conversations by content, state changes, or metadata
4. **⚡ Performance**: Indexed summaries for fast search, full events for detail
5. **🔒 Data Integrity**: Single source of truth prevents duplication and sync issues
6. **👩‍🎓 Academic Focus**: Perfect for research workflows requiring persistent memory

This creates a production-ready, ADK-compliant system that academic researchers can trust for long-term conversation persistence and retrieval.