"""
Screening Tools - Demonstrates Manual Event Creation Pattern

These tools show how to create manual events with EventActions.state_delta
for complex, multi-field state updates. This is "The Standard Way" mentioned
in ADK documentation for operations that need atomic, complex state changes.
"""

from typing import Any, Dict, List
from google.adk.tools.tool_context import ToolContext
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.genai import types
import uuid
from datetime import datetime, timezone


async def screen_paper_tool(
    paper_id: str,
    relevance: str,
    reasoning: str,
    confidence: str,
    tool_context: ToolContext  # noqa: F401
) -> Dict[str, Any]:
    """
    Screen a single paper for relevance using manual event creation.
    
    Demonstrates EventActions.state_delta for complex state updates that
    need to happen atomically across multiple state fields.
    
    Args:
        paper_id: ID of paper to screen
        relevance: "relevant", "irrelevant", or "maybe"
        reasoning: Explanation for decision
        confidence: "high", "medium", "low"
    """
    papers = tool_context.state.get("papers", {})
    
    if paper_id not in papers:
        return {
            "status": "error",
            "error": f"Paper {paper_id} not found in pipeline"
        }
    
    paper = papers[paper_id]
    
    # Validate relevance input
    valid_relevance = ["relevant", "irrelevant", "maybe"]
    if relevance not in valid_relevance:
        return {
            "status": "error",
            "error": f"Invalid relevance. Must be one of: {valid_relevance}"
        }
    
    # Create screening record
    screening_record = {
        "decision": relevance,
        "reasoning": reasoning,
        "confidence": confidence,
        "screened_by": "user",  # In real app, would be actual user ID
        "screening_date": datetime.now(timezone.utc).isoformat()
    }
    
    # Update paper record
    paper["status"] = "screened"
    paper["relevance"] = relevance
    paper["screening_notes"] = reasoning
    paper["screening_record"] = screening_record
    
    # Calculate updated metrics
    screened_count = sum(1 for p in papers.values() if p["status"] == "screened")
    relevant_count = sum(1 for p in papers.values() if p.get("relevance") == "relevant")
    
    # Create complex state delta for atomic update
    state_delta = {
        # Update the papers collection
        "papers": papers,
        
        # Update pipeline metrics
        "papers_screened": screened_count,
        "papers_relevant": relevant_count,
        "last_screening_decision": relevance,
        "last_screened_paper": paper_id,
        
        # Update pipeline stage if appropriate
        "pipeline_stage": "analysis" if screened_count == len(papers) and relevant_count > 0 else "screening",
        
        # User-level screening stats
        "user:papers_screened": tool_context.state.get("user:papers_screened", 0) + 1,
        "user:last_screening_date": datetime.now(timezone.utc).isoformat(),
        
        # App-level metrics
        "app:total_screenings": tool_context.state.get("app:total_screenings", 0) + 1,
        
        # Temporary state for this screening operation
        "temp:last_screening_operation": {
            "paper_id": paper_id,
            "decision": relevance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    # Create manual event with EventActions.state_delta
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",  # This is coming from agent tool, so "agent" author
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=f"Screened paper '{paper['title']}' as {relevance}: {reasoning}")]
        ),
        actions=EventActions(state_delta=state_delta),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    # Apply the complex state update atomically
    await tool_context.invocation_context.append_event(event)
    
    return {
        "status": "success",
        "paper_id": paper_id,
        "paper_title": paper["title"],
        "screening_decision": relevance,
        "reasoning": reasoning,
        "confidence": confidence,
        "total_screened": screened_count,
        "total_relevant": relevant_count,
        "pipeline_progress": f"{screened_count}/{len(papers)} papers screened",
        "message": f"Screened '{paper['title']}' as {relevance}. Progress: {screened_count}/{len(papers)}"
    }


