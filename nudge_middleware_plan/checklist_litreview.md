# Implementation Checklist - Literature Review Grounding Middleware

Progressive implementation plan for integrating research grounding middleware into ADK textbook agents.

## Phase 1: Foundation (Days 1-2)

### Day 1: Schemas and Data Structures

- [ ] Create `schemas/research/` directory
- [ ] Implement `ResearchGroundingBox` dataclass
  - [ ] `research_question: str`
  - [ ] `stage: ResearchStage` (enum)
  - [ ] `search_assumptions: List[str]`
  - [ ] `open_questions: List[str]`
  - [ ] `next_action: NextAction`
  - [ ] `papers_found: int`
  - [ ] `databases_searched: List[str]`
  - [ ] `current_filters: Dict[str, Any]`
- [ ] Implement `SearchReceipt` dataclass
  - [ ] Timestamp, database, query, results_count
  - [ ] Filters applied, delta description
  - [ ] Next action, duration, warnings
- [ ] Implement `SearchFailureClass` enum (6 types)
- [ ] Write JSON Schema validation files
- [ ] Test schemas with example data from `scenario_walkthrough.md`

**Acceptance**: All example scenarios validate without errors

### Day 2: In-Memory Store

- [ ] Implement `ResearchGroundingStore` class
  - [ ] `initialize()` - Start new research session
  - [ ] `update()` - Update grounding box fields with change tracking
  - [ ] `emit_receipt()` - Create and store SearchReceipt
  - [ ] `get_changed_fields()` - For Δ highlighting
  - [ ] `export_search_strategy()` - Generate methods section text
- [ ] Add state persistence helpers
  - [ ] `to_dict()` / `from_dict()` serialization
  - [ ] JSON export for storage
- [ ] Write unit tests for store operations
- [ ] Test with mock search scenarios

**Acceptance**: Store correctly tracks state through scoping → retrieval → synthesis → validation

---

## Phase 2: Prompt Integration (Days 3-4)

### Day 3: Grounding Updater Prompt

- [ ] Review `prompts/litreview/grounding_updater.txt`
- [ ] Integrate into Chapter 2 paper finder agent
- [ ] Add as system prompt after each tool call
- [ ] Test grounding box updates after searches
  - [ ] Research question refinement
  - [ ] Assumptions added/removed
  - [ ] Open questions raised/resolved
  - [ ] Next action determined
- [ ] Verify Δ highlighting for changed fields
- [ ] Test with multiple search sequences

**Acceptance**: Grounding box accurately reflects research state after each search

### Day 4: Search Gate Prompt

- [ ] Review `prompts/litreview/search_gate.txt`
- [ ] Integrate search plan presentation into agent workflow
- [ ] Add approval mechanism (OK/Short Run/Modify/Cancel)
  - [ ] Console version: Text input
  - [ ] Future: UI buttons in Chapter 8
- [ ] Implement "Short Run" preview (limit=10)
- [ ] Test plan rejection and modification flow
- [ ] Measure prevention of wasted searches

**Acceptance**: Agent presents plan before every search, respects user decisions

---

## Phase 3: Targeted Help (Day 5)

### Day 5: Failure Classification and Remedies

- [ ] Implement `SearchFailureHandler` class
  - [ ] `classify_failure()` - Detect failure type from symptoms
  - [ ] `suggest_remedy()` - Provide specific actions based on type
- [ ] Review `prompts/litreview/search_failure_help.txt`
- [ ] Implement remedies for each failure type:
  - [ ] **EMPTY_RESULTS**: Broaden query, synonyms, different DB
  - [ ] **AMBIGUOUS_TERMINOLOGY**: Show interpretations, disambiguate
  - [ ] **DATABASE_COVERAGE_GAP**: Suggest complementary DB
  - [ ] **QUERY_TOO_BROAD**: Propose filters, short run
  - [ ] **ACCESS_RESTRICTED**: Library options, find open access
  - [ ] **INCONSISTENT_RESULTS**: Explain differences, validate
- [ ] Test with synthetic failures
- [ ] Verify actionable remedies (not generic messages)

**Acceptance**: Each failure type returns 1 primary + 1 fallback remedy with specific actions

---

## Phase 4: UI Components (Days 6-7)

### Day 6: Console Grounding Panel

