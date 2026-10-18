# OMEN Arena Task — Complete Repository Inspection Protocol

Perform the COMPLETE inspection protocol from /arena (32 agents, 5 rounds) for the OMEN project at E:\OMEN.

MANDATORY STEPS (do not skip):

1. Inspect CURRENT OMEN directory fully (this worktree: E:\OMEN\.claude\worktrees\elastic-spence-36fc66). Catalog every file in app/, core/, plugins/, tools/, ui/, database/, docs/, reference/, tests/, etc.

2. Create docs/CURRENT_OMEN_AUDIT.md with: architecture, capabilities, dependencies, problems, TODOs, technical debt, migration strategy.

3. Clone/reference the 5 repositories into reference/ (JARVIS, Alice, Marven, OpenGuider, OpenJarvis) ONLY IF NOT EXISTING. Check git remotes/commits first. Record in docs/REFERENCE_COMMITS.md.

4. Perform LICENSE AUDIT (docs/LICENSE_AUDIT.md) for all 5 repos before any reuse.

5. Build complete inspection ledgers for each repo (docs/reference-analysis/01-05.md). For each file: repository, file, category, inspected, relevant_features, dependencies, implementation_notes.

6. Extract FEATURE INVENTORY (docs/FEATURE_INVENTORY.md) — every capability from all 5 repos.

7. Create FEATURE_MATRIX.md comparing all 5 + OMEN.

8. Design OMEN_ARCHITECTURE.md synthesizing the five.

9. Implement model abstraction, agent framework, tool registry, memory, RAG, voice, vision, screen, coding agent, terminal, git, browser, events, registries.

10. Build all sub-architectures (intelligence, engines, agents, tools, memory, learning, events, security, plugins, skills, scheduler, observability, config).

11. Implement CLI (omen commands), API (OpenAI-compatible), UI (premium dark desktop), system tray, mini mode, command palette, diagnostics (omen doctor), monitoring.

12. Run the 3 MANDATORY END-TO-END TESTS:
    - "OMEN, open VS Code." (intent → tool → permission → launch → verify → trace)
    - "OMEN, look at my screen and tell me why this program is showing this error." (screen → capture → vision → reasoning → response → trace)
    - "OMEN, inspect my project, find the bug, fix it, and run the tests." (CodeAgent → index → search → plan → modify → terminal → tests → repair → verify → git diff → trace)

13. Conduct self-audit loop: compare FEATURE_MATRIX.md against actual code. Fix PARTIAL/MISSING.

14. Security audit: filesystem, terminal, screen, mic, network, plugins, MCP, browser, secrets, permissions, sandbox.

15. Performance audit: startup, memory, CPU, GPU, UI, model latency, tool latency, DB.

16. UX audit: every screen, spacing, nav, shortcuts, loading/error/empty states, accessibility, dark mode, animations.

17. Complete documentation (README.md, ARCHITECTURE.md, SECURITY.md, DEVELOPMENT.md, CONFIGURATION.md, MODELS.md, ENGINES.md, AGENTS.md, TOOLS.md, MEMORY.md, RAG.md, VOICE.md, VISION.md, CODING.md, BROWSER.md, PLUGINS.md, MCP.md, SKILLS.md, LEARNING.md, TROUBLESHOOTING.md, LICENSING.md).

18. Windows packaging, installer, system tray, startup, updates.

19. Write docs/FINAL_IMPLEMENTATION_REPORT.md and docs/FEATURE_GAP_REPORT.md.

CONSTRAINTS FROM PROMPT:
- Do NOT fake functionality. Every feature works or clearly shows unavailable.
- Do NOT skip inspection. Complete ledger required.
- Do NOT claim "fully analyzed" without ledger.
- If blocked by missing credentials/service/hardware/license/dependency: document in docs/IMPLEMENTATION_BLOCKERS.md, continue with rest.
- Preserve existing useful work; don't destroy.
- Feature parity REQUIRED from all 5 refs; do not limit to obvious list.
- Superiority where feasible (architecture, integration, reliability, security, routing, recovery, UX, observability, extensibility).
- Never hard-code around one model; support local/cloud/custom endpoints (Ollama, OpenAI, Anthropic, Google, NVIDIA, OpenRouter).
- All destructive actions require permission; high-risk requires explicit confirmation.
- Use SQLite database with migrations; tables for conversations/messages/memories/documents/projects/tasks/notes/automations/agents/models/engines/plugins/skills/permissions/tool_runs/traces/settings.
- EventBus with events: INFERENCE_START/END, AGENT_START/END, TOOL_START/END, MEMORY_STORE/RETRIEVE, SCREEN_CAPTURE_START/END, SCHEDULE_START/END, PLUGIN_START/STOP, SECURITY_BLOCK, USER_CONFIRMATION_REQUIRED, TASK_COMPLETE, ERROR.
- Registries: Model, Engine, Agent, Tool, Memory, Plugin, Skill, Channel, Router.
- Sandbox support (Docker/Podman/isolated process/temp workspace/resource limits).
- Testing: unit, integration, agent, tool, security, memory, routing, UI, end-to-end (success, failure, timeout, invalid, missing provider, permission denial, network failure, model failure, tool failure, partial execution, recovery).

OUTPUT FORMAT (this agent):
- Write all deliverables under docs/, reference/, and modify code only where required.
- After each wave, report progress concisely: "Round X done: Y of 32."
- At end, return: winning solution (full), why it won (attacks survived), rounds, final check scores if baseline exists, where record lives.

Start by writing the task file (.arena/task.md), init, then drive with ARENA next.