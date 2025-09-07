#!/usr/bin/env python3
import asyncio

import httpx
from adk_consumer import ADKChatApp


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

