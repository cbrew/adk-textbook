#!/usr/bin/env python3
"""
Demonstration of Persistent State Management with DatabaseSessionService.

This script shows the real power of "The Standard Way" (Google's term) allows manual event creation
that persists across session lifecycles using database-backed sessions.

Key demonstration:
1. Create a session and add state via manual events
2. Close the session 
3. Retrieve the same session from database in a new process/connection
4. Continue adding state and see persistence in action
5. Show state scoping (user:, app:, temp:) persistence behavior

This demonstrates why "The Standard Way" is powerful for:
- External system integrations
- Background processing
- Multi-process applications
- State management across session restarts

Based on: https://google.github.io/adk-docs/sessions/state/
"""

import asyncio
import uuid
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.genai import types


async def demonstrate_persistent_state():
    """
    Demonstrate persistent state management across session lifecycles.
    
    This shows the power of "The Standard Way" with database persistence.
    """
    print("💾 Starting Persistent State Management Demo")
    print("=" * 60)
    print("This demo shows state persistence across session lifecycles")
    print("=" * 60)
    
    # Create a temporary SQLite database for this demo
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_url = f"sqlite:///{temp_db.name}"
    
    print(f"📀 Using SQLite database: {temp_db.name}")
    
    # Session identifiers that will persist
    app_name = "persistent_research_demo"
    user_id = "research_scientist_001"
    session_id = str(uuid.uuid4())
    
    print(f"🆔 Session identifiers:")
    print(f"   App: {app_name}")
    print(f"   User: {user_id}")
    print(f"   Session: {session_id}")
    print()
    
    # PHASE 1: Create session and add initial state
    print("=" * 60)
    print("PHASE 1: Initial Session Creation & State Updates")
    print("=" * 60)
    await phase1_initial_session(db_url, app_name, user_id, session_id)
    
    # PHASE 2: Close and reopen - demonstrate persistence
    print("\n" + "=" * 60)
    print("PHASE 2: Session Persistence - New Connection")

    print("=" * 60)
    await phase2_persistent_retrieval(db_url, app_name, user_id, session_id)
    
    # PHASE 3: Advanced state management across connections
    print("\n" + "=" * 60)
    print("PHASE 3: Advanced Cross-Connection State Management")
    print("=" * 60)
    await phase3_advanced_persistence(db_url, app_name, user_id, session_id)
    
    # Clean up
    Path(temp_db.name).unlink()
    print(f"\n🧹 Cleaned up database: {temp_db.name}")
    
    print(f"\n✅ Persistent state demo completed!")
    print("   Demonstrated state persistence across session lifecycles!")


async def phase1_initial_session(db_url: str, app_name: str, user_id: str, session_id: str):
    """Phase 1: Create session and establish initial state."""
    
    print("🔄 Creating new DatabaseSessionService connection...")
    session_service = DatabaseSessionService(db_url=db_url)
    
    # Create session with initial state
    print("📋 Creating new session with initial state...")
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={
            "research_status": "initialized",
            "user:total_projects": 0,
            "app:system_version": "1.0.0"
        }
    )
    
    print(f"   ✓ Session created with {len(session.state)} initial state keys")
    print_state_summary(session.state, "Initial state")
    
    # Add research project via manual event
    print("\n🔬 Adding research project via manual event...")
    await add_research_project(session_service, session, 
                             "Quantum Machine Learning Applications",
                             "Exploring quantum algorithms for ML optimization")
    
    # Add user-level progress tracking
    print("\n👤 Updating user-level progress...")
    await update_user_progress(session_service, session, user_id)
    
    # Add app-level metrics
    print("\n📊 Updating application metrics...")
    await update_app_metrics(session_service, session)
    
    # Show final state for Phase 1
    updated_session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"\n📊 Phase 1 Final State ({len(updated_session.state)} keys):")
    print_state_summary(updated_session.state, "Phase 1 completion")
    
    print(f"💾 Session state persisted to database")


