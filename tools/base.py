# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Base classes for all OMEN Tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from app.constants import RiskLevel


class ToolResult(BaseModel):
    """Result returned from a tool execution."""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None

    def to_summary(self) -> str:
        if self.success:
            return self.message or f"Operation succeeded: {self.data}"
        return f"Failed: {self.error or self.message}"


class BaseTool(ABC):
    """Abstract base class for all executable tools in OMEN."""

    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    permission_tag: str = "general"
    args_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Executes the tool with validated arguments."""
        pass

    def validate_args(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming arguments against args_schema if provided."""
        if self.args_schema:
            validated = self.args_schema(**kwargs)
            return validated.model_dump()
        return kwargs

    def verify(self, result: ToolResult, **kwargs) -> bool:
        """Optional post-execution verification check."""
        return result.success

    def to_ollama_schema(self) -> Dict[str, Any]:
        """Generates Ollama/OpenAI-compatible tool definition schema."""
        properties: Dict[str, Any] = {}
        required = []

        if self.args_schema:
            schema = self.args_schema.model_json_schema()
            properties = schema.get("properties", {})
            required = schema.get("required", [])

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


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
