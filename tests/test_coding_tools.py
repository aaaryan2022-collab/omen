import os
import tempfile
import pytest
from tools.coding.checkpoint_store import CheckpointStore
from tools.coding.apply_patch import ApplyPatchTool
from tools.coding.terminal_runner import TerminalRunTool
from tools.coding.git_tool import GitTool
from tools.coding.codebase_indexer import CodebaseSearchTool


def test_checkpoint_and_apply_patch():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "sample.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("def hello():\n    print('old')\n")

        tool = ApplyPatchTool()
        res = tool.execute(
            file_path=test_file,
            target_content="print('old')",
            replacement_content="print('new')"
        )
        assert res.success is True
        with open(test_file, "r", encoding="utf-8") as f:
            new_content = f.read()
        assert "print('new')" in new_content
        assert res.data["checkpoint_id"] is not None


def test_terminal_runner():
    tool = TerminalRunTool()
    res = tool.execute(command="python -c \"print('OMEN_OK')\"")
    assert res.success is True
    assert "OMEN_OK" in res.data["stdout"]
    assert res.data["exit_code"] == 0


def test_codebase_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "findme.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# UNIQUE_TOKEN_12345\n")

        tool = CodebaseSearchTool()
        res = tool.execute(query="UNIQUE_TOKEN_12345", root_dir=tmpdir)
        assert res.success is True
        assert res.data["count"] >= 1
        assert "findme.py" in res.data["matches"][0]["file"]
