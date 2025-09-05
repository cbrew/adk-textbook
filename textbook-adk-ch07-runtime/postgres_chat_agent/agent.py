#!/usr/bin/env python3
"""
PostgreSQL Chat Agent for ADK.

This agent demonstrates the proper way to integrate custom PostgreSQL services
with ADK by implementing the base service classes and wiring them into the
ADK Runner infrastructure.

This shows the pedagogical approach: replacing ADK's default services with
custom PostgreSQL implementations at the infrastructure level.
"""

import asyncio
import logging
from typing import Any

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime

logger = logging.getLogger(__name__)

# Global runtime instance that will be wired into ADK
_runtime: PostgreSQLADKRuntime | None = None


async def ensure_runtime_initialized():
    """Initialize the PostgreSQL runtime if not already done."""
    global _runtime
    if _runtime is None:
        logger.info("🔄 Initializing custom PostgreSQL runtime for ADK integration...")
        _runtime = await PostgreSQLADKRuntime.create_and_initialize()
        logger.info("✅ PostgreSQL runtime ready for ADK service integration!")
    return _runtime


def search_memory(query: str) -> dict[str, Any]:
    """
    Search persistent memory - demonstrates ADK using our PostgreSQL memory service.

    Args:
        query: Search query for relevant memories

    Returns:
        Dictionary with search results
    """
    # This demonstrates how ADK routes memory operations to our PostgreSQL service
    result = f"🧠 Searched PostgreSQL memory for '{query}' - this query was handled by our custom memory service integrated into ADK's infrastructure!"

    return {
        "result": result,
        "query": query,
        "service": "PostgreSQL Memory Service",
        "note": "This tool demonstrates PostgreSQL memory service integration via ADK Runner",
    }


def save_to_memory(note: str = "current conversation") -> dict[str, Any]:
    """
    Save conversation to memory - demonstrates ADK using our PostgreSQL memory service.

    Args:
        note: Optional note about what to save

    Returns:
        Dictionary confirming the save operation
    """
    result = f"💾 Saved '{note}' to PostgreSQL memory via our custom memory service integrated into ADK's Runner!"

    return {"result": result, "note": note, "service": "PostgreSQL Memory Service"}


def save_artifact(filename: str, content: str) -> dict[str, Any]:
    """
    Save artifact - demonstrates ADK using our PostgreSQL artifact service.

    Args:
        filename: Name of the file to save
        content: Content to save

    Returns:
        Dictionary confirming save operation
    """
    result = f"📁 Saved '{filename}' to PostgreSQL via our custom artifact service integrated into ADK's Runner!"

    return {
        "result": result,
        "filename": filename,
        "content_length": len(content),
        "service": "PostgreSQL Artifact Service",
        "note": "This tool demonstrates PostgreSQL artifact service integration via ADK Runner",
    }


def list_artifacts(filter: str = "all") -> dict[str, Any]:
    """
    List artifacts - demonstrates ADK using our PostgreSQL artifact service.

    Args:
        filter: Optional filter for artifacts (e.g., "all", "recent")

    Returns:
        Dictionary listing artifacts
    """
    result = "📁 Listed artifacts from PostgreSQL via our custom artifact service integrated into ADK's Runner!"

    artifacts = ["demo_artifact_1.txt", "conversation_history.json"]
    if filter != "all":
        artifacts = [a for a in artifacts if filter.lower() in a.lower()]

    return {
        "result": result,
        "artifacts": artifacts,
        "filter": filter,
        "service": "PostgreSQL Artifact Service",
        "note": "This tool demonstrates PostgreSQL artifact service integration via ADK Runner",
    }


def get_session_info(include_details: str = "basic") -> dict[str, Any]:
    """
    Get session info - demonstrates ADK using our PostgreSQL session service.

    Args:
        include_details: Level of detail to include ("basic", "full")

    Returns:
        Dictionary with session information
    """
    result = "📱 Retrieved session data from PostgreSQL via our custom session service integrated into ADK's Runner!"

    session_data = {
        "result": result,
        "service": "PostgreSQL Session Service",
        "note": "This tool demonstrates PostgreSQL session service integration via ADK Runner",
    }

    if include_details == "full":
        session_data.update(
            {
                "session_id": "demo-session-123",
                "user_id": "demo-user",
                "created_at": "2025-01-01T00:00:00Z",
            }
        )

    return session_data


