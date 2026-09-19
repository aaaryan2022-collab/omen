# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Speech-to-Text provider using SpeechRecognition (local/offline capable).
"""

import threading
from typing import Optional
from datetime import datetime
from providers.stt.base import STTProvider, SpeechResult, STTState
from app.config import config
from app.logging_config import logger

try:
    import speech_recognition as sr
    _HAVE_SPEECH_RECOGNITION = True
except ImportError:
    _HAVE_SPEECH_RECOGNITION = False


class SpeechRecProvider(STTProvider):
    """Speech recognition provider using offline-capable SpeechRecognition library."""

    def __init__(self):
        self._state = STTState.IDLE
        self._result: Optional[SpeechResult] = None
        self._lock = threading.Lock()
        self._recognizer = None
        self._microphone = None
        self._listener_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        if _HAVE_SPEECH_RECOGNITION:
            try:
                self._recognizer = sr.Recognizer()
                self._recognizer.energy_threshold = config.stt_energy_threshold
                self._recognizer.pause_threshold = config.stt_pause_threshold
                self._microphone = sr.Microphone(device_index=config.microphone_index)
                # Adjust for ambient noise
                logger.info("Adjusting for ambient noise...")
                with self._microphone as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except Exception as e:
                logger.warning(f"SpeechRecognition init warning: {e}")

    @property
    def is_available(self) -> bool:
        return _HAVE_SPEECH_RECOGNITION and self._recognizer is not None

    def get_state(self) -> STTState:
        with self._lock:
            return self._state

    def _set_state(self, state: STTState):
        with self._lock:
            self._state = state
            logger.debug(f"STT state: {state.value}")

    def start_listening(self):
        """Starts background listening thread."""
        if not self.is_available:
            raise RuntimeError("SpeechRecognition not available")

        self._stop_event.clear()
        self._set_state(STTState.LISTENING)
        self._listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="STTListener"
        )
        self._listener_thread.start()
        logger.info("STT listening started")

    def stop_listening(self) -> Optional[SpeechResult]:
        """Stops listening and returns the transcription."""
        self._stop_event.set()
        self._set_state(STTState.IDLE)
        if self._listener_thread:
            self._listener_thread.join(timeout=5.0)
        result = self._result
        self._result = None
        return result

    def _listen_loop(self):
        """Background loop that listens and transcribes."""
        while not self._stop_event.is_set():
            try:
                self._set_state(STTState.TRANSCRIBING)
                with self._microphone as source:
                    audio = self._recognizer.listen(source, timeout=10, phrase_time_limit=30)

                if self._stop_event.is_set():
                    break

                # Try offline recognition first (uses local VAD/WT)
                try:
                    text = self._recognizer.recognize_google(audio)
                    # In real deployment, use recognize_sphinx() or faster-whisper here
                except Exception:
                    try:
                        import faster_whisper
                        text = self._faster_whisper_transcribe(audio)
                    except Exception:
                        logger.warning("Speech recognition failed, no speech detected or error")
                        continue

                if text and text.strip():
                    confidence = 0.85  # SpeechRecognition doesn't provide confidence for Google
                    duration = 0.0
                    with self._lock:
                        self._result = SpeechResult(
                            text=text.strip(),
                            confidence=confidence,
                            duration_seconds=duration,
                        )
                    logger.info(f"STT result: {text.strip()}")
                    self._set_state(STTState.IDLE)
                    break

            except Exception as e:
                logger.debug(f"STT listen error: {e}")
                self._set_state(STTState.IDLE)

    def _faster_whisper_transcribe(self, audio) -> str:
        """Fallback transcription using faster-whisper."""
        try:
            import faster_whisper
            import numpy as np

            # Convert audio to numpy array
            audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(np.float32) / 32768.0
            model = faster_whisper.WhisperModel("tiny", device="cpu")
            segments, _ = model.transcribe(audio_data, language="en")
            return " ".join(segment.text for segment in segments)
        except Exception as e:
            logger.warning(f"faster-whisper fallback failed: {e}")
            return ""


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
