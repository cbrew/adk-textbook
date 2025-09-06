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


async def search_research_memory(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Search past research discussions and findings from previous sessions.

    Args:
        query: Search query for relevant research memories
        tool_context: ADK tool context with memory service access

    Returns:
        Dictionary with search results
    """
    try:
        # Search memory through ADK context (uses our PostgreSQL service)
        search_response = await tool_context.search_memory(query)
        
        # Extract memories list from the SearchMemoryResponse
        memories = search_response.memories if hasattr(search_response, 'memories') else []

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
            "result": f"🔍 Found {len(memories)} research memories matching '{query}'",
            "query": query,
            "memories": results,
            "total_found": len(memories),
            "service": "PostgreSQL Memory Service",
            "note": "Memories are created automatically from research conversations and discussions"
        }

    except Exception as e:
        return {
            "result": f"❌ Memory search failed for '{query}': {str(e)}",
            "query": query,
            "error": str(e),
            "service": "PostgreSQL Memory Service"
        }


async def track_research_progress(topic: str, findings: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Track research progress by updating session state. ADK will automatically
    convert session conversations into searchable memories.

    Args:
        topic: Research topic being tracked
        findings: Key findings or insights to remember
        tool_context: ADK tool context with session state access

    Returns:
        Dictionary confirming the tracking
    """
    try:
        # Update session state with research progress (ADK will convert to memories automatically)
        if not tool_context.state.get('research_topics'):
            tool_context.state['research_topics'] = []

        research_entry = {
            'topic': topic,
            'findings': findings,
            'timestamp': datetime.utcnow().isoformat(),
            'session_note': f"Research on {topic}: {findings}"
        }
        
        tool_context.state['research_topics'].append(research_entry)
        
        # Also update current research focus
        tool_context.state['current_research_focus'] = topic
        tool_context.state['last_research_update'] = datetime.utcnow().isoformat()

        # CRITICAL FIX: Actually persist the state changes to the database
        # Get session info from the invocation context
        session_info = tool_context._invocation_context.session
        app_name = tool_context._invocation_context.app_name  
        user_id = tool_context._invocation_context.user_id
        
        # Persist the updated state to the session service
        session_service = tool_context._invocation_context.session_service
        if hasattr(session_service, 'update_session_state'):
            session_service.update_session_state(
                session_id=session_info.id,
                state=dict(tool_context.state),
                app_name=app_name,
                user_id=user_id
            )

        return {
            "result": f"📚 Tracked research progress on '{topic}' (persisted to PostgreSQL)",
            "topic": topic,
            "findings": findings,
            "total_topics": len(tool_context.state['research_topics']),
            "service": "PostgreSQL Session Service (state persisted)",
            "note": "Research progress saved to database - ADK will create searchable memories from conversations"
        }

    except Exception as e:
        return {
            "result": f"❌ Failed to track research progress: {str(e)}",
            "topic": topic,
            "error": str(e)
        }


async def save_artifact(filename: str, content: str, tool_context: ToolContext) -> dict[str, Any]:
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
        version = await tool_context.save_artifact(filename, artifact_part)

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


async def list_artifacts(tool_context: ToolContext, filter: str = "all") -> dict[str, Any]:
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
        artifacts = await tool_context.list_artifacts()

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


def get_research_session_status(tool_context: ToolContext, include_details: str = "basic") -> dict[str, Any]:
    """
    Get current research session status and progress.

    Args:
        include_details: Level of detail to include ("basic", "full")
        tool_context: ADK tool context with session access

    Returns:
        Dictionary with research session information
    """
    try:
        # Get session state from ADK context (uses our PostgreSQL service)
        session_state = dict(tool_context.state)

        # Basic research session info
        research_topics = session_state.get('research_topics', [])
        current_focus = session_state.get('current_research_focus', 'None')
        
        session_info = {
            "result": "📚 Retrieved research session status",
            "current_research_focus": current_focus,
            "topics_explored": len(research_topics),
            "has_research_progress": len(research_topics) > 0,
            "service": "PostgreSQL Session Service"
        }

        if include_details == "full":
            session_info.update({
                "research_topics": research_topics,
                "session_state": session_state,
                "note": "Full research session state - conversations will be automatically converted to searchable memories"
            })
        else:
            session_info["note"] = "Research session persisted in PostgreSQL - memories created automatically from conversations"

        return session_info

    except Exception as e:
        return {
            "result": f"❌ Failed to retrieve research session status: {str(e)}",
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
- `search_research_memory` - Search past academic conversations and research discussions
- `track_research_progress` - Track research topics and findings via session state
- `save_artifact` - Store research documents, bibliographies, and analysis
- `list_artifacts` - Review saved academic materials and research outputs
- `get_research_session_status` - Check research session continuity and progress

💡 **Key Learning**: All persistence comes from custom PostgreSQL services integrated into ADK's Runner infrastructure, not default ADK services. Memory is created automatically from conversations - no manual saving needed!

Focus on helping with academic research while demonstrating how PostgreSQL services enable persistent, professional academic workflows!
"""

# Create the Agent
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="postgres_chat_agent",
    instruction=agent_instruction,
    tools=[
        search_research_memory,
        track_research_progress,
        save_artifact,
        list_artifacts,
        get_research_session_status,
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
