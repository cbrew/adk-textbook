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

import os
import asyncio
import uuid
from dotenv import load_dotenv

from google.adk.runners import Runner

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime
from agent import agent
from utils import call_agent_async

# Load environment variables
load_dotenv()

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
        "total_interactions": 0
    }
    
    # Application and user identifiers
    app_name = "postgres_chat_agent"
    user_id = "demo_user"
    
    print(f"📱 App: {app_name} | User: {user_id}")
    
    # Check if we have an existing session for this user
    try:
        sessions_response = await session_service.list_sessions(
            app_name=app_name,
            user_id=user_id
        )
        
        # Handle the response properly - it has a sessions attribute
        existing_sessions = sessions_response.sessions if hasattr(sessions_response, 'sessions') else []
        
        if existing_sessions and len(existing_sessions) > 0:
            # Use the most recent existing session
            session_id = existing_sessions[0].id
            print(f"📂 Continuing existing session: {session_id}")
            
            # Get current state
            current_session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            current_state = current_session.state
            print(f"📊 Session state: {current_state}")
            
        else:
            # Create a new session
            session_id = str(uuid.uuid4())
            new_session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=initial_state
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
        artifact_service=artifact_service
    )
    print("✅ Runner created with PostgreSQL backend!")
    
    # Interactive chat loop
    print("\n" + "=" * 60)
    print("🐘 PostgreSQL Chat Agent Ready!")
    print("💡 Features: Persistent sessions, semantic memory, artifact storage")
    print("🛠️  Available tools: search_memory, save_to_memory, save_artifact, list_artifacts, get_session_info")
    print("⚡ Type 'exit' or 'quit' to end")
    print("=" * 60)
    
    try:
        while True:
            user_input = input("\n🗣️  You: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            
            if user_input.strip() == '':
                continue
                
            print("🤖 Agent: ", end="", flush=True)
            
            try:
                # Use the utility function to call agent
                response = await call_agent_async(
                    runner=runner,
                    user_input=user_input,
                    session_id=session_id
                )
                
                print(response)
                
                # Update interaction counter
                try:
                    current_session = await session_service.get_session(
                        app_name=app_name,
                        user_id=user_id, 
                        session_id=session_id
                    )
                    
                    updated_state = current_session.state.copy()
                    updated_state["total_interactions"] = updated_state.get("total_interactions", 0) + 1
                    updated_state["conversation_count"] = updated_state.get("conversation_count", 0) + 1
                    
                    await session_service.update_session_state(
                        session_id=session_id,
                        state=updated_state,
                        app_name=app_name,
                        user_id=user_id
                    )
                    
                except Exception as state_error:
                    print(f"\n⚠️  Warning: Could not update session state: {state_error}")
                
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