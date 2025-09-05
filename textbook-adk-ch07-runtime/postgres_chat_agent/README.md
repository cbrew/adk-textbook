# Academic Research Assistant - PostgreSQL Edition

## What This Application Does

This is an **Academic Research Assistant** that demonstrates PostgreSQL-backed persistence for professional academic workflows. It provides two interaction modes:

### 1. **Conversational AI Mode** (Primary Interface)
- Natural language conversations about research topics
- AI assistant helps with academic tasks
- Automatic integration with PostgreSQL services for persistence
- Session continuity across restarts

### 2. **Direct Service Access Mode** (Slash Commands)
- `/memory <query>` - Direct search of PostgreSQL memory service
- `/save <topic>` - Direct save to PostgreSQL memory service
- `/artifacts` - Direct listing of PostgreSQL artifact service
- `/session` - Direct access to PostgreSQL session service info
- `/help` - Show command reference

## Technical Architecture

```
User Input
    ↓
[Slash Command?] ────Yes────→ Direct PostgreSQL Service Call
    ↓ No                           ↓
ADK Runner                    Display Results
    ↓
Agent + Tools ────────────→ PostgreSQL Services
    ↓                           ↓
AI Response               Persistent Storage
```

## PostgreSQL Services Integration

**Session Service:**
- Tracks conversation state, interaction counts
- Manages academic research sessions
- Provides continuity across application restarts

**Memory Service:**
- Stores conversation content for semantic search
- Enables research memory across sessions
- Supports academic knowledge building

**Artifact Service:**
- Stores research documents, notes, bibliographies
- Version-controlled academic artifact management
- File-based persistence with PostgreSQL metadata

## Installation & Setup

### Prerequisites
- PostgreSQL containers running (see main README)
- Python 3.11+ with uv package manager
- API keys for AI models (optional for basic testing)

### Database Setup
```bash
# From textbook root
make dev-up        # Start PostgreSQL containers
make migrate       # Apply database schema
```

### Running the Application
```bash
# From textbook-adk-ch07-runtime directory
uv run python postgres_chat_agent/main.py
```

## Usage Examples

### Academic Conversation
```
🗣️  You: I'm researching machine learning applications in academic literature analysis
🎓 Assistant: That's a fascinating research area! Machine learning has revolutionized how we can...
```

### Direct Service Access
```
🗣️  You: /save machine learning literature analysis
💾 Saving 'machine learning literature analysis' to research memory...
✅ Saved 'machine learning literature analysis' to research memory! (Total saves: 1)

🗣️  You: /memory machine learning
🔍 Searching research memory for: 'machine learning'
📚 Found 1 relevant research memories:
  1. Session conversation about machine learning applications in academic literature analysis...

🗣️  You: /artifacts
📁 Listing research artifacts...
📚 Found 2 research artifact(s):
  1. bibliography_ml_papers.txt
  2. literature_analysis_notes.md
```

## Known Limitations & Issues

### Confirmed Issues (Tested 2025-09-04)

1. **✅ FIXED - Session object missing created_at/updated_at attributes**
   - `/session` command was throwing exceptions
   - Fixed with defensive attribute access using `getattr()`

2. **🔍 INVESTIGATION NEEDED - Memory search returns malformed data**
   - Memory search returns `('memories', [])` instead of actual content
   - Memory service `add_session_to_memory` appears to work (logs show content added)
   - Memory service `search_memory` returns incorrect data structure
   - Affects both slash commands and agent tools

3. **✅ WORKING - Artifact service functions correctly**
   - All CRUD operations tested and working
   - Save, list, retrieve, delete all functional

4. **✅ WORKING - Session management functions correctly**
   - Session creation, retrieval, state updates all functional
   - Proper UUID generation and session continuity

5. **❓ UNTESTED - Agent conversation flow with AI models**
   - Requires API keys for full testing
   - May fail if AI model not properly configured

### Error Handling Status
- ✅ Database connection errors handled gracefully
- ✅ Missing sessions handled (creates new automatically)
- ✅ Service call failures show error messages
- ✅ Invalid slash commands show help
- ❌ Memory service malfunction not properly detected

### Error Handling
The application attempts to handle errors gracefully:
- Database connection failures → Error messages, graceful shutdown
- Missing sessions → Creates new session automatically  
- Service call failures → Error messages, continues operation
- Invalid slash commands → Help message display

### Testing Requirements
Before using this application:

1. **Verify PostgreSQL is running:**
   ```bash
   uv run python postgres_chat_agent/driver.py --list-sessions
   ```

2. **Test basic service functionality:**
   ```bash
   uv run python postgres_chat_agent/driver.py --test-memory
   uv run python postgres_chat_agent/driver.py --test-artifacts
   ```

3. **Verify AI model access (optional):**
   - Set ANTHROPIC_API_KEY or OPENAI_API_KEY in environment
   - Test with simple conversation

## Troubleshooting

### Common Issues

**"Runtime not initialized" errors:**
- PostgreSQL containers not running
- Database schema not migrated
- Connection configuration incorrect

**Empty memory searches:**
- No content has been saved to memory yet
- Use `/save <topic>` to build research memory first

**Agent conversation failures:**
- Missing or invalid AI model API keys
- Network connectivity issues
- Model rate limiting

**Slash commands not working:**
- Commands must start with `/` exactly
- Check spelling: `/memory` not `/memories`
- Some commands require parameters: `/memory <query>`

### Debug Mode
For detailed error information, check the console output. The application logs:
- Service initialization status
- Database operation results
- Error details with stack traces
- Session state changes

## Development Notes

This application demonstrates:
- **Custom ADK Runtime integration** - PostgreSQL services replace ADK defaults
- **Dual interaction patterns** - AI conversation + direct service access
- **Academic workflow optimization** - Research-focused features
- **Error handling patterns** - Graceful degradation when services fail
- **Session continuity** - Persistent state across application restarts

The slash commands provide direct access to PostgreSQL services, bypassing the AI layer for power users who want immediate database operations.