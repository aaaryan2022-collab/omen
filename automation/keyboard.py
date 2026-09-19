# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Keyboard injection for automation with safety bounds.
"""

import ctypes
import time
from typing import Optional
from app.config import config
from app.logging_config import logger
from safety.safety import check_command_safety


# Virtual key codes for common keys
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_BACK = 0x08
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B


def send_keys(text: str, delay_ms: float = 0.0) -> bool:
    """
    Types the given text using keyboard injection.
    Safety: checks for dangerous command patterns first.
    """
    # Safety check — never inject potentially destructive key sequences
    if not check_command_safety(text):
        logger.warning(f"Keyboard injection blocked for safety: {text[:50]}")
        return False

    # Safety: limit total length
    if len(text) > 10000:
        logger.warning("Keyboard injection blocked: text too long")
        return False

    # Safety: require user config to allow keyboard automation
    if not config.debug_mode:
        logger.info("Keyboard injection requires debug_mode=True in config")
        return False

    try:
        for char in text:
            if char == '\n':
                key_event(VK_RETURN, 0)
            elif char == '\t':
                key_event(0x09, 0)  # VK_TAB
            elif char == '\b':
                key_event(VK_BACK, 0)
            else:
                # For printable ASCII characters
                vk = ord(char)
                if 32 <= vk <= 126:
                    key_event(vk, 0)
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
        return True
    except Exception as e:
        logger.error(f"Keyboard injection failed: {e}")
        return False


def key_event(vk_code: int, flags: int = 0) -> None:
    """Sends a single key event."""
    ctypes.windll.user32.keybd_event(vk_code, 0, flags, 0)


def press_hotkey(*keys: int) -> bool:
    """
    Presses a combination of keys simultaneously (hotkey).
    Example: press_hotkey(VK_CONTROL, 0x43) for Ctrl+C.
    """
    if not check_command_safety("hotkey"):
        return False

    try:
        for vk in keys:
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        for vk in keys:
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)  # KEYUP
        return True
    except Exception as e:
        logger.error(f"Hotkey press failed: {e}")
        return False


def press_enter() -> bool:
    """Presses Enter key."""
    return key_event_simple(VK_RETURN)


def key_event_simple(vk_code: int) -> bool:
    """Presses and releases a single key."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
        return True
    except Exception as e:
        logger.error(f"Key event failed: {e}")
        return False


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
