"""Comprehensive UI unit and integration tests for OMEN Desktop Assistant."""

import os
import pytest
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure single QApplication instance across tests
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_omen_orb_states(qapp):
    from ui.orb import OmenOrb
    orb = OmenOrb(size=120)
    for state in ["idle", "listening", "thinking", "speaking", "processing", "error"]:
        orb.set_state(state)
        assert orb._state == state
    orb.set_voice_level(0.75)
    assert orb._voice_level == 0.75
    orb._tick()


def test_toast_notification(qapp):
    from ui.toast import ToastNotification, ToastManager
    from PySide6.QtWidgets import QWidget
    parent = QWidget()
    parent.resize(800, 600)
    toast = ToastNotification("Task created", level="success", parent=parent)
    toast.show_toast()
    ToastManager.show(parent, "Test message", level="info")
    assert len(ToastManager._active_toasts) >= 1


def test_command_palette(qapp):
    from ui.command_palette import CommandPalette
    pal = CommandPalette()
    assert pal._list_widget.count() > 0
    # Test filtering
    pal._filter_actions("Tasks")
    assert pal._list_widget.count() >= 1
    # Test query fallback
    pal._filter_actions("custom prompt for omen")
    first_item = pal._list_widget.item(0)
    data = first_item.data(Qt.ItemDataRole.UserRole)
    assert data["id"] == "ask_prompt"
    assert data["query"] == "custom prompt for omen"


def test_mini_widget(qapp):
    from ui.mini_widget import MiniWidget
    widget = MiniWidget()
    widget.set_state("listening")
    assert "Listening" in widget._status_label.text()
    widget.set_state("thinking")
    assert "Thinking" in widget._status_label.text()
    widget.set_state("idle")
    assert "Ready" in widget._status_label.text()


def test_voice_overlay(qapp):
    from ui.voice_overlay import VoiceOverlay
    overlay = VoiceOverlay()
    overlay.set_voice_state("listening")
    overlay.update_transcript("Hello OMEN")
    assert overlay._transcript_label.text() == "Hello OMEN"
    overlay.set_audio_level(0.5)


def test_sidebar(qapp):
    from ui.sidebar import Sidebar
    sidebar = Sidebar()
    assert sidebar.width() == 220
    # Test collapse toggle
    sidebar.toggle_collapsed()
    assert sidebar._is_collapsed is True
    assert sidebar.width() == 64
    sidebar.toggle_collapsed()
    assert sidebar._is_collapsed is False
    assert sidebar.width() == 220

    # Test active page switch
    sidebar.set_active_page("calendar")
    assert sidebar._active_page == "calendar"


def test_assistant_view(qapp):
    from ui.chat import AssistantView
    view = AssistantView()
    assert view._is_in_conversation is False
    assert not view._idle_section.isHidden()
    assert view._stream_section.isHidden()

    # Test quick action click transitions to conversation
    view._on_quick_action_clicked("Plan my day")
    assert view._is_in_conversation is True
    assert view._idle_section.isHidden()
    assert not view._stream_section.isHidden()

    # Test response rendering with code block
    sample_response = "Here is Python code:\n```python\nprint('OMEN online')\n```\nAll done."
    view.add_omen_response(sample_response, tools=[{"tool": "list_files", "status": "COMPLETED"}])
    assert view._stream_layout.count() >= 1

    # Test reset to idle
    view.reset_to_idle()
    assert view._is_in_conversation is False
    assert not view._idle_section.isHidden()
    assert view._stream_section.isHidden()


def test_tasks_view(qapp):
    from ui.views.tasks_view import TasksView
    tasks_view = TasksView()
    tasks_view._quick_input.setText("Test smoke task priority high")
    tasks_view._create_task()
    tasks_view._set_tab("today")
    assert tasks_view._current_tab == "today"
    tasks_view._set_tab("upcoming")
    assert tasks_view._current_tab == "upcoming"
    tasks_view._set_tab("completed")
    assert tasks_view._current_tab == "completed"


def test_calendar_view(qapp):
    from ui.views.calendar_view import CalendarView
    cal = CalendarView()
    initial_count = len(cal._events)
    cal._input_title.setText("New test meeting at 3pm")
    cal._add_event()
    assert len(cal._events) == initial_count + 1


def test_notes_view(qapp):
    from ui.views.notes_view import NotesView
    notes = NotesView()
    initial_count = len(notes._notes)
    notes._create_new_note()
    assert len(notes._notes) == initial_count + 1
    notes._title_edit.setText("Updated Title")
    notes._save_current_note()
    assert notes._notes[0]["title"] == "Updated Title"


def test_files_view(qapp):
    from ui.views.files_view import FilesView
    files = FilesView()
    assert files._files_list.count() > 0


def test_system_view(qapp):
    from ui.views.system_view import SystemView
    sys_view = SystemView()
    sys_view._refresh_stats()
    assert sys_view._card_cpu._value_lbl.text() != ""
    assert sys_view._card_ram._value_lbl.text() != ""


def test_main_window_assembly(qapp):
    from ui.main_window import MainWindow
    from core.agent import Agent
    agent = Agent()
    window = MainWindow(agent)
    assert window._stack.count() == 7
    window._switch_page("tasks")
    assert window._stack.currentWidget() == window._tasks_view
    window._switch_page("calendar")
    assert window._stack.currentWidget() == window._calendar_view
    window._switch_page("chat")
    assert window._stack.currentWidget() == window._assistant_view

    # Test mini mode transition
    window._toggle_mini_mode()
    assert not window.isVisible()
    assert window._mini_widget.isVisible()
    window._restore_from_mini()
    assert not window._mini_widget.isVisible()
