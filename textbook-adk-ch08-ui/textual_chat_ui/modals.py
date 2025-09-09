"""
Modal components for the Textual Chat UI.
"""

import asyncio
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class SystemMessageModal(ModalScreen[None]):
    """A modal screen for displaying system messages with auto-dismiss."""
    
    def __init__(
        self, 
        message: str, 
        message_type: str = "info", 
        auto_dismiss_seconds: float = 3.0
    ) -> None:
        super().__init__()
        self.message = message
        self.message_type = message_type
        self.auto_dismiss_seconds = auto_dismiss_seconds
        self._auto_dismiss_task: asyncio.Task | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the modal content."""
        with Center():
            with Middle():
                with Vertical(id="modal-content"):
                    # Choose icon based on message type
                    if self.message_type == "error":
                        icon = "❌"
                    elif self.message_type == "success":
                        icon = "✅"
                    elif self.message_type == "warning":
                        icon = "⚠️"
                    else:
                        icon = "ℹ️"
                    
                    yield Label(f"{icon} {self.message}", id="modal-message")
                    yield Button("OK", variant="primary", id="modal-ok")
    
    def on_mount(self) -> None:
        """Start auto-dismiss timer when modal is mounted."""
        if self.auto_dismiss_seconds > 0:
            self._auto_dismiss_task = asyncio.create_task(self._auto_dismiss_after_delay())
    
    async def _auto_dismiss_after_delay(self) -> None:
        """Auto-dismiss the modal after the specified delay."""
        try:
            await asyncio.sleep(self.auto_dismiss_seconds)
            # Only dismiss if the task wasn't cancelled and modal is still mounted
            try:
                self.dismiss()
            except Exception:
                pass  # Modal might already be dismissed
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is fine
    
    def dismiss(self, result=None):
        """Dismiss the modal and cancel auto-dismiss task."""
        if self._auto_dismiss_task and not self._auto_dismiss_task.done():
            self._auto_dismiss_task.cancel()
        return super().dismiss(result)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to dismiss modal."""
        if event.button.id == "modal-ok":
            self.dismiss()
    
    def on_key(self, event) -> None:
        """Handle key press to dismiss modal."""
        if event.key in ("enter", "escape"):
            self.dismiss()