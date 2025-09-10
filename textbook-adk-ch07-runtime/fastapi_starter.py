from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import BaseMemoryService
from google.adk.runners import Runner

# If you don't want memory yet, pass None (many setups do).
# Later: replace with your own MemoryService implementation.
# type: ignore
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

# 👉 Research State Agent - demonstrates state_delta capabilities
# This agent tracks research topics and progress in session state
from research_state_agent import root_agent
from sse_starlette.sse import EventSourceResponse


def build_runner(app_name: str = "my_app") -> Runner:
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    memory_service: BaseMemoryService | None = None  # or your custom memory

    return Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )


runner = build_runner()

app = FastAPI(title="Custom ADK API Server (In-Memory)")


# ---------
# Schemas
# ---------
class NewMessagePart(BaseModel):
    text: str = ""


class NewMessage(BaseModel):
    role: str = "user"
    parts: list[NewMessagePart]


class RunRequest(BaseModel):
    app_name: str | None = None
    user_id: str
    session_id: str
    new_message: NewMessage
    streaming: bool = True
    state_delta: dict | None = None


class CreateSessionRequest(BaseModel):
    app_name: str | None = None
    user_id: str
    session_id: str
    state: dict | None = None


# -------------
# Health + Sessions
# -------------
@app.get("/healthz")
async def healthz():
    return {"ok": True, "app": "my_app"}


# Contract-compliant session endpoints
@app.get("/apps/{app_name}/users/{user_id}/sessions")
async def list_sessions(app_name: str, user_id: str):
    """List all sessions for a user in an app."""
    try:
        sessions = await runner.session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list sessions: {str(e)}"
        )


@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def create_session_by_path(
    app_name: str, user_id: str, session_id: str, state: dict | None = None
):
    """Create a new session with optional initial state."""
    try:
        sess = await runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {},
        )
        return {"created": True, "session": sess}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session(app_name: str, user_id: str, session_id: str):
    """Delete a session."""
    try:
        await runner.session_service.delete_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete session: {str(e)}"
        )


# Legacy endpoints for backward compatibility
@app.post("/sessions")
async def create_session_legacy(req: CreateSessionRequest):
    sess = await runner.session_service.create_session(
        app_name=req.app_name or "my_app",
        user_id=req.user_id,
        session_id=req.session_id,
        state=req.state or {},
    )
    return {"created": True, "session": sess}


@app.get("/sessions/{user_id}/{session_id}")
async def get_session_legacy(user_id: str, session_id: str):
    sess = await runner.session_service.get_session(
        app_name="my_app", user_id=user_id, session_id=session_id
    )
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": sess}


# -------------
# Chat (non-streaming)
# -------------
@app.post("/run")
async def run(req: RunRequest):
    """
    Non-streaming call that consumes a user message and returns the final ADK result.
    """
    # Create proper ADK Content object
    content = types.Content(
        role=req.new_message.role,
        parts=[types.Part(text=p.text) for p in req.new_message.parts],
    )

    # Collect all events for non-streaming response
    events = []
    async for ev in runner.run_async(
        user_id=req.user_id,
        session_id=req.session_id,
        new_message=content,
        state_delta=req.state_delta,
    ):
        events.append(ev)
    return events


# -------------
# Chat (SSE streaming)
# -------------
@app.post("/run_sse")
async def run_sse(req: RunRequest):
    """
    SSE endpoint that streams ADK events as they are produced.
    """
    cfg = RunConfig(streaming_mode=StreamingMode.SSE)
    # Create proper ADK Content object - handle empty parts for state-only updates
    content = types.Content(
        role=req.new_message.role,
        parts=[types.Part(text=p.text) for p in req.new_message.parts],
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        async for ev in runner.run_async(
            user_id=req.user_id,
            session_id=req.session_id,
            new_message=content,
            state_delta=req.state_delta,
            run_config=cfg
        ):
            # Format as proper SSE data event - EventSourceResponse handles data: prefix
            sse_event = ev.model_dump_json(exclude_none=True, by_alias=True)
            yield sse_event
    return EventSourceResponse(event_generator())


# -------------
# Optional Artifacts Endpoints for UI Compatibility
# -------------
@app.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts")
async def list_artifacts(app_name: str, user_id: str, session_id: str):
    """List all artifacts for a session."""
    if not runner.artifact_service:
        raise HTTPException(status_code=503, detail="Artifact service not available")
    try:
        artifact_keys = await runner.artifact_service.list_artifact_keys(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        return {"artifacts": artifact_keys}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list artifacts: {str(e)}"
        )


@app.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{filename}")
async def get_artifact(app_name: str, user_id: str, session_id: str, filename: str):
    """Get a specific artifact by filename."""
    if not runner.artifact_service:
        raise HTTPException(status_code=503, detail="Artifact service not available")
    try:
        artifact = await runner.artifact_service.load_artifact(
            app_name=app_name, user_id=user_id, session_id=session_id, filename=filename
        )
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return {"artifact": artifact}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Artifact not found")
        raise HTTPException(status_code=500, detail=f"Failed to get artifact: {str(e)}")


# -------------
# Research Management Endpoints - ADK-compliant external state management
# -------------
class SetPriorityRequest(BaseModel):
    priority_level: str  # "High", "Medium", "Low"

@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}/research/priority")
async def set_research_priority(
    app_name: str, user_id: str, session_id: str, req: SetPriorityRequest
):
    """Set research priority using ADK-compliant agent tool invocation."""
    try:
        # Create a system message that triggers the agent tool
        system_message = (
            f"Please set the research priority to {req.priority_level} "
            f"using the set_research_priority_tool."
        )

        events = []
        async for ev in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="system",
                parts=[types.Part(text=system_message)]
            ),
        ):
            events.append(ev)
        return {"updated": True, "priority_level": req.priority_level, "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set priority: {str(e)}")


class SetDeadlineRequest(BaseModel):
    deadline: str

@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}/research/deadline")
async def set_research_deadline(
    app_name: str, user_id: str, session_id: str, req: SetDeadlineRequest
):
    """Set research deadline using ADK-compliant agent tool invocation."""
    try:
        # Create a system message that triggers the agent tool
        system_message = (
            f"Please set the research deadline to {req.deadline} "
            f"using the set_research_deadline_tool."
        )

        events = []
        async for ev in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="system",
                parts=[types.Part(text=system_message)]
            ),
        ):
            events.append(ev)
        return {"updated": True, "deadline": req.deadline, "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set deadline: {str(e)}")


class AddSourceRequest(BaseModel):
    title: str
    url: str
    type: str = "article"  # article, paper, book, etc.

@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}/research/sources")
async def add_research_source(
    app_name: str, user_id: str, session_id: str, req: AddSourceRequest
):
    """Add research source using ADK-compliant agent tool invocation."""
    try:
        # Create a system message that triggers the agent tool
        system_message = (
            f"Please add this research source using the add_research_source_tool: "
            f"title='{req.title}', url='{req.url}', type='{req.type}'"
        )

        events = []
        async for ev in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="system",
                parts=[types.Part(text=system_message)]
            ),
        ):
            events.append(ev)
        return {
            "updated": True,
            "source": {"title": req.title, "url": req.url, "type": req.type},
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add source: {str(e)}")


if __name__ == "__main__":
    from pathlib import Path

    import uvicorn
    from dotenv import load_dotenv

    env_path = Path.cwd() / "postgres_chat_agent" / ".env"
    load_dotenv(env_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)
