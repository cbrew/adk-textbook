# Nudge Middleware Plan - Complete Index

## Overview

This directory contains **two complete implementations** of the nudge middleware concept:

1. **Original**: Civil litigation workflows (attorneys, legal research)
2. **Literature Review**: Academic research workflows (researchers, systematic search)

Both share the same **cognitive science foundations** but adapt them to different domain needs.

---

## Quick Navigation

### Starting Points

**New to the concept?**
→ Start with `README.md` (civil litigation) or `README_LITREVIEW.md` (academic research)

**Want to implement it?**
→ Go to `PLAN.md` (civil litigation) or `PLAN_LITREVIEW.md` (academic research)

**Want to see it in action?**
→ Read `examples/litreview/scenario_walkthrough.md` (realistic PhD student literature review)

**Want code examples?**
→ See `examples/litreview/adk_integration_example.py` (Python integration patterns)

**Want to understand the adaptation?**
→ Read `SUMMARY_LITREVIEW_ADAPTATION.md` (how we translated principles across domains)

---

## File Structure

```
nudge_middleware_plan/
├── README.md                          # Original: Civil litigation overview
├── README_LITREVIEW.md                # ⭐ Academic research overview
├── PLAN.md                            # Original: Build plan
├── PLAN_LITREVIEW.md                  # ⭐ Academic research build plan
├── SUMMARY_LITREVIEW_ADAPTATION.md    # ⭐ Translation guide
├── checklist.md                       # Original: Implementation checklist
├── checklist_litreview.md             # ⭐ Academic research checklist
├── INDEX.md                           # This file
│
├── prompts/
│   ├── (original civil litigation prompts)
│   └── litreview/                     # ⭐ Academic research prompts
│       ├── grounding_updater.txt      # Update ResearchGroundingBox
│       ├── search_gate.txt            # Plan → Approve → Search workflow
│       └── search_failure_help.txt    # Targeted help for search failures
│
├── schemas/
│   └── (JSON schemas - shared concepts, different fields)
│
├── ui/
│   ├── grounding_panel_spec.md        # Original: Legal grounding panel
│   └── research_grounding_panel_spec.md  # ⭐ Academic grounding panel
│
├── examples/
│   ├── glue.md                        # Original: Framework-agnostic glue
│   └── litreview/                     # ⭐ Academic research examples
│       ├── scenario_walkthrough.md    # PhD student lit review session
│       └── adk_integration_example.py # Python integration code
│
└── ops/
    └── telemetry_events.md            # Shared: Observability patterns
```

⭐ = **Literature review specific files**

---

## Concept Comparison

| Aspect | Civil Litigation | Literature Review |
|--------|------------------|-------------------|
| **Domain** | Legal workflows | Academic research |
| **Primary User** | Attorneys, paralegals | Researchers, PhD students |
| **Goal Tracking** | Case objective (win motion, etc.) | Research question |
| **Workflow Stages** | ECA → Discovery → Motions → Trial | Scoping → Retrieval → Synthesis → Validation |
| **State Object** | GroundingBox | ResearchGroundingBox |
| **Key Failures** | Policy blocks, missing evidence | Coverage gaps, citation bias |
| **Audit Purpose** | Compliance, liability protection | Reproducibility, peer review |
| **Success Metric** | Legal outcome, efficiency | Research quality, completeness |

---

## Cognitive Science Foundations (Shared)

Both implementations build on the same research:

### 1. Situation Awareness (Endsley 1995)

**Level 1 (Perception)**: Current state
- Civil: Documents reviewed, depositions scheduled
- Research: Papers found, databases searched

**Level 2 (Comprehension)**: Understanding
- Civil: Case strategy, legal risks
- Research: Coverage gaps, terminology issues

**Level 3 (Projection)**: Future state
- Civil: Next legal action, deadlines
- Research: Next database, expected results

### 2. Mixed-Initiative Interaction (Allen et al. 2001)

**Balanced Control**:
- Agent proposes based on expertise (database coverage, legal procedures)
- Human decides based on domain knowledge (relevance, strategy)
- Negotiated through Plan → Approve → Act pattern

### 3. Gulf of Evaluation (Norman 1986)

**Making Internal State Visible**:
- Grounding panel shows current state continuously
- Turn receipts explain what changed and why
- Provenance links actions to outcomes

