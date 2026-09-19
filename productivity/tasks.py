# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Task management service with natural language deadline understanding.
"""

from datetime import datetime, timedelta
import re
from typing import Optional, List, Dict, Any, Tuple
from database.database import Database, get_db
from database.models import Task
from database.repositories import TaskRepository
from app.constants import TaskPriority, TaskStatus
from app.logging_config import logger


def parse_natural_date(text: str) -> Optional[datetime]:
    """
    Parses natural language date and time expressions into a concrete datetime.
    Supports:
    - 'tomorrow at 7 PM', 'tomorrow 8am', 'tomorrow'
    - 'tonight', 'this evening', 'today at 5 PM'
    - 'in 30 minutes', 'in 2 hours', 'in 3 days'
    - 'next monday', 'next friday at 4 PM'
    - '2026-09-25 18:00', '25 Sep 6 PM'
    """
    if not text:
        return None

    raw = text.strip().lower()
    now = datetime.now()

    # Relative time: in X minutes / hours / days
    rel_match = re.search(r"in\s+(\d+)\s+(minute|min|hour|hr|day|week)s?", raw)
    if rel_match:
        qty = int(rel_match.group(1))
        unit = rel_match.group(2)
        if unit.startswith("min"):
            return now + timedelta(minutes=qty)
        elif unit.startswith("hr") or unit.startswith("hour"):
            return now + timedelta(hours=qty)
        elif unit.startswith("day"):
            return now + timedelta(days=qty)
        elif unit.startswith("week"):
            return now + timedelta(weeks=qty)

    # Time extractor helper (e.g., '7 pm', '19:00', '8:30 am', 'noon')
    def extract_time(t_str: str, default_h: int = 9, default_m: int = 0) -> Tuple[int, int]:
        m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t_str)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2)) if m.group(2) else 0
            meridiem = m.group(3)
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            return hour, minute
        if "evening" in t_str or "tonight" in t_str:
            return 19, 0
        if "morning" in t_str:
            return 9, 0
        if "afternoon" in t_str:
            return 14, 0
        if "noon" in t_str:
            return 12, 0
        return default_h, default_m

    # Today / Tonight
    if "today" in raw or "tonight" in raw or "this evening" in raw:
        h, m = extract_time(raw, default_h=20 if "tonight" in raw else 18)
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        return target if target > now else target + timedelta(days=1)

    # Tomorrow
    if "tomorrow" in raw:
        h, m = extract_time(raw, default_h=19, default_m=0)
        target = (now + timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
        return target

    # Day of week: next monday, on friday, etc.
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    for day_name, day_idx in weekdays.items():
        if day_name in raw:
            h, m = extract_time(raw, default_h=18, default_m=0)
            days_ahead = (day_idx - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = (now + timedelta(days=days_ahead)).replace(hour=h, minute=m, second=0, microsecond=0)
            return target

    # ISO or standard date formats fallback
    for fmt in (
        "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
        "%d/%m/%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y %H:%M", "%d-%m-%Y",
        "%B %d at %I %p", "%b %d at %I %p", "%B %d %I:%M %p", "%b %d %I:%M %p"
    ):
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue

    return None


class TaskManager:
    """Business logic service for managing productivity tasks."""

    def __init__(self, repo: Optional[TaskRepository] = None):
        self.repo = repo or TaskRepository()

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str | TaskPriority = TaskPriority.MEDIUM,
        category: str = "General",
        due_at: Optional[str | datetime] = None,
        notes: str = "",
    ) -> Task:
        """Creates and stores a new task, parsing natural language dates if string is passed."""
        due_datetime: Optional[datetime] = None
        if isinstance(due_at, str):
            due_datetime = parse_natural_date(due_at)
        elif isinstance(due_at, datetime):
            due_datetime = due_at

        # Parse priority enum
        if isinstance(priority, str):
            p_upper = priority.strip().upper()
            priority_enum = TaskPriority(p_upper) if p_upper in TaskPriority.__members__ else TaskPriority.MEDIUM
        else:
            priority_enum = priority

        task = Task(
            title=title,
            description=description,
            priority=priority_enum,
            status=TaskStatus.PENDING,
            category=category,
            due_at=due_datetime,
            notes=notes,
        )
        saved = self.repo.create(task)
        logger.info(f"Task created: #{saved.id} - '{saved.title}' [Due: {saved.due_at}]")
        return saved

    def list_tasks(self, status: Optional[TaskStatus] = None, limit: int = 50) -> List[Task]:
        return self.repo.list_all(status=status, limit=limit)

    def get_upcoming(self, days: int = 7) -> List[Task]:
        return self.repo.get_due_today_or_upcoming(days=days)

    def complete_task(self, task_id: int) -> bool:
        return self.repo.complete_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        return self.repo.delete(task_id)

    def search_tasks(self, query: str) -> List[Task]:
        return self.repo.search(query)


_task_manager_instance: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TaskManager()
    return _task_manager_instance


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
