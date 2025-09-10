"""
ADK-compliant state management tools for Research State Agent.

These tools follow ADK best practices by using proper CallbackContext
for state mutations instead of bypassing the event system.
"""

from typing import Any

from google.adk.tools.tool_context import ToolContext


async def set_research_priority_tool(
    priority_level: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set research priority using proper ADK state management.
    
    Args:
        priority_level: High, Medium, or Low priority
        tool_context: ADK tool context with state access
    """
    # Validate priority level
    valid_priorities = ["High", "Medium", "Low"]
    if priority_level not in valid_priorities:
        return {
            "error": f"Invalid priority. Must be one of: {valid_priorities}",
            "success": False
        }

    # Use proper ADK state management
    tool_context.update_state({"research:priority_level": priority_level})

    return {
        "success": True,
        "priority_set": priority_level,
        "message": f"Research priority updated to: {priority_level}"
    }


async def set_research_deadline_tool(
    deadline: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set research deadline using proper ADK state management.
    
    Args:
        deadline: Deadline date string
        tool_context: ADK tool context with state access
    """
    # Use proper ADK state management
    tool_context.update_state({"research:deadline": deadline})

    return {
        "success": True,
        "deadline_set": deadline,
        "message": f"Research deadline updated to: {deadline}"
    }


async def add_research_source_tool(
    title: str, url: str, source_type: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Add research source using proper ADK state management.
    
    Args:
        title: Source title
        url: Source URL
        source_type: Type of source (article, paper, book, etc.)
        tool_context: ADK tool context with state access
    """
    # Get current sources from state
    current_state = tool_context.get_state()
    current_sources = current_state.get("research:sources_found", [])

    # Create new source entry
    new_source = {
        "title": title,
        "url": url,
        "type": source_type,
        "added_at": "2024-01-01"  # In real app, use datetime.utcnow().isoformat()
    }

    # Append to existing sources
    updated_sources = current_sources + [new_source]

    # Use proper ADK state management
    tool_context.update_state({"research:sources_found": updated_sources})

    return {
        "success": True,
        "source_added": new_source,
        "total_sources": len(updated_sources),
        "message": f"Added source: {title}"
    }


async def set_research_topic_tool(
    topic: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set current research topic using proper ADK state management.
    
    Args:
        topic: New research topic
        tool_context: ADK tool context with state access
    """
    # Use proper ADK state management
    tool_context.update_state({"research:current_topic": topic})

    return {
        "success": True,
        "topic_set": topic,
        "message": f"Research topic updated to: {topic}"
    }


async def add_research_progress_tool(
    step: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Add research progress step using proper ADK state management.
    
    Args:
        step: Progress step description
        tool_context: ADK tool context with state access
    """
    # Get current progress from state
    current_state = tool_context.get_state()
    current_progress = current_state.get("research:progress", [])

    # Append new step
    updated_progress = current_progress + [step]

    # Use proper ADK state management
    tool_context.update_state({"research:progress": updated_progress})

    return {
        "success": True,
        "step_added": step,
        "total_steps": len(updated_progress),
        "message": f"Added progress step: {step}"
    }


async def get_research_status_tool(
    tool_context: ToolContext
) -> dict[str, Any]:
    """
    Get current research status from session state.
    
    Args:
        tool_context: ADK tool context with state access
    """
    # Get current state
    current_state = tool_context.state
    
    # Extract research-related state
    status = {
        "current_topic": current_state.get("research:current_topic", "No topic set"),
        "priority_level": current_state.get("research:priority_level", "Not set"),
        "deadline": current_state.get("research:deadline", "No deadline set"),
        "progress_steps": len(current_state.get("research:progress", [])),
        "sources_found": len(current_state.get("research:sources_found", [])),
    }
    
    # Add progress details if available
    progress_list = current_state.get("research:progress", [])
    if progress_list:
        status["recent_progress"] = progress_list[-3:]  # Last 3 items
    
    # Add source details if available
    sources_list = current_state.get("research:sources_found", [])
    if sources_list:
        status["recent_sources"] = [s["title"] for s in sources_list[-3:]]  # Last 3 titles
    
    return {
        "success": True,
        "research_status": status,
        "message": f"Current research: {status['current_topic']} (Priority: {status['priority_level']})"
    }

