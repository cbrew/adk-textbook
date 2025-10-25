# Build Plan (for Code Assistant Execution)

## Goals
- Keep the **state of play** visible and accurate across multi-stage LLM workflows.
- Reduce user confusion using **Targeted Help**, **Grounding**, and **Mixed‑Initiative gating**.
- Produce auditable **receipts** and **consent logs** with minimal developer friction.

## Non-Goals
- Building a full agent framework.
- Tying to a single vendor’s SDK. Provide adapters instead.

---

## Architecture (high level)

```
User ↔ UI Shell
      ↓↑
 Grounding Panel (read-only view of state)
      ↓
 Middleware (this project)
   ├─ GroundingState Store (validated via JSON Schemas)
   ├─ Gatekeeper (Plan→OK?→Act→Recap)
   ├─ Targeted Help Router (on breakdowns)
   ├─ Confidence+Provenance Decorator
   └─ Telemetry (TurnReceipt/ConsentLog/ErrorClass)
      ↓
 Agent/Orchestrator (your framework)
      ↓
 Tools / Retrieval / Actions
```

### State objects
- `GroundingBox`: goal, stage, assumptions, open_items, next_action, progress
- `TurnReceipt`: what changed, what’s next, duration, tool_calls, warnings
- `ConsentLog`: defaults offered, auto-actions, timeboxed runs, user decision
- `ErrorClass`: enum with remedy mapping

---

## Milestones & Acceptance Criteria

### M1: Schemas + In-memory store (1–2 days)
- Implement JSON Schemas in `schemas/`
- Build a simple in-memory store with `validate(obj, schema)`
- **Accept**: Sample events under `examples/` validate without error

### M2: Prompt injection (Grounding + Gatekeeper) (1–2 days)
- Add `prompts/grounding_updater.txt` after each step
- Add `prompts/plan_gate.txt` before tool calls
- **Accept**: Demo script emits correct `TurnReceipt` and updates `GroundingBox`

### M3: Targeted Help (1 day)
- Implement `error_classify()` and `suggest_remedy()`
- **Accept**: Given synthetic failures, returns 1 primary and 1 fallback action

### M4: Confidence + Provenance decorator (1 day)
- Decorate answers with `confidence_explainer` and `provenance_list`
- **Accept**: Demo shows both together; sources are inspectable via a single action

### M5: UI Grounding Panel (1 day)
- Render `Goal • Stage • Assumptions • Open • Next` in console or web stub
- **Accept**: After each step, panel updates; deltas prefixed with `Δ`

### M6: Telemetry + Consent (1 day)
- Emit events per `ops/telemetry_events.md`
- **Accept**: NDJSON log file contains receipts/consents matched to steps

### M7: Civil-Litigation presets (1 day)
- Wire `prompts/civil_*` defaults into a profile toggle
- **Accept**: ECA/Motions/Discovery stages produce tailored artifacts

---

## Integration paths

### Path A: Function wrappers
- Wrap your tool calls with `with_plan_gate(plan, act_fn)`
- After `act_fn`, call `update_grounding_box(delta)` and `emit_receipt(...)`

### Path B: Custom agent step
- Insert a “Gatekeeper” node between planner and tools
- Node enforces approval, short-run option, and emits receipts

### Path C: Middleware HTTP shim
- POST `/plan` to stage plan; require `/ok` to proceed; POST `/recap` after
- Works across languages and frameworks

---

## Failure modes & remedies
- **Missing input** → Ask for the one blocking field; propose a placeholder + small scope
- **Ambiguous instruction** → Offer 2 interpretations with example continuations
- **Policy blocked** → Show allowed alternatives with rationale
- **Retrieval empty** → Narrow scope or switch source; run short-run search
- **Hallucination risk** → Reduce claim strength; surface uncertainty; require cite check

---

## Security & Ethics redlines
- Never hide defaults; always show opt-out
- Never use social proof on sensitive decisions
- Mark any unverified authority with “Check citator”
- Log consent for auto-advance/timeboxed runs
