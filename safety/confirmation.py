# ============================================
"""
Human-in-the-loop Confirmation Manager for High-Risk Actions.
"""

from typing import Callable, Optional, Dict, Any
from pydantic import BaseModel, Field
import threading
from app.constants import RiskLevel
from app.logging_config import logger


class ConfirmationRequest(BaseModel):
    """Details of a tool execution requiring user confirmation."""
    tool_name: str
    arguments: Dict[str, Any]
    risk_level: RiskLevel
    description: str


class ConfirmationManager:
    """Dispatches confirmation requests to registered UI handlers or console."""

    def __init__(self):
        self._handler: Optional[Callable[[ConfirmationRequest], bool]] = None
        self._lock = threading.Lock()

    def set_handler(self, handler: Callable[[ConfirmationRequest], bool]):
        """Registers a UI or CLI confirmation callback."""
        with self._lock:
            self._handler = handler

    def request_confirmation(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        risk_level: RiskLevel,
        description: Optional[str] = None
    ) -> bool:
        """
        Prompts the user for confirmation.
        Returns True if approved, False if denied.
        """
        desc = description or f"Execute tool '{tool_name}' with arguments: {arguments}"
        req = ConfirmationRequest(
            tool_name=tool_name,
            arguments=arguments,
            risk_level=risk_level,
            description=desc,
        )

        with self._lock:
            handler = self._handler

        if handler:
            try:
                approved = handler(req)
                logger.info(f"User confirmation for {tool_name}: {'APPROVED' if approved else 'REJECTED'}")
                return approved
            except Exception as e:
                logger.error(f"Error in confirmation handler: {e}")
                return False

        # CLI fallback if no GUI handler is set
        print(f"\n[SECURITY CONFIRMATION REQUIRED]")
        print(f"Action: {tool_name}")
        print(f"Risk Level: {risk_level.value}")
        print(f"Details: {desc}")
        response = input("Do you authorize this action? (yes/no): ").strip().lower()
        return response in ("y", "yes", "authorized", "confirm")


_confirmation_manager: Optional[ConfirmationManager] = None


def get_confirmation_manager() -> ConfirmationManager:
    global _confirmation_manager
    if _confirmation_manager is None:
        _confirmation_manager = ConfirmationManager()
    return _confirmation_manager


