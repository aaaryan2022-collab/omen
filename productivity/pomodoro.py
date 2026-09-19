# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Pomodoro Focus Timer state machine and notification integration.
"""

import time
import threading
from typing import Optional, Callable, Dict, Any
from app.constants import PomodoroState
from app.config import config
from productivity.notifications import get_notification_service
from app.logging_config import logger


class PomodoroTimer:
    """State machine for Pomodoro work and break sessions."""

    def __init__(self):
        self.state: PomodoroState = PomodoroState.IDLE
        self.work_duration_secs = config.pomodoro_work_minutes * 60
        self.short_break_secs = config.pomodoro_short_break_minutes * 60
        self.long_break_secs = config.pomodoro_long_break_minutes * 60
        self.completed_cycles: int = 0
        self.time_remaining_secs: int = self.work_duration_secs
        self.session_tag: str = "Focus"

        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()
        self._on_tick_callbacks = []
        self._on_state_change_callbacks = []

    def start(self, duration_minutes: Optional[int] = None, tag: str = "Focus"):
        """Starts a Pomodoro focus session."""
        with self._lock:
            if duration_minutes:
                self.time_remaining_secs = duration_minutes * 60
            else:
                self.time_remaining_secs = self.work_duration_secs

            self.session_tag = tag
            self.state = PomodoroState.WORK
            self._stop_event.clear()
            self._pause_event.clear()

        self._notify_state_change()
        logger.info(f"Pomodoro started: {self.time_remaining_secs // 60} mins [{self.session_tag}]")

        if self._timer_thread is None or not self._timer_thread.is_alive():
            self._timer_thread = threading.Thread(target=self._run_loop, daemon=True, name="PomodoroWorker")
            self._timer_thread.start()

    def pause(self):
        """Pauses the active Pomodoro."""
        with self._lock:
            if self.state in (PomodoroState.WORK, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
                self._pause_event.set()
                self.state = PomodoroState.PAUSED
        self._notify_state_change()

    def resume(self):
        """Resumes a paused Pomodoro."""
        with self._lock:
            if self.state == PomodoroState.PAUSED:
                self._pause_event.clear()
                self.state = PomodoroState.WORK
        self._notify_state_change()

    def stop(self):
        """Stops and resets the Pomodoro session."""
        with self._lock:
            self._stop_event.set()
            self._pause_event.clear()
            self.state = PomodoroState.IDLE
            self.time_remaining_secs = self.work_duration_secs
        self._notify_state_change()

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            mins = self.time_remaining_secs // 60
            secs = self.time_remaining_secs % 60
            return {
                "state": self.state.value,
                "time_remaining_formatted": f"{mins:02d}:{secs:02d}",
                "seconds_remaining": self.time_remaining_secs,
                "completed_cycles": self.completed_cycles,
                "tag": self.session_tag,
            }

    def register_on_tick(self, cb: Callable[[str, int], None]):
        self._on_tick_callbacks.append(cb)

    def register_on_state_change(self, cb: Callable[[PomodoroState], None]):
        self._on_state_change_callbacks.append(cb)

    def _notify_state_change(self):
        for cb in self._on_state_change_callbacks:
            try:
                cb(self.state)
            except Exception:
                pass

    def _run_loop(self):
        while not self._stop_event.is_set():
            time.sleep(1)
            if self._pause_event.is_set():
                continue

            with self._lock:
                if self.state in (PomodoroState.WORK, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
                    self.time_remaining_secs -= 1

                    # Trigger tick callbacks
                    mins = self.time_remaining_secs // 60
                    secs = self.time_remaining_secs % 60
                    formatted = f"{mins:02d}:{secs:02d}"

                    if self.time_remaining_secs <= 0:
                        self._handle_session_completed()

            for cb in self._on_tick_callbacks:
                try:
                    cb(formatted, self.time_remaining_secs)
                except Exception:
                    pass

    def _handle_session_completed(self):
        notifier = get_notification_service()
        if self.state == PomodoroState.WORK:
            self.completed_cycles += 1
            if self.completed_cycles % 4 == 0:
                self.state = PomodoroState.LONG_BREAK
                self.time_remaining_secs = self.long_break_secs
                notifier.notify("Pomodoro: Great Work!", "4 cycles completed. Take a well-deserved 15-minute break.")
            else:
                self.state = PomodoroState.SHORT_BREAK
                self.time_remaining_secs = self.short_break_secs
                notifier.notify("Pomodoro: Focus Session Ended", "Time for a 5-minute break!")
        else:
            self.state = PomodoroState.WORK
            self.time_remaining_secs = self.work_duration_secs
            notifier.notify("Pomodoro: Break Over", "Ready to start the next focus session?")


_pomodoro_timer_instance: Optional[PomodoroTimer] = None


def get_pomodoro_timer() -> PomodoroTimer:
    global _pomodoro_timer_instance
    if _pomodoro_timer_instance is None:
        _pomodoro_timer_instance = PomodoroTimer()
    return _pomodoro_timer_instance


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
