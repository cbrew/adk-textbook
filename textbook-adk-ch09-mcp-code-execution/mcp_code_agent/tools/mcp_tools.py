"""MCP integration tools for the agent.

These tools provide the interface for interacting with MCP servers,
demonstrating progressive disclosure and efficient data handling.
"""

import json
from typing import Any, Literal

from google.adk.tools.tool_context import ToolContext

# Mock MCP tool registry for demonstration
# In production, this would query actual MCP servers
MOCK_MCP_TOOLS = {
    "filesystem": {
        "read_file": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {"path": "string"},
            "server": "filesystem",
        },
        "write_file": {
            "name": "write_file",
            "description": "Write contents to a file",
            "parameters": {"path": "string", "content": "string"},
            "server": "filesystem",
        },
        "list_directory": {
            "name": "list_directory",
            "description": "List files in a directory",
            "parameters": {"path": "string"},
            "server": "filesystem",
        },
    },
    "data_processing": {
        "get_records": {
            "name": "get_records",
            "description": "Get records from data store",
            "parameters": {"filter": "object", "limit": "number"},
            "server": "data_processing",
        },
        "aggregate_data": {
            "name": "aggregate_data",
            "description": "Aggregate data by specified fields",
            "parameters": {"data": "array", "group_by": "string"},
            "server": "data_processing",
        },
    },
    "research": {
        "search_papers": {
            "name": "search_papers",
            "description": "Search academic papers",
            "parameters": {"query": "string", "max_results": "number"},
            "server": "research",
        },
        "get_citations": {
            "name": "get_citations",
            "description": "Get citations for a paper",
            "parameters": {"paper_id": "string"},
            "server": "research",
        },
        "analyze_paper": {
            "name": "analyze_paper",
            "description": "Analyze paper content and metadata",
            "parameters": {"paper_id": "string"},
            "server": "research",
        },
    },
}


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
    # Search across all tool categories
    matches = []

    query_lower = query.lower()
    for category, tools in MOCK_MCP_TOOLS.items():
        for tool_name, tool_def in tools.items():
            # Simple keyword matching
            searchable = f"{tool_name} {tool_def['description']} {category}".lower()
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
        {"query": query, "detail_level": detail_level, "matches": matches}, indent=2
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
        JSON string with the tool's response (mocked for demonstration)
    """
    # Mock implementations for demonstration
    if server == "filesystem":
        if tool_name == "read_file":
            path = parameters.get("path", "")
            return json.dumps(
                {
                    "success": True,
                    "content": f"Mock content of {path}",
                    "size": 1234,
                }
            )
        elif tool_name == "list_directory":
            return json.dumps(
                {
                    "success": True,
                    "files": [
                        "paper1.pdf",
                        "paper2.pdf",
                        "data.csv",
                        "analysis.py",
                    ],
                }
            )

    elif server == "data_processing":
        if tool_name == "get_records":
            # Return a large mock dataset to demonstrate filtering
            limit = parameters.get("limit", 1000)
            records = []
            for i in range(limit):
                records.append(
                    {
                        "id": i,
                        "status": "active" if i % 3 == 0 else "inactive",
                        "value": i * 10,
                        "category": f"cat_{i % 5}",
                    }
                )
            return json.dumps({"success": True, "records": records, "total": limit})

        elif tool_name == "aggregate_data":
            data = parameters.get("data", [])
            group_by = parameters.get("group_by", "category")
            # Mock aggregation
            aggregated = {}
            for item in data:
                key = item.get(group_by, "unknown")
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(item)
            return json.dumps({"success": True, "aggregated": aggregated})

    elif server == "research":
        if tool_name == "search_papers":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            papers = []
            for i in range(max_results):
                papers.append(
                    {
                        "id": f"paper_{i}",
                        "title": f"Research Paper on {query} - Part {i}",
                        "authors": ["Author A", "Author B"],
                        "year": 2024,
                        "citations": 100 + i * 10,
                    }
                )
            return json.dumps({"success": True, "papers": papers, "query": query})

        elif tool_name == "get_citations":
            paper_id = parameters.get("paper_id", "")
            citations = []
            for i in range(50):  # Mock 50 citations
                citations.append(
                    {
                        "id": f"cite_{i}",
                        "title": f"Citing Paper {i}",
                        "year": 2020 + (i % 5),
                    }
                )
            return json.dumps(
                {"success": True, "paper_id": paper_id, "citations": citations}
            )

    # Default response for unknown tools
    return json.dumps(
        {
            "success": False,
            "error": f"Tool {tool_name} not found on server {server}",
        }
    )
