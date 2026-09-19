# ============================================
"""
Pomodoro focus session tool definitions.
"""

from typing import Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from productivity.pomodoro import get_pomodoro_timer
from app.constants import RiskLevel


class StartPomodoroArgs(BaseModel):
    duration_minutes: Optional[int] = Field(default=25, description="Focus session duration in minutes (default 25)")
    tag: str = Field(default="Focus", description="Session label or subject (e.g. 'Coding', 'DSA', 'Writing')")


class StartPomodoroTool(BaseTool):
    name = "start_pomodoro"
    description = "Starts a background Pomodoro focus session."
    risk_level = RiskLevel.LOW
    args_schema = StartPomodoroArgs

    def execute(self, duration_minutes: Optional[int] = 25, tag: str = "Focus", **kwargs) -> ToolResult:
        pomo = get_pomodoro_timer()
        pomo.start(duration_minutes=duration_minutes, tag=tag)
        return ToolResult(
            success=True,
            data={"duration_minutes": duration_minutes, "tag": tag},
            message=f"Started a {duration_minutes}-minute Pomodoro focus session for '{tag}'. Good luck!"
        )


class PausePomodoroTool(BaseTool):
    name = "pause_pomodoro"
    description = "Pauses the currently running Pomodoro session."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        pomo = get_pomodoro_timer()
        pomo.pause()
        return ToolResult(success=True, message="Pomodoro session paused.")


class ResumePomodoroTool(BaseTool):
    name = "resume_pomodoro"
    description = "Resumes a paused Pomodoro session."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        pomo = get_pomodoro_timer()
        pomo.resume()
        return ToolResult(success=True, message="Pomodoro session resumed.")


class StopPomodoroTool(BaseTool):
    name = "stop_pomodoro"
    description = "Stops and resets the active Pomodoro focus timer."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        pomo = get_pomodoro_timer()
        pomo.stop()
        return ToolResult(success=True, message="Pomodoro timer stopped and reset.")


class GetPomodoroStatusTool(BaseTool):
    name = "get_pomodoro_status"
    description = "Checks the time remaining and state of the active Pomodoro timer."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        pomo = get_pomodoro_timer()
        status = pomo.get_status()
        return ToolResult(
            success=True,
            data=status,
            message=f"Pomodoro [{status['state']}]: {status['time_remaining_formatted']} remaining for '{status['tag']}'."
        )


