def extract_description_from_event(event: dict) -> dict:
    """
    Classify an ADK SSE event and surface the main payload.

    Returns a dict like:
    {
        "type": "USER_MESSAGE" | "STREAMING_TEXT_CHUNK" | "COMPLETE_TEXT"
                | "TOOL_CALL" | "TOOL_RESULT" | "ARTIFACT_CREATION_CALL" 
                | "ARTIFACT_CREATION_RESPONSE" | "ARTIFACT_UPDATE"
                | "STATE_OR_ARTIFACT_UPDATE" | "CONTROL_SIGNAL"
                | "ERROR" | "OTHER",
        "author": str | None,
        "text": str | None,                  # concatenated text from content.parts (if any)
        "partial": bool,                     # streaming chunk hint
        "function_calls": list | None,       # enhanced function calls with artifact details
        "function_responses": list | None,   # enhanced function responses with artifact details
        "state_delta": dict | None,
        "artifact_delta": dict | None,
        "artifact_details": dict | None,     # detailed artifact information from function calls
        "control": {                         # control / orchestration signals (may be empty)
            "transfer_to_agent": any | None,
            "escalate": any | None,
            "skip_summarization": any | None,
            "requested_auth_configs": any | None,
        },
        "long_running_tool_ids": list | None,
        "error": str | None,                 # synthesized error string if present
        "raw": dict                          # original event for fallback uses
    }
    """
    author = event.get("author")
    actions = event.get("actions") or {}
    content = event.get("content") or {}

    # Extract text from content.parts (ADK default)
    text_parts = []
    parts = content.get("parts") if isinstance(content, dict) else None
    if isinstance(parts, list):
        for p in parts:
            if isinstance(p, dict):
                # common shape: {"text": "..."}; tolerate {"type": "text", "text": "..."}
                if "text" in p and isinstance(p["text"], str):
                    text_parts.append(p["text"])
    # Sometimes content itself can be a string
    if not text_parts and isinstance(content, str):
        text_parts.append(content)

    text = "".join(text_parts) if text_parts else None

    # Partial flag can be at top-level or under content
    partial = bool(event.get("partial") or (isinstance(content, dict) and content.get("partial")))

    # Tool/function calls & responses (ADK uses "function_*"; some samples use "tool_*")
    # Also extract from content.parts for newer ADK format
    function_calls = actions.get("function_calls") or actions.get("tool_calls")
    function_responses = actions.get("function_responses") or actions.get("tool_responses")
    
    # Enhanced function call extraction from content.parts
    if not function_calls and isinstance(content, dict):
        parts = content.get("parts") or []
        extracted_calls = []
        for part in parts:
            if isinstance(part, dict) and "functionCall" in part:
                func_call = part["functionCall"]
                extracted_calls.append({
                    "id": func_call.get("id"),
                    "name": func_call.get("name"),
                    "args": func_call.get("args", {}),
                })
        function_calls = extracted_calls if extracted_calls else None
    
    # Enhanced function response extraction from content.parts
    if not function_responses and isinstance(content, dict):
        parts = content.get("parts") or []
        extracted_responses = []
        for part in parts:
            if isinstance(part, dict) and "functionResponse" in part:
                func_response = part["functionResponse"]
                extracted_responses.append({
                    "id": func_response.get("id"),
                    "name": func_response.get("name"),
                    "response": func_response.get("response", {}),
                })
        function_responses = extracted_responses if extracted_responses else None

    # State / artifact deltas
    state_delta = actions.get("state_delta") or None
    artifact_delta = actions.get("artifact_delta") or None
    
    # Extract detailed artifact information from function calls
    artifact_details = None
    if function_calls:
        for call in function_calls:
            if call.get("name") in ["save_text_artifact", "save_artifact", "create_artifact"]:
                args = call.get("args", {})
                artifact_details = {
                    "filename": args.get("filename"),
                    "content": args.get("text") or args.get("content", ""),
                    "content_length": len(args.get("text") or args.get("content", "")),
                    "function_call_id": call.get("id"),
                    "operation": call.get("name"),
                }
                break

    # Control / orchestration signals
    control = {
        "transfer_to_agent": actions.get("transfer_to_agent"),
        "escalate": actions.get("escalate"),
        "skip_summarization": actions.get("skip_summarization"),
        "requested_auth_configs": actions.get("requested_auth_configs"),
    }
    has_control = any(v is not None for v in control.values())

    # Long-running tool bookkeeping (optional)
    long_running_tool_ids = event.get("long_running_tool_ids") or actions.get("long_running_tool_ids") or None

    # Error hints (shape varies; normalize to a string if present)
    error_msg = None
    if isinstance(event.get("error"), str):
        error_msg = event["error"]
    elif isinstance(event.get("error_message"), str):
        error_msg = event["error_message"]
    elif event.get("error_code"):
        error_msg = f"{event.get('error_code')}: {event.get('error_message') or 'Unknown error'}"

    # ---- Classification order ----
    # 1) explicit errors
    if error_msg:
        etype = "ERROR"
    # 2) user messages
    elif author == "user":
        etype = "USER_MESSAGE"
    # 3) artifact-related tool calls
    elif function_calls:
        # Check for artifact-specific operations
        artifact_call = any(call.get("name") in ["save_text_artifact", "save_artifact", "create_artifact"] 
                           for call in function_calls if isinstance(call, dict))
        etype = "ARTIFACT_CREATION_CALL" if artifact_call else "TOOL_CALL"
    elif function_responses:
        # Check for artifact-specific responses
        artifact_response = any(resp.get("name") in ["save_text_artifact", "save_artifact", "create_artifact"]
                               for resp in function_responses if isinstance(resp, dict))
        etype = "ARTIFACT_CREATION_RESPONSE" if artifact_response else "TOOL_RESULT"
    # 4) control signals (transfer/escalate/skip_summarization/auth)
    elif has_control:
        etype = "CONTROL_SIGNAL"
    # 5) standalone artifact updates (version changes without function calls)
    elif artifact_delta and not (function_calls or function_responses):
        etype = "ARTIFACT_UPDATE"
    # 6) state/artifact only (no text/tool/control)
    elif (state_delta or artifact_delta) and not (text or function_calls or function_responses or has_control):
        etype = "STATE_OR_ARTIFACT_UPDATE"
    # 7) text streaming vs complete
    elif text and partial:
        etype = "STREAMING_TEXT_CHUNK"
    elif text:
        etype = "COMPLETE_TEXT"
    else:
        etype = "OTHER"

    return {
        "type": etype,
        "author": author,
        "text": text,
        "partial": partial,
        "function_calls": function_calls,
        "function_responses": function_responses,
        "state_delta": state_delta,
        "artifact_delta": artifact_delta,
        "artifact_details": artifact_details,
        "control": control,
        "long_running_tool_ids": long_running_tool_ids,
        "error": error_msg,
        "raw": event,
    }