async def phase2_persistent_retrieval(db_url: str, app_name: str, user_id: str, session_id: str):
    """Phase 2: New connection, retrieve persisted session, verify state."""
    
    print("🔄 Creating NEW DatabaseSessionService connection...")
    print("   (Simulating new process/restart scenario)")
    
    # Create completely new session service instance
    new_session_service = DatabaseSessionService(db_url=db_url)
    
    print(f"🔍 Retrieving persisted session from database...")
    retrieved_session = await new_session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id)
    
    if retrieved_session is None:
        print("❌ ERROR: Could not retrieve session from database!")
        return
        
    print(f"   ✅ Successfully retrieved session with {len(retrieved_session.state)} persisted keys")
    print_state_summary(retrieved_session.state, "Retrieved from database")
    
    # Verify specific state values persisted correctly
    print("\n🔍 Verifying state persistence:")
    expected_keys = [
        ("research_project_name", "session-level"),
        ("user:total_projects", "user-level"),
        ("user:current_project", "user-level"), 
        ("app:total_research_projects", "app-level"),
        ("app:system_version", "app-level")
    ]
    
    for key, scope in expected_keys:
        if key in retrieved_session.state:
            value = retrieved_session.state[key]
            print(f"   ✅ {scope}: {key} = {value}")
        else:
            print(f"   ❌ Missing {scope} key: {key}")
    
    # Add more state to show continued persistence
    print("\n➕ Adding milestone completion via new connection...")
    await complete_research_milestone(new_session_service, retrieved_session,
                                    "Literature Review", 
                                    "Identified 25 relevant papers on quantum ML")
    
    # Verify the addition persisted
    final_session = await new_session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"\n📊 Phase 2 Final State ({len(final_session.state)} keys):")
    print_state_summary(final_session.state, "After new connection updates")


async def phase3_advanced_persistence(db_url: str, app_name: str, user_id: str, session_id: str):
    """Phase 3: Advanced scenarios - concurrent connections, complex state."""
    
    print("🔄 Creating THIRD DatabaseSessionService connection...")
    print("   (Simulating external system integration scenario)")
    
    # Yet another new connection
    external_session_service = DatabaseSessionService(db_url=db_url)
    session = await external_session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id)
    
    # Simulate external system batch update
    print("\n🤖 Simulating external system batch state update...")
    await external_system_batch_update(external_session_service, session)
    
    # Demonstrate state scoping persistence
    print("\n🏷️  Testing state prefix persistence across connections...")
    await test_state_scoping_persistence(external_session_service, session)
    
    # Show final comprehensive state
    final_session = await external_session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"\n📊 FINAL COMPREHENSIVE STATE ({len(final_session.state)} keys):")
    print_state_by_scope(final_session.state)


