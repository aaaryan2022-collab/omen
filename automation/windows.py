# ============================================
"""
Windows OS API interactions for window management.
"""

import ctypes
import ctypes.wintypes
from typing import Optional, List
from dataclasses import dataclass
from app.logging_config import logger


@dataclass
class WindowInfo:
    """Information about a desktop window."""
    hwnd: int
    title: str
    class_name: str
    visible: bool


def get_all_windows() -> List[WindowInfo]:
    """Returns a list of all visible windows."""
    windows = []

    def _enum_callback(hwnd, _):
        if not ctypes.windll.user32.IsWindowVisible(hwnd):
            return True

        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True

        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value

        class_buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, class_buf, 256)

        windows.append(WindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_buf.value,
            visible=True,
        ))
        return True

    try:
        ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(_enum_callback), 0)
    except Exception as e:
        logger.error(f"Failed to enumerate windows: {e}")

    return windows


def get_window_by_title(partial_title: str) -> Optional[WindowInfo]:
    """Finds a window by partial title match."""
    for win in get_all_windows():
        if partial_title.lower() in win.title.lower():
            return win
    return None


def focus_window(hwnd: int) -> bool:
    """Brings a window to the foreground."""
    try:
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        logger.error(f"Failed to focus window: {e}")
        return False


def minimize_window(hwnd: int) -> bool:
    """Minimizes a window."""
    try:
        ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
        return True
    except Exception as e:
        logger.error(f"Failed to minimize window: {e}")
        return False


def get_active_window_title() -> Optional[str]:
    """Returns the title of the currently active window."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == 0:
            return None
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return None
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception as e:
        logger.debug(f"Failed to get active window: {e}")
        return None


def minimize_all_windows() -> bool:
    """Minimizes all windows (Show Desktop)."""
    try:
        # Use shell command through ctypes
        ctypes.windll.user32.ShowShellDesktop(0)
        return True
    except Exception:
        # Fallback: minimize all via keyboard shortcut
        try:
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Win key
            ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # D
            ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # D key up
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Win key up
            return True
        except Exception as e:
            logger.error(f"Failed to minimize all windows: {e}")
            return False


