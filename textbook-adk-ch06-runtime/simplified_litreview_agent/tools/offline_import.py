"""
Offline Import Tools - Demonstrates "The Standard Way" Manual Event Creation

These functions show manual event creation using session_service.append_event() 
that bypasses agent execution but still goes through the session. This is the
pattern from ADK documentation for system-level operations like:
- Batch imports from external files
- Background job processing  
- External system integrations
- Scheduled maintenance operations

Key characteristics:
- Uses session_service.append_event() directly
- Creates events with author="system" or author="external_system"  
- Updates state outside of agent/tool execution context
- Demonstrates the real power of persistent state management
"""

import asyncio
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.genai import types


async def import_bibtex_batch(
    bibtex_content: str,
    session_service: DatabaseSessionService | InMemorySessionService,
    app_name: str,
    user_id: str, 
    session_id: str,
    import_tag: str = "bibtex_import"
) -> Dict[str, Any]:
    """
    Import papers from BibTeX content using "The Standard Way" manual events.
    
    This function operates outside of agent execution context, demonstrating
    how external systems can update session state via manual event creation.
    
    Args:
        bibtex_content: Raw BibTeX file content
        session_service: Database or in-memory session service
        app_name: Application name for session identification
        user_id: User ID for session identification  
        session_id: Session ID for session identification
        import_tag: Tag to apply to imported papers
    """
    # Get the session to update
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    if not session:
        return {
            "status": "error",
            "error": f"Session not found: {app_name}/{user_id}/{session_id}"
        }
    
    # Parse BibTeX entries (simplified parser)
    entries = _parse_bibtex_simple(bibtex_content)
    
    if not entries:
        return {
            "status": "error",
            "error": "No valid BibTeX entries found"
        }
    
    # Get current papers from session state
    current_papers = session.state.get("papers", {})
    import_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Convert BibTeX entries to paper records
    imported_papers = {}
    for entry in entries:
        paper_id = f"paper_{str(uuid.uuid4())[:8]}"
        paper = {
            "id": paper_id,
            "title": entry.get("title", "Unknown Title"),
            "authors": entry.get("author", "Unknown Authors"),
            "year": int(entry.get("year", "2024")),
            "venue": entry.get("journal", entry.get("booktitle", "Unknown Venue")),
            "abstract": entry.get("abstract", "No abstract available"),
            "added_date": import_timestamp,
            "status": "unscreened",
            "relevance": None,
            "screening_notes": "",
            "tags": [import_tag, "imported"],
            "import_source": "bibtex",
            "bibtex_key": entry.get("key", ""),
            "doi": entry.get("doi", ""),
            "url": entry.get("url", "")
        }
        imported_papers[paper_id] = paper
    
    # Merge with existing papers
    all_papers = {**current_papers, **imported_papers}
    
    # Calculate updated metrics
    total_imported = len(imported_papers)
    total_papers = len(all_papers)
    
    # Create comprehensive state delta using "The Standard Way"
    state_delta = {
        # Update papers collection
        "papers": all_papers,
        "papers_in_pipeline": total_papers,
        
        # Import operation tracking
        "last_import": {
            "source": "bibtex",
            "count": total_imported,
            "timestamp": import_timestamp,
            "tag": import_tag
        },
        
        # Update pipeline stage based on new content
        "pipeline_stage": "collection" if session.state.get("pipeline_stage") == "initialization" else session.state.get("pipeline_stage", "collection"),
        
        # User-level import tracking
        "user:papers_imported": session.state.get("user:papers_imported", 0) + total_imported,
        "user:import_operations": session.state.get("user:import_operations", 0) + 1,
        "user:last_import_date": import_timestamp,
        
        # App-level metrics
        "app:total_imports": session.state.get("app:total_imports", 0) + 1,
        "app:total_imported_papers": session.state.get("app:total_imported_papers", 0) + total_imported,
        "app:import_sources": list(set(session.state.get("app:import_sources", []) + ["bibtex"])),
        
        # Temporary state for this import operation
        "temp:import_batch_id": str(uuid.uuid4()),
        "temp:import_processing": "completed",
        "temp:import_summary": {
            "format": "bibtex",
            "papers_added": total_imported,
            "duplicate_check": "skipped",  # Would implement duplicate detection in real system
            "processing_time": "< 1s"
        }
    }
    
    # Create manual system event - this is "The Standard Way"
    # Note: author="system" indicates this is a system-level operation
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",  # Key difference: system author, not agent
        content=types.Content(
            role="system",
            parts=[types.Part(text=f"BibTeX import completed: {total_imported} papers imported with tag '{import_tag}'")]
        ),
        actions=EventActions(state_delta=state_delta),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    # Apply changes using session_service.append_event - bypasses agent execution
    await session_service.append_event(session, system_event)
    
    return {
        "status": "success",
        "import_source": "bibtex",
        "papers_imported": total_imported,
        "total_papers": total_papers,
        "import_tag": import_tag,
        "imported_paper_ids": list(imported_papers.keys()),
        "message": f"Successfully imported {total_imported} papers from BibTeX. Total papers: {total_papers}"
    }


