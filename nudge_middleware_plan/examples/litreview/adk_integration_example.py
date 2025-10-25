"""
Literature Review Grounding Middleware - ADK Integration Example

This shows how to integrate the research grounding middleware with ADK agents
from the textbook (specifically adapting Chapter 2's paper finder agent).

Key patterns demonstrated:
1. ResearchGroundingBox state management
2. SearchGatekeeper for plan → approve → search workflow
3. SearchReceipt emission for audit trails
4. Targeted help on search failures
5. Integration with existing ADK tools
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import json


# ============================================================================
# SCHEMAS (from nudge_middleware_plan/schemas/research/)
# ============================================================================

class ResearchStage(Enum):
    """Research workflow stages"""
    SCOPING = "scoping"
    RETRIEVAL = "retrieval"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"


class SearchFailureClass(Enum):
    """Classification of search failures for targeted help"""
    EMPTY_RESULTS = "empty_results"
    AMBIGUOUS_TERMINOLOGY = "ambiguous_terminology"
    DATABASE_COVERAGE_GAP = "database_coverage_gap"
    QUERY_TOO_BROAD = "query_too_broad"
    ACCESS_RESTRICTED = "access_restricted"
    INCONSISTENT_RESULTS = "inconsistent_results"


@dataclass
class NextAction:
    """Structured next action specification"""
    owner: str  # agent | researcher | both
    action: str  # search | refine | synthesize | validate | ask
    target: str  # database name, query, or analysis type
    due: str  # relative or absolute time


@dataclass
class ResearchGroundingBox:
    """
    Core grounding state for literature review workflows.

    Maintains situation awareness (Endsley 1995) by tracking:
    - Level 1 (Perception): papers_found, databases_searched
    - Level 2 (Comprehension): research_question, assumptions, open_questions
    - Level 3 (Projection): next_action, stage
    """
    research_question: str
    stage: ResearchStage
    search_assumptions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    next_action: Optional[NextAction] = None
    papers_found: int = 0
    databases_searched: List[str] = field(default_factory=list)
    current_filters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/transmission"""
        d = asdict(self)
        d["stage"] = self.stage.value
        if self.next_action:
            d["next_action"] = asdict(self.next_action)
        return d

    def format_for_display(self, show_deltas: bool = False) -> str:
        """
        Format grounding box for console/UI display.

        Args:
            show_deltas: If True, prefix changed fields with Δ
        """
        delta = "Δ " if show_deltas else ""

        # Calculate stage progress (hardcoded 4 stages)
        stage_map = {
            ResearchStage.SCOPING: (1, 4),
            ResearchStage.RETRIEVAL: (2, 4),
            ResearchStage.SYNTHESIS: (3, 4),
            ResearchStage.VALIDATION: (4, 4),
        }
        k, n = stage_map[self.stage]

        # Format assumptions (max 2)
        assumptions_text = "none"
        if self.search_assumptions:
            assumptions_text = "\n│   ".join(
                f"• {a}" for a in self.search_assumptions[:2]
            )

        # Format open questions (max 3)
        questions_text = "none"
        if self.open_questions:
            questions_text = "\n│   ".join(
                f"• {q}" for q in self.open_questions[:3]
            )

        # Format next action
        next_text = "TBD"
        if self.next_action:
            next_text = (
                f"{self.next_action.owner} → {self.next_action.action} "
                f"{self.next_action.target} by {self.next_action.due}"
            )

        db_list = ", ".join(self.databases_searched) if self.databases_searched else "none"

        return f"""┌─ RESEARCH GROUNDING ─────────────────────────────────────────────────────┐
│ Question: {self.research_question[:70]}
│ Stage: {self.stage.value} ({k}/{n}) — {self.papers_found} papers, {len(self.databases_searched)} databases
│ Assumptions: {assumptions_text}
│ Open Questions: {questions_text}
│ Next: {next_text}
└───────────────────────────────────────────────────────────────────────────┘"""


