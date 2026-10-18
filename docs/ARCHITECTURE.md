# OMEN System Architecture
## Local-First, Adaptive, Command-Driven AI Desktop Assistant

### 1. Architectural Principles
OMEN is designed as an autonomous command-driven desktop assistant for Windows 11. It operates primarily locally using free and open-source models (via Ollama or local endpoints) and open-source audio/automation tools.

The core design separates:
1. **Desktop Presentation (UI)**: PySide6 (Qt) interface with living 3D particle sphere, minimal Home view, and modular studio decks.
2. **Orchestration & Task Lifecycle**: A formal finite state machine governing commands, planning, user approval gates, and autonomous execution.
3. **Capability Layer (Tools)**: Over 49 typed, permission-gated tools across filesystem, process execution, git, browser, screen perception, and productivity.
4. **Perception & Interaction**: Audio STT/TTS engine, screen OCR/element detection, and Windows UI automation.
5. **Persistence & Knowledge**: SQLite relational database (`omen.db`) and ChromaDB vector embeddings (`data/vector_memory`).

---

### 2. Lifecycle State Machine
OMEN executes tasks through strict state transitions:

```
[STANDBY]
    │
    ▼ (Wake word / Omnibar / Shortcut)
[LISTENING] ──► [UNDERSTANDING] ──► [PLANNING]
                                          │
                                          ▼
                                 [AWAITING_APPROVAL] ◄── User reviews plan & permissions
                                          │
                        ┌─────────────────┴─────────────────┐
                        │ Approved                          │ Rejected
                        ▼                                   ▼
                   [EXECUTING]                         [STANDBY]
                        │
                        ▼ (Closed-loop: Observe → Act → Observe)
                   [VERIFYING]
                        │
                        ├─► Success: [STANDBY]
                        └─► Requires User Action: [AWAITING_EXTERNAL_ACTION]
```

#### States Definition:
- **`STANDBY`**: Idling with minimal background footprint. Listening for wake word or hotkeys.
- **`LISTENING`**: Capturing microphone audio with real-time waveform visualization.
- **`UNDERSTANDING`**: Parsing user intent, context, and required scopes.
- **`PLANNING`**: Generating an ordered step-by-step execution plan with risk annotations.
- **`AWAITING_APPROVAL`**: **Strict approval gate**. The user reviews the plan, target outputs, and requested tool permissions before any execution begins.
- **`EXECUTING`**: Independent execution of approved steps without intermediate micro-prompting.
- **`VERIFYING`**: Inspecting generated files, terminal exit codes, and UI states to confirm actual outcomes.
- **`AWAITING_EXTERNAL_ACTION`**: Paused for external user action (e.g., MFA login, human verification).
- **`SLEEPING`**: Suspended active execution, state persisted, awaiting wake command.
- **`RECOVERY`**: Rolling back failed state or restoring known-good configurations.

---

### 3. Module Boundaries

- `core/`
  - `agent.py`: Agent coordinator managing the interaction cycle.
  - `planner.py`: Multi-step plan generator and dependency solver.
  - `executor.py`: Safe tool invoker with timeout and cancellation hooks.
  - `events.py`: System-wide asynchronous `EventBus`.
  - `memory.py`: Vector and short-term conversation context.
- `voice/`
  - `stt.py`: Local speech recognition with sounddevice energy gating.
  - `tts.py`: Local pyttsx3 speech synthesis.
- `tools/`
  - `registry.py`: Central tool registry with scope permissions.
  - `filesystem/`: Safe file reading, writing, and directory scanning.
  - `coding/`: `terminal_runner.py`, `git_tool.py`, `apply_patch.py`, `codebase_indexer.py`.
  - `browser/`: Lightweight browser automation and HTML extraction.
  - `system/`: Hardware telemetry (`psutil`), application launching, and OS input.
- `automation/` & `vision/`:
  - Screen capture (`mss`), template matching, OCR, and element detection.
- `database/`:
  - SQLite schema for tasks, calendar events, notes, memories, and execution traces.
- `ui/`:
  - `main_window.py`: Window shell, top search bar, status indicators, and stack manager.
  - `sidebar.py`: Minimal 220px collapsible navigation sidebar.
  - `orb.py`: 3D reactive particle sphere manifesting assistant states.
  - `views/`: 15 modular views including `home_view`, `chat`, `tasks_view`, `files_view`, `coding_view`, `research_view`, and `system_view`.
- `tests/`:
  - 32+ unit, integration, and mandatory vertical test suites.
