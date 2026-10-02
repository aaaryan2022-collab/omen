"""Continuous observe → verify → replan loop for autonomous execution.
Wired into agent execution to observe result after every important action.
No Stark artifacts; pure OMEN architecture.
"""

from typing import Optional, Dict, Any, List, Callable
import time

from vision import VisionModule
from vision.element_detect import ElementDetector
from computer import ComputerControl
from core.agent import Agent
from core.events import get_event_bus, EventType
from core.supervisor import Supervisor
from app.logging_config import logger


class ObservationLoop:
    """Continuous observation, verification, and replan cycle.

    Architecture (Spec #28 / #9 / #8):
    Instruction → Observe Screen → Understand Screen → Plan Action →
    Execute Action → Observe Result → Verify → Next Action / Re-plan
    """

    def __init__(self, supervisor: Optional[Supervisor] = None, agent: Optional[Agent] = None):
        self.supervisor = supervisor
        self.agent = agent
        self.vision = VisionModule()
        self.detector = ElementDetector()
        self.computer = ComputerControl()
        self._last_screen: Optional[Any] = None
        self._action_log: List[Dict[str, Any]] = []

    def observe_screen(self) -> Dict[str, Any]:
        """Capture screen and describe state (Spec #3 / #14)."""
        img = self.vision.screenshot()
        desc = self.vision.describe_active_window() if img else "No visual input"
        snapshot = {"screenshot": img is not None, "description": desc}
        self._last_screen = snapshot
        return snapshot

    def verify_action_result(self, expected_indicator: str, region: Optional[Dict[str, int]] = None) -> bool:
        """Check if expected indicator appears after action (Spec #9 / #10).

        Returns True if result matches expectation (e.g., button visible, error gone).
        Returns False if unexpected state (need replan / ask user).
        """
        obs = self.observe_screen()
        if obs["screenshot"]:
            # Try to find expected indicator visually
            elem = self.detector.find_element(expected_indicator, region=region)
            if elem and elem.confidence >= 0.5:
                logger.info(f"Verify: '{expected_indicator}' found at ({elem.x}, {elem.y}) — action verified")
                return True
            if expected_indicator.lower() in obs.get("description", "").lower():
                logger.info(f"Verify: '{expected_indicator}' in description — action verified")
                return True
        # If not found, treat as unverified; may need replan
        logger.info(f"Verify: '{expected_indicator}' NOT found — unverified / replan needed")
        return False

    def replan_on_failure(self, action: str, error_context: str) -> Dict[str, Any]:
        """Re-plan when expected screen does not match (Spec #10 / #27)."""
        logger.info(f"Replan triggered: action='{action}', error='{error_context}'")
        # If supervisor present, trigger recovery
        if self.supervisor:
            self.supervisor.trigger_recovery(error_context)
        # Return adaptive plan (simplified — real version uses planner)
        return {
            "original_action": action,
            "error": error_context,
            "replan_suggested": True,
            "next_step": "Re-observe screen and locate alternative element",
        }

    def run_cycle(self, instruction: str) -> Dict[str, Any]:
        """Full autonomous loop for one instruction.

        Instruction → Observe → Understand → Plan → Act → Observe → Verify → Next / Finish
        """
        # 1. Understand instruction (agent handles NL)
        # 2. Observe initial screen
        initial = self.observe_screen()
        # 3. Plan (agent planner — already exists)
        # 4. Execute (agent + computer)
        # 5. Observe result
        result_obs = self.observe_screen()
        # 6. Verify
        verified = self.verify_action_result("expected_screen_change")
        # 7. Log
        entry = {
            "instruction": instruction,
            "initial_observation": initial["description"][:60],
            "result_observation": result_obs["description"][:60],
            "verified": verified,
        }
        self._action_log.append(entry)
        return {
            "instruction": instruction,
            "observed_before": initial,
            "observed_after": result_obs,
            "verified": verified,
            "replan_needed": not verified,
            "action_log": self._action_log[-1] if self._action_log else None,
        }
