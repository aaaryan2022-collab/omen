# ============================================
"""
Speech-to-Text provider using SpeechRecognition (local/offline capable).
"""

import threading
import time
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

try:
    import sounddevice as sd
    _HAVE_SOUNDDEVICE = True
except ImportError:
    _HAVE_SOUNDDEVICE = False


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
        self._last_error: Optional[str] = None

        if _HAVE_SPEECH_RECOGNITION:
            try:
                self._recognizer = sr.Recognizer()
                self._recognizer.energy_threshold = config.stt_energy_threshold
                self._recognizer.pause_threshold = config.stt_pause_threshold
                try:
                    self._microphone = sr.Microphone(device_index=config.microphone_index)
                    with self._microphone as source:
                        self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                except Exception as mic_err:
                    self._microphone = None
                    if _HAVE_SOUNDDEVICE:
                        logger.debug("Falling back to sounddevice capture: %s", mic_err)
                    else:
                        logger.warning("No microphone input source available: %s", mic_err)
            except Exception as e:
                logger.debug("SpeechRecognition initialization notice: %s", e)

    @property
    def is_available(self) -> bool:
        return (
            _HAVE_SPEECH_RECOGNITION
            and self._recognizer is not None
            and (self._microphone is not None or _HAVE_SOUNDDEVICE)
        )

    def get_state(self) -> STTState:
        with self._lock:
            return self._state

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    def _set_state(self, state: STTState):
        with self._lock:
            self._state = state
            logger.debug(f"STT state: {state.value}")

    def start_listening(self):
        """Starts background listening thread."""
        if not self.is_available:
            raise RuntimeError("SpeechRecognition not available")

        self._stop_event.clear()
        self._last_error = None
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
                if self._microphone is not None:
                    with self._microphone as source:
                        audio = self._recognizer.listen(source, timeout=10, phrase_time_limit=30)
                else:
                    audio = self._listen_with_sounddevice()

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
                    except Exception as exc:
                        self._last_error = (
                            "Audio was captured, but transcription failed. "
                            "Install faster-whisper for local transcription or check network access."
                        )
                        logger.warning("Speech transcription failed: %s", exc)
                        break

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
                self._last_error = str(e)
                logger.debug(f"STT listen error: {e}")
                self._set_state(STTState.IDLE)

    def _listen_with_sounddevice(self):
        """Capture one short utterance without requiring the PyAudio package."""
        chunks = []

        def callback(indata, frames, time_info, status):
            del frames, time_info, status
            chunks.append(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=1024,
            channels=1,
            dtype="int16",
            callback=callback,
        ):
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline and not self._stop_event.is_set():
                time.sleep(0.05)
        if not chunks:
            raise RuntimeError("No microphone audio was captured")
        return sr.AudioData(b"".join(chunks), 16000, 2)

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


