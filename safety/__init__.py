# ============================================
"""
Safety, Security, and Permission Engine for OMEN.
"""

from safety.permissions import PermissionManager, get_permission_manager
from safety.safety import SafetyEngine, sanitize_external_content, check_command_safety
from safety.confirmation import ConfirmationManager, get_confirmation_manager, ConfirmationRequest
from safety.emergency_stop import EmergencyStop, get_emergency_stop

__all__ = [
    "PermissionManager",
    "get_permission_manager",
    "SafetyEngine",
    "sanitize_external_content",
    "check_command_safety",
    "ConfirmationManager",
    "get_confirmation_manager",
    "ConfirmationRequest",
    "EmergencyStop",
    "get_emergency_stop",
]


