"""Progressive tool discovery helpers.

This module demonstrates the progressive disclosure pattern where tool definitions
are loaded on-demand rather than all at once, conserving context tokens.
"""

import json
from typing import Literal

from google.adk.tools.tool_context import ToolContext

from .mcp_tools import MOCK_MCP_TOOLS


def get_tool_definition(
    tool_name: str,
    detail_level: Literal["summary", "full"],
    tool_context: ToolContext,  # noqa: ARG001 - required by ADK
) -> str:
    """Get the definition of a specific tool (progressive disclosure).

    This allows loading the full definition of a tool only when needed,
    after discovering it through search_mcp_tools.

    Args:
        tool_name: Name of the tool to get definition for
        detail_level: "summary" for basic info, "full" for complete definition

    Returns:
        JSON string with the tool definition
    """
    # Search for the tool across all categories
    for category, tools in MOCK_MCP_TOOLS.items():
        if tool_name in tools:
            tool_def = tools[tool_name]

            if detail_level == "summary":
                return json.dumps(
                    {
                        "name": tool_name,
                        "description": tool_def["description"],
                        "category": category,
                    },
                    indent=2,
                )
            else:  # full
                return json.dumps(
                    {
                        "name": tool_name,
                        "description": tool_def["description"],
                        "category": category,
                        "parameters": tool_def["parameters"],
                        "server": tool_def["server"],
                        "examples": _get_tool_examples(tool_name),
                    },
                    indent=2,
                )

    return json.dumps({"error": f"Tool {tool_name} not found"})


def _get_tool_examples(tool_name: str) -> list[dict[str, str]]:
    """Get usage examples for a tool."""
    examples = {
        "read_file": [
            {
                "description": "Read a JSON file",
                "code": 'call_mcp_tool("filesystem", "read_file", '
                '{"path": "data.json"})',
            }
        ],
        "get_records": [
            {
                "description": "Get active records with filtering",
                "code": """records = call_mcp_tool(
    "data_processing", "get_records", {"limit": 1000}
)
filtered = [r for r in records if r["status"] == "active"]""",
            }
        ],
        "search_papers": [
            {
                "description": "Search and filter papers by citation count",
                "code": """papers = call_mcp_tool("research", "search_papers", {
    "query": "machine learning",
    "max_results": 100
})
highly_cited = [p for p in papers if p["citations"] > 500]""",
            }
        ],
    }

    return examples.get(tool_name, [])
