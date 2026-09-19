# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Brain module: LLM orchestrator, parses tool calls from natural language requests.
"""

import json
from typing import Dict, Any, List, Optional, Tuple, Union
from providers.llm.base import LLMProvider, LLMResponse, ToolCallRequest
from providers.llm.ollama import OllamaProvider
from providers.llm.cloud import MockLLMProvider
from tools.registry import get_tool_registry
from app.config import config
from app.logging_config import logger


class Brain:
    """
    OMEN's reasoning center. Converts natural language into tool requests via LLM.
    """

    def __init__(self, llm: Optional[LLMProvider] = None, tools: Optional[List] = None):
        self.llm = llm or self._create_llm()
        self.tool_definitions = self._build_tool_schemas(tools)

    def _create_llm(self) -> LLMProvider:
        if config.mock_mode:
            return MockLLMProvider()
        return OllamaProvider()

    def _build_tool_schemas(self, tools=None) -> List[Dict[str, Any]]:
        if tools is None:
            return get_tool_registry().get_ollama_tools()
        return tools

    def process(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """Processes a user query through the LLM and returns the response."""
        messages = self._build_messages(user_query, conversation_history, system_prompt)

        if config.mock_mode:
            return self.llm.chat(messages, tools=self.tool_definitions)

        return self.llm.chat(
            messages=messages,
            tools=self.tool_definitions,
            temperature=config.ollama_temperature,
        )

    def stream_process(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ):
        """Yields streaming text chunks from the LLM."""
        messages = self._build_messages(user_query, conversation_history, system_prompt)
        if config.mock_mode:
            yield self.llm.chat(messages, tools=self.tool_definitions).content
            return

        yield from self.llm.stream_chat(
            messages=messages,
            tools=self.tool_definitions,
            temperature=config.ollama_temperature,
        )

    def _build_messages(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]],
        system_prompt: Optional[str],
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg.get("role") in ("user", "assistant"):
                    messages.append(msg)
        messages.append({"role": "user", "content": user_query})
        return messages


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
