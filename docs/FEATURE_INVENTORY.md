=== FEATURE INVENTORY (from reference inspection + user spec) ===

Feature: Local AI (Ollama) | Source: JARVIS/OpenJarvis | OMEN: IMPLEMENTED (core/agent, providers/llm/ollama)
Feature: Voice STT/TTS | Source: JARVIS/Alice/Marven | OMEN: PARTIAL (pyttsx3, SpeechRecognition available; VAD/wake not complete)
Feature: Windows App Control | Source: JARVIS | OMEN: PARTIAL (open_application, automation/windows)
Feature: Screen Awareness / Screenshot | Source: OpenGuider/Alice | OMEN: PARTIAL (observer/screenshots, vision module loaded, OCR placeholder)
Feature: Coding Agent / Editor / Terminal / Git | Source: Marven | OMEN: PARTIAL (no CodeMirror; terminal not fully implemented; git missing)
Feature: Browser Automation | Source: OpenGuider/Marven | OMEN: MISSING
Feature: Memory (conversation + facts + RAG) | Source: Alice/OpenJarvis | OMEN: PARTIAL (memory manager exists; HNSWLib/FAISS/ColBERT not implemented)
Feature: Agent Framework (multi-agent types) | Source: OpenJarvis | OMEN: PARTIAL (simple Agent; orchestrator/deep-research/monitor not complete)
Feature: Model Abstraction / Engine Router | Source: OpenJarvis | OMEN: MISSING (hardcoded to Ollama)
Feature: Plugin / Skill System | Source: OpenJarvis/Alice | OMEN: MISSING
Feature: Scheduling / Automations / Morning Digest | Source: JARVIS/Alice/OpenJarvis | OMEN: PARTIAL (scheduler/jobs exists; morning briefing partial)
Feature: Permissions / Confirmation / Sandbox | Source: JARVIS/Alice | OMEN: IMPLEMENTED (safety/permissions, confirmation)
Feature: System Tray / Startup / Packager | Source: JARVIS | OMEN: MISSING
Feature: CLI / API / SDK | Source: OpenJarvis | OMEN: PARTIAL (CLI exists; API/SDK missing)
Feature: RAG / Document Indexing | Source: Alice/OpenJarvis | OMEN: MISSING (chroma available but not wired fully)
Feature: Hardware Awareness / Energy Tracking | Source: OpenJarvis | OMEN: MISSING
Feature: EventBus / Tracing / Observability | Source: OpenJarvis | OMEN: PARTIAL (events exist; tracing not complete)
Feature: Settings / Configuration / Migration | Source: all | OMEN: IMPLEMENTED
Feature: Tests / Security Audit / Performance Audit | Source: all | OMEN: PARTIAL
