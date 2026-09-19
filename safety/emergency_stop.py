# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Global Emergency Stop Mechanism for OMEN.
"""

import threading
from typing import List, Callable, Optional
from app.logging_config import logger


class EmergencyStop:
    """Global kill-switch manager capable of halting all operations immediately."""

    def __init__(self):
        self._stopped = threading.Event()
        self._callbacks: List[Callable[[], None]] = []
        self._listener_thread = None
        self._lock = threading.Lock()

    def is_stopped(self) -> bool:
        """Returns True if emergency stop has been activated."""
        return self._stopped.is_set()

    def trigger(self, reason: str = "User triggered Emergency Stop"):
        """Activates emergency stop, interrupting all active processes."""
        self._stopped.set()
        logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")

        with self._lock:
            callbacks = list(self._callbacks)

        for cb in callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Error in emergency stop callback: {e}")

    def reset(self):
        """Resets the emergency stop state to allow normal operation."""
        self._stopped.clear()
        logger.info("Emergency Stop has been reset. OMEN returned to normal state.")

    def register_callback(self, callback: Callable[[], None]):
        """Registers a callback function to be called on emergency stop."""
        with self._lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[], None]):
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def start_hotkey_listener(self):
        """Starts background global hotkey listener for emergency stop."""
        def _listen():
            try:
                from pynput import keyboard

                def on_activate():
                    self.trigger("Global hotkey Ctrl+Shift+Esc pressed")

                with keyboard.GlobalHotKeys({
                    '<ctrl>+<shift>+<esc>': on_activate,
                    '<ctrl>+<alt>+q': on_activate,
                }) as h:
                    h.join()
            except Exception as e:
                logger.warning(f"Could not start pynput global hotkey listener: {e}")

        t = threading.Thread(target=_listen, daemon=True, name="EmergencyStopHotkeyListener")
        t.start()
        self._listener_thread = t


_emergency_stop_instance: Optional[EmergencyStop] = None


def get_emergency_stop() -> EmergencyStop:
    global _emergency_stop_instance
    if _emergency_stop_instance is None:
        _emergency_stop_instance = EmergencyStop()
    return _emergency_stop_instance


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
