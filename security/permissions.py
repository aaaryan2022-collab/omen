"""Security permissions module compatibility layer."""
from safety.permissions import PermissionManager, get_permission_manager

security_confirm_high_risk = True
__all__ = ["PermissionManager", "get_permission_manager", "security_confirm_high_risk"]

