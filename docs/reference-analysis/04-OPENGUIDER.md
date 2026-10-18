# 04 - OpenGuider Research Dossier

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
