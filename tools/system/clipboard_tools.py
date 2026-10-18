# ============================================
"""
Clipboard management tools for OMEN.
"""

import subprocess
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class SetClipboardArgs(BaseModel):
    text: str = Field(description="Text to copy to the Windows clipboard")


class GetClipboardTool(BaseTool):
    name = "get_clipboard"
    description = "Reads and returns the current text content stored on the Windows clipboard."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        try:
            # Use PowerShell Get-Clipboard
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            content = res.stdout.rstrip("\r\n")
            return ToolResult(
                success=True,
                data={"content": content, "length": len(content)},
                message=f"Clipboard read successfully ({len(content)} characters)."
            )
        except Exception as e:
            logger.error(f"Failed to read clipboard: {e}")
            return ToolResult(success=False, error=str(e), message="Failed to read Windows clipboard.")


class SetClipboardTool(BaseTool):
    name = "set_clipboard"
    description = "Copies text directly onto the Windows clipboard so it can be pasted anywhere."
    risk_level = RiskLevel.LOW
    args_schema = SetClipboardArgs

    def execute(self, text: str, **kwargs) -> ToolResult:
        try:
            # Pipe text to Set-Clipboard via powershell
            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(input=text, timeout=5)
            if proc.returncode == 0:
                return ToolResult(
                    success=True,
                    data={"length": len(text)},
                    message=f"Copied {len(text)} characters to the Windows clipboard."
                )
            return ToolResult(success=False, error=stderr, message="Failed to write to clipboard.")
        except Exception as e:
            logger.error(f"Failed to set clipboard: {e}")
            return ToolResult(success=False, error=str(e), message="Failed to set Windows clipboard.")
