# Literature Review Adaptation - Summary

## What We Built

An academic literature review adaptation of the nudge middleware plan, translating cognitive science principles from civil litigation workflows to research agent systems.

## Core Translation

### Original (Civil Litigation) → Adapted (Literature Review)

| Civil Litigation | Literature Review |
|------------------|-------------------|
| **Goal**: Case objective (e.g., win motion) | **Research Question**: What we're trying to understand |
| **Stage**: Legal process (ECA, Discovery, Motions) | **Stage**: Research workflow (Scoping, Retrieval, Synthesis, Validation) |
| **Assumptions**: Legal strategy constraints | **Search Assumptions**: Database filters, scope decisions |
| **Open Items**: Legal unknowns | **Open Questions**: Coverage gaps, unresolved issues |
| **Next Action**: Legal task | **Next Action**: Database search, query refinement |

## Cognitive Science Foundations Preserved

### 1. Situation Awareness (Endsley 1995)

**Original Application**: Tracking legal case status
**Research Application**: Tracking literature search progress

- **Level 1 (Perception)**: Papers found, databases searched, current filters
- **Level 2 (Comprehension)**: Research question clarity, coverage gaps, assumption validity
- **Level 3 (Projection)**: Next database to search, expected results, completion estimate

### 2. Mixed-Initiative Interaction (Allen et al. 2001)

**Original Application**: Attorney-agent collaboration on legal research
**Research Application**: Researcher-agent collaboration on literature search

- **Agent Initiative**: Suggests databases based on coverage characteristics
- **Human Initiative**: Researcher defines scope, overrides suggestions
- **Negotiated Control**: Plan → Approve → Search pattern balances automation and oversight

### 3. Gulf of Evaluation (Norman 1986)

**Original Application**: Making legal agent actions transparent
**Research Application**: Making search strategy transparent

- **Turn Receipts**: Show exact query, database, results after each search
- **Grounding Panel**: Continuous display of current research state
- **Provenance Tracking**: Link each paper to the query that found it

### 4. Error Recovery (Norman 1983)

**Original Application**: Targeted help when legal research fails
**Research Application**: Targeted help when searches fail

**Failure Classifications** (adapted for research):
- **EMPTY_RESULTS** → Broaden query, try synonyms, different database
- **AMBIGUOUS_TERMINOLOGY** → Disambiguate, show competing definitions
- **DATABASE_COVERAGE_GAP** → Suggest complementary database with better coverage
- **QUERY_TOO_BROAD** → Propose specific filters, offer short-run preview
- **ACCESS_RESTRICTED** → Library access options, find open-access alternatives
- **INCONSISTENT_RESULTS** → Explain database differences, suggest validation

## Key Adaptations for Academic Research

### 1. Multi-Database Reality

**Challenge**: Academic research spans multiple databases with different coverage, terminology, and biases.

**Solution**:
- Track which databases have been searched
- Warn about coverage gaps (e.g., "ACM focuses on CS – missing clinical perspectives")
- Suggest complementary databases based on topic

### 2. Terminology Variation

**Challenge**: Different fields use different terms for same concepts (e.g., "explainable AI" vs "interpretable ML" vs "AI transparency").

**Solution**:
- Classify AMBIGUOUS_TERMINOLOGY failures
- Suggest domain-specific synonyms
- Note terminology in search assumptions

### 3. Citation Bias

**Challenge**: Relying only on highly-cited papers misses emerging work.

**Solution**:
- Track citation distribution in results
- Warn when skewed toward highly-cited papers
- Suggest supplemental search for recent low-citation work

### 4. Reproducibility Requirements

**Challenge**: Academic research must document search strategies for methods sections.

**Solution**:
- Complete audit trail via SearchReceipts
- Export function generates methods section documentation
- Timestamps enable snapshot-in-time reproducibility

### 5. Research Workflow Stages

**Adapted from legal stages**:

**SCOPING** (was: Case Assessment):
- Define research question
- Identify key concepts
- Set boundaries (dates, domains, languages)

**RETRIEVAL** (was: Discovery):
- Systematic database searches
- Query refinement based on results
- Coverage tracking

