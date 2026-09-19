# ============================================
"""
Abstract base class for Speech-to-Text providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class STTState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    ERROR = "ERROR"


@dataclass
class SpeechResult:
    """Result from a speech-to-text transcription."""
    text: str
    confidence: float = 0.0
    duration_seconds: float = 0.0


class STTProvider(ABC):
    """Abstract base class for speech-to-text providers."""

    @abstractmethod
    def start_listening(self):
        """Starts listening for audio input."""
        pass

    @abstractmethod
    def stop_listening(self) -> Optional[SpeechResult]:
        """Stops listening and returns transcription result."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if STT engine is available."""
        pass

    @abstractmethod
    def get_state(self) -> STTState:
        """Returns current listening state."""
        pass


