# Feature Inventory — 5 Reference Repositories & OMEN Architecture

Comprehensive feature inventory extracted from deep source inspection across JARVIS, Alice, Marven, OpenGuider, and OpenJarvis.

---

## 1. CORE AI & MODELS
- **Multi-Provider Unified Catalog**: Support for Ollama, LMStudio, OpenAI, Anthropic, Google Gemini, Groq, NVIDIA NIM, OpenRouter, and custom endpoints. (Alice, Marven, OpenJarvis)
- **Automatic Model Discovery**: Querying `/v1/models` and local model registries to detect available models dynamically. (Alice, Marven)
- **FIM (Fill-in-the-Middle) Completion**: Dedicated model routing for sub-second code completions. (Marven)
- **Local Offline Fallback**: Regular-expression and heuristics engine guaranteeing responses when models are offline. (JARVIS)

## 2. MODEL ROUTING & INFERENCE
- **Task Complexity Classifier**: Evaluating prompt complexity, context size, and modality to route to Fast, Reasoning, Vision, or Coding models. (Marven, OpenJarvis)
- **Loop Failover**: Automatic failover to secondary provider upon API rate-limits, timeouts, or 500 errors. (Marven, OpenJarvis)
- **Stream Normalization**: Standardized SSE / WebSocket stream adapters converting disparate vendor chunk payloads into unified delta events. (Alice, Marven)

## 3. AGENT RUNTIME & ARCHITECTURES
- **Plan-and-Solve Agent**: Hierarchical planner generating structured multi-step roadmaps. (OpenGuider, OpenJarvis)
- **ReAct Loop with Reflection**: Thought-Action-Observation cycle with self-repair upon tool errors. (Marven, OpenJarvis)
- **Evaluator & Replanner Chain**: Screen/DOM inspection validating expected state post-action and correcting course. (OpenGuider)
- **Checkpoint & Rollback Engine**: Reversible state recording enabling undo of file edits and agent actions. (Marven)
- **Deep Research Agent**: Multi-hop query decomposition, recursive web scraping, evidence extraction, citation mapping, and report synthesis. (OpenJarvis)
- **Specialized Coding Agent**: AST-aware search, targeted unified diff patching, automated test running, and linting. (Marven, OpenJarvis)

## 4. MEMORY & RAG
- **Hierarchical Memory**:
  - Short-term session buffer with sliding window & summarization. (Alice, OpenJarvis)
  - Explicit preference & fact learning (e.g., aliases, tool preferences). (JARVIS, OpenJarvis)
  - Long-term semantic memory with vector retrieval. (Alice, OpenJarvis)
- **Multi-Format Document RAG**: PDF, Markdown, DOCX, TXT chunking and embedding. (Alice, OpenJarvis)
- **Codebase Indexing**: Respects `.gitignore`, AST symbol chunking, hybrid search (dense vectors + BM25 keyword matching). (Marven, OpenJarvis)
- **Context Mentions**: `@file`, `@folder`, `@symbol`, `@git` syntax expanding dynamically into agent prompt context. (Marven)

## 5. VOICE & AUDIO
- **Voice Activity Detection (VAD)**: Real-time local speech frame detection via Web Audio / Silero VAD. (JARVIS, Alice)
- **Speech-to-Text (STT)**: Faster-Whisper, local SpeechRecognition, Deepgram streaming. (JARVIS, Alice, OpenJarvis)
- **Text-to-Speech (TTS)**: Local low-latency engines (pyttsx3, Windows SAPI, Edge TTS) and neural TTS (Cartesia, Kokoro, OpenAI). (JARVIS, Alice, OpenGuider, OpenJarvis)
- **Interruptible Speech Queue**: Cancels speech synthesizer immediately when user starts speaking. (Alice, OpenGuider)
- **Wake Word Detection**: Background listening with keyword wake triggering. (JARVIS)

## 6. VISION & SCREEN PERCEPTION
- **Dual-Layer Screen Awareness**:
  - Screenshot capture via native OS capture APIs. (OpenGuider, Alice)
  - Pixel OCR with Tesseract engine locating on-screen text coordinates. (OpenGuider)
  - Multimodal LLM visual grounding translating intent into UI coordinates. (OpenGuider)
- **Window Enumeration**: Win32 `EnumWindows` discovering open applications, window titles, and viewport bounds. (OpenGuider)
- **Visual Target Overlay**: Highlighting action coordinates on screen with an animated pointer. (OpenGuider)

