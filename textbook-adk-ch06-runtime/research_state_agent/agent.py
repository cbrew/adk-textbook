"""
Research State Agent - Demonstrates ADK-compliant state management

This agent follows ADK best practices for state management using proper
tools and state key naming conventions.

IMPORTANT: This agent does NOT automatically see external state changes.
External systems must explicitly notify the agent via system messages
when state is updated, which is what our FastAPI endpoints do.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompts import AGENT_INSTRUCTION
from .tools.research_state_tools import (
    add_research_progress_tool,
    add_research_source_tool,
    get_research_status_tool,
    set_research_deadline_tool,
    set_research_priority_tool,
    set_research_topic_tool,
)

# Create the agent instance using ADK best practices
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="research_state_agent",
    instruction=AGENT_INSTRUCTION,
    tools=[
        get_research_status_tool,
        set_research_priority_tool,
        set_research_deadline_tool,
        add_research_source_tool,
        set_research_topic_tool,
        add_research_progress_tool,
    ],
)