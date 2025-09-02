#!/usr/bin/env python3
"""
Check database migration status.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import adk_runtime
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_runtime.database import DatabaseManager, MigrationManager
from adk_runtime.database.connection import DatabaseConfig


def main():
    """Check and display migration status."""
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
        status = mgr.get_migration_status()
        
        print("Migration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error checking migration status: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()