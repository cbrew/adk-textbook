#!/usr/bin/env python3
"""
Simple Textual chat interface for ADK agents.

This provides a terminal-based chat UI that integrates with the ADK web server.
"""

import asyncio
import subprocess
from pathlib import Path

import httpx
from adk_consumer import ADKConsumer
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, RichLog


class ChatInterface(App):
    """A simple chat interface using Textual."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #chat-container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #chat-log {
        height: 1fr;
        background: $surface;
        border: none;
        padding: 1;
    }

    #input-container {
        height: auto;
        padding: 0 1;
        margin: 0 0 1 0;
    }

    #message-input {
        width: 1fr;
    }

    #send-button {
        width: auto;
        margin-left: 1;
    }

    .user-message {
        color: $accent;
    }

    .agent-message {
        color: $success;
    }

    .system-message {
        color: $warning;
    }
    """

    # Reactive variable to track connection status
    connected = reactive(False)

    def __init__(self, agents_dir: str = "agents"):
        super().__init__()
        self.message_count = 0
        self.agents_dir = agents_dir
        self.adk_consumer: ADKConsumer | None = None
        self.http_client: httpx.AsyncClient | None = None
        self.adk_process: subprocess.Popen | None = None

    def compose(self) -> ComposeResult:
        """Compose the chat interface layout."""
        yield Header(show_clock=True)

        with Container(id="chat-container"):
            yield RichLog(
                id="chat-log",
                highlight=True,
                markup=True,
                wrap=True,
            )

        with Horizontal(id="input-container"):
            yield Input(
                placeholder="Type your message here...",
                id="message-input",
            )
            yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the chat interface and start ADK integration."""
        # Load environment variables
        load_dotenv()

        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("💬 Chat Interface Started")
        chat_log.write("🔄 Starting ADK web server...")

        # Focus the input field
        self.query_one("#message-input", Input).focus()

        # Start ADK integration
        asyncio.create_task(self.initialize_adk())

    async def initialize_adk(self) -> None:
        """Initialize ADK web server and client."""
        try:
            # Start ADK web server
            if await self.start_adk_server():
                self.add_system_message("✅ ADK web server started")

                # Wait a moment for server to be ready
                await asyncio.sleep(2)

                # Initialize ADK consumer
                self.http_client = httpx.AsyncClient(timeout=None)
                self.adk_consumer = await ADKConsumer.create(self.http_client)
                self.connected = True
                self.add_system_message(
                    "✅ Connected to ADK agent - Ready to chat!"
                )
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

            # Start ADK web server
            cmd = ["uv", "run", "adk", "web", str(agents_path), "--port", "8000"]

            self.adk_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path.cwd()
            )

            # Give the server time to start
            await asyncio.sleep(3)

            # Check if process is still running
            if self.adk_process.poll() is None:
                return True
            else:
                # Process failed, get error output
                _, stderr = self.adk_process.communicate()
                self.add_system_message(
                    f"ADK server failed: {stderr.decode()[:200]}..."
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

        # Display user message
        chat_log = self.query_one("#chat-log", RichLog)
        self.message_count += 1
        chat_log.write(f"[bold blue]User[/bold blue]: {message}")

        # Send message to ADK agent
        if self.connected and self.adk_consumer:
            asyncio.create_task(self.handle_agent_response(message))
        else:
            self.add_system_message("❌ Not connected to ADK agent")

    async def handle_agent_response(self, message: str) -> None:
        """Handle sending message to agent and displaying response."""
        try:
            # Show thinking indicator
            self.add_system_message("🤔 Agent is thinking...")

            # Get response from ADK agent via streaming
            chat_log = self.query_one("#chat-log", RichLog)

            # Collect agent response parts
            agent_response_parts = []

            if self.adk_consumer is None:
                self.add_system_message("❌ ADK consumer not initialized")
                return

            async for event_type, event_data in self.adk_consumer.message(text=message):
                if event_type == "Event:" and isinstance(event_data, dict):
                    # Extract text from ADK SSE events
                    text_chunk = self._extract_text_from_event(event_data)
                    if text_chunk:
                        agent_response_parts.append(text_chunk)

            # Display complete agent response
            if agent_response_parts:
                full_response = "".join(agent_response_parts)
                chat_log.write(f"[bold green]Agent[/bold green]: {full_response}")
            else:
                self.add_system_message("❌ No response from agent")

        except Exception as e:
            self.add_system_message(f"❌ Error communicating with agent: {str(e)}")

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

    @staticmethod
    def _extract_text_from_event(event: dict) -> str:
        """Extract text content from ADK SSE event."""
        # Check if this is an agent response with content
        if event.get("author") and event.get("author") != "user":
            content = event.get("content")
            if content and isinstance(content, dict):
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, dict) and "text" in part:
                        return part["text"]
            # Handle direct text in content
            elif content and isinstance(content, str):
                return content
        # Handle events that might have direct text fields
        elif "text" in event:
            return event["text"]
        return ""

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(f"[bold yellow]System[/bold yellow]: {message}")


def main():
    """Run the chat interface."""
    app = ChatInterface()
    app.title = "ADK Chat Interface"
    app.sub_title = "Terminal-based agent chat"
    app.run()


if __name__ == "__main__":
    main()
