#!/usr/bin/env python3
"""
Launcher for Research Grounding Panel.

Starts the Textual UI (connects to server on localhost:8000).
"""

from ui import GroundingPanelApp


def main():
    """Run the grounding panel Textual UI."""
    app = GroundingPanelApp()
    app.run()


if __name__ == "__main__":
    main()
