# Chapter 7 Development Notes

## Important Implementation Notes

### ADK Tool Context Documentation Needed

**Important**: The textbook needs to carefully explain ADK tool context usage. Refer to the official ADK documentation on context: https://google.github.io/adk-docs/context/

Key points to cover in the textbook:

1. **ToolContext Parameter Pattern**: 
   - Tools can include `tool_context: ToolContext` parameter for accessing session state, artifacts, etc.
   - The parameter should NOT be documented in the tool's docstring
   - ADK automatically injects ToolContext after LLM decides to call the tool

2. **Required Parameters for Tools**:
   - **Critical Bug**: Tools with no parameters cause `AttributeError: 'NoneType' object has no attribute 'required'`
   - **Solution**: All ADK tools must have at least one parameter, even if it has a default value
   - Example: `def save_to_memory(note: str = "current conversation") -> Dict[str, any]:`

3. **Proper Tool Signatures**:
   - Use `Dict[str, any]` return type annotation (not just `dict`)
   - Import from `typing`: `from typing import Dict`
   - Use `Agent` class (not `LlmAgent` in some contexts)

### Working Tool Pattern

```python
from typing import Dict
from google.adk.agents import Agent

def my_tool(param: str = "default") -> Dict[str, any]:
    """
    Tool description.
    
    Args:
        param: Description (don't document tool_context if used)
        
    Returns:
        Dictionary with results
    """
    return {"result": "success", "param": param}
```

### PostgreSQL Service Integration

The proper approach for Chapter 7 is to wire PostgreSQL services into ADK's Runner infrastructure:

```python
from google.adk.runners import Runner

# Get custom service implementations
session_service = runtime.get_session_service()
memory_service = runtime.get_memory_service()
artifact_service = runtime.get_artifact_service()

# Wire into ADK Runner (replaces defaults)
runner = Runner(
    agent=agent,
    session_service=session_service,
    memory_service=memory_service,
    artifact_service=artifact_service,
)
```

This demonstrates building **custom ADK runtimes** rather than just adding tools.

## Status

✅ Fixed tool parameter validation error  
✅ Implemented working postgres_chat_agent  
✅ Documented proper service integration pattern  
📝 Need to update textbook with context usage guidelines