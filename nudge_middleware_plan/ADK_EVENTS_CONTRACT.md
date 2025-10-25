# Research Grounding Panel ↔ ADK Events Contract

**Version**: 1.0
**Target ADK Version**: 1.13+
**Purpose**: Define the exact ADK events used by the Research Grounding Panel

This document specifies how the Research Grounding Panel consumes standard ADK events via REST/SSE, following Google's official [ADK Events documentation](https://google.github.io/adk-docs/events/).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [ADK Event Types Used](#adk-event-types-used)
3. [State Delta Mapping](#state-delta-mapping)
4. [REST API Endpoints](#rest-api-endpoints)
5. [Event Schemas](#event-schemas)
6. [Event Flow Sequences](#event-flow-sequences)
7. [Implementation Patterns](#implementation-patterns)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Research Grounding Panel                   │
│                      (Web/Console UI)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ SSE Stream (Server-Sent Events)
                         │ Consumes standard ADK events
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (ADK UI Contract)               │
│                                                             │
│  Endpoints:                                                 │
│  • POST /run_sse  → Stream ADK events                      │
│  • POST /run      → Batch ADK events                       │
│  • Session management (GET/POST/DELETE)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ Yields events
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   ADK Runner + Agent                        │
│                                                             │
│  Components:                                                │
│  • Research Agent (with search tools)                      │
│  • SessionService (stores grounding state)                 │
│  • Tool execution (database searches)                      │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: The panel is a **pure consumer** of standard ADK events. It does NOT require custom event types or extensions to the ADK event model.

---

## ADK Event Types Used

Based on [ADK Events documentation](https://google.github.io/adk-docs/events/), the Research Grounding Panel consumes these standard event types:

### 1. **User Input Events**
- **author**: `"user"`
- **content**: User's search request or approval/cancel decision
- **Purpose**: Trigger research workflow

### 2. **Agent Response Events**
- **author**: Agent name (e.g., `"research_agent"`)
- **content**: Agent's text responses, search plans, targeted help
- **Purpose**: Display agent communication to researcher

### 3. **Tool Call Request Events**
- **author**: Agent name
- **content**: Contains `function_calls` for database search tools
- **Purpose**: Show which database is being searched (transparency)

### 4. **Tool Result Events**
- **author**: Agent name
- **content**: Contains `function_responses` with search results
- **Purpose**: Show papers found, result counts

### 5. **State Update Events**
- **author**: Agent name or `"system"`
- **actions.state_delta**: Dictionary of grounding state changes
- **Purpose**: Update grounding panel fields

### 6. **Error Events**
- **content**: Error message
- **Purpose**: Display search failures, trigger targeted help

### 7. **Turn Complete Events**
- **turn_complete**: `true`
- **Purpose**: Signal end of interaction cycle

---

## State Delta Mapping

The `ResearchGroundingBox` is stored in ADK session state using these keys:

### Session State Schema

```python
session.state = {
    # Core Grounding Fields
    "grounding:research_question": str,
    "grounding:stage": str,  # "scoping" | "retrieval" | "synthesis" | "validation"
    "grounding:search_assumptions": List[str],
    "grounding:open_questions": List[str],
    "grounding:papers_found": int,
    "grounding:databases_searched": List[str],
    "grounding:current_filters": Dict[str, Any],

    # Next Action
    "grounding:next_action": {
        "owner": str,  # "agent" | "researcher" | "both"
        "action": str,  # "search" | "refine" | "synthesize" | "validate" | "ask"
        "target": str,  # database name or analysis type
        "due": str     # time constraint
    },

    # Search History (for receipts)
    "grounding:search_history": List[Dict],  # List of SearchReceipt objects

    # Current Search Plan (for approval gates)
    "grounding:pending_search_plan": Dict | None,

    # Failure Context (for targeted help)
    "grounding:last_search_failure": {
        "type": str,  # SearchFailureClass enum value
        "context": Dict[str, Any],
        "remedies": Dict[str, str]
    } | None
}
```

### State Delta Events

When grounding state changes, the agent emits events with `actions.state_delta`:

**Example: Research question refined**
```json
{
  "author": "research_agent",
  "content": null,
  "actions": {
    "state_delta": {
      "grounding:research_question": "What approaches exist for XAI in clinical decision support?",
      "grounding:stage": "retrieval"
    }
  },
  "invocation_id": "inv_123",
  "id": "evt_456",
  "timestamp": 1698765432.123
}
```

---

## REST API Endpoints

The Research Grounding Panel uses standard ADK UI Contract endpoints:

### 1. `POST /run_sse` (Streaming)

**Purpose**: Execute research workflow and stream events in real-time

**Request Body**:
```json
{
  "app_name": "research_agent",
  "user_id": "researcher_123",
  "session_id": "session_456",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "Search Semantic Scholar for explainable AI in healthcare" }
    ]
  },
  "streaming": true,
  "state_delta": {
    "grounding:current_filters": {
      "year": ">=2020",
      "fields": ["Medicine", "Computer Science"]
    }
  }
}
```

**Response**: Server-Sent Events (SSE) stream

```
data: {"author":"research_agent","content":{"parts":[{"text":"I'll search..."}]},...}

data: {"author":"research_agent","content":{"function_calls":[...]},...}

data: {"author":"research_agent","actions":{"state_delta":{"grounding:papers_found":34}},...}

data: {"author":"research_agent","turn_complete":true,...}
```

### 2. `POST /run` (Non-Streaming)

**Purpose**: Execute research workflow and return all events at once

**Request/Response**: Same as `/run_sse` but returns JSON array of all events

### 3. Session Management

Standard ADK session endpoints:

- `GET /apps/{app}/users/{user}/sessions` - List sessions
- `POST /apps/{app}/users/{user}/sessions/{session}` - Create session
- `DELETE /apps/{app}/users/{user}/sessions/{session}` - Delete session

### 4. State-Only Updates

To update grounding state without user message:

```json
{
  "app_name": "research_agent",
  "user_id": "researcher_123",
  "session_id": "session_456",
  "new_message": {
    "role": "system",
    "parts": []
  },
  "state_delta": {
    "grounding:search_assumptions": ["Clinical applications only", "2020-present"]
  }
}
```

---

## Event Schemas

### Base Event Structure

All events follow ADK's standard `Event` model:

```typescript
interface Event {
  // Core fields (always present)
  author: string;              // "user" or agent name
  invocation_id: string;       // Unique per interaction
  id: string;                  // Unique per event
  timestamp: number;           // Unix timestamp

  // Optional fields
  content?: Content;           // Message payload
  partial?: boolean;           // Streaming incomplete
  turn_complete?: boolean;     // Interaction finished
  actions?: EventActions;      // Side effects
  error?: ErrorInfo;           // Error details
}

interface EventActions {
  state_delta?: Record<string, any>;         // State changes
  artifact_delta?: Record<string, number>;   // Artifact versions
  transfer_to_agent?: string;                // Agent routing
  escalate?: boolean;                        // Loop termination
  skip_summarization?: boolean;              // Skip LLM summary
}
```

### Event Type 1: Search Plan Presentation

**Purpose**: Agent presents search plan for approval

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": {
    "parts": [
      {
        "text": "┌─ SEARCH PLAN ────────────────────────┐\n│ Database: Semantic Scholar\n│ Query: \"explainable AI clinical\"\n│ Filters:\n│   • Year: 2020-present\n│   • Fields: Medicine, CS\n│\n│ Rationale: Best interdisciplinary coverage\n│\n│ Expected Results: 30-80 papers\n│\n│ OPTIONS:\n│ [OK] Proceed  [Short Run] Preview  [Modify] Adjust  [Cancel] Skip\n└──────────────────────────────────────┘"
      }
    ]
  },
  "actions": {
    "state_delta": {
      "grounding:pending_search_plan": {
        "database": "Semantic Scholar",
        "query": "explainable AI clinical",
        "filters": {"year": ">=2020", "fields": ["Medicine", "CS"]},
        "rationale": "Best interdisciplinary coverage",
        "expected_results": "30-80 papers"
      },
      "grounding:next_action": {
        "owner": "researcher",
        "action": "approve_search",
        "target": "Semantic Scholar",
        "due": "now"
      }
    }
  },
  "invocation_id": "inv_001",
  "id": "evt_001",
  "timestamp": 1698765432.123,
  "turn_complete": false
}
```

### Event Type 2: Tool Call (Database Search)

**Purpose**: Agent executes database search

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": {
    "function_calls": [
      {
        "name": "search_semantic_scholar",
        "args": {
          "query": "explainable AI clinical",
          "field": "all"
        },
        "id": "call_123"
      }
    ]
  },
  "invocation_id": "inv_001",
  "id": "evt_002",
  "timestamp": 1698765433.456,
  "turn_complete": false
}
```

### Event Type 3: Tool Result (Search Results)

**Purpose**: Database returns search results

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": {
    "function_responses": [
      {
        "id": "call_123",
        "name": "search_semantic_scholar",
        "response": {
          "papers": [
            {
              "title": "Deep Learning for Computer Vision: A Brief Review",
              "authors": ["Li Zhang", "Sarah Chen"],
              "year": 2023,
              "citations": 1247,
              "url": "https://semantic-scholar.org/paper/12345"
            }
            // ... more papers
          ],
          "count": 34
        }
      }
    ]
  },
  "invocation_id": "inv_001",
  "id": "evt_003",
  "timestamp": 1698765435.789,
  "turn_complete": false
}
```

### Event Type 4: Grounding State Update

**Purpose**: Update grounding box after search

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": null,
  "actions": {
    "state_delta": {
      "grounding:papers_found": 34,
      "grounding:databases_searched": ["Semantic Scholar"],
      "grounding:pending_search_plan": null,
      "grounding:search_history": [
        {
          "timestamp": "14:23",
          "database": "Semantic Scholar",
          "query": "explainable AI clinical",
          "results_count": 34,
          "filters_applied": ["year>=2020", "fields=Medicine,CS"],
          "delta": "Found 34 papers from Semantic Scholar",
          "next": "Search arXiv for preprints",
          "duration_ms": 2300,
          "warnings": []
        }
      ],
      "grounding:next_action": {
        "owner": "agent",
        "action": "search",
        "target": "arXiv",
        "due": "5pm today"
      }
    }
  },
  "invocation_id": "inv_001",
  "id": "evt_004",
  "timestamp": 1698765436.012,
  "turn_complete": false
}
```

### Event Type 5: Search Receipt (Agent Response)

**Purpose**: Present search receipt to researcher

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": {
    "parts": [
      {
        "text": "[14:23] Searched Semantic Scholar: \"explainable AI clinical\" (2020+)\n→ Found 34 papers (8 surveys, 14 methods, 12 applications)\n→ Added to grounding: 34 papers, 1 database\n→ Next: Search arXiv for recent preprints"
      }
    ]
  },
  "invocation_id": "inv_001",
  "id": "evt_005",
  "timestamp": 1698765436.234,
  "turn_complete": true
}
```

### Event Type 6: Search Failure + Targeted Help

**Purpose**: Classify failure and provide specific remedies

**Event Structure**:
```json
{
  "author": "research_agent",
  "content": {
    "parts": [
      {
        "text": "┌─ SEARCH HELP ────────────────────────────────┐\n│ Only 3 papers found in ACM – this seems low.\n│\n│ Possible reasons:\n│ • ACM has CS focus but weak medical coverage\n│ • HCI venues may use different terminology\n│\n│ READY-TO-CLICK ACTIONS:\n│ → [Try Synonyms] \"AI transparency\" OR \"algorithmic explainability\"\n│ → [Different Database] Try IEEE for medical informatics\n│ → [Broaden Query] Remove \"clinical\" filter\n│\n│ Recommendation: Try synonyms first\n└──────────────────────────────────────────────┘"
      }
    ]
  },
  "actions": {
    "state_delta": {
      "grounding:last_search_failure": {
        "type": "database_coverage_gap",
        "context": {
          "database": "ACM",
          "query": "explainable AI clinical",
          "results_count": 3,
          "expected_count": 12
        },
        "remedies": {
          "primary": "Try synonyms: 'AI transparency' OR 'algorithmic explainability'",
          "fallback": "Search IEEE for medical informatics perspectives",
          "ask_researcher": "Which approach would you prefer?"
        }
      }
    }
  },
  "invocation_id": "inv_002",
  "id": "evt_010",
  "timestamp": 1698765500.123,
  "turn_complete": false
}
```

---

## Event Flow Sequences

### Sequence 1: Successful Search Flow

```
1. User Input Event
   ↓
