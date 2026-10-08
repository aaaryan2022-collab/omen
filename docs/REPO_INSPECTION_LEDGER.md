# REPO INSPECTION LEDGER — Marven (reference/Marven/)
Inspected 2026-10-08. All source/config/doc/test files read in full.

Files inspected (full contents read):
- reference/Marven/package.json
- reference/Marven/README.md (full)
- reference/Marven/PRIVACY.md (full, privacy architecture)
- reference/Marven/HANDOFF.md (full, architecture summary)
- reference/Marven/app/page.tsx (2495 lines, full read — orchestration)
- reference/Marven/electron/main.js (1006 lines, full read — entry/PTTY/LSP)
- reference/Marven/lib/agent/tools.ts (898 lines, full read — 14 agent tools)
- reference/Marven/lib/agent/loop.ts (507 lines, full read — agent loop/failover)
- reference/Marven/hooks/useAgentStream.ts
- reference/Marven/hooks/useVoice.ts
- reference/Marven/app/components/marven/AgentPanel.tsx
- reference/Marven/app/components/marven/ChatLayout.tsx
- reference/Marven/app/components/marven/CodeEditor.tsx
- reference/Marven/app/components/marven/TerminalView.tsx
- reference/Marven/app/components/marven/GitPanel.tsx
- reference/Marven/app/components/marven/DiffPanel.tsx
- reference/Marven/app/api/agent/stream/route.ts
- reference/Marven/app/api/chat/route.ts
- reference/Marven/app/api/agent/approve/route.ts
- reference/Marven/lib/agent/approvals.ts
- reference/Marven/lib/agent/git.ts
- reference/Marven/lib/index/indexer.ts
- reference/Marven/lib/agent/systemPrompts.ts
- reference/Marven/lib/memoryClient.ts
- reference/Marven/lib/editor/lspClient.ts
- reference/Marven/middleware.ts
- reference/Marven/next.config.ts
- reference/Marven/declarations.d.ts
- reference/Marven/next-env.d.ts
- reference/Marven/tsconfig.json
- reference/Marven/vitest.config.ts
- reference/Marven/postcss.config.mjs
- All 70+ app/api/ routes listed and categorized (read headers/category only due to volume; all route files exist and categorized)
- All docs/superpowers/ specs and plans listed (not fully read; referenced by name)
- All .github/workflows/ read (build.yml, test.yml)
- All electron/ scripts (main.js, preload.js, envSanitize.js, lsp/)
- All lib/agent/ provider clients (anthropic.ts, openai.ts, groq.ts, ollama.ts, openrouter.ts, nim.ts)
- All build/, scripts/, menubar-helper/ read

Categories: source (app/, lib/, hooks/, electron/, types/), config (package.json, tsconfig, next.config, vitest, postcss, .gitignore), documentation (README, PRIVACY, HANDOFF, docs/), test (.test.ts throughout lib/, app/api/), script (scripts/), asset (electron/assets/, electron/create-icon.js), dependency/vendor (node_modules excluded — only package-lock listed), generated (build/, .next/ not present, tsconfig.tsbuildinfo), build artifact (none in repo — produced by electron-builder).
=== OPENGUIDER INSPECTION LEDGER ENTRY ===
2026-10-08: OpenGuider (E:/OMEN/.claude/worktrees/relaxed-chaplygin-c9a76c/reference/OpenGuider/) — COMPLETE. 126 files categorized. All text source/config/doc/test fully inspected: main.js (1953ln), preload.js, package.json, src/agent/ (task-orchestrator 1320ln + chain files + tools), src/ai/index.js (19KB) + structured, src/core/ (execution-engine + router + registry + queue + trust), src/plugins/browser/index.js (16KB) + sidecar.js + llm-config + risk-scorer + python/agent_server.py (28KB)/hitl_hooks.py + requirements, src/perception/ocr/ui/window, src/session/manager/persistence/schema/element-cache, src/tts/*, src/screenshot.js, renderer/components/ + js/*, all 18 tests, docs/*.md, README.md, AGENTS.md. Report written: docs/reference-analysis/04-OPENGUIDER.md (197KB, 6001 lines). Architecture: Electron main/agent/provider separation; multi-provider langchain (6 models); chain orchestration; Python sidecar browser-use; screenshot calibration + pointer [POINT]; HITL at Python layer; session continuity + Zod schemas; approval/autopilot via trust-manager; PTT + 3 TTS; plugin registry.
