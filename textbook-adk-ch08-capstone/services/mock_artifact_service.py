"""
Mock ArtifactService for standalone operation.

Implements ADK ArtifactService interface with in-memory storage.
Real production implementation would use S3/GCS + database (see Chapter 7).
"""

from typing import Dict, Any, List, Optional
from google.adk.artifacts import ArtifactService, Artifact
from datetime import datetime, timezone
import io


class MockArtifactService(ArtifactService):
    """
    In-memory artifact service for testing.

    Stores artifacts as bytes in memory (not suitable for production).
    """

    def __init__(self):
        self._artifacts: Dict[str, Dict[str, Any]] = {}

    def _make_key(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str
    ) -> str:
        """Generate storage key for artifact."""
        return f"{app_name}:{user_id}:{session_id}:{filename}"

    async def save_artifact(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Save artifact to memory."""
        key = self._make_key(app_name, user_id, session_id, filename)

        now = datetime.now(timezone.utc)

        # Calculate version (increment if exists)
        existing = self._artifacts.get(key)
        version = (existing["version"] + 1) if existing else 1

        artifact_data = {
            "filename": filename,
            "data": data,
            "content_type": content_type or "application/octet-stream",
            "metadata": metadata or {},
            "version": version,
            "size": len(data),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        self._artifacts[key] = artifact_data

        return Artifact(
            filename=filename,
            version=version,
            size=len(data),
            content_type=artifact_data["content_type"],
            metadata=artifact_data["metadata"],
            created_at=now,
            updated_at=now,
        )

    async def load_artifact(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: Optional[int] = None,
    ) -> Optional[bytes]:
        """Load artifact from memory."""
        key = self._make_key(app_name, user_id, session_id, filename)
        artifact_data = self._artifacts.get(key)

        if not artifact_data:
            return None

        # Version checking not implemented in this simple mock
        # (would need to store version history)
        return artifact_data["data"]

    async def list_artifacts(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> List[Artifact]:
        """List all artifacts for a session."""
        prefix = f"{app_name}:{user_id}:{session_id}:"

        artifacts = []
        for key, data in self._artifacts.items():
            if key.startswith(prefix):
                artifacts.append(Artifact(
                    filename=data["filename"],
                    version=data["version"],
                    size=data["size"],
                    content_type=data["content_type"],
                    metadata=data["metadata"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                ))

        return artifacts

    async def delete_artifact(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
    ) -> bool:
        """Delete artifact from memory."""
        key = self._make_key(app_name, user_id, session_id, filename)

        if key in self._artifacts:
            del self._artifacts[key]
            return True

        return False