async def sync_external_database(
    session_service: DatabaseSessionService | InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    search_query: str,
    max_papers: int = 10
) -> Dict[str, Any]:
    """
    Simulate syncing with external academic database (arXiv, PubMed, etc.)
    
    Demonstrates "The Standard Way" for external system integrations that
    update session state via manual event creation with system-level authorship.
    
    Args:
        session_service: Session service instance
        app_name: Application identifier
        user_id: User identifier
        session_id: Session identifier  
        search_query: Query to search external database
        max_papers: Maximum papers to import
    """
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    if not session:
        return {
            "status": "error",
            "error": f"Session not found: {app_name}/{user_id}/{session_id}"
        }
    
    # Simulate external database API call
    mock_papers = _mock_external_database_search(search_query, max_papers)
    
    current_papers = session.state.get("papers", {})
    sync_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Convert mock results to paper records
    synced_papers = {}
    for mock_paper in mock_papers:
        paper_id = f"paper_{str(uuid.uuid4())[:8]}"
        paper = {
            "id": paper_id,
            "title": mock_paper["title"],
            "authors": mock_paper["authors"],
            "year": mock_paper["year"],
            "venue": mock_paper["venue"],
            "abstract": mock_paper["abstract"],
            "added_date": sync_timestamp,
            "status": "unscreened",
            "relevance": None,
            "screening_notes": "",
            "tags": ["external_sync", "auto_imported"],
            "import_source": mock_paper["database"],
            "external_id": mock_paper["external_id"],
            "url": mock_paper["url"],
            "sync_query": search_query
        }
        synced_papers[paper_id] = paper
    
    # Merge with existing papers
    all_papers = {**current_papers, **synced_papers}
    
    # Create state delta for external sync
    state_delta = {
        "papers": all_papers,
        "papers_in_pipeline": len(all_papers),
        
        # External sync tracking
        "last_external_sync": {
            "database": "mock_arxiv",  # Would be real database name
            "query": search_query,
            "papers_found": len(synced_papers),
            "timestamp": sync_timestamp,
            "sync_id": str(uuid.uuid4())
        },
        
        # Update pipeline stage
        "pipeline_stage": "collection",
        "current_search_query": search_query,  # Update search query from sync
        
        # User-level sync tracking  
        "user:external_syncs": session.state.get("user:external_syncs", 0) + 1,
        "user:auto_imported_papers": session.state.get("user:auto_imported_papers", 0) + len(synced_papers),
        
        # App-level external integration metrics
        "app:external_database_calls": session.state.get("app:external_database_calls", 0) + 1,
        "app:external_papers_synced": session.state.get("app:external_papers_synced", 0) + len(synced_papers),
        "app:last_external_sync": sync_timestamp,
        
        # Temporary sync operation state
        "temp:sync_operation_id": str(uuid.uuid4()),
        "temp:sync_status": "completed",
        "temp:sync_results": {
            "database": "mock_arxiv",
            "query": search_query,
            "results": len(synced_papers),
            "processing_time": "2.3s"
        }
    }
    
    # Create external system event
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="external_system",  # Different author to show external integration
        content=types.Content(
            role="system",
            parts=[types.Part(text=f"External database sync completed: {len(synced_papers)} papers from search '{search_query}'")]
        ),
        actions=EventActions(state_delta=state_delta),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    # Apply via session service - demonstrates external system updating state
    await session_service.append_event(session, event)
    
    return {
        "status": "success",
        "sync_source": "mock_arxiv",
        "search_query": search_query,
        "papers_synced": len(synced_papers),
        "total_papers": len(all_papers),
        "synced_paper_ids": list(synced_papers.keys()),
        "message": f"External sync completed: {len(synced_papers)} new papers from '{search_query}'"
    }


