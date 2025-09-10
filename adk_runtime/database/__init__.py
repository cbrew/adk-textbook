"""
Direct PostgreSQL database layer for ADK runtime.

Simple, fast, and transparent database operations without ORM overhead.
Uses raw SQL with safe parameter binding for optimal performance.
"""

from .connection import DatabaseManager
from .migrations import MigrationManager
from .schema import SCHEMA_VERSION

__all__ = ["DatabaseManager", "MigrationManager", "SCHEMA_VERSION"]
