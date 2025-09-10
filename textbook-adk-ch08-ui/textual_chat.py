#!/usr/bin/env python3
"""
Simple Textual chat interface for ADK agents.

This is the new entry point using the modular package structure.
"""

from textual_chat_ui import ChatInterface


def main():
    """Run the chat interface."""
    app = ChatInterface()
    app.title = "ADK Chat Interface"
    app.sub_title = "Terminal-based agent chat"
    app.run()


if __name__ == "__main__":
    main()
