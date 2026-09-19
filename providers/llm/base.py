# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Abstract base class and models for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum


class LLMMessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ToolCallRequest:
    """Represents a tool call requested by the LLM."""
    tool_name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None


class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str
    thought: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    model: Optional[str] = None

    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def check_connection(self) -> bool:
        """Returns True if provider is reachable."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Returns list of available models."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Sends a chat message and returns the response."""
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Streams chat response content as text chunks."""
        pass


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
