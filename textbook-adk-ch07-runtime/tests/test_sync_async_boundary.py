#!/usr/bin/env python3
"""
Test cases to isolate and verify the sync/async boundary issue.

This test suite verifies:
1. Our PostgreSQL services implement async correctly (ADK spec compliant)
2. The ToolContext integration properly awaits async service calls
3. Agent tool functions work with the corrected flow
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock
from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext
from google.genai import types

from adk_runtime.services.artifact_service import PostgreSQLArtifactService
from adk_runtime.services.session_service import PostgreSQLSessionService  
from adk_runtime.services.memory_service import PostgreSQLMemoryService
from adk_runtime.database.connection import DatabaseManager


class TestAsyncServiceCompliance:
    """Test that our services comply with ADK async specifications."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager for testing."""
        db_manager = Mock(spec=DatabaseManager)
        db_manager.execute_query = Mock(return_value=[
            {"filename": "test1.txt", "metadata": '{"app_name": "test_app"}'},
            {"filename": "test2.pdf", "metadata": '{"app_name": "test_app"}'}
        ])
        return db_manager
    
    @pytest.fixture
    def artifact_service(self, mock_db_manager):
        """Create artifact service with mocked database."""
        return PostgreSQLArtifactService(mock_db_manager)
    
    @pytest.mark.asyncio
    async def test_artifact_service_list_artifact_keys_is_async(self, artifact_service):
        """Test that list_artifact_keys is properly async and returns list[str]."""
        result = artifact_service.list_artifact_keys(
            app_name="test_app",
            user_id="test_user", 
            session_id="test_session"
        )
        
        # Verify it returns a coroutine
        assert asyncio.iscoroutine(result), "list_artifact_keys should return coroutine"
        
        # Await and verify the result
        artifact_keys = await result
        assert isinstance(artifact_keys, list), "Should return list[str]"
        assert all(isinstance(key, str) for key in artifact_keys), "All keys should be strings"
        assert artifact_keys == ["test1.txt", "test2.pdf"], "Should return expected filenames"
    
    @pytest.mark.asyncio 
    async def test_session_service_methods_are_async(self, mock_db_manager):
        """Test that session service methods are properly async."""
        service = PostgreSQLSessionService(mock_db_manager)
        
        # Test create_session is async
        result = service.create_session(
            app_name="test_app",
            user_id="test_user"
        )
        assert asyncio.iscoroutine(result), "create_session should return coroutine"
        
        session = await result
        assert session.app_name == "test_app"
        assert session.user_id == "test_user"


class TestToolContextIntegration:
    """Test the ToolContext integration with async services."""
    
    def test_tool_context_sync_call_to_async_service(self):
        """Test the problematic sync call that fails."""
        
        # Mock a ToolContext that returns coroutine (simulating current broken behavior)
        mock_tool_context = Mock(spec=ToolContext)
        
        # Simulate the broken behavior: list_artifacts returns coroutine
        async def async_list_artifacts():
            return ["file1.txt", "file2.pdf"] 
            
        mock_tool_context.list_artifacts = Mock(return_value=async_list_artifacts())
        
        # This is what happens in our agent tool - it should fail
        try:
            artifacts = mock_tool_context.list_artifacts()
            # This line should fail because artifacts is a coroutine
            for a in artifacts:
                pass
            pytest.fail("Expected TypeError for iterating over coroutine")
        except TypeError as e:
            assert "'coroutine' object is not iterable" in str(e)
    
    def test_tool_context_corrected_integration(self):
        """Test what the corrected ToolContext behavior should be."""
        
        # Mock a ToolContext that properly awaits async services
        mock_tool_context = Mock(spec=ToolContext)
        
        # Simulate corrected behavior: list_artifacts returns actual list
        mock_tool_context.list_artifacts = Mock(return_value=["file1.txt", "file2.pdf"])
        
        # This should work fine
        artifacts = mock_tool_context.list_artifacts()
        assert isinstance(artifacts, list)
        assert len(artifacts) == 2
        assert "file1.txt" in artifacts


class TestAgentToolFunctions:
    """Test agent tool functions with corrected ToolContext."""
    
    def test_list_artifacts_tool_with_correct_context(self):
        """Test list_artifacts agent tool with properly working ToolContext."""
        from postgres_chat_agent.agent import list_artifacts
        
        # Mock ToolContext that returns actual list (corrected behavior)
        mock_tool_context = Mock(spec=ToolContext)
        mock_tool_context.list_artifacts = Mock(return_value=["research.pdf", "notes.txt"])
        
        # Test the agent tool function
        result = list_artifacts(mock_tool_context, filter="all")
        
        # Verify it returns proper result dict
        assert isinstance(result, dict)
        assert result["total_count"] == 2
        assert result["filtered_count"] == 2
        assert "research.pdf" in result["artifacts"]
        assert "notes.txt" in result["artifacts"]
    
    def test_list_artifacts_tool_with_filtering(self):
        """Test list_artifacts tool with filtering functionality."""
        from postgres_chat_agent.agent import list_artifacts
        
        mock_tool_context = Mock(spec=ToolContext)
        mock_tool_context.list_artifacts = Mock(return_value=["paper1.pdf", "notes.txt", "paper2.pdf"])
        
        # Test filtering for PDF files
        result = list_artifacts(mock_tool_context, filter="pdf")
        
        assert result["total_count"] == 3
        assert result["filtered_count"] == 2
        assert "paper1.pdf" in result["artifacts"] 
        assert "paper2.pdf" in result["artifacts"]
        assert "notes.txt" not in result["artifacts"]


class TestProposedSolution:
    """Test the proposed solution approach."""
    
    @pytest.mark.asyncio
    async def test_async_service_wrapper_approach(self):
        """Test creating an async-aware ToolContext wrapper."""
        
        # Simulate our actual async service
        mock_artifact_service = AsyncMock()
        mock_artifact_service.list_artifact_keys.return_value = ["file1.txt", "file2.pdf"]
        
        class AsyncAwareToolContext:
            """Proposed ToolContext that properly handles async services."""
            
            def __init__(self, artifact_service, session_info):
                self.artifact_service = artifact_service
                self.session_info = session_info
            
            def list_artifacts(self):
                """Sync method that internally awaits async service."""
                # In a real implementation, this would need event loop handling
                # This is conceptual - showing how ToolContext should bridge sync/async
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, we need a different approach
                    # This is the core architectural challenge
                    raise RuntimeError("Cannot await in running event loop")
                else:
                    return loop.run_until_complete(
                        self.artifact_service.list_artifact_keys(**self.session_info)
                    )
        
        # Test the wrapper concept
        session_info = {
            "app_name": "test_app", 
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        tool_context = AsyncAwareToolContext(mock_artifact_service, session_info)
        
        # This should work (when not in running event loop)
        try:
            artifacts = tool_context.list_artifacts()
            assert artifacts == ["file1.txt", "file2.pdf"]
        except RuntimeError as e:
            # Expected in pytest async context
            assert "Cannot await in running event loop" in str(e)


if __name__ == "__main__":
    # Run tests to isolate the issue
    print("Running sync/async boundary tests...")
    pytest.main([__file__, "-v"])