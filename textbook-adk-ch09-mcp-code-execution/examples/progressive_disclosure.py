#!/usr/bin/env python3
"""Progressive Disclosure Pattern Demo.

This example demonstrates how to conserve context tokens by loading tool
definitions on-demand rather than upfront.

Pattern: Search → Narrow → Load Full Definition → Use

Token Savings: ~90% compared to loading all tools upfront
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_code_agent.tools.code_executor import SafeCodeExecutor
from mcp_code_agent.tools.mcp_demo_data import get_demo_tools


def demo_traditional_approach() -> None:
    """Show the inefficient traditional approach (loads everything)."""
    print("=" * 80)
    print("TRADITIONAL APPROACH: Load all tools upfront")
    print("=" * 80)

    # Count total tokens (approximation)
    total_chars = 0
    all_tools = []
    mock_tools = get_demo_tools()

    for category, tools in mock_tools.items():
        for tool_name, tool_def in tools.items():
            all_tools.append(
                {
                    "category": category,
                    "name": tool_name,
                    "description": tool_def["description"],
                    "parameters": tool_def["parameters"],
                    "server": tool_def["server"],
                }
            )

    full_definition = json.dumps(all_tools, indent=2)
    total_chars = len(full_definition)

    print(f"\nLoaded {len(all_tools)} tools")
    print(f"Total characters: {total_chars}")
    print(f"Estimated tokens: ~{total_chars // 4}\n")
    print("Sample of loaded tools:")
    print(json.dumps(all_tools[:3], indent=2))
    print("\n⚠️  Problem: All tools loaded regardless of task needs!")


def demo_progressive_disclosure() -> None:
    """Show the efficient progressive disclosure approach."""
    print("\n" + "=" * 80)
    print("PROGRESSIVE DISCLOSURE: Load tools on-demand")
    print("=" * 80)

    # Step 1: Search with summary level
    print("\n1️⃣  SEARCH PHASE: Find relevant tools")
    print("   Query: 'file operations'")
    print("   Detail level: summary")

    query = "file operations"
    matches = []
    mock_tools = get_demo_tools()
    for category, tools in mock_tools.items():
        for tool_name, tool_def in tools.items():
            searchable = f"{tool_name} {tool_def['description']} {category}".lower()
            if any(term in searchable for term in query.lower().split()):
                matches.append(
                    {
                        "name": tool_name,
                        "description": tool_def["description"],
                    }
                )

    search_result = json.dumps(matches, indent=2)
    print(f"\n   Found {len(matches)} relevant tools")
    print(f"   Characters: {len(search_result)}")
    print(f"   Estimated tokens: ~{len(search_result) // 4}")
    print(f"\n   Results:\n{search_result}")

    # Step 2: Load full definition only for chosen tool
    print("\n2️⃣  LOAD PHASE: Get full definition of chosen tool")
    print("   Tool: read_file")
    print("   Detail level: full")

    # Find the specific tool
    tool_def = None
    mock_tools2 = get_demo_tools()
    for category, tools in mock_tools2.items():
        if "read_file" in tools:
            tool_def = {
                "name": "read_file",
                "description": tools["read_file"]["description"],
                "parameters": tools["read_file"]["parameters"],
                "server": tools["read_file"]["server"],
                "category": category,
            }
            break

    full_def = json.dumps(tool_def, indent=2)
    print(f"\n   Characters: {len(full_def)}")
    print(f"   Estimated tokens: ~{len(full_def) // 4}")
    print(f"\n   Definition:\n{full_def}")

    # Step 3: Calculate savings
    print("\n3️⃣  TOKEN SAVINGS ANALYSIS")
    search_tokens = len(search_result) // 4
    load_tokens = len(full_def) // 4
    total_progressive = search_tokens + load_tokens

    # Calculate traditional approach tokens for comparison
    all_tools = []
    mock_tools3 = get_demo_tools()
    for category, tools in mock_tools3.items():
        for tool_name, tool_def in tools.items():
            all_tools.append(
                {
                    "category": category,
                    "name": tool_name,
                    "description": tool_def["description"],
                    "parameters": tool_def["parameters"],
                }
            )
    traditional_tokens = len(json.dumps(all_tools)) // 4

    print(f"\n   Traditional approach: ~{traditional_tokens} tokens")
    print(f"   Progressive approach: ~{total_progressive} tokens")
    savings_pct = (
        (traditional_tokens - total_progressive) / traditional_tokens * 100
    )
    print(f"   Savings: ~{savings_pct:.1f}%")


def demo_code_execution_with_discovery() -> None:
    """Show progressive disclosure within code execution."""
    print("\n" + "=" * 80)
    print("CODE EXECUTION: Progressive discovery in action")
    print("=" * 80)

    code = """
