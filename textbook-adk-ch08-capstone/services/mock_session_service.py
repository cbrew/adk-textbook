"""
Mock SessionService for standalone operation.

Implements ADK SessionService interface with in-memory storage.
Real production implementation would use PostgreSQL (see Chapter 7).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from google.adk.sessions import SessionService, Session


class MockSessionService(SessionService):
    """
    In-memory session service for testing and standalone operation.

    Storage structure:
    {
        "app_name:user_id:session_id": {
            "id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "state": {...},
            "events": [...]
        }
    }
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, app_name: str, user_id: str, session_id: str) -> str:
        """Generate storage key for session."""
        return f"{app_name}:{user_id}:{session_id}"

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create new session with initial state."""
        key = self._make_key(app_name, user_id, session_id)

        now = datetime.now(timezone.utc)

        session_data = {
            "id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "state": state or {},
            "events": []
        }

        self._sessions[key] = session_data

        return Session(
            id=session_id,
            state=session_data["state"],
            created_at=now,
            updated_at=now
        )

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Optional[Session]:
        """Retrieve session by ID."""
        key = self._make_key(app_name, user_id, session_id)
        session_data = self._sessions.get(key)

        if not session_data:
            return None

        return Session(
            id=session_data["id"],
            state=session_data["state"],
            created_at=datetime.fromisoformat(session_data["created_at"]),
            updated_at=datetime.fromisoformat(session_data["updated_at"])
        )

    async def update_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state_delta: Dict[str, Any],
    ) -> Session:
        """Update session state with delta."""
        key = self._make_key(app_name, user_id, session_id)
        session_data = self._sessions.get(key)

        if not session_data:
            # Create session if it doesn't exist
            return await self.create_session(
                app_name, user_id, session_id, state=state_delta
            )

        # Merge state_delta into existing state
        session_data["state"].update(state_delta)
        session_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        return Session(
            id=session_data["id"],
            state=session_data["state"],
            created_at=datetime.fromisoformat(session_data["created_at"]),
            updated_at=datetime.fromisoformat(session_data["updated_at"])
        )

    async def list_sessions(
        self,
        app_name: str,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Session]:
        """List all sessions for a user in an app."""
        prefix = f"{app_name}:{user_id}:"

        matching_sessions = [
            Session(
                id=data["id"],
                state=data["state"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            for key, data in self._sessions.items()
            if key.startswith(prefix)
        ]

        # Sort by updated_at descending
        matching_sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return matching_sessions[offset:offset + limit]

    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> bool:
        """Delete session."""
        key = self._make_key(app_name, user_id, session_id)

        if key in self._sessions:
            del self._sessions[key]
            return True

        return False

    async def add_event(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        event: Dict[str, Any],
    ) -> None:
        """Add event to session history."""
        key = self._make_key(app_name, user_id, session_id)
        session_data = self._sessions.get(key)

        if session_data:
            session_data["events"].append(event)
            session_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    def get_session_events(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all events for a session (for debugging)."""
        key = self._make_key(app_name, user_id, session_id)
        session_data = self._sessions.get(key)

        return session_data["events"] if session_data else []
