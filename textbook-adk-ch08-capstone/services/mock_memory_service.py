"""
Mock MemoryService for standalone operation.

Implements ADK MemoryService interface with in-memory storage.
Real production implementation would use vector database.
"""

from typing import List, Dict, Any, Optional
from google.adk.memory import BaseMemoryService


class MockMemoryService(BaseMemoryService):
    """
    In-memory memory service for testing.

    Not used in this demo, but required by ADK Runner.
    """

    def __init__(self):
        self._memories: Dict[str, List[Dict[str, Any]]] = {}

    def _make_key(self, app_name: str, user_id: str, session_id: str) -> str:
        """Generate storage key."""
        return f"{app_name}:{user_id}:{session_id}"

    async def add_memory(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        memory: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add memory entry."""
        key = self._make_key(app_name, user_id, session_id)

        if key not in self._memories:
            self._memories[key] = []

        self._memories[key].append({
            "content": memory,
            "metadata": metadata or {}
        })

    async def search_memories(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search memories (simple keyword match)."""
        key = self._make_key(app_name, user_id, session_id)
        memories = self._memories.get(key, [])

        # Simple keyword search
        query_lower = query.lower()
        matching = [
            m for m in memories
            if query_lower in m["content"].lower()
        ]

        return matching[:limit]

    async def clear_memories(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """Clear all memories for session."""
        key = self._make_key(app_name, user_id, session_id)
        if key in self._memories:
            del self._memories[key]
