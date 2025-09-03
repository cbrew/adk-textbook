#!/usr/bin/env python3
"""
ADK Agent with PostgreSQL persistence integration.

This demonstrates how to integrate PostgreSQL services with a standard ADK agent
that uses YAML configuration and Python tools.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

logger = logging.getLogger(__name__)


class PersistentChatTools:
    """
    Tool implementations for PostgreSQL-backed ADK agent.
    
    These tools integrate with the PostgreSQL runtime to provide
    persistent memory, session management, and artifact storage.
    """
    
    def __init__(self, app_name: str = "persistent_chat_agent"):
        self.app_name = app_name
        self.runtime = None
        self.session_service = None
        self.memory_service = None
        self.artifact_service = None
        self.current_session = None
        self.user_id = "default_user"  # In real agent, get from context
    
    async def initialize(self):
        """Initialize PostgreSQL runtime and services."""
        if self.runtime is None:
            try:
                self.runtime = await PostgreSQLADKRuntime.create_and_initialize()
                self.session_service = self.runtime.get_session_service()
                self.memory_service = self.runtime.get_memory_service()
                self.artifact_service = self.runtime.get_artifact_service()
                logger.info("PostgreSQL services initialized for agent tools")
                
                # Create or resume session
                await self._ensure_session()
                
            except Exception as e:
                logger.error(f"Failed to initialize PostgreSQL services: {e}")
                raise
    
    async def cleanup(self):
        """Cleanup resources when agent stops."""
        if self.runtime:
            await self.runtime.shutdown()
            logger.info("PostgreSQL services cleaned up")
    
    async def _ensure_session(self):
        """Ensure we have an active session."""
        if not self.current_session:
            # Create new session with initial state
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                state={
                    "created_at": datetime.now().isoformat(),
                    "tool_calls": 0,
                    "memory_saves": 0,
                    "artifacts_created": 0
                }
            )
            self.current_session = session
            logger.info(f"Created new session: {session.id}")
    
    async def save_to_memory(self) -> str:
        """
        Tool: Save current conversation context to persistent memory.
        
        This tool saves the current session state to semantic memory,
        making it searchable for future conversations.
        """
        await self.initialize()
        
        try:
            # Update session state
            current_state = self.current_session.state.copy()
            current_state["memory_saves"] += 1
            current_state["last_memory_save"] = datetime.now().isoformat()
            
            # Update session
            self.session_service.update_session_state(
                session_id=self.current_session.id,
                state=current_state,
                app_name=self.app_name,
                user_id=self.user_id
            )
            
            updated_session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.current_session.id
            )
            self.current_session = updated_session
            
            # Add to memory
            await self.memory_service.add_session_to_memory(self.current_session)
            
            return f"✅ Conversation context saved to persistent memory! This is memory save #{current_state['memory_saves']} for this session."
            
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")
            return f"❌ Failed to save to memory: {e}"
    
    async def search_memory(self, query: str) -> str:
        """
        Tool: Search previous conversations for relevant context.
        
        Args:
            query: Search query for finding relevant past conversations
            
        Returns:
            String describing search results
        """
        await self.initialize()
        
        try:
            # Search memory
            response = await self.memory_service.search_memory(
                app_name=self.app_name,
                user_id=self.user_id,
                query=query
            )
            
            if not response.memories:
                return f"🔍 No previous conversations found matching '{query}'"
            
            # Format results
            results = []
            for i, memory in enumerate(response.memories[:3], 1):  # Top 3 results
                session_id = memory.session_id[:8]
                content_preview = str(memory.content)[:100] + "..." if len(str(memory.content)) > 100 else str(memory.content)
                results.append(f"{i}. Session {session_id}...: {content_preview}")
            
            result_text = f"🔍 Found {len(response.memories)} relevant conversations for '{query}':\n\n" + "\n".join(results)
            
            if len(response.memories) > 3:
                result_text += f"\n\n(Showing top 3 of {len(response.memories)} results)"
            
            return result_text
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return f"❌ Failed to search memory: {e}"
    
    async def save_artifact(self, filename: str, content: str) -> str:
        """
        Tool: Save content as a persistent artifact file.
        
        Args:
            filename: Name of the file to save
            content: Content to save in the artifact
            
        Returns:
            String describing save result
        """
        await self.initialize()
        
        try:
            # Create artifact
            from google.genai import types
            artifact = types.Part(text=content)
            
            # Save artifact
            version = await self.artifact_service.save_artifact(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.current_session.id,
                filename=filename,
                artifact=artifact
            )
            
            # Update session state
            current_state = self.current_session.state.copy()
            current_state["artifacts_created"] += 1
            current_state["last_artifact"] = {
                "filename": filename,
                "version": version,
                "created_at": datetime.now().isoformat()
            }
            
            self.session_service.update_session_state(
                session_id=self.current_session.id,
                state=current_state,
                app_name=self.app_name,
                user_id=self.user_id
            )
            
            updated_session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.current_session.id
            )
            self.current_session = updated_session
            
            return f"✅ Saved artifact '{filename}' as version {version}! This session has created {current_state['artifacts_created']} artifacts total."
            
        except Exception as e:
            logger.error(f"Failed to save artifact: {e}")
            return f"❌ Failed to save artifact '{filename}': {e}"


# Global tool instance (ADK will use this)
_tools = PersistentChatTools()

# Tool functions for ADK (must be module-level functions)
async def save_to_memory() -> str:
    """Save current conversation context to persistent memory."""
    return await _tools.save_to_memory()

async def search_memory(query: str) -> str:
    """Search previous conversations for relevant context."""
    return await _tools.search_memory(query)

async def save_artifact(filename: str, content: str) -> str:
    """Save content as a persistent artifact file."""  
    return await _tools.save_artifact(filename, content)

# Agent lifecycle hooks (if ADK supports them)
async def on_agent_start():
    """Called when agent starts."""
    await _tools.initialize()

async def on_agent_stop():
    """Called when agent stops."""
    await _tools.cleanup()


# For direct testing
if __name__ == "__main__":
    async def test_tools():
        print("🧪 Testing PostgreSQL agent tools...")
        
        tools = PersistentChatTools("test_agent")
        
        try:
            # Test save to memory
            print("\n1. Testing save_to_memory...")
            result = await tools.save_to_memory()
            print(f"   Result: {result}")
            
            # Test search memory
            print("\n2. Testing search_memory...")
            result = await tools.search_memory("conversation")
            print(f"   Result: {result}")
            
            # Test save artifact
            print("\n3. Testing save_artifact...")
            result = await tools.save_artifact(
                "test_document.txt",
                "This is a test document created by the PostgreSQL agent tools."
            )
            print(f"   Result: {result}")
            
            print("\n✅ All tool tests completed!")
            
        except Exception as e:
            print(f"❌ Tool test failed: {e}")
        
        finally:
            await tools.cleanup()
    
    asyncio.run(test_tools())