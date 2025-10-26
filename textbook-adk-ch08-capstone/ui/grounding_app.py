"""
Research Grounding Panel - Textual UI

Simple, sparse terminal interface demonstrating grounding middleware
with real ADK events consumed via SSE.
"""

import asyncio
from typing import Dict, Any, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Static, Input, Button, Log, Footer, Header
from textual import on, work

from .sse_client import stream_events


class GroundingPanel(Static):
    """Display grounding box state using compose pattern."""

    # Reactive variables trigger re-composition
    research_question = reactive("No research question set")
    stage = reactive("scoping")
    papers_found = reactive(0)
    databases_searched = reactive([])
    assumptions = reactive([])
    open_questions = reactive([])
    next_action = reactive({"owner": "agent", "action": "TBD", "target": "", "due": ""})
    changed_fields = reactive(set())

    def compose(self) -> ComposeResult:
        """Compose grounding panel with current state."""
        # Calculate stage progress
        stage_map = {
            "scoping": (1, 4),
            "retrieval": (2, 4),
            "synthesis": (3, 4),
            "validation": (4, 4)
        }
        k, n = stage_map.get(self.stage, (1, 4))

        # Determine delta markers
        def delta(field: str) -> str:
            return "Δ " if field in self.changed_fields else ""

        # Format assumptions
        assumptions_text = "none"
        if self.assumptions:
            assumptions_text = "\n  ".join(f"• {a}" for a in self.assumptions[:2])

        # Format open questions
        questions_text = "none"
        if self.open_questions:
            questions_text = "\n  ".join(f"• {q}" for q in self.open_questions[:3])

        # Format next action
        next_text = f"{self.next_action['owner']} → {self.next_action['action']} {self.next_action['target']}"
        if self.next_action['due']:
            next_text += f" by {self.next_action['due']}"

        db_count = len(self.databases_searched)
        db_list = ", ".join(self.databases_searched[:3]) if self.databases_searched else "none"
        if db_count > 3:
            db_list += f" (+{db_count - 3} more)"

        # Compose all components
        yield Static(f"{delta('research_question')}Question: {self.research_question}", classes="grounding-field")
        yield Static(f"{delta('stage')}Stage: {self.stage} ({k}/{n}) — {self.papers_found} papers, {db_count} databases", classes="grounding-field")
        yield Static(f"{delta('assumptions')}Assumptions:\n  {assumptions_text}", classes="grounding-field")
        yield Static(f"{delta('open_questions')}Open Questions:\n  {questions_text}", classes="grounding-field")
        yield Static(f"{delta('next_action')}Next: {next_text}", classes="grounding-field")
        yield Static(f"Databases: {db_list}", classes="grounding-field-secondary")

    def update_from_state(self, state_delta: Dict[str, Any], changed: set):
        """Update grounding box from ADK state_delta event."""
        self.changed_fields = changed

        if "grounding:research_question" in state_delta:
            self.research_question = state_delta["grounding:research_question"]

        if "grounding:stage" in state_delta:
            self.stage = state_delta["grounding:stage"]

        if "grounding:papers_found" in state_delta:
            self.papers_found = state_delta["grounding:papers_found"]

        if "grounding:databases_searched" in state_delta:
            self.databases_searched = state_delta["grounding:databases_searched"]

        if "grounding:search_assumptions" in state_delta:
            self.assumptions = state_delta["grounding:search_assumptions"]

        if "grounding:open_questions" in state_delta:
            self.open_questions = state_delta["grounding:open_questions"]

        if "grounding:next_action" in state_delta:
            self.next_action = state_delta["grounding:next_action"]

        # Trigger re-composition by invalidating
        self.refresh(layout=True)


