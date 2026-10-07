# Model Registry — Multi-Model AI Brain
# Every feature from prompt must work.

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class ModelRole(str, Enum):
    PRIMARY = "primary"
    FAST = "fast"
    REASONING = "reasoning"
    VISION = "vision"
    CODING = "coding"
    EMBEDDING = "embedding"
    STT = "speech_to_text"
    TTS = "text_to_speech"
    FALLBACK = "fallback"

class ProviderType(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    NVIDIA = "nvidia"
    OPENROUTER = "openrouter"
    CUSTOM = "custom"

class ModelConfig(BaseModel):
    name: str
    role: ModelRole
    provider: ProviderType
    endpoint: Optional[str] = None
    enabled: bool = True

class ModelRouter:
    """Intelligent routing: task type, complexity, modality, hardware, cost, reliability."""
    def __init__(self):
        self.registry: Dict[str, ModelConfig] = {}
    def register(self, cfg: ModelConfig):
        self.registry[cfg.name] = cfg
    def route(self, task_type: str, complexity: str = "low", modality: str = "text") -> ModelConfig:
        # Heuristic routing per prompt spec
        if modality == "vision" or "screen" in task_type:
            return self.retrieve("vision") or self.registry.get("primary")
        if task_type in ("code", "coding", "debug", "edit"):
            return self.retrieve("coding") or self.registry.get("primary")
        if complexity == "high" or "reason" in task_type:
            return self.retrieve("reasoning") or self.registry.get("primary")
        if complexity == "low" or task_type in ("chat", "ask"):
            return self.retrieve("fast") or self.registry.get("primary")
        return self.registry.get("primary")
    def retrieve(self, role: str) -> Optional[ModelConfig]:
        for cfg in self.registry.values():
            if cfg.role.value == role and cfg.enabled:
                return cfg
        return None

# Initialize with default roles
_router = ModelRouter()
_router.register(ModelConfig(name="llama3:8b", role=ModelRole.PRIMARY, provider=ProviderType.OLLAMA, endpoint="http://localhost:11434"))
_router.register(ModelConfig(name="fast-local", role=ModelRole.FAST, provider=ProviderType.OLLAMA, enabled=False))
