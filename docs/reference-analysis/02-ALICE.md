# ALICE — REFERENCE ANALYSIS

Repo: reference/Alice/
License: MIT (confirmed)
Status: Cloned 2026-10-07

## 1. Purpose
Desktop AI companion — voice interaction, context awareness, tooling, emotional engagement.

## 2. Architecture
Python backend with UI; local + cloud model support. Modular provider system.

## 3. Technology Stack
Python, OpenAI-compatible APIs, Ollama, Whisper, Piper TTS, embeddings.

## 4. Core Modules
- Voice (STT/TTS/VAD/interruptible speech)
- Memory & context awareness
- Tool integration
- Provider abstraction (cloud + local)
- Personality / emotional engagement layer

## 5. AI/Model
Multiple provider support; primary is OpenAI/Codex; fallback to Ollama/LM Studio.

## 6. Memory
Persistent context, embedding-based retrieval.

## 7. Voice
VAD-powered STT (Whisper), streaming TTS (OpenAI/Google/Piper), interruptible.

## 8. Tools
Tool calling with external integrations.

## 9. Licensing
MIT — reuse permitted with attribution preserved.

## 10. Features Worth Adopting
Provider abstraction (local/cloud), interruptible speech, multiple STT/TTS backends, emotional/personality layer, VAD.

## 11. Not to Copy
Direct OpenAI dependency (OMEN prefers local-first); proprietary personality code.
