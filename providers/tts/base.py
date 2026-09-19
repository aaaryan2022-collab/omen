# ============================================
"""
Abstract base class for Text-to-Speech providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class TTSState(str, Enum):
    IDLE = "IDLE"
    SPEAKING = "SPEAKING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


@dataclass
class VoiceProfile:
    """Available voice profile."""
    id: int
    name: str
    language: str
    gender: str


class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""

    @abstractmethod
    def speak(self, text: str, rate: Optional[int] = None, volume: Optional[float] = None):
        """Speaks the given text. Blocks until done unless running in background."""
        pass

    @abstractmethod
    def speak_async(self, text: str, rate: Optional[int] = None, volume: Optional[float] = None):
        """Speaks text in background, interrupting any current speech."""
        pass

    @abstractmethod
    def stop(self):
        """Stops current speech immediately."""
        pass

    @abstractmethod
    def get_available_voices(self) -> list:
        """Returns list of available voice profiles."""
        pass

    @abstractmethod
    def get_state(self) -> TTSState:
        """Returns current TTS state."""
        pass


