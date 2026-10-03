# ============================================
"""
Premium navigation sidebar — compact, editorial, human-crafted.
Collapsed/expanded states, subtle hover, dark charcoal + steel blue.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor
from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, TEXT_PRIMARY, TEXT_SECONDARY,
    BACKGROUND_DARK, BACKGROUND_MEDIUM, BACKGROUND_CARD,
    BORDER, BORDER_ACTIVE, TEXT_DIM, FONT_FAMILY, FONT_MONO
)


class Sidebar(QWidget):
    """Premium compact sidebar with OMEN orb and navigation."""

    page_changed = Signal(str)

    NAV_ITEMS = [
        ("dashboard", "Command Deck", "⚡"),
        ("chat", "Chat Matrix", "💬"),
        ("tasks", "Tasks", "📋"),
        ("reminders", "Reminders", "⏰"),
        ("vision", "Vision", "👁"),
        ("activity", "Activity", "📊"),
        ("settings", "Settings", "⚙"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QWidget {{
                background: {BACKGROUND_DARK};
                border-right: 1px solid {BORDER};
            }}
            QLabel {{
                color: {TEXT_SECONDARY};
                font-family: {FONT_FAMILY};
                font-size: 11px;
            }}
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                text-align: left;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 13px;
                font-family: {FONT_FAMILY};
                border: none;
            }}
            QPushButton:hover {{
                background: {BACKGROUND_MEDIUM};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {BACKGROUND_CARD};
            }}
            QPushButton:checked {{
                background: {PRIMARY_DIM};
                color: {PRIMARY};
                font-weight: 600;
                border-left: 2px solid {PRIMARY};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 16, 12, 16)
        lay.setSpacing(6)

        # OMEN Orb + Title
        top = QWidget()
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(0, 0, 0, 0)
        top_lay.setSpacing(10)

        self.orb = QLabel("◉")
        self.orb.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        self.orb.setStyleSheet(f"color: {PRIMARY}; letter-spacing: -2px;")
        top_lay.addWidget(self.orb)

        title = QLabel("OMEN")
        title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: 1.5px;")
        top_lay.addWidget(title)

        lay.addWidget(top)
        lay.addSpacing(8)

        # Status badge
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY_DIM};
                border: 1px solid {PRIMARY};
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """)
        s_lay = QHBoxLayout(status_frame)
        s_lay.setContentsMargins(8, 4, 8, 4)
        s_lay.setSpacing(6)
        s_dot = QLabel("●")
        s_dot.setStyleSheet(f"color: {SUCCESS}; font-size: 8pt;")
        s_text = QLabel("SYSTEM READY")
        s_text.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 8pt; font-weight: 600; letter-spacing: 1px;")
        s_lay.addWidget(s_dot)
        s_lay.addWidget(s_text)
        s_lay.addStretch()
        lay.addWidget(status_frame)
        lay.addSpacing(12)

        # Navigation items
        self._nav_buttons = {}
        for page_id, label, icon in self.NAV_ITEMS:
            btn = QPushButton(f"{icon}  {label}")
            btn.setProperty("pageId", page_id)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda _, pid=page_id: self.page_changed.emit(pid))
            self._nav_buttons[page_id] = btn
            lay.addWidget(btn)

        lay.addStretch()

        # Collapse/expand hint
        hint = QLabel("Ctrl+B to collapse")
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-family: {FONT_MONO}; font-size: 9px;")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)

        # Set first as default
        self._nav_buttons["dashboard"].setChecked(True)

    def set_active_page(self, page_id: str):
        for pid, btn in self._nav_buttons.items():
            btn.setChecked(pid == page_id)


class CollapsedSidebar(QWidget):
    """Ultra-compact collapsed state — icons only."""

    page_changed = Signal(str)
    expand_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(56)
        self.setStyleSheet(f"""
            QWidget {{ background: {BACKGROUND_DARK}; border-right: 1px solid {BORDER}; }}
            QPushButton {{ background: transparent; color: {TEXT_SECONDARY};
                border-radius: 8px; font-size: 16px; padding: 12px 0; border: none; }}
            QPushButton:hover {{ background: {BACKGROUND_MEDIUM}; color: {TEXT_PRIMARY}; }}
            QPushButton:checked {{ background: {PRIMARY_DIM}; color: {PRIMARY}; }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 12, 4, 12)
        lay.setSpacing(4)

        # Orb only
        orb = QLabel("◉")
        orb.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        orb.setStyleSheet(f"color: {PRIMARY};")
        orb.setAlignment(Qt.AlignCenter)
        lay.addWidget(orb)
        lay.addSpacing(8)

        for page_id, label, icon in Sidebar.NAV_ITEMS:
            btn = QPushButton(icon)
            btn.setProperty("pageId", page_id)
            btn.setCheckable(True)
            btn.setFixedSize(40, 40)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setToolTip(label)
            btn.clicked.connect(lambda _, pid=page_id: self.page_changed.emit(pid))
            lay.addWidget(btn, alignment=Qt.AlignHCenter)

        lay.addStretch()

        # Expand button
        expand = QPushButton("⌘")
        expand.setFixedSize(40, 40)
        expand.setToolTip("Expand sidebar (Ctrl+B)")
        expand.clicked.connect(self.expand_requested.emit)
        lay.addWidget(expand, alignment=Qt.AlignHCenter)