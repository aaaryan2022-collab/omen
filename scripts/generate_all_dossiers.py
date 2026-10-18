import os

def write_alice():
    content = """# 02 - Alice Research Dossier

## 1. Purpose
A highly extensible, voice- and avatar-driven desktop personal assistant built with Electron, Vue 3, and Python, featuring deep Google Workspace integration (Gmail, Calendar), local and cloud LLMs, custom tool management, RAG document ingestion, and scheduled automations.

## 2. Architecture
Hybrid Electron + Python architecture:
- **Renderer Process**: Vue 3 + Pinia + TailwindCSS. Renders interactive chat, avatar visualizations, settings tabs, onboarding wizard, and command approval dialogs.
- **Electron Main Process**: TypeScript. Manages IPC bridge policy, security boundaries, window lifecycle, system tray, hotkeys, auth manager, settings security, and workers.
- **Backend / Python Services**: Manages voice recognition, speech models, document parsing (PDF parser worker), and thought vector embeddings.

## 3. Technology Stack
- **Frontend / Electron**: Electron, Vite, Vue 3, TypeScript, Pinia, TailwindCSS, Vitest
- **LLM Integrations**: Ollama, LMStudio, OpenAI, OpenAI-Compatible, OpenRouter, DeepSeek, Minimax, Codex, ZAI
- **APIs & Auth**: Google OAuth 2.0 (Google Calendar API, Gmail API), Codex App Server
- **Voice / Audio**: VAD runtime, Web Audio API, local TTS/STT pipelines
- **RAG & Vectors**: In-memory & SQLite vector store, PDF parsing via worker threads

## 4. Directory Structure
```
Alice/
├── electron/
│   ├── main/
│   │   ├── authManager.ts, backendManager.ts, codexAppServerManager.ts
│   │   ├── customAvatarsManager.ts, customToolsManager.ts, desktopManager.ts
│   │   ├── googleAuthManager.ts, googleCalendarManager.ts, googleGmailManager.ts
│   │   ├── hotkeyManager.ts, ipcManager.ts, memoryManager.ts, memorySearch.ts
│   │   ├── ragDocumentStore.ts, schedulerManager.ts, securityBoundaries.ts
│   │   └── thoughtVectorStore.ts, updaterManager.ts, windowManager.ts
│   └── preload/ (ipcBridgePolicy.ts, index.ts)
├── src/
│   ├── components/ (Chat.vue, Main.vue, Actions.vue, CommandApprovalDialog.vue, Settings.vue, wizard/)
│   ├── composables/ (useAudioPlayback.ts, useGoogleAuth.ts, useHotkeyRecording.ts, useScreenshot.ts)
│   ├── modules/conversation/ (chatOrchestrator.ts, historyManager.ts, turnManager.ts, toolCallHandler.ts)
│   ├── services/llmProviders/ (ollama.ts, openai.ts, deepseek.ts, lmStudio.ts, openrouter.ts, modelDiscovery.ts)
│   └── stores/ (conversationStore.ts, customToolsStore.ts, settingsStore.ts)
└── docs/ (setupInstructions.md, toolsInstructions.md, custom-tools.md)
```

## 5. Core Modules
- `GoogleAuthManager` / `GoogleGmailManager` / `GoogleCalendarManager`: Full OAuth2 workflow for real email search/read/send and calendar event scheduling/conflict checking.
- `CustomToolsManager`: UI and runtime engine enabling users to define custom JSON schema tools and JavaScript execution handlers.
- `RAGDocumentStore`: Document ingestion pipeline chunking PDFs and text files into a thought vector store for semantic retrieval.
- `ChatOrchestrator`: Multi-turn conversational controller handling streaming responses, tool call approvals, and voice playback queue.
- `SecurityBoundaries`: Strict IPC filter preventing untrusted renderer calls from accessing sensitive desktop capabilities.

## 6. AI / Model Architecture
- Multi-provider catalog supporting 8+ local and cloud backends.
- Automatic model discovery via provider endpoints (`/v1/models`, Ollama tags).
- Stream adapters normalizing streaming chunks across disparate model APIs.

## 7. Agent Architecture
- Tool-augmented conversational loop (`chatOrchestrator.ts`) with turn management, context injection, tool execution, and speech output queuing.

## 8. Tool Architecture
- Universal function calling dispatcher (`functionCaller.ts`).
- Built-in tools:
  - Calendar management (events, agenda, conflicts)
  - Gmail (read, draft, search, send)
  - Filesystem (read, write, list)
  - Clipboard (read, set)
  - Torrent management (status, magnet link handling)
  - User-defined Custom Tools (schema-validated)

## 9. Memory Architecture
- Hierarchical memory:
  - Short-term conversation history with summarization (`summarizer.ts`).
  - Long-term semantic memory (`thoughtVectorStore.ts`).
  - Searchable memory database (`memorySearch.ts`).

## 10. Voice Architecture
- Integrated voice conversation loop (`useAudioProcessing.ts`, `useAudioPlayback.ts`).
- VAD runtime (`vadRuntime.ts`) with client-side audio frame processing.
- Speech queue (`speechQueue.ts`) prioritizing responses and allowing interruption.

## 11. Vision Architecture
- Screen capture via `useScreenshot.ts` passing image base64 into multimodal LLM requests.

## 12. Screen / Computer-Use Architecture
- Window minimization, focus, and screenshot capture via `desktopManager.ts`.

## 13. Coding Architecture
- Codex App Server integration (`codexAppServerManager.ts`) for code execution and tool bridging.

## 14. Browser Architecture
- External browser URL launches and web view embedding.

## 15. Plugin Architecture
- Custom Tools manager acting as dynamic in-app plugins with user-specified arguments and handlers.

## 16. MCP Architecture
- Compatible via tool bridging layer to standard JSON-RPC tool protocols.

## 17. Scheduling
- `SchedulerManager` powered by cron parser (`cronParser.ts`) allowing scheduled reminders and background prompt runs.

## 18. Automation
- Cron-based reminders (`reminderHandler.ts`) and recurring background assistant queries.

## 19. Security
- Strict `ipcBridgePolicy.ts` enforcing permission checks at Electron main level.
- Encrypted settings storage (`settingsSecurity.ts`).
- Command approval modal (`CommandApprovalDialog.vue`) before consequential tool executions.

## 20. Permissions
- Granular permission matrix for filesystem, Google API tokens, desktop control, and external scripts.

## 21. Database
- SQLite-backed store for thought vectors, memories, and settings.

## 22. Configuration
- Pinia-based reactive settings store synchronized to disk via Electron IPC.

## 23. CLI
- Primarily GUI-focused with npm script tasks.

## 24. API
- Inter-process communication via IPC channels and Codex server bridge.

## 25. UI
- Modern Vue 3 interface with dark mode, interactive settings tabs, onboarding wizard, and animated avatar components.

## 26. Telemetry
- Local logging and error reporting.

## 27. Testing
- Comprehensive Vitest suite covering IPC policies, memory search, security boundaries, and provider catalog.

## 28. Deployment
- Electron Builder configuration supporting NSIS packaging and auto-updates.

## 29. Strengths
- Native Google Calendar and Gmail integration with real OAuth2 flows.
- User-defined custom tools and custom avatars.
- RAG document ingestion with PDF worker parser.
- Multi-provider model discovery.

## 30. Weaknesses
- Limited terminal sandboxing.
- Lacks autonomous multi-step coding agent loop with AST analysis.

## 31. Features Worth Adopting for OMEN
- Google Workspace (Calendar + Gmail) OAuth and connector architecture.
- Custom Tool builder and manager.
- Onboarding wizard and audio playback speech queue.
- PDF RAG ingestion pipeline.

## 32. Architectural Patterns Worth Adopting
- Preload IPC bridge policy validation.
- Provider catalog with streaming normalization.

## 33. Features NOT to Copy
- Vue 3 stack (OMEN uses React / TypeScript desktop stack).
- In-memory vector arrays for production embeddings (use SQLite vector / Chroma).

## 34. Licensing Concerns
- MIT License (Copyright 2025 Slava Trofimov). Permissive; clean independent implementation used in OMEN with proper attribution.
"""
    with open("docs/reference-analysis/02-ALICE.md", "w", encoding="utf-8") as f:
        f.write(content)

