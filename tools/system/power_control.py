# ============================================
"""
Workstation locking and system power tools.
"""

import ctypes
import os
import sys
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class LockWorkstationTool(BaseTool):
    name = "lock_workstation"
    description = "Locks the Windows workstation for security."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            if sys.platform == "win32":
                ctypes.windll.user32.LockWorkStation()
                return ToolResult(success=True, message="Workstation locked successfully.")
            return ToolResult(success=False, error="Workstation locking is only supported on Windows.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class SleepSystemTool(BaseTool):
    name = "sleep_system"
    description = "Puts the laptop into sleep mode. (Requires confirmation)"
    risk_level = RiskLevel.HIGH

    def execute(self, **kwargs) -> ToolResult:
        try:
            if sys.platform == "win32":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return ToolResult(success=True, message="System entering sleep mode.")
            return ToolResult(success=False, error="Only supported on Windows.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