2. Agent: Search Plan Presentation (with state_delta for pending_plan)
   ↓
3. User Input Event: "OK" (approval)
   ↓
4. Agent: Tool Call Request (search_semantic_scholar)
   ↓
5. Agent: Tool Result (papers returned)
   ↓
6. Agent: State Update (papers_found, databases_searched, search_history)
   ↓
7. Agent: Search Receipt (human-readable summary)
   ↓
8. Event with turn_complete=true
```

**Total Events**: 8 (all standard ADK events)

### Sequence 2: Search Failure with Targeted Help

```
1. User Input Event
   ↓
2. Agent: Search Plan Presentation
   ↓
3. User Input Event: "OK"
   ↓
4. Agent: Tool Call Request (search_acm_digital_library)
   ↓
5. Agent: Tool Result (only 3 papers - unexpected)
   ↓
6. Agent: State Update (papers_found, last_search_failure)
   ↓
7. Agent: Targeted Help (failure classification + remedies)
   ↓
8. User Input Event: Selects remedy (e.g., "Try Synonyms")
   ↓
9. Agent: Refined Search Plan with synonyms
   ↓
... (continues with Sequence 1)
```

### Sequence 3: State-Only Update (External Panel Action)

```
1. Panel sends POST /run_sse with:
   - new_message: { role: "system", parts: [] }
   - state_delta: { "grounding:search_assumptions": [...] }
   ↓
