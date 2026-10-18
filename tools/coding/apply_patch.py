# ============================================
"""
Unified Patch and Chunk Replacer for OMEN Coding Agent.
Applies unified diffs and precise search-and-replace chunks with automatic checkpointing.
"""

import os
import difflib
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger
from tools.coding.checkpoint_store import checkpoint_store


class ApplyPatchArgs(BaseModel):
    file_path: str = Field(..., description="Path to the file to modify")
    target_content: str = Field(..., description="Exact original code block to replace")
    replacement_content: str = Field(..., description="New code block to replace it with")
    create_if_missing: bool = Field(False, description="Whether to create the file if it does not exist")


class ApplyPatchTool(BaseTool):
    """Tool that safely applies replacement code blocks to files with automatic checkpointing."""

    name = "apply_patch"
    description = "Modifies a file by finding exact target code and replacing it with new code. Creates automatic checkpoints for undo."
    risk_level = RiskLevel.MEDIUM
    permission_tag = "fs.write"
    args_schema = ApplyPatchArgs

    def execute(
        self,
        file_path: str,
        target_content: str,
        replacement_content: str,
        create_if_missing: bool = False,
        **kwargs
    ) -> ToolResult:
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            if create_if_missing:
                try:
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                    with open(abs_path, "w", encoding="utf-8") as f:
                        f.write(replacement_content)
                    return ToolResult(
                        success=True,
                        message=f"Created new file {abs_path} with replacement content.",
                        data={"file_path": abs_path, "created": True}
                    )
                except Exception as e:
                    return ToolResult(success=False, error=str(e), message="Failed to create file.")
            return ToolResult(
                success=False,
                error=f"File not found: {abs_path}",
                message="Target file does not exist."
            )

        # Create checkpoint before modification
        cp_id = checkpoint_store.save_checkpoint(abs_path, f"Pre-patch modification")

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            if target_content not in content:
                # Try normalized line endings
                norm_target = target_content.replace("\r\n", "\n")
                norm_content = content.replace("\r\n", "\n")
                if norm_target not in norm_content:
                    return ToolResult(
                        success=False,
                        error="Target content could not be found exactly in the file.",
                        message="Target content mismatch. Ensure whitespace and line breaks match.",
                        data={"checkpoint_id": cp_id}
                    )
                # Replace with normalized
                new_content = norm_content.replace(norm_target, replacement_content.replace("\r\n", "\n"), 1)
            else:
                new_content = content.replace(target_content, replacement_content, 1)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return ToolResult(
                success=True,
                message=f"Successfully patched {os.path.basename(abs_path)}.",
                data={
                    "file_path": abs_path,
                    "checkpoint_id": cp_id,
                    "diff": "".join(difflib.unified_diff(
                        content.splitlines(True),
                        new_content.splitlines(True),
                        fromfile="before",
                        tofile="after"
                    ))
                }
            )
        except Exception as e:
            logger.error(f"Error in apply_patch: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to apply patch: {e}",
                data={"checkpoint_id": cp_id}
            )
