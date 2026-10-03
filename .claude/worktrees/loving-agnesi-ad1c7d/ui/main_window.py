"""Main OMEN window with sidebar, main assistant, and status bar."""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QSplitter, QStatusBar
)
from ui.app_shell import AppShell
from ui.components.main_assistant import MainAssistant


class OMENWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 600)
        self.setWindowTitle("OMEN - Personal AI Assistant")

        # Main layout
        container = QHBoxLayout()
        self.setLayout(container)

        # Sidebar
        self.sidebar = AppShell.sidebar
        self.sidebar.toggle_requested.connect(self._toggle_maximized)
        self.sidebar.nav_changed.connect(self._navigate)

        # Main area
        self.main_assistant = MainAssistant()
        self.conversation = self.main_assistant.conversation

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("OMEN Ready")

        # Layout structure
        container.addWidget(self.sidebar)
        main_split = QSplitter()
        self.main_area = QHBoxLayout()
        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.main_assistant)
        self.layout_main.addWidget(self.conversation)
        container.addLayout(self.layout_main)

        self.setCentralWidget(self)
        self.status_bar.showMessage("OMEN Initialized")

    def _toggle_maximized(self):
        # This would toggle between sidebar-only and full view
        pass

    def _navigate(self, key):
        # Handle navigation between sections
        pass