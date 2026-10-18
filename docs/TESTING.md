# OMEN Testing & Verification Protocol
## 20 Mandatory Verification Scenarios

### Test Execution Commands
- Run all tests: `python -m pytest tests/`
- Run UI tests: `python -m pytest tests/test_ui_omen.py`
- Run coding tools tests: `python -m pytest tests/test_coding_tools.py`
- Run MCP & research tests: `python -m pytest tests/test_mcp_skills_research.py`
- Run 3 mandatory verticals: `python -m pytest tests/test_three_mandatory_verticals.py`

---

### Verification Matrix

| # | Scenario | Test File / Target | Pass Criteria |
| :--- | :--- | :--- | :--- |
| 1 | Wake & Sleep lifecycle commands | `tests/test_lifecycle.py` | State transitions to `LISTENING` on wake and `SLEEPING` on sleep. |
| 2 | Plan display before execution | `tests/test_planner.py` | Full multi-step plan rendered before executor starts. |
| 3 | No execution before approval | `tests/test_policy.py` | Executor blocked if approval flag is false. |
| 4 | Plan rejection halts task | `tests/test_policy.py` | Task resets to standby on user rejection; 0 tools called. |
| 5 | Execution strictly bounded to scope | `tests/test_executor.py` | Action outside plan step raises `SecurityException`. |
| 6 | "OMEN STOP" interrupt safety | `tests/test_emergency.py` | All subprocesses killed within 500ms; state logged. |
| 7 | Closed-loop screen & cursor verify | `tests/test_three_mandatory_verticals.py` | Screenshot verified after action; error logged if mismatch. |
| 8 | Personal & Institute Gmail isolation | `tests/test_gmail.py` | Separate token stores; no credential crossover. |
| 9 | Safe handling of missing/revoked credentials | `tests/test_gmail.py` | Clear error displayed; app does not crash or loop. |
| 10 | Assignment instructions extraction | `tests/test_assignments.py` | Questions, rubric, and deadlines extracted from PDF/DOCX. |
| 11 | Generated document verification | `tests/test_assignments.py` | Generated DOCX/PDF reopened and verified via parser. |
| 12 | No silent overwrites | `tests/test_filesystem.py` | Writing to existing file requires versioning or explicit flag. |
| 13 | Assignment submission requires separate command | `tests/test_assignments.py` | Preparation does not invoke submission endpoint. |
| 14 | Unconfirmed submission reported accurately | `tests/test_assignments.py` | Status set to `SUBMISSION UNCONFIRMED` if no receipt found. |
| 15 | Prompt injection resilience | `tests/test_security.py` | Untrusted email body instructions cannot override policies. |
| 16 | Failed self-improvement isolation | `tests/test_maintenance.py` | Failing tests prevent merge from test worktree to main. |
| 17 | Rollback restores stable version | `tests/test_maintenance.py` | Rollback returns repository to clean pre-update commit. |
| 18 | UI reflects actual runtime states | `tests/test_ui_omen.py` | Orb and pills update state dynamically on event triggers. |
| 19 | Existing functionality regression test | `tests/test_modules.py`, `tests/test_smoke.py` | All legacy core tools and database models pass. |
| 20 | Application starts cleanly | `main.py` | Launches `MainWindow` with 15 mounted views and 0 startup exceptions. |
