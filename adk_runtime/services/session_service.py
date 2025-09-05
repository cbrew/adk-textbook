"""
PostgreSQL-backed session service implementation.

Provides persistent session storage using local PostgreSQL database.
"""

import time
import uuid
import logging
from typing import Any, Dict, List, Optional

from google.adk.sessions import BaseSessionService
from google.adk.sessions.base_session_service import GetSessionConfig, ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.events.event import Event

from ..database.connection import DatabaseManager, serialize_json, deserialize_json
from ..database.schema import QUERIES

logger = logging.getLogger(__name__)


class PostgreSQLSessionService(BaseSessionService):
    """PostgreSQL-backed session service for local persistence."""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
        
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        """Creates a new session with PostgreSQL persistence."""
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        if state is None:
            state = {}
            
        # Create session record - store state with app metadata
        session_data = {
            "app_name": app_name,
            **state
        }
        
        # Insert into database
        self.db.execute_query(
            QUERIES["insert_session"],
            (session_id, user_id, serialize_json(session_data)),
            fetch_all=False
        )
        
        logger.info(f"Created session {session_id} for user {user_id} in app {app_name}")
        
        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state,
            events=[],
            last_update_time=time.time()
        )
    
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        """Gets a session from PostgreSQL storage."""
        # Get session record
        result = self.db.execute_query(
            QUERIES["get_session"],
            (session_id,),
            fetch_one=True
        )
        
        if not result:
            logger.debug(f"Session {session_id} not found")
            return None
            
        # Parse session data from JSONB state column  
        raw_state = result.get("state", "{}")
        if isinstance(raw_state, dict):
            session_data = raw_state
        else:
            session_data = deserialize_json(raw_state)
            if not isinstance(session_data, dict):
                session_data = {}
            
        # Verify app_name and user_id match
        stored_app_name = session_data.get("app_name", "")
        stored_user_id = result.get("user_id", "")
        
        if stored_app_name != app_name or stored_user_id != user_id:
            logger.warning(f"Session {session_id} app/user mismatch: expected {app_name}/{user_id}, got {stored_app_name}/{stored_user_id}")
            return None
        
        # Get events for this session
        events = []
        if config is None or config.num_recent_events != 0:
            events = self._load_session_events(session_id, config)
        
        # Extract state (excluding metadata fields)  
        state = {k: v for k, v in session_data.items() 
                if k not in ["app_name"]}
        
        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state,
            events=events,
            last_update_time=result.get("updated_at", time.time()).timestamp() if hasattr(result.get("updated_at"), "timestamp") else time.time()
        )
    
    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        """Lists all sessions for a user in an app."""
        # Get user sessions (limited to reasonable number)
        results = self.db.execute_query(
            QUERIES["get_user_sessions"],
            (user_id, 100),  # Limit to 100 most recent sessions
            fetch_all=True
        )
        
        sessions = []
        for result in results:
            raw_state = result.get("state", "{}")
            if isinstance(raw_state, dict):
                session_data = raw_state
            else:
                session_data = deserialize_json(raw_state)
                if not isinstance(session_data, dict):
                    continue
                
            # Filter by app_name
            if session_data.get("app_name") != app_name:
                continue
            
            # Extract state (excluding metadata)
            state = {k: v for k, v in session_data.items() 
                    if k not in ["app_name"]}
            
            sessions.append(Session(
                id=result["id"],
                app_name=app_name,
                user_id=user_id,
                state=state,
                events=[],  # Events not loaded for list operation
                last_update_time=result.get("updated_at", time.time()).timestamp() if hasattr(result.get("updated_at"), "timestamp") else time.time()
            ))
        
        return ListSessionsResponse(sessions=sessions)
    
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """Deletes a session (cascades to events and artifacts)."""
        # Verify ownership before deletion
        session = await self.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if not session:
            logger.warning(f"Cannot delete session {session_id}: not found or access denied")
            return
            
        # Delete session (CASCADE will handle events and artifacts)
        self.db.execute_query(
            "DELETE FROM sessions WHERE id = %s",
            (session_id,),
            fetch_all=False
        )
        
        logger.info(f"Deleted session {session_id} for user {user_id} in app {app_name}")
    
    def _load_session_events(
        self, 
        session_id: str, 
        config: Optional[GetSessionConfig] = None
    ) -> List[Event]:
        """Load events for a session from the database."""
        # Determine query based on config
        if config and config.num_recent_events:
            results = self.db.execute_query(
                QUERIES["get_recent_events"],
                (session_id, config.num_recent_events),
                fetch_all=True
            )
            # Reverse to get chronological order
            results = list(reversed(results))
        else:
            results = self.db.execute_query(
                QUERIES["get_session_events"],
                (session_id,),
                fetch_all=True
            )
        
        events = []
        for result in results:
            try:
                event_data = deserialize_json(result["event_data"])
                if event_data:
                    # Create Event object from stored data
                    # Note: This is a simplified reconstruction
                    # In a full implementation, you'd need to properly reconstruct
                    # Event objects with all their attributes
                    event = Event.model_validate(event_data)
                    events.append(event)
            except Exception as e:
                logger.warning(f"Failed to deserialize event {result['id']}: {e}")
        
        return events
    
    def save_event(self, session_id: str, event: Event) -> str:
        """Save an event to the database and return the event ID."""
        try:
            event_data = event.model_dump()
            
            # Determine event type from event characteristics
            event_type = self._determine_event_type(event)
            
            # Use the event ID if it exists, otherwise generate one
            db_event_id = event.id if event.id else str(uuid.uuid4())
            
            self.db.execute_query(
                QUERIES["insert_event"],
                (db_event_id, session_id, event_type, serialize_json(event_data)),
                fetch_all=False
            )
            
            return db_event_id
            
        except Exception as e:
            logger.error(f"Failed to save event for session {session_id}: {e}")
            raise
    
    def _determine_event_type(self, event: Event) -> str:
        """Determine event type based on event characteristics."""
        try:
            # Check for actions to determine event type
            if hasattr(event, 'actions') and event.actions:
                if hasattr(event.actions, 'artifact_delta') and event.actions.artifact_delta:
                    return 'artifact_created'
                if hasattr(event.actions, 'state_delta') and event.actions.state_delta:
                    return 'state_updated'
                if hasattr(event.actions, 'transfer_to_agent') and event.actions.transfer_to_agent:
                    return 'agent_transfer'
                if hasattr(event.actions, 'escalate') and event.actions.escalate:
                    return 'escalation'
            
            # Check for content type
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    return 'content_message'
            
            # Check for function calls/responses
            if hasattr(event, 'get_function_calls'):
                try:
                    calls = event.get_function_calls()
                    if calls:
                        return 'function_call'
                except:
                    pass
            
            if hasattr(event, 'get_function_responses'):
                try:
                    responses = event.get_function_responses()
                    if responses:
                        return 'function_response'
                except:
                    pass
            
            # Default fallback
            return 'generic_event'
            
        except Exception as e:
            logger.debug(f"Failed to determine event type: {e}")
            return 'unknown_event'
    
    def update_session_state(self, session_id: str, state: Dict[str, Any], app_name: str, user_id: str) -> None:
        """Update session state in the database."""
        try:
            # Prepare full state data including metadata
            full_state = {
                "app_name": app_name,
                **state
            }
            
            self.db.execute_query(
                QUERIES["update_session_state"],
                (serialize_json(full_state), session_id),
                fetch_all=False
            )
        except Exception as e:
            logger.error(f"Failed to update session {session_id} state: {e}")