# ============================================
"""
Git Management Tool for OMEN.
Executes status, diff, log, commit, checkout, branch operations.
"""

import subprocess
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class GitActionArgs(BaseModel):
    action: str = Field(..., description="Action: status, diff, log, commit, branch, checkout, add")
    repo_path: Optional[str] = Field(None, description="Path to repository root")
    args: Optional[str] = Field(None, description="Additional arguments (e.g. commit message, branch name, file path)")


class GitTool(BaseTool):
    """Tool for Git source control operations."""

    name = "git_action"
    description = "Performs Git repository actions (status, diff, log, commit, checkout, branch, add)."
    risk_level = RiskLevel.MEDIUM
    permission_tag = "git"
    args_schema = GitActionArgs

    def execute(
        self,
        action: str,
        repo_path: Optional[str] = None,
        args: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        cwd = os.path.abspath(repo_path) if repo_path else os.getcwd()
        action = action.lower().strip()

        cmd = ["git"]
        if action == "status":
            cmd += ["status", "--short"]
        elif action == "diff":
            cmd += ["diff"]
            if args:
                cmd.append(args)
        elif action == "log":
            cmd += ["log", "-n", "5", "--oneline"]
        elif action == "branch":
            cmd += ["branch"]
            if args:
                cmd.append(args)
        elif action == "checkout":
            if not args:
                return ToolResult(success=False, error="Branch name required for checkout.")
            cmd += ["checkout", args]
        elif action == "add":
            cmd += ["add", args or "."]
        elif action == "commit":
            if not args:
                return ToolResult(success=False, error="Commit message required.")
            cmd += ["commit", "-m", args]
        else:
            return ToolResult(success=False, error=f"Unsupported git action: {action}")

        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            success = (res.returncode == 0)
            output = res.stdout if success else res.stderr
            return ToolResult(
                success=success,
                message=f"git {action} completed.",
                data={"action": action, "output": output.strip(), "exit_code": res.returncode}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to execute git {action}")
