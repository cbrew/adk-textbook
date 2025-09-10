#!/usr/bin/env python3
"""
Enhanced State Management Demo - Shows both simple and EventActions.state_delta approaches

This demo illustrates:
1. Simple state updates using tool_context.update_state()  
2. Complex state updates using EventActions.state_delta (The Standard Way)
3. External state mutations via API endpoints
4. Agent state visibility and response patterns

Run: python demo_enhanced_state.py
"""

import asyncio
import json
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from dotenv import load_dotenv
from enhanced_research_agent import enhanced_agent


async def demo_enhanced_state_management():
    """Comprehensive demo of both state management approaches."""
    
    # Load environment
    env_path = Path.cwd() / "postgres_chat_agent" / ".env"
    load_dotenv(env_path)
    
    print("🚀 Enhanced State Management Demo")
    print("=" * 60)
    print("This demo shows TWO approaches to ADK state management:")
    print("1. Simple: tool_context.update_state() for single updates")
    print("2. Standard: EventActions.state_delta for complex updates")
    print("=" * 60)
    
    # Create runner with enhanced agent
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    
    runner = Runner(
        agent=enhanced_agent,
        app_name="enhanced_research",
        session_service=session_service,
        artifact_service=artifact_service,
    )
    
    user_id = "demo_researcher"
    session_id = "enhanced_demo_001"
    
    # Create session
    await session_service.create_session(
        app_name="enhanced_research",
        user_id=user_id,
        session_id=session_id,
        state={}
    )
    
    print("\n📋 DEMO 1: Complex State Initialization")
    print("Using EventActions.state_delta to set up complete research project")
    print("-" * 60)
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Initialize a new research project called 'AI Ethics Study' about ethical implications of AI systems")]
        )
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    await show_current_state(session_service, user_id, session_id)
    
    print("\n📋 DEMO 2: Simple State Updates")
    print("Using simple tools for individual field updates")
    print("-" * 60)
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Add a research source: 'Ethics in AI' from ethics-ai.org")]
        )
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    
    print("\n📋 DEMO 3: External State Mutation")
    print("Simulating external system updating state via state_delta")
    print("-" * 60)
    
    # Simulate external state change (like what our FastAPI endpoints do)
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="system",
            parts=[types.Part(text="External management system updated priority to High and set deadline to 2024-03-15")]
        ),
        state_delta={
            "research:priority_level": "High",
            "research:deadline": "2024-03-15", 
            "external:update_source": "management_dashboard",
            "external:update_timestamp": "2024-01-01T14:30:00Z"
        }
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    await show_current_state(session_service, user_id, session_id)
    
    print("\n📋 DEMO 4: Complex Milestone Completion")
    print("Using EventActions.state_delta for complex milestone tracking")
    print("-" * 60)
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="I completed the literature review milestone. Key finding: Most AI ethics frameworks focus on fairness and transparency. Next steps are: interview experts, analyze case studies")]
        )
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    
    print("\n📋 DEMO 5: Batch State Updates")
    print("Using EventActions.state_delta for multiple field updates")
    print("-" * 60)
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Update my research: change topic to 'AI Ethics in Healthcare', set priority to Medium, and deadline to 2024-04-01")]
        )
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    
    print("\n📋 DEMO 6: State Visibility Check")
    print("Agent using tools to check current state")
    print("-" * 60)
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's my complete current research status?")]
        )
    ):
        events.append(event)
    
    print(f"Agent response: {extract_agent_text(events)}")
    await show_current_state(session_service, user_id, session_id)
    
    print("\n🎯 SUMMARY")
    print("=" * 60)
    print("✅ EventActions.state_delta: Used for complex, multi-field updates")
    print("✅ Simple tools: Used for single field changes")
    print("✅ External state_delta: Updates stored but agent not auto-notified")
    print("✅ Agent tools: Can read current state via ToolContext.state")
    print("✅ Explicit notification: Agent responds to external change messages")


async def show_current_state(session_service, user_id, session_id):
    """Show the current session state."""
    session = await session_service.get_session(
        app_name="enhanced_research", user_id=user_id, session_id=session_id
    )
    print(f"\n📊 Current State ({len(session.state)} keys):")
    for key, value in session.state.items():
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
        elif isinstance(value, dict):
            print(f"  {key}: {{{len(value)} fields}}")
        else:
            print(f"  {key}: {value}")


def extract_agent_text(events):
    """Extract agent's text response from events."""
    for event in events:
        if (event.author == "agent" and 
            event.content and 
            event.content.parts):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text[:200] + ("..." if len(part.text) > 200 else "")
    return "No agent response"


if __name__ == "__main__":
    asyncio.run(demo_enhanced_state_management())