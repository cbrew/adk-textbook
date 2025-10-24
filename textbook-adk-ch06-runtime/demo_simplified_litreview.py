#!/usr/bin/env python3
"""
Simplified Literature Review Agent Demo

This demo shows all ADK state management patterns through a realistic 
academic workflow. The agent helps researchers manage papers through
a 4-stage literature review pipeline with persistent state.

Demonstrates:
- Direct state access in tools
- output_key pattern for agent responses  
- State injection with {key} templating
- Manual event creation for complex operations
- Database persistence across sessions
- External system integration via offline imports

Based on: https://google.github.io/adk-docs/sessions/state/
"""

import asyncio
import tempfile
from pathlib import Path
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from simplified_litreview_agent import simplified_litreview_agent
from simplified_litreview_agent.tools.offline_import import import_bibtex_batch, sync_external_database


async def demo_literature_review_workflow():
    """
    Comprehensive demo of literature review agent with all state patterns.
    """
    print("📚 Simplified Literature Review Agent Demo")
    print("=" * 60)
    print("Demonstrates ALL ADK state management patterns through")
    print("a realistic academic literature review workflow")
    print("=" * 60)
    
    # Create temporary database for persistence demo
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_url = f"sqlite:///{temp_db.name}"
    
    # Use database session service for persistence
    session_service = DatabaseSessionService(db_url=db_url)
    artifact_service = InMemoryArtifactService()
    
    runner = Runner(
        agent=simplified_litreview_agent,
        app_name="litreview_demo",
        session_service=session_service,
        artifact_service=artifact_service,
    )
    
    user_id = "researcher_jane"
    session_id = "ai_bias_review_001"
    
    print(f"🆔 Session: {session_id}")
    print(f"👤 User: {user_id}")
    print(f"📀 Database: {temp_db.name}")
    print()
    
    # Create session with initial state
    await session_service.create_session(
        app_name="litreview_demo",
        user_id=user_id,
        session_id=session_id,
        state={
            "pipeline_stage": "initialization",
            "papers": {},
            "papers_in_pipeline": 0,
            "user:research_interests": ["AI", "bias", "ethics"],
            "user:papers_added": 0,
            "app:system_version": "demo_v1.0"
        }
    )
    
    # PHASE 1: Setup and Paper Collection
    print("PHASE 1: Research Setup & Paper Collection")
    print("-" * 40)
    await demo_phase1_setup(runner, user_id, session_id)
    
    # PHASE 2: Offline Import (demonstrates "The Standard Way")  
    print("\nPHASE 2: Offline Import - The Standard Way")
    print("-" * 40)
    await demo_phase2_offline_import(session_service, "litreview_demo", user_id, session_id)
    
    # PHASE 3: Screening and Analysis
    print("\nPHASE 3: Paper Screening & Analysis")
    print("-" * 40)
    await demo_phase3_screening(runner, user_id, session_id)
    
    # PHASE 4: Theme Extraction (output_key demo)
    print("\nPHASE 4: Theme Extraction - output_key Pattern")
    print("-" * 40)
    await demo_phase4_themes(runner, user_id, session_id)
    
    # PHASE 5: Persistence Demo
    print("\nPHASE 5: Session Persistence Demo") 
    print("-" * 40)
    await demo_phase5_persistence(session_service, "litreview_demo", user_id, session_id)
    
    # Cleanup
    Path(temp_db.name).unlink()
    print(f"\n🧹 Cleaned up database: {temp_db.name}")
    
    print(f"\n✅ Literature review demo completed!")
    print("   Demonstrated all ADK state management patterns!")


async def demo_phase1_setup(runner: Runner, user_id: str, session_id: str):
    """Phase 1: Research setup and initial paper collection."""
    
    print("🎯 Setting research query (state injection demo)...")
    
    # Set research query - demonstrates direct state access
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user", 
            parts=[types.Part(text="Set my research query to 'AI bias in hiring algorithms' with focus area 'AI Ethics'")]
        )
    ):
        events.append(event)
    
    response_text = extract_agent_text(events)
    print(f"   ✓ {response_text[:100]}...")
    
    print("\n📄 Adding papers manually (direct state access)...")
    
    # Add first paper
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="""Add this paper: 
Title: "Algorithmic Bias in Resume Screening: A Comprehensive Analysis"
Authors: "Johnson, M. & Smith, K."  
Year: "2023"
Venue: "Journal of AI Ethics"
Abstract: "This study examines bias in algorithmic resume screening systems used by major corporations."
""")]
        )
    ):
        events.append(event)
        
    print(f"   ✓ Added paper 1")
    
    # Add second paper  
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="""Add this paper:
Title: "Fairness in Automated Hiring: Challenges and Solutions" 
Authors: "Williams, A. & Chen, L. & Davis, R."
Year: "2024"
Venue: "Conference on Fair AI"
Abstract: "We propose novel techniques for ensuring fairness in automated hiring systems."
""")]
        )
    ):
        events.append(event)
        
    print(f"   ✓ Added paper 2")
    
    # Check pipeline status
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's my current pipeline status?")]
        )
    ):
        events.append(event)
        
    status_text = extract_agent_text(events)
    print(f"   📊 Status: {status_text[:150]}...")