**SYNTHESIS** (was: Motion Preparation):
- Organize papers by themes
- Identify gaps and conflicts
- Build coherent narrative

**VALIDATION** (was: Trial Prep):
- Check coverage completeness
- Identify biases (citation, publication, database)
- Ensure reproducibility

## Files Created

### Core Documentation
- `README_LITREVIEW.md` - Overview and quick start
- `PLAN_LITREVIEW.md` - Detailed build plan with milestones

### Prompts (in `prompts/litreview/`)
- `grounding_updater.txt` - Instructions for updating ResearchGroundingBox
- `search_gate.txt` - Plan → Approve → Search → Recap workflow
- `search_failure_help.txt` - Targeted help for 6 failure types

### UI Specifications (in `ui/`)
- `research_grounding_panel_spec.md` - Complete UX specification for grounding panel

### Examples (in `examples/litreview/`)
- `scenario_walkthrough.md` - Realistic PhD student literature review session
- `adk_integration_example.py` - Python code showing ADK integration patterns

## Integration with ADK Textbook

### Chapter 2: Paper Finder Agent
**Before**: Simple multi-database search agent
**With Middleware**:
- Grounding box tracks search progress
- Search gates prevent wasted effort
- Failure classification provides targeted help
- Complete audit trail for reproducibility

### Chapter 6: ADK Runtime
**Integration Points**:
- Store ResearchGroundingBox in session state
- Use EventActions.state_delta to update grounding
- Server-sent events for live panel updates
- UI Contract compliance for state visibility

### Chapter 7: PostgreSQL Runtime
**Persistence**:
- Store grounding state evolution in database
- Event sourcing for complete search history
- Enable multi-day research sessions
- Query audit logs for methods section

### Chapter 8: Textual UI
**User Interface**:
- Fixed header showing grounding panel
- Scrolling turn receipts log
- Interactive buttons for search gates
- Artifact tracking for found papers

## Responsible Research AI Principles

### Transparency
- **Never hide database limitations**: Note coverage gaps, bias risks
- **Always show query provenance**: Which search found which paper
- **Mark access status**: Full-text vs abstract-only vs unavailable

### Reproducibility
- **Log complete search strategy**: Every query, database, filter
- **Timestamp all searches**: Enable snapshot-in-time reproducibility
- **Document changes**: Why queries were refined, assumptions changed

### Researcher Autonomy
- **Never auto-exclude papers**: Always ask before filtering
- **Explain defaults**: Why these databases? Why these dates?
- **Provide opt-out**: Researcher can override all suggestions

### Scholarly Integrity
- **Don't overstate confidence**: "Likely relevant" not "perfect match"
- **Show conflicting evidence**: Don't hide contradictory papers
- **Note methodology limitations**: Search can't guarantee completeness
- **Respect access boundaries**: Don't promise unavailable content

## Success Metrics

### Research Efficiency
- **Time to comprehensive search**: Hours instead of days
- **Database coverage**: Systematic coverage of relevant sources
- **Query refinement cycles**: Minimal iterations to relevant results

### Researcher Confidence
- **Grounding box accuracy**: Matches researcher's mental model
- **Search strategy clarity**: Can explain approach to colleagues
- **Reproducibility**: Search can be replicated from audit log

### Research Quality
- **Coverage completeness**: Key papers found across databases
- **Bias awareness**: Researcher notices citation/database biases
- **Evidence synthesis**: Conflicting findings surfaced

## Comparison to Original Plan

| Aspect | Civil Litigation | Literature Review |
|--------|------------------|-------------------|
| **Domain** | Legal workflows | Academic research |
| **Users** | Attorneys, paralegals | Researchers, PhD students |
| **Stages** | 4 legal phases | 4 research phases |
| **State Object** | GroundingBox | ResearchGroundingBox |
| **Failure Types** | Policy blocks, missing inputs | Empty results, coverage gaps |
| **Audit Goal** | Compliance, liability | Reproducibility, methods section |
| **Key Concern** | Procedural correctness | Scientific rigor, completeness |
| **Success Metric** | Case outcome | Research quality, coverage |

## Key Insights from Adaptation

### 1. Cognitive Science Principles Transfer Well