def write_marven():
    content = """# 03 - Marven Research Dossier

## 1. Purpose
A high-performance developer-focused AI desktop IDE and assistant built with Next.js, Electron, and TypeScript, providing an end-to-end coding agent, Monaco code editor, Git integration, terminal, codebase indexing, Language Server Protocol (LSP), and Model Context Protocol (MCP).

## 2. Architecture
Hybrid Next.js + Electron architecture:
- **Frontend / Editor**: Next.js (React) + Monaco Editor + TailwindCSS. Provides full developer studio UI: file tree, multi-file editor tabs, split diff views, terminal emulator, problems pane, REST client, and Git management.
- **Backend / API Routes**: Next.js API route handlers running under Node.js / Electron. Powers agent execution loops, codebase indexing (walking, chunking, embedding, vector search), LSP communication, MCP client, and terminal PTY processes.

## 3. Technology Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Monaco Editor, TailwindCSS, Lucide Icons
- **Backend / Systems**: Node.js, Electron, node-pty (terminal), isomorphic-git / native git
- **AI Models**: Anthropic, OpenAI, OpenRouter, Groq, Ollama, LMStudio, NVIDIA NIM, LlamaServer
- **Coding & LSP**: Language Server Protocol (LSP) client, AST parsers, FIM (Fill-In-the-Middle) code completion
- **RAG & Search**: AST code chunker, vector store, exclusions parser (`.gitignore`)

## 4. Directory Structure
```
Marven/
├── app/
│   ├── api/
│   │   ├── agent/ (verify, loop)
│   │   ├── chat/ (parse-document, route)
│   │   ├── completion/ (inline completions)
│   │   ├── diagnostics/, files/, health/, index/ (indexer, search, chunker)
│   │   ├── mcp/ (mcp client & server)
│   │   ├── memory/, models/, system/, tts/, stt/, vision/
│   │   └── workspace/ (clone, create, file-ops, git, preview, review, scan)
│   └── components/marven/ (CodeEditor.tsx, DiffPanel.tsx, GitPanel.tsx, TerminalView.tsx, RestClientPanel.tsx)
├── lib/
│   ├── agent/ (loop.ts, applyPatch.ts, approvals.ts, checkpointStore.ts, tools.ts, rulesFile.ts)
│   ├── completion/ (fimPrompt.ts, contextWindow.ts, inlineCompletionExtension.ts)
│   ├── editor/ (lspClient.ts, lspServers.ts, lspExtension.ts)
│   ├── index/ (chunker.ts, embedder.ts, indexer.ts, search.ts, walker.ts)
│   ├── mentions/ (parser.ts, resolver.ts, formatter.ts)
│   ├── mcpClient.ts, gitUtils.ts, ssrfGuard.ts, workspaceTrust.ts
└── docs/ (superpowers plans and specs)
```

## 5. Core Modules
- `AgentLoop` (`lib/agent/loop.ts`): Autonomous coding agent loop with tool selection, patch generation, patch validation, test execution, error reflection, and checkpointing.
- `ApplyPatch` (`lib/agent/applyPatch.ts`): Unified diff and targeted chunk replacement engine with syntax verification.
- `CheckpointStore` (`lib/agent/checkpointStore.ts`): Rollback and undo capabilities for all code changes executed by AI.
- `CodebaseIndexer` (`lib/index/`): Traverses workspace respecting `.gitignore`, generates chunks, computes embeddings, and provides semantic symbol and file search.
- `MentionsResolver` (`lib/mentions/`): Context mentions (`@file`, `@folder`, `@symbol`, `@git`) expanded dynamically into model prompts.
- `LSPClient` (`lib/editor/lspClient.ts`): Connects to language servers for diagnostics, hover, go-to-definition, and symbol search.
- `RestClientPanel`: In-app HTTP/REST testing tool with request builder, headers, body, and response preview.

## 6. AI / Model Architecture
- Multi-provider support with automatic fallback (`loopFailover.ts`).
- Dedicated FIM (Fill-in-the-Middle) model routing for real-time editor code completion.
- Multimodal vision support for screenshot and UI bug analysis.

## 7. Agent Architecture
- ReAct / Plan-and-Solve coding agent loop with safety profiles, task classification (`taskClassifier.ts`), and narrated tool calls.

## 8. Tool Architecture
- Developer tools:
  - `read_file`, `write_file`, `apply_patch`
  - `run_command` (terminal PTY execution with timeout and output capture)
  - `git_status`, `git_diff`, `git_commit`, `git_checkout`
  - `codebase_search`, `symbol_search`
  - `lsp_diagnostics`

## 9. Memory Architecture
- Project memory stored in workspace `.marven/` or server conversation store with context window management.

## 10. Voice Architecture
- Local STT and TTS hooks (`useVoice.ts`, `speak.ts`, `localStt.ts`).

## 11. Vision Architecture
- Image upload and screenshot preview (`ImagePreview.tsx`, `api/vision/`).

## 12. Screen / Computer-Use Architecture
- Scoped to IDE workspace and terminal commands; no arbitrary mouse/screen control.

## 13. Coding Architecture
- Monaco Editor integration with syntax highlighting, inline diff decorations, code completion, and diagnostics panel.

## 14. Browser Architecture
- Workspace preview server (`api/workspace/preview/`) allowing live local web app preview.

## 15. Plugin Architecture
- MCP servers acting as dynamic external tool plugins.

## 16. MCP Architecture
- Full client integration (`lib/mcpClient.ts`, `app/api/mcp/`) connecting to external MCP servers via stdio / SSE.

## 17. Scheduling
- Limited to background indexing tasks.

## 18. Automation
- Automated git assistance, release checklist generator, code review workflows.

## 19. Security
- SSRF protection (`ssrfGuard.ts`).
- Workspace trust verification (`workspaceTrust.ts`).
- Environment variable sanitization (`sanitizedEnv.ts`).
- Mandatory write approval diff preview before disk modification.

## 20. Permissions
- Configurable approval policies: auto-approve reads, confirm writes, confirm terminal commands.

## 21. Database
- JSON file stores, SQLite vector store for codebase embeddings.

## 22. Configuration
- `.marven/rules` and project settings files.

## 23. CLI
- Command palette with keyboard shortcuts (`CommandPalette.tsx`, `QuickOpenModal.tsx`).

## 24. API
- Rich Next.js REST endpoints for workspace, index, git, terminal, and agent execution.

## 25. UI
- Dark modern IDE interface with collapsible sidebars, dockable terminal, problems tab, diff viewer, and symbol outline.

## 26. Telemetry
- Completion telemetry and latency tracking.

## 27. Testing
- Extensive test coverage across agent loop, diff patching, mentions parsing, and SSRF guards.

## 28. Deployment
- Electron app with Next.js standalone server packaging.

## 29. Strengths
- World-class coding agent loop with unified diff patching and undo checkpoints.
- Codebase RAG indexing with `@mentions` context injection.
- Monaco Editor + LSP + FIM inline completion.
- Built-in Git panel, terminal PTY, and REST client.

## 30. Weaknesses
- Heavy Next.js server runtime inside Electron.
- No general Windows GUI automation or OCR screen perception.

## 31. Features Worth Adopting for OMEN
- Monaco Code Editor + Diff Panel + File Explorer.
- Complete Coding Agent with `apply_patch`, checkpointing, and test-fix loops.
- Codebase indexing with `.gitignore` filtering.
- Terminal PTY execution and interactive Git panel.
- Context mentions (`@file`, `@git`, etc.).
- Built-in REST client for API testing.

## 32. Architectural Patterns Worth Adopting
- CheckpointStore rollback before autonomous agent edits.
- Diff preview modal before writing files.
- SSRF guard and environment sanitization.

## 33. Features NOT to Copy
- Next.js web server inside desktop app (FastAPI + React desktop client is cleaner and faster).
- Strong copyleft code (clean-room independent implementation required).

## 34. Licensing Concerns
- Licensed under GNU AGPLv3. STRICTLY PROHIBITED FROM DIRECT COPYING. OMEN must implement independent, clean-room equivalents of all architectures and capabilities.
"""
    with open("docs/reference-analysis/03-MARVEN.md", "w", encoding="utf-8") as f:
        f.write(content)

