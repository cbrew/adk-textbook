# Literature Review Grounding & Research Workflow Middleware

This bundle adapts the **Conversational Grounding & Targeted Help** middleware for **academic literature review workflows**, applying cognitive science principles to research agent systems.

## Core Design Principles

Built on cognitive science research about:
- **Situation awareness** (Endsley 1995): Maintaining accurate mental models during complex tasks
- **Mixed-initiative interaction** (Allen et al. 2001): Balanced human-AI control sharing
- **Error recovery** (Norman 1983): Providing actionable remedies at breakdown points
- **Transparency in AI systems** (Ribeiro et al. 2016): Explainability through provenance and confidence

## What It Does

Maintains a live **Research Grounding Box** showing:
- **Research Question**: What are we trying to understand?
- **Search Stage**: Where are we in the review process? (scoping → retrieval → synthesis → validation)
- **Search Assumptions**: What constraints/filters are active?
- **Open Questions**: What remains unclear or needs investigation?
- **Next Action**: What database/query/analysis comes next?

Enforces **Plan → OK? → Search → Recap** workflow with:
- **Targeted Help** when searches fail or return unexpected results
- **Confidence + Provenance** for each paper recommendation
- **Turn Receipts** showing what changed (papers found, filters applied, questions resolved)
- **Audit Logs** for research reproducibility

## Academic Research Context

Unlike the civil litigation example, this adaptation addresses:
- **Search space exploration**: Multiple databases with different coverage and biases
- **Query formulation challenges**: Balancing precision/recall, handling terminology variation
- **Evidence synthesis**: Building coherent narratives from diverse sources
- **Bias awareness**: Understanding database coverage gaps and citation biases
- **Research reproducibility**: Documenting search strategies for methods sections

## Contents

- `PLAN_LITREVIEW.md` — Stepwise build plan for academic research workflows
- `prompts/litreview/` — Research-specific prompt blocks
- `schemas/` — JSON Schemas for ResearchGroundingBox, SearchReceipt, SearchFailureClass
- `examples/litreview/` — Academic research workflow examples
- `ui/research_grounding_panel_spec.md` — Compact Research Grounding Panel UX
- `ops/` — Telemetry events for research workflow monitoring

## Quick Start

1) Read `PLAN_LITREVIEW.md` for academic workflow integration
2) Use prompts from `prompts/litreview/` in your research agent
3) Emit `SearchReceipt` after each database query
4) Render `ui/research_grounding_panel_spec.md` in your research UI
5) Track research workflow events per `ops/telemetry_events.md`

## Research Workflow Stages

1. **Scoping**: Define research question, identify key concepts, set boundaries
2. **Retrieval**: Query multiple databases with evolving search strategies
3. **Synthesis**: Organize papers by themes, identify gaps, build narrative
4. **Validation**: Check coverage, identify biases, ensure reproducibility

## Example: Grounding Box During Literature Review

```
Research Question: What are the current approaches to explainable AI in healthcare?
Stage: Retrieval (3/5 databases searched)
Assumptions:
  • Focusing on papers from 2020-present
  • Excluding purely theoretical work without applications
Open Questions:
  • Are we missing key European research (check non-English sources)?
  • Should we expand to adjacent fields (biomedical informatics)?
Next Action: Agent → search ACM Digital Library for HCI perspectives by today 5pm
```

## Integration with ADK Textbook

This middleware complements:
- **Chapter 2**: Paper finder agent gains grounding and mixed-initiative control
- **Chapter 6**: ADK runtime adds state visibility for research workflow tracking
- **Chapter 7**: PostgreSQL runtime persists search history and grounding state
- **Chapter 8**: Custom UI displays Research Grounding Panel with artifact tracking

## Responsible Research AI Principles

- **Never hide search limitations**: Show database coverage gaps and biases
- **Always show provenance**: Link papers to exact queries that found them
- **Mark unverified claims**: Flag papers not yet accessed or read in full
- **Log search strategies**: Enable reproducible research methods sections
- **Warn about citation bias**: Note when relying heavily on highly-cited papers only
