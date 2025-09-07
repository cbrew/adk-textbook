#!/usr/bin/env python3
"""
Simple Textual chat interface for ADK agents.

This provides a terminal-based chat UI that integrates with the ADK web server.
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional
import uuid

import httpx
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Input, RichLog, Static
from textual.reactive import reactive
from dotenv import load_dotenv


BASE_URL = "http://localhost:8000"
APP_NAME = "simple_chat_agent"
USER_ID = "u_123"
SESSION_ID = "s_127"




class ADKConsumer:
    BASE_URL = "http://localhost:8000"
    APP_NAME = "simple_chat_agent"
    USER_ID = "u_123"
    SESSION_ID = str(uuid.uuid4())
    def __init__(self, client: httpx.AsyncClient):
        self.client: httpx.AsyncClient = client

    @classmethod
    async def create(cls, param):
        # Perform async operations to get resources
        resource = await _init_consumer_async(param)
        return cls(resource)

    async def message(self, text: str= "Talk to me about citation rings"):
        run_sse_url = f"{self.BASE_URL}/run_sse"
        run_payload = {
            "app_name": self.APP_NAME,
            "user_id": self.USER_ID,
            "session_id": self.SESSION_ID,
            "new_message": {
                "role": "user",
                "parts": [{"text": text}],
            },
            # Optional but fine to include:
            "streaming": True,
        }

        async with self.client.stream("POST", run_sse_url, json=run_payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                # SSE lines look like: "data: {...json...}"
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[len("data: "):])
                        yield "Event:",event
                    except json.JSONDecodeError:
                        yield "Non-JSON SSE data:",line



async def _init_consumer_async(client: httpx.AsyncClient) -> httpx.AsyncClient:
    "Helper function for creation of ADK consumer."
    create_session_url = f"{ADKConsumer.BASE_URL}/apps/{ADKConsumer.APP_NAME}/users/{ADKConsumer.USER_ID}/sessions/{ADKConsumer.SESSION_ID}"
    create_payload = {"state": {"key1": "value1", "key2": 42}}
    r = await client.post(create_session_url, json=create_payload)
    r.raise_for_status()
    return client


class ADKWebClient:
    """HTTP client for communicating with ADK web server."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.adk_consumer = None

    async def create_session(self) -> bool:
        """Create a new ADK session."""
        self.adk_consumer = await ADKConsumer.create(self.http_client)

    async def send_message(self, message: str) -> Optional[str]:
        """Send a message to the ADK agent and get response."""

        async for sse_event in self.adk_consumer.message(text=message):
            print(sse_event)

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()


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
        self.adk_client: Optional[ADKWebClient] = None
        self.adk_process: Optional[subprocess.Popen] = None

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

                # Initialize client and create session
                self.adk_client = ADKWebClient()
                if await self.adk_client.create_session():
                    self.connected = True
                    self.add_system_message(
                        "✅ Connected to ADK agent - Ready to chat!"
                    )
                else:
                    self.add_system_message("❌ Failed to create ADK session")
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
        if self.connected and self.adk_client:
            asyncio.create_task(self.handle_agent_response(message))
        else:
            self.add_system_message("❌ Not connected to ADK agent")

    async def handle_agent_response(self, message: str) -> None:
        """Handle sending message to agent and displaying response."""
        try:
            # Show thinking indicator
            self.add_system_message("🤔 Agent is thinking...")

            # Get response from ADK agent
            response = await self.adk_client.send_message(message)

            if response:
                self.add_agent_response(response)
            else:
                self.add_system_message("❌ No response from agent")

        except Exception as e:
            self.add_system_message(f"❌ Error communicating with agent: {str(e)}")

    async def on_exit(self) -> None:
        """Cleanup when exiting the application."""
        try:
            if self.adk_client:
                await self.adk_client.close()

            if self.adk_process and self.adk_process.poll() is None:
                self.adk_process.terminate()
                self.adk_process.wait(timeout=5)
        except Exception:
            pass  # Ignore cleanup errors

    def add_agent_response(self, response: str) -> None:
        """Add an agent response to the chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(f"[bold green]Agent[/bold green]: {response}")

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
