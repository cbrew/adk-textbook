#!/usr/bin/env python3
"""
Example agent with PostgreSQL persistence.

This demonstrates how to build an ADK agent that uses PostgreSQL services
for session management, memory storage, and artifact handling.

Usage:
    # From textbook root directory:
    uv run python textbook-adk-ch07-runtime/examples/basic_agent.py

Prerequisites:
    # Start PostgreSQL services first:
    cd textbook-adk-ch07-runtime && make dev-setup
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PersistentChatAgent:
    """
    A simple chat agent that demonstrates PostgreSQL service integration.
    
    Features:
    - Persistent conversation sessions
    - Semantic memory for context retrieval  
    - Artifact storage for file handling
    """

    def __init__(self, app_name: str = "persistent_chat_agent"):
        self.app_name = app_name
        self.runtime = None
        self.session_service = None
        self.memory_service = None
        self.artifact_service = None
        self.current_session = None

    async def start(self) -> None:
        """Initialize the agent and PostgreSQL runtime."""
        logger.info(f"🚀 Starting {self.app_name}...")

        try:
            # Initialize PostgreSQL runtime
            self.runtime = await PostgreSQLADKRuntime.create_and_initialize()

            # Get service references
            self.session_service = self.runtime.get_session_service()
            self.memory_service = self.runtime.get_memory_service()
            self.artifact_service = self.runtime.get_artifact_service()

            logger.info("✅ PostgreSQL services initialized successfully!")

        except Exception as e:
            logger.error(f"❌ Failed to start agent: {e}")
            raise

    async def stop(self) -> None:
        """Shutdown the agent and cleanup resources."""
        logger.info("🔄 Shutting down agent...")

        if self.runtime:
            await self.runtime.shutdown()
            logger.info("✅ Agent shutdown complete")

    async def create_or_resume_session(self, user_id: str, session_id: str = None) -> str:
        """Create a new session or resume an existing one."""

        if session_id:
            # Try to resume existing session
            logger.info(f"🔍 Attempting to resume session: {session_id}")
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )

            if session:
                self.current_session = session
                logger.info(f"✅ Resumed session: {session_id}")
                return session_id
            else:
                logger.warning(f"⚠️  Session {session_id} not found, creating new session")

        # Create new session
        initial_state = {
            "conversation": [],
            "created_at": datetime.now().isoformat(),
            "message_count": 0,
            "topics": []
        }

        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            state=initial_state
        )

        self.current_session = session
        logger.info(f"✅ Created new session: {session.id}")
        return session.id

    async def process_message(self, user_id: str, message: str) -> str:
        """Process a user message and return a response."""

        if not self.current_session:
            raise RuntimeError("No active session. Call create_or_resume_session first.")

        logger.info(f"💬 Processing message from {user_id}: {message[:50]}...")

        # Update conversation state
        current_state = self.current_session.state.copy()
        current_state["conversation"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        current_state["message_count"] += 1

        # Simple response generation (in real agent, this would use LLM)
        response = self._generate_response(message, current_state)

        current_state["conversation"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # Update session state
        self.session_service.update_session_state(
            session_id=self.current_session.id,
            state=current_state,
            app_name=self.app_name,
            user_id=user_id
        )

        # Get updated session
        updated_session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=self.current_session.id
        )

        self.current_session = updated_session

        # Add to semantic memory if conversation is getting substantial
        if current_state["message_count"] % 10 == 0:
            await self._save_to_memory(user_id)

        logger.info(f"✅ Response generated: {response[:50]}...")
        return response

    async def search_conversation_history(self, user_id: str, query: str) -> list[dict[str, Any]]:
        """Search past conversations for relevant context."""
        logger.info(f"🔍 Searching conversation history for: {query}")

        search_response = await self.memory_service.search_memory(
            app_name=self.app_name,
            user_id=user_id,
            query=query
        )

        relevant_memories = []
        for memory in search_response.memories:
            # Parse memory content back to conversation format
            try:
                conversation_data = memory.content
                if isinstance(conversation_data, dict) and "conversation" in conversation_data:
                    relevant_memories.append({
                        "session_id": memory.session_id,
                        "created_at": conversation_data.get("created_at"),
                        "conversation_snippet": conversation_data["conversation"][-4:],  # Last 4 messages
                        "topics": conversation_data.get("topics", [])
                    })
            except Exception as e:
                logger.warning(f"Failed to parse memory content: {e}")

        logger.info(f"📋 Found {len(relevant_memories)} relevant conversation memories")
        return relevant_memories

    async def save_conversation_artifact(self, user_id: str, filename: str, content: str) -> int:
        """Save conversation data as an artifact."""
        if not self.current_session:
            raise RuntimeError("No active session")

        logger.info(f"💾 Saving conversation artifact: {filename}")

        # Create artifact from conversation content
        from google.genai import types
        artifact = types.Part(text=content)

        version = await self.artifact_service.save_artifact(
            app_name=self.app_name,
            user_id=user_id,
            session_id=self.current_session.id,
            filename=filename,
            artifact=artifact
        )

        logger.info(f"✅ Saved artifact version {version}: {filename}")
        return version

    async def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """List all sessions for a user."""
        logger.info(f"📋 Listing sessions for user: {user_id}")

        response = await self.session_service.list_sessions(
            app_name=self.app_name,
            user_id=user_id
        )

        session_summaries = []
        for session in response.sessions:
            state = session.state
            session_summaries.append({
                "session_id": session.id,
                "created_at": state.get("created_at"),
                "message_count": state.get("message_count", 0),
                "topics": state.get("topics", []),
                "last_message": state.get("conversation", [])[-1] if state.get("conversation") else None
            })

        logger.info(f"📋 Found {len(session_summaries)} sessions")
        return session_summaries

    def _generate_response(self, message: str, state: dict[str, Any]) -> str:
        """Generate a simple response (placeholder for LLM integration)."""

        message_lower = message.lower()
        message_count = state.get("message_count", 0)

        # Simple rule-based responses for demo
        if "hello" in message_lower or "hi" in message_lower:
            return f"Hello! This is message #{message_count} in our conversation. How can I help you today?"

        elif "memory" in message_lower or "remember" in message_lower:
            return f"I have access to persistent memory! I can remember our conversations across sessions. We've exchanged {message_count} messages so far."

        elif "session" in message_lower:
            return f"This is session {self.current_session.id[:8]}... I can maintain state across our entire conversation!"

        elif "artifact" in message_lower or "file" in message_lower:
            return "I can save and retrieve files using the artifact service! Try asking me to save something."

        elif "save" in message_lower:
            return "I can save our conversation or any content as artifacts. What would you like me to save?"

        else:
            responses = [
                f"Interesting point! (Message #{message_count})",
                f"I understand. This conversation is being persisted in PostgreSQL. (Message #{message_count})",
                f"Thanks for sharing that! Our session {self.current_session.id[:8]}... is tracking everything. (Message #{message_count})",
                f"That's helpful context! I can search our conversation history later. (Message #{message_count})"
            ]
            return responses[message_count % len(responses)]

    async def _save_to_memory(self, user_id: str) -> None:
        """Save current session to semantic memory."""
        try:
            await self.memory_service.add_session_to_memory(self.current_session)
            logger.info(f"💾 Saved session to memory: {self.current_session.id[:8]}...")
        except Exception as e:
            logger.warning(f"Failed to save to memory: {e}")


async def run_interactive_demo():
    """Run an interactive demo of the persistent chat agent."""

    agent = PersistentChatAgent()
    user_id = "demo_user_123"

    try:
        # Start the agent
        await agent.start()

        print("\n" + "="*60)
        print("🤖 PERSISTENT CHAT AGENT DEMO")
        print("="*60)
        print("This agent demonstrates PostgreSQL service integration:")
        print("- Persistent conversation sessions")
        print("- Semantic memory for context")
        print("- Artifact storage capabilities")
        print("\nCommands:")
        print("- 'sessions' - List all sessions")
        print("- 'search <query>' - Search conversation history")
        print("- 'save <filename>' - Save conversation as artifact")
        print("- 'new' - Start new session")
        print("- 'quit' - Exit demo")
        print("="*60)

        # Create or resume session
        session_id = await agent.create_or_resume_session(user_id)
        print(f"\n📱 Session active: {session_id[:8]}...")

        # Interactive loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    break

                elif user_input.lower() == 'sessions':
                    sessions = await agent.list_sessions(user_id)
                    print(f"\n📋 Your Sessions ({len(sessions)}):")
                    for sess in sessions[-5:]:  # Show last 5
                        print(f"  • {sess['session_id'][:8]}... - {sess['message_count']} messages")
                        if sess['last_message']:
                            print(f"    Last: {sess['last_message']['content'][:50]}...")
                    continue

                elif user_input.lower().startswith('search '):
                    query = user_input[7:].strip()
                    memories = await agent.search_conversation_history(user_id, query)
                    print(f"\n🔍 Search Results for '{query}':")
                    for mem in memories:
                        print(f"  • Session {mem['session_id'][:8]}... - {len(mem['conversation_snippet'])} messages")
                        if mem['conversation_snippet']:
                            print(f"    Snippet: {mem['conversation_snippet'][-1]['content'][:50]}...")
                    continue

                elif user_input.lower().startswith('save '):
                    filename = user_input[5:].strip()
                    if not filename:
                        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

                    # Create conversation summary
                    conversation = agent.current_session.state.get("conversation", [])
                    content = f"Conversation Export - Session {session_id}\n"
                    content += f"Created: {agent.current_session.state.get('created_at')}\n"
                    content += f"Messages: {len(conversation)}\n\n"

                    for msg in conversation:
                        content += f"{msg['role'].upper()}: {msg['content']}\n"
                        content += f"Time: {msg['timestamp']}\n\n"

                    version = await agent.save_conversation_artifact(user_id, filename, content)
                    print(f"\n💾 Saved conversation as '{filename}' (version {version})")
                    continue

                elif user_input.lower() == 'new':
                    session_id = await agent.create_or_resume_session(user_id)
                    print(f"\n📱 New session started: {session_id[:8]}...")
                    continue

                # Process regular message
                response = await agent.process_message(user_id, user_input)
                print(f"🤖 Agent: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Demo error: {e}")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        print("\n💡 Make sure PostgreSQL services are running:")
        print("   cd textbook-adk-ch07-runtime && make dev-setup")

    finally:
        # Cleanup
        await agent.stop()
        print("\n✅ Agent stopped. Thanks for trying the demo!")


async def run_automated_example():
    """Run an automated example showing key features."""

    agent = PersistentChatAgent()
    user_id = "example_user_456"

    try:
        print("\n🤖 Running Automated PostgreSQL Agent Example...")
        print("="*50)

        # Start agent
        await agent.start()

        # Create session
        session_id = await agent.create_or_resume_session(user_id)
        print(f"✅ Session created: {session_id[:8]}...")

        # Simulate conversation
        messages = [
            "Hello! I'm testing the PostgreSQL agent.",
            "Can you remember our conversation?",
            "Tell me about your memory capabilities.",
            "I'd like to save this conversation.",
            "How many sessions do I have?",
            "Search for previous conversations about memory.",
            "This demonstrates persistent state management!"
        ]

        print("\n💬 Conversation:")
        for i, message in enumerate(messages, 1):
            print(f"\n{i}. User: {message}")
            response = await agent.process_message(user_id, message)
            print(f"   Agent: {response}")

            # Add small delay for realism
            await asyncio.sleep(0.5)

        # Demonstrate memory search
        print("\n🔍 Searching conversation history...")
        memories = await agent.search_conversation_history(user_id, "memory capabilities")
        print(f"   Found {len(memories)} relevant conversations")

        # Save artifact
        print("\n💾 Saving conversation artifact...")
        conversation_text = "Example conversation demonstrating PostgreSQL integration"
        version = await agent.save_conversation_artifact(
            user_id,
            "example_conversation.txt",
            conversation_text
        )
        print(f"   Saved as version {version}")

        # List sessions
        print("\n📋 Listing user sessions...")
        sessions = await agent.list_sessions(user_id)
        print(f"   User has {len(sessions)} total sessions")

        print("\n✅ Automated example completed successfully!")

    except Exception as e:
        print(f"❌ Automated example failed: {e}")
        logger.error(f"Automated example error: {e}")

    finally:
        await agent.stop()


async def main():
    """Main entry point - choose demo mode."""

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await run_interactive_demo()
    else:
        await run_automated_example()
        print("\n💡 Run with --interactive for interactive demo:")
        print("   uv run python textbook-adk-ch07-runtime/examples/basic_agent.py --interactive")


if __name__ == "__main__":
    asyncio.run(main())
