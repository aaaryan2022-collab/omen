# Current OMEN Audit

## Architecture Overview
OMEN is built as an extensible, modular Windows Desktop AI Operating Layer with PyQt6, Python 3.14+, SQLite, ChromaDB, and local/cloud model runtimes.

- **Core Engine**: `core/agent.py`, `core/supervisor.py`, `core/event_bus.py`, `core/intent_router.py`, `core/planner.py`, `core/executor.py`
- **Security & Permissions**: `security/permissions.py`, `security/audit.py`, `security/boundaries.py`
- **Model Providers**: `providers/llm/` (Ollama, LMStudio, OpenAI, Anthropic, Gemini, fallback heuristic engine)
- **Voice System**: `voice/stt.py`, `voice/tts.py`, `providers/stt/speech_rec.py`, `providers/tts/pyttsx_provider.py`
- **Vision & Screen**: `vision/screen_capture.py`, `vision/ocr_engine.py` (Tesseract integration)
- **Tools**: 12+ built-in modules (`tools/system/`, `tools/filesystem/`, `tools/browser/`, `tools/email/`, `tools/productivity/`, `tools/news/`, `tools/media/`)
- **Memory & Storage**: SQLite database (`database/`), ChromaDB vector store (`data/vector_memory/`), short-term buffer & persistent facts
- **Productivity & Workspace**: `productivity/tasks.py`, `productivity/calendar.py`, `productivity/notes.py`, `productivity/routines.py`
- **UI Architecture**: PyQt6 desktop UI (`ui/main_window.py`, `ui/orb.py`, `ui/sidebar.py`, `ui/command_palette.py`, `ui/views/`)
- **Testing**: 23/23 tests passing in `tests/` (`test_modules.py`, `test_smoke.py`, `test_ui_omen.py`)

## Technical Debt & Gaps Identified
1. **Developer & Coding Agent Features (from Marven)**:
   - Need unified diff viewer / editor integration.
   - Need terminal emulator PTY integration.
   - Need Git panel / repository management actions.
   - Need checkpoint store for undoing agent file edits.
2. **Advanced Screen & Browser Perception (from OpenGuider)**:
   - Need visual pointer tool overlay and human-in-the-loop risk scorer for Playwright automation.
3. **Enterprise Extensibility & Multi-Agent (from OpenJarvis)**:
   - Need Model Context Protocol (MCP) client.
   - Need Deep Research agent.
   - Need modular Skills registry.
   - Need execution trace collector and `omen doctor` CLI command.
4. **Google Workspace Connectors (from Alice)**:
   - Need OAuth2 Google Calendar and Gmail connector abstraction.

## Migration & Enhancement Strategy
- Build directly upon the existing, working Python/PyQt6 architecture without breaking any existing functionality.
- Integrate the missing modules: `core/mcp/`, `core/skills/`, `core/research/`, `core/sandbox/`, `core/traces/`, `tools/coding/`, and CLI `omen doctor`.
- Maintain 100% test pass rate across the test suite.
