# ============================================
"""
Wake word detection module. Listens for "OMEN" trigger in background.
"""

import threading
from typing import Optional, Callable
from app.config import config
from app.logging_config import logger

try:
    import sounddevice as sd
    import numpy as np
    _HAVE_AUDIO = True
except ImportError:
    _HAVE_AUDIO = False


class WakeWordListener:
    """
    Background wake word detector.
    Currently uses energy-based silence detection + keyword matching placeholder.
    In production, use Vosk or Porcupine for real wake word detection.
    """

    def __init__(self, on_wake: Optional[Callable] = None):
        self._on_wake = on_wake
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._detected_callbacks: list = []

    @property
    def is_available(self) -> bool:
        return _HAVE_AUDIO and config.wake_word_enabled

    def register_callback(self, callback: Callable):
        """Registers a callback to call when wake word is detected."""
        self._detected_callbacks.append(callback)

    def start(self):
        """Starts background wake word detection."""
        if not self.is_available:
            logger.info("Wake word disabled or unavailable")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._detect_loop, daemon=True, name="WakeWord"
        )
        self._thread.start()
        logger.info("Wake word detection started")
        return True

    def stop(self):
        """Stops wake word detection."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3.0)

    def _detect_loop(self):
        """Background loop for wake word detection."""
        logger.info("Wake word listener running (placeholder — integrate Vosk/Porcupine for production)")
        while not self._stop_event.is_set():
            try:
                import time
                time.sleep(2.0)
                # Placeholder: Real implementation would use Vosk/Porcupine here
                # For now, the wake word is activated via hotkey or manual trigger
            except Exception as e:
                logger.debug(f"Wake word detect error: {e}")

    def simulate_wake(self):
        """Simulates wake word detection (for testing)."""
        logger.info("Wake word triggered (simulated)")
        for cb in self._detected_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Wake callback error: {e}")


