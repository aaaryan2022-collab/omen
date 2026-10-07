# ============================================
"""AIProvider / ModelRouter conceptual interfaces — OMEN spec §4, §5.

Defines the abstraction layer between the agent engine (core/agent_engine.py,
spec §6) and concrete LLM backends (providers/llm/ollama.py, spec §5).

Dependency note: requests is installed (v2.34.2) in this environment; if
unavailable the interface remains clean and the concrete provider notes it.

Co-Authored-By: Claude Code <noreply@anthropic.com>
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator, Union
from pydantic import BaseModel, Field
from enum import Enum


class ProviderType(str, Enum):
    """Spec §4: provider classification."""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class AIProvider(ABC):
    """Spec §4 conceptual interface — any model backend (Ollama, cloud, etc.)."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Synchronous generation — spec §4, §5."""
        ...

    @abstractmethod
    def stream(self, prompt: str, **kwargs: Any) -> Iterator[str]:
        """Streaming chunk yield — spec §5 streaming requirement."""
        ...

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Spec §4: local vs cloud classification."""
        ...

    @abstractmethod
    def check_health(self) -> bool:
        """Spec §5: connectivity check (see ollama.py check_connection)."""
        ...


class ModelRouter(ABC):
    """Spec §4: selects / routes among AIProvider instances."""

    @abstractmethod
    def route(self, request: Dict[str, Any]) -> AIProvider:
        """Return the provider best suited for request — spec §4 routing."""
        ...

    @abstractmethod
    def list_providers(self) -> List[str]:
        """Registered provider names — spec §4 registry."""
        ...


class ProviderConfig(BaseModel):
    """Spec §4: per-provider runtime settings."""
    base_url: str = Field(default="http://localhost:11434")
    model: str = Field(default="llama3:8b-instruct-q4_K_M")
    timeout: int = Field(default=60, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    provider_type: ProviderType = Field(default=ProviderType.LOCAL)


# Real import paths verified: providers.llm.base.LLMProvider exists.
# This abstraction complements it without replacing it.
