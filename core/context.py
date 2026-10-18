# ============================================
"""
Context builder handles conversation history, memory retrieval, and system prompts.
"""

from typing import List, Dict, Any, Optional
from core.memory import MemoryManager
from core.models import AgentState
from app.config import config
from app.logging_config import logger


class ContextBuilder:
    """Assembles OMEN prompt context, limiting context growth and injecting relevant memory."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory_manager = memory_manager or MemoryManager()

    def build_prompt(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        system = system_prompt or self._default_system_prompt()
        prompt: List[Dict[str, str]] = [{"role": "system", "content": system}]

        # Add relevant memories (max 3)
        memories = self.memory_manager.search(user_query)
        mem_items = []
        for m in memories:
            if isinstance(m, dict):
                text = m.get("text", "")
                if text:
                    mem_items.append(text)
            elif getattr(m, "is_active", True):
                mem_items.append(f"User info: {m.key}: {m.value}")
        if mem_items:
            mem_text = "\n".join(mem_items[:3])
            prompt.append({"role": "system", "content": f"Relevant memory: {mem_text}"})

        # Add recent conversation context (limited size)
        if conversation_history:
            limit = config.context_window_size
            for msg in conversation_history[-limit:]:
                if msg.get("role") in ("user", "assistant"):
                    prompt.append({"role": msg["role"], "content": str(msg.get("content", ""))})

        # Append current query
        prompt.append({"role": "user", "content": user_query})
        return prompt

    def _default_system_prompt(self) -> str:
        return (
            "You are OMEN, the sovereign AI Operating Layer and digital workshop co-engineer for Windows, "
            "engineered in the spirit of Tony Stark's J.A.R.V.I.S.\n\n"
            "You are not a passive assistant; you are an unshakeable, sophisticated synthetic intelligence with "
            "direct authority over the OS, hardware telemetry, application lifecycles, filesystems, terminals, "
            "git version control, code patching, and screen perception.\n\n"
            "CORE DIRECTIVES:\n"
            "1. Action Over Narration: Never explain what you can execute. Call tools immediately to inspect, build, and verify.\n"
            "2. Engineering Rigor: Inspect architectures before editing, apply surgical atomic diffs, and preserve rollback safety.\n"
            "3. HUD & Visual Grounding: Visually perceive active windows and screen states to diagnose errors and drive UI actions.\n"
            "4. Calm Sophistication: Deliver concise, confident, and unflappable status updates. Never output generic AI disclaimers."
        )


