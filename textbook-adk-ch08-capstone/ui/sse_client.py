"""
SSE client for consuming ADK events.

Connects to FastAPI /run_sse endpoint and yields events as they arrive.
"""

import json
from typing import AsyncIterator, Dict, Any

import httpx


async def stream_events(
    server_url: str,
    app_name: str,
    user_id: str,
    session_id: str,
    message: str,
    state_delta: Dict[str, Any] | None = None
) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream ADK events from /run_sse endpoint.

    Args:
        server_url: Base URL of FastAPI server (e.g., "http://localhost:8000")
        app_name: ADK app name
        user_id: User identifier
        session_id: Session identifier
        message: User message text
        state_delta: Optional state delta to inject

    Yields:
        ADK Event dictionaries
    """
    url = f"{server_url}/run_sse"

    request_body = {
        "app_name": app_name,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}]
        },
        "streaming": True,
        "state_delta": state_delta
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=request_body) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                # SSE format: "data: <json>\n"
                if line.startswith("data: "):
                    event_json = line[6:]  # Strip "data: " prefix

                    try:
                        event = json.loads(event_json)
                        yield event
                    except json.JSONDecodeError:
                        # Skip malformed events
                        continue
