# 01 - JARVIS Research Dossier

## 1. Purpose
A lightweight, offline-first, dual-process desktop AI assistant for Windows that enables hands-free voice interaction, system control, file management, and routine automation with zero external cloud dependencies.

## 2. Architecture
Two cooperating processes communicating over a strictly loopback-only (`127.0.0.1`) REST + WebSocket bridge:
- **Frontend Process**: Electron + React + TypeScript. Controls UI presentation, native window lifecycle, system tray, global hotkeys, autostart via Windows login items, and backend process supervision.
- **Backend Process**: Python (FastAPI). Controls local AI model execution (Ollama), speech synthesis & recognition, file operations, system actions, memory persistence, and permission enforcement.

## 3. Technology Stack
- **Frontend**: Electron, React, TypeScript, TailwindCSS, Vite
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic
- **AI/Inference**: Ollama REST API (default `llama3.1:8b`), regex pattern-matched fallback
- **Voice**: SpeechRecognition, pyttsx3, Web VAD (Silero/worklet)
- **OS Control**: psutil, win32 subprocesses, Explorer shell integration

## 4. Directory Structure
```
JARVIS/
├── backend/
│   ├── app/
│   │   ├── ai/ (backend.py, backends.py, manager.py, ollama_backend.py, responder.py)
│   │   ├── api/ (server.py)
│   │   ├── automation/ (routines.py)
│   │   ├── control/ (actions.py, files.py, system.py)
│   │   ├── history/ (action_log.py)
│   │   ├── memory/ (facts.py, store.py, config.py)
│   │   ├── security/ (permissions.py)
│   │   ├── settings/ (manager.py)
│   │   └── voice/ (live_transcribe.py, stt.py, tts.py, wakeword.py)
│   └── main.py
├── frontend/
│   ├── src/main/ (autostart.ts, backendManager.ts, index.ts, ipc.ts, tray.ts, updater.ts)
│   ├── src/preload/ (index.ts)
│   └── src/renderer/ (components, hooks, lib)
└── shared/ (ipc-contract.md)
```

## 5. Core Modules
- `AIManager`: Decides actions, orchestrates tool calls, handles confirmations.
- `AIBackend`: Protocol defining `chat()` and `is_available()`.
- `ControlActions` & `ControlFiles`: Whitelisted app launching, window switching, personal folder file operations.
- `PermissionManager`: Scoped permission verification and persistence.
- `RoutinesManager`: Named ordered step routines.
- `BackendManager`: Electron child-process supervisor with backoff-capped retry (1s, 2s, 4s, 8s, 16s).

## 6. AI / Model Architecture
- Local Ollama model invocation via standard HTTP endpoint.
- Pluggable `AIBackend` protocol.
- Pattern matching fallback engine when local LLM is offline or uninstalled.
- Zero cloud API keys required.

## 7. Agent Architecture
- Single unified agent loop in `AIManager` with two-phase execution: plan/propose action -> evaluate permissions -> prompt confirmation if risky -> execute tool -> synthesize response.

## 8. Tool Architecture
- Built-in tool primitives in `app/control/`:
  - `open_app(app_name)`
  - `close_app(app_name)` (requires confirmation)
  - `switch_to_app(app_name)`
  - `open_settings(page)`
  - `open_folder(path)`
  - `search_files(pattern)`
  - `organize_folder(path)` (requires confirmation)
  - `check_system_performance()`

## 9. Memory Architecture
- JSON-persisted conversation history (`store.py`).
- Explicit learned facts/preferences (`facts.py`), e.g., user aliases like "my editor" mapped to "VS Code".
- Module-level file-path-keyed in-memory cache to prevent race conditions across requests.

## 10. Voice Architecture
- Push-to-talk and continuous listening support.
- Silero VAD audio worklet in renderer.
- Porcupine/custom wake word bridge (`wakewordBridge.ts`).
- STT via `SpeechRecognition` (lazy imported to minimize boot time).
- TTS via `pyttsx3` (local, zero-latency).

## 11. Vision Architecture
- Minimal / Not natively present in JARVIS (delegates to OS screenshot/file tools).

## 12. Screen / Computer-Use Architecture
- Scoped to window switching and application launches. No raw mouse/coordinate clicking.

## 13. Coding Architecture
- Limited to launching IDEs and managing files in user directories.

## 14. Browser Architecture
- Simple URL launch via default browser handler (`os.startfile(url)`).

## 15. Plugin Architecture
- Not modularized as external plugins; tools are statically registered in `control/`.

## 16. MCP Architecture
- Not implemented in JARVIS.

## 17. Scheduling
- Limited to sequential routine execution; no persistent cron daemon.

## 18. Automation
- User-defined named routines (e.g. "Work Mode", "Gaming Mode") stored in JSON.
- Step-by-step execution with safety gates.

## 19. Security
- Loopback-only HTTP binding (`127.0.0.1`).
- Scoped directory access restricted to user profile folders (`Desktop`, `Documents`, `Downloads`, `Pictures`, `Music`, `Videos`).
- Destructive operations (`delete`, raw cmd execution) completely omitted.

## 20. Permissions
- Explicit scopes: `control.apps`, `fs.read`, `fs.write`, `memory.enabled`.
- Granular confirmation dialogs for risky operations.

## 21. Database
- JSON file stores with memory caching layer.

## 22. Configuration
- Persisted JSON settings managed through `SettingsManager`.

## 23. CLI
- Batch launcher `Start JARVIS.bat`.

## 24. API
- REST API with FastAPI (`/health`, `/api/ai/chat`, `/api/control/*`, `/api/settings/*`).

## 25. UI
- Clean dark-themed React + Electron UI with sidebar navigation, orb visualizer, status indicators, and modal confirmations.

## 26. Telemetry
- Persisted action history audit log (`action_log.py`).

## 27. Testing
- Integration tests in frontend and backend unit tests.

## 28. Deployment
- Electron Builder with NSIS Windows installer, autostart via Windows login items.

## 29. Strengths
- Clean separation of concerns between Electron shell and Python intelligence engine.
- Resilient process supervisor with health polling and automatic crash recovery.
- Strict security scoping for files and applications.

## 30. Weaknesses
- No coding agent or terminal sandbox.
- No computer-use or vision perception.
- No MCP or extensible plugin system.

## 31. Features Worth Adopting for OMEN
- Dual-process supervisor with backoff crash recovery.
- Scoped personal folder permissions and action audit log.
- Multi-step named routines/automations.

## 32. Architectural Patterns Worth Adopting
- Module-level path caching for JSON stores.
- Strict loopback isolation.

## 33. Features NOT to Copy
- Relying exclusively on JSON files without ACID database (OMEN uses SQLite).
- Lack of terminal execution.

## 34. Licensing Concerns
- Repository has no license file. Code cannot be directly copied; independent clean implementation is mandatory.
