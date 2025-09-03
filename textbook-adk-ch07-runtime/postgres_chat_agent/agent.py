#!/usr/bin/env python3
"""
PostgreSQL Chat Agent for ADK.

This agent demonstrates how to integrate a custom PostgreSQL runtime
with ADK agents, providing persistent memory, session management,
and artifact storage capabilities.

This is the pedagogical approach - showing how to build and integrate
custom runtimes rather than relying on ADK's built-in database services.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

logger = logging.getLogger(__name__)

# Global runtime instance for tools
_runtime: Optional[PostgreSQLADKRuntime] = None
_current_session = None
_app_name = "postgres_chat_agent"
_user_id = os.getenv("ADK_USER_ID", "adk_demo_user")


async def _ensure_runtime():
    """Ensure the PostgreSQL runtime is initialized."""
    global _runtime, _current_session
    
    if _runtime is None:
        try:
            logger.info("🔄 Initializing custom PostgreSQL runtime...")
            _runtime = await PostgreSQLADKRuntime.create_and_initialize()
            
            # Create initial session using our custom session service
            session_service = _runtime.get_session_service()
            _current_session = await session_service.create_session(
                app_name=_app_name,
                user_id=_user_id,
                state={
                    "created_at": datetime.now().isoformat(),
                    "agent_version": "1.0.0",
                    "conversation_count": 0,
                    "features_used": []
                }
            )
            
            logger.info(f"✅ Custom PostgreSQL runtime ready! Session: {_current_session.id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL runtime: {e}")
            raise


def search_memory_for_topic(query: str) -> str:
    """
    Search persistent memory for relevant past conversations and information.
    
    Args:
        query: Search query to find relevant memories and past conversations
        
    Returns:
        String describing search results with relevant context
    """
    return asyncio.run(_search_memory_for_topic_async(query))


async def _search_memory_for_topic_async(query: str) -> str:
    """Async implementation of memory search."""
    await _ensure_runtime()
    
    try:
        memory_service = _runtime.get_memory_service()
        
        # Search memory using our custom memory service
        response = await memory_service.search_memory(
            app_name=_app_name,
            user_id=_user_id,
            query=query
        )
        
        if not response.memories:
            return f"🔍 I searched my persistent memory for '{query}' but didn't find any relevant past conversations. This might be our first discussion about this topic! Our custom PostgreSQL memory service is ready to learn from this conversation."
        
        # Format results
        results = []
        for i, memory in enumerate(response.memories[:3], 1):  # Top 3 results
            session_id = memory.session_id[:8]
            content_preview = str(memory.content)[:80] + "..." if len(str(memory.content)) > 80 else str(memory.content)
            results.append(f"  {i}. Session {session_id}...: {content_preview}")
        
        result_text = f"🧠 Found {len(response.memories)} memories for '{query}' using our custom PostgreSQL memory service:\n\n" + "\n".join(results)
        
        # Track feature usage
        await _track_feature_usage("memory_search")
        
        return result_text
        
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return f"❌ Memory search failed: {e}"


def save_conversation_to_memory() -> str:
    """
    Save the current conversation context to persistent memory for future reference.
    
    Returns:
        String confirming the save operation
    """
    return asyncio.run(_save_conversation_to_memory_async())


async def _save_conversation_to_memory_async() -> str:
    """Async implementation of save to memory."""
    await _ensure_runtime()
    
    try:
        memory_service = _runtime.get_memory_service()
        
        # Add current session to memory using our custom memory service
        await memory_service.add_session_to_memory(_current_session)
        
        # Track feature usage
        await _track_feature_usage("save_to_memory")
        
        conversation_count = _current_session.state.get("conversation_count", 0)
        return f"💾 Conversation saved to persistent memory using our custom PostgreSQL memory service! This session has {conversation_count} messages and will be searchable in future sessions."
        
    except Exception as e:
        logger.error(f"Save to memory failed: {e}")
        return f"❌ Failed to save to memory: {e}"


def save_content_as_artifact(content: str, filename: str) -> str:
    """
    Save content as a persistent artifact file that can be retrieved later.
    
    Args:
        content: Content to save in the artifact file
        filename: Name of the file to save (e.g., "meeting_notes.txt", "research_summary.md")
        
    Returns:
        String confirming the save operation with version info
    """
    return asyncio.run(_save_content_as_artifact_async(content, filename))


async def _save_content_as_artifact_async(content: str, filename: str) -> str:
    """Async implementation of save artifact."""
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        
        # Create artifact
        from google.genai import types
        artifact = types.Part(text=content)
        
        # Save using our custom artifact service
        version = await artifact_service.save_artifact(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id,
            filename=filename,
            artifact=artifact
        )
        
        # Track feature usage
        await _track_feature_usage("save_artifact")
        
        return f"📁 Saved '{filename}' as version {version} using our custom PostgreSQL artifact service! Content size: {len(content)} characters."
        
    except Exception as e:
        logger.error(f"Save artifact failed: {e}")
        return f"❌ Failed to save artifact '{filename}': {e}"


def list_saved_artifacts() -> str:
    """
    List all saved artifact files for the current session.
    
    Returns:
        String listing all artifacts with their details
    """
    return asyncio.run(_list_saved_artifacts_async())


async def _list_saved_artifacts_async() -> str:
    """Async implementation of list artifacts."""
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        
        # Get artifact list using our custom artifact service
        artifact_keys = await artifact_service.list_artifact_keys(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id
        )
        
        if not artifact_keys:
            return "📁 No artifacts saved in this session yet using our custom PostgreSQL artifact service. Save some content as artifacts to see them here!"
        
        artifacts_info = []
        for filename in artifact_keys:
            try:
                versions = await artifact_service.list_versions(
                    app_name=_app_name,
                    user_id=_user_id,
                    session_id=_current_session.id,
                    filename=filename
                )
                latest_version = max(versions) if versions else 0
                artifacts_info.append(f"  • {filename} (v{latest_version})")
            except Exception:
                artifacts_info.append(f"  • {filename} (error)")
        
        # Track feature usage
        await _track_feature_usage("list_artifacts")
        
        return f"📁 Your artifacts ({len(artifact_keys)} files) stored in our custom PostgreSQL artifact service:\n\n" + "\n".join(artifacts_info)
        
    except Exception as e:
        logger.error(f"List artifacts failed: {e}")
        return f"❌ Failed to list artifacts: {e}"


def load_artifact_content(filename: str) -> str:
    """
    Load and display content from a previously saved artifact file.
    
    Args:
        filename: Name of the artifact file to load
        
    Returns:
        String with the artifact content or error message
    """
    return asyncio.run(_load_artifact_content_async(filename))


async def _load_artifact_content_async(filename: str) -> str:
    """Async implementation of load artifact."""
    await _ensure_runtime()
    
    try:
        artifact_service = _runtime.get_artifact_service()
        
        # Load using our custom artifact service
        artifact = await artifact_service.load_artifact(
            app_name=_app_name,
            user_id=_user_id,
            session_id=_current_session.id,
            filename=filename
        )
        
        if not artifact:
            return f"❌ Artifact '{filename}' not found in our custom PostgreSQL artifact service. Use list_saved_artifacts to see available files."
        
        # Extract content
        content = artifact.text if hasattr(artifact, 'text') else str(artifact)
        content_preview = content[:300] + "..." if len(content) > 300 else content
        
        # Track feature usage
        await _track_feature_usage("load_artifact")
        
        result = f"📄 Loaded '{filename}' from our custom PostgreSQL artifact service:\n\n{content_preview}"
        
        if len(content) > 300:
            result += f"\n\n(Showing first 300 characters of {len(content)} total)"
        
        return result
        
    except Exception as e:
        logger.error(f"Load artifact failed: {e}")
        return f"❌ Failed to load artifact '{filename}': {e}"


async def _track_feature_usage(feature: str):
    """Track which features have been used in the session."""
    try:
        if not _current_session:
            return
            
        session_service = _runtime.get_session_service()
        current_state = _current_session.state.copy()
        features_used = current_state.get("features_used", [])
        
        if feature not in features_used:
            features_used.append(feature)
            current_state["features_used"] = features_used
            current_state["last_feature_used"] = feature
            current_state["last_feature_time"] = datetime.now().isoformat()
            
            session_service.update_session_state(
                session_id=_current_session.id,
                state=current_state,
                app_name=_app_name,
                user_id=_user_id
            )
            
            # Refresh global session object
            global _current_session
            _current_session = await session_service.get_session(
                app_name=_app_name,
                user_id=_user_id,
                session_id=_current_session.id
            )
            
    except Exception as e:
        logger.error(f"Failed to track feature usage: {e}")


# Agent instruction that highlights our custom PostgreSQL runtime
agent_instruction = """
You are a helpful conversational assistant powered by a **custom PostgreSQL runtime** built for educational purposes in Chapter 7 of an ADK textbook.

