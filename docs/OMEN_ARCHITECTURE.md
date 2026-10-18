# OMEN Architecture — The Personal AI Operating Layer

## High-Level Vision
OMEN fuses the architectural triumphs of the five reference systems into a cohesive, high-performance, resilient desktop operating layer for Windows:
- **From JARVIS**: Clean dual-process supervisory lifecycle, scoped personal folder permissions, local Ollama engine fallback, action audit logging, and named routines.
- **From Alice**: Native Google Workspace integration (Calendar & Gmail OAuth2), user-defined Custom Tools engine, RAG document ingestion with PDF worker, and speech playback queue.
- **From Marven**: Monaco Editor integration, autonomous coding agent with unified diff patching, AST codebase indexing, checkpoint/rollback undo system, integrated terminal PTY, Git panel, and REST client.
- **From OpenGuider**: Dual-layer screen perception (Win32 screenshot + Tesseract OCR + Multimodal LLM), four-chain agent loop (Plan, Execute, Evaluate, Replan), browser sidecar automation, and floating Mini Mode widget.
- **From OpenJarvis**: Centralized asynchronous EventBus, Model Context Protocol (MCP) client, Deep Research agent, modular Skills registry, sandbox execution runtime, structured execution traces, and CLI diagnostics (`omen doctor`).

```
                              ┌────────────────────────────────────────┐
                              │            OMEN USER INTERFACE         │
                              │  (Main Window, Orb, Mini Mode, Palette)│
                              └───────────────────┬────────────────────┘
                                                  │ IPC / Events
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                       OMEN CORE                                        │
│                                                                                        │
│   ┌────────────────────┐   ┌────────────────────┐   ┌──────────────────────────────┐   │
│   │    EVENT BUS       │   │  SECURITY & TRUST  │   │      TRACING & LEARNING      │   │
│   │ (Asynchronous Hub) │   │(Permissions, HITL) │   │  (Metrics, Logs, Doctor)     │   │
│   └─────────┬──────────┘   └─────────┬──────────┘   └──────────────┬───────────────┘   │
│             │                        │                             │                   │
│   ┌─────────▼────────────────────────▼─────────────────────────────▼───────────────┐   │
│   │                                 AGENT RUNTIME                                  │   │
│   │  • OrchestratorAgent     • CodeAgent (AST/Diff/LSP)   • DeepResearchAgent      │   │
│   │  • Plan-Exec-Eval-Replan • BrowserAgent (Playwright)  • ScheduledAgent         │   │
│   └──────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                      │                                                 │
│   ┌──────────────────────────────────▼─────────────────────────────────────────────┐   │
│   │                            MODEL & INFERENCE LAYER                             │   │
│   │  • Model Catalog (Local Ollama/LMStudio, Cloud OpenAI/Anthropic/Gemini/NVIDIA) │   │
│   │  • Intelligent Router (Complexity, FIM, Vision, Fallback)                      │   │
│   └──────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                      │                                                 │
│   ┌──────────────────────────────────▼─────────────────────────────────────────────┐   │
│   │                             TOOL & SERVICE RUNTIME                             │   │
│   │  • System & App Control  • Monaco Editor / Terminal   • Screen Perception/OCR  │   │
│   │  • Git Management        • Google Workspace           • MCP Client & Skills    │   │
│   │  • Scoped File System    • Document & Code RAG        • Sandbox Container      │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

## Subsystem Breakdown

### 1. Intelligence & Model Layer
- Unified `ModelCatalog` supporting both local providers (Ollama, LMStudio, vLLM) and cloud endpoints (OpenAI, Anthropic, Google Gemini, OpenRouter, Groq, NVIDIA NIM).
- `ComplexityRouter`: Automatically evaluates prompt length, tool necessity, modality, and latency needs to direct to Fast, Reasoning, Vision, or Coding models.
- Transparent streaming adapters normalizing server-sent events across providers.

### 2. Multi-Agent Framework
- `OrchestratorAgent`: Decomposes high-level instructions into coordinated sub-plans.
- `CodeAgent`: Full developer agent equipped with unified patch applicator, checkpoint store for undo, syntax checking, terminal test execution, and Git diff inspection.
- `VisionAgent`: Takes screen captures, analyzes OCR bounding boxes via Tesseract, grounds UI elements, and executes Win32 clicks with visual pointer targets.
- `BrowserAgent`: Connects to isolated Playwright automation for multi-step web scraping and interaction with human-in-the-loop risk scoring.
- `DeepResearchAgent`: Multi-hop recursive research synthesizing citations from multiple web sources into comprehensive reports.

### 3. Memory & RAG Engine
- Multi-tier memory combining working short-term context, explicit user preference learning ("remember that my editor is VS Code"), and semantic vector retrieval.
- Hybrid Codebase & Document Indexer supporting PDF, TXT, Markdown, and source code files with `.gitignore` exclusion awareness.

### 4. Windows Desktop Integration
- Win32 API window discovery (`EnumWindows`), window focus/minimize, application launching and graceful termination.
- Hardware telemetry monitor tracking real-time CPU, GPU, RAM, VRAM, disk, and battery statistics.
- System tray integration, autostart via Windows login settings, and global hotkeys (`Ctrl+Space`).

### 5. Extensibility: Skills & MCP
- Native Model Context Protocol (MCP) client supporting tools and resources over stdio and SSE.
- Modular Skills system for loadable domain capabilities.
- Custom Tool Creator allowing users to register custom scripts with JSON schema inputs.

### 6. Security & Governance
- Granular capability-based permission model (`fs.read`, `fs.write`, `terminal`, `screen`, `system`, `network`).
- Interactive modal confirmation before destructive actions (file deletion, app termination, Git push, unconfirmed shell execution).
- SSRF guards and directory traversal boundary checks.
