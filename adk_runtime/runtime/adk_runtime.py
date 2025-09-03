"""
PostgreSQL-backed ADK runtime implementation.

Provides a complete ADK runtime using PostgreSQL for persistence.
"""

import logging
from typing import Optional

from ..database.connection import DatabaseManager, DatabaseConfig
from ..services.session_service import PostgreSQLSessionService
from ..services.memory_service import PostgreSQLMemoryService
from ..services.artifact_service import PostgreSQLArtifactService

logger = logging.getLogger(__name__)


class PostgreSQLADKRuntime:
    """
    Complete ADK runtime with PostgreSQL persistence.
    
    Provides session management, memory storage, and artifact handling
    using a local PostgreSQL database instead of Google Cloud services.
    """
    
    def __init__(
        self, 
        database_config: Optional[DatabaseConfig] = None,
        artifact_storage_path: str = "./artifacts"
    ):
        """
        Initialize the PostgreSQL ADK runtime.
        
        Args:
            database_config: Database connection configuration
            artifact_storage_path: Local path for artifact file storage
        """
        self.database_config = database_config or DatabaseConfig()
        self.artifact_storage_path = artifact_storage_path
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.database_config)
        
        # Initialize services
        self.session_service = PostgreSQLSessionService(self.db_manager)
        self.memory_service = PostgreSQLMemoryService(self.db_manager)
        self.artifact_service = PostgreSQLArtifactService(
            self.db_manager, 
            self.artifact_storage_path
        )
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the runtime and all services."""
        try:
            # Initialize database connection pool
            self.db_manager.initialize()
            await self.db_manager.initialize_async()
            
            # Verify database schema is up to date
            await self._verify_schema()
            
            self._initialized = True
            logger.info("PostgreSQL ADK Runtime initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL ADK Runtime: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the runtime and cleanup resources."""
        try:
            # Close database connections
            self.db_manager.close()
            await self.db_manager.close_async()
            
            self._initialized = False
            logger.info("PostgreSQL ADK Runtime shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during runtime shutdown: {e}")
            raise
    
    def get_session_service(self) -> PostgreSQLSessionService:
        """Get the session service instance."""
        if not self._initialized:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        return self.session_service
    
    def get_memory_service(self) -> PostgreSQLMemoryService:
        """Get the memory service instance."""
        if not self._initialized:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        return self.memory_service
    
    def get_artifact_service(self) -> PostgreSQLArtifactService:
        """Get the artifact service instance."""
        if not self._initialized:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        return self.artifact_service
    
    async def _verify_schema(self) -> None:
        """Verify that the database schema is properly set up."""
        try:
            # Check if migrations table exists
            result = self.db_manager.execute_query(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'schema_migrations'
                )
                """,
                fetch_one=True
            )
            
            if not result or not result.get("exists"):
                raise RuntimeError(
                    "Database schema not initialized. Please run migrations first.\n"
                    "Use: python textbook-adk-ch07-runtime/examples/setup_database.py"
                )
            
            # Check for required tables
            required_tables = ["sessions", "events", "artifacts", "memory"]
            for table in required_tables:
                result = self.db_manager.execute_query(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                    """,
                    (table,),
                    fetch_one=True
                )
                
                if not result or not result.get("exists"):
                    raise RuntimeError(f"Required table '{table}' not found in database")
            
            logger.info("Database schema verification complete")
            
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            raise
    
    @classmethod
    async def create_and_initialize(
        cls,
        database_config: Optional[DatabaseConfig] = None,
        artifact_storage_path: str = "./artifacts"
    ) -> "PostgreSQLADKRuntime":
        """
        Create and initialize a PostgreSQL ADK Runtime instance.
        
        Convenience method that handles both creation and initialization.
        """
        runtime = cls(database_config, artifact_storage_path)
        await runtime.initialize()
        return runtime
    
    def __str__(self) -> str:
        return f"PostgreSQLADKRuntime(db={self.database_config.host}:{self.database_config.port}/{self.database_config.database}, initialized={self._initialized})"
    
    def __repr__(self) -> str:
        return self.__str__()