### 4. Error Recovery (Norman 1983)

**Targeted Help, Not Generic Errors**:
- Classify failure based on symptoms
- Provide specific remedies based on type
- Offer primary action + fallback + ask human

---

## When to Use Which Version

### Use Civil Litigation Version If:
- Building legal tech, compliance systems
- Users are attorneys, paralegals, legal researchers
- Workflow has regulatory/procedural requirements
- Audit trail needed for liability protection
- Multiple parties with different permissions

### Use Literature Review Version If:
- Building academic research tools
- Users are researchers, PhD students, librarians
- Workflow involves multi-database search
- Audit trail needed for reproducibility
- Need to document methodology for publications

### Adapt for Your Domain If:
- Neither domain matches exactly
- Read `SUMMARY_LITREVIEW_ADAPTATION.md` to see how we translated
- Core pattern: Goal → Stages → Assumptions → Open Items → Next Action
- Customize failure classifications for your domain
- Keep cognitive science principles intact

---

## Implementation Paths

### Path 1: Start from Scratch
1. Pick your domain (legal, research, or custom)
2. Follow appropriate build plan (`PLAN.md` or `PLAN_LITREVIEW.md`)
3. Use appropriate checklist
4. Adapt prompts to your needs
5. Build UI based on spec

### Path 2: Integrate with Existing Agent
1. Review `examples/litreview/adk_integration_example.py`
2. Wrap your existing tools with grounding middleware
3. Add state store to track grounding box
4. Inject prompts into system messages
5. Add UI panel for state visibility

### Path 3: Framework-Specific
1. Review `examples/glue.md` for framework-agnostic patterns
2. Adapt to your framework (OpenAI, LangGraph, custom)
3. Use function wrappers (easy) or custom nodes (more control)
4. Focus on state management patterns

---

## Integration with ADK Textbook

Both versions integrate with the textbook chapters:

### Chapter 2: Python Agents with Tools
**What**: Paper finder agent with database search tools
**Integration**:
- Wrap search tools with grounding middleware
- Add ResearchGroundingBox tracking
- Emit SearchReceipts for audit trail

### Chapter 6: ADK Runtime Fundamentals
**What**: FastAPI server with UI Contract compliance
**Integration**:
- Store grounding state in session state
- Use EventActions.state_delta for updates
- Server-sent events for live panel updates

### Chapter 7: PostgreSQL Runtime
**What**: Custom runtime with database persistence
**Integration**:
- Persist grounding state in PostgreSQL
- Store search history as events
- Enable multi-day research sessions

### Chapter 8: Textual UI
**What**: Custom user interface with Textual framework
**Integration**:
- Grounding panel as fixed header widget
- Scrolling turn receipts view
- Interactive buttons for search gates

---

## Key Files by Use Case

### "I want to understand the concept"
1. `README_LITREVIEW.md` - Academic research overview
2. `examples/litreview/scenario_walkthrough.md` - Realistic session
3. `SUMMARY_LITREVIEW_ADAPTATION.md` - How it was adapted

### "I want to build it"
1. `PLAN_LITREVIEW.md` - Detailed build plan
2. `checklist_litreview.md` - Day-by-day implementation
3. `examples/litreview/adk_integration_example.py` - Code patterns

### "I want to customize the UI"
1. `ui/research_grounding_panel_spec.md` - Complete UX spec
2. `prompts/litreview/grounding_updater.txt` - State update logic
3. `prompts/litreview/search_gate.txt` - Approval workflow

### "I want to handle errors better"
1. `prompts/litreview/search_failure_help.txt` - 6 failure types + remedies
2. `examples/litreview/adk_integration_example.py` - Classification code
3. `PLAN_LITREVIEW.md` - Failure modes section

### "I want to adapt it to my domain"
1. `SUMMARY_LITREVIEW_ADAPTATION.md` - Translation process
2. `PLAN_LITREVIEW.md` - Architecture and patterns
3. `prompts/litreview/` - Template for domain-specific prompts

---

## Milestones (Literature Review Version)

### M1: Schemas + Store (1-2 days)
**Goal**: Data structures and state management
**Acceptance**: Example scenarios validate correctly

### M2: Prompt Integration (2 days)
**Goal**: Grounding updates and search gates working
**Acceptance**: Agent maintains grounding box accurately