async def add_research_project(session_service: DatabaseSessionService, session: Session, 
                             project_name: str, description: str):
    """Add research project using manual event creation."""
    
    state_changes = {
        "research_project_name": project_name,
        "research_description": description,
        "research_status": "active",
        "research_created": datetime.now(timezone.utc).isoformat(),
        "research_phase": "planning"
    }
    
    # Create manual system event
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",  # System-level event, not agent
        content=types.Content(
            role="system",
            parts=[types.Part(text=f"Research project created: {project_name}")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print(f"   ✓ Added research project: {project_name}")


async def update_user_progress(session_service: DatabaseSessionService, session: Session, user_id: str):
    """Update user-level progress tracking."""
    
    current_projects = session.state.get("user:total_projects", 0)
    
    state_changes = {
        "user:total_projects": current_projects + 1,
        "user:current_project": session.state.get("research_project_name", "Unknown"),
        "user:last_activity": datetime.now(timezone.utc).isoformat(),
        "user:skill_level": "advanced_researcher"
    }
    
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text=f"Updated user progress for {user_id}")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print(f"   ✓ Updated user progress: {current_projects + 1} total projects")


async def update_app_metrics(session_service: DatabaseSessionService, session: Session):
    """Update application-level metrics."""
    
    current_projects = session.state.get("app:total_research_projects", 0)
    
    state_changes = {
        "app:total_research_projects": current_projects + 1,
        "app:last_project_created": datetime.now(timezone.utc).isoformat(),
        "app:active_researchers": session.state.get("app:active_researchers", []) + ["research_scientist_001"],
        "app:system_health": "optimal"
    }
    
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system", 
            parts=[types.Part(text="Updated application metrics")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print(f"   ✓ Updated app metrics: {current_projects + 1} total research projects")


async def complete_research_milestone(session_service: DatabaseSessionService, session: Session,
                                    milestone_name: str, findings: str):
    """Complete a research milestone via manual event."""
    
    milestones = session.state.get("research_milestones", [])
    milestone_record = {
        "name": milestone_name,
        "findings": findings,
        "completed": datetime.now(timezone.utc).isoformat()
    }
    
    state_changes = {
        "research_milestones": milestones + [milestone_record],
        "research_phase": "execution",
        "last_milestone": milestone_name,
        "milestone_count": len(milestones) + 1
    }
    
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text=f"Milestone completed: {milestone_name}")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print(f"   ✓ Completed milestone: {milestone_name}")


async def external_system_batch_update(session_service: DatabaseSessionService, session: Session):
    """Simulate external system making batch state updates."""
    
    state_changes = {
        # Simulate data from external research database
        "external:paper_count": 127,
        "external:citation_impact": 8.5,
        "external:collaboration_score": "high",
        "external:last_sync": datetime.now(timezone.utc).isoformat(),
        
        # Update research status based on external data
        "research_validation": "peer_reviewed",
        "research_impact_score": 8.5,
        
        # App-level external integrations
        "app:external_integrations": ["arxiv", "pubmed", "ieee_xplore"],
        "app:api_calls_today": 1247
    }
    
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="external_system",  # Different author to show external integration
        content=types.Content(
            role="system",
            parts=[types.Part(text="External research database sync completed")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print("   ✓ External system batch update completed")


async def test_state_scoping_persistence(session_service: DatabaseSessionService, session: Session):
    """Test that different state scopes persist correctly."""
    
    state_changes = {
        # Session-specific (should persist with session)
        "test_session_data": "session_specific_value",
        
        # User-level (should persist across user sessions)
        "user:test_preference": "dark_mode",
        "user:test_counter": session.state.get("user:test_counter", 0) + 1,
        
        # App-level (should persist across all users/sessions)
        "app:test_global_setting": "production",
        "app:test_feature_flags": {"advanced_analytics": True, "beta_ui": False},
        
        # Temp state (behavior depends on implementation)
        "temp:test_processing_id": str(uuid.uuid4()),
        "temp:test_batch_job": "state_persistence_test"
    }
    
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text="State scoping persistence test")]
        ),
        actions=EventActions(state_delta=state_changes),
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, event)
    print("   ✓ State scoping test data added")


def print_state_summary(state: dict, context: str):
    """Print a summary of the current state."""
    if not state:
        print(f"   📝 {context}: No state data")
        return
        
    print(f"   📝 {context}:")
    for key, value in sorted(state.items())[:5]:  # Show first 5 keys
        if len(str(value)) > 50:
            print(f"      {key}: {str(value)[:50]}...")
        else:
            print(f"      {key}: {value}")
    
    if len(state) > 5:
        print(f"      ... and {len(state) - 5} more keys")


def print_state_by_scope(state: dict):
    """Print state organized by scope prefixes."""
    scopes = {
        "session": [],
        "user": [],
        "app": [], 
        "temp": [],
        "external": [],
        "other": []
    }
    
    for key, value in state.items():
        if key.startswith("user:"):
            scopes["user"].append((key, value))
        elif key.startswith("app:"):
            scopes["app"].append((key, value))
        elif key.startswith("temp:"):
            scopes["temp"].append((key, value))
        elif key.startswith("external:"):
            scopes["external"].append((key, value))
        elif ":" in key:
            scopes["other"].append((key, value))
        else:
            scopes["session"].append((key, value))
    
    for scope, items in scopes.items():
        if items:
            print(f"\n   📁 {scope.upper()} SCOPE ({len(items)} keys):")
            for key, value in sorted(items)[:3]:  # Show first 3 of each scope
                if len(str(value)) > 60:
                    print(f"      {key}: {str(value)[:60]}...")
                else:
                    print(f"      {key}: {value}")
            if len(items) > 3:
                print(f"      ... and {len(items) - 3} more {scope} keys")


if __name__ == "__main__":
    print("Persistent State Management Demo")
    print("Demonstrates DatabaseSessionService with 'The Standard Way'")
    print("Based on: https://google.github.io/adk-docs/sessions/state/")
    print()
    
    asyncio.run(demonstrate_persistent_state())