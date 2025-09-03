"""
ADK Runtime with PostgreSQL Persistence

A custom implementation of the Google Agent Development Kit (ADK) runtime
that provides local PostgreSQL persistence while maintaining full ADK compatibility.

Key Components:
- SessionService: PostgreSQL-backed session and state management
- ArtifactService: Binary data storage with database metadata
- MemoryService: Semantic memory with pgvector support
- Runner: Event-driven execution orchestrator
"""

from .services.session_service import PostgreSQLSessionService
from .services.artifact_service import PostgreSQLArtifactService  
from .services.memory_service import PostgreSQLMemoryService
from .runtime.adk_runtime import PostgreSQLADKRuntime

__version__ = "0.1.0"
__all__ = [
    "PostgreSQLSessionService",
    "PostgreSQLArtifactService", 
    "PostgreSQLMemoryService",
    "PostgreSQLADKRuntime",
]