def write_openguider():
    content = """# 04 - OpenGuider Research Dossier

## 1. Purpose
An intelligent desktop AI copilot specialized in screen perception, OCR, visual GUI navigation, human-in-the-loop task execution, and browser automation via a sidecar architecture.

## 2. Architecture
Hybrid Electron + Node.js + Python sidecar:
- **Electron Shell**: Main process manages native screen capture, window enumeration (Win32), global shortcuts, floating task widget, and sidecar lifecycle.
- **Node.js Agent Core**: Orchestrates task planning, plan validation, step queuing, OCR analysis, UI scanning, and pointer tool visualization.
- **Python Browser Sidecar**: High-performance browser automation service using Playwright/browser-use communicating over local JSON-RPC / IPC.

## 3. Technology Stack
- **Desktop / UI**: Electron, Node.js, HTML5/CSS3/Vanilla JS, Tesseract.js / Tesseract OCR
- **Computer-Use / Win32**: desktopCapturer, EnumWindows, robotjs / nut.js / Win32 mouse & keyboard APIs
- **Browser Automation**: Python 3.10+, Playwright, browser-use, asyncio
- **Vision & Perception**: Tesseract OCR engine, bounds validator, semantic UI scanner

## 4. Directory Structure
```
OpenGuider/
├── src/
│   ├── agent/ (evaluator-chain.js, executor-chain.js, planner-chain.js, replanner-chain.js, task-orchestrator.js)
│   │   └── tools/ (capture-screen-tool.js, plan-tool.js, pointer-tool.js)
│   ├── core/ (execution-engine.js, intent-router.js, plugin-registry.js, step-queue.js, trust-manager.js)
│   ├── perception/ (ocr-engine.js, ui-scanner.js, window-enum.js)
│   ├── plugins/browser/ (sidecar.js, risk-scorer.js, python/agent_server.py, python/hitl_hooks.py)
│   ├── session/ (session-manager.js, session-persistence.js)
│   ├── tts/ (google-tts.js, openai-tts.js, windows-tts.js)
│   └── validation/ (bounds-validator.js, semantic-verifier.js)
├── renderer/ (components/execution-log, components/step-approval, js/widget.js, js/panel/)
└── main.js, preload.js
```

## 5. Core Modules
- `TaskOrchestrator`: Coordinates the full autonomous agent cycle: Plan -> Execute -> Evaluate -> Replan.
- `UI_Scanner` & `OCREngine`: Inspects screen pixels, extracts on-screen text coordinates, and identifies clickable bounding boxes.
- `PointerTool`: Visualizes action targets by projecting an animated click pointer or highlight overlay on the desktop.
- `BrowserSidecar`: Spawns a supervised Python subprocess running browser-use for autonomous web workflows.
- `HITL_Hooks`: Human-in-the-loop interception points that pause execution and prompt the user before high-risk actions.
- `RiskScorer`: Analyzes intended browser or desktop actions and computes a risk tier (safe, moderate, destructive).

## 6. AI / Model Architecture
- Multimodal vision LLM integration (GPT-4o, Claude 3.5 Sonnet, local vision models) for UI comprehension.
- Structured outputs validation ensuring coordinates and actions conform to JSON schema.

## 7. Agent Architecture
- Four-chain agent loop:
  1. `PlannerChain`: Generates decomposed action steps.
  2. `ExecutorChain`: Executes individual step via pointer/browser tools.
  3. `EvaluatorChain`: Inspects screen post-action to verify success.
  4. `ReplannerChain`: Corrects trajectory if an unexpected state or error dialog appears.

## 8. Tool Architecture
- Vision & Interaction tools:
  - `capture_screen`: Takes full desktop or active window snapshot.
  - `pointer_tool`: Moves mouse, clicks coordinates, types text, scrolls.
  - `plan_tool`: Emits structured task roadmap.
  - `browser_actions`: Navigate, click element, extract table, fill form.

## 9. Memory Architecture
- Session-based action memory and element cache caching resolved UI bounding boxes.

## 10. Voice Architecture
- Push-to-talk listener and multi-engine TTS (Windows SAPI, Google TTS, OpenAI TTS).

## 11. Vision Architecture
- Dual-layer perception:
  - Pixel OCR with Tesseract (`eng.traineddata`).
  - Multimodal LLM visual grounding mapping user intents to (x, y) coordinates.

## 12. Screen / Computer-Use Architecture
- Active window enumeration (`window-enum.js`), desktop screenshot capture, and Win32 coordinate translation.

## 13. Coding Architecture
- Minimal (focused on desktop automation rather than source code editing).

## 14. Browser Architecture
- Dedicated Python sidecar running Playwright with persistent browser context, anti-detect headers, and DOM extraction.

## 15. Plugin Architecture
- Extensible `PluginRegistry` allowing new capability plugins (e.g., browser plugin).

## 16. MCP Architecture
- Compatible via tool interface.

## 17. Scheduling
- Session-based execution queue.

## 18. Automation
- Multi-step interactive GUI automations with live screen feedback.

## 19. Security
- `RiskScorer` evaluating action danger.
- `TrustManager` preventing autonomous execution of high-risk actions without explicit approval.
- Bounds validation preventing mouse clicks outside active desktop viewports.

## 20. Permissions
- Step approval cards (`StepApprovalCard.js`) requiring manual clicks before submitting sensitive forms or modifying OS state.

## 21. Database
- JSON file stores for sessions and settings.

## 22. Configuration
- Local store schema validating provider keys, sidecar paths, and OCR thresholds.

## 23. CLI
- Task execution logging view.

## 24. API
- Local JSON-RPC bridge between Node.js and Python sidecar.

## 25. UI
- Floating Task Widget (`widget.js`, `task-widget.js`) that sits unobtrusively on top of other desktop windows, showing live status, step progress, and pause/resume buttons.

## 26. Telemetry
- Performance metrics tracking step duration, token cost, and OCR recognition latency.

## 27. Testing
- Integration and UI smoke tests for task orchestrator, execution log, and browser sidecar paths.

## 28. Deployment
- Electron builder with after-pack scripts bundling Python sidecar dependencies.

## 29. Strengths
- Unmatched screen perception with OCR and visual element detection.
- Four-chain Plan -> Execute -> Evaluate -> Replan autonomous loop.
- Floating desktop widget UX.
- Browser sidecar with human-in-the-loop safety scoring.

## 30. Weaknesses
- Tesseract OCR can be slow on high-res displays without GPU acceleration.
- Python sidecar packaging requires careful virtualenv / binary bundling.

## 31. Features Worth Adopting for OMEN
- Screen capture + OCR + Vision LLM perception pipeline.
- Four-chain Planner / Executor / Evaluator / Replanner loop.
- Floating Mini Mode / Widget overlay.
- Risk Scorer & Human-in-the-Loop approval cards for consequential actions.
- Playwright browser automation agent.

## 32. Architectural Patterns Worth Adopting
- Sidecar isolation for heavy automation engines.
- Semantic verification and bounds checking before dispatching mouse actions.

## 33. Features NOT to Copy
- Heavy reliance on fragile coordinate clicking when accessibility APIs or DOM APIs are available.

## 34. Licensing Concerns
- Licensed under Apache 2.0 (with browser-use MIT). Permissive; clean independent implementation used in OMEN with required notices.
"""
    with open("docs/reference-analysis/04-OPENGUIDER.md", "w", encoding="utf-8") as f:
        f.write(content)