2. Agent: State Update Event (echoes state_delta)
   ↓
3. Panel updates grounding box display
```

**No agent processing**: Pure state mutation

### Sequence 4: Short Run Preview

```
1. User Input Event
   ↓
2. Agent: Search Plan Presentation
   ↓
3. User Input Event: "Short Run"
   ↓
4. Agent: Tool Call with limit=10
   ↓
5. Agent: Tool Result (10 papers)
   ↓
6. Agent: State Update (preview mode)
   ↓
7. Agent: Preview Summary + Ask "Proceed with full search?"
   ↓
8. User decides: OK → full search, Modify → adjust, Cancel → skip
```

---

## Implementation Patterns

### Pattern 1: Injecting Grounding State via state_delta

**In Agent Tool**:
```python
from google.adk.tools.tool_context import ToolContext

def search_semantic_scholar(query: str, tool_context: ToolContext) -> dict:
    # Execute search
    results = _perform_search(query)

    # Update grounding state via ADK's standard mechanism
    tool_context.state["grounding:papers_found"] += len(results["papers"])

    current_dbs = tool_context.state.get("grounding:databases_searched", [])
    tool_context.state["grounding:databases_searched"] = current_dbs + ["Semantic Scholar"]

    # Append to search history
    current_history = tool_context.state.get("grounding:search_history", [])
    tool_context.state["grounding:search_history"] = current_history + [{
        "timestamp": datetime.now().strftime("%H:%M"),
        "database": "Semantic Scholar",
        "query": query,
        "results_count": len(results["papers"]),
        "filters_applied": ["year>=2020"],
        "delta": f"Found {len(results['papers'])} papers",
        "next": "Search arXiv",
        "duration_ms": 2300,
        "warnings": []
    }]

    return results  # ADK automatically emits state_delta event
