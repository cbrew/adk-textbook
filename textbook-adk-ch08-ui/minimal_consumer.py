# adk_chat_httpx.py
import asyncio
import json
import httpx
import uuid





class ADKConsumer:
    BASE_URL = "http://localhost:8000"
    APP_NAME = "simple_chat_agent"
    USER_ID = "u_123"
    SESSION_ID = str(uuid.uuid4())
    def __init__(self, client: httpx.AsyncClient):
        self.client: httpx.AsyncClient = client

    @classmethod
    async def create(cls, param):
        # Perform async operations to get resources
        resource = await _init_consumer_async(param)
        return cls(resource)

    async def message(self, text: str= "Talk to me about citation rings"):
        run_sse_url = f"{self.BASE_URL}/run_sse"
        run_payload = {
            "app_name": self.APP_NAME,
            "user_id": self.USER_ID,
            "session_id": self.SESSION_ID,
            "new_message": {
                "role": "user",
                "parts": [{"text": text}],
            },
            # Optional but fine to include:
            "streaming": True,
        }

        async with self.client.stream("POST", run_sse_url, json=run_payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                # SSE lines look like: "data: {...json...}"
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[len("data: "):])
                        yield "Event:",event
                    except json.JSONDecodeError:
                        yield "Non-JSON SSE data:",line



async def _init_consumer_async(client: httpx.AsyncClient) -> httpx.AsyncClient:
    "Helper function for creation of ADK consumer."
    create_session_url = f"{ADKConsumer.BASE_URL}/apps/{ADKConsumer.APP_NAME}/users/{ADKConsumer.USER_ID}/sessions/{ADKConsumer.SESSION_ID}"
    create_payload = {"state": {"key1": "value1", "key2": 42}}
    r = await client.post(create_session_url, json=create_payload)
    r.raise_for_status()
    return client



def print_data(prefix: str,response: dict):
    print(prefix,response)




async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        adk_consumer = await ADKConsumer.create(client)
        async for et,data in adk_consumer.message():
            print_data(et,data)


if __name__ == "__main__":
    asyncio.run(main())
