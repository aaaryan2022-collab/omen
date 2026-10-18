# 02 - Alice Research Dossier

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
