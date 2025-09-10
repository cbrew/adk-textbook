"""Simple chat agent for Textual UI testing."""

from .agent import SimpleChatAgent

__all__ = ["SimpleChatAgent", "root_agent"]

root_agent = SimpleChatAgent()
