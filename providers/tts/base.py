# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
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
