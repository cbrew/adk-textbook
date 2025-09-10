"""
PostgreSQL Chat Agent for ADK.

A conversational agent with PostgreSQL-backed persistent memory,
session management, and artifact storage capabilities.
"""
from .agent import agent
__version__ = "1.0.0"

root_agent = agent