async def batch_screen_papers_tool(
    screening_decisions: List[Dict[str, str]],
    tool_context: ToolContext  # noqa: F401
) -> Dict[str, Any]:
    """
    Screen multiple papers in a single atomic operation.
    
    Demonstrates the power of EventActions.state_delta for complex batch operations
    that need to maintain consistency across multiple related state changes.
    
    Args:
        screening_decisions: List of dicts with keys: paper_id, relevance, reasoning, confidence
    """
    papers = tool_context.state.get("papers", {})
    
    if not screening_decisions:
        return {
            "status": "error",
            "error": "No screening decisions provided"
        }
    
    # Validate all decisions first
    valid_relevance = ["relevant", "irrelevant", "maybe"]
    processed_decisions = []
    
    for decision in screening_decisions:
        paper_id = decision.get("paper_id")
        relevance = decision.get("relevance")
        reasoning = decision.get("reasoning", "")
        confidence = decision.get("confidence", "medium")
        
        if not paper_id or paper_id not in papers:
            return {
                "status": "error",
                "error": f"Invalid or missing paper_id: {paper_id}"
            }
        
        if relevance not in valid_relevance:
            return {
                "status": "error",
                "error": f"Invalid relevance '{relevance}' for paper {paper_id}"
            }
        
        processed_decisions.append({
            "paper_id": paper_id,
            "relevance": relevance, 
            "reasoning": reasoning,
            "confidence": confidence
        })
    
    # Apply all screening decisions
    batch_timestamp = datetime.now(timezone.utc).isoformat()
    
    for decision in processed_decisions:
        paper_id = decision["paper_id"]
        paper = papers[paper_id]
        
        # Update paper with screening decision
        paper["status"] = "screened"
        paper["relevance"] = decision["relevance"]
        paper["screening_notes"] = decision["reasoning"]
        paper["screening_record"] = {
            "decision": decision["relevance"],
            "reasoning": decision["reasoning"],
            "confidence": decision["confidence"],
            "screened_by": "user",
            "screening_date": batch_timestamp,
            "batch_operation": True
        }
    
    # Calculate comprehensive metrics
    total_papers = len(papers)
    screened_count = sum(1 for p in papers.values() if p["status"] == "screened")
    relevant_count = sum(1 for p in papers.values() if p.get("relevance") == "relevant")
    maybe_count = sum(1 for p in papers.values() if p.get("relevance") == "maybe")
    
    # Determine new pipeline stage
    new_stage = "screening"
    if screened_count == total_papers:
        if relevant_count > 0:
            new_stage = "analysis"
        else:
            new_stage = "collection"  # Need more papers
    
    # Create comprehensive state delta for batch operation
    state_delta = {
        # Update papers collection
        "papers": papers,
        
        # Update pipeline metrics
        "papers_screened": screened_count,
        "papers_relevant": relevant_count,
        "papers_maybe": maybe_count,
        "pipeline_stage": new_stage,
        "last_batch_screening": {
            "count": len(processed_decisions),
            "timestamp": batch_timestamp,
            "results": {
                "relevant": sum(1 for d in processed_decisions if d["relevance"] == "relevant"),
                "irrelevant": sum(1 for d in processed_decisions if d["relevance"] == "irrelevant"),
                "maybe": sum(1 for d in processed_decisions if d["relevance"] == "maybe")
            }
        },
        
        # User-level stats  
        "user:papers_screened": tool_context.state.get("user:papers_screened", 0) + len(processed_decisions),
        "user:batch_operations": tool_context.state.get("user:batch_operations", 0) + 1,
        "user:last_activity": batch_timestamp,
        
        # App-level metrics
        "app:total_screenings": tool_context.state.get("app:total_screenings", 0) + len(processed_decisions),
        "app:batch_screening_operations": tool_context.state.get("app:batch_screening_operations", 0) + 1,
        
        # Temporary state for this batch
        "temp:batch_screening_id": str(uuid.uuid4()),
        "temp:batch_size": len(processed_decisions),
        "temp:batch_completion": "screening_complete" if screened_count == total_papers else "screening_partial"
    }
    
    # Create manual event for batch operation
    summary_text = f"Batch screened {len(processed_decisions)} papers. "
    summary_text += f"Results: {state_delta['last_batch_screening']['results']}"
    
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=summary_text)]
        ),
        actions=EventActions(state_delta=state_delta),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    # Apply batch update atomically
    await tool_context.invocation_context.append_event(event)
    
    return {
        "status": "success",
        "papers_processed": len(processed_decisions),
        "screening_results": state_delta['last_batch_screening']['results'],
        "total_screened": screened_count,
        "total_papers": total_papers,
        "pipeline_stage": new_stage,
        "completion_percentage": (screened_count / total_papers) * 100,
        "message": f"Batch screened {len(processed_decisions)} papers. Pipeline now at {new_stage} stage."
    }


async def update_screening_criteria_tool(
    criteria_name: str,
    criteria_description: str,
    importance: str,
    tool_context: ToolContext  # noqa: F401
) -> Dict[str, Any]:
    """
    Update screening criteria used for paper evaluation.
    
    Demonstrates manual events for updating shared configuration that
    affects future screening decisions.
    
    Args:
        criteria_name: Name of the screening criteria
        criteria_description: Detailed description
        importance: "high", "medium", "low"
    """
    current_criteria = tool_context.state.get("screening_criteria", {})
    
    # Add or update criteria
    current_criteria[criteria_name] = {
        "description": criteria_description,
        "importance": importance,
        "created_date": datetime.now(timezone.utc).isoformat(),
        "created_by": "user"
    }
    
    # Create state delta for criteria update
    state_delta = {
        "screening_criteria": current_criteria,
        "criteria_last_updated": datetime.now(timezone.utc).isoformat(),
        "criteria_count": len(current_criteria),
        
        # User preferences
        "user:custom_criteria_count": len([c for c in current_criteria.values() if c["created_by"] == "user"]),
        
        # App-level criteria tracking
        "app:total_criteria_updates": tool_context.state.get("app:total_criteria_updates", 0) + 1,
        
        # Temporary state
        "temp:last_criteria_update": criteria_name
    }
    
    # Create manual event for criteria update
    event = Event(
        invocation_id=tool_context.invocation_context.invocation_id,
        author="agent",
        content=types.Content(
            role="assistant",
            parts=[types.Part(text=f"Updated screening criteria '{criteria_name}': {criteria_description}")]
        ),
        actions=EventActions(state_delta=state_delta),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await tool_context.invocation_context.append_event(event)
    
    return {
        "status": "success",
        "criteria_name": criteria_name,
        "criteria_description": criteria_description,
        "importance": importance,
        "total_criteria": len(current_criteria),
        "message": f"Updated screening criteria: '{criteria_name}' with {importance} importance"
    }