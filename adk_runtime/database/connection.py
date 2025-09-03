"""
Direct PostgreSQL connection management with connection pooling.

Provides simple, safe database operations without ORM complexity.
"""

import json
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple, Union
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
import asyncpg
import asyncio
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    
    host: str = "localhost"
    port: int = 5432
    database: str = "adk_runtime"
    username: str = "adk_user"
    password: str = "adk_password"
    min_connections: int = 1
    max_connections: int = 20
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseManager:
    """
    Direct PostgreSQL database manager with connection pooling.
    
    Provides simple, safe database operations using raw SQL with parameter binding.
    No ORM overhead - just fast, transparent database access.
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._async_pool: Optional[asyncpg.Pool] = None
        
    def initialize(self) -> None:
        """Initialize synchronous connection pool."""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def initialize_async(self) -> None:
        """Initialize asynchronous connection pool."""
        try:
            self._async_pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections
            )
            logger.info("Async database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize async database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool (context manager)."""
        if not self._pool:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Execute a SQL query with safe parameter binding.
        
        Args:
            query: SQL query with $1, $2, etc. placeholders
            params: Tuple of parameters to bind
            fetch_one: Return single row as dict
            fetch_all: Return all rows as list of dicts
            
        Returns:
            Query results or None for non-SELECT queries
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    # For INSERT/UPDATE/DELETE
                    conn.commit()
                    return None
    
    def execute_transaction(self, operations: List[Tuple[str, Optional[Tuple]]]) -> None:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of (query, params) tuples to execute
        """
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    for query, params in operations:
                        cursor.execute(query, params or ())
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    async def execute_query_async(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """Async version of execute_query."""
        if not self._async_pool:
            raise RuntimeError("Async pool not initialized. Call initialize_async() first.")
        
        async with self._async_pool.acquire() as conn:
            if fetch_one:
                result = await conn.fetchrow(query, *(params or ()))
                return dict(result) if result else None
            elif fetch_all:
                results = await conn.fetch(query, *(params or ()))
                return [dict(row) for row in results]
            else:
                await conn.execute(query, *(params or ()))
                return None
    
    def close(self) -> None:
        """Close connection pools."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")
    
    async def close_async(self) -> None:
        """Close async connection pool."""
        if self._async_pool:
            await self._async_pool.close()
            logger.info("Async database connection pool closed")


def serialize_json(obj: Any) -> str:
    """Safely serialize objects to JSON for database storage."""
    return json.dumps(obj, default=str, ensure_ascii=False)


def deserialize_json(json_str: Optional[str]) -> Any:
    """Safely deserialize JSON from database."""
    if json_str is None:
        return None
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to deserialize JSON: {json_str}")
        return None