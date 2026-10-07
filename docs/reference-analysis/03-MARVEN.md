# MARVEN — REFERENCE ANALYSIS

Repo: reference/Marven/
License: AGPL v3 (confirmed from LICENSE)
Status: Cloned 2026-10-07

## Key Features (from README)
- Desktop AI assistant + full-featured code editor (CodeMirror 6)
- Multi-provider AI chat (Groq, OpenAI, Anthropic, OpenRouter, NIM, Ollama)
- Coding agent with file awareness, terminal, global search, git tools
- Local-first (files, settings, memory stay on machine)
- Privacy: localStorage + JSON settings, encrypted API keys
- Voice support (optional)

## Licensing Warning
AGPL v3 — copyleft + network interaction clause. Any code derived from Marven must be released under AGPL and source made available to users interacting over network. Do NOT copy Marven source into OMEN.

## Features Worth Studying (independent implementation)
- CodeMirror 6 editor integration
- Multi-provider abstraction (Groq/OpenAI/Anthropic/OpenRouter/NIM/Ollama)
- File-aware coding agent
- Secure key storage (OS-backed encryption)
- Global search + git integration
- Terminal integration
- Local semantic index (.gitignore-respecting)

## Not to Copy
- AGPL-licensed code
- Direct CodeMirror 6 integration (OMEN uses PySide6, not web editor)
