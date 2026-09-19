# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Core internal domain models for OMEN agent system.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class AgentState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


class PlanStep(BaseModel):
    """Individual step in a task plan."""
    id: str
    objective: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"
    requires_confirmation: bool = False
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    order: int = 0

    def to_summary(self) -> str:
        return f"Step {self.order}: {self.objective} [{self.status.value}]"


class TaskPlan(BaseModel):
    """Structured plan produced by the Planner for a multi-step task."""
    id: Optional[str] = None
    objective: str
    original_request: str = ""
    steps: List[PlanStep] = Field(default_factory=list)
    status: str = "PLANNED"
    created_at: datetime = Field(default_factory=datetime.now)


class AgentThought(BaseModel):
    """High-level internal reasoning state (shown in UI only as status)."""
    state: AgentState = AgentState.THINKING
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class ToolCallRequest(BaseModel):
    """Structured tool call produced by LLM."""
    tool_name: str
    arguments: Dict[str, Any]
    risk_level: str = "LOW"
    requires_confirmation: bool = False


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
