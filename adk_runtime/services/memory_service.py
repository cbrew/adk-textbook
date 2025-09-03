"""
PostgreSQL-backed memory service implementation with pgvector.

Provides semantic memory storage using local PostgreSQL with vector embeddings.
"""

import json
import uuid
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types

from ..database.connection import DatabaseManager, serialize_json, deserialize_json
from ..database.schema import QUERIES

if TYPE_CHECKING:
    from google.adk.sessions.session import Session

logger = logging.getLogger(__name__)


class PostgreSQLMemoryService(BaseMemoryService):
    """PostgreSQL-backed memory service with vector search capabilities."""
    
    def __init__(self, database_manager: DatabaseManager, embedding_service=None):
        self.db = database_manager
        self.embedding_service = embedding_service
        
    async def add_session_to_memory(self, session: "Session") -> None:
        """Adds session content to memory with embeddings."""
        try:
            # Extract meaningful content from session events
            content_parts = []
            
            # Add session state as context
            if session.state:
                state_summary = self._summarize_state(session.state)
                if state_summary:
                    content_parts.append(f"Session state: {state_summary}")
            
            # Extract content from events
            for event in session.events:
                event_content = self._extract_event_content(event)
                if event_content:
                    content_parts.append(event_content)
            
            if not content_parts:
                logger.debug(f"No meaningful content found in session {session.id}")
                return
            
            # Combine content
            full_content = "\n".join(content_parts)
            
            # Generate embedding if service available
            embedding = None
            if self.embedding_service:
                try:
                    embedding = await self.embedding_service.generate_embedding(full_content)
                except Exception as e:
                    logger.warning(f"Failed to generate embedding: {e}")
            
            # Store in database
            metadata = {
                "session_id": session.id,
                "app_name": session.app_name,
                "event_count": len(session.events),
                "added_at": datetime.utcnow().isoformat()
            }
            
            # Ensure session.id is a valid UUID string
            session_uuid = session.id if session.id else str(uuid.uuid4())
            
            self.db.execute_query(
                QUERIES["insert_memory"],
                (
                    str(uuid.uuid4()),
                    session_uuid,
                    None,  # user_id is None for session-scoped memory
                    full_content,
                    embedding,  # Will be None if no embedding service
                    serialize_json(metadata)
                ),
                fetch_all=False
            )
            
            logger.info(f"Added session {session.id} to memory (content length: {len(full_content)})")
            
        except Exception as e:
            logger.error(f"Failed to add session {session.id} to memory: {e}")
            
    async def search_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        query: str,
    ) -> SearchMemoryResponse:
        """Search for relevant memories using text and vector similarity."""
        try:
            memories = []
            
            # Try embedding-based search first if available
            if self.embedding_service:
                memories.extend(await self._search_by_embedding(app_name, user_id, query))
            
            # Fallback to text search if no embedding results or no embedding service
            if not memories:
                memories.extend(await self._search_by_text(app_name, user_id, query))
            
            return SearchMemoryResponse(memories=memories)
            
        except Exception as e:
            logger.error(f"Memory search failed for query '{query}': {e}")
            return SearchMemoryResponse(memories=[])
    
    async def _search_by_embedding(
        self, app_name: str, user_id: str, query: str, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Search using cosine similarity
            results = self.db.execute_query(
                QUERIES["search_memory_by_embedding"],
                (query_embedding, None, user_id, limit),  # session_id=None for user-scoped search
                fetch_all=True
            )
            
            return self._results_to_memory_entries(results, app_name)
            
        except Exception as e:
            logger.error(f"Embedding search failed: {e}")
            return []
    
    async def _search_by_text(
        self, app_name: str, user_id: str, query: str, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories using text similarity (ILIKE)."""
        try:
            # Use PostgreSQL ILIKE for fuzzy text matching
            search_pattern = f"%{query}%"
            
            results = self.db.execute_query(
                QUERIES["search_memory"],
                (search_pattern, None, user_id, limit),  # session_id=None for user-scoped search
                fetch_all=True
            )
            
            return self._results_to_memory_entries(results, app_name)
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    def _results_to_memory_entries(self, results: List[Dict], app_name: str) -> List[MemoryEntry]:
        """Convert database results to MemoryEntry objects."""
        memories = []
        
        for result in results:
            try:
                metadata = deserialize_json(result.get("metadata", "{}"))
                if not isinstance(metadata, dict):
                    metadata = {}
                
                # Filter by app_name if provided in metadata
                if metadata.get("app_name") and metadata["app_name"] != app_name:
                    continue
                
                # Create content from stored text
                content = types.Content(
                    role="user",  # Default role
                    parts=[types.Part.from_text(result["content"])]
                )
                
                # Extract timestamp from metadata or use created_at
                timestamp = metadata.get("added_at")
                if not timestamp and result.get("created_at"):
                    timestamp = result["created_at"].isoformat()
                
                memory = MemoryEntry(
                    content=content,
                    author=metadata.get("author"),
                    timestamp=timestamp
                )
                
                memories.append(memory)
                
            except Exception as e:
                logger.warning(f"Failed to convert memory result to MemoryEntry: {e}")
        
        return memories
    
    def _summarize_state(self, state: Dict[str, Any]) -> Optional[str]:
        """Create a summary of session state for memory storage."""
        if not state:
            return None
        
        try:
            # Simple state summarization - in production you might use an LLM
            summary_parts = []
            for key, value in state.items():
                if isinstance(value, (str, int, float, bool)):
                    summary_parts.append(f"{key}: {value}")
                elif isinstance(value, (dict, list)):
                    summary_parts.append(f"{key}: {json.dumps(value)}")
            
            return "; ".join(summary_parts[:10])  # Limit to 10 key items
            
        except Exception as e:
            logger.warning(f"Failed to summarize state: {e}")
            return None
    
    def _extract_event_content(self, event) -> Optional[str]:
        """Extract meaningful text content from an event."""
        try:
            # This is a simplified extraction - in production you'd want more sophisticated parsing
            content_parts = []
            
            # Add event type context
            if hasattr(event, 'event_type') and event.event_type:
                content_parts.append(f"Event: {event.event_type}")
            
            # Extract input/output content
            if hasattr(event, 'input') and event.input:
                if hasattr(event.input, 'parts'):
                    for part in event.input.parts:
                        if hasattr(part, 'text') and part.text:
                            content_parts.append(f"Input: {part.text}")
            
            if hasattr(event, 'output') and event.output:
                if hasattr(event.output, 'parts'):
                    for part in event.output.parts:
                        if hasattr(part, 'text') and part.text:
                            content_parts.append(f"Output: {part.text}")
            
            return "\n".join(content_parts) if content_parts else None
            
        except Exception as e:
            logger.warning(f"Failed to extract event content: {e}")
            return None