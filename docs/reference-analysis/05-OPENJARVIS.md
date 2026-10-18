# 05 - OpenJarvis Research Dossier

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
