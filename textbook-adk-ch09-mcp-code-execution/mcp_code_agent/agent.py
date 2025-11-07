"""Main agent module for MCP Code Execution demonstrations.

This agent demonstrates the code execution patterns from Anthropic's blog post:
https://www.anthropic.com/engineering/code-execution-with-mcp
"""

from google.adk import Agent
from google.adk.tools import Tool

from .config import config
from .prompts import SYSTEM_PROMPT
from .tools import (
    call_mcp_tool,
    execute_python_code,
    get_tool_definition,
    search_mcp_tools,
)


def create_mcp_code_agent() -> Agent:
    """Create an agent with code execution and MCP capabilities.

    Returns:
        Configured Agent instance
    """
    # Define the tools
    tools = [
        Tool(
            name="execute_python_code",
            function=execute_python_code,
            description="""Execute Python code to interact with MCP servers \
and process data.

Use this tool to:
- Implement complex workflows with loops and conditionals
- Filter and transform large datasets locally
- Call multiple MCP tools in a single execution
- Build and save reusable functions (skills)
- Handle sensitive data with privacy preservation

The code has access to these helper functions:
- call_mcp_tool(server, tool_name, params): Call MCP server tools
- search_mcp_tools(query, detail_level): Search for available tools
- save_state(key, data): Save data for later use
- load_state(key): Load saved data
- save_skill(name, code): Save reusable functions
- load_skill(name): Load saved functions
- tokenize_email(email): Tokenize emails for privacy
- tokenize_sensitive(text, pattern): Tokenize sensitive data

Return results by assigning to 'result' variable or using print().""",
        ),
        Tool(
            name="search_mcp_tools",
            function=search_mcp_tools,
            description="""Search for MCP tools by query \
(progressive disclosure pattern).

Use this to discover available tools without loading all definitions upfront.

Arguments:
- query: What you're looking for (e.g., "file operations", "data analysis")
- detail_level: "summary" (names only), "moderate" (with parameters), "full" (complete)

Example: search_mcp_tools("file operations", "summary")""",
        ),
        Tool(
            name="get_tool_definition",
            function=get_tool_definition,
            description="""Get the full definition of a specific tool.

Use this after discovering a tool with search_mcp_tools to load its complete definition.

Arguments:
- tool_name: Name of the tool
- detail_level: "summary" or "full"

Example: get_tool_definition("read_file", "full")""",
        ),
        Tool(
            name="call_mcp_tool",
            function=call_mcp_tool,
            description="""Call an MCP tool directly (for simple operations).

Use execute_python_code for complex workflows. Use this for single, simple tool calls.

Arguments:
- server: Server name ("filesystem", "data_processing", "research")
- tool_name: Name of the tool to call
- parameters: Dictionary of parameters

Example: call_mcp_tool("filesystem", "read_file", {"path": "data.json"})""",
        ),
    ]

    # Create the agent
    agent = Agent(
        name="mcp_code_agent",
        model=config.model_name,
        instructions=SYSTEM_PROMPT,
        tools=tools,
        temperature=config.temperature,
    )

    return agent


# Create the default agent instance
root_agent = create_mcp_code_agent()
