"""Sidebar — compact left panel with OMEN logo and navigation."""
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.design import BG, SURFACE, CARD, BORDER, ACCENT, ACCENT_DIM, TEXT, TEXT_DIM, R_SM, SHADOW
from ui.components.orb import AIOrb

NAV_ITEMS = [
    ("home", "Home"),
    ("assistant", "Assistant"),
    ("tasks", "Tasks"),
    ("calendar", "Calendar"),
    ("notes", "Notes"),
    ("files", "Files"),
    ("system", "System"),
    ("settings", "Settings"),
]


class Sidebar(QWidget):
    """Compact left sidebar with OMEN orb and navigation."""
    toggle_requested = Signal()
    nav_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QWidget {{
                background: {tokens.get('BG', BG)};
                border-right: 1px solid {tokens.get('BORDER', BORDER)};
            }}
            QPushButton {{
                background: transparent;
                color: {tokens.get('TEXT_DIM', TEXT_MUTED)};
                text-align: left;
                padding: 10px 14px;
                border-radius: {tokens.get('R_SM', 8)}px;
                font-size: 13px;
                font-family: {tokens.get('FONT', 'Inter')};
            }}
            QPushButton:hover {{
                background: {tokens.get('SURFACE', '#15151B')};
                color: {tokens.get('TEXT', '#ECECEE')};
            }}
            QPushButton:pressed {{
                background: {tokens.get('ELEVATED', '#1D1D24')};
            }}
            QPushButton.active {{
                background: {tokens.get('ACCENT_DIM', ACCENT_DIM)};
                color: {tokens.get('ACCENT', '#00D4FF')};
                font-weight: 600;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 20, 0, 0)
        lay.setSpacing(4)

        # OMEN Orb + title row
        top = QWidget()
        top_lay = QVBoxLayout(top)
        top_lay.setContentsMargins(16, 12, 16, 12)
        top_lay.setSpacing(6)

        self.orb = AIOrb()
        self.orb.setFixedSize(32, 32)
        top_lay.addWidget(self.orb, 0, Qt.AlignLeft)

        self.title = QLabel("OMEN")
        self.title.setFont(QFont(tokens.get('FONT', 'Inter'), 14, QFont.Weight.Bold))
        top_lay.addWidget(self.title)

        lay.addWidget(top)
        lay.addSpacing(12)

        # Navigation items
        for icon, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setProperty("navKey", icon)
            btn.setFixedHeight(36)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {tokens.get('TEXT_DIM', TEXT_MUTED)};
                    padding: 8px 12px;
                }}
                QPushButton:hover {{
                    background: {tokens.get('SURFACE', '#15151B')};
                    color: {tokens.get('TEXT', '#ECECEE')};
                }}
                QPushButton:checked {{
                    background: {tokens.get('ACCENT_DIM', ACCENT_DIM)};
                    color: {tokens.get('ACCENT', '#00D4FF')};
                    font-weight: 600;
                    border-left: 2px solid {tokens.get('ACCENT', '#00D4FF')};
                }}
            """)
            btn.clicked.connect(lambda _, k=icon: self.nav_changed.emit(k))
            lay.addWidget(btn)

        lay.addStretch()
        # Mini mode toggle
        mini = QPushButton("•••")
        mini.setFixedSize(28, 28)
        mini.setStyleSheet(f"""
            QPushButton {{
                background: {tokens.get('CARD-bg', '#1C1C24')};
                color: {tokens.get('TEXT-muted', '#6B7280')};
                border-radius: 14px;
                border: 1px solid {tokens.get('border-subtle', '#3F3F46')};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {tokens.get('SURFACE', '#15151B')};
                color: {tokens.get('TEXT', '#ECECEE')};
            }}
        """)
        mini.clicked.connect(self.toggle_requested.emit)
        lay.addWidget(mini)

    def set_active(self, key):
        """Highlight navigation item by key."""
        for prop, text in NAV_ITEMS:
            key_map = {"home": "home", "assistant": "assistant", "tasks": "tasks",
                       "calendar": "calendar", "notes": "notes", "files": "files",
                       "system": "system", "settings": "settings"}
            btn = self.findChild(QPushButton, f"nav_{key_map.get(key, 'home')}")
            if btn:
                btn.setChecked(True)