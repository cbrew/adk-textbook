"""
ADK Core Library

Core functionality for interacting with Google's Agent Development Kit (ADK).
Includes consumers, event processing, and artifact management.
"""

from .artifact_consumer import ArtifactEventConsumer
from .chat_app import ADKChatApp
from .consumer import ADKConsumer
from .event_extractor import extract_description_from_event

__all__ = [
    "ADKConsumer",
    "ArtifactEventConsumer",
    "extract_description_from_event",
    "ADKChatApp"
]
