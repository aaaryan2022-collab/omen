# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Task Planner converts Brain LLM tool calls into structured multi-step TaskPlans.
"""

from typing import List, Dict, Any, Optional
from core.models import TaskPlan, PlanStep, AgentState
from tools.registry import get_tool_registry
from app.logging_config import logger


class Planner:
    """
    Converts LLM responses (tool requests) into an ordered TaskPlan with verification.
    """

    def __init__(self):
        self.tool_registry = get_tool_registry()

    def plan(self, llm_response_text: str, original_query: str) -> TaskPlan:
        """Builds a TaskPlan from LLM response or simple request."""
        plan = TaskPlan(objective=original_query, original_request=original_query)
        plan.id = f"plan_{hash(original_query) % (10 ** 8)}"

        # Determine intended tools from natural language cues if LLM didn't produce structured calls
        implied_tools = self._infer_tools(original_query)
        order = 0
        for tool_name in implied_tools:
            step = PlanStep(
                id=f"step_{order}",
                objective=f"Execute {tool_name} based on request",
                tool=tool_name,
                arguments={},
                risk_level=self._estimate_risk(tool_name),
                requires_confirmation=self._needs_confirmation(tool_name),
                order=order,
                status="PENDING",
            )
            plan.steps.append(step)
            order += 1

        if not plan.steps:
            # Single conversational step
            plan.steps.append(PlanStep(
                id="step_0",
                objective="Respond conversationally to user query",
                tool="respond",
                arguments={"text": original_query},
                risk_level="LOW",
                requires_confirmation=False,
                order=0,
                status="PENDING",
            ))

        return plan

    def plan_from_tool_calls(self, tool_calls: List[Dict[str, Any]], original_query: str) -> TaskPlan:
        """Builds a plan from structured tool calls returned by LLM."""
        plan = TaskPlan(objective=original_query, original_request=original_query)
        plan.id = f"plan_{hash(original_query) % (10 ** 8)}"
        order = 0
        for tc in tool_calls:
            tool_name = tc.get("name", tc.get("tool", "unknown"))
            args = tc.get("arguments", tc.get("args", {}))
            step = PlanStep(
                id=f"step_{order}",
                objective=f"Execute {tool_name}",
                tool=tool_name,
                arguments=args,
                risk_level=self._estimate_risk(tool_name),
                requires_confirmation=self._needs_confirmation(tool_name),
                order=order,
                status="PENDING",
            )
            plan.steps.append(step)
            order += 1
        return plan

    def _infer_tools(self, query: str) -> List[str]:
        q_lower = query.lower()
        tools = []
        if any(w in q_lower for w in ["open ", "launch ", "start ", "run "]):
            tools.append("open_application")
        if any(w in q_lower for w in ["remind ", "reminder ", "remember "]):
            tools.append("set_reminder")
        if any(w in q_lower for w in ["task ", "todo ", "assignment ", "deadline "]):
            tools.append("add_task")
        if any(w in q_lower for w in ["search ", "find "]):
            tools.append("search_files")
        if any(w in q_lower for w in ["read ", "open file", "summary "]):
            tools.append("read_file")
        if any(w in q_lower for w in ["news", "headlines", "briefing"]):
            tools.append("get_morning_briefing")
        if any(w in q_lower for w in ["email", "mail"]):
            tools.append("get_inbox")
        if any(w in q_lower for w in ["cpu", "ram", "memory usage", "battery"]):
            tools.append("get_system_info")
        if any(w in q_lower for w in ["pomodoro", "focus", "timer"]):
            tools.append("start_pomodoro")
        if not tools:
            tools = ["respond"]
        return tools

    def _estimate_risk(self, tool_name: str) -> str:
        tool = self.tool_registry.get(tool_name)
        if tool:
            return tool.risk_level.value if hasattr(tool.risk_level, "value") else str(tool.risk_level)
        return "LOW"

    def _needs_confirmation(self, tool_name: str) -> bool:
        tool = self.tool_registry.get(tool_name)
        if tool:
            return tool.risk_level.value == "HIGH" if hasattr(tool.risk_level, "value") else False
        return False


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
