# OMEN UI CAPABILITY MAP

This document maps every backend capability, engine, tool, and service in OMEN to its interactive UI representations in the new Adaptive Desktop Interface.

---

## 1. Core Architecture & Runtime Mapping

| Backend Component | Module / Entry Point | Real Capabilities | Required UI Representation |
| :--- | :--- | :--- | :--- |
| **Agent Core & Planner** | `core/agent.py`<br>`core/planner.py`<br>`core/executor.py` | Multi-step task planning, reasoning, streaming responses, plan re-evaluation | • Central Omnibar & Chat Feed<br>• Real-time Agent Activity side panel (step hierarchy, progress %)<br>• Plan execution stepper |
| **Tool Registry** | `tools/registry.py` (49 tools) | OS operations, coding, browser, files, system control, vision, news, email | • Live Tools HUD cards<br>• Command Palette (`Ctrl+K`) direct execution<br>• Structured output cards in conversation |
| **Voice Engine (STT & TTS)** | `voice/stt.py`<br>`voice/tts.py`<br>`providers/stt/speech_rec.py`<br>`providers/tts/local_tts.py` | Speech capture, continuous conversation, pyttsx3 speech synthesis, VAD | • Central 3D Particle Sphere (voice-reactive amplitude/frequency deformation)<br>• Floating Voice capsule indicator (`Listening...` with waveform)<br>• Mic toggle button |
| **Memory & Knowledge** | `core/memory.py`<br>`memory/fact_memory.py`<br>`database/repositories.py` | Short-term conversation history, SQLite facts, ChromaDB embeddings | • System Status pill (`Memory: Active`)<br>• Memory View with facts, categories, search, pin/delete |
| **Research Engine** | `core/research/deep_research.py` | Multi-phase web crawl, query generation, synthesis, citation tracking | • Deep Research Omnibar action pill<br>• Research View: Dossier viewer, search queries tree, sources list |
| **Coding Engine** | `tools/coding/*`<br>`tools/coding/terminal_runner.py`<br>`tools/coding/git_tool.py`<br>`tools/coding/apply_patch.py`<br>`tools/coding/checkpoint_store.py` | Shell execution, Git operations, unified diff patching, code checkpoints | • Tiled Code Workspace panel<br>• Terminal runner tab with real shell output<br>• Checkpoint rollback interface |
| **Browser Engine** | `tools/browser/browser_ops.py` | URL launching, webpage text extraction, search results | • Mini Browser panel in workspace<br>• Quick URL navigation & summary triggers |
| **Computer Use & Automation** | `automation/*`<br>`tools/system/input_control.py`<br>`vision/element_detect.py` | Mouse click, cursor move, keyboard typing, window switching, screenshot target finding | • Computer Use pill in Omnibar<br>• Screen overlay & interactive target highlighting |
| **Vision Engine** | `tools/vision.py`<br>`automation/screenshots.py` | Full-screen capture, element detection, OCR / scene description | • Vision Inspector panel<br>• Screenshot attachment preview |
| **System & Telemetry** | `app/hardware.py`<br>`tools/system/system_info.py` | CPU %, RAM %, Battery %, Disk, Process list, Hardware profile | • System Status card on Home view (live CPU/RAM bars)<br>• Telemetry HUD |
| **Productivity & Scheduler** | `productivity/*`<br>`scheduler/*` | Tasks (CRUD, complete), Reminders, Pomodoro timer, Cron jobs | • Recent Tasks widget on Home view<br>• Tasks Workspace panel with Today/Upcoming tabs<br>• Reminders & Pomodoro controls |
| **Safety & Security** | `safety/*`<br>`security/*` | Emergency stop, user confirmation dialogs, credential vault | • Emergency stop trigger (`Ctrl+Shift+Esc`) & active banner<br>• High-risk action confirmation modal |

---

## 2. Central 3D Particle Sphere State Matrix

The particle sphere acts as the living physical manifestation of OMEN. It is rendered in high-performance hardware-accelerated graphics (using OpenGL / mathematically projected dynamic particles with depth sorting and glow blurs).

| State | Visual Behavior | Color Palette | Audio / Mouse Interaction |
| :--- | :--- | :--- | :--- |
| **IDLE** | Gentle organic breathing, slow orbital rotation, slight harmonic oscillation | Deep Nebula Violet (`#6C5CE7`) to Cyan (`#00D2EE`), 12% ambient glow | Responds to cursor proximity with gentle gravitational pull |
| **LISTENING** | Radial expansion, particle spikes modulated by microphone amplitude & frequency | High-contrast Electric Cyan (`#00F5FF`) with White core sparks | Real-time deformation matching voice volume; pulse ring ripples outwards |
| **THINKING** | Rapid internal vortex rotation, particles swirling inward toward nucleus | Bioluminescent Purple (`#A29BFE`) with shimmering amber accents | Orbit speed scales with planning duration; mouse hover perturbs vortex |
| **SPEAKING** | Harmonically pulsating wave rings emitting along the equatorial plane | Emerald Cyan (`#00E5FF`) and Soft Lavender (`#D8B4FE`) | Pulse amplitude syncs with TTS playback envelope |
| **TOOL EXECUTION** | Tangential particle streams ejecting outward like data packets | Technical Amber (`#F59E0B`) & Electric Blue | Orbit sparks highlight active tool category (Browser, Code, Terminal) |
| **SUCCESS** | Coherent luminous bloom that expands smoothly and settles back to idle | Pure Emerald (`#10B981`) and Star White | Quick calming ripple |
| **ERROR** | Turbulent erratic vibration, fractured orbital rings, red dispersal | Warning Crimson (`#EF4444`) to Dark Rose | Slow decay back to idle upon resolution |

