#!/usr/bin/env python3
"""
Database setup and migration example for ADK PostgreSQL runtime.

This script demonstrates how to:
1. Initialize database connections
2. Run migrations
3. Check database status
4. Reset database (for development)
"""

import logging
import os
import sys

from adk_runtime.database import DatabaseManager, MigrationManager
from adk_runtime.database.connection import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main setup function."""

    # Load configuration from environment or use defaults
    config = DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "adk_runtime"),
        username=os.getenv("DB_USER", "adk_user"),
        password=os.getenv("DB_PASSWORD", "adk_password"),
    )

    logger.info(
        f"Connecting to database: {config.host}:{config.port}/{config.database}"
    )

    # Initialize database manager
    db_manager = DatabaseManager(config)

    try:
        # Initialize connection pool
        db_manager.initialize()
        logger.info("Database connection established")

        # Initialize migration manager
        migration_manager = MigrationManager(db_manager)

        # Check current migration status
        status = migration_manager.get_migration_status()
        logger.info(f"Migration status: {status}")

        if not status.get("database_ready", False):
            logger.info("Running pending migrations...")
            migration_manager.run_pending_migrations()

            # Check status again
            status = migration_manager.get_migration_status()
            logger.info(f"Updated migration status: {status}")

        # Test basic database operations
        logger.info("Testing database operations...")
        test_basic_operations(db_manager)

        logger.info("Database setup completed successfully!")

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

    finally:
        db_manager.close()


def test_basic_operations(db_manager: DatabaseManager):
    """Test basic database operations to ensure everything works."""
    import json
    import uuid
    from datetime import datetime

    # Test session operations
    session_id = str(uuid.uuid4())
    user_id = "test_user_123"
    test_state = {
        "conversation": ["Hello", "Hi there!"],
        "context": {"topic": "database_testing"},
    }

    # Insert test session
    db_manager.execute_query(
        "INSERT INTO sessions (id, user_id, state) VALUES (%s, %s, %s)",
        (session_id, user_id, json.dumps(test_state)),
        fetch_all=False,
    )
    logger.info(f"Inserted test session: {session_id}")

    # Retrieve test session
    session = db_manager.execute_query(
        "SELECT * FROM sessions WHERE id = %s", (session_id,), fetch_one=True
    )
    logger.info(
        f"Retrieved session: {session['user_id']} with state keys: {list(session['state'].keys())}"
    )

    # Test event operations
    event_id = str(uuid.uuid4())
    event_data = {
        "type": "user_message",
        "content": "Test message",
        "timestamp": datetime.now().isoformat(),
    }

    db_manager.execute_query(
        "INSERT INTO events (id, session_id, event_type, event_data) VALUES (%s, %s, %s, %s)",
        (event_id, session_id, "test_event", json.dumps(event_data)),
        fetch_all=False,
    )
    logger.info(f"Inserted test event: {event_id}")

    # Retrieve events
    events = db_manager.execute_query(
        "SELECT * FROM events WHERE session_id = %s", (session_id,), fetch_all=True
    )
    logger.info(f"Retrieved {len(events)} events for session")

    # Clean up test data
    db_manager.execute_query(
        "DELETE FROM sessions WHERE id = %s", (session_id,), fetch_all=False
    )
    logger.info("Cleaned up test data")


if __name__ == "__main__":
    main()
