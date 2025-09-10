#!/usr/bin/env python3
import asyncio

import httpx

from .artifact_consumer import ArtifactEventConsumer
from .consumer import ADKChatApp
from .event_extractor import extract_description_from_event


async def main():
    print("🤖 ADK Chat Application")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            chat_app = await ADKChatApp.create(client)
            # Create enhanced artifact consumer
            artifact_consumer = (
                ArtifactEventConsumer(chat_app.consumer) if chat_app.consumer else None
            )
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
                    artifact_created = []
                    async for event in chat_app.send_message(user_input):
                        if isinstance(event, dict):
                            # Use enhanced artifact consumer if available
                            if artifact_consumer:
                                enhanced_info = (
                                    artifact_consumer.extract_enhanced_event_info(event)
                                )
                                event_type_to_use = enhanced_info["type"]
                                text_to_use = enhanced_info["text"]
                                author_to_use = enhanced_info["author"]
                                function_calls = enhanced_info.get("function_calls", [])
                                function_responses = enhanced_info.get(
                                    "function_responses", []
                                )
                                error_text = enhanced_info.get("error")
                            else:
                                # Fallback to original extractor
                                extracted = extract_description_from_event(event)
                                event_type_to_use = extracted["type"]
                                text_to_use = extracted["text"]
                                author_to_use = extracted["author"]
                                function_calls = extracted.get("function_calls", [])
                                function_responses = extracted.get(
                                    "function_responses", []
                                )
                                error_text = extracted.get("error")

                            # Handle different event types with enhanced classifications
                            if event_type_to_use == "STREAMING_TEXT_CHUNK":
                                if text_to_use and author_to_use != "user":
                                    print(text_to_use, end="", flush=True)
                                    response_text += text_to_use
                            elif event_type_to_use == "COMPLETE_TEXT":
                                if text_to_use and author_to_use != "user":
                                    print(text_to_use, end="", flush=True)
                                    response_text += text_to_use
                            elif event_type_to_use == "ARTIFACT_CREATION_CALL":
                                if function_calls:
                                    print(
                                        "[📁 Creating artifact...]", end="", flush=True
                                    )
                                    # Extract artifact filename from function calls
                                    for call in function_calls:
                                        if (
                                            isinstance(call, dict)
                                            and "artifact_info" in call
                                        ):
                                            artifact_info = call["artifact_info"]
                                            filename = artifact_info.get(
                                                "filename", "unknown"
                                            )
                                            print(
                                                f"[📁 Creating '{filename}'...]",
                                                end="",
                                                flush=True,
                                            )
                                            break
                            elif event_type_to_use == "ARTIFACT_CREATION_RESPONSE":
                                if function_responses:
                                    print(
                                        "[📁 Artifact created successfully]",
                                        end="",
                                        flush=True,
                                    )
                                    # Track created artifacts
                                    for resp in function_responses:
                                        if (
                                            isinstance(resp, dict)
                                            and resp.get("name") == "save_text_artifact"
                                        ):
                                            response_data = resp.get("response", {})
                                            if isinstance(response_data, dict):
                                                filename = response_data.get(
                                                    "filename", "artifact"
                                                )
                                                version = response_data.get(
                                                    "version", 0
                                                )
                                                artifact_created.append(
                                                    f"{filename} v{version}"
                                                )
                            elif event_type_to_use == "TOOL_CALL":
                                if function_calls:
                                    print(
                                        f"[🔧 Tool call: {len(function_calls)} functions]",
                                        end="",
                                        flush=True,
                                    )
                            elif event_type_to_use == "TOOL_RESULT":
                                if function_responses:
                                    print(
                                        "[✅ Tool results received]", end="", flush=True
                                    )
                            elif event_type_to_use == "ARTIFACT_UPDATE":
                                print("[📁 Artifacts updated]", end="", flush=True)
                            elif event_type_to_use == "ERROR":
                                print(
                                    f"\n❌ Agent error: {error_text}",
                                    end="",
                                    flush=True,
                                )

                    print()  # New line after response

                    # Show artifact summary if any were created
                    if artifact_created:
                        print(f"📁 Artifacts created: {', '.join(artifact_created)}")

                    # Show conversation summary from enhanced consumer
                    if artifact_consumer:
                        summary = artifact_consumer.get_conversation_summary()
                        if summary["total_artifacts"] > 0:
                            print(
                                f"💾 Total artifacts in session: {summary['total_artifacts']}"
                            )

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
