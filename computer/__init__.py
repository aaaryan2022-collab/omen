"""Computer control layer — mouse, keyboard, window, app abstraction."""
from typing import Optional, Tuple, List, Dict, Any
import ctypes
from ctypes import wintypes
from ctypes import windll

from app.logging_config import logger

# Low-level Windows API for window enumeration
user32 = windll.user32


class ComputerControl:
    """Cross-tool computer control: mouse, keyboard, windows, apps."""

    def __init__(self):
        self._throttle = 0.1

    def move_mouse(self, x: int, y: int, duration: float = 0.0):
        import pyautogui
        pyautogui.moveTo(x, y, duration=duration)

    def click(self, button: str = "left", x: Optional[int] = None, y: Optional[int] = None):
        import pyautogui
        if x is not None and y is not None:
            self.move_mouse(x, y)
        pyautogui.click(button=button)

    def type(self, text: str):
        import pyautogui
        pyautogui.typewrite(text)

    def hotkey(self, keys: Tuple[str, ...]):
        import pyautogui
        pyautogui.hotkey(*keys)

    def list_windows(self) -> List[Dict[str, Any]]:
        windows: List[Dict[str, Any]] = []

        def enum_cb(hwnd: wintypes.HWND, lparam: wintypes.LPARAM) -> wintypes.BOOL:
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    windows.append({"hwnd": hwnd, "title": buff.value})
            return True

        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(callback_type(enum_cb), 0)
        return windows

    def get_active_window(self) -> Optional[Dict[str, Any]]:
        hwnd = user32.GetForegroundWindow()
        title = user32.GetWindowTextW(hwnd) if hwnd else ""
        return {"hwnd": hwnd, "title": title} if title else None

    def open_app(self, name: str) -> bool:
        import subprocess, os
        resolved = self._resolve_app_path(name)
        if resolved and os.path.isfile(resolved):
            subprocess.Popen(f'start "" "{resolved}"', shell=True)
            return True
        return False

    def _resolve_app_path(self, name: str) -> Optional[str]:
        paths = [
            f"C:\\Program Files\\{name}\\{name}.exe",
            f"C:\\Program Files (x86)\\{name}\\{name}.exe",
        ]
        for p in paths:
            if os.path.isfile(p):
                return p
        return None

    def screenshot_region(self, x: int, y: int, w: int, h: int):
        from mss import mss
        from PIL import Image
        with mss() as s:
            img = s.grab({"left": x, "top": y, "width": w, "height": h})
            return Image.frombytes("RGB", img.size, img.rgb)