## 7. COMPUTER-USE & WINDOWS INTEGRATION
- **System Actions**: Launch, close, switch, and minimize desktop applications. (JARVIS, Alice)
- **Win32 Shell Integration**: Volume control, system settings, Explorer folder opening. (JARVIS)
- **Hardware Monitoring**: Real-time CPU, GPU, RAM, VRAM, and disk utilization via psutil. (JARVIS, OpenJarvis)
- **System Tray & Hotkeys**: Global shortcuts (e.g. Ctrl+Space) and tray minimization. (JARVIS, Alice, Marven)

## 8. BROWSER AUTOMATION
- **Playwright / Browser-Use Sidecar**: Isolated browser automation subprocess for web crawling, form submission, and extraction. (OpenGuider)
- **Human-in-the-Loop Risk Scoring**: Evaluating navigation actions and requiring explicit approval before high-risk operations. (OpenGuider)
- **Local Web Preview**: In-app server hosting workspace web applications for live preview. (Marven)

## 9. DEVELOPER & CODING STUDIO
- **Monaco Code Editor**: Syntax highlighting, multi-tab editing, inline completions. (Marven)
- **Unified Diff Viewer**: Split and inline diff visualizations with approve/reject controls. (Marven)
- **Terminal Emulator (PTY)**: Integrated terminal execution with real-time streaming output, ANSI color support, and interrupt capability. (Marven)
- **Interactive Git Panel**: Stage, unstage, diff, commit, branch, push, and checkout. (Marven)
- **Built-in REST Client**: In-app API request builder and response inspector. (Marven)
- **LSP Integration**: Language Server Protocol client for live syntax diagnostics and symbol search. (Marven)

## 10. PRODUCTIVITY & WORKSPACE CONNECTORS
- **Google Calendar**: Real OAuth2 event listing, creation, and conflict detection. (Alice, OpenJarvis)
- **Gmail**: Email search, reading, thread summarization, and safe drafting. (Alice, OpenJarvis)
- **Tasks & Reminders**: Hierarchical task tracking with due dates, tags, and cron reminders. (Alice, OpenJarvis)
- **Markdown Notes**: Categorized notes linked to projects and tasks. (Alice, OpenJarvis)
- **Routines & Automations**: Multi-step user-defined workflows (e.g. "Work Mode", "Gaming Mode"). (JARVIS)

## 11. EXTENSIBILITY: MCP, SKILLS & PLUGINS
- **Model Context Protocol (MCP)**: Full client supporting stdio and SSE transport, discovering external tools and resources. (Marven, OpenJarvis)
- **Custom Tool Builder**: User-facing UI and schema validator for custom scripted tools. (Alice)
- **Skills Registry**: Modular loadable domain skills with dependency management. (OpenJarvis)
- **Plugin Architecture**: Extensible plugin interface with isolated lifecycle management. (OpenGuider, OpenJarvis)

## 12. SECURITY, GOVERNANCE & SANDBOXING
- **Granular Permission Scopes**: Explicit capability tokens (`fs.read`, `fs.write`, `terminal`, `network`, `screen`, `system`). (JARVIS, Alice, OpenJarvis)
- **Human-in-the-Loop Confirmations**: Modal approvals for destructive file operations, app termination, and external execution. (JARVIS, Alice, Marven, OpenGuider)
- **SSRF & Path Traversal Guards**: URL validation preventing internal network probing and directory traversal out of project root. (Marven, OpenJarvis)
- **Execution Sandboxing**: Process isolation and Docker container runtime. (OpenJarvis)
- **Encrypted Credential Storage**: Secure OS credential vault for API keys and tokens. (Alice, OpenJarvis)

## 13. OBSERVABILITY, TRACING & LEARNING
- **Central EventBus**: Asynchronous event hub broadcasting system lifecycle, agent milestones, and tool executions. (OpenJarvis)
- **Execution Traces**: Persistent structured logs of prompts, tool calls, latency, token counts, and outcomes. (OpenJarvis)
- **Action Audit Log**: Append-only log recording every OS action taken. (JARVIS)
- **Diagnostics Suite (`doctor`)**: Comprehensive self-test auditing Python, Node, GPU, Ollama, microphone, and tools. (OpenJarvis)

## 14. UI / UX DESIGN
- **OMEN Orb Visualizer**: Interactive pulsating core reflecting assistant states (IDLE, LISTENING, THINKING, SPEAKING, EXECUTING, ERROR). (JARVIS, Alice, Marven)
- **Mini Mode / Floating Widget**: Lightweight overlay widget providing quick mic input and live task progress. (OpenGuider)
- **Command Palette**: Fuzzy search launcher triggered via `Ctrl+Space`. (Marven)
- **Dark Minimal Aesthetics**: Premium developer-first dark theme with glassmorphic cards and subtle animations. (Alice, Marven, JARVIS)
