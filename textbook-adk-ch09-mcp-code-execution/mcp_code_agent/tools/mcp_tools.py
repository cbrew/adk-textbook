"""MCP integration tools for the agent.

These tools provide the interface for interacting with MCP servers,
demonstrating progressive disclosure and efficient data handling.

Supports both real MCP servers and demo mode for when servers aren't available.
"""

import asyncio
import json
import os
from typing import Any, Literal

from google.adk.tools.tool_context import ToolContext

from .mcp_client import get_manager, initialize_default_servers
from .mcp_demo_data import get_demo_response, get_demo_tools

# Check if we should use real MCP servers or demo mode
USE_REAL_MCP = os.getenv("USE_REAL_MCP", "false").lower() in ("true", "1", "yes")

# Track initialization
_mcp_initialized = False


async def _ensure_mcp_initialized() -> None:
    """Ensure MCP servers are initialized."""
    global _mcp_initialized
    if not _mcp_initialized and USE_REAL_MCP:
        try:
            await initialize_default_servers()
            _mcp_initialized = True
            print("✓ Real MCP servers initialized")
        except Exception as e:
            print(f"⚠ Could not initialize MCP servers: {e}")
            print("Falling back to demo mode")


def search_mcp_tools(
    query: str,
    detail_level: Literal["summary", "moderate", "full"],
    tool_context: ToolContext,  # noqa: ARG001 - required by ADK
) -> str:
    """Search for MCP tools matching a query (progressive disclosure).

    This demonstrates the progressive disclosure pattern from the blog post,
    where tools are discovered on-demand rather than loading all definitions upfront.

    Args:
        query: Search query (e.g., "file operations", "data analysis")
        detail_level: How much detail to return:
            - "summary": Just names and brief descriptions
            - "moderate": Include parameters
            - "full": Complete tool definitions

    Returns:
        JSON string with matching tools at the requested detail level
    """
    if USE_REAL_MCP:
        # Use real MCP client
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def _search() -> list[dict[str, Any]]:
            await _ensure_mcp_initialized()
            manager = await get_manager()
            return await manager.search_tools(query, detail_level)

        matches = loop.run_until_complete(_search())
        return json.dumps(
            {"query": query, "detail_level": detail_level, "matches": matches},
            indent=2,
        )
    else:
        # Use demo mode
        all_tools = get_demo_tools()
        matches = []
        query_lower = query.lower()

        for category, tools in all_tools.items():
            for tool_name, tool_def in tools.items():
                searchable = (
                    f"{tool_name} {tool_def['description']} {category}".lower()
                )
                if any(term in searchable for term in query_lower.split()):
                    if detail_level == "summary":
                        matches.append(
                            {
                                "name": tool_name,
                                "description": tool_def["description"],
                                "category": category,
                            }
                        )
                    elif detail_level == "moderate":
                        matches.append(
                            {
                                "name": tool_name,
                                "description": tool_def["description"],
                                "category": category,
                                "parameters": list(tool_def["parameters"].keys()),
                            }
                        )
                    else:  # full
                        matches.append(tool_def)

        return json.dumps(
            {"query": query, "detail_level": detail_level, "matches": matches},
            indent=2,
        )


def call_mcp_tool(
    server: str,
    tool_name: str,
    parameters: dict[str, Any],
    tool_context: ToolContext,  # noqa: ARG001 - required by ADK
) -> str:
    """Call an MCP tool on a specified server.

    This is typically used within code execution blocks to interact with MCP servers,
    allowing local data processing before returning results to the model.

    Args:
        server: MCP server name (e.g., "filesystem", "data_processing")
        tool_name: Name of the tool to call
        parameters: Parameters to pass to the tool

    Returns:
        JSON string with the tool's response
    """
    if USE_REAL_MCP:
        # Use real MCP client
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def _call_tool() -> Any:
            await _ensure_mcp_initialized()
            manager = await get_manager()
            result = await manager.call_tool(server, tool_name, parameters)

            # Format result as JSON
            if hasattr(result, "content"):
                # MCP result object
                return {
                    "success": True,
                    "content": result.content,
                }
            else:
                return {"success": True, "result": result}

        try:
            result = loop.run_until_complete(_call_tool())
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {"success": False, "error": f"MCP call failed: {e}"}, indent=2
            )
    else:
        # Use demo mode
        response = get_demo_response(server, tool_name, parameters)
        return json.dumps(response, indent=2)
