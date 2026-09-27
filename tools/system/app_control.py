# ============================================
"""
Application launcher and process manager for Windows desktop.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict
from pydantic import BaseModel, Field
import psutil
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel, DEFAULT_APP_ALIASES
from app.config import config
from app.logging_config import logger


class OpenAppArgs(BaseModel):
    application: str = Field(description="Name or alias of application to launch (e.g., 'chrome', 'code', 'notepad')")
    path_or_args: Optional[str] = Field(default=None, description="Optional file path or argument to pass to app")


class CloseAppArgs(BaseModel):
    application: str = Field(description="Name or process name of application to close (e.g., 'chrome', 'notepad.exe')")


class OpenApplicationTool(BaseTool):
    name = "open_application"
    description = "Launches an application or opens a project/file in a specific program (e.g. Chrome, VS Code, Notepad)."
    risk_level = RiskLevel.LOW
    args_schema = OpenAppArgs

    def execute(self, application: str, path_or_args: Optional[str] = None, **kwargs) -> ToolResult:
        app_clean = application.strip().lower()
        cmd = config.app_aliases.get(app_clean, application)

        try:
            # Build execution command
            full_cmd = [cmd]
            if path_or_args:
                full_cmd.append(path_or_args)

            # Use os.startfile or subprocess safely
            if hasattr(os, "startfile") and (os.path.exists(cmd) or (path_or_args and os.path.exists(path_or_args))):
                if path_or_args and os.path.exists(path_or_args):
                    os.startfile(path_or_args)
                else:
                    os.startfile(cmd)
            elif shutil.which(cmd) is not None or os.path.exists(cmd):
                subprocess.Popen(full_cmd, shell=False)
            else:
                # Try Windows shell execution with argument list
                subprocess.Popen(["cmd.exe", "/c", "start", "", *full_cmd], shell=False)

            logger.info(f"Opened application: {application} ({cmd})")
            return ToolResult(
                success=True,
                data={"application": application, "command": cmd},
                message=f"Successfully opened {application}."
            )
        except Exception as e:
            logger.error(f"Failed to open application '{application}': {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Could not open {application}. Ensure it is installed or configure its path in Settings."
            )


class CloseApplicationTool(BaseTool):
    name = "close_application"
    description = "Closes a running desktop application or terminates its processes gracefully."
    risk_level = RiskLevel.MEDIUM
    args_schema = CloseAppArgs

    def execute(self, application: str, **kwargs) -> ToolResult:
        target = application.strip().lower()
        if target.endswith(".exe"):
            target = target[:-4]

        closed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = (proc.info['name'] or "").lower()
                if target in proc_name:
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            return ToolResult(
                success=True,
                data={"closed_count": closed_count},
                message=f"Closed {closed_count} process(es) matching '{application}'."
            )
        return ToolResult(
            success=False,
            message=f"No running processes found matching '{application}'."
        )


