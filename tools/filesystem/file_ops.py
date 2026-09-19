# ============================================
"""
Safe File Operations and Document Readers with Sandboxing.
"""

from pathlib import Path
import os
import shutil
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from tools.base import BaseTool, ToolResult
from safety.permissions import get_permission_manager
from safety.safety import sanitize_external_content
from app.constants import RiskLevel, DATA_DIR
from app.logging_config import logger


class SearchFilesArgs(BaseModel):
    query: str = Field(description="Filename pattern or keyword to search for (e.g. '*.py', 'assignment', 'resume')")
    search_directory: Optional[str] = Field(default=None, description="Directory to search in (must be permitted)")
    max_results: int = Field(default=20, description="Max matching files to return")


class ReadFileArgs(BaseModel):
    file_path: str = Field(description="Full path to the file to read (TXT, PDF, DOCX, MD, PY, JSON, CSV)")
    max_lines: int = Field(default=200, description="Maximum lines or paragraphs to read")


class CreateFileArgs(BaseModel):
    file_path: str = Field(description="Destination file path to create")
    content: str = Field(description="Text content to write into the file")


class CreateFolderArgs(BaseModel):
    folder_path: str = Field(description="Directory path to create")


class FileTransferArgs(BaseModel):
    source_path: str = Field(description="Source file or directory path")
    destination_path: str = Field(description="Destination file or directory path")


