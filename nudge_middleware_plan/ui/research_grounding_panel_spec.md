# Research Grounding Panel – UX Specification

## Purpose

Maintain **situation awareness** (Endsley 1995) during multi-database literature review workflows by continuously displaying the current research state.

## Design Principles

1. **Always Visible**: Panel stays visible throughout research session (pinned/sidebar)
2. **Change Highlighting**: Prefix changed lines with `Δ` after each action
3. **Compact**: Fixed 6-7 lines (doesn't dominate screen)
4. **Scannable**: Structured format allows quick status check
5. **Actionable**: Shows clear next action, not just history

---

## Panel Layout (Console/Terminal Version)

```
┌─ RESEARCH GROUNDING ─────────────────────────────────────────────────────┐
│ Question: <research question in one line>                                │
│ Stage: <stage_name> (k/n) — <papers_found> papers, <db_count> databases  │
│ Assumptions: <bullet list, max 2, or 'none'>                             │
│ Open Questions: <bullet list, max 3, or 'none'>                          │
│ Next: <owner> → <action> <database/tool> by <time>                       │
└───────────────────────────────────────────────────────────────────────────┘
```

### After Each Action: Turn Receipt (below panel)

```
[HH:MM] <action description> → <results summary> → <what changed> → Next: <next action>
```

---

## Panel Layout (Web/GUI Version)

```
╔══ RESEARCH GROUNDING ══════════════════════════════════════════╗
║ Question                                                        ║
║ What approaches exist for explainable AI in healthcare?        ║
║                                                                 ║
║ Stage: Retrieval (3/5) ━━━━━━━━━━━━░░░░░░ 60%                 ║
║ Papers: 47 | Databases: SemanticScholar, arXiv, ACM            ║
║                                                                 ║
║ Assumptions                                                     ║
║ • Clinical applications only (excluded lab tools)              ║
║ • 2018-present (when XAI in healthcare emerged)                ║
║                                                                 ║
║ Open Questions                                                  ║
║ • Missing European research? (mostly US papers so far)         ║
║ • Include grey literature (hospital white papers)?             ║
║                                                                 ║
║ Next Action                                                     ║
║ Agent → Search PubMed for medical perspectives by 10am         ║
║                                                                 ║
║ [View Search History] [Export Strategy] [Modify Plan]          ║
╚═════════════════════════════════════════════════════════════════╝

─── TURN RECEIPT ────────────────────────────────────────────────
[14:23] Searched ACM: "explainable AI clinical" (2018-2024)
→ Found 12 papers (4 CHI, 3 AI in Medicine, 5 general)
→ Added assumption: "Peer-reviewed venues only"
→ Warning: ACM skews toward HCI – add medical database
→ Next: Search PubMed for clinical perspectives
```

---

## Field Specifications

### 1. Research Question (1 line, ≤100 chars)

**Purpose**: Shared understanding of what we're trying to learn

**Format**: Question form preferred, statement acceptable
- ✓ "What approaches exist for explainable AI in healthcare?"
- ✓ "Survey of transfer learning in low-resource NLP"
- ✗ "XAI" (too vague)

**Updates**: When question is refined/clarified during scoping/retrieval

**Change indicator**: Δ prefix if question text changes

---

### 2. Stage (with progress indicator)

**Purpose**: Where are we in the research workflow?

**Format**: `<stage_name> (k/n)` where k=current step, n=total steps

**Stages**:
- `scoping (1/4)` — Defining question, identifying concepts
- `retrieval (2/4)` — Systematic database searches
- `synthesis (3/4)` — Organizing papers, identifying themes
- `validation (4/4)` — Checking coverage, addressing biases

**Progress bar** (web version): Visual indicator of completion

**Papers & Databases Counter**:
- Papers: Running total across all databases
- Databases: List of sources searched (abbreviated if >3)

**Change indicator**: Δ prefix if stage advances or counts update

---

### 3. Assumptions (≤2 bullets, or 'none')

**Purpose**: Make implicit constraints explicit for later methods section

**Format**: Bulleted list, each ≤60 chars
- ✓ "Clinical applications only (excluded lab tools)"
- ✓ "2018-present (when XAI in healthcare emerged)"
- ✓ "English language papers"
- ✗ "Various filters applied" (too vague)

**When to add**:
- Filters applied (date ranges, venues, languages)
- Scope decisions (included/excluded domains)
- Quality thresholds (min citations, peer-reviewed only)

**Max 2 shown**: If >2, show most recent/important

**Change indicator**:
- Δ for new assumptions added
- ~~strikethrough~~ for invalidated assumptions (keep visible 1 turn)

---

### 4. Open Questions (≤3 bullets, or 'none')

**Purpose**: Track unresolved issues and coverage gaps

**Format**: Question form, each ≤60 chars
- ✓ "Missing European research? (mostly US papers)"
- ✓ "Include grey literature?"
- ✓ "Expand to adjacent fields (biomed informatics)?"
- ✗ "Check other stuff" (not specific enough)

**Types of questions**:
- Coverage gaps (geographic, language, venue type)
- Scope ambiguities (include/exclude borderline topics)
- Methodological decisions (synthesis strategy, bias handling)

**Max 3 shown**: Prioritize by importance/blocking nature

**Change indicator**:
- Δ for new questions added
- ~~strikethrough~~ for resolved questions (keep visible 1 turn)

---

### 5. Next Action (1 line)

**Purpose**: Clear, specific next step (reduces uncertainty)

**Format**: `<owner> → <action> <target> by <time>`

**Owner**:
- `agent` — Agent will perform automatically
- `researcher` — Researcher decision/input needed
- `both` — Collaborative step

**Action verbs**:
- `search` — Query a database
- `refine` — Improve query based on results
- `synthesize` — Organize/analyze papers found
- `validate` — Check coverage/biases
- `ask` — Need researcher input/decision

**Target**: Specific database, tool, or analysis
- ✓ "search PubMed"
- ✓ "refine query for ACM"
- ✓ "ask researcher about scope"
- ✗ "continue working" (not specific)

**Timing**: Relative (by 5pm) or absolute (by tomorrow 10am)

**Examples**:
- `agent → search arXiv for recent preprints by 5pm`
- `researcher → decide on grey literature inclusion by EOD`
- `both → validate coverage gaps tomorrow 10am`

**Change indicator**: Δ if next action changes (every turn)

---

## Interactive Elements (Web Version)

### Three-Button Pattern (appears when PLAN shown)

```
┌─────────────────────────────────────────────────────────┐
│ [   OK   ]  [Short Run]  [  Modify  ]  [  Cancel  ]    │
└─────────────────────────────────────────────────────────┘
```

**OK**: Proceed with full search as planned
**Short Run**: Preview with top 10 results first
**Modify**: Adjust query/filters/database before executing
**Cancel**: Skip this search

### Additional Actions

**[View Search History]**: Expandable timeline of all searches
- Database, query, results count, timestamp
- Clickable to see full results from past searches

**[Export Strategy]**: Download complete search strategy
- All queries, databases, filters
- Formatted for methods section
- Includes timestamps, result counts

**[Modify Plan]**: Override next action
- Researcher can change database, query, or skip step
- Agent adapts to researcher preferences

---

## Turn Receipt Specification

Appears **below** grounding panel after each action (scrolls up over time)

### Format

```
[HH:MM] <action> → <results> → <grounding_delta> → Next: <next_action>
```

### Components

**Timestamp**: HH:MM format (24-hour)

**Action**: What was done
- "Searched SemanticScholar: 'XAI healthcare' (2018-2024)"
- "Applied filter: conferences only"
- "Researcher narrowed question to clinical focus"

**Results**: What was found
- "Found 23 papers (12 surveys, 11 methods)"
- "No results (query too specific)"
- "47 results (too broad, needs filtering)"

**Grounding Delta**: What changed in grounding box
- "Added assumption: clinical only"
- "Resolved question: scope includes devices"
- "New question: missing European research?"

**Next**: What's coming next
- "Next: Search arXiv for preprints"
- "Next: Ask researcher about venue filters"

**Warnings** (if applicable): Append with ⚠️
- "⚠️ ACM has HCI bias – add medical database"
- "⚠️ Citation bias – mostly highly-cited papers"
- "⚠️ Access restricted for 12/23 papers"

### Examples

```
[14:23] Searched ACM: "explainable AI clinical" (2018-2024)
→ Found 12 papers (4 CHI, 3 AI in Medicine, 5 general)
→ Added assumption: peer-reviewed venues only
→ Next: Search PubMed for clinical perspectives
⚠️ ACM skews toward HCI/systems papers

[14:27] Researcher narrowed question to "clinical decision support"
→ Question refined (was: "healthcare", now: "clinical decision support")
→ Stage advanced: scoping (1/4) → retrieval (2/4)
→ Next: Search SemanticScholar with refined query

[14:31] Searched SemanticScholar: "XAI clinical decision support" (2018+)
→ Found 23 papers (excellent coverage of recent work)
→ No grounding changes (query worked as expected)
→ Next: Search arXiv for very recent preprints
```

---

## Change Highlighting Pattern

### Δ Prefix for Changes

Any line that changed in the current turn gets Δ prefix

**Example: After refining research question**
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
Δ Question: What approaches for XAI in clinical decision support?
Δ Stage: retrieval (2/4) — 23 papers, 1 database
  Assumptions: • Clinical apps only • 2018-present
Δ Open Questions: • Include diagnostic vs treatment decisions?
Δ Next: agent → search arXiv for preprints by 5pm
└───────────────────────────────────────────────────────────┘
```

### Strikethrough for Resolved/Invalidated (1 turn persistence)

**Example: Assumption invalidated**
```
Assumptions:
  ~~• Minimum 50 citations (too restrictive – found 0 papers)~~
Δ • No citation minimum (exploratory phase)
  • 2018-present
```

**Example: Question resolved**
```
Open Questions:
  ~~• Which healthcare domains? → Answered: clinical decision support~~
Δ • Include diagnostic vs treatment decisions?
  • Missing European research?
```

---

## Responsive Behavior

### Narrow Console (≤80 chars)

Compact single-line format:
```
Q: XAI in healthcare | Stage: 2/4 (47 papers, 3 DBs) | Next: PubMed search
Assumptions: clinical+2018 | Open: EU coverage?, grey lit?
```

### Wide Screen (≥120 chars)

Full panel with expandable sections

### Mobile

Collapsible sections:
- Question + Stage always visible
- Tap to expand Assumptions/Questions/Next

---

## Integration with ADK Textbook

### Chapter 6: FastAPI Runtime
- Grounding panel updates via SSE (server-sent events)
- State stored in session state
- UI Contract compliance for state visibility

### Chapter 7: PostgreSQL Runtime
- Grounding state persisted in database
- Search history stored as events
- Resume research sessions across days

### Chapter 8: Textual UI
- Grounding panel as fixed header widget
- Turn receipts in scrolling log view
- Interactive buttons for Plan gates

---

## Cognitive Science Foundations

### Situation Awareness (Endsley 1995)

**Level 1 (Perception)**:
- Papers found count
- Databases searched list
- Current filters/assumptions

**Level 2 (Comprehension)**:
- Open questions show gaps
- Stage shows progress
- Assumptions show constraints

**Level 3 (Projection)**:
- Next action shows what's coming
- Stage progress predicts completion
- Open questions guide future work

### Gulf of Evaluation (Norman 1986)

**Problem**: User can't tell what system did or why
**Solution**: Turn receipts make every action explicit

**Problem**: User uncertain about current state
**Solution**: Grounding panel always shows current state

### Recognition Over Recall (Nielsen Heuristic)

**Problem**: Remembering what's been searched
**Solution**: Databases searched list visible

**Problem**: Remembering active filters
**Solution**: Assumptions section shows constraints

---

## Accessibility

- **Screen readers**: Semantic HTML, ARIA labels
- **Keyboard nav**: Tab through sections, arrow keys for buttons
- **High contrast**: Δ prefix (not just color) for changes
- **Reduced motion**: Optional: disable progress bar animation

---

## Testing Checklist

- [ ] Grounding panel updates after each search
- [ ] Δ prefix appears on changed lines only
- [ ] Turn receipts scroll but panel stays fixed
- [ ] Buttons appear only when plan is presented
- [ ] Short Run limits results to preview
- [ ] Search history expandable and scrollable
- [ ] Export generates complete strategy document
- [ ] Panel responsive to screen size
- [ ] Change highlighting works without color
- [ ] Screen reader announces updates
