# ============================================
"""
Task management tool definitions.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from productivity.tasks import get_task_manager
from app.constants import RiskLevel, TaskPriority, TaskStatus


class AddTaskArgs(BaseModel):
    title: str = Field(description="Title or summary of the task to create (e.g. 'Finish Python assignment')")
    description: str = Field(default="", description="Optional extended details or context")
    priority: str = Field(default="MEDIUM", description="Task priority: LOW, MEDIUM, HIGH, or URGENT")
    category: str = Field(default="General", description="Category: General, Work, College, Project, Personal")
    due_at: Optional[str] = Field(default=None, description="Natural language due date (e.g. 'tomorrow at 7 PM', 'Friday', 'in 2 hours')")


class ListTasksArgs(BaseModel):
    status: Optional[str] = Field(default=None, description="Filter by status: PENDING, IN_PROGRESS, COMPLETED, or leave empty for all active")


class TaskIdArgs(BaseModel):
    task_id: int = Field(description="Unique numeric ID of the task")


class SearchTasksArgs(BaseModel):
    query: str = Field(description="Search term to match against task title, description, or notes")


class AddTaskTool(BaseTool):
    name = "add_task"
    description = "Creates a new task with optional priority, category, and natural language due date."
    risk_level = RiskLevel.LOW
    args_schema = AddTaskArgs

    def execute(self, title: str, description: str = "", priority: str = "MEDIUM", category: str = "General", due_at: Optional[str] = None, **kwargs) -> ToolResult:
        tm = get_task_manager()
        task = tm.add_task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_at=due_at
        )
        due_str = f" [Due: {task.due_at.strftime('%Y-%m-%d %I:%M %p')}]" if task.due_at else ""
        return ToolResult(
            success=True,
            data=task.model_dump(),
            message=f"Added task #{task.id}: '{task.title}' (Priority: {task.priority.value}){due_str}."
        )

    def verify(self, result: ToolResult, **kwargs) -> bool:
        if result.success and result.data and "id" in result.data:
            return get_task_manager().repo.get_by_id(result.data["id"]) is not None
        return False


class ListTasksTool(BaseTool):
    name = "list_tasks"
    description = "Lists user tasks, deadlines, and their current completion status."
    risk_level = RiskLevel.LOW
    args_schema = ListTasksArgs

    def execute(self, status: Optional[str] = None, **kwargs) -> ToolResult:
        tm = get_task_manager()
        status_enum = TaskStatus(status.upper()) if status and status.upper() in TaskStatus.__members__ else None
        tasks = tm.list_tasks(status=status_enum)

        if not tasks:
            return ToolResult(success=True, data=[], message="You have no tasks matching this filter.")

        lines = []
        for t in tasks:
            status_mark = "[x]" if t.status == TaskStatus.COMPLETED else "[ ]"
            due_info = f" (Due: {t.due_at.strftime('%a, %b %d at %I:%M %p')})" if t.due_at else ""
            lines.append(f"{status_mark} #{t.id}: {t.title} [{t.priority.value}]{due_info}")

        summary = f"Found {len(tasks)} task(s):\n" + "\n".join(lines)
        return ToolResult(
            success=True,
            data=[t.model_dump() for t in tasks],
            message=summary
        )


class CompleteTaskTool(BaseTool):
    name = "complete_task"
    description = "Marks an existing task as COMPLETED."
    risk_level = RiskLevel.LOW
    args_schema = TaskIdArgs

    def execute(self, task_id: int, **kwargs) -> ToolResult:
        tm = get_task_manager()
        success = tm.complete_task(task_id)
        if success:
            return ToolResult(success=True, message=f"Task #{task_id} marked as completed.")
        return ToolResult(success=False, error=f"Task #{task_id} not found.")


class DeleteTaskTool(BaseTool):
    name = "delete_task"
    description = "Deletes a task from the system."
    risk_level = RiskLevel.MEDIUM
    args_schema = TaskIdArgs

    def execute(self, task_id: int, **kwargs) -> ToolResult:
        tm = get_task_manager()
        success = tm.delete_task(task_id)
        if success:
            return ToolResult(success=True, message=f"Task #{task_id} deleted successfully.")
        return ToolResult(success=False, error=f"Task #{task_id} not found.")


class SearchTasksTool(BaseTool):
    name = "search_tasks"
    description = "Searches for tasks by keyword or phrase."
    risk_level = RiskLevel.LOW
    args_schema = SearchTasksArgs

    def execute(self, query: str, **kwargs) -> ToolResult:
        tm = get_task_manager()
        matches = tm.search_tasks(query)
        if matches:
            lines = [f"#{t.id}: {t.title} ({t.status.value})" for t in matches]
            return ToolResult(success=True, data=[t.model_dump() for t in matches], message="Matches:\n" + "\n".join(lines))
        return ToolResult(success=True, data=[], message=f"No tasks found matching '{query}'.")


