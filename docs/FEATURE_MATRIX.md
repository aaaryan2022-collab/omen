# Cross-Repository Feature Matrix

Comparison of features across the five reference systems and OMEN's unified implementation.

| Feature Category | Capability / Feature | JARVIS | Alice | Marven | OpenGuider | OpenJarvis | OMEN Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Core AI & Models** | Multi-Provider Catalog (Local + Cloud) | ✓ | ✓ | ✓ | ✓ | ✓ | **IMPLEMENTED** |
| | Dynamic Model Discovery | - | ✓ | ✓ | - | ✓ | **IMPLEMENTED** |
| | FIM Code Completion Routing | - | - | ✓ | - | - | **IMPLEMENTED** |
| | Offline Heuristic / Regex Fallback | ✓ | - | - | - | ✓ | **IMPLEMENTED** |
| **Model Routing** | Complexity-Based Intent Router | - | - | ✓ | ✓ | ✓ | **IMPLEMENTED** |
| | Automatic Failover across Providers | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Normalized Streaming Adapters | - | ✓ | ✓ | - | ✓ | **IMPLEMENTED** |
| **Agent System** | Four-Chain Loop (Plan/Exec/Eval/Replan) | - | - | - | ✓ | - | **IMPLEMENTED** |
| | ReAct Coding Agent with AST Analysis | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Checkpoint & Rollback (Undo Agent Edits) | - | - | ✓ | - | - | **IMPLEMENTED** |
| | Deep Research Multi-Source Agent | - | - | - | - | ✓ | **IMPLEMENTED** |
| **Memory & RAG** | Fact Extraction & User Preferences | ✓ | - | - | - | ✓ | **IMPLEMENTED** |
| | Conversation Memory with Summarization | ✓ | ✓ | ✓ | - | ✓ | **IMPLEMENTED** |
| | Document RAG (PDF / DOCX / TXT) | - | ✓ | - | - | ✓ | **IMPLEMENTED** |
| | Codebase Indexing (.gitignore aware) | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Context Mentions (@file, @git, etc.) | - | - | ✓ | - | - | **IMPLEMENTED** |
| **Voice & Speech** | Low-Latency VAD Frame Detection | ✓ | ✓ | - | - | ✓ | **IMPLEMENTED** |
| | Streaming STT (Whisper / SpeechRec) | ✓ | ✓ | ✓ | - | ✓ | **IMPLEMENTED** |
| | Local & Neural TTS (pyttsx3 / Edge / Cloud)| ✓ | ✓ | ✓ | ✓ | ✓ | **IMPLEMENTED** |
| | Interruptible Speech Queue | - | ✓ | - | ✓ | ✓ | **IMPLEMENTED** |
| | Wake Word Activation | ✓ | - | - | - | - | **IMPLEMENTED** |
| **Vision & Screen** | Screen Capture & Active Window Snapping | - | ✓ | ✓ | ✓ | - | **IMPLEMENTED** |
| | Pixel OCR Screen Perception (Tesseract) | - | - | - | ✓ | - | **IMPLEMENTED** |
| | Win32 Window Enumeration | - | - | - | ✓ | - | **IMPLEMENTED** |
| | Animated Screen Pointer Overlay | - | - | - | ✓ | - | **IMPLEMENTED** |
| **Windows Control** | App Launch, Switch, Close | ✓ | ✓ | - | ✓ | - | **IMPLEMENTED** |
| | Scoped Personal Folder File Management | ✓ | ✓ | - | - | - | **IMPLEMENTED** |
| | Real-Time Hardware Telemetry (psutil) | ✓ | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | System Tray & Autostart Integration | ✓ | ✓ | ✓ | - | - | **IMPLEMENTED** |
| **Browser Agent** | Playwright Automation Sidecar | - | - | - | ✓ | ✓ | **IMPLEMENTED** |
| | Human-in-the-Loop Risk Scoring | - | - | - | ✓ | - | **IMPLEMENTED** |
| **Coding Studio** | Monaco Code Editor Integration | - | - | ✓ | - | - | **IMPLEMENTED** |
| | Unified Split / Inline Diff Viewer | - | - | ✓ | - | - | **IMPLEMENTED** |
| | Integrated Terminal PTY Execution | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Interactive Git Management (Diff/Commit) | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | In-App REST Client | - | - | ✓ | - | - | **IMPLEMENTED** |
| **Productivity** | Google Calendar Integration | - | ✓ | - | - | ✓ | **IMPLEMENTED** |
| | Gmail Integration | - | ✓ | - | - | ✓ | **IMPLEMENTED** |
| | Hierarchical Tasks & Cron Reminders | - | ✓ | - | - | ✓ | **IMPLEMENTED** |
| | Markdown Notes Management | - | - | - | - | ✓ | **IMPLEMENTED** |
| | Named Multi-Step Routines | ✓ | - | - | - | - | **IMPLEMENTED** |
| **Extensibility** | Model Context Protocol (MCP) Client | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Custom Tool Creator & Schema Validator | - | ✓ | - | - | - | **IMPLEMENTED** |
| | Modular Skills Registry | - | - | - | - | ✓ | **IMPLEMENTED** |
| **Security & Safety** | Granular Capability Permissions | ✓ | ✓ | ✓ | ✓ | ✓ | **IMPLEMENTED** |
| | Interactive Modal Approval Dialogs | ✓ | ✓ | ✓ | ✓ | - | **IMPLEMENTED** |
| | SSRF & Path Traversal Verification | - | - | ✓ | - | ✓ | **IMPLEMENTED** |
| | Process / Docker Sandboxing | - | - | - | - | ✓ | **IMPLEMENTED** |
| | Encrypted Secret & Credential Vault | - | ✓ | - | - | ✓ | **IMPLEMENTED** |
| **Observability** | Asynchronous EventBus Pub/Sub | - | - | - | - | ✓ | **IMPLEMENTED** |
| | Structured Tracing & Latency Metrics | - | - | ✓ | ✓ | ✓ | **IMPLEMENTED** |
| | Append-Only Action History Audit Log | ✓ | - | - | - | - | **IMPLEMENTED** |
| | CLI System Diagnostics (`omen doctor`) | - | - | - | - | ✓ | **IMPLEMENTED** |
| **UI Experience** | State-Aware Orb Visualizer | ✓ | - | - | - | - | **IMPLEMENTED** |
| | Floating Mini Mode / Task Widget | - | - | - | ✓ | - | **IMPLEMENTED** |
| | Global Command Palette (Ctrl+Space) | - | - | ✓ | - | - | **IMPLEMENTED** |
| | Dark Mode Developer Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ | **IMPLEMENTED** |
