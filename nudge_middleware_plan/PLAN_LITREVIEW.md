# Build Plan: Literature Review Grounding Middleware

## Goals
- Maintain **research situation awareness** across multi-database literature searches
- Reduce researcher confusion through **Search Grounding**, **Targeted Search Help**, and **Mixed-Initiative Query Control**
- Produce **reproducible search strategies** with auditable receipts and provenance trails
- Apply cognitive science principles to academic research agent workflows

## Non-Goals
- Building a complete literature review system (focus on the grounding/control middleware)
- Replacing existing academic search UIs (provide augmentation patterns instead)
- Automating scholarly judgment (keep humans in the loop for critical decisions)

---

## Architecture (high level)

```
Researcher ↔ Research UI
             ↓↑
     Research Grounding Panel (live research state)
             ↓
     Middleware (this project)
       ├─ ResearchGroundingState (validated via JSON Schemas)
       ├─ SearchGatekeeper (Plan→OK?→Search→Recap)
       ├─ SearchFailureRouter (targeted help on empty results, query errors)
       ├─ Confidence+Provenance Decorator (paper recommendations with sources)
       └─ Telemetry (SearchReceipt/QueryLog/BiasWarnings)
             ↓
     Research Agent/Orchestrator (ADK, LangGraph, custom)
             ↓
     Academic Database Tools (Semantic Scholar, arXiv, ACM, etc.)
```

### State Objects

**ResearchGroundingBox**:
```python
{
  "research_question": str,           # What are we trying to understand?
  "stage": str,                       # scoping | retrieval | synthesis | validation
  "search_assumptions": List[str],    # Active filters, date ranges, exclusions
  "open_questions": List[str],        # Unresolved issues, coverage gaps
  "next_action": {                    # Next search/analysis step
    "owner": str,                     # agent | researcher | both
    "action": str,                    # search_database | refine_query | synthesize_results
    "database": str,                  # Which database/tool to use next
    "due": str                        # Timing constraint
  },
  "papers_found": int,                # Running count
  "databases_searched": List[str],    # Audit trail
  "current_filters": Dict[str, any]   # Active search constraints
}
```

**SearchReceipt**:
```python
{
  "timestamp": str,
  "database": str,                    # Which database was queried
  "query": str,                       # Exact query string used
  "results_count": int,               # Papers returned
  "filters_applied": List[str],       # year>=2020, venue=conference, etc.
  "delta": str,                       # What changed in grounding state
  "next": str,                        # Next planned action
  "duration_ms": int,
  "warnings": List[str]               # Coverage gaps, bias alerts
}
```

**SearchFailureClass** (enum):
- `EMPTY_RESULTS` → Broaden query, try synonyms, search different database
- `AMBIGUOUS_TERMINOLOGY` → Show competing definitions, ask researcher to clarify
- `DATABASE_COVERAGE_GAP` → Suggest complementary databases, note limitation
- `QUERY_TOO_BROAD` → Propose narrowing filters with examples
- `ACCESS_RESTRICTED` → Show library/ILL options, note unavailable papers
- `INCONSISTENT_RESULTS` → Explain database differences, suggest validation strategy

---

## Milestones & Acceptance Criteria

### M1: Schemas + Research State Store (1-2 days)
- Implement `ResearchGroundingBox`, `SearchReceipt`, `SearchFailureClass` schemas
- Build in-memory store with validation
- **Accept**: Example literature review scenarios validate without error

### M2: Prompt Injection (Research Grounding + Search Gatekeeper) (2 days)
- Add `prompts/litreview/grounding_updater.txt` after each search
- Add `prompts/litreview/search_gate.txt` before database queries
- **Accept**: Demo script shows grounding box updating through scoping → retrieval → synthesis

### M3: Targeted Search Help (1 day)
- Implement `classify_search_failure()` and `suggest_search_remedy()`
- Map empty results → query expansion, terminology issues → disambiguation
- **Accept**: Given synthetic search failures, returns actionable recovery options

### M4: Confidence + Provenance for Papers (1 day)
- Decorate paper recommendations with:
  - Confidence level (based on citation count, recency, venue quality)
  - Provenance (which query found it, from which database)
  - Relevance explanation (why recommended for this research question)
- **Accept**: Demo shows provenance trail from research question → query → paper

### M5: Research Grounding Panel UI (1 day)
- Render `Question • Stage • Assumptions • Open Questions • Next` in console/web
- Show papers found count and databases searched
- **Accept**: After each search, panel updates with deltas marked `Δ`

### M6: Telemetry + Research Audit Logs (1 day)
- Emit events per `ops/telemetry_events.md`
- Log complete search strategy for reproducibility
- **Accept**: NDJSON log contains full query history, suitable for methods section documentation

### M7: Academic Research Presets (1 day)
- Wire research stage-specific prompts: scoping, retrieval, synthesis, validation
- **Accept**: Agent behavior adapts to research stage (exploratory in scoping, precise in validation)

