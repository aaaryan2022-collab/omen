# JARVIS — REFERENCE ANALYSIS

Repo: reference/JARVIS/
License: Verify (no root LICENSE; check backend/ headers)
Branch: main
Status: Cloned 2026-10-07

## 1. Purpose
Futuristic desktop AI assistant for Windows. Electron + React frontend, Python FastAPI backend.

## 2. Architecture
Split: frontend/ (UI) and backend/ (API/intelligence) with shared/ module.
Intentional module boundaries: AI, voice, computer control, memory, settings, security.

## 3. Technology Stack
- Electron + React + TypeScript (frontend)
- Python + FastAPI (backend)
- Local Ollama (AI manager)
- Voice, computer control, memory, settings, security modules

## 4. Directory Structure
ARCHITECTURE.md, README.md, backend/, frontend/, shared/, Start JARVIS.bat, package.json

## 5. Core Modules
AI manager (Ollama + tool use), voice (STT/TTS), computer control, memory, settings, security

## 6. AI/Model Architecture
Local model via Ollama, tool-calling enabled. No hardcoded cloud API.

## 7. Agent Architecture
AI manager acts as central agent with tool registry.

## 8. Tool Architecture
Backend exposes tool endpoints; frontend calls via API.

## 9. Memory
Persistent memory module (study reference)

## 10. Voice
STT + TTS via backend services

## 11. Vision/Screen
Computer control includes screen awareness

## 12. Coding
Not primary feature (study only)

## 13. Browser
Not primary

## 14. Plugin
Modular design suggests plugin capability

## 15. MCP
Not explicitly shown

## 16. Scheduling
Not primary

## 17. Automation
Computer automation via backend

## 18. Security
Dedicated security module with settings

## 19. Permissions
Settings-controlled

## 20. Database
Not explicitly shown; likely SQLite or file-based

## 21. Configuration
Config settings module

## 22. CLI
Not primary (GUI-focused)

## 23. API
FastAPI backend serves REST API

## 24. UI
Premium Electron/React with dark theme, minimal clutter

## 25. Telemetry
Not shown

## 26. Testing
Not shown in root

## 27. Deployment
Batch scripts (Start JARVIS.bat)

## 28. Strengths
Clean split architecture; local-first design; modular boundaries

## 29. Weaknesses
Requires Electron + Python both running; larger footprint

## 30. Features Worth Adopting
Module split (frontend/backend), security module, settings architecture, AI manager concept

## 31. Architectural Patterns
Independent modules with clear interfaces; shared module for contracts

## 32. Features NOT to Copy
Electron dependency (OMEN uses PySide6); full duplicate architecture

## 33. Licensing Concerns
Verify license file; do not reuse code without confirmation.
