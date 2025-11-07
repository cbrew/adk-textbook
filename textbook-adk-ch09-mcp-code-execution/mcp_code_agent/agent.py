"""Main agent module for MCP Code Execution demonstrations.

This agent demonstrates the code execution patterns from Anthropic's blog post:
https://www.anthropic.com/engineering/code-execution-with-mcp
"""

from google.adk import Agent
from google.adk.tools import FunctionTool

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
    # Define the tools using FunctionTool wrapper
    # ADK automatically extracts tool names and descriptions from the functions
    tools = [
        FunctionTool(execute_python_code),
        FunctionTool(search_mcp_tools),
        FunctionTool(get_tool_definition),
        FunctionTool(call_mcp_tool),
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
