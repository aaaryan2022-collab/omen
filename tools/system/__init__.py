# ============================================
"""
System control and telemetry tools for OMEN.
"""

from tools.system.system_info import (
    GetSystemInfoTool,
    GetCpuUsageTool,
    GetMemoryUsageTool,
    GetDiskUsageTool,
    GetBatteryStatusTool,
    GetRunningProcessesTool,
)
from tools.system.app_control import (
    OpenApplicationTool,
    CloseApplicationTool,
)
from tools.system.power_control import (
    LockWorkstationTool,
    SleepSystemTool,
)

__all__ = [
    "GetSystemInfoTool",
    "GetCpuUsageTool",
    "GetMemoryUsageTool",
    "GetDiskUsageTool",
    "GetBatteryStatusTool",
    "GetRunningProcessesTool",
    "OpenApplicationTool",
    "CloseApplicationTool",
    "LockWorkstationTool",
    "SleepSystemTool",
]