The core principles (situation awareness, mixed-initiative, error recovery) apply across domains. The **patterns** are universal even though the **content** differs.

### 2. Domain-Specific Failure Modes Matter

While the framework is similar, the specific failure classifications needed to be completely redesigned for academic research:
- Legal: Policy blocks, privilege claims, missing evidence
- Research: Coverage gaps, terminology variation, citation bias

### 3. Workflow Stages Map Conceptually

Both domains have natural progression:
- Legal: Case assessment → Discovery → Motions → Trial
- Research: Scoping → Retrieval → Synthesis → Validation

The **structure** of "start broad, narrow down, validate" appears in both.

### 4. Audit Requirements Drive Design

- Legal: Compliance, attorney work product, discovery logs
- Research: Reproducibility, methods documentation, peer review

Both require complete audit trails but for different **purposes**.

### 5. Mixed-Initiative is Critical in Both

Neither domain wants full automation:
- Attorneys need to control legal strategy
- Researchers need to control scholarly judgment

The Plan → Approve → Act pattern provides exactly the right balance.

## Next Steps for Implementation

### Phase 1: Schemas and State (M1)
- Implement ResearchGroundingBox, SearchReceipt, SearchFailureClass
- Build in-memory store with validation
- Test with example scenarios

### Phase 2: Prompt Integration (M2)
- Inject grounding_updater, search_gate, failure_help prompts
- Test with Chapter 2 paper finder agent
- Validate grounding box updates correctly

### Phase 3: Targeted Help (M3)
- Implement failure classification logic
- Build remedy suggestion system
- Test with synthetic search failures

### Phase 4: UI Implementation (M5)
- Build console version of grounding panel
- Implement turn receipts display
- Add change highlighting (Δ prefix)

### Phase 5: ADK Integration (M7)
- Wire into Chapter 6 FastAPI runtime
- Add state persistence in Chapter 7 PostgreSQL
- Build Textual UI in Chapter 8

### Phase 6: Evaluation
- Test with real PhD student literature reviews
- Measure efficiency gains vs manual search
- Validate reproducibility from audit logs
- Assess researcher satisfaction and trust

## References

### Cognitive Science Foundations

**Endsley, M. R. (1995)**. Toward a theory of situation awareness in dynamic systems. *Human Factors*, 37(1), 32-64.
- Theory of situation awareness (perception, comprehension, projection)

**Allen, J. F., Byron, D. K., Dzikovska, M., Ferguson, G., Galescu, L., & Stent, A. (2001)**. Toward conversational human-computer interaction. *AI Magazine*, 22(4), 27-37.
- Mixed-initiative interaction in dialogue systems

**Norman, D. A. (1986)**. Cognitive engineering. In *User centered system design* (pp. 31-61).
- Gulf of execution and evaluation, design principles

**Norman, D. A. (1983)**. Design rules based on analyses of human error. *Communications of the ACM*, 26(4), 254-258.
- Error classification and recovery strategies

### Explainability and Transparency

**Ribeiro, M. T., Singh, S., & Guestrin, C. (2016)**. "Why should I trust you?" Explaining the predictions of any classifier. In *Proceedings of KDD* (pp. 1135-1144).
- LIME and model interpretability

### Academic Research Methods

**Webster, J., & Watson, R. T. (2002)**. Analyzing the past to prepare for the future: Writing a literature review. *MIS Quarterly*, 26(2), xiii-xxiii.
- Systematic literature review methodology

**Kitchenham, B. (2004)**. Procedures for performing systematic reviews. *Keele University Technical Report*, 33(2004), 1-26.
- Systematic review protocols for software engineering

## Conclusion

This adaptation demonstrates that **cognitive science principles for responsible AI workflow management transfer effectively across domains** when:

1. **Core patterns preserved**: Situation awareness, mixed-initiative, error recovery
2. **Domain specifics adapted**: Failure modes, terminology, workflow stages
3. **User needs centered**: Researcher autonomy, scholarly integrity, reproducibility
4. **Transparency maintained**: Complete audit trails, provenance tracking

The result is a **research agent middleware** that makes literature review faster, more systematic, and more reproducible while keeping researchers in control of scholarly judgment.
