"""
Enhanced research tools that demonstrate EventActions.state_delta usage.

These tools show "The Standard Way" for complex state updates using
EventActions.state_delta as mentioned in the ADK documentation.
"""

from typing import Any
from google.adk.tools.tool_context import ToolContext
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.genai import types


async def batch_update_research_state_tool(
    topic: str, priority: str, deadline: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Demonstrates EventActions.state_delta for complex multi-field state updates.
    
    This is "The Standard Way" mentioned in ADK docs for updating multiple state
    keys simultaneously with proper event sourcing.
    
    Args:
        topic: Research topic to set
        priority: Priority level (High, Medium, Low)
        deadline: Research deadline
        tool_context: ADK tool context
    """
    # Validate inputs
    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        return {
            "success": False,
            "error": f"Invalid priority. Must be one of: {valid_priorities}"
        }
    
    # Create complex state delta for multiple updates
    state_delta = {
        "research:current_topic": topic,
        "research:priority_level": priority,
        "research:deadline": deadline,
        "research:last_updated": "2024-01-01T12:00:00Z",  # In real app, use datetime.utcnow().isoformat()
        "research:update_source": "batch_tool"
    }
    
    # Create event with EventActions.state_delta - this is the ADK standard way
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=f"Updated research: {topic} (Priority: {priority}, Deadline: {deadline})")]
        ),
        actions=EventActions(state_delta=state_delta)
    )
    
    # Append the event - this triggers proper state persistence and event sourcing
    await tool_context.invocation_context.append_event(event)
    
    return {
        "success": True,
        "updated_fields": list(state_delta.keys()),
        "topic": topic,
        "priority": priority,
        "deadline": deadline,
        "message": f"Batch updated research state: {topic}"
    }


async def initialize_research_project_tool(
    project_name: str, description: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Initialize a complete research project with multiple state fields.
    
    Demonstrates EventActions.state_delta for setting up complex initial state.
    """
    # Create comprehensive initial state
    state_delta = {
        "research:project_name": project_name,
        "research:description": description,
        "research:current_topic": project_name,  # Start with project as topic
        "research:priority_level": "Medium",  # Default priority
        "research:progress": ["Project initialized"],  # Initial progress step
        "research:sources_found": [],  # Empty sources list
        "research:created_at": "2024-01-01T12:00:00Z",
        "research:status": "active",
        # Use different prefixes to demonstrate scoping
        "temp:setup_complete": True,
        "user:project_count": 1  # This would be user-level state
    }
    
    # Create event with comprehensive state initialization
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=f"Initialized research project: {project_name}")]
        ),
        actions=EventActions(state_delta=state_delta)
    )
    
    await tool_context.invocation_context.append_event(event)
    
    return {
        "success": True,
        "project_initialized": project_name,
        "description": description,
        "initial_state_keys": list(state_delta.keys()),
        "message": f"Research project '{project_name}' initialized successfully"
    }


async def complete_research_milestone_tool(
    milestone_name: str, findings: str, next_steps: list[str], tool_context: ToolContext
) -> dict[str, Any]:
    """
    Complete a research milestone with complex state updates.
    
    Shows EventActions.state_delta updating arrays and complex structures.
    """
    # Get current state to build upon
    current_state = tool_context.state
    current_progress = current_state.get("research:progress", [])
    
    # Create milestone completion record
    milestone_record = {
        "name": milestone_name,
        "findings": findings,
        "completed_at": "2024-01-01T12:00:00Z",
        "next_steps": next_steps
    }
    
    # Build complex state delta
    state_delta = {
        "research:progress": current_progress + [f"Milestone completed: {milestone_name}"],
        "research:last_milestone": milestone_record,
        "research:next_steps": next_steps,
        "research:milestones_completed": current_state.get("research:milestones_completed", 0) + 1,
        # Temp state for this completion event
        "temp:milestone_celebration": f"🎉 Completed {milestone_name}!"
    }
    
    # Create event with milestone completion
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=f"Milestone '{milestone_name}' completed! Findings: {findings}")]
        ),
        actions=EventActions(state_delta=state_delta)
    )
    
    await tool_context.invocation_context.append_event(event)
    
    return {
        "success": True,
        "milestone_completed": milestone_name,
        "findings": findings,
        "next_steps": next_steps,
        "total_milestones": state_delta["research:milestones_completed"],
        "message": f"Milestone '{milestone_name}' completed with {len(next_steps)} next steps"
    }