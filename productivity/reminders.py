# ============================================
"""
Reminder Management Service for scheduling and triggering notifications.
"""

from datetime import datetime
from typing import Optional, List, Callable
from database.database import Database, get_db
from database.models import Reminder
from database.repositories import ReminderRepository
from productivity.tasks import parse_natural_date
from productivity.notifications import get_notification_service
from app.constants import ReminderStatus
from app.logging_config import logger


class ReminderManager:
    """Business logic service for creating, managing and triggering reminders."""

    def __init__(self, repo: Optional[ReminderRepository] = None):
        self.repo = repo or ReminderRepository()
        self.notification_service = get_notification_service()
        self._on_fire_callbacks: List[Callable[[Reminder], None]] = []

    def register_on_fire(self, callback: Callable[[Reminder], None]):
        """Registers a callback to be notified when a reminder fires (e.g. for TTS / UI sound)."""
        self._on_fire_callbacks.append(callback)

    def set_reminder(
        self,
        title: str,
        trigger_time: str | datetime,
        message: str = "",
        is_recurring: bool = False,
        recurring_cron: Optional[str] = None,
        associated_task_id: Optional[int] = None,
    ) -> Optional[Reminder]:
        """Creates and stores a reminder."""
        target_time: Optional[datetime] = None
        if isinstance(trigger_time, str):
            target_time = parse_natural_date(trigger_time)
        elif isinstance(trigger_time, datetime):
            target_time = trigger_time

        if not target_time:
            logger.error(f"Could not parse reminder trigger time: '{trigger_time}'")
            return None

        reminder = Reminder(
            title=title,
            message=message or title,
            trigger_time=target_time,
            status=ReminderStatus.SCHEDULED,
            is_recurring=is_recurring,
            recurring_cron=recurring_cron,
            associated_task_id=associated_task_id,
        )
        saved = self.repo.create(reminder)
        logger.info(f"Reminder set: #{saved.id} - '{saved.title}' at {saved.trigger_time.strftime('%Y-%m-%d %H:%M')}")
        return saved

    def list_active(self) -> List[Reminder]:
        return self.repo.list_active()

    def list_all(self, limit: int = 50) -> List[Reminder]:
        return self.repo.list_all(limit=limit)

    def check_and_fire_due_reminders(self) -> List[Reminder]:
        """Checks for any active reminders whose trigger_time has passed, and fires notifications."""
        now = datetime.now()
        active = self.repo.list_active()
        fired = []
        for r in active:
            if r.trigger_time <= now:
                self.fire_reminder(r)
                fired.append(r)
        return fired

    def fire_reminder(self, reminder: Reminder):
        """Fires a reminder alert."""
        logger.info(f"FIRING REMINDER #{reminder.id}: {reminder.title} - {reminder.message}")
        self.repo.mark_fired(reminder.id)  # type: ignore
        self.notification_service.notify(
            title=f"OMEN Reminder: {reminder.title}",
            message=reminder.message or "Scheduled reminder alert."
        )
        for cb in self._on_fire_callbacks:
            try:
                cb(reminder)
            except Exception as e:
                logger.error(f"Error in reminder fire callback: {e}")

    def dismiss_reminder(self, reminder_id: int) -> bool:
        return self.repo.dismiss(reminder_id)

    def delete_reminder(self, reminder_id: int) -> bool:
        return self.repo.delete(reminder_id)


_reminder_manager_instance: Optional[ReminderManager] = None


def get_reminder_manager() -> ReminderManager:
    global _reminder_manager_instance
    if _reminder_manager_instance is None:
        _reminder_manager_instance = ReminderManager()
    return _reminder_manager_instance


