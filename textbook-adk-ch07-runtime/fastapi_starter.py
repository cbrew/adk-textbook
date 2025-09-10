from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import BaseMemoryService
from google.adk.runners import Runner
from google.genai import types


# If you don't want memory yet, pass None (many setups do).
# Later: replace with your own MemoryService implementation.
# type: ignore
from google.adk.sessions import InMemorySessionService

# 👉 Provide your actual ADK agent here
# It should be the same kind of root agent you'd pass to ADK's Runner elsewhere.
from  postgres_chat_agent import root_agent  # TODO: replace with your agent factory/object
from pydantic import BaseModel
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
    text: str


class NewMessage(BaseModel):
    role: str = "user"
    parts: list[NewMessagePart]


class RunRequest(BaseModel):
    app_name: str | None = None
    user_id: str
    session_id: str
    new_message: NewMessage


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


@app.post("/sessions")
async def create_session(req: CreateSessionRequest):
    sess = await runner.session_service.create_session(
        app_name=req.app_name or "my_app",
        user_id=req.user_id,
        session_id=req.session_id,
        state=req.state or {},
    )
    return {"created": True, "session": sess}


@app.get("/sessions/{user_id}/{session_id}")
async def get_session(user_id: str, session_id: str):
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
    
    final = None
    async for ev in runner.run_async(
        user_id=req.user_id,
        session_id=req.session_id,
        new_message=content,
    ):
        final = ev
    return {"result": final}


# -------------
# Chat (SSE streaming)
# -------------
@app.post("/run_sse")
async def run_sse(req: RunRequest):
    """
    SSE endpoint that streams ADK events as they are produced.
    """
    cfg = RunConfig(streaming_mode=StreamingMode.SSE)
    # Create proper ADK Content object
    content = types.Content(
        role=req.new_message.role,
        parts=[types.Part(text=p.text) for p in req.new_message.parts],
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        async for ev in runner.run_async(
            user_id=req.user_id,
            session_id=req.session_id,
            new_message=content,
            run_config=cfg
        ):
            sse_event = ev.model_dump_json(exclude_none=True, by_alias=True)
            yield sse_event
    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    from pathlib import Path
    from dotenv import load_dotenv

    env_path = Path.cwd() / "postgres_chat_agent" / ".env"
    load_dotenv(env_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)
