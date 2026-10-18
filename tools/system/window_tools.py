# ============================================
"""
Window management and switching tools for OMEN.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from automation.windows import (
    get_all_windows,
    get_window_by_title,
    focus_window,
    minimize_window,
    minimize_all_windows,
    get_active_window_title,
)
from app.logging_config import logger


class FocusWindowArgs(BaseModel):
    title: str = Field(description="Exact or partial window title to focus (e.g., 'Notepad', 'Chrome', 'Visual Studio Code')")


class MinimizeWindowArgs(BaseModel):
    title: str = Field(description="Exact or partial window title to minimize")


class ListWindowsTool(BaseTool):
    name = "list_windows"
    description = "Lists all currently visible desktop application windows with their titles and window handles."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            windows = get_all_windows()
            active_title = get_active_window_title()
            win_list = [
                {
                    "title": w.title,
                    "hwnd": w.hwnd,
                    "class_name": w.class_name,
                    "is_active": (w.title == active_title),
                }
                for w in windows
                if w.title and len(w.title.strip()) > 0
            ]
            return ToolResult(
                success=True,
                data={"windows": win_list, "count": len(win_list), "active_window": active_title},
                message=f"Found {len(win_list)} visible window(s). Active window: '{active_title}'."
            )
        except Exception as e:
            logger.error(f"Failed to list windows: {e}")
            return ToolResult(success=False, error=str(e), message="Failed to enumerate open windows.")


class FocusWindowTool(BaseTool):
    name = "focus_window"
    description = "Brings a specific open application window to the foreground and focuses it."
    risk_level = RiskLevel.LOW
    args_schema = FocusWindowArgs

    def execute(self, title: str, **kwargs) -> ToolResult:
        try:
            win = get_window_by_title(title)
            if not win:
                return ToolResult(
                    success=False,
                    message=f"No window found matching title '{title}'."
                )
            success = focus_window(win.hwnd)
            if success:
                return ToolResult(
                    success=True,
                    data={"hwnd": win.hwnd, "title": win.title},
                    message=f"Brought window '{win.title}' to the foreground."
                )
            return ToolResult(success=False, message=f"Failed to bring window '{title}' to focus.")
        except Exception as e:
            logger.error(f"Error focusing window '{title}': {e}")
            return ToolResult(success=False, error=str(e), message=f"Error focusing window: {e}")


class MinimizeWindowTool(BaseTool):
    name = "minimize_window"
    description = "Minimizes a specific window by partial title match."
    risk_level = RiskLevel.LOW
    args_schema = MinimizeWindowArgs

    def execute(self, title: str, **kwargs) -> ToolResult:
        try:
            win = get_window_by_title(title)
            if not win:
                return ToolResult(
                    success=False,
                    message=f"No window found matching title '{title}'."
                )
            success = minimize_window(win.hwnd)
            return ToolResult(
                success=success,
                data={"hwnd": win.hwnd, "title": win.title},
                message=f"Minimized window '{win.title}'." if success else f"Failed to minimize '{title}'."
            )
        except Exception as e:
            logger.error(f"Error minimizing window '{title}': {e}")
            return ToolResult(success=False, error=str(e), message=f"Error minimizing window: {e}")


class ShowDesktopTool(BaseTool):
    name = "show_desktop"
    description = "Minimizes all windows to reveal the desktop."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            success = minimize_all_windows()
            return ToolResult(
                success=success,
                message="Revealed desktop by minimizing all open windows."
            )
        except Exception as e:
            logger.error(f"Error showing desktop: {e}")
            return ToolResult(success=False, error=str(e), message="Failed to show desktop.")
