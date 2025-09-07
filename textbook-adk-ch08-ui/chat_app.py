#!/usr/bin/env python3
import asyncio
import json
import httpx
import uuid
from typing import AsyncGenerator


class ADKChatApp:
    BASE_URL = "http://localhost:8000"
    APP_NAME = "simple_chat_agent"
    USER_ID = "u_123"
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.session_id = str(uuid.uuid4())

    @classmethod
    async def create(cls, client: httpx.AsyncClient):
        instance = cls(client)
        await instance._init_session()
        return instance

    async def _init_session(self):
        """Initialize the ADK session"""
        create_session_url = f"{self.BASE_URL}/apps/{self.APP_NAME}/users/{self.USER_ID}/sessions/{self.session_id}"
        create_payload = {"state": {"key1": "value1", "key2": 42}}
        r = await self.client.post(create_session_url, json=create_payload)
        r.raise_for_status()

    async def send_message(self, text: str) -> AsyncGenerator[dict, None]:
        """Send a message to the agent and yield streaming responses"""
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
                        event = json.loads(line[len("data: "):])
                        yield event
                    except json.JSONDecodeError:
                        continue


async def main():
    print("🤖 ADK Chat Application")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            chat_app = await ADKChatApp.create(client)
            print("✅ Connected to ADK agent")
            
            while True:
                try:
                    # Get user input
                    user_input = input("\n👤 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    print("🤖 Agent: ", end="", flush=True)
                    
                    # Send message and stream response
                    response_text = ""
                    async for event in chat_app.send_message(user_input):
                        # Handle ADK SSE events based on the documented structure
                        if isinstance(event, dict):
                            # Check if this is an agent response with content
                            if event.get("author") and event.get("author") != "user":
                                content = event.get("content")
                                if content and isinstance(content, dict):
                                    parts = content.get("parts", [])
                                    for part in parts:
                                        if isinstance(part, dict) and "text" in part:
                                            text = part["text"]
                                            print(text, end="", flush=True)
                                            response_text += text
                                # Handle direct text in content
                                elif content and isinstance(content, str):
                                    print(content, end="", flush=True)
                                    response_text += content
                            # Handle events that might have direct text fields
                            elif "text" in event:
                                text = event["text"]
                                print(text, end="", flush=True)
                                response_text += text
                    
                    print()  # New line after response
                    
                except KeyboardInterrupt:
                    print("\n👋 Chat interrupted. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    print("Please try again or type 'quit' to exit.")
                    
        except Exception as e:
            print(f"❌ Failed to connect to ADK agent: {e}")
            print("Make sure the ADK server is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main())