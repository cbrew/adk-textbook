"""
Simplified Literature Review Agent for Chapter 6 - ADK State Management Demos

This agent demonstrates all ADK state management patterns through a realistic
academic workflow: managing papers through a 4-stage pipeline.

Stages:
1. Search & Collect (manual entry + mock API)
2. Offline Import (BibTeX batch import via manual events) 
3. Screen & Classify (relevance screening)
4. Extract & Synthesize (theme identification)

State Management Patterns Demonstrated:
- Direct state access in tools (tool_context.state)
- output_key for automatic agent response saving
- State injection with {key} templating in instructions
- Manual event creation for batch operations
- State scoping with user:, app:, temp: prefixes
- Database persistence across sessions

Based on: https://google.github.io/adk-docs/sessions/state/
"""

from .agent import agent as simplified_litreview_agent

__all__ = ["simplified_litreview_agent"]