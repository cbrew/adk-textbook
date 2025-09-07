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

class ADKWebClient:
    """HTTP client for communicating with ADK web server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def create_session(self) -> bool:
        """Create a new ADK session."""
        create_session_url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
        create_payload = {"state": {"key1": "value1", "key2": 42}}
        r = await self.http_client.post(create_session_url, json=create_payload)
        r.raise_for_status()
        print("Session upserted:", r.json().get("id", SESSION_ID))
        self.session_id = SESSION_ID
    
    async def send_message(self, message: str) -> Optional[str]:
        """Send a message to the ADK agent and get response."""
        if not self.session_id:
            return None
        
        try:
            # Use the correct ADK API format


            run_payload = {
                "app_name": APP_NAME,
                "user_id": USER_ID,
                "session_id": SESSION_ID,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": "Talk to me about citation rings"}],
                },
            }
            response = await self.http_client.post(
                f"{self.base_url}/run",
                json=run_payload
            )
            
            if response.status_code == 200:
                events = response.json()  # Response is array of events directly
                
                # Extract agent response from events
                for event in events:
                    content = event.get("content")
                    if content and isinstance(content, dict):
                        parts = content.get("parts", [])
                        for part in parts:
                            if part.get("text"):
                                return part["text"]
                
                return "Agent response received but no text found."
            
            # Better error reporting
            try:
                error_detail = response.text
                return f"HTTP {response.status_code}: {error_detail[:100]}"
            except:
                return f"HTTP {response.status_code} error (no details available)"
            
        except Exception as e:
            return f"Connection error: {str(e)}"
    
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
                    self.add_system_message("✅ Connected to ADK agent - Ready to chat!")
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
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # Give the server time to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if self.adk_process.poll() is None:
                return True
            else:
                # Process failed, get error output
                _, stderr = self.adk_process.communicate()
                self.add_system_message(f"ADK server failed: {stderr.decode()[:200]}...")
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