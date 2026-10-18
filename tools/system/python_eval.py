# ============================================
"""
Dynamic Python code execution tool for OMEN.
Allows OMEN to compute, process data, or perform ad-hoc scripts on the fly.
"""

import sys
import subprocess
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class ExecutePythonArgs(BaseModel):
    code: str = Field(description="Python code block to execute dynamically. Print outputs using print().")
    timeout_seconds: int = Field(default=30, ge=1, le=120, description="Execution timeout in seconds")


class ExecutePythonTool(BaseTool):
    name = "execute_python"
    description = "Executes arbitrary Python code in an isolated sub-process and captures stdout/stderr outputs."
    risk_level = RiskLevel.MEDIUM
    args_schema = ExecutePythonArgs

    def execute(self, code: str, timeout_seconds: int = 30, **kwargs) -> ToolResult:
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
                f.write(code)
                temp_path = Path(f.name)

            try:
                res = subprocess.run(
                    [sys.executable, str(temp_path)],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
                output = res.stdout
                error = res.stderr
                success = (res.returncode == 0)

                return ToolResult(
                    success=success,
                    data={"stdout": output, "stderr": error, "exit_code": res.returncode},
                    message=(output if output.strip() else error) if (output or error) else "Execution finished with no output.",
                    error=error if not success else None
                )
            finally:
                if temp_path.exists():
                    temp_path.unlink()
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Python execution timed out after {timeout_seconds} seconds.",
                message="Execution timed out."
            )
        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to execute Python code: {e}"
            )
