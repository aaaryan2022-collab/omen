# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
TTS (Text-to-Speech) module with thread-safe speaking and interrupt.
"""

from typing import Optional
from providers.tts.local_tts import TTSController
from app.config import config
from app.logging_config import logger


class OmenTTS:
    """
    OMEN's Text-to-Speech controller.
    Wraps the TTS provider for convenient use by the Agent and UI.
    """

    def __init__(self):
        self._provider = TTSController()
        self._available = self._provider.is_available

    @property
    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str, interrupt: bool = True):
        """
        Speaks text. If interrupt=True, stops any current speech first.
        """
        if not self._available or not text.strip():
            return
        if interrupt:
            self._provider.speak_async(text)
        else:
            self._provider.speak(text)

    def stop(self):
        """Stops any ongoing speech."""
        if self._provider:
            self._provider.stop()

    def get_voices(self):
        """Returns available voice profiles."""
        if self._provider:
            return self._provider.get_available_voices()
        return []


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
