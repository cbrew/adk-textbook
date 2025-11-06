"""Tests for the code executor."""

from pathlib import Path

import pytest
from mcp_code_agent.tools.code_executor import SafeCodeExecutor


@pytest.fixture
def executor() -> SafeCodeExecutor:
    """Create a code executor instance."""
    return SafeCodeExecutor()


def test_basic_execution(executor: SafeCodeExecutor) -> None:
    """Test basic code execution."""
    code = """
result = 2 + 2
print("Calculation complete")
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert result["result"] == 4
    assert "Calculation complete" in result["output"]
    assert result["error"] is None


def test_code_with_loops(executor: SafeCodeExecutor) -> None:
    """Test code with loops and data processing."""
    code = """
# Process some data
numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers]
result = sum(squared)
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert result["result"] == 55  # 1 + 4 + 9 + 16 + 25


def test_safe_imports(executor: SafeCodeExecutor) -> None:
    """Test that allowed imports work."""
    code = """
import json

data = {"test": "value"}
result = json.dumps(data)
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert result["result"] == '{"test": "value"}'


def test_disallowed_imports(executor: SafeCodeExecutor) -> None:
    """Test that disallowed imports are blocked."""
    code = """
import os
result = os.listdir('.')
"""

    result = executor.execute(code)

    assert result["success"] is False
    assert "Import not allowed: os" in result["error"]


def test_syntax_error(executor: SafeCodeExecutor) -> None:
    """Test handling of syntax errors."""
    code = """
result = 2 +
"""

    result = executor.execute(code)

    assert result["success"] is False
    assert "Syntax error" in result["error"]


def test_runtime_error(executor: SafeCodeExecutor) -> None:
    """Test handling of runtime errors."""
    code = """
result = 1 / 0
"""

    result = executor.execute(code)

    assert result["success"] is False
    assert "ZeroDivisionError" in result["error"]


def test_state_persistence(executor: SafeCodeExecutor, tmp_path: Path) -> None:
    """Test state saving and loading."""
    # Override state directory
    executor.state_dir = tmp_path / "state"
    executor.state_dir.mkdir(parents=True, exist_ok=True)

    # Save state
    code_save = """
save_state("test_key", {"value": 42, "name": "test"})
result = "saved"
"""

    result = executor.execute(code_save)
    assert result["success"] is True

    # Load state
    code_load = """
loaded = load_state("test_key")
result = loaded
"""

    result = executor.execute(code_load)
    assert result["success"] is True
    assert result["result"]["value"] == 42
    assert result["result"]["name"] == "test"


def test_email_tokenization(executor: SafeCodeExecutor) -> None:
    """Test email tokenization for privacy."""
    code = """
email = "user@example.com"
tokenized = tokenize_email(email)
result = tokenized
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert "@example.com" in result["result"]
    assert "***" in result["result"]
    assert "user" not in result["result"] or result["result"].startswith("use")


def test_data_filtering_pattern(executor: SafeCodeExecutor) -> None:
    """Test data filtering pattern."""
    code = """
# Simulate large dataset
data = [{"id": i, "status": "active" if i % 2 == 0 else "inactive"}
        for i in range(100)]

# Filter locally
active = [item for item in data if item["status"] == "active"]

# Return summary
result = {
    "total": len(data),
    "active": len(active),
    "inactive": len(data) - len(active)
}
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert result["result"]["total"] == 100
    assert result["result"]["active"] == 50
    assert result["result"]["inactive"] == 50


def test_progressive_disclosure_pattern(executor: SafeCodeExecutor) -> None:
    """Test progressive disclosure with mock tools."""
    code = """
import json

# Mock tool search
mock_tools = [
    {"name": "read_file", "description": "Read a file"},
    {"name": "write_file", "description": "Write a file"}
]

# Search for relevant tool
relevant = [t for t in mock_tools if "read" in t["name"]]

result = {
    "found": len(relevant),
    "tool_name": relevant[0]["name"] if relevant else None
}
"""

    result = executor.execute(code)

    assert result["success"] is True
    assert result["result"]["found"] == 1
    assert result["result"]["tool_name"] == "read_file"
