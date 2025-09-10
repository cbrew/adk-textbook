"""
PostgreSQL-backed memory service implementation with pgvector.

Provides semantic memory storage using local PostgreSQL with vector embeddings.
"""

import json
import uuid
import logging
from pathlib import Path
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
        """Creates searchable memory indexes for session events (event sourcing approach).

        This follows ADK's event sourcing pattern - instead of duplicating conversation content,
        we create searchable indexes that reference the authoritative event stream.
        """
        try:
            if not session.events:
                logger.debug(f"No events in session {session.id} to index")
                return

            # Create memory index entries for searchable events
            for event in session.events:
                await self._index_event_if_searchable(session, event)

            logger.info(
                f"Indexed {len(session.events)} events for session {session.id}"
            )

        except Exception as e:
            logger.error(f"Failed to index session {session.id} events: {e}")

    async def _index_event_if_searchable(self, session: "Session", event) -> None:
        """Create memory index entry for an event if it contains searchable content."""
        try:
            # Extract searchable keywords from event
            keywords = self._extract_event_keywords(event)
            if not keywords:
                return  # Skip events with no searchable content

            # Create searchable summary without duplicating full content
            content_summary = self._create_event_summary(event)
            topics = self._extract_event_topics(event)

            # Store memory index entry that references the event
            metadata = {
                "session_id": session.id,
                "app_name": session.app_name,
                "event_id": event.id,
                "event_author": event.author,
                "event_timestamp": getattr(event, "timestamp", None),
                "event_type": self._classify_event_type(event),
                "topics": topics,
                "keywords": keywords,
                "indexed_at": datetime.utcnow().isoformat(),
                "is_index": True,  # Flag to identify this as an index entry
            }

            # Generate embedding for search if available
            embedding = None
            if self.embedding_service and content_summary:
                try:
                    embedding = await self.embedding_service.generate_embedding(
                        content_summary
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to generate embedding for event {event.id}: {e}"
                    )

            # Store index entry (not full content)
            self.db.execute_query(
                QUERIES["insert_memory"],
                (
                    str(uuid.uuid4()),
                    session.id,
                    None,  # user_id for session-scoped indexing
                    content_summary,  # Brief summary, not full duplication
                    embedding,
                    serialize_json(metadata),
                ),
                fetch_all=False,
            )

        except Exception as e:
            logger.warning(
                f"Failed to index event {getattr(event, 'id', 'unknown')}: {e}"
            )

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
                memories.extend(
                    await self._search_by_embedding(app_name, user_id, query)
                )

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
            if not self.embedding_service:
                return []
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Search using cosine similarity
            results = self.db.execute_query(
                QUERIES["search_memory_by_embedding"],
                (
                    query_embedding,
                    None,
                    user_id,
                    limit,
                ),  # session_id=None for user-scoped search
                fetch_all=True,
            )

            results_list = results if isinstance(results, list) else []
            return self._results_to_memory_entries(results_list, app_name)

        except Exception as e:
            logger.error(f"Embedding search failed: {e}")
            return []

    async def _search_by_text(
        self, app_name: str, user_id: str, query: str, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memory indexes and reconstruct from events (event sourcing)."""
        try:
            # Search memory indexes for relevant events
            search_pattern = f"%{query}%"

            index_results = self.db.execute_query(
                """
                SELECT id, session_id, user_id, content, embedding, metadata, created_at 
                FROM memory 
                WHERE content ILIKE %s 
                AND metadata::text ILIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
                """,
                (
                    search_pattern,
                    '%"is_index": true%',
                    limit * 2,
                ),  # Get more indexes to find relevant events
                fetch_all=True,
            )

            # Reconstruct memory entries from the referenced events
            index_results_list = (
                index_results if isinstance(index_results, list) else []
            )
            return await self._reconstruct_from_event_indexes(
                index_results_list, app_name, limit
            )

        except Exception as e:
            logger.error(f"Event-sourced text search failed: {e}")
            return []

    async def _reconstruct_from_event_indexes(
        self, index_results: List[Dict], app_name: str, limit: int
    ) -> List[MemoryEntry]:
        """Reconstruct MemoryEntry objects from event indexes by fetching the actual events."""
        memories = []
        seen_events = set()  # Avoid duplicate events

        for index_result in index_results:
            try:
                # Parse metadata to get event reference
                metadata = index_result.get("metadata", {})
                if isinstance(metadata, str):
                    metadata = deserialize_json(metadata)

                # Filter by app_name
                if metadata.get("app_name") != app_name:
                    continue

                # Get event details from index
                session_id = metadata.get("session_id")
                event_id = metadata.get("event_id")

                if not session_id or not event_id or event_id in seen_events:
                    continue

                seen_events.add(event_id)

                # Reconstruct memory entry from event information in index
                # Instead of fetching the full session, use the indexed information
                memory_content = await self._create_memory_content_from_index(
                    index_result, metadata
                )
                if memory_content:
                    memories.append(memory_content)

                if len(memories) >= limit:
                    break

            except Exception as e:
                logger.warning(f"Failed to reconstruct memory from index: {e}")

        return memories[:limit]

    async def _create_memory_content_from_index(
        self, index_result: Dict, metadata: Dict
    ) -> Optional[MemoryEntry]:
        """Create a MemoryEntry from index metadata without fetching the full event."""
        try:
            # Use the summary stored in the index for the content
            content_text = index_result.get("content", "")

            # Create Content object
            content = types.Content(
                role="user",  # Default role for memory
                parts=[types.Part(text=content_text)],
            )

            # Use event metadata for timestamp and author info
            timestamp = metadata.get("indexed_at") or metadata.get("event_timestamp")
            author = metadata.get("event_author", "unknown")

            memory = MemoryEntry(content=content, author=author, timestamp=timestamp)

            return memory

        except Exception as e:
            logger.warning(f"Failed to create memory entry from index: {e}")
            return None

    def _results_to_memory_entries(
        self, results: List[Dict], app_name: str
    ) -> List[MemoryEntry]:
        """Convert database results to MemoryEntry objects."""
        memories = []

        for result in results:
            try:
                # Handle metadata - it might be a dict or JSON string
                metadata = result.get("metadata", {})
                if isinstance(metadata, str):
                    metadata = deserialize_json(metadata)
                if not isinstance(metadata, dict):
                    metadata = {}

                # Filter by app_name if provided in metadata
                if metadata.get("app_name") and metadata["app_name"] != app_name:
                    continue

                # Create content from stored text - use correct API
                content = types.Content(
                    role="user",  # Default role
                    parts=[types.Part(text=result["content"])],
                )

                # Extract timestamp from metadata or use created_at
                timestamp = metadata.get("added_at")
                if not timestamp and result.get("created_at"):
                    timestamp = result["created_at"].isoformat()

                memory = MemoryEntry(
                    content=content, author=metadata.get("author"), timestamp=timestamp
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
            if hasattr(event, "event_type") and event.event_type:
                content_parts.append(f"Event: {event.event_type}")

            # Extract input/output content
            if hasattr(event, "input") and event.input:
                if hasattr(event.input, "parts"):
                    for part in event.input.parts:
                        if hasattr(part, "text") and part.text:
                            content_parts.append(f"Input: {part.text}")

            if hasattr(event, "output") and event.output:
                if hasattr(event.output, "parts"):
                    for part in event.output.parts:
                        if hasattr(part, "text") and part.text:
                            content_parts.append(f"Output: {part.text}")

            return "\n".join(content_parts) if content_parts else None

        except Exception as e:
            logger.warning(f"Failed to extract event content: {e}")
            return None

    def _extract_event_keywords(self, event) -> List[str]:
        """Extract searchable keywords from an ADK event."""
        keywords = []

        try:
            # Extract from text content (user messages, agent responses)
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
            ):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        # Simple keyword extraction - split on common delimiters
                        text = part.text.lower()
                        words = (
                            text.replace(",", " ")
                            .replace(".", " ")
                            .replace("?", " ")
                            .split()
                        )
                        # Filter out common stop words and short words
                        filtered_words = [
                            w
                            for w in words
                            if len(w) > 3
                            and w
                            not in [
                                "this",
                                "that",
                                "with",
                                "have",
                                "they",
                                "were",
                                "been",
                                "from",
                            ]
                        ]
                        keywords.extend(filtered_words[:10])  # Limit per part

            # Extract from function calls (tool names are keywords)
            if hasattr(event, "get_function_calls"):
                function_calls = event.get_function_calls()
                for call in function_calls:
                    if hasattr(call, "name"):
                        keywords.append(call.name.lower())

            # Extract from function responses
            if hasattr(event, "get_function_responses"):
                function_responses = event.get_function_responses()
                for response in function_responses:
                    if hasattr(response, "name"):
                        keywords.append(f"{response.name}_result".lower())

            # Extract from state_delta (state update events)
            if (
                hasattr(event, "actions")
                and event.actions
                and hasattr(event.actions, "state_delta")
                and event.actions.state_delta
            ):
                state_delta = event.actions.state_delta

                # Extract topic keywords from conversation_topic
                if (
                    "conversation_topic" in state_delta
                    and state_delta["conversation_topic"]
                ):
                    topic_words = (
                        str(state_delta["conversation_topic"])
                        .lower()
                        .replace(",", " ")
                        .split()
                    )
                    filtered_topic_words = [w for w in topic_words if len(w) > 3]
                    keywords.extend(filtered_topic_words)

                # Add state-related keywords
                keywords.append("state_update")
                if "message_count" in state_delta:
                    keywords.append("conversation")
                if "last_interaction" in state_delta:
                    keywords.append("interaction")

                # Extract searchable values from other state fields
                searchable_state_fields = [
                    "status",
                    "phase",
                    "current_task",
                    "focus_area",
                ]
                for field in searchable_state_fields:
                    if field in state_delta and state_delta[field]:
                        value_words = (
                            str(state_delta[field]).lower().replace("_", " ").split()
                        )
                        keywords.extend([w for w in value_words if len(w) > 3])

            # Extract from artifact_delta (artifact creation/update events)
            if (
                hasattr(event, "actions")
                and event.actions
                and hasattr(event.actions, "artifact_delta")
                and event.actions.artifact_delta
            ):
                artifact_delta = event.actions.artifact_delta

                # Add artifact-related keywords
                keywords.append("artifact")
                keywords.append("file")
                keywords.append("document")

                # Extract filename keywords
                for filename, version in artifact_delta.items():
                    filename_words = (
                        str(filename)
                        .lower()
                        .replace(".", " ")
                        .replace("_", " ")
                        .replace("-", " ")
                        .split()
                    )
                    keywords.extend([w for w in filename_words if len(w) > 2])

                    # Add file extension as keyword
                    if "." in filename:
                        extension = filename.split(".")[-1].lower()
                        keywords.append(extension)

                    # Add version info
                    keywords.append(f"version_{version}")

                # Add storage-related keywords from text content
                if (
                    hasattr(event, "content")
                    and event.content
                    and hasattr(event.content, "parts")
                ):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            text = part.text.lower()
                            if "postgresql" in text or "bytea" in text:
                                keywords.append("postgresql_storage")
                            if "filesystem" in text:
                                keywords.append("filesystem_storage")
                            if "bytes" in text:
                                keywords.append("binary_data")

        except Exception as e:
            logger.debug(f"Failed to extract keywords from event: {e}")

        return list(set(keywords))  # Remove duplicates

    def _create_event_summary(self, event) -> str:
        """Create a brief searchable summary of an event without full content duplication."""
        try:
            summary_parts = []

            # Add author context
            if hasattr(event, "author"):
                summary_parts.append(f"From {event.author}")

            # Add event type classification
            event_type = self._classify_event_type(event)
            if event_type != "unknown":
                summary_parts.append(f"Type: {event_type}")

            # Add brief text content (first 100 chars)
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
            ):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_preview = part.text[:100]
                        if len(part.text) > 100:
                            text_preview += "..."
                        summary_parts.append(f"Content: {text_preview}")
                        break  # Only first text part for summary

            # Add function call info
            if hasattr(event, "get_function_calls"):
                function_calls = event.get_function_calls()
                if function_calls:
                    tool_names = [
                        call.name for call in function_calls if hasattr(call, "name")
                    ]
                    summary_parts.append(f"Tools: {', '.join(tool_names)}")

            # Add state_delta information for state update events
            if (
                hasattr(event, "actions")
                and event.actions
                and hasattr(event.actions, "state_delta")
                and event.actions.state_delta
            ):
                state_info = self._summarize_state_delta(event.actions.state_delta)
                if state_info:
                    summary_parts.append(f"State: {state_info}")

            # Add artifact_delta information for artifact events
            if (
                hasattr(event, "actions")
                and event.actions
                and hasattr(event.actions, "artifact_delta")
                and event.actions.artifact_delta
            ):
                artifact_info = self._summarize_artifact_delta(
                    event.actions.artifact_delta
                )
                if artifact_info:
                    summary_parts.append(f"Artifacts: {artifact_info}")

            return " | ".join(summary_parts)

        except Exception as e:
            logger.debug(f"Failed to create event summary: {e}")
            return "Event summary unavailable"

    def _summarize_state_delta(self, state_delta: Dict[str, Any]) -> str:
        """Create a brief summary of state_delta changes for indexing."""
        try:
            summary_parts = []

            # Extract key state information that's useful for search
            if "conversation_topic" in state_delta:
                summary_parts.append(f"topic: {state_delta['conversation_topic']}")

            if "message_count" in state_delta:
                summary_parts.append(f"msgs: {state_delta['message_count']}")

            if "last_interaction" in state_delta:
                # Extract just the date part for readability
                timestamp = state_delta["last_interaction"]
                if isinstance(timestamp, str) and "T" in timestamp:
                    date_part = timestamp.split("T")[0]
                    summary_parts.append(f"updated: {date_part}")

            # Add any other searchable state fields
            searchable_fields = ["status", "phase", "current_task", "focus_area"]
            for field in searchable_fields:
                if field in state_delta and state_delta[field]:
                    summary_parts.append(f"{field}: {state_delta[field]}")

            return ", ".join(summary_parts[:4])  # Limit to 4 key items

        except Exception as e:
            logger.debug(f"Failed to summarize state_delta: {e}")
            return "state_update"

    def _summarize_artifact_delta(self, artifact_delta: Dict[str, int]) -> str:
        """Create a brief summary of artifact_delta changes for indexing."""
        try:
            summary_parts = []

            # Process each artifact in the delta
            for filename, version in artifact_delta.items():
                # Extract file info
                file_base = Path(filename).stem
                file_ext = Path(filename).suffix

                # Create concise summary
                if file_ext:
                    summary_parts.append(f"{file_base}{file_ext} v{version}")
                else:
                    summary_parts.append(f"{filename} v{version}")

            return ", ".join(summary_parts[:3])  # Limit to 3 files for readability

        except Exception as e:
            logger.debug(f"Failed to summarize artifact_delta: {e}")
            return "artifact_created"

    def _extract_event_topics(self, event) -> List[str]:
        """Extract topic keywords from event content."""
        topics = []

        try:
            # Simple topic extraction from text
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
            ):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        text = part.text.lower()

                        # Look for academic/research-related topics
                        academic_keywords = [
                            "research",
                            "paper",
                            "study",
                            "analysis",
                            "data",
                            "model",
                            "algorithm",
                            "machine learning",
                            "deep learning",
                            "neural",
                            "database",
                            "postgresql",
                            "sql",
                            "query",
                            "table",
                            "python",
                            "code",
                            "programming",
                            "development",
                        ]

                        for keyword in academic_keywords:
                            if keyword in text:
                                topics.append(keyword)

        except Exception as e:
            logger.debug(f"Failed to extract topics from event: {e}")

        return list(set(topics))  # Remove duplicates

    def _classify_event_type(self, event) -> str:
        """Classify event type based on ADK event structure."""
        try:
            # Check for function calls
            if hasattr(event, "get_function_calls"):
                function_calls = event.get_function_calls()
                if function_calls:
                    return "function_call"

            # Check for function responses
            if hasattr(event, "get_function_responses"):
                function_responses = event.get_function_responses()
                if function_responses:
                    return "function_response"

            # Check for text content
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
            ):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        # Determine if streaming or complete based on partial flag
                        if hasattr(event, "partial") and event.partial:
                            return "streaming_text"
                        else:
                            return "text_message"

            # Check for actions/control signals
            if hasattr(event, "actions") and event.actions:
                if hasattr(event.actions, "state_delta") and event.actions.state_delta:
                    return "state_update"
                if (
                    hasattr(event.actions, "artifact_delta")
                    and event.actions.artifact_delta
                ):
                    return "artifact_update"
                if (
                    hasattr(event.actions, "transfer_to_agent")
                    and event.actions.transfer_to_agent
                ):
                    return "agent_transfer"
                if hasattr(event.actions, "escalate") and event.actions.escalate:
                    return "escalation"

            return "unknown"

        except Exception as e:
            logger.debug(f"Failed to classify event type: {e}")
            return "unknown"