```

**Result**: ADK Runner automatically generates an event with `actions.state_delta` containing the changes.

### Pattern 2: Panel Consuming SSE Stream

**JavaScript/TypeScript** (web panel):
```typescript
const eventSource = new EventSource('/run_sse', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
});

eventSource.onmessage = (event) => {
  const adkEvent = JSON.parse(event.data);

  // Update grounding panel if state_delta present
  if (adkEvent.actions?.state_delta) {
    updateGroundingPanel(adkEvent.actions.state_delta);
  }

  // Display agent text
  if (adkEvent.content?.parts) {
    displayAgentMessage(adkEvent.content.parts);
  }

  // Handle turn complete
  if (adkEvent.turn_complete) {
    markTurnComplete();
  }
};
```

**Python** (console panel):
```python
import httpx

async with httpx.stream("POST", "/run_sse", json=request) as response:
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            event_json = line[6:]  # Strip "data: " prefix
            event = json.loads(event_json)

            # Update grounding panel
            if event.get("actions", {}).get("state_delta"):
                update_grounding_panel(event["actions"]["state_delta"])

            # Display receipts
            if event.get("content", {}).get("parts"):
                display_turn_receipt(event["content"]["parts"][0]["text"])
```

### Pattern 3: Emitting Custom Display Events

**Agent can emit display-only events** without state changes:

```python
from google.genai import types

