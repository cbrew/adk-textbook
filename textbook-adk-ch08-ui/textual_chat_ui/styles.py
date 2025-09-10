"""
CSS styles for the Textual Chat UI.
"""

CHAT_INTERFACE_CSS = """
Screen {
    layout: vertical;
}

/* TabbedContent styling */
TabbedContent {
    height: 1fr;
    margin: 1;
    border: solid $primary;
}

/* Tab panes */
TabPane {
    padding: 1;
    background: $surface;
}

/* Events table styling - make it scrollable */
#events-table {
    height: 1fr;
    scrollbar-size: 1 1;
}

/* Artifacts layout styling */
#artifacts-container {
    layout: horizontal;
    height: 1fr;
}

#artifacts-list {
    width: 50%;
    height: 1fr;
    border: solid $primary;
    margin: 0 1 0 0;
}

#artifacts-viewer {
    width: 50%;
    height: 1fr;
    border: solid $primary;
    margin: 0 0 0 1;
}

/* Artifacts table styling */
#artifacts-table {
    height: 1fr;
    scrollbar-size: 1 1;
}

#artifacts-table:focus {
    border: solid $accent;
}

#artifacts-table > .datatable--cursor {
    background: $accent 50%;
}

/* Artifacts info styling */
#artifacts-info {
    height: auto;
    background: $panel;
    border: solid $primary;
    padding: 1;
    margin: 1;
}

/* Artifact viewer content */
#artifact-content {
    height: 1fr;
    padding: 1;
    background: $surface;
    border: solid $primary;
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

/* Modal styling */
#modal-content {
    width: 60;
    height: auto;
    background: $surface;
    border: solid $primary;
    padding: 2;
}

#modal-message {
    text-align: center;
    margin: 1 0;
    text-wrap: wrap;
}

#modal-ok {
    margin: 1 0 0 0;
    width: 1fr;
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
