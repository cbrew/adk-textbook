"""Configuration for MCP Code Execution Agent."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPCodeConfig:
    """Configuration for MCP code execution agent."""

    # Model configuration
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 8192

    # Code execution settings
    execution_timeout: int = 30  # seconds
    max_code_length: int = 10000  # characters
    allowed_imports: list[str] = None  # None = allow all

    # MCP settings
    mcp_servers: list[str] = None  # List of MCP server URLs
    enable_progressive_disclosure: bool = True
    max_tools_per_request: int = 10

    # Storage settings
    state_dir: Path = Path("./agent_state")
    skills_dir: Path = Path("./agent_skills")
    cache_dir: Path = Path("./agent_cache")

    # Privacy settings
    auto_tokenize_sensitive: bool = True
    sensitive_patterns: list[str] = None  # Regex patterns for sensitive data

    def __post_init__(self) -> None:
        """Initialize default values and create directories."""
        if self.allowed_imports is None:
            self.allowed_imports = [
                "json",
                "csv",
                "re",
                "math",
                "statistics",
                "datetime",
                "pathlib",
                "typing",
            ]

        if self.mcp_servers is None:
            # Default to mock MCP servers for demonstration
            self.mcp_servers = [
                "http://localhost:8000/mcp",  # Mock filesystem server
                "http://localhost:8001/mcp",  # Mock data server
            ]

        if self.sensitive_patterns is None:
            self.sensitive_patterns = [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                r"\b\d{16}\b",  # Credit card
            ]

        # Create directories
        for directory in [self.state_dir, self.skills_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = MCPCodeConfig()
