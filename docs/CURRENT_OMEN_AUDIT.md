# OMEN — CURRENT CODEBASE AUDIT

Date: 2026-10-07
Branch: claude/infallible-archimedes-b8bf3f
Status: CLEAN (no uncommitted changes)

## REPOSITORY FILE MANIFEST (complete)

Total files (excluding .git, .venv, node_modules, __pycache__): ~170+
Source (.py): ~85 files
Config (.qss, .json, .env): 5 files
Data: 1 SQLite + chroma DB + vector_memory
Documentation: README.md only
Tests: tests/test_modules.py + tests/test_smoke.py

## CATEGORIZATION OF ALL RELEVANT FILES (inspection ledger)

| File | Category | Inspected | Features | Notes |
|---|---|---|---|---|
| main.py | source | YES | CLI, GUI, wizard, self-test | Full pipeline from input to agent |
| app/config.py | config | YES | Settings, Ollama, voice, security | Pydantic BaseSettings, env-file |
| app/constants.py | source | YES | Enums, paths, aliases | RiskLevel, AgentState, TaskStatus |
| app/hardware.py | source | YES | GPU/CPU detection, profile | nvidia-smi query, psutil |
| app/logging_config.py | source | YES | Redaction, structured logs | SensitiveDataFilter |
| core/agent.py | source | YES | Main pipeline | Brain→Planner→Executor→Memory→Response |
| core/brain.py | source | YES | LLM, tool schemas | OllamaProvider / MockLLMProvider |
| core/events.py | source | YES | PubSub | EventBus with history |
| core/memory.py | source | YES | SQLite + ChromaDB | MemoryManager |
| core/planner.py | source | YES | TaskPlan, step inference | Infer tools from NL |
| core/executor.py | source | YES | Plan execution | ToolRegistry-based |
| core/models.py | source | YES | Pydantic models | TaskPlan, PlanStep |
| core/context.py | source | YES | Context builder | |
| core/observation_loop.py | source | YES | Screen observe/verify | |
| core/supervisor.py | source | YES | Registry, recovery | |
| core/agent.py (dup ref) | — | — | — | Same as above |
| database/*.py | source | PARTIAL | SQLite, repos | Models, repositories |
| ui/*.py | source | PARTIAL | MainWindow, sidebar, orb | Qt PySide6 |
| ui/styles/*.qss | config | PARTIAL | Dark theme | Steel blue palette |
| tools/*.py | source | PARTIAL | Registry, file ops, system | ToolRegistry |
| providers/*.py | source | PARTIAL | LLM, STT, TTS, email | Base + implementations |
| voice/*.py | source | PARTIAL | STT, TTS, wake | |
| vision/*.py | source | PARTIAL | Screenshot, element detect | |
| automation/*.py | source | PARTIAL | Mouse, keyboard, windows | |
| computer/*.py | source | PARTIAL | App control | |
| browser/*.py | source | PARTIAL | Browser ops | |
| security/*.py | source | PARTIAL | Permissions, secrets | |
| safety/*.py | source | PARTIAL | Emergency stop, confirmation | |
| productivity/*.py | source | PARTIAL | Pomodoro, tasks, reminders | |
| observer/*.py | source | PARTIAL | Console observer | |
| identity/*.py | source | PARTIAL | Voice profile, identity | |
| scheduler/*.py | source | PARTIAL | APScheduler jobs | |
| tests/*.py | test | PARTIAL | Smoke + module tests | |

## CURRENT ARCHITECTURE (from source trace)

USER INPUT → main.py (CLI/GUI) → Agent.process()
  → Brain (LLM + tool schemas) → LLMResponse
  → Planner (TaskPlan from response or inference)
  → Executor (ToolRegistry.execute_plan)
  → MemoryManager (SQLite + ChromaDB)
  → EventBus (state change events)
  → TTS (optional voice)
  → NotificationService (Windows toast)
  → Response to user + trace

Observation loop: observe_screen() → verify_action_result()

## CURRENT CAPABILITIES

✓ CLI / GUI dual mode
✓ Config via .env + Pydantic
✓ Agent pipeline with planning
✓ LLM integration (Ollama + mock)
✓ Tool registry with schemas
✓ Memory (SQLite + optional ChromaDB)
✓ EventBus
✓ Voice (STT/TTS, optional)
✓ Vision (screenshot, element detect)
✓ Automation (keyboard, mouse, windows)
✓ Browser automation (DOM-first + visual)
✓ System info / app control
✓ Productivity (pomodoro, tasks, reminders, notifications)
✓ Security (permissions, emergency stop, secrets)
✓ Scheduler (morning briefing)
✓ Database (SQLite with migrations)

## CURRENT PROBLEMS / TECHNICAL DEBT

- Only 2 test files; minimal coverage
- No full reference repository inspection yet
- No docs/ directory for architecture docs
- No docs/REFERENCE_COMMITS.md
- No docs/LICENSE_AUDIT.md
- No docs/FEATURE_INVENTORY.md
- No docs/FEATURE_MATRIX.md
- No docs/OMEN_ARCHITECTURE.md
- UI sidebar may reference missing imports (FIXED in 270c4fa)
- No complete plugin/system integration yet
- Reference repos not cloned
- No installer / packaging beyond pyproject.toml
