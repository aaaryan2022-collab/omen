# ============================================
"""
Terminal Command Runner for OMEN Coding Agent.
Executes shell commands with timeout, exit code capture, and working directory control.
"""

import subprocess
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class TerminalRunArgs(BaseModel):
    command: str = Field(..., description="The shell command to execute")
    cwd: Optional[str] = Field(None, description="Working directory for the command execution")
    timeout_seconds: int = Field(60, description="Maximum execution time in seconds")


class TerminalRunTool(BaseTool):
    """Executes a terminal command safely and returns stdout, stderr, and exit code."""

    name = "terminal_run"
    description = "Executes a shell command in the operating system terminal with timeout and output capture."
    risk_level = RiskLevel.HIGH
    permission_tag = "terminal"
    args_schema = TerminalRunArgs

    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout_seconds: int = 60,
        **kwargs
    ) -> ToolResult:
        work_dir = os.path.abspath(cwd) if cwd else os.getcwd()
        if not os.path.isdir(work_dir):
            return ToolResult(
                success=False,
                error=f"Working directory does not exist: {work_dir}",
                message="Invalid working directory."
            )

        # Block dangerously destructive raw commands
        lower_cmd = command.lower().strip()
        blocked_commands = ["format c:", "rmdir /s /q c:\\", "del /f /s /q c:\\"]
        if any(b in lower_cmd for b in blocked_commands):
            return ToolResult(
                success=False,
                error="Command blocked by safety boundary: Destructive system drive modification.",
                message="Execution blocked by security policy."
            )

        try:
            logger.info(f"Executing terminal command: '{command}' in {work_dir}")
            res = subprocess.run(
                command,
                cwd=work_dir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            success = (res.returncode == 0)
            output = res.stdout
            if res.stderr:
                output += ("\n[STDERR]\n" + res.stderr)

            return ToolResult(
                success=success,
                message=f"Command finished with exit code {res.returncode}.",
                data={
                    "command": command,
                    "exit_code": res.returncode,
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                    "cwd": work_dir
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {timeout_seconds} seconds.",
                message="Execution timed out."
            )
        except Exception as e:
            logger.error(f"Error running command '{command}': {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to execute command: {e}"
            )
