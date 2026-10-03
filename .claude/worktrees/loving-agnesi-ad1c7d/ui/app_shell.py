"""AppShell — premium dark layout with sidebar + main workspace + status bar."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QStatusBar
from PySide6.QtCore import Qt

from ui.components.sidebar import Sidebar
from ui.design.tokens import BG, BORDER


class AppShell(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self.setWindowTitle("OMEN — Personal AI Assistant")
        self.layout_main = QHBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.layout_main.addWidget(self.sidebar)

        # Main workspace container
        self.main_area = QWidget()
        self.main_area.setStyleSheet(f"background: {BG};")
        self.layout_main.addWidget(self.main_area)
