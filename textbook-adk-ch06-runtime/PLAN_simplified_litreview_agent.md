# Simplified Literature Review Agent - Chapter 6 Plan

## 📚 Core Concept: "Paper Pipeline Manager"

**Focus**: Track papers through a simple 3-stage review pipeline while demonstrating all ADK state patterns.

## 📋 Simplified Workflow

1. **Search & Collect**: Add papers (manual entry + mock API)
2. **Offline Import**: Batch import from BibTeX files (manual state updates)
3. **Screen & Classify**: Mark papers as relevant/irrelevant with reasons
4. **Extract & Synthesize**: Pull key findings, track themes

## 🔧 State Management Demonstrations

### Session State (no prefix)
```python
{
    "current_search_query": "machine learning education",
    "pipeline_stage": "screening", 
    "papers_in_pipeline": 12,
    "current_paper_id": "paper_003",
    "session_notes": "Focus on K-12 applications today"
}
```

### User State (`user:` prefix)
```python
{
    "user:preferred_databases": ["arxiv", "pubmed"],
    "user:screening_criteria": ["peer_reviewed", "recent"],
    "user:total_papers_reviewed": 47,
    "user:research_interests": ["AI", "education", "HCI"],
    "user:reviewer_role": "primary_screener"
}
```

### App State (`app:` prefix) 
```python
{
    "app:total_papers_in_system": 1247,
    "app:popular_search_terms": ["LLM", "education", "bias"],
    "app:system_metrics": {"avg_screening_time": "3.2min"},
    "app:database_last_sync": "2024-01-15T10:00:00Z"
}
```

## 🛠️ Agent Architecture

```
simplified_litreview_agent/
├── agent.py              # Main agent with sub-agents for output_key demo
├── prompts.py            # Instructions with {current_search_query} injection  
└── tools/
    ├── paper_tools.py    # Add, search, retrieve papers
    ├── screening_tools.py # Mark relevant, add screening notes
    └── analysis_tools.py  # Extract themes, generate summaries
```

## 🔍 Specific Tools & State Patterns

### Paper Management Tools (Direct State Access)
- `add_paper_tool()` - Add paper to pipeline
- `search_papers_tool()` - Filter papers by criteria
- `get_pipeline_status_tool()` - Show current progress

### Screening Tools (Manual Events)  
- `batch_screen_papers_tool()` - Screen multiple papers via manual events
- `update_screening_criteria_tool()` - External system updates criteria
- `sync_with_collaborator_tool()` - External reviewer state updates

### Offline Import Tools ("The Standard Way" Manual State Updates)
- `import_bibtex_batch()` - Offline script that parses BibTeX files
- `sync_external_database()` - Batch import from institutional repositories
- `merge_collaborator_library()` - Import papers from colleague's Zotero export

*These tools demonstrate manual event creation for system-level operations that happen outside of interactive agent sessions - the key use case for "The Standard Way" pattern.*

### Analysis Sub-Agents (output_key Pattern)
- `SummaryAgent` - Generates paper summaries → `paper_summary` state
- `ThemeAgent` - Identifies themes → `extracted_themes` state  
- `RecommendationAgent` - Suggests next steps → `recommendations` state

## 📊 Database Persistence Scenarios

### Scenario 1: Session Interruption
1. Add 5 papers, screen 3 as relevant
2. Close session (simulate crash/logout)
3. Resume - papers and screening decisions persist
4. Continue with synthesis on relevant papers

### Scenario 2: Offline Import & Sync
1. Researcher exports 50 papers from Mendeley as BibTeX
2. Offline import script uses manual events to batch-add papers
3. Agent session resumes - all imported papers appear in pipeline
4. Mock API adds new papers from arXiv daily feed (manual events)

### Scenario 3: Collaborative Review
1. Primary reviewer adds papers, does initial screening
2. Secondary reviewer (new session) sees shared papers
3. External system updates from institutional database
4. Both reviewers see synchronized state

### Scenario 4: Long-Running Research
1. Week 1: Initial search and broad screening
2. Week 2: Focused screening on relevant subset  
3. Week 3: Theme extraction and synthesis
4. All state persists across weeks/sessions

## 🎨 User Experience Flow

```
> "Start a literature review on 'AI bias in hiring'"
  ✓ Creates search session, sets current_search_query state

> "Add this paper: 'Algorithmic Bias in Resume Screening'"  
  ✓ Uses add_paper_tool, updates papers_in_pipeline count

> "Import my BibTeX library from Zotero"
  ✓ Offline script uses manual events, batch-adds 47 papers

> "Search arXiv for new papers on AI bias"
  ✓ Mock API returns 12 papers, added via manual events

> "Screen the papers for relevance"
  ✓ Delegates to screening tools, saves decisions to state

> "What themes emerge from the relevant papers?"
  ✓ Uses ThemeAgent with output_key, saves to extracted_themes

> [Session ends, resume tomorrow]
  ✓ All state persists via DatabaseSessionService

> "Continue my literature review"
  ✓ Retrieves state, shows progress, suggests next steps
```

## 🚀 Implementation Benefits

1. **Authentic Academic Use**: Addresses real research workflow
2. **Clear State Progression**: Papers flow through obvious stages
3. **Collaborative Potential**: Multiple reviewers, external integrations
4. **Persistent Value**: Work isn't lost between sessions
5. **Demonstrative Power**: Shows all ADK patterns meaningfully

## 📝 Chapter 6 Learning Objectives

- **State Scoping**: User preferences vs session progress vs global metrics
- **Persistence**: Long-running research survives interruptions
- **External Integration**: Mock APIs, BibTeX imports, collaborator updates, system sync
- **Output Management**: Agent-generated summaries persist in state
- **Complex Workflows**: Multi-step processes with state transitions

## 🎯 Why This Works for Chapter 6

Creates a **realistic academic tool** that students would actually want to use, while perfectly demonstrating the power of ADK state management patterns. Much more engaging than generic "research project tracking" - this has clear academic value and workflow progression that makes state management essential rather than artificial.

### Key State Management Demos:

1. **Manual Entry**: Direct agent interaction with immediate state updates
2. **Mock API**: Simulated external service calls updating state via manual events
3. **BibTeX Import**: Offline batch processing demonstrating "The Standard Way"
4. **Collaborative Sync**: External system integration showing persistent state

This covers the full spectrum of ADK state patterns in authentic academic workflows.

## Relationship to Book Capstone

This simplified version introduces the core concepts and state patterns that will be expanded in the book's capstone literature review system. Students learn the fundamentals here, then see the full-scale implementation later.

## Manual State Updates Use Cases

The offline import tools demonstrate why "The Standard Way" (manual event creation) is essential:

- **Batch Operations**: Import 100s of papers from BibTeX files
- **System Integration**: Sync with institutional databases overnight
- **Data Migration**: Import existing research libraries
- **External APIs**: Background jobs fetching new papers
- **Collaborative Workflows**: Merge libraries from multiple researchers

These operations happen outside interactive agent sessions but need to update the same state that agents use - exactly what manual event creation enables.