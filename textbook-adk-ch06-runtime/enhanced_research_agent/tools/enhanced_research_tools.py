"""
This file previously contained incorrectly implemented EventActions.state_delta tools.

The original implementation was wrong because:
1. It used EventActions.state_delta within tool contexts 
2. It manually created events within tools
3. This is NOT "The Standard Way" from ADK documentation

"The Standard Way" actually means:
- Manual event creation using session_service.append_event()
- Direct session manipulation without agent execution
- System-level state updates outside of tool contexts

See the standalone demo script for the correct implementation.
"""

# This file is intentionally empty to show the removal of incorrect patterns