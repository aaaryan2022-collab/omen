# ============================================
"""
Speech-to-Text provider using SpeechRecognition (local/offline capable).
Optimized for low-latency, dynamic VAD, and continuous conversational speech.
"""

import threading
import time
import math
from typing import Optional
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
    """Robust speech recognition provider with dynamic VAD and fallback pipeline."""

    _instance: Optional["SpeechRecProvider"] = None

    @classmethod
    def get_instance(cls) -> "SpeechRecProvider":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._state = STTState.IDLE
        self._result: Optional[SpeechResult] = None
        self._lock = threading.Lock()
        self._recognizer: Optional[sr.Recognizer] = None
        self._microphone: Optional[sr.Microphone] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_error: Optional[str] = None
        self._device_index: Optional[int] = None

        if _HAVE_SPEECH_RECOGNITION:
            try:
                self._recognizer = sr.Recognizer()
                # Optimized VAD parameters for responsive desktop conversational interaction
                self._recognizer.energy_threshold = max(120, config.stt_energy_threshold or 250)
                self._recognizer.dynamic_energy_threshold = True
                self._recognizer.dynamic_energy_adjustment_damping = 0.15
                self._recognizer.dynamic_energy_ratio = 1.4
                self._recognizer.pause_threshold = 0.85
                self._recognizer.phrase_threshold = 0.25
                self._recognizer.non_speaking_duration = 0.5

                # Detect best input device index
                target_index = config.microphone_index
                if target_index is None and _HAVE_SOUNDDEVICE:
                    try:
                        def_input = sd.default.device[0]
                        if def_input is not None and def_input >= 0:
                            dev_info = sd.query_devices(def_input)
                            if dev_info.get("max_input_channels", 0) > 0:
                                target_index = def_input
                    except Exception as dev_err:
                        logger.debug("Sounddevice default query notice: %s", dev_err)

                self._device_index = target_index

                # Initialize microphone instance
                try:
                    self._microphone = sr.Microphone(device_index=self._device_index)
                    with self._microphone as source:
                        logger.info(
                            "Calibrating OMEN microphone (device index: %s)...",
                            self._device_index if self._device_index is not None else "System Default",
                        )
                        self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                        # Clamp calibrated threshold to avoid deafening or overly sensitive thresholds
                        self._recognizer.energy_threshold = max(120, min(480, self._recognizer.energy_threshold))
                        logger.info("Calibrated STT energy threshold: %.1f", self._recognizer.energy_threshold)
                except Exception as mic_err:
                    logger.warning("Default microphone init failed (%s); trying fallback default", mic_err)
                    try:
                        self._microphone = sr.Microphone()
                        with self._microphone as source:
                            self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                            self._recognizer.energy_threshold = max(120, min(480, self._recognizer.energy_threshold))
                    except Exception as fallback_err:
                        self._microphone = None
                        logger.warning("Microphone initialization fell back to sounddevice: %s", fallback_err)
            except Exception as e:
                logger.error("SpeechRecognition engine setup error: %s", e)

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
            logger.debug("STT state: %s", state.value)

    def start_listening(self):
        """Starts background listening thread."""
        if not self.is_available:
            raise RuntimeError("SpeechRecognition backend is unavailable")

        self._stop_event.clear()
        self._last_error = None
        self._set_state(STTState.LISTENING)
        self._listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="STTListener"
        )
        self._listener_thread.start()
        logger.info("STT listening started")

    def stop_listening(self) -> Optional[SpeechResult]:
        """Stops background listening and returns transcription."""
        self._stop_event.set()
        self._set_state(STTState.IDLE)
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=3.0)
        result = self._result
        self._result = None
        return result

    def listen_once(self, timeout: float = 6.0, phrase_time_limit: float = 14.0) -> Optional[SpeechResult]:
        """Directly listens for a single utterance and transcribes it synchronously."""
        if not self.is_available:
            self._last_error = "Audio input system unavailable"
            return None

        self._set_state(STTState.LISTENING)
        self._last_error = None

        try:
            audio = None
            if self._microphone is not None:
                with self._microphone as source:
                    # Do NOT run adjust_for_ambient_noise here to avoid clipping the user's initial syllable
                    try:
                        audio = self._recognizer.listen(
                            source, timeout=timeout, phrase_time_limit=phrase_time_limit
                        )
                    except sr.WaitTimeoutError:
                        self._last_error = "No speech detected"
                        self._set_state(STTState.IDLE)
                        return None
            else:
                audio = self._listen_with_sounddevice(timeout=timeout, phrase_time_limit=phrase_time_limit)

            if not audio:
                self._last_error = "No speech detected"
                self._set_state(STTState.IDLE)
                return None

            self._set_state(STTState.TRANSCRIBING)
            text = ""

            # Primary transcription: Google Speech Recognition
            try:
                text = self._recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                self._last_error = "Speech was unclear"
                self._set_state(STTState.IDLE)
                return None
            except sr.RequestError as req_err:
                # Network unreachable; attempt local faster-whisper fallback
                try:
                    text = self._faster_whisper_transcribe(audio)
                except Exception:
                    self._last_error = f"Speech service unreachable: {req_err}"
            except Exception as exc:
                try:
                    text = self._faster_whisper_transcribe(audio)
                except Exception:
                    self._last_error = f"Transcription error: {exc}"

            self._set_state(STTState.IDLE)
            if text and text.strip():
                return SpeechResult(text=text.strip(), confidence=0.92, duration_seconds=0.0)
            return None

        except Exception as e:
            self._last_error = str(e)
            self._set_state(STTState.IDLE)
            return None

    def _listen_with_sounddevice(self, timeout: float = 6.0, phrase_time_limit: float = 14.0):
        """VAD-guided recording via sounddevice if PyAudio/Microphone is unavailable."""
        if not _HAVE_SOUNDDEVICE:
            return None

        chunks = []
        speech_started = False
        silence_start = None
        start_time = time.monotonic()
        threshold = 450.0  # RMS threshold for speech detection

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
            while not self._stop_event.is_set():
                now = time.monotonic()
                if not speech_started and (now - start_time) > timeout:
                    return None
                if speech_started and (now - start_time) > phrase_time_limit:
                    break

                # Inspect recent chunk energy
                if chunks:
                    last_chunk = chunks[-1]
                    samples = [int.from_bytes(last_chunk[i:i+2], "little", signed=True) for i in range(0, len(last_chunk), 2)]
                    if samples:
                        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
                        if rms > threshold:
                            speech_started = True
                            silence_start = None
                        elif speech_started:
                            if silence_start is None:
                                silence_start = now
                            elif (now - silence_start) > 0.8:  # 800ms of trailing silence ends utterance
                                break
                time.sleep(0.04)

        if not chunks or not speech_started:
            return None
        return sr.AudioData(b"".join(chunks), 16000, 2)

    def _listen_loop(self):
        """Continuous background listening loop."""
        while not self._stop_event.is_set():
            res = self.listen_once(timeout=8.0, phrase_time_limit=14.0)
            if res and res.text:
                with self._lock:
                    self._result = res
                logger.info("STT heard: %s", res.text)
                break
            time.sleep(0.1)

    def _faster_whisper_transcribe(self, audio) -> str:
        """Local offline transcription fallback via faster-whisper."""
        try:
            import faster_whisper
            import numpy as np
            audio_bytes = audio.get_raw_data(convert_rate=16000, convert_width=2)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            model = faster_whisper.WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(audio_data, language="en")
            return " ".join(s.text for s in segments)
        except Exception as e:
            logger.debug("faster-whisper local fallback unavailable: %s", e)
            return ""


def get_stt_provider() -> SpeechRecProvider:
    return SpeechRecProvider.get_instance()
