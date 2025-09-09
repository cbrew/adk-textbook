# Chapter 8 UI - Textual Chat Interface

A sophisticated chat interface for Google's Agent Development Kit (ADK) built with the Textual framework. This interface provides real-time agent interaction with advanced artifact management capabilities.

## Features

- **🗣️ Real-time Chat** - Interactive conversation with ADK agents
- **📁 Artifact Management** - Create, view, and retrieve artifacts with split-screen interface
- **📊 Event Monitoring** - Live event tracking and analysis
- **🎨 Professional UI** - Modal notifications with auto-dismiss functionality
- **🏗️ Modular Architecture** - Clean, maintainable codebase structure

## Quick Start

### Prerequisites
- Python 3.11+
- `uv` package manager
- ADK agents configured in the `agents/` directory

### Installation
```bash
# Install dependencies
uv install

# Start the chat interface
python textual_chat.py
```

### Usage
1. **Chat Tab** - Interactive conversation with your agent
2. **Events Tab** - Monitor real-time ADK events 
3. **Artifacts Tab** - Browse and view created artifacts

## Architecture

### Modular Package Structure
```
textual_chat_ui/
├── __init__.py          # Package entry point
├── main.py             # Core ChatInterface (300 lines)
├── modals.py          # Modal system with auto-dismiss (70 lines)
├── handlers.py        # Event & artifact processing (250 lines)
└── styles.py          # CSS styling (130 lines)
```

### Key Components

#### **ChatInterface** (`main.py`)
- Main application class extending Textual's `App`
- Handles ADK server management and client connections
- Orchestrates UI components and event processing

#### **SystemMessageModal** (`modals.py`)
- Professional modal notifications
- Auto-dismiss after 3 seconds (configurable)
- Smart message type detection (error/success/warning/info)

#### **Event & Artifact Handlers** (`handlers.py`)
- `EventHandler` - Processes and displays ADK events
- `ArtifactHandler` - Manages artifact creation and retrieval
- Content caching and split-screen artifact viewing

#### **CSS Styling** (`styles.py`)
- Comprehensive UI styling
- Responsive layout with tabbed interface
- Professional modal and chat bubble design

## ADK Integration

### Agent Configuration
The interface works with any ADK agent. Example configuration:

```python
# agents/simple_chat_agent/agent.py
class SimpleChatAgent(Agent):
    def __init__(self):
        super().__init__(
            name="simple_chat_agent",
            model=LiteLlm(model="gpt-4"),
            tools=[
                FunctionTool(save_text_artifact),
                FunctionTool(retrieve_artifact)
            ]
        )
```

### Artifact Tools
- **`save_text_artifact(text, filename)`** - Save content as artifact
- **`retrieve_artifact(filename)`** - Retrieve artifact content

## File Overview

| File | Purpose | Lines |
|------|---------|-------|
| `textual_chat.py` | Main entry point | 15 |
| `chat_app.py` | CLI chat application | 140 |
| `adk_consumer.py` | ADK client wrapper | 100 |
| `event_extractor.py` | Event processing logic | 180 |
| `artifact_event_consumer.py` | Enhanced artifact tracking | 350 |
| `textual_chat_old.py` | Legacy monolithic version | 1000+ |

### Documentation
- `docs/` - Technical documentation and analysis reports
- `README.md` - This file

### Agents
- `agents/simple_chat_agent/` - Example ADK agent configuration

## Development

### Code Quality
- Type annotations throughout
- Comprehensive error handling
- Modular, testable architecture
- Clean separation of concerns

### Testing
```bash
# Run type checking
pyright textual_chat_ui/

# Test imports
python -c "from textual_chat_ui import ChatInterface; print('✅ Import successful')"

# Start development server
python textual_chat.py
```

## Architecture Benefits

### Before Refactoring
- Single 1000+ line file
- Difficult to maintain and debug
- Mixed concerns (UI, logic, styling)
- Hard to test individual components

### After Refactoring  
- 4 focused modules (~200 lines each)
- Clear separation of concerns
- Easy to maintain and extend
- Testable components
- Professional UI with modal system

## Contributing

This codebase follows the ADK textbook's development standards:
- Small, focused commits
- Comprehensive testing
- Clear documentation
- Type safety throughout