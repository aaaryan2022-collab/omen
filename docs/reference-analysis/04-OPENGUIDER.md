# OPENGUIDER COMPLETE INSPECTION REPORT
Repo: reference/OpenGuider/ | 126 files | 2026-10-08

## 1. DIRECTORY TREE
All directories covered: .github/workflows, docs, landing, renderer (assets/components/css/js/panel/widget), scripts, src (agent/ai/context/core/ipc/perception/plugins/browser/python/session/tts/utils/validation), tests (integration/ui/unit).

## 2. FILE MANIFEST + CATEGORIES
SRC: main.js, preload.js, all src/* (~48 files), renderer/* (~24), landing/*, scripts/* (2)
CFG: package.json, .github/*.yml, llm-config.js, requirements.txt
DOC: README.md (14.6KB), AGENTS.md, docs/*.md, docs/*.pdf, LICENSE, THIRD_PARTY
TST: 18 test files (integration/task-orchestrator; ui/7; unit/10)
SCR: after-pack.js, download-browser-agent.js
AST: logo.*, full/half-closed.png, landing.css/js, style.css, tutorial.gif
DEP: eng.traineddata (5.2MB Tesseract)
BLD/IRR: .git internals, package-lock

## 3. FULL SOURCE INSPECTION (read in full)
main.js (1953ln/71.5KB): Electron main — tray, windows, IPC, AI stream, screenshot, pointer calibration (buildPointerCalibration/updatePointerCalibration by display), cursor overlay, session/task init, plugin registry, FAST_MODE_PROMPT embedded.
preload.js (28ln): Bridge.
package.json: openguider 0.3.5, electron 34.3, langchain packages, tesseract, ws, zod.
src/agent/task-orchestrator.js (1320ln/44KB): Core orchestrator — planner/executor/evaluator/replanner/fallback chains, approval/autopilot (trust-manager), session continuity.
src/agent/planner/replanner/executor/evaluator/fallback/interaction/llm-client/schemas/tools/*: All inspected.
src/ai/index.js (19KB): streamAIResponse, parsePointTag, fetchOllamaModels — multi-provider.
src/core/execution-engine/intent-router/plugin-registry/step-queue/trust-manager: Engine, routing, plugins, queue, trust.
src/plugins/browser/index.js (16KB): BrowserPlugin; sidecar.js; llm-config; risk-scorer; python/agent_server.py (28KB)/hitl_hooks.py/14KB/json_repair/requirements.txt — browser-use via Python sidecar with HITL.
src/perception/ocr-engine/ui-scanner/window-enum: Tesseract OCR + UI scan + window enum.
src/session/session-manager/persistence/schema/element-cache: Continuity, persistence (electron-store), Zod schemas, element cache.
src/tts/*.js + panel/ptt.js/tts.js: TTS (OpenAI/Google/Windows) + PTT.
src/screenshot.js + tools/pointer-tool.js: Multi-display capture + [POINT:x,y:label] parsing + calibration.
renderer/components/step-approval/ExecutionLog.js + js/app.js/panel/*.js + settings.html/js: Panel (440x660), widget (220px), approval cards, execution log, settings, messaging, plan-view, bootstrap, state, ui.

## 4. ARCHITECTURE TRACE (CODE-LEVEL)
USER INPUT -> renderer/app/messaging -> preload -> main ipc -> intent-router -> task-orchestrator -> planner-chain -> step-queue -> execution-engine -> executor-chain -> tool (pointer/capture/plan/browser) -> ai/index.js stream -> provider (Claude/OpenAI/Gemini/Groq/Ollama/OpenRouter) -> response -> structured parse -> pointer emission (calibrated) -> evaluator -> replanner -> session save -> renderer update (execution-log/plan-view/approval) -> cursor overlay -> TTS -> OUTPUT.
Browser sub: browser/index -> sidecar -> agent_server.py -> hitl_hooks (approval) -> risk-scorer -> screenshot -> ui-scanner/ocr -> AI guided -> actions -> browser-bridge -> evaluation.

## 5. MODELS / AGENTS / TOOLS / PLAN / SCREENSHOT / SESSION / VOICE / PLUGIN / APPROVAL / UI ARCHITECTURE
MODELS: 6 providers (Anthropic, OpenAI, Google GenAI, Groq, Ollama, OpenRouter) via langchain/direct APIs; selected by aiProvider setting.
AGENTS: planner/executor/evaluator/replanner/fallback/task-orchestrator chains.
TOOLS: pointer-tool, capture-screen-tool, plan-tool, browser-tools (Python agent_server).
PLAN: Goal->plan->steps via planner-chain + step-queue; replanner on failure.
SCREENSHOT/AWARENESS: screenshot.js (displayId/screenNumber/width/height); ui-scanner + ocr-engine; pointer-tool [POINT] tags; calibration scaleX/scaleY per display.
SESSION: session-manager + persistence + schema + element-cache + electron-store.
VOICE: TTS 3 providers + PTT (ptt.js + main.js isPushToTalkRecording).
PLUGIN: interface + registry + browser plugin + BROWSER_PLUGIN_RELEVANT_SETTINGS integration.
APPROVAL: trust-manager + approval.html/StepApprovalCard + fast-mode prompt + HITL hooks (Python).
UI: Main (system/AI/screenshot/TTS) / Agent (chains) / Provider (ai/index) / Renderer (panel/widget/settings/approval/log) / Preload (secure bridge).

## 6. KEY ARCHITECTURAL DECISIONS
1. Electron main/renderer + preload (secure). 2. Chain architecture (modular/replanning). 3. Multi-provider langchain (not vendor-locked). 4. Python sidecar for browser automation. 5. Screenshot calibration for multi-monitor clicks. 6. HITL at Python layer. 7. Fast-mode embedded prompt. 8. Secure store (safeStorage) for keys. 9. Plugin registry. 10. Zod session schemas.

## 7. DEPENDENCIES
electron 34.3, @langchain/anthropic/core/google-genai/openai, @xenova/transformers, tesseract.js + 5.2MB eng.traineddata, ws, zod, electron-store, google-tts-api, onnxruntime-node, (optional) keytar/rcedit.

## 8. ENTRY POINTS & ROUTING
Start: electron . -> main.js -> whenReady -> window/tray/shortcuts/plugins/task. Input: panel/voice/CLI -> IPC -> router -> orchestrator -> chains -> execution -> AI -> result -> session -> renderer update.
Pointer: AI text [POINT] -> parse -> calibrate -> overlay -> click.
Browser: plugin -> sidecar -> Python -> HITL -> actions -> bridge -> evaluation.

## 9. TESTS
18 files inspected (integration/task-orchestrator.test.js; ui/7; unit/10). node --test runner. Mocked ai-providers for integration.

*INSPECTION COMPLETE — all 126 files categorized; all relevant text-based source/config/doc/test inspected; full architecture traced from entry through agent chains, AI providers, screenshot awareness, pointer calibration, session continuity, browser automation, approval/autopilot, voice, plugin architecture, and renderer components.*
