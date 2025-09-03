#!/usr/bin/env python3
"""
PostgreSQL-backed tools for ADK agent.

Provides persistent memory, session management, and artifact storage
using the adk_runtime PostgreSQL services.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

logger = logging.getLogger(__name__)

# Global runtime instance for tool functions
_runtime: Optional[PostgreSQLADKRuntime] = None
_current_session = None
_user_id = os.getenv("ADK_USER_ID", "adk_user")
_app_name = "postgres_chat_agent"


async def _ensure_runtime():
    """Ensure the PostgreSQL runtime is initialized."""
    global _runtime, _current_session
    
    if _runtime is None:
        try:
            _runtime = await PostgreSQLADKRuntime.create_and_initialize()
            logger.info("PostgreSQL runtime initialized for agent tools")
            
            # Create initial session
            session_service = _runtime.get_session_service()
            _current_session = await session_service.create_session(
                app_name=_app_name,
                user_id=_user_id,
                state={
                    "created_at": datetime.now().isoformat(),
                    "conversation_count": 0,
                    "memory_saves": 0,
                    "artifacts_created": 0
                }
            )
            logger.info(f"Created agent session: {_current_session.id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL runtime: {e}")
            raise


async def search_memory(query: str) -> str:
    """
    Search persistent memory for relevant past conversations and information.
    
    Args:
        query: Search query to find relevant memories and past conversations
        
    Returns:
        String describing search results with relevant context
    """
    await _ensure_runtime()
    
    try:
        memory_service = _runtime.get_memory_service()
        
        # Search memory
        response = await memory_service.search_memory(
            app_name=_app_name,
            user_id=_user_id,
            query=query
        )
        
        if not response.memories:
            return f"🔍 No relevant memories found for '{query}'. This might be our first conversation about this topic!"
        
        # Format results with context
        results = []
        for i, memory in enumerate(response.memories[:3], 1):  # Top 3 results
            session_id = memory.session_id[:8]
            
            # Try to extract meaningful content
            content = memory.content
            if isinstance(content, dict):
                # Extract conversation snippet if available
                conversation = content.get("conversation", [])
                if conversation:
                    last_messages = conversation[-2:]  # Last 2 messages
                    snippet = " | ".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}..." 
                                        for msg in last_messages])
                else:
                    snippet = str(content)[:100] + "..."
            else:
                snippet = str(content)[:100] + "..."
            
            results.append(f"{i}. Session {session_id}...: {snippet}")
        
        result_text = f"🧠 Found {len(response.memories)} relevant memories for '{query}':\n\n" + "\n".join(results)
        
        if len(response.memories) > 3:
            result_text += f"\n\n(Showing top 3 of {len(response.memories)} results)"
        
        return result_text
        
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return f"❌ Memory search failed: {e}"


async def save_to_memory() -> str:
    """
    Save the current conversation context to persistent memory for future reference.
    
    Returns:
        String confirming the save operation
    """
    await _ensure_runtime()
    
    try:
        memory_service = _runtime.get_memory_service()
        session_service = _runtime.get_session_service()
        
        # Update session state
        current_state = _current_session.state.copy()
        current_state["memory_saves"] = current_state.get("memory_saves", 0) + 1
        current_state["last_memory_save"] = datetime.now().isoformat()
        
        # Update the session
        session_service.update_session_state(
            session_id=_current_session.id,
            state=current_state,
            app_name=_app_name,
            user_id=_user_id
        )
        
        # Refresh session object
        updated_session = await session_service.get_session(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id
        )
        
        global _current_session
        _current_session = updated_session
        
        # Add to persistent memory
        await memory_service.add_session_to_memory(_current_session)
        
        saves_count = current_state["memory_saves"]
        return f"💾 Conversation saved to persistent memory! This session has {saves_count} memory saves. I'll be able to reference this conversation in future sessions."
        
    except Exception as e:
        logger.error(f"Save to memory failed: {e}")
        return f"❌ Failed to save to memory: {e}"


async def save_artifact(filename: str, content: str) -> str:
    """
    Save content as a persistent artifact file that can be retrieved later.
    
    Args:
        filename: Name of the file to save
        content: Content to save in the artifact file
        
    Returns:
        String confirming the save operation with version info
    """
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        session_service = _runtime.get_session_service()
        
        # Create artifact
        from google.genai import types
        artifact = types.Part(text=content)
        
        # Save artifact
        version = await artifact_service.save_artifact(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id,
            filename=filename,
            artifact=artifact
        )
        
        # Update session state
        current_state = _current_session.state.copy()
        current_state["artifacts_created"] = current_state.get("artifacts_created", 0) + 1
        current_state["last_artifact"] = {
            "filename": filename,
            "version": version,
            "created_at": datetime.now().isoformat()
        }
        
        session_service.update_session_state(
            session_id=_current_session.id,
            state=current_state,
            app_name=_app_name,
            user_id=_user_id
        )
        
        # Refresh session
        updated_session = await session_service.get_session(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id
        )
        
        global _current_session
        _current_session = updated_session
        
        artifacts_count = current_state["artifacts_created"]
        return f"📁 Saved artifact '{filename}' as version {version}! Content size: {len(content)} characters. This session has created {artifacts_count} artifacts total."
        
    except Exception as e:
        logger.error(f"Save artifact failed: {e}")
        return f"❌ Failed to save artifact '{filename}': {e}"


async def list_artifacts() -> str:
    """
    List all saved artifact files for the current session.
    
    Returns:
        String listing all artifacts with their details
    """
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        
        # Get artifact list
        artifact_keys = await artifact_service.list_artifact_keys(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id
        )
        
        if not artifact_keys:
            return "📁 No artifacts saved in this session yet. Use save_artifact to create some!"
        
        # Get details for each artifact
        artifacts_info = []
        for filename in artifact_keys:
            try:
                # Get versions
                versions = await artifact_service.list_versions(
                    app_name=_app_name,
                    user_id=_user_id,
                    session_id=_current_session.id,
                    filename=filename
                )
                
                latest_version = max(versions) if versions else 0
                artifacts_info.append(f"• {filename} (v{latest_version}, {len(versions)} versions)")
                
            except Exception as e:
                artifacts_info.append(f"• {filename} (error: {e})")
        
        result = f"📁 Artifacts in this session ({len(artifact_keys)} files):\n\n" + "\n".join(artifacts_info)
        result += "\n\nUse load_artifact to retrieve any of these files."
        
        return result
        
    except Exception as e:
        logger.error(f"List artifacts failed: {e}")
        return f"❌ Failed to list artifacts: {e}"


async def load_artifact(filename: str) -> str:
    """
    Load and display content from a previously saved artifact file.
    
    Args:
        filename: Name of the artifact file to load
        
    Returns:
        String with the artifact content or error message
    """
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        
        # Load the artifact
        artifact = await artifact_service.load_artifact(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id,
            filename=filename
        )
        
        if not artifact:
            return f"❌ Artifact '{filename}' not found. Use list_artifacts to see available files."
        
        # Extract content
        if hasattr(artifact, 'text'):
            content = artifact.text
        else:
            content = str(artifact)
        
        # Format response
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        result = f"📄 Loaded artifact '{filename}':\n\n{content_preview}"
        
        if len(content) > 500:
            result += f"\n\n(Showing first 500 characters of {len(content)} total)"
        
        return result
        
    except Exception as e:
        logger.error(f"Load artifact failed: {e}")
        return f"❌ Failed to load artifact '{filename}': {e}"


# Cleanup function (called when agent shuts down)
async def cleanup_tools():
    """Cleanup function to shutdown the runtime when agent stops."""
    global _runtime
    if _runtime:
        await _runtime.shutdown()
        _runtime = None
        logger.info("PostgreSQL runtime shut down")