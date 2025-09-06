#!/usr/bin/env python3
"""
Interactive chat agent with PostgreSQL persistence.

This demonstrates the same pattern as saptak's adk-masterclass example
but using our custom PostgreSQL services instead of SQLite.

IMPORTANT: This implementation only works when run directly (python main.py).
The standard ADK CLI commands (adk web, adk run) use ADK's default services,
not our custom PostgreSQL services. To use PostgreSQL services, run this
script directly or use the programmatic Runner approach shown here.
"""

import asyncio
import uuid

from agent import agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from utils import call_agent_async

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

# Load environment variables
load_dotenv()


async def handle_slash_command(
    command,
    session_service,
    memory_service,
    artifact_service,
    app_name,
    user_id,
    session_id,
):
    """Handle slash commands for direct service access."""
    parts = command.strip().split(" ", 1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "/help":
        print("📚 Available Slash Commands:")
        print("  /memory <query>     - Search research memory directly")
        print("  /save <topic>       - Save current discussion topic to memory")
        print("  /artifacts          - List saved research artifacts")
        print("  /session            - Show current session information")
        print("  /help               - Show this help message")

    elif cmd == "/memory":
        if not arg:
            print("💭 Usage: /memory <search query>")
            print("   Example: /memory machine learning papers")
            return

        print(f"🔍 Searching research memory for: '{arg}'")
        try:
            response = await memory_service.search_memory(
                app_name=app_name, user_id=user_id, query=arg
            )

            if not response.memories:
                print(
                    f"📝 No research memory found for '{arg}'. Start a conversation to build memory!"
                )
            else:
                print(f"📚 Found {len(response.memories)} relevant research memories:")
                for i, memory in enumerate(response.memories[:5], 1):
                    content_preview = (
                        str(memory.content)[:150] + "..."
                        if len(str(memory.content)) > 150
                        else str(memory.content)
                    )
                    print(f"  {i}. {content_preview}")

        except Exception as e:
            print(f"❌ Memory search failed: {e}")

    elif cmd == "/save":
        topic = arg if arg else "current research discussion"
        print(f"💾 Saving '{topic}' to research memory...")

        try:
            # Create a session entry to save to memory
            session = await session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

            # Add current session context to memory
            await memory_service.add_session_to_memory(session)

            # Update session state
            updated_state = session.state.copy()
            updated_state["memory_saves"] = updated_state.get("memory_saves", 0) + 1
            updated_state["last_memory_save"] = topic

            session_service.update_session_state(
                session_id=session_id,
                state=updated_state,
                app_name=app_name,
                user_id=user_id,
            )

            print(
                f"✅ Saved '{topic}' to research memory! (Total saves: {updated_state['memory_saves']})"
            )

        except Exception as e:
            print(f"❌ Memory save failed: {e}")

    elif cmd == "/artifacts":
        print("📁 Listing research artifacts...")
        try:
            artifacts = await artifact_service.list_artifact_keys(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

            if not artifacts:
                print(
                    "📄 No artifacts found. Use save_artifact tool to create research documents!"
                )
            else:
                print(f"📚 Found {len(artifacts)} research artifact(s):")
                for i, artifact_key in enumerate(artifacts, 1):
                    print(f"  {i}. {artifact_key}")

        except Exception as e:
            print(f"❌ Artifact listing failed: {e}")

    elif cmd == "/session":
        print("📱 Current Research Session Information:")
        try:
            session = await session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

            print(f"  🆔 Session ID: {session.id}")
            print(f"  👤 User ID: {user_id}")
            print(f"  📅 Created: {getattr(session, 'created_at', 'Unknown')}")
            print(f"  🔄 Updated: {getattr(session, 'updated_at', 'Unknown')}")
            print(f"  📊 State: {session.state}")

        except Exception as e:
            print(f"❌ Session info retrieval failed: {e}")

    else:
        print(f"❓ Unknown command: {cmd}")
        print("💡 Type /help for available commands")


async def main():
    """Main agent loop with PostgreSQL persistence."""
    print("🐘 Initializing PostgreSQL Chat Agent...")

    # Initialize PostgreSQL runtime
    runtime = await PostgreSQLADKRuntime.create_and_initialize()

    # Get our custom PostgreSQL services
    session_service = runtime.get_session_service()
    memory_service = runtime.get_memory_service()
    artifact_service = runtime.get_artifact_service()

    # Define initial state for new sessions
    initial_state = {
        "username": "User",
        "conversation_count": 0,
        "memory_saves": 0,
        "artifacts_created": 0,
        "total_interactions": 0,
    }

    # Application and user identifiers
    app_name = "postgres_chat_agent"
    user_id = "demo_user"

    print(f"📱 App: {app_name} | User: {user_id}")

    # Check if we have an existing session for this user
    try:
        sessions_response = await session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )

        # Handle the response properly - it has a sessions attribute
        existing_sessions = (
            sessions_response.sessions if hasattr(sessions_response, "sessions") else []
        )

        if existing_sessions and len(existing_sessions) > 0:
            # Use the most recent existing session
            session_id = existing_sessions[0].id
            print(f"📂 Continuing existing session: {session_id}")

            # Get current state
            current_session = await session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            if current_session:
                current_state = current_session.state
                print(f"📊 Session state: {current_state}")
            else:
                print("⚠️ Could not retrieve session state")

        else:
            # Create a new session
            session_id = str(uuid.uuid4())
            new_session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=initial_state,
            )
            session_id = new_session.id
            print(f"✨ Created new session: {session_id}")

    except Exception as e:
        print(f"❌ Error managing sessions: {e}")
        return

    # Create a runner with our agent and PostgreSQL services
    print("🔄 Creating ADK Runner with PostgreSQL services...")
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )
    print("✅ Runner created with PostgreSQL backend!")

    # Interactive chat loop
    print("\n" + "=" * 70)
    print("🎓 Academic Research Assistant - PostgreSQL Edition")
    print(
        "💡 Features: Persistent research memory, academic artifact storage, session continuity"
    )
    print(
        "🛠️  Available tools: search_research_memory, track_research_progress, save_artifact, list_artifacts"
    )
    print("")
    print("📚 Slash Commands for Direct Service Access:")
    print("  /memory <query>     - Search research memory directly")
    print("  /save <topic>       - Save current discussion to memory")
    print("  /artifacts          - List saved research artifacts")
    print("  /session            - Show current session info")
    print("  /help               - Show this help message")
    print("")
    print("⚡ Type 'exit' or 'quit' to end | Focus: Academic research workflows")
    print("=" * 70)

    try:
        while True:
            user_input = input("\n🗣️  You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break

            if user_input.strip() == "":
                continue

            # Handle slash commands for direct service access
            if user_input.startswith("/"):
                try:
                    await handle_slash_command(
                        user_input,
                        session_service,
                        memory_service,
                        artifact_service,
                        app_name,
                        user_id,
                        session_id,
                    )
                    continue
                except Exception as e:
                    print(f"❌ Slash command error: {e}")
                    continue

            print("🎓 Assistant: ", end="", flush=True)

            try:
                # Use the utility function to call agent
                response = await call_agent_async(
                    runner=runner, user_input=user_input, session_id=session_id
                )

                print(response)

                # Update interaction counter
                try:
                    current_session = await session_service.get_session(
                        app_name=app_name, user_id=user_id, session_id=session_id
                    )

                    if current_session:
                        updated_state = current_session.state.copy()
                    else:
                        updated_state = {"total_interactions": 0, "conversation_count": 0}
                    updated_state["total_interactions"] = (
                        updated_state.get("total_interactions", 0) + 1
                    )
                    updated_state["conversation_count"] = (
                        updated_state.get("conversation_count", 0) + 1
                    )

                    session_service.update_session_state(
                        session_id=session_id,
                        state=updated_state,
                        app_name=app_name,
                        user_id=user_id,
                    )

                except Exception as state_error:
                    print(
                        f"\n⚠️  Warning: Could not update session state: {state_error}"
                    )

            except Exception as e:
                print(f"❌ Error calling agent: {e}")

    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")

    finally:
        # Cleanup PostgreSQL runtime
        print("🧹 Cleaning up PostgreSQL runtime...")
        await runtime.shutdown()
        print("✅ Cleanup complete!")


if __name__ == "__main__":
    asyncio.run(main())
