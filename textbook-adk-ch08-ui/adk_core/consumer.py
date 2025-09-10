"""
Shared ADK consumer module for interacting with ADK web server.

This module provides reusable classes for connecting to and communicating
with ADK agents via HTTP streaming API.
"""

import json
import uuid
from collections.abc import AsyncGenerator

import httpx


class ADKConsumer:
    """Client for consuming ADK agent responses via streaming API."""

    BASE_URL = "http://localhost:8000"
    APP_NAME = "simple_chat_agent"
    USER_ID = "u_123"

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.session_id = str(uuid.uuid4())

    @classmethod
    async def create(cls, client: httpx.AsyncClient):
        """Create and initialize a new ADK consumer instance."""
        instance = cls(client)
        await instance._init_session()
        return instance

    async def _init_session(self):
        """Initialize the ADK session."""
        create_session_url = (
            f"{self.BASE_URL}/apps/{self.APP_NAME}/users/{self.USER_ID}/"
            f"sessions/{self.session_id}"
        )
        create_payload = {"state": {"key1": "value1", "key2": 42}}
        r = await self.client.post(create_session_url, json=create_payload)
        r.raise_for_status()

    async def message(
        self, text: str = "Talk to me about citation rings"
    ) -> AsyncGenerator[tuple[str, dict | str], None]:
        """Send a message to the agent and yield streaming responses."""
        run_sse_url = f"{self.BASE_URL}/run_sse"
        run_payload = {
            "app_name": self.APP_NAME,
            "user_id": self.USER_ID,
            "session_id": self.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": text}],
            },
            "streaming": True,
        }

        async with self.client.stream("POST", run_sse_url, json=run_payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[len("data: ") :])
                        yield "Event:", event
                    except json.JSONDecodeError:
                        yield "Non-JSON SSE data:", str(line)


class ADKChatApp:
    """Higher-level chat application interface built on ADKConsumer."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.consumer: ADKConsumer | None = None

    @classmethod
    async def create(cls, client: httpx.AsyncClient):
        """Create and initialize a new ADK chat app instance."""
        instance = cls(client)
        instance.consumer = await ADKConsumer.create(client)
        return instance

    async def send_message(self, text: str) -> AsyncGenerator[dict, None]:
        """Send a message to the agent and yield streaming responses."""
        if not self.consumer:
            raise RuntimeError("ADK consumer not initialized")

        async for event_type, event_data in self.consumer.message(text):
            if event_type == "Event:" and isinstance(event_data, dict):
                yield event_data
