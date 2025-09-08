#!/usr/bin/env python3
import asyncio

import httpx
from adk_consumer import ADKChatApp
from event_extractor import extract_description_from_event


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

                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("👋 Goodbye!")
                        break

                    if not user_input:
                        continue

                    print("🤖 Agent: ", end="", flush=True)

                    # Send message and stream response
                    response_text = ""
                    async for event in chat_app.send_message(user_input):
                        if isinstance(event, dict):
                            # Extract structured event information using event extractor
                            extracted = extract_description_from_event(event)
                            
                            # Handle different event types
                            if extracted["type"] == "STREAMING_TEXT_CHUNK":
                                if extracted["text"] and extracted["author"] != "user":
                                    print(extracted["text"], end="", flush=True)
                                    response_text += extracted["text"]
                            elif extracted["type"] == "COMPLETE_TEXT":
                                if extracted["text"] and extracted["author"] != "user":
                                    print(extracted["text"], end="", flush=True)
                                    response_text += extracted["text"]
                            elif extracted["type"] == "TOOL_CALL":
                                if extracted["function_calls"]:
                                    print(f"[🔧 Tool call: {len(extracted['function_calls'])} functions]", end="", flush=True)
                            elif extracted["type"] == "TOOL_RESULT":
                                if extracted["function_responses"]:
                                    print(f"[✅ Tool results received]", end="", flush=True)
                            elif extracted["type"] == "ERROR":
                                print(f"\n❌ Agent error: {extracted['error']}", end="", flush=True)

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
