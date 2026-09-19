"""
Identity voice profile — modular voice identity settings.
No Stark artifacts.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from providers.tts.base import VoiceProfile


class VoiceProfileConfig(BaseModel):
    """OMEN's voice identity settings — calm, professional, slightly futuristic."""
    name: str = Field(default="OMEN", description="Voice identity name")
    description: str = Field(default="Calm. Precise. Slightly futuristic.", description="Personality description")
    preferred_voice_index: int = Field(default=0, description="TTS voice index")
    speech_rate: int = Field(default=175, description="Words per minute")
    volume: float = Field(default=0.9, ge=0.0, le=1.0)
    language: str = Field(default="en", description="Language code")
    gender: str = Field(default="neutral", description="Voice gender preference")


class IdentityProfile:
    """Modular identity module — voice profile and persona settings."""

    def __init__(self, config: Optional[VoiceProfileConfig] = None):
        self.config = config or VoiceProfileConfig()

    def get_profile(self) -> VoiceProfileConfig:
        return self.config

    def set_voice_index(self, idx: int):
        self.config.preferred_voice_index = idx

    def describe(self) -> str:
        return f"{self.config.name}: {self.config.description} (rate={self.config.speech_rate} wpm, vol={self.config.volume})"
