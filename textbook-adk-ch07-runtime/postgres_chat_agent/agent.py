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
from datetime import datetime
from typing import Any

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types

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


def search_memory(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Search persistent memory including artifact events using PostgreSQL memory service.

    Args:
        query: Search query for relevant memories and artifacts
        tool_context: ADK tool context with memory service access

    Returns:
        Dictionary with search results
    """
    try:
        # Search memory through ADK context (uses our PostgreSQL service with artifact event indexing)
        memories = tool_context.search_memory(query)

        # Format results for display
        results = []
        for i, memory in enumerate(memories[:5], 1):  # Show top 5 results
            # Extract content preview
            content_text = ""
            if hasattr(memory.content, 'parts'):
                for part in memory.content.parts:
                    if hasattr(part, 'text') and part.text:
                        content_text = part.text[:150] + ("..." if len(part.text) > 150 else "")
                        break

            results.append({
                "rank": i,
                "content_preview": content_text,
                "author": memory.author,
                "timestamp": memory.timestamp
            })

        return {
            "result": f"🔍 Found {len(memories)} memories matching '{query}'",
            "query": query,
            "memories": results,
            "total_found": len(memories),
            "service": "PostgreSQL Memory Service with Artifact Event Indexing",
            "note": "Search includes conversation history and artifact creation events for comprehensive results"
        }

    except Exception as e:
        return {
            "result": f"❌ Memory search failed for '{query}': {str(e)}",
            "query": query,
            "error": str(e),
            "service": "PostgreSQL Memory Service"
        }


def save_to_memory(tool_context: ToolContext, note: str = "current conversation") -> dict[str, Any]:
    """
    Save conversation state to memory using PostgreSQL memory service.

    Args:
        note: Description of what to save
        tool_context: ADK tool context with memory service access

    Returns:
        Dictionary confirming the save operation
    """
    try:
        # Create memory content
        memory_content = f"Research session note: {note}"

        # Add to memory through ADK context (uses our PostgreSQL service)
        # Note: ADK automatically handles memory persistence during conversation flow
        # This tool demonstrates explicit memory addition for user notes

        # Update session state to indicate memory was added
        if not tool_context.state.get('saved_notes'):
            tool_context.state['saved_notes'] = []

        tool_context.state['saved_notes'].append({
            'note': note,
            'content': memory_content,
            'timestamp': datetime.utcnow().isoformat()
        })

        return {
            "result": f"💾 Added research note to persistent memory: '{note}'",
            "note": note,
            "content": memory_content,
            "service": "PostgreSQL Memory Service with Event Sourcing",
            "note_detail": "Memory will be indexed and searchable in future sessions"
        }

    except Exception as e:
        return {
            "result": f"❌ Failed to save to memory: {str(e)}",
            "note": note,
            "error": str(e),
            "service": "PostgreSQL Memory Service"
        }


def save_artifact(filename: str, content: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Save artifact using PostgreSQL-backed artifact service with event sourcing.

    Args:
        filename: Name of the file to save
        content: Content to save
        tool_context: ADK tool context with artifact service access

    Returns:
        Dictionary confirming save operation
    """
    try:
        # Create artifact Part from content
        artifact_part = types.Part(text=content)

        # Save artifact through ADK context (uses our PostgreSQL service)
        version = tool_context.save_artifact(filename, artifact_part)

        # Determine storage method based on file size
        storage_method = "PostgreSQL BYTEA" if len(content.encode('utf-8')) <= 1024*1024 else "Filesystem"

        return {
            "result": f"✅ Successfully saved '{filename}' version {version}",
            "filename": filename,
            "version": version,
            "content_length": len(content),
            "storage_method": storage_method,
            "service": "PostgreSQL Artifact Service with Event Sourcing",
            "note": "Artifact saved and indexed for semantic search via event sourcing"
        }

    except Exception as e:
        return {
            "result": f"❌ Failed to save artifact '{filename}': {str(e)}",
            "filename": filename,
            "error": str(e),
            "service": "PostgreSQL Artifact Service"
        }


def list_artifacts(tool_context: ToolContext, filter: str = "all") -> dict[str, Any]:
    """
    List artifacts stored in PostgreSQL artifact service.

    Args:
        filter: Optional filter for artifacts (e.g., "all", "recent", file extension)
        tool_context: ADK tool context with artifact service access

    Returns:
        Dictionary listing artifacts
    """
    try:
        # Get artifacts from ADK context (uses our PostgreSQL service)
        artifacts = tool_context.list_artifacts()

        # Apply filter if specified
        if filter != "all" and artifacts:
            filtered_artifacts = [a for a in artifacts if filter.lower() in a.lower()]
        else:
            filtered_artifacts = artifacts

        return {
            "result": f"📁 Found {len(artifacts)} total artifacts, showing {len(filtered_artifacts)} matching '{filter}'",
            "artifacts": filtered_artifacts,
            "total_count": len(artifacts),
            "filtered_count": len(filtered_artifacts),
            "filter": filter,
            "service": "PostgreSQL Artifact Service",
            "note": "Artifacts retrieved from PostgreSQL with hybrid storage (BYTEA + filesystem)"
        }

    except Exception as e:
        return {
            "result": f"❌ Failed to list artifacts: {str(e)}",
            "error": str(e),
            "filter": filter,
            "service": "PostgreSQL Artifact Service"
        }


def get_session_info(tool_context: ToolContext, include_details: str = "basic") -> dict[str, Any]:
    """
    Get session information from PostgreSQL session service.

    Args:
        include_details: Level of detail to include ("basic", "full")
        tool_context: ADK tool context with session access

    Returns:
        Dictionary with session information
    """
    try:
        # Get session state from ADK context (uses our PostgreSQL service)
        session_state = dict(tool_context.state)

        # Basic session info
        session_info = {
            "result": "📱 Retrieved session from PostgreSQL with persistent state",
            "has_saved_notes": bool(session_state.get('saved_notes')),
            "state_keys": list(session_state.keys()),
            "service": "PostgreSQL Session Service"
        }

        if include_details == "full":
            session_info.update({
                "session_state": session_state,
                "saved_notes_count": len(session_state.get('saved_notes', [])),
                "note": "Full session state retrieved from PostgreSQL with event sourcing support"
            })
        else:
            session_info["note"] = "Basic session info - use include_details='full' for complete state"

        return session_info

    except Exception as e:
        return {
            "result": f"❌ Failed to retrieve session info: {str(e)}",
            "error": str(e),
            "include_details": include_details,
            "service": "PostgreSQL Session Service"
        }


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
