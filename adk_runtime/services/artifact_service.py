"""
PostgreSQL-backed artifact service implementation.

Provides file storage with PostgreSQL metadata and local filesystem storage.
"""

import os
import uuid
import shutil
import logging
import hashlib
from pathlib import Path
from typing import List, Optional

from google.adk.artifacts import BaseArtifactService
from google.genai import types

from ..database.connection import DatabaseManager, serialize_json, deserialize_json
from ..database.schema import QUERIES

logger = logging.getLogger(__name__)


class PostgreSQLArtifactService(BaseArtifactService):
    """PostgreSQL-backed artifact service with filesystem storage."""
    
    def __init__(self, database_manager: DatabaseManager, storage_root: str = "./artifacts"):
        self.db = database_manager
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        """Save artifact to filesystem and metadata to PostgreSQL."""
        try:
            # Create directory structure: storage_root/app_name/user_id/session_id/
            artifact_dir = self.storage_root / app_name / user_id / session_id
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if artifact already exists to determine version
            existing_versions = await self.list_versions(
                app_name=app_name,
                user_id=user_id, 
                session_id=session_id,
                filename=filename
            )
            next_version = len(existing_versions)
            
            # Create versioned filename
            file_stem = Path(filename).stem
            file_suffix = Path(filename).suffix
            versioned_filename = f"{file_stem}_v{next_version}{file_suffix}"
            file_path = artifact_dir / versioned_filename
            
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
            
            # Write file to storage
            with open(file_path, 'wb') as f:
                f.write(content_bytes)
                file_size = len(content_bytes)
            
            # Store metadata in database
            metadata = {
                "app_name": app_name,
                "version": next_version,
                "content_hash": hashlib.sha256(content_bytes).hexdigest(),
                "original_filename": filename,
                "storage_path": str(file_path.relative_to(self.storage_root))
            }
            
            self.db.execute_query(
                QUERIES["insert_artifact"],
                (
                    str(uuid.uuid4()),
                    session_id,
                    filename,
                    content_type,
                    file_size,
                    str(file_path),
                    serialize_json(metadata)
                ),
                fetch_all=False
            )
            
            logger.info(f"Saved artifact {filename} v{next_version} for session {session_id} (size: {file_size} bytes)")
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
        version: Optional[int] = None,
    ) -> Optional[types.Part]:
        """Load artifact from filesystem using PostgreSQL metadata."""
        try:
            # Query for artifact metadata
            if version is not None:
                # Load specific version
                query = """
                SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at
                FROM artifacts 
                WHERE session_id = %s AND filename = %s AND metadata->>'version' = %s
                ORDER BY created_at DESC 
                LIMIT 1
                """
                params = (session_id, filename, str(version))
            else:
                # Load latest version
                query = """
                SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at
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
            
            # Load file content
            file_path = Path(result["file_path"])
            if not file_path.exists():
                logger.error(f"Artifact file not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                content_bytes = f.read()
            
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
    ) -> List[str]:
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
                SELECT id, file_path, metadata 
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
                    # Delete file from filesystem
                    file_path = Path(result["file_path"])
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Delete metadata from database
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
    ) -> List[int]:
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
        """Clean up files that exist in filesystem but not in database."""
        try:
            cleaned_count = 0
            
            # Walk through all files in storage
            for file_path in self.storage_root.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Check if file exists in database
                result = self.db.execute_query(
                    "SELECT id FROM artifacts WHERE file_path = %s",
                    (str(file_path),),
                    fetch_one=True
                )
                
                if not result:
                    # Orphaned file - remove it
                    file_path.unlink()
                    cleaned_count += 1
                    logger.debug(f"Removed orphaned file: {file_path}")
            
            # Also clean up empty directories
            for dir_path in self.storage_root.rglob("*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.debug(f"Removed empty directory: {dir_path}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} orphaned files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned files: {e}")
            return 0