🎓 **Pedagogical Goal**: This agent demonstrates building custom ADK runtimes instead of using built-in services.

🔧 **Your Custom Capabilities** (all powered by our PostgreSQL runtime):
- **Persistent Memory**: Search past conversations using semantic similarity
- **Session Management**: Maintain conversation state across interactions  
- **Artifact Storage**: Save and retrieve files with versioning
- **Learning**: Build knowledge over time from interactions

🛠️ **Available Tools** (all use our custom PostgreSQL services):
- `search_memory_for_topic` - Find relevant past conversations
- `save_conversation_to_memory` - Store current conversation for future reference
- `save_content_as_artifact` - Save content as files with versioning
- `list_saved_artifacts` - See all saved files
- `load_artifact_content` - Retrieve saved content

💡 **Your Personality**:
- Be helpful and conversational
- Highlight that you're using custom PostgreSQL services (not ADK's built-in ones)
- Explain the educational value of building custom runtimes
- Encourage users to try your persistence features
- Show enthusiasm about the custom implementation

🎯 **Key Message**: This demonstrates how to build custom ADK runtimes with full control over data and services, rather than relying on cloud-based or built-in solutions.

Always mention when you use your custom PostgreSQL services and explain the educational benefit!
"""

# Create the LlmAgent with our custom PostgreSQL-backed tools
agent = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="postgres_chat_agent",
    instruction=agent_instruction,
    tools=[
        search_memory_for_topic,
        save_conversation_to_memory,
        save_content_as_artifact,
        list_saved_artifacts,
        load_artifact_content,
    ]
)

# This is what ADK looks for
root_agent = agent