@dataclass
class SearchReceipt:
    """
    Audit trail for each database search (turn receipt).

    Provides transparency and reproducibility by logging:
    - Exact query executed
    - Results obtained
    - Grounding state changes
    - Warnings/issues encountered
    """
    timestamp: str
    database: str
    query: str
    results_count: int
    filters_applied: List[str]
    delta: str  # What changed in grounding box
    next: str  # Next planned action
    duration_ms: int
    warnings: List[str] = field(default_factory=list)

    def format_for_display(self) -> str:
        """Format as console turn receipt"""
        warnings_text = ""
        if self.warnings:
            warnings_text = "\n" + "\n".join(f"⚠️  {w}" for w in self.warnings)

        filters_text = ""
        if self.filters_applied:
            filters_text = f" (filters: {', '.join(self.filters_applied)})"

        return (
            f"[{self.timestamp}] Searched {self.database}: \"{self.query}\"{filters_text}\n"
            f"→ Found {self.results_count} papers\n"
            f"→ {self.delta}\n"
            f"→ Next: {self.next}"
            f"{warnings_text}"
        )


# ============================================================================
# GROUNDING STATE STORE
# ============================================================================

class ResearchGroundingStore:
    """
    In-memory store for research grounding state.

    In production (Chapter 7), this would be backed by PostgreSQL with
    event sourcing for complete audit trails.
    """

    def __init__(self):
        self.grounding_box: Optional[ResearchGroundingBox] = None
        self.receipts: List[SearchReceipt] = []
        self.previous_state: Optional[Dict[str, Any]] = None

    def initialize(
        self,
        research_question: str,
        initial_stage: ResearchStage = ResearchStage.SCOPING
    ):
        """Initialize grounding box for new research session"""
        self.grounding_box = ResearchGroundingBox(
            research_question=research_question,
            stage=initial_stage,
        )
        self.previous_state = self.grounding_box.to_dict()

    def update(self, **updates) -> Dict[str, Any]:
        """
        Update grounding box fields and track changes.

        Returns:
            Dictionary of changed fields
        """
        if not self.grounding_box:
            raise ValueError("Grounding box not initialized")

        changed = {}
        for key, value in updates.items():
            if not hasattr(self.grounding_box, key):
                raise ValueError(f"Invalid grounding box field: {key}")

            old_value = getattr(self.grounding_box, key)
            if old_value != value:
                setattr(self.grounding_box, key, value)
                changed[key] = {"old": old_value, "new": value}

        self.previous_state = self.grounding_box.to_dict()
        return changed

    def emit_receipt(
        self,
        database: str,
        query: str,
        results_count: int,
        filters_applied: List[str],
        delta: str,
        next_action: str,
        duration_ms: int,
        warnings: Optional[List[str]] = None
    ) -> SearchReceipt:
        """Emit search receipt for audit trail"""
        receipt = SearchReceipt(
            timestamp=datetime.now(timezone.utc).strftime("%H:%M"),
            database=database,
            query=query,
            results_count=results_count,
            filters_applied=filters_applied,
            delta=delta,
            next=next_action,
            duration_ms=duration_ms,
            warnings=warnings or []
        )
        self.receipts.append(receipt)
        return receipt

    def get_changed_fields(self) -> List[str]:
        """
        Identify which fields changed since last state.

        Used for Δ prefix highlighting in UI.
        """
        if not self.previous_state or not self.grounding_box:
            return []

        current = self.grounding_box.to_dict()
        changed = []

        for key in current:
            if current[key] != self.previous_state.get(key):
                changed.append(key)

        return changed

    def export_search_strategy(self) -> str:
        """
        Export complete search strategy for methods section.

        Supports reproducible research by documenting:
        - All databases searched
        - All queries executed
        - All filters applied
        - Temporal order of searches
        """
        if not self.grounding_box:
            return "No search strategy available"

        databases = ", ".join(self.grounding_box.databases_searched)

        queries = []
        for receipt in self.receipts:
            filters = ", ".join(receipt.filters_applied) if receipt.filters_applied else "none"
            queries.append(
                f"  - {receipt.database}: \"{receipt.query}\" "
                f"(filters: {filters}) → {receipt.results_count} papers"
            )
        queries_text = "\n".join(queries)

        assumptions = "\n".join(f"  - {a}" for a in self.grounding_box.search_assumptions)

        return f"""LITERATURE REVIEW SEARCH STRATEGY

Research Question:
{self.grounding_box.research_question}

Databases Searched:
{databases}

Queries Executed:
{queries_text}

Inclusion Criteria:
{assumptions}

Total Papers Found: {self.grounding_box.papers_found}

Search Date: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
"""


