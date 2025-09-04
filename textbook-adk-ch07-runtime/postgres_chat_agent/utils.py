"""
Utility functions for PostgreSQL chat agent.

Adapted from saptak's adk-masterclass example to work with our PostgreSQL services.
"""

import asyncio
from google.genai import types

async def call_agent_async(runner, user_input, session_id):
    """
    Process a user query through the agent asynchronously.
    
    Args:
        runner: ADK Runner instance with PostgreSQL services
        user_input: User's input message
        session_id: Current session ID
        
    Returns:
        str: Agent's response text
    """
    # Create content from the user query
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
    
    # Get the session to see state before processing
    try:
        session = await runner.session_service.get_session(
            app_name="postgres_chat_agent",
            user_id="demo_user", 
            session_id=session_id
        )
        print(f"\n📊 State before processing: {session.state}")
    except Exception as e:
        print(f"⚠️  Could not retrieve session state before processing: {e}")
    
    # Run the agent with the user query
    try:
        response = await runner.run_async(
            user_id="demo_user",
            session_id=session_id,
            content=content
        )
        
        # Process the response
        final_response_text = None
        
        for event in response.events:
            if event.type == "content" and event.content.role == "agent":
                final_response_text = event.content.parts[0].text
                break
        
        # Get updated session to see state after processing
        try:
            session = await runner.session_service.get_session(
                app_name="postgres_chat_agent",
                user_id="demo_user",
                session_id=session_id
            )
            print(f"📊 State after processing: {session.state}")
        except Exception as e:
            print(f"⚠️  Could not retrieve session state after processing: {e}")
        
        return final_response_text or "I apologize, but I couldn't generate a response."
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        return f"Sorry, I encountered an error: {e}"

async def display_session_info(session_service, app_name="postgres_chat_agent", user_id="demo_user", session_id=None):
    """
    Display information about current session(s).
    
    Args:
        session_service: PostgreSQL session service instance
        app_name: Application name
        user_id: User identifier  
        session_id: Specific session ID (optional)
    """
    try:
        if session_id:
            # Display specific session
            session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            print(f"📱 Session {session.id}:")
            print(f"   Created: {session.created_at}")
            print(f"   Updated: {session.updated_at}")
            print(f"   State: {session.state}")
        else:
            # List all sessions for user
            sessions = await session_service.list_sessions(
                app_name=app_name,
                user_id=user_id
            )
            print(f"📋 Found {len(sessions)} session(s) for {user_id}:")
            for i, session in enumerate(sessions, 1):
                print(f"   {i}. {session.id} (updated: {session.updated_at})")
                
    except Exception as e:
        print(f"❌ Error retrieving session info: {e}")

async def search_conversation_history(memory_service, query, app_name="postgres_chat_agent", user_id="demo_user"):
    """
    Search conversation history using semantic memory.
    
    Args:
        memory_service: PostgreSQL memory service instance
        query: Search query
        app_name: Application name
        user_id: User identifier
        
    Returns:
        str: Formatted search results
    """
    try:
        response = await memory_service.search_memory(
            app_name=app_name,
            user_id=user_id,
            query=query
        )
        
        if not response.memories:
            return f"🔍 No conversation history found for '{query}'"
            
        results = []
        for i, memory in enumerate(response.memories[:3], 1):  # Top 3 results
            content_preview = str(memory.content)[:100] + "..." if len(str(memory.content)) > 100 else str(memory.content)
            results.append(f"{i}. {content_preview}")
            
        return f"🔍 Found {len(response.memories)} relevant conversations for '{query}':\n" + "\n".join(results)
        
    except Exception as e:
        return f"❌ Error searching conversation history: {e}"

async def list_user_artifacts(artifact_service, app_name="postgres_chat_agent", user_id="demo_user", session_id=None):
    """
    List artifacts for a user or session.
    
    Args:
        artifact_service: PostgreSQL artifact service instance
        app_name: Application name
        user_id: User identifier
        session_id: Optional session ID filter
        
    Returns:
        str: Formatted artifact list
    """
    try:
        # List artifacts using the service's list method
        artifacts = await artifact_service.list_artifact_keys(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if not artifacts:
            scope = f"session {session_id}" if session_id else f"user {user_id}"
            return f"📁 No artifacts found for {scope}"
            
        results = []
        for i, artifact_key in enumerate(artifacts, 1):
            results.append(f"{i}. {artifact_key}")
            
        scope = f"session {session_id}" if session_id else f"user {user_id}"
        return f"📁 Found {len(artifacts)} artifact(s) for {scope}:\n" + "\n".join(results)
        
    except Exception as e:
        return f"❌ Error listing artifacts: {e}"

def format_response_for_display(response_text):
    """
    Format agent response for better display in terminal.
    
    Args:
        response_text: Raw response from agent
        
    Returns:
        str: Formatted response
    """
    if not response_text:
        return "💭 (No response generated)"
        
    # Add some basic formatting for better readability
    lines = response_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('*'):
            # Bullet points - add emoji
            formatted_lines.append(f"  • {stripped[1:].strip()}")
        elif stripped.startswith('-'):
            # Dash points - add emoji
            formatted_lines.append(f"  • {stripped[1:].strip()}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)