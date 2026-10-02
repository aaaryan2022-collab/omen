# ============================================
"""
STT (Speech-to-Text) module with background listening and VAD support.
"""

import threading
from typing import Optional, Callable
from providers.stt.base import STTProvider, SpeechResult, STTState
from providers.stt.speech_rec import SpeechRecProvider
from app.config import config
from app.logging_config import logger


class OmenSTT:
    """
    OMEN's Speech-to-Text controller wrapping a concrete STT provider.
    Handles background listening, VAD, and callback dispatch.
    """

    def __init__(self, on_transcript: Optional[Callable[[str], None]] = None):
        self._provider: Optional[STTProvider] = None
        self._on_transcript = on_transcript
        self._listener_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Auto-select provider
        if config.mock_mode:
            logger.info("STT: Mock mode active")
        else:
            self._provider = SpeechRecProvider()
        # AUTO-START
        self.start()

    @property
    def is_available(self) -> bool:
        return self._provider is not None and self._provider.is_available

    @property
    def last_error(self) -> Optional[str]:
        return getattr(self._provider, "last_error", None) if self._provider else None

    def start(self, on_transcript: Optional[Callable[[str], None]] = None):
        """Starts background STT listening."""
        if not self.is_available:
            logger.warning("Cannot start STT: provider unavailable")
            return False

        if on_transcript:
            self._on_transcript = on_transcript

        self._stop_event.clear()
        self._listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="STTDispatch"
        )
        self._listener_thread.start()
        logger.info("OMEN STT started")
        return True

    def stop(self):
        """Stops STT listening."""
        self._stop_event.set()
        if self._listener_thread:
            self._listener_thread.join(timeout=5.0)
        logger.info("OMEN STT stopped")

    def listen_once(self) -> Optional[str]:
        """Capture one utterance and return its transcript."""
        if not self.is_available:
            logger.warning("Cannot listen: microphone provider unavailable")
            return None
        try:
            self._provider.start_listening()
            result = self._provider.stop_listening()
            return result.text if result and result.text.strip() else None
        except Exception as exc:
            logger.warning("Single voice capture failed: %s", exc)
            return None

    def _listen_loop(self):
        """Background loop that uses provider to get transcripts."""
        while not self._stop_event.is_set():
            try:
                self._provider.start_listening()
                result = self._provider.stop_listening()
                if result and result.text.strip() and not self._stop_event.is_set():
                    logger.info(f"Transcript: {result.text}")
                    if self._on_transcript:
                        try:
                            self._on_transcript(result.text)
                        except Exception as e:
                            logger.error(f"Transcript callback error: {e}")
            except Exception as e:
                logger.error(f"STT loop error: {e}")


