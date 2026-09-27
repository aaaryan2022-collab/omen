"""Explicit, permission-gated mouse and keyboard controls."""

from pydantic import BaseModel, Field

from app.constants import RiskLevel
from automation.keyboard import send_keys
from automation.mouse import click_mouse, move_mouse
from tools.base import BaseTool, ToolResult


class CursorArgs(BaseModel):
    x: int = Field(ge=0, description="Horizontal screen coordinate")
    y: int = Field(ge=0, description="Vertical screen coordinate")


class ClickArgs(CursorArgs):
    button: str = Field(default="left", pattern="^(left|right|middle)$")


class TypeTextArgs(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class MoveCursorTool(BaseTool):
    name = "move_cursor"
    description = "Moves the mouse cursor to an exact screen coordinate. Requires confirmation."
    risk_level = RiskLevel.HIGH
    permission_tag = "desktop_automation"
    args_schema = CursorArgs

    def execute(self, x: int, y: int, **kwargs) -> ToolResult:
        try:
            success = move_mouse(x, y)
            return ToolResult(success=success, data={"x": x, "y": y}, message=f"Cursor moved to ({x}, {y}).")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), message="Cursor movement failed.")


class ClickMouseTool(BaseTool):
    name = "click_mouse"
    description = "Clicks at an exact screen coordinate. Requires confirmation."
    risk_level = RiskLevel.HIGH
    permission_tag = "desktop_automation"
    args_schema = ClickArgs

    def execute(self, x: int, y: int, button: str = "left", **kwargs) -> ToolResult:
        try:
            success = click_mouse(x, y, button)
            return ToolResult(success=success, data={"x": x, "y": y, "button": button}, message=f"Clicked at ({x}, {y}).")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), message="Mouse click failed.")


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "Types text into the currently focused application. Requires confirmation."
    risk_level = RiskLevel.HIGH
    permission_tag = "desktop_automation"
    args_schema = TypeTextArgs

    def execute(self, text: str, **kwargs) -> ToolResult:
        try:
            success = send_keys(text)
            return ToolResult(success=success, data={"length": len(text)}, message="Text entered.")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), message="Text entry failed.")