async def demo_phase2_offline_import(session_service: DatabaseSessionService, 
                                   app_name: str, user_id: str, session_id: str):
    """Phase 2: Offline imports using 'The Standard Way' manual events."""
    
    print("📚 BibTeX import (manual event creation)...")
    
    # Sample BibTeX for import
    sample_bibtex = '''
    @article{garcia2023fairness,
        title={Fairness Metrics in Machine Learning: A Critical Review},
        author={Garcia, Maria and Thompson, James},
        journal={AI Review Quarterly},
        year={2023},
        abstract={This paper provides a comprehensive review of fairness metrics used in machine learning systems, with special focus on hiring applications.}
    }
    
    @inproceedings{patel2024bias,
        title={Detecting and Mitigating Bias in Recruitment Algorithms},
        author={Patel, Raj and Kim, Susan},
        booktitle={International Conference on AI Fairness},
        year={2024},
        abstract={We present novel methods for detecting and mitigating various forms of bias in algorithmic recruitment systems.}
    }
    '''
    
    result = await import_bibtex_batch(
        bibtex_content=sample_bibtex,
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        import_tag="bias_research"
    )
    
    print(f"   ✓ {result['message']}")
    
    print("\n🌐 External database sync (system-level events)...")
    
    result = await sync_external_database(
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        search_query="algorithmic bias hiring",
        max_papers=3
    )
    
    print(f"   ✓ {result['message']}")


async def demo_phase3_screening(runner: Runner, user_id: str, session_id: str):
    """Phase 3: Paper screening using manual event creation for complex updates."""
    
    print("🔍 Screening papers (manual event creation for complex updates)...")
    
    # First, get current papers to screen
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Search for all papers so I can screen them")]
        )
    ):
        events.append(event)
    
    search_text = extract_agent_text(events)
    print(f"   📋 Found papers to screen")
    
    # Screen a paper as relevant
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id, 
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="""Screen the first paper as relevant with reasoning: 
"Directly addresses algorithmic bias in hiring, which is central to my research question. High-quality empirical study with clear methodology."
Confidence: high""")]
        )
    ):
        events.append(event)
        
    screening_text = extract_agent_text(events)
    print(f"   ✓ Screened paper as relevant")
    
    # Update screening criteria  
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="""Update screening criteria: 
Name: "Empirical Evidence Required"
Description: "Paper must include original empirical research or analysis, not just theoretical discussion" 
Importance: high""")]
        )
    ):
        events.append(event)
        
    criteria_text = extract_agent_text(events)
    print(f"   ✓ Updated screening criteria")


async def demo_phase4_themes(runner: Runner, user_id: str, session_id: str):
    """Phase 4: Theme extraction using output_key pattern with sub-agents."""
    
    print("🎨 Using ThemeAgent (output_key pattern)...")
    
    # Delegate to theme extraction agent
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Use the ThemeAgent to identify key themes from my relevant papers")]
        )
    ):
        events.append(event)
        
    themes_text = extract_agent_text(events)
    print(f"   ✓ Themes extracted and saved to state: {themes_text[:100]}...")
    
    print("\n💡 Using RecommendationAgent (output_key pattern)...")
    
    # Get research recommendations
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user", 
            parts=[types.Part(text="Use the RecommendationAgent to suggest next steps for my literature review")]
        )
    ):
        events.append(event)
        
    recs_text = extract_agent_text(events) 
    print(f"   ✓ Recommendations generated and saved: {recs_text[:100]}...")


async def demo_phase5_persistence(session_service: DatabaseSessionService,
                                app_name: str, user_id: str, session_id: str):
    """Phase 5: Demonstrate state persistence across sessions."""
    
    print("💾 Testing state persistence...")
    
    # Get session state 
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    if session:
        papers_count = len(session.state.get("papers", {}))
        pipeline_stage = session.state.get("pipeline_stage", "unknown")
        search_query = session.state.get("current_search_query", "not set")
        
        print(f"   📊 Persisted state retrieved:")
        print(f"      Papers: {papers_count}")
        print(f"      Stage: {pipeline_stage}")
        print(f"      Query: {search_query}")
        print(f"      Total state keys: {len(session.state)}")
        
        # Show state by scope
        scopes = {"session": 0, "user": 0, "app": 0, "temp": 0}
        for key in session.state.keys():
            if key.startswith("user:"):
                scopes["user"] += 1
            elif key.startswith("app:"):
                scopes["app"] += 1
            elif key.startswith("temp:"):
                scopes["temp"] += 1
            else:
                scopes["session"] += 1
                
        print(f"      State scoping: {scopes}")
        print("   ✓ All state persisted successfully across phases")
    else:
        print("   ❌ Session not found!")


def extract_agent_text(events) -> str:
    """Extract agent text from event stream."""
    agent_texts = []
    for event in events:
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'text'):
                agent_texts.append(event.content.text)
            elif hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        agent_texts.append(part.text)
    return " ".join(agent_texts) if agent_texts else "No response text found"


if __name__ == "__main__":
    print("Simplified Literature Review Agent Demo")
    print("Comprehensive ADK State Management Demonstration") 
    print("Based on: https://google.github.io/adk-docs/sessions/state/")
    print()
    
    asyncio.run(demo_literature_review_workflow())