- [ ] Review `ui/research_grounding_panel_spec.md`
- [ ] Implement console rendering
  - [ ] Fixed 6-line panel format
  - [ ] Question | Stage | Assumptions | Questions | Next
  - [ ] Papers count and databases searched
- [ ] Add change highlighting with Δ prefix
- [ ] Implement turn receipt display (below panel)
- [ ] Test responsive behavior (≤80 chars, ≥120 chars)
- [ ] Add color coding (optional, must work without)

**Acceptance**: Panel updates after each action, changes clearly visible

### Day 7: Search History and Export

- [ ] Implement search history view (expandable)
  - [ ] Chronological list of all searches
  - [ ] Database, query, results, timestamp
  - [ ] Click to see full results (future UI)
- [ ] Implement export function
  - [ ] Markdown format for methods section
  - [ ] Complete query history
  - [ ] Inclusion criteria (assumptions)
  - [ ] Database coverage
- [ ] Test export with complete scenario
- [ ] Verify methods section is publication-ready

**Acceptance**: Export produces reproducible search strategy documentation

---

## Phase 5: ADK Integration (Days 8-9)

### Day 8: Chapter 2 Paper Finder Integration

- [ ] Review Chapter 2 `paperfinder/agent.py`
- [ ] Wrap existing search tools with grounding middleware
  - [ ] `search_semantic_scholar` → wrapped version
  - [ ] `search_arxiv` → wrapped version
  - [ ] `search_acm_digital_library` → wrapped version
  - [ ] `search_acl_anthology` → wrapped version
  - [ ] `search_osu_digital_collections` → wrapped version
- [ ] Add grounding store to agent initialization
- [ ] Update agent instructions to include grounding awareness
- [ ] Test multi-database search with grounding
- [ ] Verify receipts generated for each search

**Acceptance**: Existing agent works with grounding, no functionality lost

### Day 9: Chapter 6 Runtime Integration

- [ ] Add ResearchGroundingBox to session state
- [ ] Use `EventActions.state_delta` for grounding updates
- [ ] Implement SSE streaming for panel updates
- [ ] Test UI Contract compliance
- [ ] Add grounding panel to FastAPI UI
- [ ] Test real-time updates during search

**Acceptance**: Grounding state visible in runtime UI, updates in real-time

---

## Phase 6: Persistence (Day 10)

### Day 10: Chapter 7 PostgreSQL Integration

- [ ] Add grounding state table to schema
  ```sql
  CREATE TABLE research_grounding_state (
    session_id UUID REFERENCES sessions(id),
    grounding_box JSONB,
    updated_at TIMESTAMP
  );
  ```
- [ ] Add search receipts table
  ```sql
  CREATE TABLE search_receipts (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    receipt JSONB,
    created_at TIMESTAMP
  );
  ```
- [ ] Implement persistence in PostgreSQL runtime
  - [ ] Save grounding state after each update
  - [ ] Store receipts as events
  - [ ] Load grounding state on session resume
- [ ] Test multi-day research session
- [ ] Verify complete audit trail in database

**Acceptance**: Research sessions persist across days, complete history available

---

## Phase 7: Advanced Features (Days 11-12)

### Day 11: Citation Bias Detection

- [ ] Implement citation distribution analysis
  - [ ] Calculate mean, median, quartiles of citations
  - [ ] Detect skew toward highly-cited papers
- [ ] Add bias warnings to receipts
  - [ ] "⚠️ Citation bias: 80% papers have >100 citations"
  - [ ] Suggest supplemental search for emerging work
- [ ] Test with realistic citation distributions
- [ ] Verify warnings appear at right times

**Acceptance**: System detects and warns about citation bias

### Day 12: Chapter 8 Textual UI

- [ ] Implement grounding panel as Textual widget
  - [ ] Fixed header, always visible
  - [ ] Scrolling turn receipts view
  - [ ] Interactive buttons for search gates
- [ ] Add artifact tracking for found papers
  - [ ] List of papers with metadata
  - [ ] Link to provenance (which query found it)
- [ ] Test complete UI workflow
- [ ] Polish aesthetics (colors, layout, responsiveness)

**Acceptance**: Professional research UI with grounding panel and paper tracking

---

## Phase 8: Evaluation (Days 13-14)

### Day 13: User Testing

- [ ] Recruit 2-3 PhD students for testing
- [ ] Define test scenarios (realistic literature reviews)
  - [ ] Scenario 1: Narrow technical topic
  - [ ] Scenario 2: Broad interdisciplinary topic
  - [ ] Scenario 3: Topic with known coverage gaps
