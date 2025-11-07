"""Real MCP client implementation.

This module provides actual MCP protocol integration, replacing the mock
implementations with real connections to MCP servers.
"""

from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Real MCP client for connecting to MCP servers."""

    def __init__(
        self, server_command: str, server_args: list[str] | None = None
    ) -> None:
        """Initialize MCP client.

        Args:
            server_command: Command to start the MCP server (e.g., "node", "python")
            server_args: Arguments to pass to the server command
        """
        self.server_command = server_command
        self.server_args = server_args or []
        self.session: ClientSession | None = None
        self._tools_cache: dict[str, Any] = {}

    async def connect(self) -> None:
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
        )

        # Use stdio_client as async context manager
        self.stdio_context = stdio_client(server_params)
        self.read, self.write = await self.stdio_context.__aenter__()

        # Create session
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()

        # Initialize the session
        await self.session.initialize()

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, "stdio_context"):
            await self.stdio_context.__aexit__(None, None, None)

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools from the MCP server.

        Returns:
            List of tool definitions
        """
        if not self.session:
            msg = "Not connected to MCP server"
            raise RuntimeError(msg)

        response = await self.session.list_tools()
        tools = []

        for tool in response.tools:
            tool_def = {
                "name": tool.name,
                "description": tool.description,
            }

            # Add input schema if available
            if tool.inputSchema:
                tool_def["inputSchema"] = tool.inputSchema

            tools.append(tool_def)
            self._tools_cache[tool.name] = tool_def

        return tools

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> Any:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        if not self.session:
            msg = "Not connected to MCP server"
            raise RuntimeError(msg)

        result = await self.session.call_tool(tool_name, arguments or {})
        return result

    async def search_tools(
        self, query: str, detail_level: str = "summary"
    ) -> list[dict[str, Any]]:
        """Search for tools matching a query.

        Args:
            query: Search query
            detail_level: Level of detail ("summary", "moderate", "full")

        Returns:
            List of matching tools
        """
        # Get all tools if cache is empty
        if not self._tools_cache:
            await self.list_tools()

        # Search through cached tools
        matches = []
        query_lower = query.lower()

        for tool_name, tool_def in self._tools_cache.items():
            searchable = f"{tool_name} {tool_def.get('description', '')}".lower()
            if any(term in searchable for term in query_lower.split()):
                if detail_level == "summary":
                    matches.append(
                        {
                            "name": tool_name,
                            "description": tool_def.get("description", ""),
                        }
                    )
                elif detail_level == "moderate":
                    match_tool = {
                        "name": tool_name,
                        "description": tool_def.get("description", ""),
                    }
                    if "inputSchema" in tool_def:
                        schema = tool_def["inputSchema"]
                        if isinstance(schema, dict) and "properties" in schema:
                            match_tool["parameters"] = list(schema["properties"].keys())
                    matches.append(match_tool)
                else:  # full
                    matches.append(tool_def)

        return matches


class MCPClientManager:
    """Manager for multiple MCP clients."""

    def __init__(self) -> None:
        """Initialize the MCP client manager."""
        self.clients: dict[str, MCPClient] = {}

    async def add_client(
        self, name: str, command: str, args: list[str] | None = None
    ) -> None:
        """Add and connect an MCP client.

        Args:
            name: Name for this client connection
            command: Command to start the MCP server
            args: Arguments for the server command
        """
        client = MCPClient(command, args)
        await client.connect()
        self.clients[name] = client

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> Any:
        """Call a tool on a specific server.

        Args:
            server_name: Name of the server/client
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if server_name not in self.clients:
            msg = f"No client connected for server: {server_name}"
            raise ValueError(msg)

        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def search_tools(
        self, query: str, detail_level: str = "summary", server_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Search for tools across clients.

        Args:
            query: Search query
            detail_level: Level of detail
            server_name: Optional specific server to search

        Returns:
            List of matching tools
        """
        if server_name:
            if server_name not in self.clients:
                msg = f"No client connected for server: {server_name}"
                raise ValueError(msg)
            return await self.clients[server_name].search_tools(query, detail_level)

        # Search across all clients
        all_matches = []
        for name, client in self.clients.items():
            matches = await client.search_tools(query, detail_level)
            for match in matches:
                match["server"] = name
            all_matches.extend(matches)

        return all_matches

    async def disconnect_all(self) -> None:
        """Disconnect all clients."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()


# Global manager instance for the agent to use
_manager: MCPClientManager | None = None


async def get_manager() -> MCPClientManager:
    """Get or create the global MCP client manager."""
    global _manager
    if _manager is None:
        _manager = MCPClientManager()
    return _manager


async def initialize_default_servers() -> MCPClientManager:
    """Initialize default MCP servers for demonstration.

    This sets up commonly used MCP servers like filesystem.

    Returns:
        Configured MCPClientManager
    """
    manager = await get_manager()

    # Try to add filesystem server if available
    # This is typically provided by @modelcontextprotocol/server-filesystem
    try:
        await manager.add_client(
            "filesystem",
            "npx",
            ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
    except Exception as e:
        print(f"Could not connect to filesystem server: {e}")

    return manager
