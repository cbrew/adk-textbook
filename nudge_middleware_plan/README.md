# Conversational Grounding & Targeted Help Middleware (Plan Bundle)

This bundle packages a **practical plan + prompt templates + schemas** to build an LLM middleware that:
- Maintains a live **Grounding Box** (Goal • Stage • Assumptions • Open Items • Next Action)
- Enforces **Plan → OK? → Act → Recap** mixed‑initiative gates
- Provides **Targeted Help** on breakdowns with ready-to-click recovery actions
- Shows **confidence + provenance** together
- Logs **turn receipts** and **state deltas** for auditability

Designed to be consumed by a **code assistant** (e.g., Copilot/ChatGPT) and wired into *any* agent framework (OpenAI, LangGraph, ADK, Burr, custom).

## Contents
- `PLAN.md` — stepwise build plan with milestones and acceptance criteria
- `prompts/` — copy‑ready prompt blocks (generic + civil‑litigation tuned)
- `schemas/` — JSON Schemas for GroundingBox, TurnReceipt, ErrorClass, ConsentLog
- `examples/` — framework-agnostic pseudocode & minimal Python glue
- `ui/` — UX spec for a compact Grounding Panel and receipts
- `ops/` — observability/telemetry events and redlines for responsible use
- `checklist.md` — day‑1 to day‑10 implementation checklist

## Quick start
1) Read `PLAN.md` and pick your framework integration path.
2) Drop the prompts from `prompts/` into your system/developer messages.
3) Validate your state with `schemas/`. Emit `TurnReceipt` after each tool call.
4) Render `ui/grounding_panel_spec.md` in your app shell or console.
5) Track events per `ops/telemetry_events.md`.