import json

# Step 1: Search for relevant tools (summary level only)
print("Searching for file tools...")
file_tools = search_mcp_tools("file operations", detail_level="summary")
print(f"Found {len(json.loads(file_tools)['matches'])} tools")

# Step 2: Load full definition only for the one we need
print("\\nLoading full definition for read_file...")
tool_def = get_tool_definition("read_file", detail_level="full")
print(f"Loaded definition: {json.loads(tool_def)['name']}")

# Step 3: Use the tool
print("\\nReading file...")
result = call_mcp_tool("filesystem", "read_file", {"path": "data.json"})
data = json.loads(result)

# Step 4: Process locally (more efficient than returning raw data)
processed = {
    "success": data["success"],
    "file_size": data["size"],
    "preview": data["content"][:100]
}

print(f"\\nProcessed result: {json.dumps(processed, indent=2)}")
result = processed
"""

    print("\nExecuting code with progressive tool discovery:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    # Provide mock implementations for demonstration
    def mock_search_mcp_tools(query: str, detail_level: str) -> str:
        matches = []
        mock_tools4 = get_demo_tools()
        for category, tools in mock_tools4.items():
            for tool_name, tool_def in tools.items():
                if "file" in query.lower() and "file" in tool_name.lower():
                    if detail_level == "summary":
                        matches.append(
                            {
                                "name": tool_name,
                                "description": tool_def["description"],
                            }
                        )
        return json.dumps({"matches": matches})

    def mock_get_tool_definition(tool_name: str, detail_level: str) -> str:
        mock_tools5 = get_demo_tools()
        for category, tools in mock_tools5.items():
            if tool_name in tools:
                return json.dumps(
                    {
                        "name": tool_name,
                        "description": tools[tool_name]["description"],
                        "parameters": tools[tool_name]["parameters"],
                    }
                )
        return json.dumps({"error": "not found"})

    def mock_call_mcp_tool(
        server: str, tool_name: str, parameters: dict
    ) -> str:  # noqa: ARG001
        return json.dumps(
            {
                "success": True,
                "content": "Mock file content here... " * 10,
                "size": 1234,
            }
        )

    # Execute with mock functions
    result = executor.execute(
        code,
        {
            "search_mcp_tools": mock_search_mcp_tools,
            "get_tool_definition": mock_get_tool_definition,
            "call_mcp_tool": mock_call_mcp_tool,
        },
    )

    print(result["output"])

    if result["success"]:
        print("\n✅ Code executed successfully")
        print(f"\nFinal result: {json.dumps(result['result'], indent=2)}")
    else:
        print(f"\n❌ Error: {result['error']}")


def main() -> None:
    """Run all progressive disclosure demos."""
    print("\n" + "🔍" * 40)
    print("PROGRESSIVE DISCLOSURE PATTERN DEMONSTRATION")
    print("🔍" * 40)

    demo_traditional_approach()
    demo_progressive_disclosure()
    demo_code_execution_with_discovery()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. ✅ Search first with 'summary' detail level
2. ✅ Narrow down to relevant tools
3. ✅ Load 'full' definition only for chosen tools
4. ✅ Combine with code execution for maximum efficiency
5. ✅ Save ~90% of context tokens compared to loading all tools

This pattern is especially valuable when:
- Working with large tool collections (50+ tools)
- Tool needs are task-specific
- Context window is limited
- Multiple tool calls are needed
""")


if __name__ == "__main__":
    main()