def present_search_plan(database: str, query: str, tool_context: ToolContext):
    # Format search plan text
    plan_text = format_search_plan(database, query)

    # Store pending plan in state for approval tracking
    tool_context.state["grounding:pending_search_plan"] = {
        "database": database,
        "query": query,
        "filters": {...}
    }

    # Return text that becomes agent response event
    return f"I propose this search:\n\n{plan_text}\n\nDo you approve?"
```

The text return value becomes an agent response event with no tool calls.

### Pattern 4: Handling Multi-Turn Approval

**Approval flow using standard user/agent events**:

```
Turn 1: Agent presents plan
  → Event: Agent text with plan + state_delta (pending_plan)

Turn 2: User responds "OK", "Short Run", "Modify", or "Cancel"
  → Event: User input with approval

Turn 3: Agent checks state
  if pending_plan and user said "OK":
      execute search
  elif user said "Short Run":
      execute with limit
  elif user said "Modify":
      ask what to change
  else:
      cancel and move to next action
```

**Implementation**:
```python
def handle_user_response(message: str, tool_context: ToolContext) -> str:
    pending_plan = tool_context.state.get("grounding:pending_search_plan")

    if not pending_plan:
        return "No pending search plan to approve."

    if message.lower() in ["ok", "yes", "approve"]:
        # Execute full search
        return execute_search(pending_plan, limit=None, tool_context=tool_context)

    elif message.lower() == "short run":
        # Execute preview
        return execute_search(pending_plan, limit=10, tool_context=tool_context)

    elif message.lower() in ["modify", "adjust"]:
        # Ask for changes
        tool_context.state["grounding:next_action"] = {
            "owner": "researcher",
            "action": "modify_plan",
            "target": pending_plan["database"],
            "due": "now"
        }
        return "What would you like to change about the search plan?"

    else:  # Cancel
        tool_context.state["grounding:pending_search_plan"] = None
        return "Search cancelled. What would you like to do next?"
```

---

## Summary: Pure ADK Event Compliance

The Research Grounding Panel achieves full functionality using **only standard ADK events**:

✅ **No custom event types required**
✅ **No ADK framework modifications**
✅ **No special event fields**

All grounding state travels via:
- `actions.state_delta` (standard ADK)
- `content.parts[].text` (standard ADK)
- `content.function_calls` (standard ADK)
- `content.function_responses` (standard ADK)

The panel is a **pure consumer** of the ADK UI Contract as documented by Google.

---

## References

- [ADK Events Documentation](https://google.github.io/adk-docs/events/)
- [ADK State Management](https://google.github.io/adk-docs/sessions/state/)
- Chapter 6 UI Contract: `textbook-adk-ch06-runtime/adk_ui_contract.md`
- Chapter 6 FastAPI Implementation: `textbook-adk-ch06-runtime/fastapi_starter.py`

---

**Document Version**: 1.0
**Last Updated**: 2025-01-25
**Maintained By**: ADK Textbook Project
