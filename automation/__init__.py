# ============================================
"""
Automation package — Windows, keyboard, mouse, screenshots.
"""

from automation.windows import get_all_windows, focus_window, minimize_window, get_active_window_title, minimize_all_windows, WindowInfo
from automation.keyboard import send_keys, press_hotkey, press_enter, key_event_simple
from automation.mouse import move_mouse, click_mouse, double_click, get_mouse_position, scroll_mouse
from automation.screenshots import capture_screen, capture_all_monitors, ScreenshotInfo


