#!/usr/bin/env python3
"""
Test script to determine if agents can see state_delta changes.

This will help us understand:
1. Whether state changes are visible to the agent
2. How the agent should be prompted to handle external state changes
3. Whether EventActions.state_delta events are processed differently
"""

import asyncio
import json
from pathlib import Path

from google.adk.agents import Agent, RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from dotenv import load_dotenv


# Simple test agent that reports what it can see
test_agent_instruction = """
You are a State Visibility Test Agent. Your job is to report exactly what you can observe about the session state.

When you receive a message, please respond with:
1. "CURRENT SESSION STATE:" followed by any state keys and values you can see
2. "MESSAGE RECEIVED:" followed by the message content
3. "STATE OBSERVATION:" followed by any changes you notice from previous interactions

Be very explicit about what state information is available to you.
If you cannot see any state, say "NO STATE VISIBLE".
If you can see state, list every key-value pair you have access to.

Always be detailed about what information is or isn't available to you as an agent.
"""

test_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="state_visibility_test_agent",
    instruction=test_agent_instruction,
)


async def test_state_visibility():
    """Test whether agents can see state_delta changes."""
    
    # Load environment
    env_path = Path.cwd() / "postgres_chat_agent" / ".env"
    load_dotenv(env_path)
    
    print("🧪 Testing Agent State Visibility")
    print("=" * 50)
    
    # Create runner
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    
    runner = Runner(
        agent=test_agent,
        app_name="state_test",
        session_service=session_service,
        artifact_service=artifact_service,
    )
    
    user_id = "test_user"
    session_id = "state_visibility_test"
    
    # Create session first
    await session_service.create_session(
        app_name="state_test",
        user_id=user_id,
        session_id=session_id,
        state={}
    )
    
    print("🔧 Test 1: Initial message (no state)")
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Hello, what state can you see?")]
        )
    ):
        events.append(event)
    
    print(f"Agent response 1: {extract_agent_response(events)}")
    
    print("\n🔧 Test 2: External state injection via state_delta")
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="system",
            parts=[types.Part(text="External system updated state")]
        ),
        state_delta={
            "research:topic": "Neural Networks",
            "research:priority": "High", 
            "external:source": "management_dashboard",
            "temp:update_type": "priority_change"
        }
    ):
        events.append(event)
    
    print(f"Agent response 2: {extract_agent_response(events)}")
    
    print("\n🔧 Test 3: Ask agent about state after external update")
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What state can you see now? Did anything change?")]
        )
    ):
        events.append(event)
    
    print(f"Agent response 3: {extract_agent_response(events)}")
    
    print("\n🔧 Test 4: Check session state directly")
    session = await session_service.get_session(
        app_name="state_test", user_id=user_id, session_id=session_id
    )
    print(f"Direct session state: {json.dumps(session.state, indent=2)}")
    
    print("\n📊 Analysis:")
    print("- Test 1: Baseline agent response with no state")
    print("- Test 2: Agent response immediately after state_delta injection")  
    print("- Test 3: Agent response to follow-up question about state")
    print("- Test 4: Direct verification of what's actually in session state")


def extract_agent_response(events):
    """Extract the agent's text response from events."""
    print(f"  DEBUG: Got {len(events)} events")
    for i, event in enumerate(events):
        print(f"  Event {i}: author={event.author}, content={bool(event.content)}")
        if event.content and event.content.parts:
            print(f"    Parts: {len(event.content.parts)}")
            for j, part in enumerate(event.content.parts):
                print(f"    Part {j}: {type(part).__name__}")
                if hasattr(part, 'text'):
                    print(f"      Text: {part.text[:100]}...")
        if event.actions:
            print(f"    Actions: state_delta={bool(event.actions.state_delta)}")
            
    for event in events:
        if (event.author == "agent" and 
            event.content and 
            event.content.parts):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
    return "No agent response found"


if __name__ == "__main__":
    asyncio.run(test_state_visibility())