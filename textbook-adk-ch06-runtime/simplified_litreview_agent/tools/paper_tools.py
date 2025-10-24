"""
Paper Management Tools - Demonstrates Direct State Access Pattern

These tools use tool_context.state[key] = value for simple, single-field
state updates. This is the recommended ADK pattern for tool-based state
management as it automatically captures changes in the event's state_delta.
"""

from typing import Any, Dict, List
from google.adk.tools.tool_context import ToolContext
import uuid
from datetime import datetime, timezone


def add_paper_tool(
    title: str, 
    authors: str, 
    year: str, 
    venue: str,
    abstract: str,
    tool_context: ToolContext  # noqa: F401
) -> Dict[str, Any]:
    """
    Add a single paper to the literature review pipeline.
    
    Demonstrates direct state access - the simplest ADK state pattern.
    Changes are automatically captured in the event's state_delta.
    
    Args:
        title: Paper title
        authors: Comma-separated author names
        year: Publication year
        venue: Journal/conference name  
        abstract: Paper abstract
    """
    # Create paper record
    paper_id = f"paper_{str(uuid.uuid4())[:8]}"
    paper = {
        "id": paper_id,
        "title": title,
        "authors": authors,
        "year": int(year) if year.isdigit() else 2024,
        "venue": venue,
        "abstract": abstract,
        "added_date": datetime.now(timezone.utc).isoformat(),
        "status": "unscreened",
        "relevance": None,
        "screening_notes": "",
        "tags": []
    }
    
    # Get current papers from state
    current_papers = tool_context.state.get("papers", {})
    
    # Add new paper - direct state access (recommended pattern)
    current_papers[paper_id] = paper
    tool_context.state["papers"] = current_papers
    
    # Update pipeline metrics - each update captured automatically  
    tool_context.state["papers_in_pipeline"] = len(current_papers)
    tool_context.state["last_paper_added"] = paper_id
    tool_context.state["pipeline_stage"] = "collection"
    
    # Update user-level metrics
    user_total = tool_context.state.get("user:papers_added", 0)
    tool_context.state["user:papers_added"] = user_total + 1
    
    return {
        "status": "success",
        "paper_id": paper_id,
        "paper_title": title,
        "total_papers": len(current_papers),
        "message": f"Added paper '{title}' to pipeline. Total papers: {len(current_papers)}"
    }


def search_papers_tool(
    query: str,
    filter_by: str = "title",
    tool_context: ToolContext = None # noqa: F401
) -> Dict[str, Any]:
    """
    Search through papers in the pipeline by various criteria.
    
    Args:
        query: Search term
        filter_by: Field to search in (title, authors, venue, abstract, tags)
    """
    papers = tool_context.state.get("papers", {})
    
    if not papers:
        return {
            "status": "success", 
            "matching_papers": [],
            "total_matches": 0,
            "message": "No papers in pipeline yet. Add some papers first!"
        }
    
    # Simple text search in specified field
    matches = []
    query_lower = query.lower()
    
    for paper_id, paper in papers.items():
        search_text = ""
        if filter_by == "title":
            search_text = paper.get("title", "")
        elif filter_by == "authors":
            search_text = paper.get("authors", "")
        elif filter_by == "venue":
            search_text = paper.get("venue", "")
        elif filter_by == "abstract":
            search_text = paper.get("abstract", "")
        elif filter_by == "tags":
            search_text = " ".join(paper.get("tags", []))
        
        if query_lower in search_text.lower():
            matches.append({
                "id": paper_id,
                "title": paper["title"],
                "authors": paper["authors"],
                "year": paper["year"],
                "status": paper["status"]
            })
    
    # Update search history in state
    search_history = tool_context.state.get("search_history", [])
    search_entry = {
        "query": query,
        "filter": filter_by,
        "results": len(matches),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    search_history.append(search_entry)
    tool_context.state["search_history"] = search_history[-10:]  # Keep last 10 searches
    
    return {
        "status": "success",
        "matching_papers": matches,
        "total_matches": len(matches),
        "searched_field": filter_by,
        "message": f"Found {len(matches)} papers matching '{query}' in {filter_by}"
    }


def get_pipeline_status_tool(
    tool_context: ToolContext  # noqa: F401
) -> Dict[str, Any]:
    """
    Get comprehensive status of the literature review pipeline.
    
    Shows current progress and suggests next actions based on state.
    """
    papers = tool_context.state.get("papers", {})
    pipeline_stage = tool_context.state.get("pipeline_stage", "initialization")
    search_query = tool_context.state.get("current_search_query", "Not set")
    
    # Calculate status metrics
    total_papers = len(papers)
    screened_papers = sum(1 for p in papers.values() if p["status"] != "unscreened")
    relevant_papers = sum(1 for p in papers.values() if p.get("relevance") == "relevant")
    
    # Determine next suggested actions
    suggestions = []
    if total_papers == 0:
        suggestions.append("Add papers manually or import from BibTeX")
    elif screened_papers == 0:
        suggestions.append("Start screening papers for relevance") 
    elif screened_papers < total_papers:
        suggestions.append(f"Continue screening ({total_papers - screened_papers} papers remaining)")
    elif relevant_papers > 0:
        suggestions.append("Use analysis agents to extract themes and insights")
    
    # Update state with current status
    status_summary = {
        "stage": pipeline_stage,
        "total_papers": total_papers,
        "screened": screened_papers,
        "relevant": relevant_papers,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    tool_context.state["pipeline_status"] = status_summary
    
    return {
        "status": "success",
        "current_stage": pipeline_stage,
        "search_query": search_query,
        "total_papers": total_papers,
        "screened_papers": screened_papers,
        "relevant_papers": relevant_papers,
        "completion_percentage": (screened_papers / max(total_papers, 1)) * 100,
        "suggested_actions": suggestions,
        "message": f"Pipeline Status: {total_papers} papers, {screened_papers} screened, {relevant_papers} relevant"
    }


def set_research_query_tool(
    query: str,
    research_focus: str,
    tool_context: ToolContext  # noqa: F401  
) -> Dict[str, Any]:
    """
    Set or update the current research query and focus area.
    
    Args:
        query: Main research question or search terms
        research_focus: Broader research area or discipline
    """
    # Update session-level state  
    tool_context.state["current_search_query"] = query
    tool_context.state["research_focus"] = research_focus
    tool_context.state["query_set_date"] = datetime.now(timezone.utc).isoformat()
    
    # Update pipeline stage if this is the first query
    if not tool_context.state.get("pipeline_stage"):
        tool_context.state["pipeline_stage"] = "collection"
    
    # Update user preferences
    user_interests = tool_context.state.get("user:research_interests", [])
    if research_focus not in user_interests:
        user_interests.append(research_focus)
        tool_context.state["user:research_interests"] = user_interests
    
    return {
        "status": "success", 
        "query_set": query,
        "research_focus": research_focus,
        "pipeline_stage": tool_context.state["pipeline_stage"],
        "message": f"Research query set: '{query}' in area '{research_focus}'"
    }