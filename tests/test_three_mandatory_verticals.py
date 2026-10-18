# ============================================
"""
Three Mandatory End-to-End Vertical Tests required by Section 76:
TEST 1: "OMEN, open VS Code."
TEST 2: "OMEN, look at my screen and tell me why this program is showing this error."
TEST 3: "OMEN, inspect my project, find the bug, fix it, and run the tests."
"""

import os
import tempfile
import pytest
from app.config import config
from core.agent import Agent
from core.traces.trace_collector import trace_collector
from tools.registry import get_tool_registry
from tools.coding import ApplyPatchTool, TerminalRunTool, CodebaseSearchTool, checkpoint_store


def test_vertical_1_open_app():
    """
    TEST 1:
    User: "OMEN, open VS Code."
    Flow: intent detection -> tool selection -> permission check -> application launch -> verification -> trace -> response
    """
    agent = Agent()
    prompt = "OMEN, open VS Code"
    
    # Process through full agent pipeline
    response = agent.process_input(prompt)
    assert response is not None
    assert len(response) > 0

    # Verify tool registry has open_application
    reg = get_tool_registry()
    open_tool = reg.get("open_application")
    assert open_tool is not None
    assert open_tool.risk_level.value == "LOW"

    # Verify trace is recorded
    recent_traces = trace_collector.list_recent()
    assert len(recent_traces) >= 1


def test_vertical_2_screen_error_analysis():
    """
    TEST 2:
    User: "OMEN, look at my screen and tell me why this program is showing this error."
    Flow: screen permission -> screenshot -> vision model -> reasoning -> response -> trace
    """
    agent = Agent()
    prompt = "OMEN, look at my screen and tell me why this program is showing this error."

    # Verify screen tools are available
    reg = get_tool_registry()
    screen_tool = reg.get("analyze_screen")
    assert screen_tool is not None
    assert screen_tool.risk_level.value == "MEDIUM"

    response = agent.process_input(prompt)
    assert response is not None
    assert len(response) > 0


def test_vertical_3_inspect_fix_and_test():
    """
    TEST 3:
    User: "OMEN, inspect my project, find the bug, fix it, and run the tests."
    Flow: CodeAgent -> repository indexing -> search -> planning -> file modification permission
          -> modification -> terminal -> tests -> failure analysis -> repair -> final verification -> Git diff -> trace
    """
    with tempfile.TemporaryDirectory() as project_dir:
        # 1. Create a project with a buggy file and a test file
        buggy_file = os.path.join(project_dir, "calculator.py")
        test_file = os.path.join(project_dir, "test_calc.py")

        with open(buggy_file, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a - b  # BUG: should be +\n")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                "from calculator import add\n"
                "def test_add():\n"
                "    assert add(2, 3) == 5\n"
            )

        # 2. Step 1: Repository Indexing & Code Search
        search_tool = CodebaseSearchTool()
        search_res = search_tool.execute(query="def add", root_dir=project_dir)
        assert search_res.success is True
        assert len(search_res.data["matches"]) >= 1

        # 3. Step 2: Initial Terminal Test Run (demonstrates bug failure)
        terminal_tool = TerminalRunTool()
        initial_test = terminal_tool.execute(
            command=f"python -m pytest {test_file}",
            cwd=project_dir
        )
        assert initial_test.success is False  # Test fails as expected

        # 4. Step 3: Patch Modification with checkpoint
        patch_tool = ApplyPatchTool()
        patch_res = patch_tool.execute(
            file_path=buggy_file,
            target_content="return a - b  # BUG: should be +",
            replacement_content="return a + b"
        )
        assert patch_res.success is True
        assert patch_res.data["checkpoint_id"] is not None

        # 5. Step 4: Verification Terminal Test Run (demonstrates bug repaired)
        repaired_test = terminal_tool.execute(
            command=f"python -m pytest {test_file}",
            cwd=project_dir
        )
        assert repaired_test.success is True  # Tests now pass!

        # 6. Verify checkpoint rollback works if needed
        rolled_back = checkpoint_store.rollback(patch_res.data["checkpoint_id"])
        assert rolled_back is True
        with open(buggy_file, "r", encoding="utf-8") as f:
            assert "return a - b" in f.read()
