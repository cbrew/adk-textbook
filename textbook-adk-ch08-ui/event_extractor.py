def extract_description_from_event(event: dict) -> dict:
    """
    Classify an ADK SSE event and surface the main payload.

    Returns a dict like:
    {
        "type": "USER_MESSAGE" | "STREAMING_TEXT_CHUNK" | "COMPLETE_TEXT"
                | "TOOL_CALL" | "TOOL_RESULT"
                | "STATE_OR_ARTIFACT_UPDATE" | "CONTROL_SIGNAL"
                | "ERROR" | "OTHER",
        "author": str | None,
        "text": str | None,                  # concatenated text from content.parts (if any)
        "partial": bool,                     # streaming chunk hint
        "function_calls": list | None,       # actions.function_calls / tool_calls
        "function_responses": list | None,   # actions.function_responses / tool_responses
        "state_delta": dict | None,
        "artifact_delta": dict | None,
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
    function_calls = actions.get("function_calls") or actions.get("tool_calls") or None
    function_responses = actions.get("function_responses") or actions.get("tool_responses") or None

    # State / artifact deltas
    state_delta = actions.get("state_delta") or None
    artifact_delta = actions.get("artifact_delta") or None

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
    # 3) tool-related
    elif function_calls:
        etype = "TOOL_CALL"
    elif function_responses:
        etype = "TOOL_RESULT"
    # 4) control signals (transfer/escalate/skip_summarization/auth)
    elif has_control:
        etype = "CONTROL_SIGNAL"
    # 5) state/artifact only (no text/tool/control)
    elif (state_delta or artifact_delta) and not (text or function_calls or function_responses or has_control):
        etype = "STATE_OR_ARTIFACT_UPDATE"
    # 6) text streaming vs complete
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
        "control": control,
        "long_running_tool_ids": long_running_tool_ids,
        "error": error_msg,
        "raw": event,
    }
