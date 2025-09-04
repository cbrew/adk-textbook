#!/usr/bin/env python3
"""
Clean and efficient PostgreSQL driver function for Chapter 7.

This driver function adapts the SQLite implementation approach from
https://saptak.in/writing/2025/05/10/google-adk-masterclass-part6
but uses our PostgreSQL services instead.

Usage:
    # Basic usage (creates a new session)
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py

    # Interactive mode
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --interactive

    # List all sessions
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --list-sessions

    # Clear all sessions
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --clear-all-sessions

    # Test memory service
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --test-memory

    # Search memory
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --search-memory "database"

    # List all memories
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --list-memories

    # Test artifact service
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --test-artifacts

    # List all artifacts
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --list-artifacts

    # Get specific artifact
    uv run python textbook-adk-ch07-runtime/postgres_chat_agent/driver.py --get-artifact <artifact_id>
"""

import asyncio
import argparse
import logging
import uuid
from typing import Optional, Dict, List
from datetime import datetime

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime
from google.genai import types

logger = logging.getLogger(__name__)


class PostgreSQLChatDriver:
    """Clean driver for PostgreSQL-backed chat sessions using ADK services."""
    
    def __init__(self, app_name: str = "postgres_chat_driver"):
        self.app_name = app_name
        self.user_id = "user123"  # Default demo user
        self.runtime: Optional[PostgreSQLADKRuntime] = None
    
    async def initialize(self):
        """Initialize PostgreSQL runtime and services."""
        logger.info("🔄 Initializing PostgreSQL runtime...")
        self.runtime = await PostgreSQLADKRuntime.create_and_initialize()
        logger.info("✅ PostgreSQL runtime initialized")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.runtime:
            await self.runtime.shutdown()
            logger.info("🧹 Runtime shutdown complete")
    
    async def create_session(self, session_id: str, initial_state: Optional[Dict] = None) -> Dict:
        """
        Create a new session using PostgreSQL session service.
        
        Args:
            session_id: Unique identifier for the session
            initial_state: Optional initial state data
            
        Returns:
            Dictionary with session creation result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        
        session_service = self.runtime.get_session_service()
        
        # Set default initial state
        state = initial_state or {
            "created_at": datetime.now().isoformat(),
            "message_count": 0,
            "topics": []
        }
        
        try:
            await session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id,
                state=state
            )
            
            logger.info(f"✅ Created session: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "app_name": self.app_name,
                "user_id": self.user_id,
                "initial_state": state
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create session {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve an existing session from PostgreSQL.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        session_service = self.runtime.get_session_service()
        
        try:
            session = await session_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            
            if session:
                logger.info(f"📋 Retrieved session: {session_id}")
                return {
                    "session_id": session_id,
                    "data": session,
                    "found": True
                }
            else:
                logger.warning(f"⚠️  Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving session {session_id}: {e}")
            return None
    
    async def list_sessions(self) -> List[Dict]:
        """
        List all sessions for the current user and app.
        
        Returns:
            List of session information
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        session_service = self.runtime.get_session_service()
        
        try:
            sessions_response = await session_service.list_sessions(
                app_name=self.app_name,
                user_id=self.user_id
            )
            
            # Handle the response properly - it might be a response object with sessions attribute
            if hasattr(sessions_response, 'sessions'):
                sessions_list = sessions_response.sessions
            else:
                sessions_list = sessions_response
            
            logger.info(f"📝 Found {len(sessions_list) if sessions_list else 0} sessions")
            return [
                {
                    "session_id": getattr(session, 'session_id', getattr(session, 'id', str(session))),
                    "created_at": getattr(session, 'created_at', datetime.now()).isoformat() if hasattr(session, 'created_at') else "unknown",
                    "state": getattr(session, 'state', {})
                }
                for session in (sessions_list or [])
            ]
            
        except Exception as e:
            logger.error(f"❌ Error listing sessions: {e}")
            return []
    
    async def save_message(self, session_id: str, message: str, response: str) -> Dict:
        """
        Save conversation to memory service using add_session_to_memory.
        
        Args:
            session_id: Session identifier
            message: User message
            response: Agent response
            
        Returns:
            Save operation result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        memory_service = self.runtime.get_memory_service()
        session_service = self.runtime.get_session_service()
        
        try:
            # Get the session to add it to memory
            session = await session_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            
            if not session:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found"
                }
            
            # Use ADK's add_session_to_memory method
            await memory_service.add_session_to_memory(session)
            
            logger.info(f"💾 Added session to memory: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session added to memory successfully",
                "service": "PostgreSQL Memory Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding session to memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def store_memory(self, content: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict:
        """
        Store content in memory service.
        
        Args:
            content: Content to store
            session_id: Optional session identifier
            metadata: Optional metadata
            
        Returns:
            Store operation result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        memory_service = self.runtime.get_memory_service()
        
        try:
            # Add default metadata
            store_metadata = metadata or {}
            store_metadata.update({
                "stored_at": datetime.now().isoformat(),
                "type": store_metadata.get("type", "general")
            })
            
            memory_id = await memory_service.store(
                session_id=session_id,
                content=content,
                metadata=store_metadata
            )
            
            logger.info(f"💾 Stored memory: {memory_id}")
            return {
                "success": True,
                "memory_id": memory_id,
                "session_id": session_id,
                "content": content,
                "metadata": store_metadata,
                "service": "PostgreSQL Memory Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error storing memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_memory(self, query: str, session_id: Optional[str] = None, limit: int = 5) -> Dict:
        """
        Search memory service using ADK's search_memory method.
        
        Args:
            query: Search query
            session_id: Optional session identifier
            limit: Maximum results to return
            
        Returns:
            Search results
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        memory_service = self.runtime.get_memory_service()
        
        try:
            # Use ADK's search_memory method with required parameters
            results = await memory_service.search_memory(
                app_name=self.app_name,
                user_id=self.user_id,
                query=query
            )
            
            # Handle SearchMemoryResponse object
            formatted_results = []
            if results:
                # Extract results from the response object
                search_results = getattr(results, 'results', results)
                if hasattr(search_results, '__iter__') and not isinstance(search_results, str):
                    for result in list(search_results)[:limit]:  # Apply limit
                        formatted_results.append({
                            "content": getattr(result, 'content', str(result)),
                            "metadata": getattr(result, 'metadata', {}),
                            "similarity": getattr(result, 'similarity', 'unknown'),
                            "source": getattr(result, 'source', 'unknown')
                        })
                else:
                    # Handle single result or unexpected format
                    formatted_results.append({
                        "content": str(search_results),
                        "metadata": {},
                        "similarity": 'unknown',
                        "source": 'unknown'
                    })
            
            logger.info(f"🔍 Found {len(formatted_results)} memory results for query: {query}")
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "service": "PostgreSQL Memory Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error searching memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_memories(self, session_id: Optional[str] = None, limit: int = 10) -> Dict:
        """
        List memories from memory service.
        
        Args:
            session_id: Optional session identifier
            limit: Maximum memories to return
            
        Returns:
            List of memories
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        memory_service = self.runtime.get_memory_service()
        
        try:
            memories = await memory_service.list(
                session_id=session_id,
                limit=limit
            )
            
            # Format memories for display
            formatted_memories = []
            for memory in memories:
                formatted_memories.append({
                    "id": getattr(memory, 'id', 'unknown'),
                    "content": getattr(memory, 'content', ''),
                    "metadata": getattr(memory, 'metadata', {}),
                    "session_id": getattr(memory, 'session_id', None),
                    "created_at": getattr(memory, 'created_at', 'unknown')
                })
            
            logger.info(f"📋 Retrieved {len(formatted_memories)} memories")
            return {
                "success": True,
                "session_id": session_id,
                "memories": formatted_memories,
                "count": len(formatted_memories),
                "service": "PostgreSQL Memory Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error listing memories: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def clear_all_sessions(self) -> Dict:
        """
        Clear all sessions for the current user and app.
        
        Returns:
            Dictionary with cleanup result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        session_service = self.runtime.get_session_service()
        
        try:
            # First, list sessions to see how many we're deleting
            sessions_response = await session_service.list_sessions(
                app_name=self.app_name,
                user_id=self.user_id
            )
            
            # Handle the response properly
            if hasattr(sessions_response, 'sessions'):
                sessions_list = sessions_response.sessions
            else:
                sessions_list = sessions_response
            
            session_count = len(sessions_list) if sessions_list else 0
            
            if session_count == 0:
                logger.info("🧹 No sessions to clear")
                return {
                    "success": True,
                    "cleared_count": 0,
                    "message": "No sessions found to clear"
                }
            
            # Delete each session
            cleared_count = 0
            for session in (sessions_list or []):
                session_id = getattr(session, 'session_id', getattr(session, 'id', str(session)))
                try:
                    await session_service.delete_session(
                        app_name=self.app_name,
                        user_id=self.user_id,
                        session_id=session_id
                    )
                    cleared_count += 1
                    logger.info(f"🗑️  Deleted session: {session_id}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to delete session {session_id}: {e}")
            
            logger.info(f"🧹 Cleared {cleared_count} of {session_count} sessions")
            return {
                "success": True,
                "cleared_count": cleared_count,
                "total_found": session_count,
                "message": f"Successfully cleared {cleared_count} sessions"
            }
            
        except Exception as e:
            logger.error(f"❌ Error clearing sessions: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def save_artifact(self, session_id: str, filename: str, content: str, content_type: str = "text/plain") -> Dict:
        """
        Save artifact using PostgreSQL artifact service.
        
        Args:
            session_id: Session identifier
            filename: Artifact filename
            content: Artifact content
            content_type: MIME type of the content
            
        Returns:
            Save operation result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        artifact_service = self.runtime.get_artifact_service()
        
        try:
            # Create ADK Part object from content
            if content_type.startswith('text/'):
                artifact_part = types.Part(text=content)
            else:
                # For binary content, convert string to bytes
                artifact_part = types.Part(data=content.encode('utf-8'), mime_type=content_type)
            
            # Use correct ADK method name: save_artifact
            version = await artifact_service.save_artifact(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id,
                filename=filename,
                artifact=artifact_part
            )
            
            logger.info(f"📁 Saved artifact: {filename} ({len(content)} bytes) -> version {version}")
            return {
                "success": True,
                "version": version,
                "filename": filename,
                "session_id": session_id,
                "size": len(content),
                "content_type": content_type,
                "service": "PostgreSQL Artifact Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving artifact: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_artifact(self, filename: str, session_id: str, version: Optional[int] = None) -> Dict:
        """
        Retrieve artifact using PostgreSQL artifact service.
        
        Args:
            filename: Artifact filename
            session_id: Session identifier
            version: Optional version number (None for latest)
            
        Returns:
            Artifact data or error
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        artifact_service = self.runtime.get_artifact_service()
        
        try:
            # Use correct ADK method name: load_artifact
            artifact_part = await artifact_service.load_artifact(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id,
                filename=filename,
                version=version
            )
            
            if artifact_part:
                # Extract content from Part object
                if hasattr(artifact_part, 'text') and artifact_part.text:
                    content = artifact_part.text
                    content_type = "text/plain"
                elif hasattr(artifact_part, 'data') and artifact_part.data:
                    content = artifact_part.data.decode('utf-8', errors='ignore')
                    content_type = "application/octet-stream"
                else:
                    content = str(artifact_part)
                    content_type = "text/plain"
                
                logger.info(f"📋 Retrieved artifact: {filename}")
                return {
                    "success": True,
                    "filename": filename,
                    "content": content,
                    "content_type": content_type,
                    "size": len(content),
                    "session_id": session_id,
                    "version": version,
                    "service": "PostgreSQL Artifact Service"
                }
            else:
                logger.warning(f"⚠️  Artifact not found: {filename}")
                return {
                    "success": False,
                    "error": f"Artifact {filename} not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Error retrieving artifact {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_artifacts(self, session_id: Optional[str] = None, limit: int = 10) -> Dict:
        """
        List artifacts from PostgreSQL artifact service.
        
        Args:
            session_id: Optional session identifier
            limit: Maximum artifacts to return
            
        Returns:
            List of artifacts
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        artifact_service = self.runtime.get_artifact_service()
        
        try:
            if not session_id:
                # Cannot list artifacts without session_id in ADK
                logger.warning("⚠️  Session ID required for listing artifacts")
                return {
                    "success": False,
                    "error": "Session ID is required for listing artifacts"
                }
            
            # Use correct ADK method name: list_artifact_keys
            filenames = await artifact_service.list_artifact_keys(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            
            # Format as artifact objects for display
            formatted_artifacts = []
            for filename in filenames:
                # Get versions for each artifact
                try:
                    versions = await artifact_service.list_versions(
                        app_name=self.app_name,
                        user_id=self.user_id,
                        session_id=session_id,
                        filename=filename
                    )
                    latest_version = max(versions) if versions else 1
                except Exception:
                    latest_version = 1
                
                formatted_artifacts.append({
                    "filename": filename,
                    "session_id": session_id,
                    "latest_version": latest_version,
                    "versions_count": len(versions) if 'versions' in locals() else 1
                })
            
            logger.info(f"📂 Retrieved {len(formatted_artifacts)} artifacts")
            return {
                "success": True,
                "session_id": session_id,
                "artifacts": formatted_artifacts,
                "count": len(formatted_artifacts),
                "service": "PostgreSQL Artifact Service"
            }
            
        except Exception as e:
            logger.error(f"❌ Error listing artifacts: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_artifact(self, filename: str, session_id: str) -> Dict:
        """
        Delete artifact using PostgreSQL artifact service.
        
        Args:
            filename: Artifact filename
            session_id: Session identifier
            
        Returns:
            Delete operation result
        """
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        artifact_service = self.runtime.get_artifact_service()
        
        try:
            # Use correct ADK method name: delete_artifact
            await artifact_service.delete_artifact(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id,
                filename=filename
            )
            
            logger.info(f"🗑️  Deleted artifact: {filename}")
            return {
                "success": True,
                "filename": filename,
                "session_id": session_id,
                "message": "Artifact deleted successfully",
                "service": "PostgreSQL Artifact Service"
            }
                
        except Exception as e:
            logger.error(f"❌ Error deleting artifact {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


async def run_automated_demo():
    """Run automated demonstration of PostgreSQL services."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")  # Use consistent app name
    
    try:
        print("🚀 Starting PostgreSQL Chat Driver Demo")
        print("=" * 50)
        
        # Initialize
        await driver.initialize()
        
        # Create a new session with proper UUID
        print("\n1. Creating new session...")
        demo_session_id = str(uuid.uuid4())
        session_result = await driver.create_session(
            demo_session_id,
            {"demo": True, "purpose": "testing PostgreSQL services"}
        )
        print(f"   Result: {session_result}")
        
        # List sessions
        print("\n2. Listing all sessions...")
        sessions = await driver.list_sessions()
        print(f"   Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"     - {session['session_id']} (created: {session['created_at']})")
        
        # Retrieve the session
        print("\n3. Retrieving session...")
        retrieved = await driver.get_session(demo_session_id)
        print(f"   Retrieved: {retrieved}")
        
        # Save conversation
        print("\n4. Saving conversation to memory...")
        memory_result = await driver.save_message(
            demo_session_id,
            "Hello, how does PostgreSQL integration work?",
            "Great question! Our PostgreSQL services replace ADK's default services..."
        )
        print(f"   Result: {memory_result}")
        
        # Save artifact
        print("\n5. Saving artifact...")
        artifact_result = await driver.save_artifact(
            demo_session_id,
            "demo_conversation.txt",
            "This is a demonstration of PostgreSQL service integration.\n\nFeatures:\n- Session management\n- Memory persistence\n- Artifact storage"
        )
        print(f"   Result: {artifact_result}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        await driver.cleanup()


async def run_interactive_demo():
    """Run interactive chat demonstration."""
    driver = PostgreSQLChatDriver("postgres_interactive_app")
    
    try:
        print("🎯 Interactive PostgreSQL Chat Driver")
        print("=" * 40)
        print("Commands: 'quit', 'sessions', 'create <id>', 'get <id>'")
        print()
        
        await driver.initialize()
        
        while True:
            try:
                command = input("🐘 > ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                
                elif command.lower() == 'sessions':
                    sessions = await driver.list_sessions()
                    if sessions:
                        print(f"📝 Found {len(sessions)} sessions:")
                        for session in sessions:
                            print(f"  • {session['session_id']}")
                    else:
                        print("📝 No sessions found")
                
                elif command.startswith('create '):
                    session_id = command[7:].strip()
                    if session_id:
                        result = await driver.create_session(session_id)
                        if result['success']:
                            print(f"✅ Created session: {session_id}")
                        else:
                            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Please provide a session ID")
                
                elif command.startswith('get '):
                    session_id = command[4:].strip()
                    if session_id:
                        result = await driver.get_session(session_id)
                        if result:
                            print(f"📋 Session {session_id}:")
                            print(f"   Data: {result['data']}")
                        else:
                            print(f"❌ Session not found: {session_id}")
                    else:
                        print("❌ Please provide a session ID")
                
                else:
                    print("❓ Unknown command. Try: sessions, create <id>, get <id>, quit")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")
    finally:
        await driver.cleanup()


async def list_all_sessions():
    """List all sessions (utility function)."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")  # Use consistent app name
    
    try:
        await driver.initialize()
        sessions = await driver.list_sessions()
        
        print("📝 All Sessions:")
        print("=" * 20)
        
        if sessions:
            for i, session in enumerate(sessions, 1):
                print(f"{i}. {session['session_id']}")
                print(f"   Created: {session['created_at']}")
                print(f"   State: {session['state']}")
                print()
        else:
            print("No sessions found.")
        
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
    finally:
        await driver.cleanup()


async def clear_all_sessions():
    """Clear all sessions (utility function)."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")  # Use consistent app name
    
    try:
        await driver.initialize()
        
        print("🧹 Clearing all sessions...")
        print("=" * 30)
        
        result = await driver.clear_all_sessions()
        
        if result['success']:
            if result['cleared_count'] > 0:
                print(f"✅ {result['message']}")
                print(f"   Cleared: {result['cleared_count']} sessions")
                if result['cleared_count'] != result.get('total_found', 0):
                    failed = result.get('total_found', 0) - result['cleared_count']
                    print(f"   Failed: {failed} sessions")
            else:
                print(f"ℹ️  {result['message']}")
        else:
            print(f"❌ Failed to clear sessions: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error clearing sessions: {e}")
    finally:
        await driver.cleanup()


async def test_memory_service():
    """Test PostgreSQL memory service functionality."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        print("🧠 Testing PostgreSQL Memory Service")
        print("=" * 40)
        
        # Create a session first for testing
        test_session_id = str(uuid.uuid4())
        session_result = await driver.create_session(test_session_id, {"test": "memory_service"})
        print(f"✅ Created test session: {test_session_id}")
        
        # Test 1: Add session to memory using ADK's add_session_to_memory
        print("\n1. Adding session to memory...")
        memory_result = await driver.save_message(
            test_session_id,
            "What is PostgreSQL?",
            "PostgreSQL is a powerful relational database that supports advanced features..."
        )
        if memory_result['success']:
            print(f"   ✅ Added session to memory: {test_session_id}")
        else:
            print(f"   ❌ Failed to add session: {memory_result.get('error')}")
        
        # Test 2: Search memory using ADK's search_memory
        print("\n2. Searching memory...")
        search_queries = ["PostgreSQL", "database", "relational"]
        
        for query in search_queries:
            search_result = await driver.search_memory(query)
            if search_result['success']:
                print(f"   🔍 Query '{query}' found {search_result['count']} results:")
                for i, result in enumerate(search_result['results'][:2], 1):  # Show first 2
                    print(f"     {i}. {result['content'][:60]}...")
            else:
                print(f"   ❌ Search failed for '{query}': {search_result.get('error')}")
        
        print("\n✅ Memory service test completed!")
        print("📝 Note: ADK BaseMemoryService provides add_session_to_memory and search_memory methods")
        
        # Cleanup test session
        await driver.clear_all_sessions()
        print("🧹 Cleaned up test session")
        
    except Exception as e:
        print(f"❌ Memory service test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await driver.cleanup()


async def search_memory_cli(query: str):
    """Search memory from command line."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        print(f"🔍 Searching memory for: '{query}'")
        print("=" * 50)
        
        result = await driver.search_memory(query, limit=10)
        
        if result['success']:
            if result['count'] > 0:
                print(f"✅ Found {result['count']} results:")
                for i, memory in enumerate(result['results'], 1):
                    print(f"\n{i}. {memory['content']}")
                    if memory['metadata']:
                        print(f"   📝 Metadata: {memory['metadata']}")
                    print(f"   📅 Created: {memory['created_at']}")
                    if memory['similarity'] != 'unknown':
                        print(f"   📊 Similarity: {memory['similarity']}")
            else:
                print("ℹ️  No memories found matching your query")
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error searching memory: {e}")
    finally:
        await driver.cleanup()


async def list_all_memories():
    """List all memories from command line."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        print("🧠 All Memories:")
        print("=" * 20)
        
        result = await driver.list_memories(limit=50)
        
        if result['success']:
            if result['count'] > 0:
                print(f"📊 Found {result['count']} memories:")
                print()
                
                for i, memory in enumerate(result['memories'], 1):
                    print(f"{i}. {memory['content']}")
                    if memory['metadata']:
                        print(f"   📝 Type: {memory['metadata'].get('type', 'unknown')}")
                        print(f"   📂 Topic: {memory['metadata'].get('topic', 'general')}")
                    if memory['session_id']:
                        print(f"   🔗 Session: {memory['session_id']}")
                    print(f"   📅 Created: {memory['created_at']}")
                    print()
            else:
                print("ℹ️  No memories found")
        else:
            print(f"❌ Failed to list memories: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error listing memories: {e}")
    finally:
        await driver.cleanup()


async def test_artifact_service():
    """Test PostgreSQL artifact service functionality."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        print("📁 Testing PostgreSQL Artifact Service")
        print("=" * 40)
        
        # Create a session first for testing
        test_session_id = str(uuid.uuid4())
        session_result = await driver.create_session(test_session_id, {"test": "artifact_service"})
        print(f"✅ Created test session: {test_session_id}")
        
        # Test artifacts to create
        test_artifacts = [
            ("config.json", '{"database": "postgresql", "port": 5432}', "application/json"),
            ("README.md", "# PostgreSQL Artifact Testing\\n\\nThis demonstrates artifact storage.", "text/markdown"),
            ("data.txt", "Sample data for testing\\nLine 2\\nLine 3", "text/plain"),
            ("script.py", "#!/usr/bin/env python3\\nprint('Hello from artifact!')", "text/x-python")
        ]
        
        stored_artifacts = []
        
        # Test 1: Store artifacts
        print("\\n1. Storing artifacts...")
        for filename, content, content_type in test_artifacts:
            result = await driver.save_artifact(test_session_id, filename, content, content_type)
            if result['success']:
                stored_artifacts.append({
                    "version": result['version'],
                    "filename": filename,
                    "size": result['size']
                })
                print(f"   ✅ Stored: {filename} ({result['size']} bytes) -> version {result['version']}")
            else:
                print(f"   ❌ Failed to store: {filename} - {result.get('error')}")
        
        print(f"   📊 Stored {len(stored_artifacts)} artifacts")
        
        # Test 2: List artifacts
        print("\\n2. Listing artifacts...")
        list_result = await driver.list_artifacts(test_session_id, limit=10)
        if list_result['success']:
            print(f"   📂 Found {list_result['count']} artifacts:")
            for i, artifact in enumerate(list_result['artifacts'], 1):
                print(f"     {i}. {artifact['filename']}")
                print(f"        Latest Version: {artifact['latest_version']}")
                print(f"        Total Versions: {artifact['versions_count']}")
        else:
            print(f"   ❌ Failed to list artifacts: {list_result.get('error')}")
        
        # Test 3: Retrieve artifacts
        print("\\n3. Retrieving artifacts...")
        for artifact in stored_artifacts[:2]:  # Test first 2
            get_result = await driver.get_artifact(artifact['filename'], test_session_id)
            if get_result['success']:
                print(f"   ✅ Retrieved: {get_result['filename']}")
                print(f"      Content preview: {get_result['content'][:50]}...")
                print(f"      Type: {get_result['content_type']}")
            else:
                print(f"   ❌ Failed to retrieve: {artifact['filename']} - {get_result.get('error')}")
        
        # Test 4: Delete an artifact
        print("\\n4. Testing artifact deletion...")
        if stored_artifacts:
            test_artifact = stored_artifacts[0]
            delete_result = await driver.delete_artifact(test_artifact['filename'], test_session_id)
            if delete_result['success']:
                print(f"   ✅ Deleted: {test_artifact['filename']}")
            else:
                print(f"   ❌ Failed to delete: {test_artifact['filename']} - {delete_result.get('error')}")
            
            # Verify deletion
            get_result = await driver.get_artifact(test_artifact['filename'], test_session_id)
            if not get_result['success']:
                print(f"   ✅ Confirmed deletion: {test_artifact['filename']} no longer exists")
            else:
                print(f"   ⚠️  Artifact still exists after deletion attempt")
        
        print("\\n✅ Artifact service test completed!")
        print("📝 Note: ADK Artifact Service provides save_artifact, load_artifact, list_artifact_keys, and delete_artifact methods")
        
        # Cleanup test session
        await driver.clear_all_sessions()
        print("🧹 Cleaned up test session")
        
    except Exception as e:
        print(f"❌ Artifact service test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await driver.cleanup()


async def list_all_artifacts():
    """List all artifacts from command line."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        print("📁 All Artifacts:")
        print("=" * 20)
        
        # For list_artifacts, we need a session ID, so get the first available session
        sessions = await driver.list_sessions()
        if not sessions:
            print("ℹ️  No sessions found. Create a session first to store artifacts.")
            return
        
        session_id = sessions[0]['session_id']
        result = await driver.list_artifacts(session_id, limit=50)
        
        if result['success']:
            if result['count'] > 0:
                print(f"📊 Found {result['count']} artifacts:")
                print()
                
                for i, artifact in enumerate(result['artifacts'], 1):
                    print(f"{i}. {artifact['filename']}")
                    print(f"   🔗 Session: {artifact['session_id']}")
                    print(f"   📊 Latest Version: {artifact['latest_version']}")
                    print(f"   📈 Total Versions: {artifact['versions_count']}")
                    print()
            else:
                print("ℹ️  No artifacts found")
        else:
            print(f"❌ Failed to list artifacts: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error listing artifacts: {e}")
    finally:
        await driver.cleanup()


async def get_artifact_cli(filename: str):
    """Retrieve artifact from command line."""
    driver = PostgreSQLChatDriver("postgres_chat_driver")
    
    try:
        await driver.initialize()
        
        # Need to get a session ID for artifact retrieval
        sessions = await driver.list_sessions()
        if not sessions:
            print("❌ No sessions found. Please create a session first.")
            return
        
        session_id = sessions[0]['session_id']
        print(f"📋 Retrieving artifact: {filename} from session: {session_id}")
        print("=" * 60)
        
        result = await driver.get_artifact(filename, session_id)
        
        if result['success']:
            print(f"✅ Artifact retrieved successfully:")
            print(f"   📄 Filename: {result['filename']}")
            print(f"   📝 Content Type: {result['content_type']}")
            print(f"   📊 Size: {result['size']} bytes")
            print(f"   📅 Created: {result['created_at']}")
            print("\\n📄 Content:")
            print("-" * 30)
            print(result['content'])
            print("-" * 30)
        else:
            print(f"❌ Failed to retrieve artifact: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error retrieving artifact: {e}")
    finally:
        await driver.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PostgreSQL Chat Driver - Clean implementation using PostgreSQL services",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--interactive', '-i', action='store_true',
                      help='Run interactive mode')
    group.add_argument('--list-sessions', '-l', action='store_true',
                      help='List all sessions')
    group.add_argument('--clear-all-sessions', '-c', action='store_true',
                      help='Clear all sessions')
    group.add_argument('--test-memory', action='store_true',
                      help='Test memory service functionality')
    group.add_argument('--search-memory', type=str, metavar='QUERY',
                      help='Search memory for specific query')
    group.add_argument('--list-memories', action='store_true',
                      help='List all memories')
    group.add_argument('--test-artifacts', action='store_true',
                      help='Test artifact service functionality')
    group.add_argument('--list-artifacts', action='store_true',
                      help='List all artifacts')
    group.add_argument('--get-artifact', type=str, metavar='FILENAME',
                      help='Retrieve specific artifact by filename')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.interactive:
        asyncio.run(run_interactive_demo())
    elif args.list_sessions:
        asyncio.run(list_all_sessions())
    elif args.clear_all_sessions:
        asyncio.run(clear_all_sessions())
    elif args.test_memory:
        asyncio.run(test_memory_service())
    elif args.search_memory:
        asyncio.run(search_memory_cli(args.search_memory))
    elif args.list_memories:
        asyncio.run(list_all_memories())
    elif args.test_artifacts:
        asyncio.run(test_artifact_service())
    elif args.list_artifacts:
        asyncio.run(list_all_artifacts())
    elif args.get_artifact:
        asyncio.run(get_artifact_cli(args.get_artifact))
    else:
        asyncio.run(run_automated_demo())


if __name__ == "__main__":
    main()