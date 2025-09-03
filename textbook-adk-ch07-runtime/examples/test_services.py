#!/usr/bin/env python3
"""
Test script for PostgreSQL ADK services.

Verifies that session, memory, and artifact services work with the database.
"""

import asyncio
import logging
import uuid

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime
from adk_runtime.database.connection import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_session_service():
    """Test basic session service functionality."""
    logger.info("Testing session service...")
    
    runtime = None
    try:
        # Initialize runtime
        runtime = await PostgreSQLADKRuntime.create_and_initialize()
        session_service = runtime.get_session_service()
        
        # Test session creation
        session = await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            state={"test_key": "test_value", "counter": 0}
        )
        
        logger.info(f"Created session: {session.id}")
        
        # Test session retrieval
        retrieved_session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user", 
            session_id=session.id
        )
        
        if retrieved_session:
            logger.info(f"Retrieved session: {retrieved_session.id}")
            logger.info(f"Session state: {retrieved_session.state}")
        else:
            raise Exception("Failed to retrieve session")
        
        # Test session listing
        sessions_response = await session_service.list_sessions(
            app_name="test_app",
            user_id="test_user"
        )
        
        logger.info(f"Found {len(sessions_response.sessions)} sessions")
        
        # Test session deletion
        await session_service.delete_session(
            app_name="test_app",
            user_id="test_user",
            session_id=session.id
        )
        
        logger.info("✅ Session service tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Session service test failed: {e}")
        raise
    finally:
        if runtime:
            await runtime.shutdown()


async def test_memory_service():
    """Test basic memory service functionality."""
    logger.info("Testing memory service...")
    
    runtime = None
    try:
        # Initialize runtime
        runtime = await PostgreSQLADKRuntime.create_and_initialize()
        memory_service = runtime.get_memory_service()
        session_service = runtime.get_session_service()
        
        # Create a real session first (needed for foreign key constraint)
        session = await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            state={"topic": "machine learning", "progress": "started"}
        )
        
        # Test adding session to memory
        await memory_service.add_session_to_memory(session)
        logger.info("Added session to memory")
        
        # Test memory search
        search_response = await memory_service.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="machine learning"
        )
        
        logger.info(f"Memory search returned {len(search_response.memories)} results")
        
        # Clean up test session
        await session_service.delete_session(
            app_name="test_app",
            user_id="test_user", 
            session_id=session.id
        )
        
        logger.info("✅ Memory service tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Memory service test failed: {e}")
        raise
    finally:
        if runtime:
            await runtime.shutdown()


async def test_artifact_service():
    """Test basic artifact service functionality.""" 
    logger.info("Testing artifact service...")
    
    runtime = None
    try:
        # Initialize runtime
        runtime = await PostgreSQLADKRuntime.create_and_initialize()
        artifact_service = runtime.get_artifact_service()
        session_service = runtime.get_session_service()
        
        # Create a real session first (needed for foreign key constraint)
        session = await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            state={"artifact_test": True}
        )
        
        # Create test artifact
        from google.genai import types
        test_content = "This is a test artifact content"
        test_artifact = types.Part(text=test_content)
        
        # Test saving artifact
        version = await artifact_service.save_artifact(
            app_name="test_app",
            user_id="test_user",
            session_id=session.id,
            filename="test.txt",
            artifact=test_artifact
        )
        
        logger.info(f"Saved artifact version: {version}")
        
        # Test loading artifact
        loaded_artifact = await artifact_service.load_artifact(
            app_name="test_app", 
            user_id="test_user",
            session_id=session.id,
            filename="test.txt"
        )
        
        if loaded_artifact and hasattr(loaded_artifact, 'text'):
            logger.info(f"Loaded artifact content: {loaded_artifact.text[:50]}...")
        else:
            raise Exception("Failed to load artifact or artifact has no text")
        
        # Test listing artifacts
        artifact_keys = await artifact_service.list_artifact_keys(
            app_name="test_app",
            user_id="test_user", 
            session_id=session.id
        )
        
        logger.info(f"Found artifacts: {artifact_keys}")
        
        # Test listing versions
        versions = await artifact_service.list_versions(
            app_name="test_app",
            user_id="test_user",
            session_id=session.id, 
            filename="test.txt"
        )
        
        logger.info(f"Artifact versions: {versions}")
        
        # Test deleting artifact
        await artifact_service.delete_artifact(
            app_name="test_app",
            user_id="test_user",
            session_id=session.id,
            filename="test.txt"
        )
        
        # Clean up test session
        await session_service.delete_session(
            app_name="test_app",
            user_id="test_user",
            session_id=session.id
        )
        
        logger.info("✅ Artifact service tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Artifact service test failed: {e}")
        raise
    finally:
        if runtime:
            await runtime.shutdown()


async def main():
    """Run all service tests."""
    logger.info("🚀 Starting PostgreSQL ADK Services Tests")
    
    try:
        await test_session_service()
        await test_memory_service() 
        await test_artifact_service()
        
        logger.info("🎉 All tests passed!")
        
    except Exception as e:
        logger.error(f"💥 Tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())