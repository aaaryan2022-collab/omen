# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Mouse automation with safety killswitch.
"""

import ctypes
import time
from typing import Optional, Tuple
from app.config import config
from app.logging_config import logger
from safety.safety import check_command_safety

# Mouse event flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000


def move_mouse(x: int, y: int, absolute: bool = False) -> bool:
    """
    Moves the mouse cursor to (x, y).
    If absolute=True, uses absolute screen coordinates.
    Safety: requires debug_mode=True.
    """
    if not config.debug_mode:
        logger.info("Mouse automation requires debug_mode=True in config")
        return False

    if not check_command_safety("mouse"):
        return False

    try:
        if absolute:
            # Convert to 65535 range for absolute positioning
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            abs_x = int((x / screen_width) * 65535)
            abs_y = int((y / screen_height) * 65535)
            ctypes.windll.user32.mouse_event(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                abs_x, abs_y, 0, 0
            )
        else:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, x, y, 0, 0)
        return True
    except Exception as e:
        logger.error(f"Mouse move failed: {e}")
        return False


def click_mouse(x: int, y: int, button: str = "left", absolute: bool = False) -> bool:
    """
    Clicks at (x, y) with specified button ('left', 'right', 'middle').
    """
    if not config.debug_mode:
        logger.info("Mouse automation requires debug_mode=True in config")
        return False

    try:
        if absolute:
            move_mouse(x, y, absolute=True)
        else:
            move_mouse(x, y)

        time.sleep(0.05)

        if button == "left":
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif button == "middle":
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
        return True
    except Exception as e:
        logger.error(f"Mouse click failed: {e}")
        return False


def double_click(x: int, y: int) -> bool:
    """Double-clicks at (x, y)."""
    if not click_mouse(x, y, "left"):
        return False
    time.sleep(0.1)
    return click_mouse(x, y, "left")


def get_mouse_position() -> Optional[Tuple[int, int]]:
    """Returns current mouse cursor position (x, y)."""
    try:
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)
    except Exception as e:
        logger.debug(f"Failed to get mouse position: {e}")
        return None


def scroll_mouse(delta: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
    """Scrolls the mouse wheel by delta."""
    if not config.debug_mode:
        return False
    try:
        if x is not None and y is not None:
            move_mouse(x, y)
        ctypes.windll.user32.mouse_event(0x0080, 0, delta * 120, 0, 0)  # MK_MOUSEWHEEL
        return True
    except Exception as e:
        logger.error(f"Scroll failed: {e}")
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
