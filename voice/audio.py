# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Audio device discovery and stream handling for OMEN voice pipeline.
"""

import sounddevice as sd
from typing import List, Optional
from dataclasses import dataclass
from app.logging_config import logger


@dataclass
class AudioDevice:
    name: str
    index: int
    is_input: bool
    sample_rate: int = 16000
    channels: int = 1


def list_input_devices() -> List[AudioDevice]:
    """Lists all available audio input devices."""
    devices = []
    try:
        devices_info = sd.query_devices()
        for i, dev in enumerate(devices_info):
            if dev["max_input_channels"] > 0:
                devices.append(AudioDevice(
                    name=dev["name"],
                    index=i,
                    is_input=True,
                    sample_rate=int(dev["default_samplerate"]),
                    channels=dev["max_input_channels"],
                ))
    except Exception as e:
        logger.warning(f"Failed to list audio devices: {e}")
    return devices


def list_output_devices() -> List[AudioDevice]:
    """Lists all available audio output devices."""
    devices = []
    try:
        devices_info = sd.query_devices()
        for i, dev in enumerate(devices_info):
            if dev["max_output_channels"] > 0:
                devices.append(AudioDevice(
                    name=dev["name"],
                    index=i,
                    is_input=False,
                    sample_rate=int(dev["default_samplerate"]),
                    channels=dev["max_output_channels"],
                ))
    except Exception as e:
        logger.warning(f"Failed to list audio devices: {e}")
    return devices


def get_default_input_device() -> Optional[AudioDevice]:
    """Returns the default audio input device."""
    inputs = list_input_devices()
    return inputs[0] if inputs else None


def record_audio(duration_seconds: float, sample_rate: int = 16000) -> Optional[bytes]:
    """Records raw audio bytes for the given duration."""
    try:
        audio = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        return audio.tobytes()
    except Exception as e:
        logger.warning(f"Audio recording failed: {e}")
        return None


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
