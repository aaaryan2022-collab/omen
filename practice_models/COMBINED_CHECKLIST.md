# COMBINED FEATURE CHECKLIST — Alice + Marven + OpenGuider → OMEN
# Source repos: practice_models/Alice (125M), Marven (4.8M), OpenGuider (55M)
# Goal: MAX features / MIN size. Tony Stark mode.

## [A] ALICE (animation / electron / visual)
- [ ] 3D animation engine (gif-based → real-time CSS/WebGL)
- [ ] Electron shell architecture (renderer + preload + main)
- [ ] Glass-morphism card grid
- [ ] Animated AI orb with state transitions
- [ ] Multi-language docs
- [ ] Auto-update / packaging (electron-builder)

## [M] MARVEN (app / memory / security / voice)
- [ ] Memory alias resolution (FactMemory)
- [ ] 5 permission scopes + confirmation modal
- [ ] Audit log (capped 200, append-only)
- [ ] Module-level JSON cache
- [ ] Crash recovery (backoff respawn 1s→2s→4s→8s→16s)
- [ ] Health-check startup sequence + /health polling
- [ ] Wake-word listener (openWakeWord)
- [ ] VAD + barge-in + continuous voice mode
- [ ] Live partial transcript (liveTranscribe / Whisper tiny)
- [ ] Real confirmation dialog (shared ConfirmDialog)
- [ ] Settings UI (AI, Voice, Security, Memory, Automations)
- [ ] Automations page + routines (Gaming Mode / Work Mode)
- [ ] Reduced-motion support

## [O] OPENGUIDER (agents / guides / multi-lang)
- [ ] Agent orchestration framework (AGENTS.md)
- [ ] Multi-language user guides (EN / TR / docs)
- [ ] Configuration PDFs + landing pages
- [ ] Trained OCR/model data (eng.traineddata)
- [ ] Open-source agent workflows

## [OMEN EXISTING — PRESERVE]
- [ ] PySide6 holographic backend
- [ ] 3D cube orb (manual projection)
- [ ] Glass cards + QSS themes
- [ ] SQLite WAL + Chroma vector memory
- [ ] 7 passing pytest tests

## [FUSION — SUPERIOR OMEN TARGET]
- [ ] Combine: Electron-style UI shell + OMEN 3D cube
- [ ] Add: Confirm dialog + audit log + 5 scopes (from Marven)
- [ ] Add: Routines + automations + memory facts (Marven)
- [ ] Add: Wake-word + VAD + live caption (Marven)
- [ ] Add: Update/packaging + tray + startup (Marven/Alice)
- [ ] Add: Agent orchestration layer (OpenGuider)
- [ ] MINIMIZE: Remove redundant build artifacts, keep only code that serves features
