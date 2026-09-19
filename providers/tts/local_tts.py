# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Text-to-Speech provider using pyttsx3 (offline, Windows SAPI5 backend).
"""

import threading
import queue
from typing import Optional
from providers.tts.base import TTSProvider, TTSState, VoiceProfile
from app.config import config
from app.logging_config import logger

try:
    import pyttsx3
    _HAVE_PYTTSX3 = True
except ImportError:
    _HAVE_PYTTSX3 = False


class TTSController(TTSProvider):
    """
    Thread-safe TTS controller using pyttsx3.
    Supports async speaking, interruption, and a speak queue.
    """

    def __init__(self):
        self._state = TTSState.IDLE
        self._lock = threading.Lock()
        self._speak_queue: queue.Queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._engine = None
        self._interrupt_event = threading.Event()

        if _HAVE_PYTTSX3:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", config.voice_rate)
                self._engine.setProperty("volume", config.voice_volume)
                # Select voice by index
                voices = self._engine.getProperty("voices")
                if config.voice_index < len(voices):
                    self._engine.setProperty("voice", voices[config.voice_index].id)
                logger.info("pyttsx3 TTS engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
                self._engine = None

        # Start queue worker
        self._worker_thread = threading.Thread(
            target=self._queue_worker, daemon=True, name="TTSWorker"
        )
        self._worker_thread.start()

    @property
    def is_available(self) -> bool:
        return _HAVE_PYTTSX3 and self._engine is not None

    def get_state(self) -> TTSState:
        with self._lock:
            return self._state

    def _set_state(self, state: TTSState):
        with self._lock:
            self._state = state

    def speak(self, text: str, rate: Optional[int] = None, volume: Optional[float] = None):
        """Speaks text synchronously (blocks until done)."""
        if not self.is_available or not text.strip():
            return
        self._speak_text(text, rate, volume)

    def speak_async(self, text: str, rate: Optional[int] = None, volume: Optional[float] = None):
        """Speaks text in background, interrupting any current speech."""
        if not self.is_available or not text.strip():
            return
        self._interrupt_event.set()  # Interrupt current speech
        self._speak_queue.put((text, rate, volume))

    def stop(self):
        """Stops current speech immediately."""
        self._interrupt_event.set()
        self._speak_queue.queue.clear()
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
        self._set_state(TTSState.IDLE)

    def get_available_voices(self) -> list:
        voices = []
        if self._engine:
            for i, v in enumerate(self._engine.getProperty("voices")):
                voices.append(VoiceProfile(
                    id=i,
                    name=v.name,
                    language=v.languages[0] if v.languages else "en",
                    gender="unknown",
                ))
        return voices

    def _speak_text(self, text: str, rate: Optional[int], volume: Optional[float]):
        """Internal method to speak text on the main thread."""
        if not self._engine:
            return
        try:
            self._set_state(TTSState.SPEAKING)
            if rate is not None:
                self._engine.setProperty("rate", rate)
            if volume is not None:
                self._engine.setProperty("volume", volume)
            self._engine.say(text)
            self._engine.runAndWait()
            self._set_state(TTSState.IDLE)
        except Exception as e:
            logger.error(f"TTS speak error: {e}")
            self._set_state(TTSState.ERROR)

    def _queue_worker(self):
        """Background worker that processes the speak queue."""
        while True:
            try:
                text, rate, volume = self._speak_queue.get(timeout=1.0)
                if self._interrupt_event.is_set():
                    self._interrupt_event.clear()
                    try:
                        self._engine.stop()
                    except Exception:
                        pass

                if self.is_available and text.strip():
                    self._speak_text(text, rate, volume)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS worker error: {e}")


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
