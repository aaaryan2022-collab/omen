# ============================================
"""
APScheduler-based background scheduler for OMEN reminders and jobs.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import Optional, Callable
from app.logging_config import logger


class OmenScheduler:
    """
    Background task scheduler using APScheduler.
    Manages reminders, health checks, and periodic jobs.
    """

    def __init__(self):
        self._scheduler: Optional[BackgroundScheduler] = None
        self._job_store = {}

    @property
    def is_running(self) -> bool:
        return self._scheduler is not None and self._scheduler.running

    def start(self):
        """Starts the background scheduler."""
        if self._scheduler and self._scheduler.running:
            return True
        self._scheduler = BackgroundScheduler()
        self._scheduler.start()
        logger.info("APScheduler started")
        return True

    def shutdown(self, wait: bool = True):
        """Shuts down the scheduler."""
        if self._scheduler:
            self._scheduler.shutdown(wait=wait)
            logger.info("APScheduler shutdown")

    def schedule_reminder(
        self,
        reminder_id: int,
        trigger_time: datetime,
        title: str,
        message: str,
        on_fire: Optional[Callable] = None,
    ) -> bool:
        """Schedules a reminder to fire at a specific time."""
        if not self.is_running:
            self.start()

        try:
            self._scheduler.add_job(
                self._fire_reminder,
                trigger=DateTrigger(run_date=trigger_time),
                id=f"reminder_{reminder_id}",
                args=[reminder_id, title, message],
                kwargs={"callback": on_fire},
                replace_existing=True,
                name=f"Reminder: {title}",
            )
            self._job_store[reminder_id] = {
                "title": title,
                "message": message,
                "trigger_time": trigger_time,
            }
            logger.info(f"Scheduled reminder {reminder_id} at {trigger_time}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule reminder: {e}")
            return False

    def schedule_periodic(
        self,
        func: Callable,
        interval_seconds: int = 60,
        job_id: str = "periodic",
        **kwargs,
    ):
        """Schedules a periodic task."""
        if not self.is_running:
            self.start()

        try:
            self._scheduler.add_job(
                func,
                trigger=IntervalTrigger(seconds=interval_seconds),
                id=job_id,
                replace_existing=True,
                **kwargs,
            )
            logger.info(f"Scheduled periodic job {job_id} every {interval_seconds}s")
        except Exception as e:
            logger.error(f"Failed to schedule periodic job: {e}")

    def schedule_cron(self, func: Callable, job_id: str, hour: int, minute: int = 0, **kwargs):
        """Schedule a job at a local wall-clock time every day."""
        if not self.is_running:
            self.start()
        try:
            self._scheduler.add_job(
                func,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=job_id,
                replace_existing=True,
                **kwargs,
            )
            logger.info("Scheduled daily cron job %s at %02d:%02d", job_id, hour, minute)
            return True
        except Exception as exc:
            logger.error("Failed to schedule cron job: %s", exc)
            return False

    def remove_job(self, job_id: str) -> bool:
        """Removes a scheduled job."""
        try:
            if self._scheduler and self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
                return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
        return False

    @staticmethod
    def _fire_reminder(reminder_id: int, title: str, message: str, callback=None):
        """Internal: fires a reminder notification."""
        from app.logging_config import logger as log
        log.info(f"REMINDER FIRED [{reminder_id}]: {title} — {message}")
        if callback:
            try:
                callback(reminder_id, title, message)
            except Exception as e:
                log.error(f"Reminder callback error: {e}")


_scheduler_instance: Optional[OmenScheduler] = None


def get_scheduler() -> OmenScheduler:
    """Return the process-wide background scheduler."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = OmenScheduler()
        _scheduler_instance.start()
    return _scheduler_instance


