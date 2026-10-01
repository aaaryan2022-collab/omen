# ============================================
"""
Navigation sidebar with futuristic cyberpunk OMEN styling.
"""

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel,
    QSizePolicy, QHBoxLayout, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from ui.styles.palette import PRIMARY, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_MEDIUM, SUCCESS


class Sidebar(QWidget):
    """Futuristic navigation sidebar with holographic page routing."""

    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self.setMinimumHeight(500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(12)

        # Header / Brand Section
        brand_box = QVBoxLayout()
        header_label = QLabel("◉ OMEN")
        header_label.setObjectName("brandLabel")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {PRIMARY}; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #A355FF); font-size: 18pt; font-weight: 900; letter-spacing: 4px;")
        brand_box.addWidget(header_label)

        subtitle = QLabel("ARTIFICIAL INTELLIGENCE")
        subtitle.setObjectName("brandSubtitle")
        brand_box.addWidget(subtitle)
        layout.addLayout(brand_box)

        # Status badge
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 255, 157, 0.08);
                border: 1px solid rgba(0, 255, 157, 0.25);
                border-radius: 6px;
                padding: 4px 8px;
            }
        """)
        s_layout = QHBoxLayout(status_frame)
        s_layout.setContentsMargins(4, 2, 4, 2)
        s_dot = QLabel("●")
        s_dot.setStyleSheet(f"color: {SUCCESS}; font-size: 8pt;")
        s_text = QLabel("SYSTEM ARMED")
        s_text.setStyleSheet("color: #F1F5F9; font-size: 8pt; font-weight: bold; letter-spacing: 1px;")
        s_layout.addWidget(s_dot)
        s_layout.addWidget(s_text)
        s_layout.addStretch()
        layout.addWidget(status_frame)
        layout.addSpacing(8)

        # Navigation items list
        self._nav_list = QListWidget()
        self._nav_list.setObjectName("navList")
        self._nav_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._nav_list.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self._nav_list)

        self._populate_items()
        self._nav_list.setCurrentRow(0)

    def _populate_items(self):
        items = [
            ("⚡  Command Deck", "dashboard"),
            ("💬  Chat Matrix", "chat"),
            ("📋  Operational Tasks", "tasks"),
            ("⏰  Alarms & Reminders", "reminders"),
            ("👁  Vision Perception", "vision"),
            ("📊  Telemetry & Logs", "activity"),
            ("⚙  Settings & Persona", "settings"),
        ]
        for label, page_id in items:
            item = QListWidgetItem(f" {label}")
            item.setData(Qt.ItemDataRole.UserRole, page_id)
            self._nav_list.addItem(item)

    def _on_nav_changed(self, row: int):
        item = self._nav_list.item(row)
        if item:
            page_id = item.data(Qt.ItemDataRole.UserRole)
            self.page_changed.emit(page_id)

    def set_active_page(self, page_id: str):
        for i in range(self._nav_list.count()):
            item = self._nav_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == page_id:
                self._nav_list.setCurrentRow(i)
                break
