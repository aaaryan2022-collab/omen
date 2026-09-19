"""
Supervisor — modular oversight layer for OMEN agent execution.
Monitors agent state, verifies step outcomes, triggers recovery.
No Stark artifacts; pure OMEN architecture.
"""

from typing import Optional, Dict, Any, List, Callable
from core.models import AgentState, TaskPlan, PlanStep
from core.agent import Agent
from core.events import get_event_bus, EventType
from app.logging_config import logger


class Supervisor:
    """Modular oversight for agent pipeline steps."""

    def __init__(self, agent: Optional[Agent] = None):
        self.agent = agent
        self._watchers: List[Callable] = []
        self._recovery_actions: Dict[str, Callable] = {}
        self._state_log: List[Dict[str, Any]] = []

    def register_watcher(self, fn: Callable[[AgentState, str], None]):
        self._watchers.append(fn)

    def observe_state_changes(self, old: AgentState, new: AgentState, context: str = ""):
        entry = {"from": old.value, "to": new.value, "context": context}
        self._state_log.append(entry)
        for w in self._watchers:
            try:
                w(old, new, context)
            except Exception as e:
                logger.debug(f"Watcher error: {e}")

    def verify_step_result(self, step: PlanStep, result: Dict[str, Any]) -> bool:
        return result.get("success", False) and (step.status.value == "COMPLETED")

    def trigger_recovery(self, error_context: str) -> bool:
        logger.info(f"Supervisor recovery triggered: {error_context}")
        return True

    def get_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._state_log[-limit:]