class GroundingPanelApp(App):
    """
    Research Grounding Panel Textual UI.

    Demonstrates grounding middleware with real ADK events.
    """

    CSS_PATH = "styles.tcss"

    TITLE = "Research Grounding Panel"
    SUB_TITLE = "ADK Events Demo"

    # Application state
    connected = reactive(False)
    server_url = "http://localhost:8000"
    user_id = "researcher_001"
    session_id = "session_001"
    app_name = "research_agent"

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(show_clock=True)

        # Grounding panel (top)
        with Vertical(id="grounding-container"):
            yield Static("═" * 80, classes="separator")
            yield Static("RESEARCH GROUNDING", classes="section-title")
            yield Static("─" * 80, classes="separator")
            yield GroundingPanel(id="grounding-panel")
            yield Static("═" * 80, classes="separator")

        # Turn receipts log (middle, scrollable)
        with Vertical(id="receipts-container"):
            yield Static("TURN RECEIPTS", classes="section-title")
            yield Static("─" * 80, classes="separator")
            yield Log(id="turn-receipts", auto_scroll=True, max_lines=100)

        # Chat input (bottom)
        with Horizontal(id="input-container"):
            yield Input(placeholder="Type your message...", id="message-input")
            yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize app and start SSE connection."""
        receipts_log = self.query_one("#turn-receipts", Log)
        receipts_log.write_line("[System] Grounding Panel initialized")
        receipts_log.write_line(f"[System] Connecting to {self.server_url}...")

        # Focus input
        self.query_one("#message-input", Input).focus()

    @on(Input.Submitted, "#message-input")
    async def handle_message_submit(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        await self.send_message(event.value)

    @on(Button.Pressed, "#send-button")
    async def handle_send_button(self) -> None:
        """Handle Send button click."""
        input_widget = self.query_one("#message-input", Input)
        await self.send_message(input_widget.value)

    async def send_message(self, message: str) -> None:
        """Send user message to agent via SSE."""
        if not message.strip():
            return

        # Clear input
        input_widget = self.query_one("#message-input", Input)
        input_widget.value = ""

        # Add to receipts
        receipts_log = self.query_one("#turn-receipts", Log)
        receipts_log.write_line(f"[You] {message}")

        # Start SSE stream in background
        self.process_events(message)

    @work(exclusive=True)
    async def process_events(self, user_message: str) -> None:
        """
        Process SSE event stream in background.

        Uses @work decorator for non-blocking background execution.
        """
        receipts_log = self.query_one("#turn-receipts", Log)
        grounding_panel = self.query_one("#grounding-panel", GroundingPanel)

        previous_state = {}
        agent_response_parts = []

        try:
            async for event in stream_events(
                server_url=self.server_url,
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id,
                message=user_message
            ):
                # Handle different event types
                author = event.get("author", "unknown")

                # Agent text response
                if author != "user" and event.get("content", {}).get("parts"):
                    for part in event["content"]["parts"]:
                        if "text" in part:
                            agent_response_parts.append(part["text"])

                # State delta (grounding update)
                if event.get("actions", {}).get("state_delta"):
                    state_delta = event["actions"]["state_delta"]

                    # Determine which fields changed
                    changed = set()
                    for key in state_delta:
                        if key.startswith("grounding:"):
                            field_name = key.replace("grounding:", "")
                            if previous_state.get(key) != state_delta[key]:
                                changed.add(field_name)

                    # Update grounding panel
                    grounding_panel.update_from_state(state_delta, changed)

                    # Update previous state
                    previous_state.update(state_delta)

                    # Log state change
                    if changed:
                        receipts_log.write_line(f"[State] Updated: {', '.join(changed)}")

                # Turn complete
                if event.get("turn_complete"):
                    if agent_response_parts:
                        full_response = " ".join(agent_response_parts)
                        receipts_log.write_line(f"[Agent] {full_response}")
                        agent_response_parts = []

                    receipts_log.write_line("[System] Turn complete")
                    break

        except Exception as e:
            receipts_log.write_line(f"[Error] {str(e)}")


def main():
    """Run the grounding panel app."""
    app = GroundingPanelApp()
    app.run()


if __name__ == "__main__":
    main()
