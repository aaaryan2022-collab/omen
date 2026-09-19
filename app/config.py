# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Configuration management for OMEN using Pydantic Settings.
"""

from typing import List, Optional
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.constants import (
    DEFAULT_ALLOWED_DIRS,
    PROJECT_ROOT,
    DEFAULT_APP_ALIASES,
)


class OmenConfig(BaseSettings):
    """Global configuration settings for OMEN Assistant."""

    # AI / LLM Provider Settings
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_model: str = Field(default="gemma4:31b-cloud", description="Default Ollama model name")
    ollama_timeout: int = Field(default=60, description="Ollama request timeout in seconds")
    ollama_temperature: float = Field(default=0.7, description="LLM sampling temperature")
    context_window_size: int = Field(default=10, description="Number of recent messages in context")

    # Voice Settings
    voice_enabled: bool = Field(default=True, description="Enable voice speech responses")
    voice_rate: int = Field(default=175, description="TTS speech rate in WPM")
    voice_volume: float = Field(default=0.9, description="TTS volume from 0.0 to 1.0")
    voice_index: int = Field(default=0, description="Selected TTS voice index")
    wake_word_enabled: bool = Field(default=False, description="Enable background wake-word detection")
    wake_word: str = Field(default="omen", description="Wake word trigger phrase")
    stt_energy_threshold: int = Field(default=300, description="Microphone speech energy threshold")
    stt_pause_threshold: float = Field(default=0.8, description="Pause duration to consider speech ended")
    microphone_index: Optional[int] = Field(default=None, description="Preferred input microphone index")

    # Security & Safety
    security_confirm_high_risk: bool = Field(default=True, description="Require confirmation for HIGH risk tools")
    allowed_directories: List[str] = Field(default_factory=lambda: list(DEFAULT_ALLOWED_DIRS), description="Permitted directory paths")
    emergency_stop_hotkey: str = Field(default="<ctrl>+<shift>+<esc>", description="Emergency stop key combination")

    # Productivity Defaults
    pomodoro_work_minutes: int = Field(default=25, description="Pomodoro work duration in minutes")
    pomodoro_short_break_minutes: int = Field(default=5, description="Pomodoro short break in minutes")
    pomodoro_long_break_minutes: int = Field(default=15, description="Pomodoro long break in minutes")

    # News & External Providers
    news_region: str = Field(default="India", description="Default news region")
    mock_mode: bool = Field(default=False, description="Enable mock mode for external services")
    email_provider: str = Field(default="mock", description="Email provider: mock, gmail, outlook, imap")

    # UI / System Settings
    debug_mode: bool = Field(default=False, description="Enable verbose debug logging and UI features")
    start_minimized: bool = Field(default=False, description="Start OMEN in the system tray")
    start_with_windows: bool = Field(default=False, description="Auto-start OMEN on Windows login")
    first_run_completed: bool = Field(default=False, description="Whether setup wizard has been run")
    theme: str = Field(default="dark", description="UI color theme")

    # Custom App Aliases
    app_aliases: dict[str, str] = Field(default_factory=lambda: dict(DEFAULT_APP_ALIASES))

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global singleton configuration
config = OmenConfig()


def reload_config() -> OmenConfig:
    """Reloads configuration from environment and disk."""
    global config
    config = OmenConfig()
    return config


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
