#!/usr/bin/env python3
"""
Test client for fastapi_starter.py SSE endpoint
Creates a session, sends a message, and prints the streaming events
"""

import asyncio
import json
from datetime import datetime

import httpx


def classify_adk_event(event_data: dict) -> str:
    """
    Classify ADK event type based on event structure.
    Based on official ADK Event model documentation.
    """
    # Check if event has content
    if not event_data.get('content'):
        return "metadata_event"
    
    content = event_data['content']
    parts = content.get('parts', [])
    
    if not parts:
        return "empty_content"
    
    # Check for function calls/responses
    for part in parts:
        if 'functionCall' in part:
            return "function_call_request"
        elif 'functionResponse' in part:
            return "function_call_response"
    
    # Check for text content
    has_text = any('text' in part for part in parts)
    if has_text:
        # Check if this is a partial streaming event
        if event_data.get('partial', False):
            return "streaming_text_chunk"
        else:
            return "complete_text_message"
    
    return "unknown_content_type"


async def test_sse_endpoint():
    """Test the SSE streaming endpoint"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Starting SSE test...")
        
        # Step 1: Create session
        session_data = {
            "user_id": "test_user", 
            "session_id": "sse_test_session",
            "state": {}
        }
        
        print(f"📝 Creating session: {session_data['session_id']}")
        session_response = await client.post(f"{base_url}/sessions", json=session_data)
        
        if session_response.status_code != 200:
            print(f"❌ Session creation failed: {session_response.status_code}")
            print(session_response.text)
            return
            
        print(f"✅ Session created successfully")
        session_result = session_response.json()
        print(f"   Session info: {session_result}")
        
        # Step 2: Send message via SSE endpoint
        message_data = {
            "user_id": "test_user",
            "session_id": "sse_test_session", 
            "new_message": {
                "role": "user",
                "parts": [{"text": "Hello! Can you tell me about PostgreSQL and explain what makes it powerful?"}]
            }
        }
        
        print(f"\n💬 Sending message via SSE: '{message_data['new_message']['parts'][0]['text']}'")
        print(f"📡 Streaming events from {base_url}/run_sse...")
        print("-" * 80)
        
        # Step 3: Stream SSE events
        event_count = 0
        try:
            async with client.stream(
                "POST", 
                f"{base_url}/run_sse",
                json=message_data,
                headers={"Accept": "text/event-stream"}
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ SSE request failed: {response.status_code}")
                    print(await response.aread())
                    return
                
                async for line in response.aiter_lines():
                    if line.strip():  # Skip empty lines
                        event_count += 1
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        
                        # Parse SSE format (should be "data: {json}")
                        if line.startswith("data: "):
                            event_json = line[6:]  # Remove "data: " prefix
                            try:
                                event_data = json.loads(event_json)
                                
                                # Classify event type based on ADK Event model
                                event_type = classify_adk_event(event_data)
                                
                                print(f"[{timestamp}] Event #{event_count}:")
                                print(f"  Type: {event_type}")
                                print(f"  Author: {event_data.get('author', 'unknown')}")
                                print(f"  ID: {event_data.get('id', 'N/A')}")
                                print(f"  Invocation ID: {event_data.get('invocationId', 'N/A')}")
                                
                                # Show partial status for streaming events
                                if 'partial' in event_data:
                                    print(f"  Partial: {event_data['partial']}")
                                
                                # Print content if available
                                if 'content' in event_data and event_data['content']:
                                    content = event_data['content']
                                    if 'parts' in content and content['parts']:
                                        for i, part in enumerate(content['parts']):
                                            if 'text' in part:
                                                text = part['text'][:100]  # Truncate long text
                                                print(f"  Content[{i}]: {text}{'...' if len(part['text']) > 100 else ''}")
                                            elif 'functionCall' in part:
                                                func_call = part['functionCall']
                                                print(f"  Function Call: {func_call.get('name', 'unknown')}")
                                            elif 'functionResponse' in part:
                                                func_resp = part['functionResponse']
                                                print(f"  Function Response: {func_resp.get('name', 'unknown')}")
                                
                                # Print actions if available
                                if 'actions' in event_data and event_data['actions']:
                                    actions = event_data['actions']
                                    if actions.get('stateDelta'):
                                        print(f"  State Delta: {len(actions['stateDelta'])} changes")
                                    if actions.get('artifactDelta'):
                                        print(f"  Artifact Delta: {len(actions['artifactDelta'])} changes")
                                        
                                print()  # Empty line between events
                                
                            except json.JSONDecodeError as e:
                                print(f"[{timestamp}] ⚠️ Invalid JSON in event #{event_count}: {e}")
                                print(f"  Raw data: {line}")
                        else:
                            print(f"[{timestamp}] Raw line #{event_count}: {line}")
                            
        except httpx.TimeoutException:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error during SSE streaming: {e}")
            
        print("-" * 80)
        print(f"🏁 Finished. Received {event_count} events total.")


if __name__ == "__main__":
    asyncio.run(test_sse_endpoint())