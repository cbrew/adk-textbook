"""Demo data for MCP tools when real servers aren't available.

This module provides fallback implementations that generate realistic demo data
for demonstration and testing purposes.
"""

from typing import Any


def get_demo_tools() -> dict[str, dict[str, dict[str, Any]]]:
    """Get demo tool registry.

    Returns:
        Dictionary of demo tools organized by category
    """
    return {
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


def get_demo_response(
    server: str, tool_name: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    """Get demo response for a tool call.

    Args:
        server: Server name
        tool_name: Tool name
        parameters: Tool parameters

    Returns:
        Demo response data
    """
    # Filesystem server
    if server == "filesystem":
        if tool_name == "read_file":
            path = parameters.get("path", "")
            return {
                "success": True,
                "content": f"Mock content of {path}\n\nThis is demo data.",
                "size": 1234,
            }
        elif tool_name == "write_file":
            path = parameters.get("path", "")
            return {
                "success": True,
                "path": path,
                "bytes_written": 1234,
            }
        elif tool_name == "list_directory":
            return {
                "success": True,
                "files": [
                    "paper1.pdf",
                    "paper2.pdf",
                    "data.csv",
                    "analysis.py",
                    "results.json",
                ],
            }

    # Data processing server
    elif server == "data_processing":
        if tool_name == "get_records":
            limit = parameters.get("limit", 1000)
            records = []
            for i in range(min(limit, 10000)):  # Cap at 10k for demo
                records.append(
                    {
                        "id": i,
                        "status": "active" if i % 3 == 0 else "inactive",
                        "value": i * 10,
                        "category": f"cat_{i % 5}",
                        "timestamp": f"2024-11-{(i % 30) + 1:02d}",
                    }
                )
            return {"success": True, "records": records, "total": len(records)}

        elif tool_name == "aggregate_data":
            data = parameters.get("data", [])
            group_by = parameters.get("group_by", "category")
            aggregated = {}
            for item in data:
                key = item.get(group_by, "unknown")
                if key not in aggregated:
                    aggregated[key] = {"count": 0, "items": []}
                aggregated[key]["count"] += 1
                aggregated[key]["items"].append(item)
            return {"success": True, "aggregated": aggregated}

    # Research server
    elif server == "research":
        if tool_name == "search_papers":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            papers = []
            for i in range(min(max_results, 100)):  # Cap at 100 for demo
                papers.append(
                    {
                        "id": f"paper_{i}",
                        "title": f"Research on {query}: {_get_demo_title(i)}",
                        "authors": _get_demo_authors(i),
                        "year": 2024 - (i % 5),
                        "citations": 100 + i * 10,
                        "abstract": _get_demo_abstract(query, i),
                    }
                )
            return {"success": True, "papers": papers, "query": query}

        elif tool_name == "get_citations":
            paper_id = parameters.get("paper_id", "")
            citations = []
            for i in range(50):
                citations.append(
                    {
                        "id": f"cite_{i}",
                        "title": f"Citing Paper {i}: {_get_demo_title(i)}",
                        "authors": _get_demo_authors(i),
                        "year": 2020 + (i % 5),
                        "venue": _get_demo_venue(i),
                    }
                )
            return {"success": True, "paper_id": paper_id, "citations": citations}

        elif tool_name == "analyze_paper":
            paper_id = parameters.get("paper_id", "")
            return {
                "success": True,
                "paper_id": paper_id,
                "analysis": {
                    "word_count": 8542,
                    "sections": ["Introduction", "Methods", "Results", "Discussion"],
                    "key_topics": [
                        "machine learning",
                        "neural networks",
                        "optimization",
                    ],
                    "citation_count": 234,
                    "highly_cited": True,
                },
            }

    # Default response for unknown combinations
    return {
        "success": False,
        "error": f"Tool {tool_name} not found on server {server}",
    }


def _get_demo_title(index: int) -> str:
    """Generate a demo paper title."""
    titles = [
        "Advanced Techniques and Methods",
        "A Comprehensive Survey",
        "Novel Approaches to Core Problems",
        "Learning from Large-Scale Data",
        "Optimization and Performance Analysis",
        "Theoretical Foundations",
        "Practical Applications in Real-World Scenarios",
        "Comparative Study of Recent Methods",
        "Deep Dive into Fundamental Concepts",
        "Future Directions and Open Challenges",
    ]
    return titles[index % len(titles)]


def _get_demo_authors(index: int) -> list[str]:
    """Generate demo author names."""
    authors = [
        ["Alice Smith", "Bob Johnson"],
        ["Carol Williams", "David Brown"],
        ["Eve Davis", "Frank Miller"],
        ["Grace Wilson", "Henry Moore"],
        ["Ivy Taylor", "Jack Anderson"],
    ]
    return authors[index % len(authors)]


def _get_demo_abstract(query: str, index: int) -> str:
    """Generate a demo abstract."""
    return (
        f"This paper presents novel research on {query}. "
        f"We propose a new approach that significantly improves upon existing methods. "
        f"Our experiments demonstrate {index % 3 + 1}x performance improvement. "
        "The results have implications for both theory and practice."
    )


def _get_demo_venue(index: int) -> str:
    """Generate a demo venue name."""
    venues = [
        "ICML",
        "NeurIPS",
        "ICLR",
        "AAAI",
        "IJCAI",
        "ACL",
        "EMNLP",
        "CVPR",
        "ICCV",
        "ECCV",
    ]
    return venues[index % len(venues)]
