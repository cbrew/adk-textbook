#!/usr/bin/env python3
"""
Reset database - WARNING: This destroys all data!
Only for development use.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import adk_runtime
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_runtime.database import DatabaseManager, MigrationManager
from adk_runtime.database.connection import DatabaseConfig


def main():
    """Reset the database - destroys all data!"""

    # Safety check
    env = os.getenv("ENVIRONMENT", "development")
    if env.lower() not in ["development", "dev", "test"]:
        print("ERROR: Database reset is only allowed in development/test environments!")
        print(f"Current environment: {env}")
        print("Set ENVIRONMENT=development to proceed")
        sys.exit(1)

    # Confirmation prompt
    response = input("WARNING: This will delete ALL data in the database. Continue? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Database reset cancelled.")
        sys.exit(0)

    config = DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "adk_runtime"),
        username=os.getenv("DB_USER", "adk_user"),
        password=os.getenv("DB_PASSWORD", "adk_password")
    )

    db = DatabaseManager(config)

    try:
        db.initialize()
        mgr = MigrationManager(db)
        mgr.reset_database()
        print("Database reset completed - all data has been deleted!")

    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