---

## 3. Screen Layout & Progressive Disclosure Architecture

### 3.1 Layout Anatomy (Reference: NOVA Architecture)
```
+-------------------------------------------------------------------------------------------------------+
| [OMEN Orb] OMEN  [Search anything... Ctrl+K]               (Vol) (Net) [Model: Ollama/Cloud] [Time]   |
+-------------------+---------------------------------------------------------------+-------------------+
| [Home]            |  [System Status]              [Listening Capsule]             | [Agent Activity]  |
| [Chat]            |  * Online                     (Mic) [Live Waveform]           | Step 1: [x] Done  |
| [Projects]        |  Model: Mistral-Nemo                                          | Step 2: [>] Active|
| [Research]        |  Voice: Active  Agents: 1                                     | Progress: [==== ] |
| [Tasks]           |  CPU: [=== ] 14%  RAM: 28%                                    |                   |
|                   |                                                               | [Live Tools]      |
| Workspace         |                  [ CENTRAL 3D PARTICLE SPHERE ]               | * Terminal (run)  |
| - Files           |                       (States: Idle/Voice)                    | * Browser (open)  |
| - Terminal        |                                                               |                   |
| - Git             |                      "Good evening, Axion"                    | [Recent Tasks]    |
| - Agents          |                  "What can I do for you today?"               | [x] Fix auth bug  |
| - Browser         |                                                               | [ ] Research docs |
| - Use Computer    |      +--------------------------------------------------+     |                   |
|                   |      | [Ask anything...]               (Mic) (Send)     |     | Model: [Switch]   |
| Personal          |      | [+] [Deep Research] [Code] [Browse] [Use Computer]    |     | Voice: [On/Wave]  |
| - Memory          |      +--------------------------------------------------+     +-------------------+
| - Notes           |                                                                                   |
| - Calendar        |      [Chat] [Research] [Code] [Tasks] [Projects] [More Tools]                     |
|                   +-----------------------------------------------------------------------------------+
| System            |  [ Tiled Workspace Deck: Code / Browser / Terminal / Tasks ]                      |
| - Integrations    |  +--------------------+---------------------+------------------+-----------------+  |
| - Activity        |  | Code Editor        | Mini Browser        | Terminal         | Tasks           |  |
| - Settings        |  +--------------------+---------------------+------------------+-----------------+  |
+-------------------+-----------------------------------------------------------------------------------+
```

### 3.2 Progressive Disclosure Tiers
1. **Tier 1 (Surface / Minimal)**:
   - Floating Particle Sphere + Clean greeting + Omnibar input + System status capsule + Agent activity badge.
   - Screen feels vast, calm, uncluttered, focused.
2. **Tier 2 (Interactive Context)**:
   - When user queries code, research, or terminal: Tiled workspace panels smoothly slide up or expand.
   - Omnibar action pills dynamically adapt (`[Deep Research]`, `[Code]`, `[Browse]`, `[Use Computer]`).
3. **Tier 3 (Deep Workbench)**:
   - Collapsible right sidebar opens full Agent traces, tool call parameters, inspection trees, and memory inspection.
   - Full-page dedicated views accessible via navigation sidebar (Files, Git, Research Dossier, System Telemetry, Settings).

---

## 4. Real Functional Verification Checklist

Every component designed for the new UI is bound directly to functional backend code:
- [x] Omnibar query -> `Agent.run_step()` / `AgentEngine.step()`
- [x] Voice capsule -> `OmenSTT.listen_once()` & `OmenTTS.speak_async()`
- [x] CPU / RAM bars -> `app/hardware.py` / `psutil`
- [x] Agent Activity -> `core/events.py` `EventBus` (`PLAN_STEP_COMPLETED`, etc.)
- [x] Live Tools -> `core/traces/trace_collector.py` & `tools/registry.py`
- [x] Tiled Terminal -> `tools/coding/terminal_runner.py`
- [x] Tiled Code -> `tools/filesystem/file_ops.py` & `tools/coding/apply_patch.py`
- [x] Recent Tasks -> `productivity/tasks.py` / `database/repositories.py`
- [x] Command Palette -> `ui/command_palette.py` with 30+ registered commands