- [ ] Measure metrics:
  - [ ] Time to comprehensive search
  - [ ] Number of databases searched
  - [ ] Query refinement cycles
  - [ ] User satisfaction (survey)
- [ ] Collect qualitative feedback
  - [ ] Grounding box clarity
  - [ ] Targeted help usefulness
  - [ ] Reproducibility confidence

**Acceptance**: Positive feedback, measurable efficiency gains

### Day 14: Refinement and Documentation

- [ ] Address feedback from user testing
- [ ] Fix identified issues
- [ ] Write comprehensive documentation
  - [ ] User guide for researchers
  - [ ] Developer guide for extending middleware
  - [ ] Integration guide for other ADK agents
- [ ] Create video demo/walkthrough
- [ ] Write blog post about cognitive science principles

**Acceptance**: Production-ready middleware with complete documentation

---

## Phase 9: Advanced Research Scenarios (Days 15-16)

### Day 15: Systematic Review Support

- [ ] Add PRISMA flow diagram support
  - [ ] Track papers at each stage (identification, screening, included)
  - [ ] Generate PRISMA diagram from receipts
- [ ] Add inclusion/exclusion criteria tracking
  - [ ] Structured criteria specification
  - [ ] Automatic tracking of why papers excluded
- [ ] Add inter-rater reliability support
  - [ ] Track multiple researchers' decisions
  - [ ] Calculate agreement metrics

**Acceptance**: Support for formal systematic review methodology

### Day 16: Citation Network Analysis

- [ ] Add backward citation search
  - [ ] "Find papers cited by key paper X"
  - [ ] Track citation provenance
- [ ] Add forward citation search
  - [ ] "Find papers that cite key paper X"
  - [ ] Identify recent developments
- [ ] Visualize citation networks
  - [ ] Graph of papers and citations
  - [ ] Identify seminal works, clusters

**Acceptance**: Support for citation-based discovery and validation

---

## Success Criteria (Overall)

### Technical
- [ ] All schemas validate correctly
- [ ] State persists across sessions (PostgreSQL)
- [ ] Complete audit trail for reproducibility
- [ ] UI updates in real-time (SSE)
- [ ] Works with all Chapter 2 search tools

### User Experience
- [ ] Grounding box matches researcher mental model
- [ ] Search gates prevent wasted effort
- [ ] Targeted help resolves failures quickly
- [ ] Turn receipts provide clear feedback
- [ ] Export ready for methods section

### Research Quality
- [ ] Coverage gaps identified
- [ ] Citation bias detected
- [ ] Terminology variations handled
- [ ] Database biases noted
- [ ] Search strategy reproducible

### Cognitive Science Validation
- [ ] Situation awareness maintained (Endsley)
- [ ] Mixed-initiative control working (Allen et al.)
- [ ] Gulf of evaluation bridged (Norman)
- [ ] Error recovery effective (Norman)

---

## Optional Extensions

### Research Domain Presets
- [ ] Computer Science preset (ACM, arXiv, IEEE)
- [ ] Biomedical preset (PubMed, MEDLINE, EMBASE)
- [ ] Social Sciences preset (PsycINFO, JSTOR)
- [ ] Humanities preset (JSTOR, Project MUSE)

### Collaboration Features
- [ ] Multi-researcher sessions
- [ ] Shared grounding box
- [ ] Comment/annotation on searches
- [ ] Decision tracking for systematic reviews

### AI-Enhanced Features
- [ ] Query suggestion based on results
- [ ] Automatic synonym expansion
- [ ] Duplicate detection across databases
- [ ] Theme extraction from papers found

### Integration with Reference Managers
- [ ] Export to Zotero/Mendeley
- [ ] Import existing collections
- [ ] Sync grounding state with collections

---

## Notes

- **Start small**: Begin with console version, add GUI later
- **Test continuously**: Each phase should have working demo
- **Get user feedback early**: Test with real researchers by Day 13
- **Document as you go**: Don't wait until end
- **Keep cognitive science grounded**: Always tie features to principles

## Resources

- Cognitive science papers in references (Endsley, Norman, Allen et al.)
- ADK documentation for integration
- Chapter 2-8 codebases for patterns
- `scenario_walkthrough.md` for realistic usage examples
- `adk_integration_example.py` for code patterns
