# ============================================
"""
Hotkey and keyboard control tools for OMEN.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from automation.keyboard import press_hotkey, key_event_simple, press_enter
from app.logging_config import logger


class SendHotkeyArgs(BaseModel):
    keys: List[str] = Field(
        description="List of keys to press simultaneously (e.g., ['ctrl', 'c'], ['alt', 'tab'], ['win', 'd'], ['ctrl', 'shift', 'esc'])"
    )


class PressKeyArgs(BaseModel):
    key: str = Field(description="Single key name to press (e.g., 'enter', 'esc', 'tab', 'backspace', 'up', 'down', 'f5')")


class SendHotkeyTool(BaseTool):
    name = "send_hotkey"
    description = "Triggers a keyboard shortcut by pressing multiple keys together (e.g. ['ctrl', 'v'], ['alt', 'tab'], ['ctrl', 's'])."
    risk_level = RiskLevel.MEDIUM
    permission_tag = "desktop_automation"
    args_schema = SendHotkeyArgs

    def execute(self, keys: List[str], **kwargs) -> ToolResult:
        try:
            if not keys:
                return ToolResult(success=False, message="No keys specified for hotkey.")
            clean_keys = [k.strip().lower() for k in keys]
            success = press_hotkey(*clean_keys)
            key_combo = "+".join(clean_keys)
            return ToolResult(
                success=success,
                data={"keys": clean_keys},
                message=f"Pressed hotkey combo: {key_combo}" if success else "Hotkey execution aborted by safety."
            )
        except Exception as e:
            logger.error(f"Failed to execute hotkey {keys}: {e}")
            return ToolResult(success=False, error=str(e), message=f"Hotkey execution failed: {e}")


class PressKeyTool(BaseTool):
    name = "press_key"
    description = "Presses a single key on the keyboard (e.g. 'enter', 'escape', 'tab', 'space', 'f5')."
    risk_level = RiskLevel.LOW
    permission_tag = "desktop_automation"
    args_schema = PressKeyArgs

    def execute(self, key: str, **kwargs) -> ToolResult:
        try:
            clean_key = key.strip().lower()
            if clean_key in ("enter", "return"):
                success = press_enter()
            else:
                success = key_event_simple(clean_key)
            return ToolResult(
                success=success,
                data={"key": clean_key},
                message=f"Pressed key: {clean_key}" if success else "Key press aborted by safety."
            )
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            return ToolResult(success=False, error=str(e), message=f"Failed to press key: {e}")
