"""
Simple database migration system for ADK runtime.

No complex ORM migrations - just straightforward SQL execution with version tracking.
"""

import logging
from typing import List
from .connection import DatabaseManager
from .schema import SCHEMA_SQL, SCHEMA_VERSION, get_all_schema_versions

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Simple migration manager for database schema changes.

    Tracks applied migrations and executes new ones in order.
    Much simpler than Alembic - just pure SQL with version tracking.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def initialize_migrations_table(self) -> None:
        """Create the migrations tracking table if it doesn't exist."""
        try:
            self.db.execute_query(SCHEMA_SQL["005_create_migrations"], fetch_all=False)
            logger.info("Migrations table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize migrations table: {e}")
            raise

    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration versions."""
        try:
            results = self.db.execute_query(
                "SELECT version FROM schema_migrations ORDER BY version", fetch_all=True
            )
            return [row["version"] for row in (results or [])]
        except Exception as e:
            # Table might not exist yet
            logger.info(f"Could not get applied migrations: {e}")
            return []

    def mark_migration_applied(self, version: str) -> None:
        """Mark a migration version as applied."""
        self.db.execute_query(
            "INSERT INTO schema_migrations (version) VALUES (%s)",
            (version,),
            fetch_all=False,
        )
        logger.info(f"Marked migration {version} as applied")

    def run_migration(self, version: str) -> None:
        """Run a specific migration version."""
        migration_key = None
        for key in SCHEMA_SQL:
            if key.startswith(f"{version}_"):
                migration_key = key
                break

        if not migration_key:
            raise ValueError(f"Migration {version} not found")

        try:
            # Execute the migration SQL
            sql = SCHEMA_SQL[migration_key]
            logger.info(f"Running migration {version}: {migration_key}")

            # Split on semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
            operations = [(stmt, None) for stmt in statements]

            self.db.execute_transaction(operations)

            # Mark as applied
            self.mark_migration_applied(version)
            logger.info(f"Migration {version} completed successfully")

        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            raise

    def run_pending_migrations(self) -> None:
        """Run all pending migrations in order."""
        # Initialize migrations table first
        self.initialize_migrations_table()

        # Get applied and available migrations
        applied = set(self.get_applied_migrations())
        available = get_all_schema_versions()

        # Find pending migrations
        pending = [v for v in available if v not in applied]
        pending.sort()  # Ensure proper order

        if not pending:
            logger.info("No pending migrations")
            return

        logger.info(f"Running {len(pending)} pending migrations: {pending}")

        for version in pending:
            self.run_migration(version)

        logger.info("All migrations completed successfully")

    def get_migration_status(self) -> dict:
        """Get current migration status."""
        try:
            applied = set(self.get_applied_migrations())
            available = set(get_all_schema_versions())
            pending = available - applied

            return {
                "current_version": SCHEMA_VERSION,
                "applied_migrations": sorted(applied),
                "pending_migrations": sorted(pending),
                "total_available": len(available),
                "database_ready": len(pending) == 0,
            }
        except Exception as e:
            return {"error": str(e), "database_ready": False}

    def reset_database(self) -> None:
        """
        WARNING: Drop all tables and reset database.
        Only use for development/testing!
        """
        logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")

        reset_sql = """
        DROP TABLE IF EXISTS memory CASCADE;
        DROP TABLE IF EXISTS artifacts CASCADE;
        DROP TABLE IF EXISTS events CASCADE;
        DROP TABLE IF EXISTS sessions CASCADE;
        DROP TABLE IF EXISTS schema_migrations CASCADE;
        """

        statements = [stmt.strip() for stmt in reset_sql.split(";") if stmt.strip()]
        operations = [(stmt, None) for stmt in statements]

        self.db.execute_transaction(operations)
        logger.info("Database reset completed")


def create_database_if_not_exists(config) -> None:
    """Create the database if it doesn't exist (requires superuser connection)."""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    # Connect to postgres database to create our database
    try:
        conn = psycopg2.connect(
            host=config.host,
            port=config.port,
            database="postgres",  # Connect to default postgres db
            user=config.username,
            password=config.password,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (config.database,)
            )

            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {config.database}")
                logger.info(f"Created database {config.database}")
            else:
                logger.info(f"Database {config.database} already exists")

        conn.close()

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        # Don't raise - database might already exist or we might not have permissions
