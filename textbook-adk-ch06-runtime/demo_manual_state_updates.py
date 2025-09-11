#!/usr/bin/env python3
"""
Demonstration of "The Standard Way" for ADK state management.

This script shows how to manually create events with state updates using
session_service.append_event() - the pattern shown in ADK documentation
that bypasses agent execution but still goes through the session.

Key characteristics:
- Direct session manipulation without agent runs
- Manual event creation with EventActions.state_delta
- System-level state updates outside of tool contexts
- Proper state scoping with prefixes

Based on: https://google.github.io/adk-docs/sessions/state/
"""

import asyncio
import uuid
from datetime import datetime, timezone
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.genai import types


async def demonstrate_manual_state_updates():
    """
    Demonstrate the proper "Standard Way" for manual state updates.
    
    This is the pattern shown in ADK docs that creates events manually
    without running an agent, but still goes through the session.
    """
    print("🚀 Starting Manual State Updates Demo - The Standard Way")
    print("=" * 60)
    
    # Create a new session for demonstration
    session_service = InMemorySessionService()
    app_name = "manual_state_demo"
    user_id = "demo_user"
    session_id = str(uuid.uuid4())
    
    # Create session with proper parameters - this returns the session object
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user:login_count": 0, "task_status": "idle"}
    )
    
    print(f"📋 Created session: {session_id}")
    print(f"   Initial state: {session.state}")
    print()
    
    # Demo 1: Simple session state update
    print("Demo 1: Simple session state update (no prefix)")
    await update_session_state(session_service, session)
    
    # Demo 2: User-level state update
    print("\nDemo 2: User-level state update (user: prefix)")
    await update_user_state(session_service, session, session_id)
    
    # Demo 3: Application-wide state update
    print("\nDemo 3: Application-wide state update (app: prefix)")
    await update_app_state(session_service, session)
    
    # Demo 4: Temporary state update
    print("\nDemo 4: Temporary state update (temp: prefix)")
    await update_temp_state(session_service, session)
    
    # Demo 5: Complex multi-prefix batch update
    print("\nDemo 5: Complex batch update with all prefixes")
    await complex_batch_update(session_service, session)
    
    # Show final state
    print("\n" + "=" * 60)
    print("📊 FINAL SESSION STATE:")
    for key, value in sorted(session.state.items()):
        print(f"   {key}: {value}")
    
    print(f"\n✅ Manual state updates demo completed!")
    print("   This demonstrates 'The Standard Way' from ADK documentation.")


async def update_session_state(session_service: InMemorySessionService, session: Session):
    """Update session-specific state (no prefix)."""
    
    state_changes = {
        "research_topic": "Machine Learning in Academic Research",
        "session_started": datetime.now(timezone.utc).isoformat(),
        "demo_step": "session_state"
    }
    
    # Create EventActions with state_delta - this is "The Standard Way"
    actions_with_update = EventActions(state_delta=state_changes)
    
    # Create a manual system event (no agent execution)
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",  # Important: system author, not agent
        content=types.Content(
            role="system",
            parts=[types.Part(text="Session state initialized")]
        ),
        actions=actions_with_update,
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    # Apply changes using session_service.append_event
    await session_service.append_event(session, system_event)
    
    print(f"   ✓ Updated session state: {list(state_changes.keys())}")
    print(f"   Current topic: {session.state.get('research_topic')}")


async def update_user_state(session_service: InMemorySessionService, session: Session, session_id: str):
    """Update user-level state (user: prefix) - persists across sessions."""
    
    current_login_count = session.state.get("user:login_count", 0)
    
    state_changes = {
        "user:login_count": current_login_count + 1,
        "user:last_login_ts": datetime.now(timezone.utc).isoformat(),
        "user:preferred_topic": "AI Research",
        "user:session_history": session.state.get("user:session_history", []) + [session_id]
    }
    
    actions_with_update = EventActions(state_delta=state_changes)
    
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text="User state updated")]
        ),
        actions=actions_with_update,
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, system_event)
    
    print(f"   ✓ Updated user state: user:login_count = {state_changes['user:login_count']}")
    print(f"   Total sessions: {len(state_changes['user:session_history'])}")


async def update_app_state(session_service: InMemorySessionService, session: Session):
    """Update application-wide state (app: prefix) - global across all users."""
    
    total_sessions = session.state.get("app:total_sessions_created", 0)
    
    state_changes = {
        "app:total_sessions_created": total_sessions + 1,
        "app:last_update": datetime.now(timezone.utc).isoformat(),
        "app:system_status": "active",
        "app:feature_flags": {"manual_state_demo": True, "advanced_research": True}
    }
    
    actions_with_update = EventActions(state_delta=state_changes)
    
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text="Application state updated")]
        ),
        actions=actions_with_update,
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, system_event)
    
    print(f"   ✓ Updated app state: total_sessions = {state_changes['app:total_sessions_created']}")
    print(f"   System status: {state_changes['app:system_status']}")


async def update_temp_state(session_service: InMemorySessionService, session: Session):
    """Update temporary state (temp: prefix) - cleaned up after invocation."""
    
    state_changes = {
        "temp:processing_step": "manual_demo",
        "temp:demo_timestamp": datetime.now(timezone.utc).isoformat(),
        "temp:cleanup_needed": True,
        "temp:workspace_files": ["demo_file_1.txt", "demo_file_2.txt"]
    }
    
    actions_with_update = EventActions(state_delta=state_changes)
    
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text="Temporary workspace created")]
        ),
        actions=actions_with_update,
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, system_event)
    
    print(f"   ✓ Updated temp state: workspace with {len(state_changes['temp:workspace_files'])} files")
    print(f"   Cleanup needed: {state_changes['temp:cleanup_needed']}")


async def complex_batch_update(session_service: InMemorySessionService, session: Session):
    """Demonstrate complex batch update with all prefix types in one event."""
    
    # This shows the power of "The Standard Way" - updating multiple
    # scopes and many fields in a single atomic operation
    state_changes = {
        # Session state
        "research_milestone": "Complex State Management",
        "demo_completed": True,
        "completion_timestamp": datetime.now(timezone.utc).isoformat(),
        
        # User state
        "user:demos_completed": session.state.get("user:demos_completed", 0) + 1,
        "user:expertise_level": "advanced",
        "user:last_completion": datetime.now(timezone.utc).isoformat(),
        
        # App state
        "app:successful_demos": session.state.get("app:successful_demos", 0) + 1,
        "app:demo_types_completed": session.state.get("app:demo_types_completed", []) + ["manual_state"],
        
        # Temp state
        "temp:batch_operation": "complex_update",
        "temp:fields_updated": 9,
        "temp:operation_success": True
    }
    
    actions_with_update = EventActions(state_delta=state_changes)
    
    system_event = Event(
        invocation_id=str(uuid.uuid4()),
        author="system",
        content=types.Content(
            role="system",
            parts=[types.Part(text="Complex batch state update completed")]
        ),
        actions=actions_with_update,
        timestamp=datetime.now(timezone.utc).timestamp()
    )
    
    await session_service.append_event(session, system_event)
    
    print(f"   ✓ Complex batch update: {len(state_changes)} fields across all scopes")
    print(f"   User demos completed: {state_changes['user:demos_completed']}")
    print(f"   App successful demos: {state_changes['app:successful_demos']}")


if __name__ == "__main__":
    print("Manual State Updates Demo - The Standard Way")
    print("Demonstrates proper EventActions.state_delta usage")
    print("Based on: https://google.github.io/adk-docs/sessions/state/")
    print()
    
    asyncio.run(demonstrate_manual_state_updates())