---

## Integration Paths for Research Agents

### Path A: Wrap Database Tool Calls
```python
with search_plan_gate(plan, database_tool, short_run_option):
    results = database_tool(query, filters)
    update_research_grounding_box(results)
    emit_search_receipt(database, query, results)
```

### Path B: Research Stage Nodes
- Insert "SearchGatekeeper" node between query planner and database tools
- Node enforces approval for expensive searches (e.g., full-text retrieval)
- Emits receipts for audit trail

### Path C: Middleware for Research APIs
- POST `/plan-search` to preview query
- Require `/approve` to execute (with short-run option)
- POST `/search-recap` with results and grounding update

---

## Search Failure Modes & Remedies (Academic Research)

### EMPTY_RESULTS
**Symptoms**: Query returns 0 papers
**Remedies**:
1. **Primary**: Broaden query (remove restrictive filters, try synonyms)
2. **Fallback**: Try different database (coverage varies by discipline)
3. **Ask Researcher**: "No results for 'explainable ML in radiology' – try 'interpretable AI medical imaging'?"

### AMBIGUOUS_TERMINOLOGY
**Symptoms**: Results span unrelated topics
**Remedies**:
1. **Primary**: Show 2-3 interpretations with example papers from each
2. **Fallback**: Add disambiguating filter (venue, author, date range)
3. **Ask Researcher**: "ML governance" could mean policy OR model monitoring – which?"

### DATABASE_COVERAGE_GAP
**Symptoms**: Expected papers missing from results
**Remedies**:
1. **Primary**: Suggest complementary database (e.g., arXiv for preprints if missing from journals)
2. **Warning**: Note known limitation ("ACM focuses on CS – try PubMed for medical papers")
3. **Offer**: Search additional source with one click

### QUERY_TOO_BROAD
**Symptoms**: 10,000+ results, unclear how to filter
**Remedies**:
1. **Primary**: Propose specific filter ("Narrow to 2020-2024?", "Conference papers only?")
2. **Short-run**: "Show top 20 by citations first, then decide on filters"
3. **Ask Researcher**: Offer 2-3 narrowing strategies to choose from

