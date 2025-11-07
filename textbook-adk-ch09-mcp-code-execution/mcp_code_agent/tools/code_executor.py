"""Code execution tool for MCP agent.

This tool allows the agent to execute Python code with access to MCP tools,
demonstrating the patterns from Anthropic's blog post on code execution with MCP.
"""

import ast
import json
import re
from io import StringIO
from typing import Any

from google.adk.tools.tool_context import ToolContext

from ..config import config


class SafeCodeExecutor:
    """Sandboxed Python code executor with MCP integration."""

    def __init__(self) -> None:
        """Initialize the code executor."""
        self.allowed_imports = set(config.allowed_imports)
        self.state_dir = config.state_dir
        self.skills_dir = config.skills_dir

    def validate_code(self, code: str) -> tuple[bool, str | None]:
        """Validate code for safety.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        # Check for disallowed imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.allowed_imports:
                        return False, f"Import not allowed: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in self.allowed_imports:
                    return False, f"Import not allowed: {node.module}"

        return True, None

    def execute(
        self, code: str, globals_dict: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute Python code in a controlled environment.

        Args:
            code: Python code to execute
            globals_dict: Optional global namespace to use

        Returns:
            Dictionary with 'success', 'result', 'output', and optional 'error'
        """
        # Validate code first
        is_valid, error_msg = self.validate_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "result": None,
                "output": "",
            }

        # Set up execution environment
        if globals_dict is None:
            globals_dict = {}

        # Add safe builtins and helper functions
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "min": min,
                "max": max,
                "sum": sum,
                "sorted": sorted,
                "any": any,
                "all": all,
            },
            # Helper functions for patterns
            "save_state": self._save_state,
            "load_state": self._load_state,
            "save_skill": self._save_skill,
            "load_skill": self._load_skill,
            "tokenize_email": self._tokenize_email,
            "tokenize_sensitive": self._tokenize_sensitive,
        }
        safe_globals.update(globals_dict)

        # Capture output
        output_buffer = StringIO()
        result = None

        try:
            # Compile and execute
            compiled = compile(code, "<string>", "exec")

            # Execute with output capture
            import sys

            old_stdout = sys.stdout
            sys.stdout = output_buffer

            exec(compiled, safe_globals)

            # If code assigns to 'result', capture it
            if "result" in safe_globals:
                result = safe_globals["result"]

            sys.stdout = old_stdout

            return {
                "success": True,
                "result": result,
                "output": output_buffer.getvalue(),
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"{type(e).__name__}: {e}",
                "result": None,
                "output": output_buffer.getvalue(),
            }

    def _save_state(self, key: str, data: Any) -> None:
        """Save state to file."""
        path = self.state_dir / f"{key}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_state(self, key: str) -> Any:
        """Load state from file."""
        path = self.state_dir / f"{key}.json"
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def _save_skill(self, name: str, code: str) -> None:
        """Save a reusable skill (function) for future use."""
        path = self.skills_dir / f"{name}.py"
        with open(path, "w") as f:
            f.write(code)

    def _load_skill(self, name: str) -> str | None:
        """Load a previously saved skill."""
        path = self.skills_dir / f"{name}.py"
        if not path.exists():
            return None
        with open(path) as f:
            return f.read()

    def _tokenize_email(self, email: str) -> str:
        """Tokenize an email address for privacy."""
        if "@" not in email:
            return email
        local, domain = email.split("@", 1)
        # Keep first 3 chars, hash the rest
        tokenized_local = local[:3] + "***"
        return f"{tokenized_local}@{domain}"

    def _tokenize_sensitive(self, text: str, pattern: str) -> str:
        """Tokenize sensitive data matching a pattern."""
        return re.sub(pattern, "***REDACTED***", text)


# Global executor instance
_executor = SafeCodeExecutor()


def execute_python_code(
    code: str,
    tool_context: ToolContext,  # noqa: ARG001 - required by ADK but not used here
) -> str:
    """Execute Python code with MCP integration.

    This tool enables the code execution patterns described in Anthropic's blog post:
    - Progressive tool discovery
    - Local data filtering
    - Control flow efficiency
    - Privacy preservation
    - State and skills management

    Args:
        code: Python code to execute. The code has access to helper functions:
            - save_state(key, data): Save data to persistent storage
            - load_state(key): Load previously saved data
            - save_skill(name, code): Save reusable function
            - load_skill(name): Load saved function
            - tokenize_email(email): Tokenize email for privacy
            - tokenize_sensitive(text, pattern): Tokenize sensitive data

    Returns:
        JSON string with execution results including success status, output,
        and any returned result.

    Example:
        ```python
        # Progressive disclosure - search for tools
        tools = search_mcp_tools("file operations", detail_level="summary")

        # Data filtering - process locally
        data = call_mcp_tool("data_server", "get_records", {})
        filtered = [r for r in data if r["active"]]
        result = {"total": len(data), "active": len(filtered)}

        # Save for later
        save_state("analysis", result)
        ```
    """
    # Execute the code
    execution_result = _executor.execute(code)

    # Return formatted result
    return json.dumps(execution_result, indent=2)
