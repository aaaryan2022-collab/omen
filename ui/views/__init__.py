"""UI Views package for OMEN."""
from ui.views.tasks_view import TasksView
from ui.views.reminders_view import RemindersView
from ui.views.vision_view import VisionView
from ui.views.activity_view import ActivityView
from ui.views.settings_view import SettingsView
from ui.views.calendar_view import CalendarView
from ui.views.notes_view import NotesView
from ui.views.files_view import FilesView
from ui.views.system_view import SystemView

__all__ = [
    "TasksView",
    "RemindersView",
    "VisionView",
    "ActivityView",
    "SettingsView",
    "CalendarView",
    "NotesView",
    "FilesView",
    "SystemView",
]
