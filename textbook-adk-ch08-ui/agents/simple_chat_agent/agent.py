#!/usr/bin/env python3
"""
Simple chat agent for Textual UI integration.

This agent provides basic conversational capabilities using the model specified in .env.
"""

import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm


class SimpleChatAgent(Agent):
    """A simple conversational agent for testing Textual UI integration."""
    
    def __init__(self):
        # Use model from environment with fallback
        model_name = os.getenv("ANTHROPIC_MODEL", "anthropic/claude-3-5-haiku-20241022")
        
        super().__init__(
            name="simple_chat_agent",
            description="A simple agent for testing Textual chat interfaces",
            model=LiteLlm(model=model_name),
        )