def _parse_bibtex_simple(bibtex_content: str) -> List[Dict[str, str]]:
    """
    Simple BibTeX parser for demonstration purposes.
    
    In a real implementation, you'd use a proper BibTeX parser like `bibtexparser`.
    """
    entries = []
    
    # Split by @article, @inproceedings, etc.
    entry_pattern = r'@\w+\s*\{([^}]+)\}'
    matches = re.finditer(entry_pattern, bibtex_content, re.DOTALL | re.IGNORECASE)
    
    for i, match in enumerate(matches):
        content = match.group(1)
        lines = content.split('\n')
        
        entry = {"key": f"entry_{i}"}
        
        # Extract key-value pairs (simplified)
        for line in lines:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip(',').strip('"').strip('{').strip('}')
                entry[key.lower()] = value
        
        # Ensure required fields have defaults
        if 'title' in entry and entry['title']:
            entries.append(entry)
    
    return entries


def _mock_external_database_search(query: str, max_papers: int) -> List[Dict[str, Any]]:
    """
    Mock external database search results.
    
    In a real implementation, this would call actual APIs like arXiv, PubMed, etc.
    """
    # Generate mock papers based on search query
    mock_papers = []
    
    for i in range(min(max_papers, 5)):  # Generate up to 5 mock papers
        paper = {
            "title": f"Research Paper on {query.title()} - Study {i+1}",
            "authors": f"Smith, J. & Jones, A. & Wilson, {chr(66+i)}.",
            "year": 2023 + (i % 2),
            "venue": f"Journal of {query.split()[0].title()} Research" if query else "Academic Journal",
            "abstract": f"This paper investigates {query} using novel methodologies. Our findings contribute to understanding of {query} in academic contexts. Key contributions include theoretical framework and empirical validation.",
            "database": "mock_arxiv",
            "external_id": f"arxiv:2024.{i+1:04d}",
            "url": f"https://arxiv.org/abs/2024.{i+1:04d}",
        }
        mock_papers.append(paper)
    
    return mock_papers


# Convenience function for testing the offline import functionality
async def demo_offline_import(db_url: Optional[str] = None) -> None:
    """
    Demonstration of offline import functionality.
    
    Shows how external systems can update literature review sessions
    using "The Standard Way" manual event creation.
    """
    print("🔄 Offline Import Demo - The Standard Way")
    print("=" * 50)
    
    # Use in-memory session service for demo, or database if provided
    if db_url:
        session_service = DatabaseSessionService(db_url=db_url)
        print(f"📀 Using database: {db_url}")
    else:
        session_service = InMemorySessionService()
        print("💾 Using in-memory session service")
    
    app_name = "litreview_offline_demo"
    user_id = "researcher_001"
    session_id = str(uuid.uuid4())
    
    # Create session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id, 
        session_id=session_id,
        state={"pipeline_stage": "initialization", "papers": {}}
    )
    
    print(f"📋 Created session: {session_id}")
    print(f"   Initial state: {len(session.state.get('papers', {}))} papers")
    
    # Demo 1: BibTeX import
    sample_bibtex = '''
    @article{smith2023ai,
        title={Artificial Intelligence in Academic Research},
        author={Smith, John and Jones, Alice},
        journal={Journal of AI Research},
        year={2023},
        abstract={This paper explores the applications of AI in academic research workflows.}
    }
    
    @inproceedings{wilson2024litreview,
        title={Automated Literature Review Systems},
        author={Wilson, Bob},
        booktitle={Conference on Academic Tools},
        year={2024},
        abstract={We present a novel approach to automating literature review processes.}
    }
    '''
    
    print("\n📚 Demo 1: BibTeX Import")
    result1 = await import_bibtex_batch(
        bibtex_content=sample_bibtex,
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        import_tag="demo_import"
    )
    print(f"   ✅ {result1['message']}")
    
    # Demo 2: External database sync
    print("\n🌐 Demo 2: External Database Sync")
    result2 = await sync_external_database(
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        search_query="machine learning education",
        max_papers=3
    )
    print(f"   ✅ {result2['message']}")
    
    # Show final state
    final_session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    total_papers = len(final_session.state.get("papers", {}))
    
    print(f"\n📊 Final State: {total_papers} papers in pipeline")
    print("   Import sources:", final_session.state.get("app:import_sources", []))
    print("   Pipeline stage:", final_session.state.get("pipeline_stage"))
    
    print("\n✅ Offline import demo completed!")
    print("   Demonstrated 'The Standard Way' for external system integration")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_offline_import())