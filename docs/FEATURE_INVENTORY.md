# FEATURE INVENTORY — OMEN vs FIVE REFERENCES

Status: PARTIAL — all discovered features listed; implementation tracked against OMEN source.

| Feature | Source | OMEN Status | Notes |
|---|---|---|---|
| CLI | OMEN (main.py) | IMPLEMENTED | --cli, --debug, --wizard |
| GUI | OMEN (PySide6) | IMPLEMENTED | Dark steel-blue theme |
| Agent pipeline | OMEN (core/agent) | IMPLEMENTED | Brain→Planner→Executor |
| LLM (Ollama) | OMEN (providers/llm) | IMPLEMENTED | Local first |
| Mock mode | OMEN | IMPLEMENTED | For testing |
| Tool registry | OMEN (tools/registry) | IMPLEMENTED | Dynamic schemas |
| Memory (SQLite) | OMEN (core/memory) | IMPLEMENTED | + ChromaDB optional |
| EventBus | OMEN (core/events) | IMPLEMENTED | PubSub |
| Voice (STT) | OMEN (voice/stt) | PARTIAL | SpeechRecognition |
| Voice (TTS) | OMEN (voice/tts) | PARTIAL | pyttsx3 |
| Wake word | OMEN (voice/wake_word) | PARTIAL | Configured, not fully active |
| Vision / screenshot | OMEN (vision/) | PARTIAL | Element detect + screenshot |
| Screen awareness | OMEN (core/observation_loop) | PARTIAL | Observe/verify loop |
| Computer control | OMEN (computer/) | PARTIAL | Mouse/keyboard/app |
| Browser agent | OMEN (browser/, tools/browser) | PARTIAL | DOM + visual fallback |
| Coding agent | References (Marven) | MISSING | Requires editor + terminal + git |
| Code editor | References (Marven, Alice) | MISSING | No Monaco/CodeMirror |
| Git integration | References | PARTIAL | Tools exist; full git UUI missing |
| Terminal | OMEN (automation) | PARTIAL | No integrated terminal UI |
| System info | OMEN (app/hardware) | IMPLEMENTED | GPU/CPU detection |
| App control | OMEN (tools/system) | PARTIAL | Open/close apps |
| Tasks / reminders | OMEN (productivity/) | IMPLEMENTED | Pomodoro + reminders |
| Calendar | References | MISSING | Architecture only |
| Email | OMEN (providers/email/) | PARTIAL | Mock + Gmail OAuth |
| News | OMEN (providers/news/) | IMPLEMENTED | RSS feed |
| Scheduling | OMEN (scheduler/) | IMPLEMENTED | APScheduler |
| Monitoring | OMEN (core/supervisor) | PARTIAL | Observatory loops |
| Plugins | References | MISSING | No plugin registry |
| MCP | References (Alice, Marven) | MISSING | No MCP server management |
| Skills | References | MISSING | No skill system |
| Security / permissions | OMEN (safety/, security/) | IMPLEMENTED | Risk levels + confirmation |
| Sandboxing | References | MISSING | No Docker/isolation |
| Hardware detection | OMEN (app/hardware) | IMPLEMENTED | psutil + nvidia-smi |
| Settings / config | OMEN (app/config) | IMPLEMENTED | Pydantic + .env |
| Command palette | OMEN (UI) | MISSING | No Ctrl+Space palette |
| Mini mode | OMEN (UI) | MISSING | No floating widget |
| System tray | OMEN (productivity/) | PARTIAL | Notification service |
| Observatory / observations | OMEN | PARTIAL | ObservationLoop |
| RAG / document retrieval | OMEN (core/memory) | PARTIAL | Vector memory optional |
| Data / database | OMEN (database/) | IMPLEMENTED | SQLite with migrations |
| Tests | OMEN (tests/) | PARTIAL | Only smoke + modules |
| Documentation | OMEN (README) | PARTIAL | Need docs/ complete |
| Packaging / installer | OMEN (pyproject) | PARTIAL | No Windows installer |
| Learning / routing | References | MISSING | Heuristic only in planner |
| Telemetry | References | PARTIAL | Logging only; no analytics |
| Tracing | References (OpenJarvis) | PARTIAL | EventBus + logs |
