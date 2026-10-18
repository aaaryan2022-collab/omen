# ============================================
"""
Codebase Indexer for OMEN.
Scans project directory respecting .gitignore, extracts symbols and performs fast code search.
"""

import os
import re
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


def load_gitignore_patterns(root_dir: str) -> Set[str]:
    patterns = {".git", "__pycache__", "node_modules", ".pytest_cache", "venv", ".venv", "dist", "build", ".omen"}
    gi_path = os.path.join(root_dir, ".gitignore")
    if os.path.isfile(gi_path):
        try:
            with open(gi_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line.rstrip("/"))
        except Exception:
            pass
    return patterns


def is_ignored(rel_path: str, patterns: Set[str]) -> bool:
    parts = rel_path.replace("\\", "/").split("/")
    for p in parts:
        if p in patterns or any(pat in p for pat in [".pyc", ".egg-info"]):
            return True
    return False


class CodebaseSearchArgs(BaseModel):
    query: str = Field(..., description="Text query, symbol name, or regex pattern to search for")
    root_dir: Optional[str] = Field(None, description="Root directory to search inside")
    file_extension: Optional[str] = Field(None, description="Optional extension filter (e.g. '.py', '.ts')")


class CodebaseSearchTool(BaseTool):
    """Searches code files within workspace respecting .gitignore."""

    name = "codebase_search"
    description = "Searches for text, function definitions, or patterns across the codebase respecting .gitignore."
    risk_level = RiskLevel.LOW
    permission_tag = "fs.read"
    args_schema = CodebaseSearchArgs

    def execute(
        self,
        query: str,
        root_dir: Optional[str] = None,
        file_extension: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        base_path = os.path.abspath(root_dir) if root_dir else os.getcwd()
        if not os.path.isdir(base_path):
            return ToolResult(success=False, error=f"Invalid search directory: {base_path}")

        patterns = load_gitignore_patterns(base_path)
        matches: List[Dict] = []
        max_matches = 50

        try:
            for root, dirs, files in os.walk(base_path):
                rel_root = os.path.relpath(root, base_path)
                if is_ignored(rel_root, patterns):
                    dirs[:] = []
                    continue

                for f in files:
                    if file_extension and not f.endswith(file_extension):
                        continue
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, base_path).replace("\\", "/")
                    if is_ignored(rel_p, patterns):
                        continue

                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as file_obj:
                            for idx, line in enumerate(file_obj, 1):
                                if query.lower() in line.lower():
                                    matches.append({
                                        "file": rel_p,
                                        "line": idx,
                                        "content": line.strip()[:200]
                                    })
                                    if len(matches) >= max_matches:
                                        break
                    except Exception:
                        continue
                    if len(matches) >= max_matches:
                        break
                if len(matches) >= max_matches:
                    break

            return ToolResult(
                success=True,
                message=f"Found {len(matches)} match(es) for '{query}'.",
                data={"query": query, "matches": matches, "count": len(matches)}
            )
        except Exception as e:
            logger.error(f"Error in codebase_search: {e}")
            return ToolResult(success=False, error=str(e), message="Search failed.")
