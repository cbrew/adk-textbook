"""
Enhanced Research State Agent - Demonstrates both state update approaches

This agent shows two ADK-compliant approaches for state management:
1. Simple approach: tool_context.update_state() for single updates
2. Standard approach: EventActions.state_delta for complex updates

Use this agent to demonstrate "The Standard Way" from ADK documentation.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from research_state_tools import (
    add_research_progress_tool,
    add_research_source_tool,
    get_research_status_tool,
    set_research_deadline_tool,
    set_research_priority_tool,
    set_research_topic_tool,
)
from enhanced_research_tools import (
    batch_update_research_state_tool,
    initialize_research_project_tool,
    complete_research_milestone_tool,
)

# Enhanced agent instruction
agent_instruction = """
You are an Enhanced Research State Agent that demonstrates two approaches to state management:

SIMPLE TOOLS (for single state updates):
- get_research_status_tool: Check current research status
- set_research_topic_tool: Set research topic  
- add_research_progress_tool: Add progress step
- set_research_priority_tool: Set priority level
- set_research_deadline_tool: Set deadline
- add_research_source_tool: Add research source

ADVANCED TOOLS (using EventActions.state_delta for complex updates):
- batch_update_research_state_tool: Update topic, priority, and deadline together
- initialize_research_project_tool: Set up complete new research project
- complete_research_milestone_tool: Mark milestone complete with findings

WHEN TO USE EACH APPROACH:
- Use simple tools for single field updates (changing just priority, adding one source, etc.)
- Use advanced tools for complex updates (setting up projects, completing milestones, batch changes)

The advanced tools demonstrate "The Standard Way" mentioned in ADK documentation using
EventActions.state_delta for complex state changes with proper event sourcing.

You will receive explicit notifications about external state changes via system messages.
Use get_research_status_tool when users ask about current progress or when you need to 
reference current state values in your responses.

Be encouraging about research progress and suggest appropriate tools based on what the user wants to accomplish.
"""

# Enhanced agent with both simple and complex state management tools
enhanced_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="enhanced_research_state_agent",
    instruction=agent_instruction,
    tools=[
        # Simple state management tools
        get_research_status_tool,
        set_research_topic_tool, 
        add_research_progress_tool,
        set_research_priority_tool,
        set_research_deadline_tool,
        add_research_source_tool,
        # Advanced EventActions.state_delta tools
        batch_update_research_state_tool,
        initialize_research_project_tool,
        complete_research_milestone_tool,
    ],
)