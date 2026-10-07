# OMEN ARCHITECTURE — SYNTHESIS FROM FIVE REFERENCES

Based on deep inspection of JARVIS, Alice, Marven, OpenGuider, OpenJarvis + existing OMEN source.

## Core Design Principles
- Independent primitives (not monolithic)
- Local-first by default
- Multi-model abstraction (not hard-coded)
- Security by design (permissions + confirmation)
- Study references, do not copy AGPL/MIT code directly

## OMEN CORE STRUCTURE (recommended)

OMEN CORE
├── Intelligence
│   ├── Brain (LLM router + tool schemas)
│   ├── Planner (TaskPlan from NL / tool calls)
│   ├── Memory (SQLite + vector)
│   └── Context (conversation + retrieval)
├── Inference Engines
│   ├── ModelRegistry (Ollama, cloud, custom)
│   └── EngineRouter (task-type + complexity)
├── Agent Runtime
│   ├── Agent (process pipeline)
│   ├── SimpleAgent
│   ├── ChatAgent
│   ├── OrchestratorAgent
│   ├── CodeAgent
│   ├── ResearchAgent
│   ├── VisionAgent
│   └── ComputerUseAgent
├── Tool Runtime
│   ├── ToolRegistry (universal)
│   ├── FileOps
│   ├── SystemControl
│   ├── BrowserOps
│   └── CodingTools
├── Memory
│   ├── ConversationMemory
│   ├── ProjectMemory
│   ├── DocumentMemory (RAG)
│   └── TaskMemory
├── Learning / Traces
│   ├── EventBus
│   ├── TraceLog
│   └── RoutingHeuristics
├── Security
│   ├── PermissionManager
│   ├── ConfirmationSystem
│   ├── SecretStore
│   └── Sandbox (where practical)
├── Plugin System
│   ├── PluginRegistry
│   └── SkillRegistry
├── Scheduler
│   ├── APScheduler integration
│   └── JobRegistry
├── Observability
│   ├── Monitor (system info)
│   ├── Trace (request→result)
│   └── Telemetry (local-only default)
└── Configuration
    ├── Pydantic settings (env + file)
    └── Project workspace config

## Model Abstraction (required for parity)
Providers: Ollama, OpenAI-compatible, Anthropic-compatible, Google-compatible, OpenRouter, NVIDIA, custom endpoints.
Models: PRIMARY, FAST, REASONING, VISION, CODING, EMBEDDING, SPEECH-TO-TEXT, TEXT-TO-SPEECH, FALLBACK.
Never hard-code around one.

## Hybrid Intelligence (optional multi-model)
Complex task → Intent Router → Vision → Reasoning → Coding → Verification → Tool Execution → Final Answer.
Simple question → ONE MODEL.
