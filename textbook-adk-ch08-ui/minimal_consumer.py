# adk_chat_httpx.py
import asyncio
import json
import httpx
import uuid

BASE_URL = "http://localhost:8000"
APP_NAME = "simple_chat_agent"
USER_ID = "u_123"
SESSION_ID =  str(uuid.uuid4())

async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        # 1) Create/Update the session (matches your first curl)
        create_session_url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
        create_payload = {"state": {"key1": "value1", "key2": 42}}
        r = await client.post(create_session_url, json=create_payload)
        r.raise_for_status()
        print("Session upserted:", r.json().get("id", SESSION_ID))

        # 2) Stream a chat turn via /run_sse (matches your second curl)
        run_sse_url = f"{BASE_URL}/run_sse"
        run_payload = {
            "app_name": APP_NAME,
            "user_id": USER_ID,
            "session_id": SESSION_ID,
            "new_message": {
                "role": "user",
                "parts": [{"text": "Talk to me about citation rings"}],
            },
            # Optional but fine to include:
            "streaming": True,
        }

        async with client.stream("POST", run_sse_url, json=run_payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                # SSE lines look like: "data: {...json...}"
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[len("data: "):])
                    except json.JSONDecodeError:
                        print("Non-JSON SSE data:", line)
                        continue
                    print("Event:", event)

if __name__ == "__main__":
    asyncio.run(main())
