# ============================================
"""
System monitoring and hardware telemetry tools using psutil.
"""

from typing import Dict, Any, List, Optional
import psutil
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.hardware import get_hardware_profile


class GetSystemInfoTool(BaseTool):
    name = "get_system_info"
    description = "Retrieves an overview of CPU, RAM, Disk, and Battery usage."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            import os
            root_drive = os.path.splitdrive(os.path.abspath("."))[0] + "\\" if os.name == "nt" else "/"
            disk = psutil.disk_usage(root_drive)
            battery = psutil.sensors_battery()

            info = {
                "cpu_percent": cpu_percent,
                "memory_total_gb": round(mem.total / (1024**3), 2),
                "memory_used_gb": round(mem.used / (1024**3), 2),
                "memory_percent": mem.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent,
                "battery_percent": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
            }
            summary = (
                f"CPU: {cpu_percent}% | RAM: {mem.percent}% ({info['memory_used_gb']}/{info['memory_total_gb']} GB) | "
                f"Disk: {disk.percent}% used | Battery: {info['battery_percent']}%"
            )
            return ToolResult(success=True, data=info, message=summary)
        except Exception as e:
            return ToolResult(success=False, error=str(e), message="Failed to retrieve system information")


class GetHardwareProfileTool(BaseTool):
    name = "get_hardware_profile"
    description = "Reports the host CPU, RAM, NVIDIA GPU, VRAM, and OMEN resource policy."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        profile = get_hardware_profile()
        data = {
            "cpu_threads": profile.cpu_threads,
            "ram_gb": profile.ram_gb,
            "gpu_name": profile.gpu_name,
            "gpu_vram_mb": profile.gpu_vram_mb,
            "gpu_vram_used_mb": profile.gpu_vram_used_mb,
            "driver_version": profile.driver_version,
            "recommended_context_tokens": profile.recommended_context_tokens,
            "recommended_output_tokens": profile.recommended_output_tokens,
        }
        gpu = profile.gpu_name or "CPU-only fallback"
        return ToolResult(success=True, data=data, message=f"{gpu}; {profile.ram_gb} GB RAM; {profile.cpu_threads} CPU threads.")


class GetCpuUsageTool(BaseTool):
    name = "get_cpu_usage"
    description = "Gets current CPU utilization percentage across cores."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            cpu_overall = psutil.cpu_percent(interval=0.2)
            cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
            return ToolResult(
                success=True,
                data={"overall": cpu_overall, "cores": cpu_cores},
                message=f"Current CPU usage is {cpu_overall}% across {len(cpu_cores)} logical cores."
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetMemoryUsageTool(BaseTool):
    name = "get_memory_usage"
    description = "Gets detailed RAM utilization and identifies the top memory-consuming processes."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            mem = psutil.virtual_memory()
            # Top 5 RAM processes
            processes = []
            for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(p.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            top_procs = sorted(processes, key=lambda x: x.get('memory_percent') or 0, reverse=True)[:5]

            data = {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
                "top_processes": top_procs
            }
            top_names = ", ".join([f"{p['name']} ({round(p['memory_percent'] or 0, 1)}%)" for p in top_procs])
            return ToolResult(
                success=True,
                data=data,
                message=f"RAM Usage: {mem.percent}% ({data['used_gb']}/{data['total_gb']} GB). Top consumers: {top_names}"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetDiskUsageTool(BaseTool):
    name = "get_disk_usage"
    description = "Gets hard drive storage capacity and free space."
    risk_level = RiskLevel.LOW

    def execute(self, path: str = "C:/", **kwargs) -> ToolResult:
        try:
            disk = psutil.disk_usage(path)
            data = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
            return ToolResult(
                success=True,
                data=data,
                message=f"Drive {path}: {data['free_gb']} GB free of {data['total_gb']} GB ({data['percent']}% used)."
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetBatteryStatusTool(BaseTool):
    name = "get_battery_status"
    description = "Checks battery percentage and charging state."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            battery = psutil.sensors_battery()
            if not battery:
                return ToolResult(success=True, data={"battery": None}, message="No battery detected (Desktop power).")
            data = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secs_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
            }
            status = "Plugged in (Charging)" if battery.power_plugged else "On Battery"
            return ToolResult(
                success=True,
                data=data,
                message=f"Battery is at {battery.percent}% ({status})."
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetRunningProcessesTool(BaseTool):
    name = "get_running_processes"
    description = "Lists currently running processes with PID and CPU/memory usage."
    risk_level = RiskLevel.LOW

    def execute(self, limit: int = 15, **kwargs) -> ToolResult:
        try:
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procs.append(p.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            top_procs = sorted(procs, key=lambda x: x.get('cpu_percent') or 0, reverse=True)[:limit]
            return ToolResult(success=True, data=top_procs, message=f"Retrieved {len(top_procs)} top running processes.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


