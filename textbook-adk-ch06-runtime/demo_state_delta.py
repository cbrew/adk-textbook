#!/usr/bin/env python3
"""
Demo script showing state_delta functionality with the enhanced FastAPI starter.

This script demonstrates:
1. Creating a session
2. Normal user interaction
3. External state mutations using state_delta (point 4 from the contract)
4. How the agent responds to state changes

Run the FastAPI server first: python fastapi_starter.py
Then run this demo: python demo_state_delta.py
"""

import asyncio
from typing import Any

import httpx


class ADKStateDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.app_name = "research_app"
        self.user_id = "demo_user"
        self.session_id = "demo_session_001"

    async def create_session(self):
        """Create a new session."""
        print("🔧 Creating session...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}",
                json={"research:current_topic": "Machine Learning Research"}
            )
            print(f"✅ Session created: {response.json()}")

    async def user_interaction(self, message: str):
        """Send a normal user message."""
        print(f"\n💬 User: {message}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/run",
                json={
                    "app_name": self.app_name,
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "new_message": {
                        "role": "user",
                        "parts": [{"text": message}]
                    }
                }
            )
            events = response.json()
            print(f"🤖 Agent response: {events}")

    async def external_state_update(self, endpoint: str, data: dict[str, Any]):
        """Demonstrate external state mutation via state_delta."""
        print(f"\n🔄 External system updating {endpoint}: {data}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}{endpoint}",
                json=data
            )
            result = response.json()
            print(f"✅ State updated: {result}")

    async def state_delta_injection(self, state_delta: dict[str, Any]):
        """Direct state_delta injection through /run_sse."""
        print(f"\n🎯 Direct state_delta injection: {state_delta}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/run",
                json={
                    "app_name": self.app_name,
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "new_message": {
                        "role": "system",
                        "parts": []  # Empty parts for state-only update
                    },
                    "state_delta": state_delta
                }
            )
            events = response.json()
            print(f"🎯 State delta result: {events}")

    async def run_demo(self):
        """Run the complete demo."""
        print("🚀 Starting ADK State Delta Demo")
        print("=" * 50)

        try:
            # 1. Create session
            await self.create_session()

            # 2. Normal user interaction
            await self.user_interaction(
                "Hello! I'm starting research on neural networks."
            )

            # 3. External state mutations (point 4 from contract)
            await self.external_state_update(
                "/research/priority", {"priority_level": "High"}
            )

            await self.external_state_update(
                "/research/deadline", {"deadline": "2024-02-15"}
            )

            await self.external_state_update("/research/sources", {
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "type": "paper"
            })

            # 4. Direct state_delta injection (contract compatibility)
            await self.state_delta_injection({
                "research:current_topic": "Transformer Architectures",
                "research:progress": [
                    "Literature review completed",
                    "Initial experiments designed",
                ]
            })

            # 5. See how agent responds to all the state changes
            await self.user_interaction("What's my current research status?")

            print("\n🎉 Demo completed successfully!")
            print("\nThis demonstrates how external components can inject state_delta")
            print("updates into ADK sessions while maintaining event sourcing and")
            print("contract compatibility with the Angular UI.")

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print("Make sure the FastAPI server is running: python fastapi_starter.py")


if __name__ == "__main__":
    demo = ADKStateDemo()
    asyncio.run(demo.run_demo())