### ACCESS_RESTRICTED
**Symptoms**: Papers found but full-text unavailable
**Remedies**:
1. **Primary**: Show library access options (ILL, institutional subscriptions)
2. **Warning**: Note incomplete information ("Abstract only – full paper needed for claims")
3. **Alternative**: Search for open-access version (arXiv, author's website)

### INCONSISTENT_RESULTS
**Symptoms**: Different databases return conflicting information
**Remedies**:
1. **Primary**: Explain database characteristics (Semantic Scholar has broader coverage, ACM has authoritative venues)
2. **Validation**: Suggest cross-checking key papers in multiple databases
3. **Warning**: Note citation count differences, metadata quality issues

---

## Research Workflow Stage-Specific Behavior

### Stage: SCOPING
**Goals**: Define research question, identify key concepts, set boundaries
**Grounding Focus**:
- Research question clarity
- Concept identification
- Scope boundaries (date ranges, disciplines, publication types)
**Agent Behavior**:
- Exploratory queries (broad terms, multiple databases)
- Suggest alternative framings of research question
- Identify terminology variations early

### Stage: RETRIEVAL
**Goals**: Execute systematic searches across databases
**Grounding Focus**:
- Database coverage tracking
- Query evolution (what's been tried, what worked)
- Papers found count by source
**Agent Behavior**:
- Systematic database coverage (don't miss major sources)
- Query refinement based on initial results
- Track assumptions (filters, exclusions)

### Stage: SYNTHESIS
**Goals**: Organize papers, identify themes and gaps
**Grounding Focus**:
- Thematic organization emerging
- Gap identification
- Conflicting findings
**Agent Behavior**:
- Group papers by approach/method/finding
- Highlight disagreements in literature
- Note under-explored areas

### Stage: VALIDATION
**Goals**: Check coverage completeness, identify biases
**Grounding Focus**:
- Coverage assessment
- Bias detection (citation bias, publication bias, database bias)
- Reproducibility of search strategy
**Agent Behavior**:
- Backward/forward citation searches for key papers
- Check for missing perspectives (languages, regions, venues)
- Document complete search strategy for methods section

---

## Cognitive Science Foundations

### Situation Awareness (Endsley 1995)
- **Level 1** (Perception): Show what databases have been searched, papers found
- **Level 2** (Comprehension): Explain what results mean for research question
- **Level 3** (Projection): Suggest next search steps based on current state

### Mixed-Initiative Interaction (Allen et al. 2001)
- **Agent Initiative**: Suggest next database based on coverage gaps
- **Human Initiative**: Researcher can override, add constraints, change direction
- **Negotiated Control**: Plan → OK? → Search pattern balances automation and control

### Gulf of Evaluation (Norman 1986)
- **Bridge the Gap**: Grounding panel makes internal agent state visible
- **Continuous Feedback**: Search receipts show what changed after each action
- **Predictability**: Clear next action reduces uncertainty

### Error Recovery (Norman 1983)
- **Slips** (wrong database): Quick undo/redo, low friction correction
- **Mistakes** (wrong query strategy): Explain why approach failed, suggest alternatives
- **Targeted Help**: Specific remedies based on error classification, not generic messages

---

## Responsible Research AI Redlines

### Transparency Requirements
- **Never hide database limitations**: Note coverage gaps, bias risks
- **Always show query provenance**: Which search found which paper
- **Mark access status**: Full-text vs abstract-only vs unavailable
- **Warn about citation bias**: Over-reliance on highly-cited papers

### Reproducibility Standards
- **Log complete search strategy**: Every query, every database, every filter
- **Timestamp all searches**: Enable snapshot-in-time reproducibility
- **Document changes**: Why queries were refined, what assumptions changed
- **Export audit trail**: Ready for methods section or supplementary materials

### Researcher Autonomy
- **Never auto-exclude papers**: Always ask before applying filters
- **Explain all defaults**: Why starting with these databases? Why these dates?
- **Provide opt-out**: Researcher can always override agent suggestions
- **No hidden ranking**: If sorting by citations, say so explicitly

### Scholarly Integrity
- **Don't overstate confidence**: "Likely relevant" not "perfect match"
- **Show conflicting evidence**: Don't hide papers that contradict hypothesis
- **Note methodology limitations**: Search strategy can't guarantee completeness
- **Respect access boundaries**: Don't promise unavailable full-text access

---

## Example: Grounding Box Evolution During Literature Review

**Initial State (Scoping)**:
```
Research Question: What approaches exist for explainable AI in healthcare?
Stage: scoping (1/4)
Assumptions: [none yet]
Open Questions:
  • Which healthcare domains? (radiology, EHR, diagnostics, all?)
  • Include only clinical applications or also research tools?
  • Date range? (XAI is recent, how far back?)
Next Action: agent → explore terminology variations by EOD
```

**After Initial Searches (Retrieval)**:
```
Δ Research Question: What approaches exist for explainable AI in clinical decision support?
Δ Stage: retrieval (2/4) — 3/5 databases searched
Δ Assumptions:
  • Clinical applications only (excluded research lab tools)
  • 2018-present (when XAI in healthcare emerged)
  • English language papers
Δ Open Questions:
  • Missing European research? (mostly US papers so far)
  • Include grey literature (hospital white papers)?
Papers Found: 47 (SemanticScholar: 23, arXiv: 12, ACM: 12)
Δ Next Action: agent → search PubMed for medical perspectives by tomorrow 10am
```

**Turn Receipt** (shown below grounding panel):
```
[14:23] Searched ACM Digital Library: "explainable AI clinical" (2018-2024)
→ Found 12 papers (4 CHI, 3 AI in Medicine venues, 5 general AI)
→ Applied filter: venue=conference OR journal (excluded workshops)
→ Added assumption: "Focusing on peer-reviewed venues"
→ Warning: ACM skews toward HCI/system papers – add medical database
Next: Search PubMed for clinical/medical perspectives
```

---

## Success Metrics

### Research Efficiency
- **Reduced duplicate searches**: Track if same queries repeated unnecessarily
- **Database coverage**: Percentage of relevant databases searched for topic
- **Query refinement cycles**: How many iterations to find relevant papers

### Researcher Confidence
- **Grounding box accuracy**: Does it match researcher's mental model?
- **Search strategy clarity**: Can researcher explain approach to colleague?
- **Reproducibility**: Can search be replicated from audit log?

### Research Quality
- **Coverage completeness**: Were key papers found?
- **Bias awareness**: Did researcher notice database/citation biases?
- **Evidence synthesis**: Were conflicting findings surfaced?

---

## Integration with ADK Textbook Chapters

### Chapter 2: Paper Finder Agent
- Add ResearchGroundingBox to track multi-database searches
- Implement SearchGatekeeper before tool calls
- Emit SearchReceipts for each database query

### Chapter 6: ADK Runtime
- Store grounding state in session state
- Use EventActions.state_delta to update grounding box
- Show research state in UI contract compliance

### Chapter 7: PostgreSQL Runtime
- Persist search history and grounding state evolution
- Enable "research session resume" across multiple sessions
- Store complete audit trail for reproducibility

### Chapter 8: UI Frameworks
- Render Research Grounding Panel in Textual interface
- Show live updates as searches progress
- Display paper provenance (query → database → paper)

---

## Next Steps for Implementation

1. **Create schemas** in `schemas/research/` directory
2. **Write prompts** for each research stage in `prompts/litreview/`
3. **Build glue code** adapting existing paper finder agent
4. **Test with scenarios**: Scoping → Retrieval → Synthesis → Validation
5. **Document patterns** for reproducible research methods
