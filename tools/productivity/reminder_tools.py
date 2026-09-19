# ============================================
"""
Reminder tool definitions.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from productivity.reminders import get_reminder_manager
from app.constants import RiskLevel


class SetReminderArgs(BaseModel):
    title: str = Field(description="Subject or short summary of what to remind (e.g. 'Submit assignment', 'Meeting with team')")
    trigger_time: str = Field(description="When to fire reminder in natural language (e.g. 'tomorrow at 7 PM', 'in 45 minutes', 'tonight at 9 PM')")
    message: Optional[str] = Field(default="", description="Detailed reminder notification message")


class CancelReminderArgs(BaseModel):
    reminder_id: int = Field(description="Numeric ID of the reminder to cancel")


class SetReminderTool(BaseTool):
    name = "set_reminder"
    description = "Schedules a reminder alert with natural language time parsing."
    risk_level = RiskLevel.LOW
    args_schema = SetReminderArgs

    def execute(self, title: str, trigger_time: str, message: str = "", **kwargs) -> ToolResult:
        rm = get_reminder_manager()
        reminder = rm.set_reminder(title=title, trigger_time=trigger_time, message=message)
        if reminder:
            time_formatted = reminder.trigger_time.strftime("%A, %b %d at %I:%M %p")
            return ToolResult(
                success=True,
                data=reminder.model_dump(),
                message=f"Reminder scheduled: '{reminder.title}' for {time_formatted}."
            )
        return ToolResult(
            success=False,
            error=f"Could not parse time '{trigger_time}'. Please provide a valid time like 'tomorrow at 7 PM' or 'in 30 minutes'."
        )

    def verify(self, result: ToolResult, **kwargs) -> bool:
        if result.success and result.data and "id" in result.data:
            return get_reminder_manager().repo.get_by_id(result.data["id"]) is not None
        return False


class ListRemindersTool(BaseTool):
    name = "list_reminders"
    description = "Lists all upcoming active scheduled reminders."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        rm = get_reminder_manager()
        reminders = rm.list_active()
        if not reminders:
            return ToolResult(success=True, data=[], message="You have no active reminders scheduled.")

        lines = [f"#{r.id}: '{r.title}' at {r.trigger_time.strftime('%a, %b %d %I:%M %p')}" for r in reminders]
        return ToolResult(
            success=True,
            data=[r.model_dump() for r in reminders],
            message=f"Active Reminders ({len(reminders)}):\n" + "\n".join(lines)
        )


class CancelReminderTool(BaseTool):
    name = "cancel_reminder"
    description = "Cancels a scheduled reminder by ID."
    risk_level = RiskLevel.LOW
    args_schema = CancelReminderArgs

    def execute(self, reminder_id: int, **kwargs) -> ToolResult:
        rm = get_reminder_manager()
        success = rm.delete_reminder(reminder_id)
        if success:
            return ToolResult(success=True, message=f"Reminder #{reminder_id} was cancelled.")
        return ToolResult(success=False, error=f"Reminder #{reminder_id} not found.")