class DeleteFileArgs(BaseModel):
    file_path: str = Field(description="Path of the file to delete (moves to recycle/trash)")


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Searches for files matching a pattern or name across permitted directories."
    risk_level = RiskLevel.LOW
    args_schema = SearchFilesArgs

    def execute(self, query: str, search_directory: Optional[str] = None, max_results: int = 20, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        search_dirs = [Path(search_directory).resolve()] if search_directory else [Path(d) for d in perm.get_allowed_directories()]

        # Filter only valid existing directories
        valid_dirs = []
        for d in search_dirs:
            if perm.is_path_allowed(d) and d.exists() and d.is_dir():
                valid_dirs.append(d)

        if not valid_dirs:
            return ToolResult(success=False, error="No accessible permitted directories to search.")

        results: List[Dict[str, Any]] = []
        pattern = query if ("*" in query or "?" in query) else f"*{query}*"

        for root_dir in valid_dirs:
            try:
                for match in root_dir.rglob(pattern):
                    if match.is_file():
                        stat = match.stat()
                        results.append({
                            "name": match.name,
                            "path": str(match.resolve()),
                            "size_kb": round(stat.st_size / 1024, 1),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        })
                        if len(results) >= max_results:
                            break
            except Exception as e:
                logger.warning(f"Error scanning directory {root_dir}: {e}")

            if len(results) >= max_results:
                break

        if results:
            summary = f"Found {len(results)} matching file(s):\n" + "\n".join([f"- {r['name']} ({r['path']})" for r in results[:10]])
            return ToolResult(success=True, data=results, message=summary)
        return ToolResult(success=True, data=[], message=f"No files found matching '{query}'.")


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads text and document contents (PDF, DOCX, TXT, MD, PY, JSON, CSV) from permitted paths."
    risk_level = RiskLevel.LOW
    args_schema = ReadFileArgs

    def execute(self, file_path: str, max_lines: int = 200, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            path = perm.validate_path(file_path)
            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {file_path}")
            if not path.is_file():
                return ToolResult(success=False, error=f"Path is not a file: {file_path}")

            suffix = path.suffix.lower()
            content = ""

            if suffix == ".pdf":
                # PDF parsing via pypdf
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(path))
                    pages_text = []
                    for i, page in enumerate(reader.pages[:10]):  # First 10 pages
                        txt = page.extract_text() or ""
                        if txt.strip():
                            pages_text.append(f"--- Page {i+1} ---\n{txt}")
                    content = "\n\n".join(pages_text)
                except Exception as e:
                    return ToolResult(success=False, error=f"Failed to extract PDF text: {e}")

            elif suffix in (".docx", ".doc"):
                # DOCX parsing via python-docx
                try:
                    import docx
                    doc = docx.Document(str(path))
                    content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()][:max_lines])
                except Exception as e:
                    return ToolResult(success=False, error=f"Failed to read DOCX: {e}")

            else:
                # Text-based file reading
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        lines = [f.readline() for _ in range(max_lines)]
                        content = "".join(lines)
                except Exception as e:
                    return ToolResult(success=False, error=f"Failed to read text file: {e}")

            sanitized = sanitize_external_content(content, source_type=f"File ({path.name})")
            return ToolResult(
                success=True,
                data={"path": str(path), "size_chars": len(content), "content": content},
                message=sanitized
            )

        except PermissionError as pe:
            return ToolResult(success=False, error=str(pe))
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CreateFileTool(BaseTool):
    name = "create_file"
    description = "Creates or writes a new text file at a permitted destination."
    risk_level = RiskLevel.MEDIUM
    args_schema = CreateFileArgs

    def execute(self, file_path: str, content: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            path = perm.validate_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(
                success=True,
                data={"path": str(path), "bytes_written": len(content.encode("utf-8"))},
                message=f"Created file: {path.name} ({str(path)})"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def verify(self, result: ToolResult, **kwargs) -> bool:
        if result.success and result.data and "path" in result.data:
            return Path(result.data["path"]).is_file()
        return False


class CreateFolderTool(BaseTool):
    name = "create_folder"
    description = "Creates a directory inside permitted paths."
    risk_level = RiskLevel.LOW
    args_schema = CreateFolderArgs

    def execute(self, folder_path: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            path = perm.validate_path(folder_path)
            path.mkdir(parents=True, exist_ok=True)
            return ToolResult(success=True, data={"path": str(path)}, message=f"Created folder: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class RenameFileTool(BaseTool):
    name = "rename_file"
    description = "Renames a file or folder inside permitted paths."
    risk_level = RiskLevel.MEDIUM
    args_schema = FileTransferArgs

    def execute(self, source_path: str, destination_path: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            src = perm.validate_path(source_path)
            dst = perm.validate_path(destination_path)
            if not src.exists():
                return ToolResult(success=False, error=f"Source does not exist: {src}")
            src.rename(dst)
            return ToolResult(success=True, message=f"Renamed '{src.name}' to '{dst.name}'.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class MoveFileTool(BaseTool):
    name = "move_file"
    description = "Moves a file or folder to a new location inside permitted paths."
    risk_level = RiskLevel.MEDIUM
    args_schema = FileTransferArgs

    def execute(self, source_path: str, destination_path: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            src = perm.validate_path(source_path)
            dst = perm.validate_path(destination_path)
            shutil.move(str(src), str(dst))
            return ToolResult(success=True, message=f"Moved '{src.name}' to '{dst}'.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CopyFileTool(BaseTool):
    name = "copy_file"
    description = "Copies a file or folder to a destination in permitted paths."
    risk_level = RiskLevel.LOW
    args_schema = FileTransferArgs

    def execute(self, source_path: str, destination_path: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            src = perm.validate_path(source_path)
            dst = perm.validate_path(destination_path)
            if src.is_dir():
                shutil.copytree(str(src), str(dst))
            else:
                shutil.copy2(str(src), str(dst))
            return ToolResult(success=True, message=f"Copied '{src.name}' to '{dst}'.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Moves a file to the OMEN quarantine trash folder safely. (HIGH risk, requires confirmation)"
    risk_level = RiskLevel.HIGH
    args_schema = DeleteFileArgs

    def execute(self, file_path: str, **kwargs) -> ToolResult:
        perm = get_permission_manager()
        try:
            src = perm.validate_path(file_path)
            if not src.exists():
                return ToolResult(success=False, error=f"File not found: {file_path}")

            # Safe quarantine trash directory
            trash_dir = DATA_DIR / "trash"
            trash_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_target = trash_dir / f"{timestamp}_{src.name}"

            shutil.move(str(src), str(trash_target))
            return ToolResult(
                success=True,
                data={"original": str(src), "quarantine": str(trash_target)},
                message=f"File '{src.name}' was safely moved to trash quarantine."
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