### M3: Targeted Help (1 day)
**Goal**: Failure classification and remedies
**Acceptance**: Each failure type returns actionable remedies

### M4: Confidence + Provenance (1 day)
**Goal**: Paper recommendations with sources
**Acceptance**: Can trace paper → query → database

### M5: UI Panel (1 day)
**Goal**: Visual grounding panel
**Acceptance**: Panel updates after each search with Δ highlighting

### M6: Telemetry + Audit (1 day)
**Goal**: Complete search strategy logging
**Acceptance**: Export produces methods section documentation

### M7: Research Presets (1 day)
**Goal**: Stage-specific behavior
**Acceptance**: Agent adapts to scoping/retrieval/synthesis/validation

---

## Success Metrics

### Research Efficiency
- ✅ Time to comprehensive search: Hours not days
- ✅ Database coverage: Systematic, not ad-hoc
- ✅ Query refinement: Minimal wasted searches

### Researcher Confidence
- ✅ Grounding box matches mental model
- ✅ Search strategy explainable to colleagues
- ✅ Reproducible from audit log

### Research Quality
- ✅ Key papers found across databases
- ✅ Coverage gaps identified
- ✅ Biases (citation, database) noted
- ✅ Conflicting evidence surfaced

### Cognitive Science Validation
- ✅ Situation awareness maintained throughout
- ✅ Mixed-initiative control balanced correctly
- ✅ Gulf of evaluation bridged
- ✅ Error recovery effective with targeted help

---

## Responsible AI Principles

### Transparency
- Never hide limitations (database coverage, access restrictions)
- Always show provenance (query → database → paper)
- Mark unverified information clearly

### Reproducibility
- Log complete search strategy
- Timestamp all actions
- Document assumption changes
- Export ready for methods section

### User Autonomy
- Never auto-exclude without asking
- Explain all defaults
- Provide opt-out for all suggestions
- No hidden ranking/filtering

### Domain Integrity
- **Legal**: Don't overstate legal conclusions, note limitations
- **Research**: Don't overstate confidence, show conflicting evidence

---

## Next Steps

### If You're Building the Literature Review Version:
1. Start with `PLAN_LITREVIEW.md`
2. Follow `checklist_litreview.md`
3. Use `examples/litreview/adk_integration_example.py` as template
4. Test with `examples/litreview/scenario_walkthrough.md` scenarios

### If You're Adapting to a New Domain:
1. Read `SUMMARY_LITREVIEW_ADAPTATION.md` for translation process
2. Map your domain to core pattern:
   - What's the "goal"?
   - What are the "stages"?
   - What are common "failure modes"?
   - What "assumptions" need tracking?
   - What "next actions" are typical?
3. Customize prompts in `prompts/` directory
4. Adapt UI spec in `ui/` directory
5. Keep cognitive science principles intact

### If You're Evaluating the Concept:
1. Read realistic scenario: `examples/litreview/scenario_walkthrough.md`
2. Review cognitive science foundations in `SUMMARY_LITREVIEW_ADAPTATION.md`
3. Check responsible AI principles above
4. Consider: Does this balance automation and human control effectively?

---

## References

### Cognitive Science Papers
- **Endsley, M. R. (1995)**. Situation awareness in dynamic systems. *Human Factors*.
- **Allen, J. F., et al. (2001)**. Toward conversational HCI. *AI Magazine*.
- **Norman, D. A. (1986)**. Cognitive engineering. *User Centered System Design*.
- **Norman, D. A. (1983)**. Design rules based on analyses of human error. *CACM*.

### Research Methods
- **Webster & Watson (2002)**. Writing a literature review. *MIS Quarterly*.
- **Kitchenham (2004)**. Systematic reviews. *Keele University Technical Report*.

### AI Transparency
- **Ribeiro, et al. (2016)**. "Why should I trust you?" *KDD*.

---

## Contributing

Suggestions for improvements:
1. Additional domain adaptations
2. Failure mode classifications for new domains
3. UI improvements
4. Integration examples for other frameworks
5. Evaluation results with real users

---

## License & Attribution

This work adapts cognitive science research for AI agent middleware design. Original cognitive science papers cited throughout. Implementation patterns are framework-agnostic and adaptable to various domains.

---

**Questions? Start with the appropriate README file for your domain.**
