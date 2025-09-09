"""
Enhanced ADK consumer with artifact event handling.

This consumer provides better tracking of artifact-related events, including
creation, updates, and proper aggregation of streaming content.
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from adk_consumer import ADKConsumer


@dataclass
class ArtifactInfo:
    """Information about an artifact from events."""
    filename: str
    version: int = 0
    content: str = ""
    content_type: str = "text"
    created_in_invocation: str = ""
    last_updated_in_invocation: str = ""
    function_call_id: str = ""


@dataclass
class ConversationState:
    """Tracks the state of an ongoing conversation."""
    current_invocation: str = ""
    streaming_text: str = ""  # Accumulated streaming text for current response
    artifacts: dict[str, ArtifactInfo] = field(default_factory=dict)
    invocation_artifacts: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


class ArtifactEventConsumer:
    """Enhanced consumer that tracks artifacts and conversation flow."""
    
    def __init__(self, consumer: ADKConsumer):
        self.consumer = consumer
        self.state = ConversationState()
    
    def extract_enhanced_event_info(self, event: dict) -> dict:
        """Extract detailed event information with artifact awareness."""
        # Get basic event info
        author = event.get("author")
        actions = event.get("actions", {})
        content = event.get("content", {})
        invocation_id = event.get("invocationId", "")
        
        # Update current invocation tracking
        if invocation_id and invocation_id != self.state.current_invocation:
            # New invocation started - reset streaming text
            self.state.current_invocation = invocation_id
            self.state.streaming_text = ""
        
        # Extract and accumulate text content
        text = self._extract_text_content(content)
        full_text = ""
        
        if text and event.get("partial", False):
            self.state.streaming_text += text
            full_text = self.state.streaming_text
        elif text and not event.get("partial", False):
            # Complete text - use accumulated + current
            full_text = self.state.streaming_text + text
            self.state.streaming_text = ""  # Reset for next response
        else:
            full_text = self.state.streaming_text if event.get("partial", False) else (text or "")
        
        # Extract function calls with detailed artifact information
        function_calls = self._extract_function_calls(content)
        
        # Extract function responses and update artifact tracking
        function_responses = self._extract_function_responses(content)
        self._update_artifact_tracking_from_responses(function_responses, invocation_id)
        
        # Extract artifact deltas and update tracking
        artifact_delta = actions.get("artifactDelta", {})
        self._update_artifact_tracking_from_delta(artifact_delta, invocation_id)
        
        # Classify event type with artifact awareness
        event_type = self._classify_event_with_artifacts(
            event, author, function_calls, function_responses, artifact_delta, text
        )
        
        return {
            "type": event_type,
            "author": author,
            "invocation_id": invocation_id,
            "text": text,
            "full_accumulated_text": full_text,
            "partial": event.get("partial", False),
            "function_calls": function_calls,
            "function_responses": function_responses,
            "artifact_delta": artifact_delta,
            "artifacts_in_invocation": list(self.state.invocation_artifacts.get(invocation_id, [])),
            "all_artifacts": {name: {
                "filename": info.filename,
                "version": info.version,
                "content_preview": info.content[:100] + "..." if len(info.content) > 100 else info.content,
                "content_type": info.content_type
            } for name, info in self.state.artifacts.items()},
            "raw": event,
        }
    
    def _extract_text_content(self, content: dict | str) -> str | None:
        """Extract text from content parts."""
        if isinstance(content, str):
            return content
        
        if not isinstance(content, dict):
            return None
        
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            return None
        
        text_parts = []
        for part in parts:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        
        return "".join(text_parts) if text_parts else None
    
    def _extract_function_calls(self, content: dict) -> list[dict] | None:
        """Extract detailed function call information."""
        if not isinstance(content, dict):
            return None
        
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            return None
        
        function_calls = []
        for part in parts:
            if isinstance(part, dict) and "functionCall" in part:
                func_call = part["functionCall"]
                call_info = {
                    "id": func_call.get("id"),
                    "name": func_call.get("name"),
                    "args": func_call.get("args", {}),
                }
                
                # Special handling for artifact-related functions
                if func_call.get("name") == "save_text_artifact":
                    args = func_call.get("args", {})
                    call_info["artifact_info"] = {
                        "filename": args.get("filename"),
                        "content": args.get("text", ""),
                        "content_length": len(args.get("text", "")),
                    }
                elif func_call.get("name") == "retrieve_artifact":
                    args = func_call.get("args", {})
                    call_info["artifact_info"] = {
                        "filename": args.get("filename"),
                        "operation": "retrieve",
                    }
                
                function_calls.append(call_info)
        
        return function_calls if function_calls else None
    
    def _extract_function_responses(self, content: dict) -> list[dict] | None:
        """Extract function response information."""
        if not isinstance(content, dict):
            return None
        
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            return None
        
        function_responses = []
        for part in parts:
            if isinstance(part, dict) and "functionResponse" in part:
                func_response = part["functionResponse"]
                response_info = {
                    "id": func_response.get("id"),
                    "name": func_response.get("name"),
                    "response": func_response.get("response", {}),
                }
                function_responses.append(response_info)
        
        return function_responses if function_responses else None
    
    def _update_artifact_tracking_from_responses(self, function_responses: list[dict] | None, invocation_id: str):
        """Update artifact tracking from function responses."""
        if not function_responses:
            return
        
        for response in function_responses:
            if response.get("name") == "save_text_artifact":
                resp_data = response.get("response", {})
                filename = resp_data.get("filename")
                version = resp_data.get("version", 0)
                
                if filename:
                    if filename not in self.state.artifacts:
                        self.state.artifacts[filename] = ArtifactInfo(
                            filename=filename,
                            version=version,
                            created_in_invocation=invocation_id,
                            function_call_id=response.get("id", "")
                        )
                    else:
                        self.state.artifacts[filename].version = version
                        self.state.artifacts[filename].last_updated_in_invocation = invocation_id
                    
                    # Track which artifacts were created/updated in this invocation
                    if invocation_id not in self.state.invocation_artifacts:
                        self.state.invocation_artifacts[invocation_id] = []
                    if filename not in self.state.invocation_artifacts[invocation_id]:
                        self.state.invocation_artifacts[invocation_id].append(filename)
    
    def _update_artifact_tracking_from_delta(self, artifact_delta: dict, invocation_id: str):
        """Update artifact tracking from artifact delta information."""
        if not artifact_delta:
            return
        
        for filename, version in artifact_delta.items():
            if filename not in self.state.artifacts:
                self.state.artifacts[filename] = ArtifactInfo(
                    filename=filename,
                    version=version,
                    created_in_invocation=invocation_id
                )
            else:
                self.state.artifacts[filename].version = version
                self.state.artifacts[filename].last_updated_in_invocation = invocation_id
    
    def _classify_event_with_artifacts(
        self, 
        event: dict, 
        author: str | None, 
        function_calls: list | None, 
        function_responses: list | None,
        artifact_delta: dict,
        text: str | None
    ) -> str:
        """Classify events with artifact awareness."""
        # Check for errors first
        if event.get("error") or event.get("error_message"):
            return "ERROR"
        
        # User messages
        if author == "user":
            return "USER_MESSAGE"
        
        # Artifact-specific events
        if function_calls:
            # Check if this is an artifact-related call
            for call in function_calls:
                if call.get("name") in ["save_text_artifact", "save_artifact", "create_artifact"]:
                    return "ARTIFACT_CREATION_CALL"
                elif call.get("name") in ["retrieve_artifact", "get_artifact"]:
                    return "ARTIFACT_RETRIEVAL_CALL"
            return "TOOL_CALL"
        
        if function_responses:
            # Check if this is an artifact-related response
            for response in function_responses:
                if response.get("name") in ["save_text_artifact", "save_artifact", "create_artifact"]:
                    return "ARTIFACT_CREATION_RESPONSE"
                elif response.get("name") in ["retrieve_artifact", "get_artifact"]:
                    return "ARTIFACT_RETRIEVAL_RESPONSE"
            return "TOOL_RESULT"
        
        # Artifact delta updates (version changes, etc.)
        if artifact_delta:
            return "ARTIFACT_UPDATE"
        
        # Text streaming vs complete
        if text:
            if event.get("partial", False):
                return "STREAMING_TEXT_CHUNK"
            else:
                return "COMPLETE_TEXT"
        
        # Control signals
        actions = event.get("actions", {})
        control_signals = ["transfer_to_agent", "escalate", "skip_summarization", "requested_auth_configs"]
        if any(actions.get(signal) for signal in control_signals):
            return "CONTROL_SIGNAL"
        
        return "OTHER"
    
    def get_conversation_summary(self) -> dict:
        """Get a summary of the current conversation state."""
        return {
            "current_invocation": self.state.current_invocation,
            "total_artifacts": len(self.state.artifacts),
            "artifacts": {
                name: {
                    "filename": info.filename,
                    "version": info.version,
                    "content_length": len(info.content),
                    "created_in": info.created_in_invocation,
                }
                for name, info in self.state.artifacts.items()
            },
            "invocations_with_artifacts": len(self.state.invocation_artifacts),
        }


async def demonstrate_improved_consumption():
    """Demonstrate the improved artifact event consumption."""
    import httpx
    
    async with httpx.AsyncClient(timeout=None) as client:
        base_consumer = await ADKConsumer.create(client)
        artifact_consumer = ArtifactEventConsumer(base_consumer)
        
        print("=== Enhanced Artifact-Aware Event Consumption ===\n")
        
        async for event_type, event_data in base_consumer.message("make me a note about rhubarb and save it as an artifact"):
            if event_type == "Event:" and isinstance(event_data, dict):
                enhanced_info = artifact_consumer.extract_enhanced_event_info(event_data)
                
                print(f"Event Type: {enhanced_info['type']}")
                print(f"Author: {enhanced_info['author']}")
                print(f"Invocation: {enhanced_info['invocation_id'][:8]}...")
                
                if enhanced_info['text']:
                    print(f"Text: {enhanced_info['text'][:100]}...")
                
                if enhanced_info['function_calls']:
                    for call in enhanced_info['function_calls']:
                        print(f"Function Call: {call['name']}")
                        if 'artifact_info' in call:
                            artifact_info = call['artifact_info']
                            print(f"  -> Artifact: {artifact_info['filename']} ({artifact_info['content_length']} chars)")
                
                if enhanced_info['function_responses']:
                    for response in enhanced_info['function_responses']:
                        print(f"Function Response: {response['name']} -> {response['response']}")
                
                if enhanced_info['artifact_delta']:
                    print(f"Artifact Delta: {enhanced_info['artifact_delta']}")
                
                if enhanced_info['artifacts_in_invocation']:
                    print(f"Artifacts in this invocation: {enhanced_info['artifacts_in_invocation']}")
                
                print("---")
        
        print("\n=== Final Conversation Summary ===")
        summary = artifact_consumer.get_conversation_summary()
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_improved_consumption())