# ============================================================================
# SEARCH GATEKEEPER (Mixed-Initiative Control)
# ============================================================================

class SearchGatekeeper:
    """
    Implements Plan → Approve → Search → Recap pattern.

    Provides mixed-initiative control (Allen et al. 2001):
    - Agent proposes searches based on expertise
    - Researcher approves/modifies based on domain knowledge
    - Prevents wasted effort on wrong queries
    """

    @staticmethod
    def format_search_plan(
        database: str,
        query: str,
        filters: Dict[str, Any],
        rationale: str,
        expected_results: str,
        cost_time: str,
        alternative: Optional[str] = None
    ) -> str:
        """Format search plan for researcher approval"""
        filters_text = "\n│   ".join(
            f"• {k}: {v}" for k, v in filters.items()
        )

        alt_text = ""
        if alternative:
            alt_text = f"│ Alternative: {alternative}\n"

        return f"""┌─ SEARCH PLAN ────────────────────────────────────────┐
│ Database: {database}
│ Query: "{query}"
│ Filters:
│   {filters_text}
│
│ Rationale:
│ {rationale}
│
│ Expected Results: {expected_results}
│
│ Cost/Time: {cost_time}
│
{alt_text}└───────────────────────────────────────────────────────┘

OPTIONS:
[OK] Proceed with full search
[Short Run] Preview top 10 results first
[Modify] Adjust query/filters
[Cancel] Skip this search"""

    @staticmethod
    def should_request_approval(query_complexity: str = "standard") -> bool:
        """
        Determine if search plan should go through approval gate.

        Args:
            query_complexity: "simple" | "standard" | "expensive"

        Returns:
            True if approval needed
        """
        # Always request approval for expensive searches
        # Could be made configurable based on researcher preferences
        return query_complexity in ["standard", "expensive"]


# ============================================================================
# SEARCH FAILURE CLASSIFIER & TARGETED HELP
# ============================================================================

