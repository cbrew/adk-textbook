#!/usr/bin/env python3
"""
Simple Textual chat interface for ADK agents.

"""

import asyncio
import subprocess
from pathlib import Path

import httpx
from adk_consumer import ADKConsumer
from dotenv import load_dotenv
from event_extractor import extract_description_from_event
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)


class ChatInterface(App):
    """A simple chat interface using Textual, with scrollable compact bubbles."""

    # NOTE:
    # - Textual spacing units are integers (no decimals like 0.5).
    # - padding / margin shorthands support 1, 2, or 4 integers.

    CSS = """
    Screen {
        layout: vertical;
    }

    /* TabbedContent styling */
    TabbedContent {
        height: 1fr;
        margin: 1;
    }

    /* Tab panes */
    TabPane {
        border: solid $primary;
    }

    /* Events table styling */
    #events-table {
        height: 1fr;
    }

    /* Artifacts table styling */
    #artifacts-table {
        height: 1fr;
    }

    /* Artifacts info styling */
    #artifacts-info {
        height: auto;
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    /* The scrollable transcript itself */
    #chat-scroll {
        height: 1fr;
        background: $surface;
        border: none;
        padding: 0;             /* let bubbles define spacing */
        /* ScrollableContainer manages scrollbars; no overflow needed */
    }

    /* Input row */
    #input-container {
        height: auto;
        padding: 0 1;           /* top/btm=0, left/right=1 */
        margin: 0 0 1 0;
    }

    #message-input {
        width: 1fr;
    }

    #send-button {
        width: auto;
        margin-left: 1;
    }

    /* --- Compact bubbles --- */
    .msg {
        /* No extra space before/after each bubble */
        margin: 0 1 0 1;        /* top 0, right 1, bottom 0, left 1 */
        padding: 0 1;           /* top/bottom 0, left/right 1 */
        border: round $panel;
        max-width: 85%;
    }

    .msg.user {
        background: $accent;
        color: $text;
        text-align: right;
        align-horizontal: right;
    }

    .msg.agent {
        background: $boost;
        color: $text;
        text-align: left;
        align-horizontal: left;
    }

    .msg.system {
        background: $warning 15%;
        color: $warning;
        text-style: italic;
        text-align: center;
        align-horizontal: center;
        max-width: 95%;
        /* Make system notices slimmer than chat bubbles */
        padding: 0;
        border: none;
    }
    """

    connected = reactive(False)

    def __init__(self, agents_dir: str = "agents"):
        super().__init__()
        self.message_count = 0
        self.agents_dir = agents_dir
        self.adk_consumer: ADKConsumer | None = None
        self.http_client: httpx.AsyncClient | None = None
        self.adk_process: subprocess.Popen | None = None
        self.current_agent_md: Markdown | None = None  # live bubble while streaming
        self.event_records: list[dict] = []  # Store event records
        self.artifact_records: list[dict] = []  # Store artifact records
        self.active_tab = "chat"  # Track active tab

    def compose(self) -> ComposeResult:
        """Compose the chat interface layout with tabs."""
        yield Header(show_clock=True)

        # Tabbed content with chat, events, and artifacts tabs
        with TabbedContent(initial="chat"):
            # Chat tab
            with TabPane("Chat", id="chat"):
                yield ScrollableContainer(id="chat-scroll")

            # Events tab
            with TabPane("Events", id="events"):
                yield DataTable(id="events-table")

            # Artifacts tab
            with TabPane("Artifacts", id="artifacts"):
                yield Static(
                    "📁 **Artifact Tracking**\n\n"
                    "This pane shows artifacts created during the session.",
                    id="artifacts-info"
                )
                yield DataTable(id="artifacts-table")

        with Horizontal(id="input-container"):
            yield Input(placeholder="Type your message here...", id="message-input")
            yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the chat interface and start ADK integration."""
        load_dotenv()

        # Setup the events and artifacts tables
        self._setup_events_table()
        self._setup_artifacts_table()

        # Initial messages
        self._append_markdown_bubble("system", "**💬 Chat Interface Started**")
        self._append_markdown_bubble("system", "🔄 Starting ADK web server…")

        # Focus the input field
        self.query_one("#message-input", Input).focus()

        # Start ADK integration
        asyncio.create_task(self.initialize_adk())

    async def initialize_adk(self) -> None:
        """Initialize ADK web server and client."""
        try:
            if await self.start_adk_server():
                self.add_system_message("✅ ADK web server started")
                await asyncio.sleep(2)  # brief settle
                self.http_client = httpx.AsyncClient(timeout=None)
                self.adk_consumer = await ADKConsumer.create(self.http_client)
                self.connected = True
                self.add_system_message("✅ Connected to ADK agent — Ready to chat!")
            else:
                self.add_system_message("❌ Failed to start ADK web server")
        except Exception as e:
            self.add_system_message(f"❌ ADK initialization error: {str(e)}")

    async def start_adk_server(self) -> bool:
        """Start the ADK web server for the specified agents directory."""
        try:
            agents_path = Path(self.agents_dir)
            if not agents_path.exists():
                self.add_system_message(f"❌ Agents directory not found: {agents_path}")
                return False

            cmd = ["uv", "run", "adk", "web", str(agents_path), "--port", "8000"]
            self.adk_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path.cwd()
            )

            # Give the server time to start
            await asyncio.sleep(3)

            if self.adk_process.poll() is None:
                return True
            else:
                _, stderr = self.adk_process.communicate()
                self.add_system_message(
                    f"ADK server failed: {stderr.decode(errors='ignore')[:200]}..."
                )
                return False

        except Exception as e:
            self.add_system_message(f"Failed to start ADK server: {str(e)}")
            return False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-button":
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "message-input":
            self.send_message()

    def send_message(self) -> None:
        """Send a message from the input field."""
        message_input = self.query_one("#message-input", Input)
        message = message_input.value.strip()
        if not message:
            return

        # Clear the input
        message_input.value = ""

        # Display user bubble (render as markdown)
        self._append_markdown_bubble("user", message)

        # Send message to ADK agent
        if self.connected and self.adk_consumer:
            asyncio.create_task(self.handle_agent_response(message))
        else:
            self.add_system_message("❌ Not connected to ADK agent")

    async def handle_agent_response(self, message: str) -> None:
        """Handle sending message to agent and displaying response."""
        try:
            thinking = self._append_markdown_bubble("system", "🤔 Agent is thinking…")

            # Prepare an empty agent bubble that we'll update as chunks stream in
            self.current_agent_md = self._append_markdown_bubble("agent", "")
            buffer: list[str] = []

            if self.adk_consumer is None:
                self.add_system_message("❌ ADK consumer not initialized")
                return

            # Keep the active bubble visible as tokens arrive
            async for event_type, event_data in self.adk_consumer.message(text=message):
                if event_type == "Event:" and isinstance(event_data, dict):
                    extracted = extract_description_from_event(event_data)

                    # Store event record for Events tab
                    self._store_event_record(extracted)

                    # Check for artifact updates
                    if extracted.get("artifact_delta"):
                        self._handle_artifact_update(extracted)

                    # Handle different event types
                    if extracted["type"] == "STREAMING_TEXT_CHUNK":
                        if extracted["text"] and extracted["author"] != "user":
                            buffer.append(extracted["text"])
                            if self.current_agent_md:
                                await self.current_agent_md.update("".join(buffer))
                                self._scroll_to_active(self.current_agent_md)
                    elif extracted["type"] == "COMPLETE_TEXT":
                        if extracted["text"] and extracted["author"] != "user":
                            buffer.append(extracted["text"])
                            if self.current_agent_md:
                                await self.current_agent_md.update("".join(buffer))
                                self._scroll_to_active(self.current_agent_md)
                    elif extracted["type"] == "TOOL_CALL":
                        if extracted["function_calls"]:
                            num_calls = len(extracted['function_calls'])
                            tool_msg = f"*🔧 Calling {num_calls} tool(s)...*"
                            self.add_system_message(tool_msg)
                    elif extracted["type"] == "TOOL_RESULT":
                        if extracted["function_responses"]:
                            num_results = len(extracted['function_responses'])
                            result_msg = f"*✅ Received {num_results} tool result(s)*"
                            self.add_system_message(result_msg)
                    elif extracted["type"] == "ERROR":
                        if extracted["error"]:
                            error_msg = f"*❌ Agent error: {extracted['error']}*"
                            self.add_system_message(error_msg)

            # remove the “thinking” notice after we’re done
            try:
                await thinking.remove()
            except Exception:
                pass

            if not buffer:
                self.add_system_message("❌ No response from agent")

            # Ensure final message is in view
            if self.current_agent_md:
                self._scroll_to_active(self.current_agent_md)

        except Exception as e:
            self.add_system_message(f"❌ Error communicating with agent: {str(e)}")
        finally:
            self.current_agent_md = None

    async def on_exit(self) -> None:
        """Cleanup when exiting the application."""
        try:
            if self.http_client:
                await self.http_client.aclose()

            if self.adk_process and self.adk_process.poll() is None:
                self.adk_process.terminate()
                self.adk_process.wait(timeout=5)
        except Exception:
            pass  # Ignore cleanup errors


    def _append_markdown_bubble(self, role: str, md_text: str) -> Markdown:
        """Create and mount a Markdown bubble for a given role; returns the widget."""
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        # Strip trailing whitespace to avoid extra vertical slack
        bubble = Markdown(md_text.rstrip(), classes=f"msg {role}")
        scroll.mount(bubble)
        self._scroll_to_active(bubble)
        return bubble

    def _scroll_to_active(self, bubble: Markdown) -> None:
        """Scroll transcript to ensure `bubble` is visible after layout."""

        def _do_scroll() -> None:
            try:
                bubble.scroll_visible()
            except Exception:
                # If for any reason scroll_visible isn't available, do nothing;
                # ScrollableContainer handles wheel / key scrolling.
                pass

        # Run after next render/layout so geometry is final
        self.call_after_refresh(_do_scroll)

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat."""
        self._append_markdown_bubble("system", message)

    def _setup_events_table(self) -> None:
        """Setup the events table with columns."""
        table = self.query_one("#events-table", DataTable)
        table.add_columns("Time", "Type", "Author", "Text", "Function Calls", "Error")


    def _store_event_record(self, extracted: dict) -> None:
        """Store an event record and update the events table."""
        import time

        # Create a simplified record for the table
        record = {
            "time": time.strftime("%H:%M:%S"),
            "type": extracted.get("type", ""),
            "author": extracted.get("author", "") or "",
            "text": (
                (extracted.get("text", "") or "")[:50] +
                ("..." if len(extracted.get("text", "") or "") > 50 else "")
            ),
            "function_calls": (
                str(len(extracted.get("function_calls", []) or []))
                if extracted.get("function_calls") else ""
            ),
            "error": extracted.get("error", "") or ""
        }

        # Store full record
        self.event_records.append(extracted)

        # Add to table if events tab is active or table exists
        try:
            table = self.query_one("#events-table", DataTable)
            table.add_row(
                record["time"],
                record["type"],
                record["author"],
                record["text"],
                record["function_calls"],
                record["error"]
            )
        except Exception:
            pass  # Table might not be ready yet

    def _setup_artifacts_table(self) -> None:
        """Setup the artifacts table with columns."""
        try:
            table = self.query_one("#artifacts-table", DataTable)
            table.add_columns("Time", "Filename", "Version", "Size (bytes)", "Status")
        except Exception:
            pass  # Table might not be ready yet

    def _handle_artifact_update(self, extracted: dict) -> None:
        """Handle artifact creation/update events."""
        import time

        artifact_delta = extracted.get("artifact_delta", {})
        if not artifact_delta:
            return

        # Create artifact record
        artifact_record = {
            "time": time.strftime("%H:%M:%S"),
            "filename": "Unknown",
            "version": "Unknown",
            "size_bytes": "Unknown",
            "status": "Created",
            "delta": artifact_delta
        }

        # Try to extract filename/version from the delta or function calls
        function_calls = extracted.get("function_calls", [])
        if function_calls:
            for call in function_calls:
                if isinstance(call, dict) and call.get("name") == "save_text_artifact":
                    args = call.get("args", {})
                    if "filename" in args:
                        artifact_record["filename"] = args["filename"]
                    if "text" in args:
                        artifact_record["size_bytes"] = str(
                            len(args["text"].encode("utf-8"))
                        )

        # Try to get version from artifact delta keys
        if isinstance(artifact_delta, dict):
            for key, value in artifact_delta.items():
                if "version" in key.lower():
                    artifact_record["version"] = str(value)
                elif "filename" in key.lower():
                    artifact_record["filename"] = str(value)
                elif "size" in key.lower():
                    artifact_record["size_bytes"] = str(value)

        # Store the record
        self.artifact_records.append(artifact_record)

        # Add to artifacts table
        try:
            table = self.query_one("#artifacts-table", DataTable)
            table.add_row(
                artifact_record["time"],
                artifact_record["filename"],
                artifact_record["version"],
                artifact_record["size_bytes"],
                artifact_record["status"]
            )

            # Also show a system message about the artifact
            self.add_system_message(
                f"📁 Artifact created: {artifact_record['filename']}"
            )

        except Exception:
            pass  # Table might not be ready yet


def main():
    """Run the chat interface."""
    app = ChatInterface()
    app.title = "ADK Chat Interface"
    app.sub_title = "Terminal-based agent chat"
    app.run()


if __name__ == "__main__":
    main()
