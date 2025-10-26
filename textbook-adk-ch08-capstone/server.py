"""
FastAPI server implementing ADK UI Contract.

Mock agent that demonstrates grounding state updates via real ADK events.
"""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from services import MockSessionService, MockMemoryService, MockArtifactService


# ============================================================================
# Request/Response Models
# ============================================================================

class NewMessagePart(BaseModel):
    text: str = ""


class NewMessage(BaseModel):
    role: str = "user"
    parts: list[NewMessagePart]


class RunRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    new_message: NewMessage
    streaming: bool = True
    state_delta: dict | None = None


# ============================================================================
# FastAPI App & Services
# ============================================================================

app = FastAPI(title="Research Grounding Panel Server")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock services
session_service = MockSessionService()
memory_service = MockMemoryService()
artifact_service = MockArtifactService()


# ============================================================================
# Mock Agent Logic
# ============================================================================

async def mock_agent_run(
    user_message: str,
    current_state: dict,
    invocation_id: str
) -> AsyncGenerator[dict, None]:
    """
    Mock agent that demonstrates grounding state updates.

    Yields ADK-compliant events:
    1. User input event
    2. Agent response with state_delta
    3. Turn complete
    """

    # Event 1: User input (echo)
    yield {
        "author": "user",
        "content": {
            "parts": [{"text": user_message}]
        },
        "invocation_id": invocation_id,
        "id": f"evt_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).timestamp(),
        "turn_complete": False
    }

    # Determine response based on user message
    message_lower = user_message.lower()

    # Check for grounding updates
    state_delta = {}
    agent_response = ""

    if "search" in message_lower or "find" in message_lower:
        # Simulate search
        state_delta = {
            "grounding:research_question": user_message,
            "grounding:stage": "retrieval",
            "grounding:papers_found": 34,
            "grounding:databases_searched": ["Semantic Scholar"],
            "grounding:search_assumptions": ["2020-present", "Peer-reviewed only"],
            "grounding:open_questions": ["Include preprints?", "Missing European research?"],
            "grounding:next_action": {
                "owner": "agent",
                "action": "search",
                "target": "arXiv",
                "due": "5pm today"
            }
        }
        agent_response = f"I'll search for papers on: {user_message}\n\nFound 34 papers in Semantic Scholar. Next, I'll search arXiv for preprints."

    elif "hello" in message_lower or "hi" in message_lower:
        state_delta = {
            "grounding:research_question": "Getting started",
            "grounding:stage": "scoping",
            "grounding:next_action": {
                "owner": "researcher",
                "action": "provide_query",
                "target": "search topic",
                "due": "now"
            }
        }
        agent_response = "Hello! I'm ready to help with your literature review. What would you like to search for?"

    else:
        # Generic echo
        agent_response = f"Received: {user_message}"

    # Event 2: State delta (if any)
    if state_delta:
        yield {
            "author": "research_agent",
            "content": None,
            "actions": {
                "state_delta": state_delta
            },
            "invocation_id": invocation_id,
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).timestamp(),
            "turn_complete": False
        }

    # Event 3: Agent response
    yield {
        "author": "research_agent",
        "content": {
            "parts": [{"text": agent_response}]
        },
        "invocation_id": invocation_id,
        "id": f"evt_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).timestamp(),
        "turn_complete": False
    }

    # Event 4: Turn complete
    yield {
        "author": "research_agent",
        "content": None,
        "invocation_id": invocation_id,
        "id": f"evt_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).timestamp(),
        "turn_complete": True
    }


# ============================================================================
# ADK UI Contract Endpoints
# ============================================================================

@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"ok": True, "service": "research_grounding_panel"}


@app.post("/run_sse")
async def run_sse(req: RunRequest):
    """
    SSE streaming endpoint (ADK UI Contract).

    Streams events as they are generated.
    """
    # Get or create session
    session = await session_service.get_session(
        req.app_name, req.user_id, req.session_id
    )
    if not session:
        session = await session_service.create_session(
            req.app_name, req.user_id, req.session_id, state={}
        )

    # Apply incoming state_delta if provided
    if req.state_delta:
        await session_service.update_state(
            req.app_name, req.user_id, req.session_id, req.state_delta
        )

    # Get current state
    session = await session_service.get_session(
        req.app_name, req.user_id, req.session_id
    )
    current_state = session.state

    # Generate invocation ID
    invocation_id = f"inv_{uuid.uuid4().hex[:12]}"

    # Extract user message
    user_message = ""
    if req.new_message.parts:
        user_message = req.new_message.parts[0].text

    async def event_generator():
        """Generate SSE events."""
        async for event in mock_agent_run(user_message, current_state, invocation_id):
            # Update session state if state_delta present
            if event.get("actions", {}).get("state_delta"):
                await session_service.update_state(
                    req.app_name,
                    req.user_id,
                    req.session_id,
                    event["actions"]["state_delta"]
                )

            # Store event
            await session_service.add_event(
                req.app_name, req.user_id, req.session_id, event
            )

            # Yield as SSE
            yield {
                "event": "message",
                "data": event
            }

    return EventSourceResponse(event_generator())


@app.post("/run")
async def run(req: RunRequest):
    """
    Non-streaming endpoint (ADK UI Contract).

    Returns all events at once.
    """
    # Get or create session
    session = await session_service.get_session(
        req.app_name, req.user_id, req.session_id
    )
    if not session:
        session = await session_service.create_session(
            req.app_name, req.user_id, req.session_id, state={}
        )

    # Apply incoming state_delta
    if req.state_delta:
        await session_service.update_state(
            req.app_name, req.user_id, req.session_id, req.state_delta
        )

    session = await session_service.get_session(
        req.app_name, req.user_id, req.session_id
    )
    current_state = session.state

    invocation_id = f"inv_{uuid.uuid4().hex[:12]}"

    user_message = ""
    if req.new_message.parts:
        user_message = req.new_message.parts[0].text

    # Collect all events
    events = []
    async for event in mock_agent_run(user_message, current_state, invocation_id):
        if event.get("actions", {}).get("state_delta"):
            await session_service.update_state(
                req.app_name,
                req.user_id,
                req.session_id,
                event["actions"]["state_delta"]
            )

        await session_service.add_event(
            req.app_name, req.user_id, req.session_id, event
        )

        events.append(event)

    return events


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/apps/{app_name}/users/{user_id}/sessions")
async def list_sessions(app_name: str, user_id: str):
    """List all sessions for a user."""
    sessions = await session_service.list_sessions(app_name, user_id)
    return {"sessions": [{"id": s.id, "state": s.state} for s in sessions]}


@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def create_session(
    app_name: str,
    user_id: str,
    session_id: str,
    state: dict | None = None
):
    """Create a new session."""
    session = await session_service.create_session(
        app_name, user_id, session_id, state=state or {}
    )
    return {"created": True, "session": {"id": session.id, "state": session.state}}


@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session(app_name: str, user_id: str, session_id: str):
    """Delete a session."""
    deleted = await session_service.delete_session(app_name, user_id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
