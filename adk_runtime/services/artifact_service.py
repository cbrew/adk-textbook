"""
PostgreSQL-backed artifact service implementation.

Provides pure PostgreSQL BYTEA storage with size limits.
"""

import hashlib
import logging
import uuid
from typing import TYPE_CHECKING, Optional

from google.adk.artifacts import BaseArtifactService
from google.adk.events import EventActions
from google.adk.events.event import Event
from google.genai import types

if TYPE_CHECKING:
    from .session_service import PostgreSQLSessionService

from ..database.connection import DatabaseManager, deserialize_json, serialize_json
from ..database.schema import QUERIES

logger = logging.getLogger(__name__)


class PostgreSQLArtifactService(BaseArtifactService):
    """PostgreSQL-backed artifact service with pure PostgreSQL BYTEA storage."""

    # Maximum artifact size for PostgreSQL BYTEA storage (25MB)
    MAX_ARTIFACT_SIZE = 25 * 1024 * 1024

    def __init__(self, database_manager: DatabaseManager, storage_root: str = "./artifacts", session_service: Optional["PostgreSQLSessionService"] = None):
        self.db = database_manager
        # Note: storage_root parameter kept for compatibility but no longer used
        self.session_service = session_service

    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        """Save artifact using PostgreSQL BYTEA storage with event sourcing."""
        try:
            # Check if artifact already exists to determine version
            existing_versions = await self.list_versions(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                filename=filename
            )
            next_version = len(existing_versions)

            # Extract content and metadata from artifact
            content_bytes = None
            content_type = None
            file_size = 0

            if hasattr(artifact, 'data') and artifact.data:
                content_bytes = artifact.data
                content_type = getattr(artifact, 'mime_type', 'application/octet-stream')
            elif hasattr(artifact, 'text') and artifact.text:
                content_bytes = artifact.text.encode('utf-8')
                content_type = 'text/plain'
            else:
                raise ValueError(f"Unsupported artifact type: {type(artifact)}")

            file_size = len(content_bytes)

            # Check size limit
            if file_size > self.MAX_ARTIFACT_SIZE:
                raise ValueError(f"Artifact too large ({file_size} bytes, max {self.MAX_ARTIFACT_SIZE} bytes / 25MB). Consider splitting into smaller files.")

            content_hash = hashlib.sha256(content_bytes).hexdigest()

            # Create event for event sourcing before saving artifact
            event_id = str(uuid.uuid4())
            artifact_event = Event(
                id=event_id,
                author="system",
                content=types.Content(
                    role="system",
                    parts=[types.Part(text=f"Created artifact '{filename}' (version {next_version}, {file_size} bytes)")]
                ),
                actions=EventActions(
                    artifact_delta={filename: next_version}
                )
            )

            # Store in PostgreSQL BYTEA (pure BYTEA storage)
            storage_type = 'postgresql'
            file_path = f"pg://{app_name}/{user_id}/{session_id}/{filename}_v{next_version}"
            file_data = content_bytes
            logger.debug(f"Using PostgreSQL BYTEA storage for {filename} ({file_size} bytes)")

            # Save event to session first (to satisfy foreign key constraint)
            if self.session_service:
                # Save event and get the actual stored event ID
                stored_event_id = self.session_service.save_event(session_id, artifact_event)
                logger.debug(f"Saved artifact creation event {event_id} for session {session_id}")
            else:
                logger.warning("No session service available - event sourcing disabled")

            # Store artifact metadata and content in database
            metadata = {
                "app_name": app_name,
                "version": next_version,
                "content_hash": content_hash,
                "original_filename": filename,
                "storage_type": storage_type,
                "event_id": event_id
            }

            artifact_id = str(uuid.uuid4())
            self.db.execute_query(
                QUERIES["insert_artifact"],
                (
                    artifact_id,
                    session_id,
                    filename,
                    content_type,
                    file_size,
                    file_path,
                    serialize_json(metadata),
                    file_data,
                    event_id,
                    storage_type
                ),
                fetch_all=False
            )

            logger.info(f"Saved artifact {filename} v{next_version} for session {session_id} (size: {file_size} bytes, storage: {storage_type})")
            return next_version

        except Exception as e:
            logger.error(f"Failed to save artifact {filename}: {e}")
            raise

    async def load_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: int | None = None,
    ) -> types.Part | None:
        """Load artifact from PostgreSQL BYTEA storage using metadata."""
        try:
            # Query for artifact metadata and data
            if version is not None:
                # Load specific version
                query = """
                SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at, file_data, event_id, storage_type
                FROM artifacts 
                WHERE session_id = %s AND filename = %s AND metadata->>'version' = %s
                ORDER BY created_at DESC 
                LIMIT 1
                """
                params = (session_id, filename, str(version))
            else:
                # Load latest version
                query = """
                SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at, file_data, event_id, storage_type
                FROM artifacts 
                WHERE session_id = %s AND filename = %s
                ORDER BY (metadata->>'version')::int DESC 
                LIMIT 1
                """
                params = (session_id, filename)

            result = self.db.execute_query(query, params, fetch_one=True)

            if not result:
                logger.debug(f"Artifact {filename} v{version} not found in session {session_id}")
                return None

            # Handle JSONB metadata (might be dict or string)
            raw_metadata = result.get("metadata", "{}")
            if isinstance(raw_metadata, dict):
                metadata = raw_metadata
            else:
                metadata = deserialize_json(raw_metadata)
                if not isinstance(metadata, dict):
                    metadata = {}

            # Verify app/user match
            if metadata.get("app_name") != app_name:
                logger.warning(f"Artifact {filename} app mismatch: expected {app_name}, got {metadata.get('app_name')}")
                return None

            # Load from PostgreSQL BYTEA
            file_data = result.get("file_data")
            if file_data is None:
                logger.error(f"Artifact {filename} has no file_data in PostgreSQL BYTEA storage")
                return None

            # Handle PostgreSQL BYTEA data (can be memoryview or bytes)
            if isinstance(file_data, memoryview):
                content_bytes = file_data.tobytes()
            elif isinstance(file_data, bytes):
                content_bytes = file_data
            else:
                logger.error(f"Unexpected file_data type: {type(file_data)}")
                return None

            logger.debug(f"Loaded {filename} from PostgreSQL BYTEA ({len(content_bytes)} bytes)")

            # Create appropriate Part object based on content type
            content_type = result.get("content_type", "application/octet-stream")

            if content_type.startswith("text/"):
                return types.Part(text=content_bytes.decode('utf-8'))
            else:
                return types.Part(data=content_bytes, mime_type=content_type)

        except Exception as e:
            logger.error(f"Failed to load artifact {filename}: {e}")
            return None

    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        """List all artifact filenames in a session."""
        try:
            results = self.db.execute_query(
                QUERIES["get_session_artifacts"],
                (session_id,),
                fetch_all=True
            )

            # Filter by app_name and collect unique filenames
            filenames = set()
            for result in results:
                raw_metadata = result.get("metadata", "{}")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata
                else:
                    metadata = deserialize_json(raw_metadata)

                if isinstance(metadata, dict) and metadata.get("app_name") == app_name:
                    filenames.add(result["filename"])

            return sorted(list(filenames))

        except Exception as e:
            logger.error(f"Failed to list artifacts for session {session_id}: {e}")
            return []

    async def delete_artifact(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> None:
        """Delete all versions of an artifact."""
        try:
            # Get all versions of the artifact
            results = self.db.execute_query(
                """
                SELECT id, file_path, metadata, storage_type 
                FROM artifacts 
                WHERE session_id = %s AND filename = %s
                """,
                (session_id, filename),
                fetch_all=True
            )

            deleted_count = 0
            for result in results:
                raw_metadata = result.get("metadata", "{}")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata
                else:
                    metadata = deserialize_json(raw_metadata)

                if isinstance(metadata, dict) and metadata.get("app_name") == app_name:
                    # Delete from database (no filesystem cleanup needed with pure BYTEA storage)
                    logger.debug("Deleting artifact from PostgreSQL BYTEA storage")

                    # Delete metadata and data from database
                    self.db.execute_query(
                        "DELETE FROM artifacts WHERE id = %s",
                        (result["id"],),
                        fetch_all=False
                    )
                    deleted_count += 1

            logger.info(f"Deleted {deleted_count} versions of artifact {filename} from session {session_id}")

        except Exception as e:
            logger.error(f"Failed to delete artifact {filename}: {e}")
            raise

    async def list_versions(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> list[int]:
        """List all versions of an artifact."""
        try:
            results = self.db.execute_query(
                """
                SELECT metadata 
                FROM artifacts 
                WHERE session_id = %s AND filename = %s
                ORDER BY (metadata->>'version')::int ASC
                """,
                (session_id, filename),
                fetch_all=True
            )

            versions = []
            for result in results:
                raw_metadata = result.get("metadata", "{}")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata
                else:
                    metadata = deserialize_json(raw_metadata)

                if isinstance(metadata, dict) and metadata.get("app_name") == app_name:
                    version = metadata.get("version")
                    if isinstance(version, int):
                        versions.append(version)

            return versions

        except Exception as e:
            logger.error(f"Failed to list versions for artifact {filename}: {e}")
            return []

    def cleanup_orphaned_files(self) -> int:
        """No-op: Pure PostgreSQL BYTEA storage doesn't use filesystem files."""
        logger.info("No filesystem cleanup needed - using pure PostgreSQL BYTEA storage")
        return 0
