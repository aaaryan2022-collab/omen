"""
Test suite validating the new Marvel J.A.R.V.I.S.-tier capabilities for OMEN:
- Window management (list_windows, focus_window, minimize_window, show_desktop)
- Hotkey execution (send_hotkey, press_key)
- Clipboard interaction (get_clipboard, set_clipboard)
- Media controls (media_play_pause, media_next_track, media_prev_track, media_mute)
- Dynamic Python sandbox (execute_python)
"""

import pytest
from tools.registry import get_tool_registry


def test_registry_contains_jarvis_arsenal():
    registry = get_tool_registry()
    tool_names = [t.name for t in registry.list_all()]

    expected_tools = [
        "list_windows",
        "focus_window",
        "minimize_window",
        "show_desktop",
        "send_hotkey",
        "press_key",
        "get_clipboard",
        "set_clipboard",
        "media_play_pause",
        "media_next_track",
        "media_prev_track",
        "media_mute",
        "execute_python",
    ]

    for tool in expected_tools:
        assert tool in tool_names, f"Expected {tool} to be registered in OMEN tool registry."


def test_list_windows_execution():
    registry = get_tool_registry()
    tool = registry.get("list_windows")
    assert tool is not None
    res = tool.execute()
    assert res.success is True
    assert "windows" in res.data
    assert isinstance(res.data["windows"], list)


def test_clipboard_read_write():
    registry = get_tool_registry()
    set_tool = registry.get("set_clipboard")
    get_tool = registry.get("get_clipboard")
    assert set_tool is not None and get_tool is not None

    test_payload = "OMEN_JARVIS_PAYLOAD_TEST_12345"
    set_res = set_tool.execute(text=test_payload)
    assert set_res.success is True

    get_res = get_tool.execute()
    assert get_res.success is True
    assert get_res.data["content"] == test_payload


def test_execute_python_sandbox():
    registry = get_tool_registry()
    py_tool = registry.get("execute_python")
    assert py_tool is not None

    code = "print(sum([x * 2 for x in range(10)]))"
    res = py_tool.execute(code=code)
    assert res.success is True
    assert res.data["stdout"].strip() == "90"
