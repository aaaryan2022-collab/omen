# 03 - Marven Research Dossier

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
