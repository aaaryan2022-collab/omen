# OMEN BEFORE UPGRADE — BASELINE (2026-10-07)
ARCHITECTURE: PySide6 GUI (main_window.py), agent core (core/agent_engine.py thin 28L), orb (OmenOrb), permissions_v5 (FS_WRITE=False conservative), SQLite DB (database/), voice pipeline real, 5 refs (2 present: JARVIS/Alice; 3 missing: Marven/OpenGuider/OpenJarvis).
PRESENT: agent, orb, permissions, voice, chat view, sidebar, palette (SECONDARY_LIGHT ok), command palette, mini widget, emergency stop, 11 audit docs, 7 git commits with attribution.
PLACEhOLDERS/INCOMPLETE: core/planner.py thin, core/agent_engine minimal, no command center / agent center / model center / memory center / task trace / screen workspace / code agent / browser workspace / settings redesign; reference/ missing 3; OMEN_BEFORE_UPGRADE.md missing; no full backend registries (Model/Agent/Tool/Memory/Event/Task/Trace).
NOT BROKEN (verified): palette, orb paint, permissions — no critical crashes.
FILES TO MODIFY: ui/main_window.py (redesign), ui/styles/, core/ (registries), reference/ (clone), docs/ (after-upgrade).
RUN STATUS: git clean; python main.py launches (verified earlier); 3 e2e tests passed previously.
