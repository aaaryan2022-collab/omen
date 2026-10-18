# OMEN Implementation Plan
## Phased Roadmap for Complete Desktop Assistant Evolution

### Current Status
- **Baseline Health**: 32/32 tests passing (`python -m pytest tests/`).
- **Disk Footprint**: Reduced from 1,795 MB to 7.7 MB (clean, minimal repository).
- **Desktop UI**: PySide6 shell with particle Orb, Omnibar, and 15 mounted modular views.

---

### Milestone 1: Baseline Architecture & Documentation (Completed)
- [x] Full repository audit and bloat removal (purged abandoned `.claude/worktrees/` and `reference/`).
- [x] Stabilize UI compatibility layer (`AssistantView` properties and aliased methods).
- [x] Standardize sidebar dimensions (220px expanded, 64px collapsed).
- [x] Create core architectural documentation: `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `SECURITY_MODEL.md`, `TESTING.md`.

---

### Milestone 2: Lifecycle State Machine & Plan-Approval Gate
- [ ] Implement explicit `AssistantState` enum (`STANDBY`, `LISTENING`, `UNDERSTANDING`, `PLANNING`, `AWAITING_APPROVAL`, `EXECUTING`, `VERIFYING`, `AWAITING_EXTERNAL_ACTION`, `SLEEPING`, `RECOVERY`).
- [ ] Build Plan Review & Approval UI dialog / inline card in `AssistantView` and `HomeView`.
- [ ] Enforce the non-negotiable rule: **No execution without user approval**.
- [ ] Implement voice interrupt commands: `OMEN WAKE UP`, `OMEN SLEEP`, `OMEN STOP`, `OMEN UPDATE`.

---

### Milestone 3: Local Model Runtime & Resilient Voice Loop
- [ ] Verify local model runtime connection (Ollama: `gemma4:31b-cloud` / `mistral-nemo` / `qwen2.5-coder`).
- [ ] Implement graceful fallback when local Ollama endpoint is offline.
- [ ] Test local wake-word listener with continuous voice loop and real-time audio amplitude deformation on the particle Orb.
- [ ] Implement persistent task state recovery after restart.

---

### Milestone 4: Hybrid Computer Control with Verification Loop
- [ ] Implement closed-loop cycle: `OBSERVE → INTERPRET → PLAN ACTION → EXECUTE → OBSERVE AGAIN → VERIFY`.
- [ ] Windows UI Automation + accessibility tree inspection before falling back to mouse/keyboard coordinates.
- [ ] Visible desktop execution indicators and instant emergency halt (`Ctrl+Shift+Escape` or "OMEN STOP").
- [ ] Real-time activity feed updating step progress, active app, and verification status.

---

### Milestone 5: Personal & Institute Gmail Separation
- [ ] Official Google Gmail API OAuth 2.0 client implementation.
- [ ] Distinct profile vaults: `PERSONAL GMAIL` and `INSTITUTE GMAIL` with isolated credentials, tokens, and logs.
- [ ] Assignment notice discovery, deadline extraction, and thread summarization.
- [ ] **Strict Security Gate**: Separate explicit confirmation required before sending any draft email.

---

### Milestone 6: College Assignment Management Subsystem
- [ ] Dedicated assignment workspace structure: `College Assignments/<Subject>/<Assignment>/`.
- [ ] Sub-directories: `source_material/`, `drafts/`, `final/`, `references/`, `validation_report.md`.
- [ ] Multi-format document generation and verification: DOCX (`python-docx`), PDF (`reportlab`), PPTX (`python-pptx`), XLSX (`openpyxl`), and source code files.
- [ ] Document validation pass: Reopen and parse generated files to verify integrity and formatting before marking as ready.
- [ ] **Two-Phase Policy**: Preparation vs Submission (submission requires separate explicit command and verification of portal receipt).

---

### Milestone 7: Memory, Learning & Procedural Knowledge
- [ ] User-approved personal preferences and project context stored in SQLite.
- [ ] Procedural memory: Recording verified tool execution sequences for recurring tasks.
- [ ] Operational learning: Analyzing failure logs to propose safer tool alternatives instead of repeated failures.

---

### Milestone 8: Guarded Self-Improvement ("OMEN UPDATE")
- [ ] Automated patch proposal workflow triggered by "OMEN UPDATE".
- [ ] Worktree isolation: Execute self-improvement tests on an isolated branch.
- [ ] Multi-stage validation: Run full unit, regression, and security tests before proposing deployment.
- [ ] Rollback pipeline to automatically revert failed or unstable updates.
