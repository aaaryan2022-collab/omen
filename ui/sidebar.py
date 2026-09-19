# ============================================
"""
Navigation sidebar with futuristic styling.
"""

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel,
    QSizePolicy, QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.styles.palette import PRIMARY, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_MEDIUM, FONT_SIZE_MEDIUM, FONT_SIZE_DEFAULT, SPACING_DEFAULT, SPACING_LARGE


class Sidebar(QWidget):
    """
    Navigation sidebar with page switching signals.
    """

    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setMinimumHeight(400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_DEFAULT, SPACING_LARGE, SPACING_DEFAULT, SPACING_DEFAULT)
        layout.setSpacing(SPACING_DEFAULT)

        # Header / Brand
        header_layout = QHBoxLayout()
        header_label = QLabel("OMEN")
        header_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {PRIMARY}; font-size: 24pt;")
        header_layout.addWidget(header_label)
        layout.addLayout(header_layout)

        subtitle = QLabel("AI Assistant")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9pt; padding-left: 4px;")
        layout.addWidget(subtitle)
        layout.addSpacing(SPACING_LARGE)

        # Navigation items
        self._nav_list = QListWidget()
        self._nav_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._nav_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {BACKGROUND_MEDIUM};
                border: none;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 0;
                color: {TEXT_SECONDARY};
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 212, 170, 0.15);
                color: {PRIMARY};
                border-left: 3px solid {PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: #1A2035;
                color: {TEXT_PRIMARY};
            }}
        """)
        self._nav_list.setCurrentRow(-1)
        self._nav_list.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self._nav_list)

        self._populate_items()

    def _populate_items(self):
        items = [
            ("Dashboard", "dashboard"),
            ("Chat", "chat"),
            ("Tasks", "tasks"),
            ("Reminders", "reminders"),
            ("Emails", "emails"),
            ("News", "news"),
            ("Memory", "memory"),
            ("Activity", "activity"),
            ("Settings", "settings"),
        ]
        for label, page_id in items:
            item = QListWidgetItem(f"  {label}")
            item.setData(Qt.UserRole, page_id)
            self._nav_list.addItem(item)

    def _on_nav_changed(self, row: int):
        item = self._nav_list.item(row)
        if item:
            page_id = item.data(Qt.UserRole)
            self.page_changed.emit(page_id)

    def set_active_page(self, page_id: str):
        for i in range(self._nav_list.count()):
            item = self._nav_list.item(i)
            if item and item.data(Qt.UserRole) == page_id:
                self._nav_list.setCurrentRow(i)
                break


