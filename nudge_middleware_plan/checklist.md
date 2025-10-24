# Implementation Checklist

- [ ] Wire `plan_gate.txt` before any tool call
- [ ] Add `grounding_updater.txt` after every step
- [ ] Validate `GroundingBox` against schema on every update
- [ ] Emit `TurnReceipt` after every tool call
- [ ] Implement `error_classify()` → `suggest_remedy()` and connect to failures
- [ ] Decorate responses with confidence + provenance together
- [ ] Render `ui/grounding_panel_spec.md` in shell or web
- [ ] Enable **civil-litigation profile** (ECA, Motions, Discovery prompts)
- [ ] Add NDJSON logging with timestamps (UTC)
- [ ] Add unit tests for schema validation + failure routing
