"""
ADK-compliant state management tools for Enhanced Research State Agent.

These tools follow ADK best practices by using proper CallbackContext
for state mutations instead of bypassing the event system.
"""

from typing import Any

from google.adk.tools.tool_context import ToolContext


def set_research_priority_tool(
    priority_level: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set research priority using proper ADK state management.
    
    Args:
        priority_level: High, Medium, or Low priority
    """
    # Validate priority level
    valid_priorities = ["High", "Medium", "Low"]
    if priority_level not in valid_priorities:
        return {
            "status": "error",
            "error": f"Invalid priority. Must be one of: {valid_priorities}"
        }

    # Use proper ADK state management
    tool_context.state["research:priority_level"] = priority_level

    return {
        "status": "success",
        "priority_set": priority_level,
        "message": f"Research priority updated to: {priority_level}"
    }


def set_research_deadline_tool(
    deadline: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set research deadline using proper ADK state management.
    
    Args:
        deadline: Deadline date string
    """
    # Use proper ADK state management
    tool_context.state["research:deadline"] = deadline

    return {
        "status": "success",
        "deadline_set": deadline,
        "message": f"Research deadline updated to: {deadline}"
    }


def add_research_source_tool(
    title: str, url: str, source_type: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Add research source using proper ADK state management.
    
    Args:
        title: Source title
        url: Source URL
        source_type: Type of source (article, paper, book, etc.)
    """
    # Get current sources from state
    current_sources = tool_context.state.get("research:sources_found", [])

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
    tool_context.state["research:sources_found"] = updated_sources

    return {
        "status": "success",
        "source_added": new_source,
        "total_sources": len(updated_sources),
        "message": f"Added source: {title}"
    }


def set_research_topic_tool(
    topic: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Set current research topic using proper ADK state management.
    
    Args:
        topic: New research topic
    """
    # Use proper ADK state management
    tool_context.state["research:current_topic"] = topic

    return {
        "status": "success",
        "topic_set": topic,
        "message": f"Research topic updated to: {topic}"
    }


def add_research_progress_tool(
    step: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Add research progress step using proper ADK state management.
    
    Args:
        step: Progress step description
    """
    # Get current progress from state
    current_progress = tool_context.state.get("research:progress", [])

    # Append new step
    updated_progress = current_progress + [step]

    # Use proper ADK state management
    tool_context.state["research:progress"] = updated_progress

    return {
        "status": "success",
        "step_added": step,
        "total_steps": len(updated_progress),
        "message": f"Added progress step: {step}"
    }


def get_research_status_tool(key:str,
    tool_context: ToolContext
) -> dict[str, Any]:
    """
    Get current research status from session state.
    """
    # Extract research-related state
    status = {
        "current_topic": tool_context.state.get("research:current_topic", "No topic set"),
        "priority_level": tool_context.state.get("research:priority_level", "Not set"),
        "deadline": tool_context.state.get("research:deadline", "No deadline set"),
        "progress_steps": len(tool_context.state.get("research:progress", [])),
        "sources_found": len(tool_context.state.get("research:sources_found", [])),
    }
    
    # Add progress details if available
    progress_list = tool_context.state.get("research:progress", [])
    if progress_list:
        status["recent_progress"] = progress_list[-3:]  # Last 3 items
    
    # Add source details if available
    sources_list = tool_context.state.get("research:sources_found", [])
    if sources_list:
        status["recent_sources"] = [s["title"] for s in sources_list[-3:]]  # Last 3 titles
    
    return {
        "status": "success",
        "research_status": status,
        "message": f"Current research: {status['current_topic']} (Priority: {status['priority_level']})"
    }