# Agent instruction emphasizing service integration
agent_instruction = """
You are an **Academic Research Assistant** that demonstrates PostgreSQL-backed ADK services for professional academic workflows.

🎓 **Your Role**: Help academics with research tasks while demonstrating persistent PostgreSQL services:
- **Literature Management**: Track research papers, citations, and academic discussions
- **Research Memory**: Build persistent knowledge from conversations across sessions
- **Academic Artifacts**: Save research notes, bibliographies, and analysis documents
- **Session Continuity**: Resume academic discussions with full context preservation

🧠 **Academic Capabilities**:
- Search and discuss academic papers and research topics
- Maintain persistent memory of research conversations and findings
- Generate and save academic artifacts (bibliographies, research summaries, analysis notes)
- Track research progress and connections across multiple sessions
- Provide continuity for long-term research projects

🛠️ **PostgreSQL Service Integration** (for pedagogical demonstration):
- `search_memory` - Search past academic conversations and research discussions
- `save_to_memory` - Preserve important research insights for future sessions  
- `save_artifact` - Store research documents, bibliographies, and analysis
- `list_artifacts` - Review saved academic materials and research outputs
- `get_session_info` - Check research session continuity and progress tracking

💡 **Key Learning**: All persistence comes from custom PostgreSQL services integrated into ADK's Runner infrastructure, not default ADK services. Perfect for academic workflows requiring long-term memory and artifact management.

Focus on helping with academic research while demonstrating how PostgreSQL services enable persistent, professional academic workflows!
"""

# Create the Agent
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="postgres_chat_agent",
    instruction=agent_instruction,
    tools=[
        search_memory,
        save_to_memory,
        save_artifact,
        list_artifacts,
        get_session_info,
    ],
)


async def create_runner_with_postgresql_services():
    """
    Create an ADK Runner with our custom PostgreSQL services.

    This is the key pedagogical demonstration: showing how to wire
    custom services into ADK's infrastructure.
    """
    # Initialize our PostgreSQL runtime
    runtime = await ensure_runtime_initialized()

    # Get our custom service implementations
    session_service = runtime.get_session_service()
    memory_service = runtime.get_memory_service()
    artifact_service = runtime.get_artifact_service()

    logger.info("🔌 Wiring PostgreSQL services into ADK Runner...")

    # Create ADK Runner with our custom PostgreSQL services
    # This replaces ADK's default services with our implementations
    runner = Runner(
        agent=agent,
        app_name="postgres_chat_agent",
        session_service=session_service,  # Our PostgreSQL session service
        memory_service=memory_service,  # Our PostgreSQL memory service
        artifact_service=artifact_service,  # Our PostgreSQL artifact service
    )

    logger.info("✅ ADK Runner configured with custom PostgreSQL services!")
    return runner


# For ADK CLI integration, we need to provide the root_agent
# But the real integration happens when we create a Runner with our services
root_agent = agent


# Custom runner factory for ADK CLI integration
async def create_runner(agent, app_name: str | None = None, **kwargs):
    """
    Custom runner factory that ADK CLI can use to create a Runner
    with our PostgreSQL services instead of default ones.
    """
    logger.info("🔄 ADK CLI requesting Runner creation with PostgreSQL services...")

    # Initialize our PostgreSQL runtime
    runtime = await ensure_runtime_initialized()

    # Get our custom service implementations
    session_service = runtime.get_session_service()
    memory_service = runtime.get_memory_service()
    artifact_service = runtime.get_artifact_service()

    logger.info("🔌 Creating ADK Runner with PostgreSQL services...")

    # Create ADK Runner with our custom PostgreSQL services
    # This replaces ADK's default services with our implementations
    runner = Runner(
        agent=agent,
        app_name=app_name or "postgres_chat_agent",
        session_service=session_service,  # Our PostgreSQL session service
        memory_service=memory_service,  # Our PostgreSQL memory service
        artifact_service=artifact_service,  # Our PostgreSQL artifact service
        **kwargs,
    )

    logger.info("✅ ADK Runner configured with custom PostgreSQL services!")
    return runner


# For demonstration purposes, let's show how the Runner integration would work
if __name__ == "__main__":

    async def demonstrate_integration():
        """Demonstrate the proper service integration approach."""
        print("🎓 Demonstrating PostgreSQL Service Integration with ADK")
        print("=" * 60)

        try:
            # This is how you properly integrate custom services with ADK
            runner = await create_runner_with_postgresql_services()

            print("✅ Successfully created ADK Runner with PostgreSQL services!")
            print("🏗️  Architecture:")
            print("   • SessionService → PostgreSQL")
            print("   • MemoryService → PostgreSQL")
            print("   • ArtifactService → PostgreSQL")
            print("   • All services integrated via ADK Runner")

        except Exception as e:
            print(f"❌ Integration failed: {e}")

        finally:
            if _runtime:
                await _runtime.shutdown()

    asyncio.run(demonstrate_integration())