class SearchFailureHandler:
    """
    Classifies search failures and provides targeted remedies.

    Implements error recovery (Norman 1983) with specific actions
    based on failure type, not generic "try again" messages.
    """

    @staticmethod
    def classify_failure(
        results_count: int,
        expected_count_range: tuple[int, int],
        database: str,
        query: str
    ) -> Optional[SearchFailureClass]:
        """
        Classify search failure based on symptoms.

        Returns:
            SearchFailureClass if failure detected, None if success
        """
        min_expected, max_expected = expected_count_range

        if results_count == 0:
            return SearchFailureClass.EMPTY_RESULTS

        if results_count > max_expected * 10:
            return SearchFailureClass.QUERY_TOO_BROAD

        if results_count < min_expected * 0.2:
            # Much lower than expected - possible coverage gap
            return SearchFailureClass.DATABASE_COVERAGE_GAP

        return None  # Success

    @staticmethod
    def suggest_remedy(
        failure_class: SearchFailureClass,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest specific remedies based on failure classification.

        Returns:
            Dictionary with primary remedy, fallback, and researcher question
        """
        remedies = {
            SearchFailureClass.EMPTY_RESULTS: {
                "primary": f"Broaden query: remove filter '{context.get('restrictive_filter', 'N/A')}'",
                "fallback": f"Try synonyms: {context.get('synonyms', 'N/A')}",
                "ask_researcher": "What terminology does your field use for this concept?"
            },
            SearchFailureClass.DATABASE_COVERAGE_GAP: {
                "primary": f"Try {context.get('alternative_database', 'different database')} instead",
                "fallback": "Note limitation and continue with available results",
                "ask_researcher": "Do you know which venues published key papers on this topic?"
            },
            SearchFailureClass.QUERY_TOO_BROAD: {
                "primary": f"Apply filter: {context.get('suggested_filter', 'narrow date range')}",
                "fallback": "Short run: show top 20 by citations, then decide",
                "ask_researcher": "Which aspect of this topic is most relevant to your research?"
            },
        }

        return remedies.get(failure_class, {
            "primary": "Review query and try refinement",
            "fallback": "Consult with domain expert",
            "ask_researcher": "How would you like to proceed?"
        })


# ============================================================================
# ADK INTEGRATION WRAPPER
# ============================================================================

def wrap_search_tool_with_grounding(
    search_tool_fn,
    store: ResearchGroundingStore,
    gatekeeper: SearchGatekeeper
):
    """
    Wrapper for ADK tool functions that adds grounding middleware.

    This shows how to integrate with existing tools from Chapter 2
    (search_semantic_scholar, search_arxiv, etc.) without modifying them.

    Pattern:
    1. Present search plan to researcher
    2. Wait for approval (OK/Short Run/Modify/Cancel)
    3. Execute search
    4. Update grounding box
    5. Emit search receipt
    6. Check for failures and provide targeted help if needed
    """

    def wrapped_tool(query: str, **kwargs):
        # This would integrate with ADK's approval mechanism
        # For now, showing the pattern

        database = kwargs.get("database", "unknown")
        filters = kwargs.get("filters", {})

        # STEP 1: Format and present search plan
        plan = gatekeeper.format_search_plan(
            database=database,
            query=query,
            filters=filters,
            rationale=kwargs.get("rationale", "Standard search"),
            expected_results=kwargs.get("expected_results", "10-50 papers"),
            cost_time="1 API call, ~2 seconds",
            alternative=kwargs.get("alternative", None)
        )

        # In real implementation, this would use ADK's UI to get approval
        # For demo, we'll assume approval
        print(plan)
        approval = "OK"  # Would come from user interaction

        if approval == "Cancel":
            return {"cancelled": True, "reason": "User cancelled search"}

        if approval == "Short Run":
            kwargs["limit"] = 10

        # STEP 2: Execute search
        start_time = datetime.now(timezone.utc)
        results = search_tool_fn(query, **kwargs)
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # STEP 3: Update grounding box
        results_count = len(results.get("papers", []))

        store.update(
            papers_found=store.grounding_box.papers_found + results_count,
            databases_searched=list(set(
                store.grounding_box.databases_searched + [database]
            ))
        )

        # STEP 4: Emit search receipt
        receipt = store.emit_receipt(
            database=database,
            query=query,
            results_count=results_count,
            filters_applied=[f"{k}={v}" for k, v in filters.items()],
            delta=f"Added {results_count} papers from {database}",
            next_action="Continue to next database",
            duration_ms=duration_ms
        )

        print("\n" + receipt.format_for_display())

        # STEP 5: Check for failures and provide help
        expected_range = kwargs.get("expected_range", (10, 50))
        failure = SearchFailureHandler.classify_failure(
            results_count, expected_range, database, query
        )

        if failure:
            remedies = SearchFailureHandler.suggest_remedy(
                failure, context=kwargs.get("failure_context", {})
            )
            print(f"\n⚠️  Search issue detected: {failure.value}")
            print(f"Suggested remedy: {remedies['primary']}")

        return results

    return wrapped_tool


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize store
    store = ResearchGroundingStore()
    store.initialize(
        research_question="What approaches exist for XAI in clinical decision support?",
        initial_stage=ResearchStage.SCOPING
    )

    print(store.grounding_box.format_for_display())
    print("\n" + "="*80 + "\n")

    # Simulate wrapped tool usage
    # In real implementation, this would wrap tools from Chapter 2

    def mock_semantic_scholar(query: str, **kwargs):
        """Mock search tool for demonstration"""
        return {
            "papers": [
                {"title": f"Paper {i}", "authors": ["Author A"], "year": 2023}
                for i in range(34)
            ]
        }

    gatekeeper = SearchGatekeeper()
    wrapped_search = wrap_search_tool_with_grounding(
        mock_semantic_scholar, store, gatekeeper
    )

    # Execute search
    results = wrapped_search(
        "explainable AI clinical decision support",
        database="SemanticScholar",
        filters={"year": "2020+", "fields": ["Medicine", "CS"]},
        rationale="Starting with broad interdisciplinary search",
        expected_results="30-80 papers",
        expected_range=(30, 80)
    )

    print("\n" + "="*80 + "\n")
    print(store.grounding_box.format_for_display(show_deltas=True))

    print("\n" + "="*80 + "\n")
    print("SEARCH STRATEGY EXPORT:\n")
    print(store.export_search_strategy())
