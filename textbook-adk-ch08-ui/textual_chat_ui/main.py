"""
Main ChatInterface class for the Textual Chat UI.
"""

import asyncio
import subprocess
from pathlib import Path

import httpx
from adk_consumer import ADKConsumer
from artifact_event_consumer import ArtifactEventConsumer
from dotenv import load_dotenv
from event_extractor import extract_description_from_event
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
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

from .handlers import ArtifactHandler, EventHandler
from .modals import SystemMessageModal
from .styles import CHAT_INTERFACE_CSS


class ChatInterface(App):
    """A simple chat interface using Textual, with scrollable compact bubbles."""

    CSS = CHAT_INTERFACE_CSS
    connected = reactive(False)

    def __init__(self, agents_dir: str = "agents"):
        super().__init__()
        self.message_count = 0
        self.agents_dir = agents_dir
        self.adk_consumer: ADKConsumer | None = None
        self.artifact_consumer: ArtifactEventConsumer | None = None
        self.http_client: httpx.AsyncClient | None = None
        self.adk_process: subprocess.Popen | None = None
        self.current_agent_md: Markdown | None = None  # live bubble while streaming
        self.event_records: list[dict] = []  # Store event records
        self.artifact_records: list[dict] = []  # Store artifact records
        self.artifact_content_cache: dict[str, str] = {}  # Cache artifact content
        self.active_tab = "chat"  # Track active tab
        self.current_modal: SystemMessageModal | None = None  # Track current modal

        # Initialize handlers
        self.event_handler = EventHandler(self)
        self.artifact_handler = ArtifactHandler(self)

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

            # Artifacts tab with split-screen layout
            with TabPane("Artifacts", id="artifacts"):
                yield Static(
                    "📁 **Artifact Tracking** - Click on an artifact to view content",
                    id="artifacts-info",
                )
                with Horizontal(id="artifacts-container"):
                    with Vertical(id="artifacts-list"):
                        yield DataTable(id="artifacts-table")
                    with Vertical(id="artifacts-viewer"):
                        yield Static(
                            "Select an artifact from the list to view content here.",
                            id="artifact-content",
                        )

        with Horizontal(id="input-container"):
            yield Input(placeholder="Type your message here...", id="message-input")
            yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the chat interface and start ADK integration."""
        load_dotenv()

        # Setup the events and artifacts tables
        self.event_handler.setup_events_table()
        self.artifact_handler.setup_artifacts_table()

        # Initial messages
        self._append_markdown_bubble("system", "**💬 Chat Interface Started**")
        self.update_status("🔄 Starting ADK web server…")

        # Focus the input field
        self.query_one("#message-input", Input).focus()

        # Start ADK integration
        asyncio.create_task(self.initialize_adk())

    async def initialize_adk(self) -> None:
        """Initialize ADK web server and client."""
        try:
            if await self.start_adk_server():
                self.update_status("✅ ADK web server started")
                await asyncio.sleep(2)  # brief settle
                self.http_client = httpx.AsyncClient(timeout=None)
                self.adk_consumer = await ADKConsumer.create(self.http_client)
                self.artifact_consumer = ArtifactEventConsumer(self.adk_consumer)
                self.connected = True
                self.update_status("✅ Connected to ADK agent — Ready to chat!")
            else:
                self.update_status("❌ Failed to start ADK web server")
        except Exception as e:
            self.update_status(f"❌ ADK initialization error: {str(e)}")

    async def start_adk_server(self) -> bool:
        """Start the ADK web server for the specified agents directory."""
        try:
            agents_path = Path(self.agents_dir)
            if not agents_path.exists():
                self.update_status(f"❌ Agents directory not found: {agents_path}")
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
                self.update_status(
                    f"ADK server failed: {stderr.decode(errors='ignore')[:200]}..."
                )
                return False

        except Exception as e:
            self.update_status(f"Failed to start ADK server: {str(e)}")
            return False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-button":
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "message-input":
            self.send_message()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in data tables."""
        if event.data_table.id == "artifacts-table":
            self._handle_artifact_selection(event)

    def _handle_artifact_selection(self, event: DataTable.RowSelected) -> None:
        """Handle artifact table row selection to display content."""
        try:
            # Get the row key - in Textual DataTable, row_key is the index
            row_key = event.row_key

            # Convert row_key to index for our artifact_records list
            try:
                # Try to get the row data using the row_key
                table = event.data_table
                row_data = table.get_row(row_key)

                # Find the matching artifact record by filename
                # Filename is in column 1 (index 0 is time)
                if len(row_data) >= 2:
                    filename_from_row = str(row_data[1])  # Filename column

                    # Find matching record in our artifact_records list
                    row_index = None
                    for i, record in enumerate(self.artifact_records):
                        if record.get("filename", "") == filename_from_row:
                            row_index = i
                            break

                    if row_index is None:
                        row_index = 0  # Default to first record
                else:
                    row_index = 0

            except Exception:
                # Fallback: try to convert row_key directly to int
                try:
                    row_index = int(str(row_key))
                except (ValueError, TypeError):
                    row_index = 0  # Default to first row

            # Ensure row_index is valid
            if 0 <= row_index < len(self.artifact_records):
                artifact_record = self.artifact_records[row_index]
                filename = artifact_record.get("filename", "Unknown")

                # Try to get content from cache first, then retrieve if needed
                content_to_display = self.artifact_handler.get_artifact_content(
                    filename, artifact_record
                )

                # Update the artifact viewer with a clear header
                content_widget = self.query_one("#artifact-content", Static)
                display_content = f"## 📄 {filename}\n\n{content_to_display}"
                content_widget.update(display_content)

                # If we don't have the actual content cached, try to retrieve it
                cache_missing = filename not in self.artifact_content_cache
                cache_has_placeholder = (
                    not cache_missing
                    and self.artifact_content_cache[filename].startswith(
                        "**Artifact Information:**"
                    )
                )
                if cache_missing or cache_has_placeholder:
                    asyncio.create_task(
                        self._retrieve_and_display_artifact(filename, artifact_record)
                    )

                # Add a debug message to status line
                self.update_status(f"🔍 Viewing artifact: {filename}")
            else:
                # Row index out of bounds
                content_widget = self.query_one("#artifact-content", Static)
                content_widget.update(f"❌ Invalid row selection (index {row_index})")

        except Exception as e:
            # If selection fails, show error message
            try:
                content_widget = self.query_one("#artifact-content", Static)
                content_widget.update(f"❌ Error loading artifact: {str(e)}")
                # Also add debug info to status
                self.update_status(f"⚠️ Artifact selection error: {str(e)}")
            except Exception:
                pass  # Ignore if we can't update the content widget

    async def _retrieve_and_display_artifact(
        self, filename: str, artifact_record: dict
    ) -> None:
        """Retrieve artifact content from the agent and update the display."""
        try:
            # Show loading message
            content_widget = self.query_one("#artifact-content", Static)
            content_widget.update(f"## 📄 {filename}\n\n🔄 Loading artifact content...")

            if not self.connected or not self.adk_consumer:
                content_widget.update(f"## 📄 {filename}\n\n❌ Not connected to agent")
                return

            # Send a message to the agent to retrieve the artifact
            retrieve_message = (
                f"Use the retrieve_artifact tool to load the content of "
                f"the file named '{filename}'. Please retrieve this artifact."
            )

            # Track if we got content from the retrieve call
            retrieved_content = None

            async for event_type, event_data in self.adk_consumer.message(
                text=retrieve_message
            ):
                if event_type == "Event:" and isinstance(event_data, dict):
                    # Use enhanced artifact consumer for processing
                    if self.artifact_consumer:
                        enhanced_info = (
                            self.artifact_consumer.extract_enhanced_event_info(
                                event_data
                            )
                        )

                        # Debug: Log event types we're seeing
                        event_type_received = enhanced_info.get("type", "UNKNOWN")
                        retrieval_events = [
                            "ARTIFACT_RETRIEVAL_CALL",
                            "ARTIFACT_RETRIEVAL_RESPONSE",
                        ]
                        if event_type_received in retrieval_events:
                            self.update_status(
                                f"🔍 Debug: Received {event_type_received} event"
                            )

                        # Look for retrieve_artifact function responses
                        function_responses = enhanced_info.get("function_responses", [])
                        # Safety check to prevent iteration on None
                        if function_responses:
                            for resp in function_responses:
                                is_retrieve = (
                                    isinstance(resp, dict)
                                    and resp.get("name") == "retrieve_artifact"
                                )
                                if is_retrieve:
                                    response_data = resp.get("response", {})
                                    if isinstance(response_data, dict):
                                        if response_data.get("status") == "success":
                                            retrieved_content = response_data.get(
                                                "content", ""
                                            )
                                            content_length = response_data.get(
                                                "content_length", len(retrieved_content)
                                            )
                                            mime_type = response_data.get(
                                                "mime_type", "text/plain"
                                            )

                                            # Cache the retrieved content
                                            self.artifact_content_cache[filename] = (
                                                retrieved_content
                                            )

                                            # Update the display with the actual content
                                            display_content = f"""**Content:**

{retrieved_content}

---
**Metadata:**
- Status: {artifact_record.get("status", "Unknown")}
- Version: {artifact_record.get("version", "Unknown")}
- Size: {content_length} characters
- MIME Type: {mime_type}
- Retrieved: Just now"""

                                            content_widget.update(
                                                f"## 📄 {filename}\n\n{display_content}"
                                            )
                                            self.update_status(
                                                f"✅ Retrieved content for: {filename}"
                                            )
                                            return

                                        elif response_data.get("status") == "error":
                                            error_msg = response_data.get(
                                                "error", "Unknown error"
                                            )
                                            content_widget.update(
                                                f"## 📄 {filename}\n\n❌ {error_msg}"
                                            )
                                            self.update_status(
                                                f"❌ Failed to retrieve: {filename}"
                                            )
                                            return

            # If we get here, no retrieve_artifact response was found
            if retrieved_content is None:
                fallback_content = self.artifact_handler.get_artifact_content(
                    filename, artifact_record
                )
                fallback_text = (
                    f"## 📄 {filename}\n\n{fallback_content}\n\n"
                    f"💡 **Auto-retrieval failed**\n"
                    f"Try manually asking: 'Please retrieve the content of {filename}'"
                )
                content_widget.update(fallback_text)
                self.update_status(
                    f"⚠️ Auto-retrieval failed for {filename} - "
                    f"agent may not have called retrieve_artifact tool"
                )

        except Exception as e:
            try:
                content_widget = self.query_one("#artifact-content", Static)
                content_widget.update(
                    f"## 📄 {filename}\n\n❌ Error retrieving content: {str(e)}"
                )
                self.update_status(f"⚠️ Retrieval error for {filename}: {str(e)}")
            except Exception:
                pass  # Ignore if we can't update the widget

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
            self.update_status("❌ Not connected to ADK agent")

    async def handle_agent_response(self, message: str) -> None:
        """Handle sending message to agent and displaying response."""
        try:
            thinking = self._append_markdown_bubble("system", "🤔 Agent is thinking…")

            # Prepare an empty agent bubble that we'll update as chunks stream in
            self.current_agent_md = self._append_markdown_bubble("agent", "")
            buffer: list[str] = []

            if self.adk_consumer is None:
                self.update_status("❌ ADK consumer not initialized")
                return

            # Keep the active bubble visible as tokens arrive
            async for event_type, event_data in self.adk_consumer.message(text=message):
                if event_type == "Event:" and isinstance(event_data, dict):
                    # Use enhanced artifact consumer for better event processing
                    if self.artifact_consumer:
                        enhanced_info = (
                            self.artifact_consumer.extract_enhanced_event_info(
                                event_data
                            )
                        )
                        self.event_handler.store_event_record(enhanced_info)
                        self.artifact_handler.handle_enhanced_artifact_update(
                            enhanced_info
                        )
                        event_type_to_use = enhanced_info["type"]
                        text_to_use = enhanced_info["text"]
                        author_to_use = enhanced_info["author"]
                    else:
                        # Fallback to original extractor
                        enhanced_info = extract_description_from_event(event_data)
                        self.event_handler.store_event_record(enhanced_info)
                        self.artifact_handler.handle_artifact_update(enhanced_info)
                        event_type_to_use = enhanced_info["type"]
                        text_to_use = enhanced_info["text"]
                        author_to_use = enhanced_info["author"]

                    # Handle different event types with enhanced classifications
                    await self._handle_event_type(
                        event_type_to_use,
                        text_to_use,
                        author_to_use,
                        enhanced_info,
                        buffer,
                    )

            # remove the "thinking" notice after we're done
            try:
                await thinking.remove()
            except Exception:
                pass

            if not buffer:
                self.update_status("❌ No response from agent")

            # Ensure final message is in view
            if self.current_agent_md:
                self._scroll_to_active(self.current_agent_md)

            # Set ready status after response is complete
            self.set_ready_status()

        except Exception as e:
            self.update_status(f"❌ Error communicating with agent: {str(e)}")
        finally:
            self.current_agent_md = None

    async def _handle_event_type(
        self,
        event_type: str,
        text: str,
        author: str,
        enhanced_info: dict,
        buffer: list[str],
    ) -> None:
        """Handle different types of events from the agent."""
        if event_type == "STREAMING_TEXT_CHUNK":
            if text and author != "user":
                buffer.append(text)
                if self.current_agent_md:
                    await self.current_agent_md.update("".join(buffer))
                    self._scroll_to_active(self.current_agent_md)
        elif event_type == "COMPLETE_TEXT":
            # Only use complete text if we haven't been streaming (buffer is empty)
            if text and author != "user" and not buffer:
                buffer.append(text)
                if self.current_agent_md:
                    await self.current_agent_md.update("".join(buffer))
                    self._scroll_to_active(self.current_agent_md)
        elif event_type in [
            "TOOL_CALL",
            "ARTIFACT_CREATION_CALL",
            "ARTIFACT_RETRIEVAL_CALL",
        ]:
            self._handle_tool_call_event(event_type, enhanced_info)
        elif event_type in [
            "TOOL_RESULT",
            "ARTIFACT_CREATION_RESPONSE",
            "ARTIFACT_RETRIEVAL_RESPONSE",
        ]:
            self._handle_tool_result_event(event_type, enhanced_info)
        elif event_type == "ARTIFACT_UPDATE":
            self._handle_artifact_update_event(enhanced_info)
        elif event_type == "ERROR":
            self._handle_error_event(enhanced_info)

    def _handle_tool_call_event(self, event_type: str, enhanced_info: dict) -> None:
        """Handle tool call events."""
        function_calls = enhanced_info.get("function_calls", [])
        if function_calls:
            num_calls = len(function_calls)
            if event_type == "ARTIFACT_CREATION_CALL":
                tool_msg = "📁 Creating artifact..."
            elif event_type == "ARTIFACT_RETRIEVAL_CALL":
                tool_msg = "🔍 Retrieving artifact..."
            else:
                tool_msg = f"🔧 Calling {num_calls} tool(s)..."
            self.update_status(tool_msg)

    def _handle_tool_result_event(self, event_type: str, enhanced_info: dict) -> None:
        """Handle tool result events."""
        function_responses = enhanced_info.get("function_responses", [])
        if function_responses:
            if event_type == "ARTIFACT_CREATION_RESPONSE":
                # Get artifact filename from the response
                artifact_name = "artifact"
                for resp in function_responses:
                    if isinstance(resp, dict):
                        response_data = resp.get("response", {})
                        if isinstance(response_data, dict):
                            filename = response_data.get("filename", "")
                            if filename:
                                artifact_name = filename
                                break
                tool_msg = f"📁 Artifact '{artifact_name}' created successfully"
            elif event_type == "ARTIFACT_RETRIEVAL_RESPONSE":
                # Get artifact filename from the response
                artifact_name = "artifact"
                status = "retrieved"
                for resp in function_responses:
                    if isinstance(resp, dict):
                        response_data = resp.get("response", {})
                        if isinstance(response_data, dict):
                            filename = response_data.get("filename", "")
                            resp_status = response_data.get("status", "unknown")
                            if filename:
                                artifact_name = filename
                            if resp_status:
                                status = resp_status
                            break
                if status == "success":
                    tool_msg = f"🔍 Artifact '{artifact_name}' retrieved successfully"
                else:
                    tool_msg = f"❌ Failed to retrieve artifact '{artifact_name}'"
            else:
                num_results = len(function_responses)
                tool_msg = f"✅ Received {num_results} tool result(s)"
            self.update_status(tool_msg)

    def _handle_artifact_update_event(self, enhanced_info: dict) -> None:
        """Handle artifact update events."""
        artifact_delta = enhanced_info.get("artifact_delta", {})
        if artifact_delta:
            filenames = list(artifact_delta.keys())
            if filenames:
                tool_msg = f"*📁 Updated artifacts: {', '.join(filenames)}*"
                self.add_system_message(tool_msg)

    def _handle_error_event(self, enhanced_info: dict) -> None:
        """Handle error events."""
        error_msg_text = enhanced_info.get("error")
        if error_msg_text:
            error_msg = f"*❌ Agent error: {error_msg_text}*"
            self.add_system_message(error_msg)

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

    def show_status_modal(self, message: str, message_type: str = "info") -> None:
        """Show a status message in a modal popup."""
        if message.strip():  # Only show modal for non-empty messages
            # Dismiss any existing modal first
            if self.current_modal is not None:
                try:
                    self.current_modal.dismiss()
                except Exception:
                    pass  # Modal might already be dismissed

            # Create and show new modal
            self.current_modal = SystemMessageModal(message.strip(), message_type)
            self.push_screen(self.current_modal)

    def update_status(self, message: str) -> None:
        """Update status by showing a modal popup."""
        # Determine message type based on content
        if "❌" in message or "error" in message.lower() or "failed" in message.lower():
            message_type = "error"
        elif (
            "✅" in message
            or "success" in message.lower()
            or "connected" in message.lower()
        ):
            message_type = "success"
        elif "⚠️" in message or "warning" in message.lower():
            message_type = "warning"
        else:
            message_type = "info"

        # Only show important status updates as modals (skip debug messages)
        important_keywords = ["Starting", "Connected", "Failed", "Error", "Ready"]
        if any(keyword in message for keyword in important_keywords):
            self.show_status_modal(message, message_type)

    def set_ready_status(self) -> None:
        """Show ready status."""
        # Don't show a modal for ready status, just add a system message
        self.add_system_message("💬 Ready to chat")