def write_openjarvis():
    content = """# 05 - OpenJarvis Research Dossier

## 1. Purpose
A massively scalable, enterprise-grade, multi-agent AI operating layer providing hybrid cloud/local model orchestration, agent-to-agent communication (A2A), deep research, skill pools, sandboxing, learning & reinforcement optimization (GRPO/SFT), MCP integration, and multi-channel messaging (CLI, Discord, Slack, Telegram, Web).

## 2. Architecture
Modular multi-tier architecture:
- **Core Engine & Gateways**: Python + Rust bridge (`_rust_bridge.py`). Manages event bus, session lifecycle, telemetry, credentials, and daemon service.
- **Hybrid Intelligence Layer**: Model catalog, inference routers, heuristic routing policies, and fallback engines (Cloud, Ollama, vLLM, Apple MPS).
- **Agent Framework**: ReAct, Orchestrator, Deep Research, Claude Code agent, and SkillOrchestra agent pools.
- **Communication & Protocols**: A2A (Agent-to-Agent protocol), MCP (Model Context Protocol), SSE, WebSocket, and 30+ channel connectors.
- **Learning & Optimization**: Tracing collector, DSPy/ACE optimizers, complexity analyzer, and spec search.
- **Execution Sandbox**: Docker and Wasm container runners with strict mount security.

## 3. Technology Stack
- **Core / Backend**: Python 3.11+, Rust (PyO3 bridge), Pydantic, FastAPI, Uvicorn, asyncio
- **Engines**: OpenAI, Anthropic, Google Gemini, Ollama, vLLM, Groq, NVIDIA, DeepSeek
- **Sandboxing**: Docker SDK, Wasmtime / WASI
- **Database & RAG**: SQLite, Chroma, BM25, ColBERT backend, text chunking
- **Speech**: Faster-Whisper, Deepgram, Cartesia, Kokoro, ElevenLabs
- **Protocols**: Model Context Protocol (MCP), Agent-to-Agent (A2A) protocol

## 4. Directory Structure
```
OpenJarvis/
├── src/openjarvis/
│   ├── a2a/ (protocol, client, server)
│   ├── agents/ (claude_code.py, deep_research.py, channel_agent.py, hybrid/)
│   ├── channels/ (discord, slack, telegram, email, bluebubbles, cli, web)
│   ├── connectors/ (google, apple, github, notion, etc.)
│   ├── core/ (config, credentials, events)
│   ├── engine/ (cloud, vllm, ollama, apple_fm)
│   ├── learning/ (routing, optimize, spec_search, grpo_trainer)
│   ├── mcp/ (client, loader, protocol)
│   ├── memory/ (extractor, service, store)
│   ├── sandbox/ (mount_security, runner, wasm_runner)
│   ├── scheduler/ (scheduler, store, tools)
│   ├── security/ (audit, boundary, capabilities)
│   ├── skills/ (dependency, executor, importer, sources)
│   ├── speech/ (faster_whisper, cartesia_tts, deepgram)
│   ├── tools/ (agent_tools, apply_patch, storage RAG)
│   ├── traces/ (analyzer, collector, store)
│   └── workflow/ (builder, engine, graph)
├── rust/ (Cargo.toml, native performance extensions)
├── frontend/ (Vue / React web client)
└── desktop/ (Tauri / Electron desktop wrapper)
```

## 5. Core Modules
- `EventBus` (`core/events.py`): Central asynchronous pub/sub event system decoupling subsystems.
- `A2A Protocol` (`a2a/protocol.py`): Standardized agent-to-agent JSON-RPC exchange enabling multi-agent coordination.
- `DeepResearchAgent`: Multi-step query decomposition, multi-source web crawling, evidence extraction, citation tracking, and report synthesis.
- `SkillOrchestra`: Dynamic skill pool loader resolving dependencies, importing skills from Git/Hermes, and executing sandboxed skills.
- `SandboxRunner`: Secure isolated execution environment (Docker/Wasm) preventing unauthorized host filesystem access.
- `LearningOrchestrator` & `RoutingPolicy`: Heuristic and learned complexity-based routing selecting optimal models based on task requirements.
- `TraceStore`: Structured recording of full execution traces (latency, token consumption, tool invocations, user feedback).

## 6. AI / Model Architecture
- Universal inference engine abstraction (`engine/cloud.py`, `engine/vllm.py`, `engine/ollama.py`).
- Intelligent router balancing cost, context window, latency, and capability.
- Automatic failover across cloud and local backends.

## 7. Agent Architecture
- Multi-agent orchestration framework:
  - `ClaudeCodeAgent`: Interactive coding, repository exploration, diff patching, terminal tests.
  - `DeepResearchAgent`: Long-horizon autonomous research with synthesis and citations.
  - `OrchestratorAgent`: Decomposes complex tasks and delegates to specialist subagents.

## 8. Tool Architecture
- Universal tool registry with Pydantic schema validation, permission gates, retry policies, and timeout handling.
- Comprehensive built-in tool suite (40+ tools covering git, system, web, calendar, files, shell).

## 9. Memory Architecture
- Multi-tier memory service:
  - Working session memory with context compression.
  - Long-term semantic fact extraction (`extractor.py`).
  - Hybrid RAG storage combining BM25 keyword search and dense vector embeddings (ColBERT/Chroma).

## 10. Voice Architecture
- Ultra-low latency voice pipeline:
  - STT: Faster-Whisper, Deepgram streaming.
  - TTS: Cartesia, Kokoro, Edge TTS, ElevenLabs.

## 11. Vision Architecture
- Multimodal visual reasoning integrated into tool calling and agent decision pipelines.

## 12. Screen / Computer-Use Architecture
- System connectors providing OS automation and window inspection.

## 13. Coding Architecture
- Full coding suite: syntax-aware file search, regex search, patch application, test runner, git diff analysis.

## 14. Browser Architecture
- Headless browser automation connectors and web content extractors.

## 15. Plugin Architecture
- Pluggable skill sources (local directory, GitHub repositories, remote registries) with dependency resolution.

## 16. MCP Architecture
- Full-spec Model Context Protocol client and server implementation supporting dynamic tool discovery and resource sampling.

## 17. Scheduling
- Persistent SQLite-backed cron scheduler executing periodic agent workflows, daily briefings, and monitoring jobs.

## 18. Automation
- Directed acyclic graph (DAG) workflow engine (`workflow/engine.py`) executing complex multi-step pipelines.

## 19. Security
- Multi-layered security framework:
  - Capability-based authorization (`security/capabilities.py`).
  - Boundary filters and audit loggers (`security/audit.py`).
  - Mount security preventing path traversal in sandboxed tasks.
  - Credential vault securing API keys and tokens.

## 20. Permissions
- Granular permission flags per tool and per agent scope.

## 21. Database
- SQLite database with Alembic/custom schema migrations.

## 22. Configuration
- Hierarchical configuration system with environment overrides and schema validation.

## 23. CLI
- Comprehensive CLI (`openjarvis cli`) offering subcommands: `ask`, `agent`, `models`, `tools`, `doctor`, `trace`, `schedule`.

## 24. API
- REST & WebSocket API matching OpenAI API compatibility for standard chat and completions endpoints.

## 25. UI
- Desktop and web interfaces with execution tracking, trace inspector, and chat stream.

## 26. Telemetry
- Structured telemetry collector aggregating model latency, token metrics, and energy consumption.

## 27. Testing
- Over 700 automated tests covering unit, integration, benchmark, and security boundaries.

## 28. Deployment
- Docker Compose, Makefile, uv-based dependency management, and multi-platform packaging.

## 29. Strengths
- Unrivaled architectural depth: EventBus, A2A protocol, Deep Research, Skill pools, MCP, and Docker sandboxing.
- Hybrid learning and trace collection infrastructure.
- Multi-channel connectivity and OpenAI-compatible API server.

## 30. Weaknesses
- Large monolithic codebase with significant dependencies.
- High setup complexity if all optional services (Docker, vLLM, Rust extensions) are required.

## 31. Features Worth Adopting for OMEN
- EventBus pub/sub architecture.
- Deep Research agent with multi-source synthesis and citations.
- ModelContextProtocol (MCP) client.
- Skills registry and loader.
- Sandboxed tool execution with mount security.
- Structured execution tracing and complexity-based routing.
- Comprehensive CLI (`doctor`, `ask`, `status`, `trace`).

## 32. Architectural Patterns Worth Adopting
- Event-driven decoupling via EventBus.
- Capability-based security model.
- Trace store for learning and auditability.

## 33. Features NOT to Copy
- Excessive enterprise complexity and dependencies unnecessary for a personal desktop OS assistant.

## 34. Licensing Concerns
- Licensed under Apache License 2.0. Permissive; clean independent implementation used in OMEN with required attribution notices.
"""
    with open("docs/reference-analysis/05-OPENJARVIS.md", "w", encoding="utf-8") as f:
        f.write(content)

write_alice()
print("Wrote 02-ALICE.md")
write_marven()
print("Wrote 03-MARVEN.md")
write_openguider()
print("Wrote 04-OPENGUIDER.md")
write_openjarvis()
print("Wrote 05-OPENJARVIS.md")
