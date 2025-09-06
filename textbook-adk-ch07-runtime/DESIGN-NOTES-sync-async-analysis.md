# ADK Service Sync/Async Analysis and Design Notes

## Problem Statement
The `list_artifacts` function is failing with `'coroutine' object is not iterable` error, indicating a fundamental mismatch between sync and async patterns in our PostgreSQL service integration.

## Control Flow Analysis

### CORRECTED Root Cause Analysis:
**The problem was in our agent tool function implementations, NOT in ToolContext.**

### Current Flow (WAS BROKEN, NOW FIXED):
1. **Agent Tool** (`postgres_chat_agent/agent.py:196`):
   ```python
   # BEFORE (BROKEN):
   def list_artifacts(tool_context: ToolContext, filter: str = "all") -> dict[str, Any]:
       artifacts = tool_context.list_artifacts()  # ❌ SYNC call to ASYNC method
       for a in artifacts:  # ❌ ERROR: artifacts is a coroutine, not iterable
   
   # AFTER (FIXED):
   async def list_artifacts(tool_context: ToolContext, filter: str = "all") -> dict[str, Any]:
       artifacts = await tool_context.list_artifacts()  # ✅ ASYNC call with await
       for a in artifacts:  # ✅ artifacts is now a list[str]
   ```

2. **ToolContext** (ADK internal - WAS ALWAYS CORRECT):
   ```python
   async def list_artifacts(self) -> list[str]:
       return await self._invocation_context.artifact_service.list_artifact_keys(...)
   ```

3. **Our PostgreSQL Artifact Service** (WAS ALWAYS CORRECT):
   ```python
   async def list_artifact_keys(
       self, *, app_name: str, user_id: str, session_id: str
   ) -> list[str]:  # ASYNC method returning list[str]
   ```

### Root Cause: Agent Tool Functions Were Sync Instead of Async
- **ADK Base Services**: Correctly async ✅
- **ToolContext**: Correctly async ✅  
- **Agent Tools**: Were incorrectly sync ❌ (now fixed to async ✅)
- **Our Services**: Always correctly async ✅

## ADK Service Specification Compliance

### BaseArtifactService (from ADK docs)
```python
async def list_artifact_keys(self, *, app_name: str, user_id: str, session_id: str) -> List[str]
```
✅ **Our implementation COMPLIES** with the async specification

### BaseSessionService (from ADK docs) 
```python
async def create_session(self, *, app_name: str, user_id: str, ...) -> Session
async def get_session(self, *, app_name: str, user_id: str, session_id: str, ...) -> Optional[Session]  
async def list_sessions(self, *, app_name: str, user_id: str) -> ListSessionsResponse
async def delete_session(self, *, app_name: str, user_id: str, session_id: str) -> None
```
✅ **Our implementation COMPLIES** with the async specification

### BaseMemoryService (from ADK docs)
```python
async def add_session_to_memory(self, ...) -> None
async def search_memory(self, ...) -> SearchMemoryResponse  
```
✅ **Our implementation COMPLIES** with the async specification

## Architectural Issues Identified

### 1. ToolContext Adaptation Layer Missing
- ADK's ToolContext is supposed to bridge sync tool functions with async services
- The ToolContext should handle awaiting async service calls
- Our services are correctly async, but the ToolContext adaptation is broken

### 2. Agent Tool Function Signatures
- Agent tools are defined as sync functions: `def list_artifacts(...) -> dict`
- They expect sync results from `tool_context.list_artifacts()`
- But the underlying service methods are correctly async

### 3. Service Integration Pattern
- Our services implement ADK base classes correctly (async)
- The Runner integration is correct (async services passed to Runner)
- The break occurs at the ToolContext → Agent tool boundary

## Coherent Policy Recommendations

### Policy 1: Maintain ADK Compliance (RECOMMENDED)
- **Keep our services async** (they comply with ADK 1.0.0 spec)
- **Fix ToolContext integration** to properly await async calls
- **Agent tools remain sync** (as designed by ADK)

**Advantages:**
- Full ADK specification compliance
- Future-proof for ADK updates  
- Proper async performance benefits
- Clean separation of concerns

**Implementation:**
1. Verify ToolContext properly awaits our async service methods
2. If ToolContext is broken, create adapter wrapper
3. Keep all service methods async

### Policy 2: Sync Service Wrapper (NOT RECOMMENDED)
- Create sync wrapper methods that block on async calls
- Convert async services to sync versions

**Disadvantages:**
- Violates ADK specification
- Poor performance (blocking I/O)
- Technical debt and maintenance issues
- May break future ADK versions

## Next Steps

### Immediate Actions:
1. **Investigate ToolContext implementation** - Find where async services are called
2. **Create test cases** to isolate the async/sync boundary issue
3. **Fix the ToolContext integration** to properly await async service calls

### Test Strategy:
1. **Unit tests for individual services** (verify async behavior)
2. **Integration tests for ToolContext** (verify sync tool → async service flow)
3. **End-to-end tests** for agent tool functions

### Technical Debt Notes:
- Our PostgreSQL services are architecturally correct
- The issue is in the integration layer, not our service implementation
- This analysis suggests ADK's ToolContext may have a bug or incomplete async handling