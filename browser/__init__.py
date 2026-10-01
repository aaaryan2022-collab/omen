"""Browser automation layer — DOM-first, visual fallback."""
from typing import Optional, Dict, Any, List
import webbrowser
from urllib.parse import quote_plus

from app.logging_config import logger


class BrowserAutomation:
    """DOM-aware browser operations; falls back to visual interaction."""

    def __init__(self):
        self._playwright_available = False
        try:
            import playwright
            self._playwright_available = True
        except ImportError:
            pass

    def open_url(self, url: str) -> bool:
        try:
            webbrowser.open_new_tab(url)
            return True
        except Exception as exc:
            logger.error(f"Browser open failed: {exc}")
            return False

    def search(self, query: str, engine: str = "https://www.google.com/search?q=") -> bool:
        return self.open_url(engine + quote_plus(query))

    def get_page_text(self) -> Optional[str]:
        if self._playwright_available:
            # Placeholder for Playwright page text extraction
            return "Playwright page extraction not wired yet."
        return None

    def click_element(self, selector: str) -> bool:
        if self._playwright_available:
            # Placeholder
            return False
        return False

    def type_into(self, selector: str, text: str) -> bool:
        if self._playwright_available:
            return False
        return False

    def navigate_back(self) -> bool:
        import pyautogui
        pyautogui.hotkey("alt", "left")
        return True

    def navigate_forward(self) -> bool:
        import pyautogui
        pyautogui.hotkey("alt", "right")
        return True

    def refresh(self) -> bool:
        import pyautogui
        pyautogui.hotkey("f5")
        return True