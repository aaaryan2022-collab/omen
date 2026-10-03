# ============================================
"""
OMEN Navigation Sidebar — Compact, Collapsible, Premium Editorial Layout.
Includes:
- OMEN logo / orb
- "+ New Conversation" action button
- Navigation items: Chat, Tasks, Calendar, Notes, Files, System, Settings
- Smooth toggle between expanded (220px) and collapsed (64px) states.
"""

from typing import List, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame, QButtonGroup,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QCursor
from ui.orb import OmenOrb
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, BACKGROUND_DARK, BACKGROUND_MEDIUM, BACKGROUND_CARD,
    BORDER, BORDER_ACTIVE, FONT_FAMILY,
    WARNING, ERROR,
)


class Sidebar(QWidget):
    """Refined collapsible desktop sidebar with OMEN branding and navigation."""

    page_changed = Signal(str)
    new_conversation_requested = Signal()
    collapse_toggled = Signal(bool)

    NAV_ITEMS: List[Tuple[str, str, str]] = [
        ("chat", "Chat", "💬"),
        ("tasks", "Tasks", "✓"),
        ("calendar", "Calendar", "📅"),
        ("notes", "Notes", "📝"),
        ("files", "Files", "📁"),
        ("system", "System", "⚡"),
        ("settings", "Settings", "⚙"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._is_collapsed = False
        self._buttons = {}
        self._active_page = "chat"

        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {BACKGROUND_DARK};
                border-right: 1px solid rgba(255, 255, 255, 0.06);
            }}
            QLabel {{
                color: {TEXT_SECONDARY};
                font-family: {FONT_FAMILY};
            }}
            QPushButton.navBtn {{
                background: transparent;
                color: {TEXT_SECONDARY};
                text-align: left;
                padding: 9px 12px;
                border-radius: 8px;
                font-size: 13px;
                font-family: {FONT_FAMILY};
                font-weight: 500;
                border: 1px solid transparent;
            }}
            QPushButton.navBtn:hover {{
                background: rgba(255, 255, 255, 0.05);
                color: {TEXT_PRIMARY};
            }}
            QPushButton.navBtn:checked {{
                background: rgba(0, 210, 238, 0.10);
                color: #00D2EE;
                font-weight: 600;
                border-left: 2px solid #00D2EE;
                border-radius: 4px 8px 8px 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 16, 10, 14)
        layout.setSpacing(6)

        # 1. Header with OMEN Brand & Collapse Toggle
        header_row = QHBoxLayout()
        header_row.setContentsMargins(4, 0, 4, 0)
        header_row.setSpacing(8)

        self._orb_icon = OmenOrb(size=26, show_label=False)
        header_row.addWidget(self._orb_icon)

        self._brand_title = QLabel("OMEN")
        self._brand_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._brand_title.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: 1.5px;")
        header_row.addWidget(self._brand_title)

        header_row.addStretch()

        self._collapse_btn = QPushButton("◀")
        self._collapse_btn.setFixedSize(24, 24)
        self._collapse_btn.setToolTip("Collapse Sidebar")
        self._collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #71717A;
                border: none;
                font-size: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                color: #EDEDEF;
            }
        """)
        self._collapse_btn.clicked.connect(self.toggle_collapsed)
        header_row.addWidget(self._collapse_btn)

        layout.addLayout(header_row)
        layout.addSpacing(10)

        # 2. "+ New Conversation" Button
        self._new_chat_btn = QPushButton("＋  New Chat")
        self._new_chat_btn.setToolTip("Start New Conversation (Ctrl+N)")
        self._new_chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: {TEXT_PRIMARY};
                text-align: center;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 210, 238, 0.12);
                border-color: rgba(0, 210, 238, 0.35);
                color: #00D2EE;
            }}
        """)
        self._new_chat_btn.clicked.connect(self.new_conversation_requested.emit)
        layout.addWidget(self._new_chat_btn)
        layout.addSpacing(6)

        # 3. Navigation Buttons
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for page_id, label, icon in self.NAV_ITEMS:
            btn = QPushButton(f"{icon}   {label}")
            btn.setProperty("class", "navBtn")
            btn.setCheckable(True)
            btn.setToolTip(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_clicked(pid))

            self._btn_group.addButton(btn)
            self._buttons[page_id] = (btn, label, icon)
            layout.addWidget(btn)

        layout.addStretch()

        # 4. Status Indicator Badge (Bottom)
        self._status_frame = QFrame()
        self._status_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 6px 10px;
            }
        """)
        status_layout = QHBoxLayout(self._status_frame)
        status_layout.setContentsMargins(6, 4, 6, 4)
        status_layout.setSpacing(8)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
        status_layout.addWidget(self._status_dot)

        self._status_text = QLabel("OMEN v1.0 · Ready")
        self._status_text.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        status_layout.addWidget(self._status_text)
        status_layout.addStretch()

        layout.addWidget(self._status_frame)

        # Set default active
        self.set_active_page("chat")

    def toggle_collapsed(self):
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.setFixedWidth(64)
            self._brand_title.hide()
            self._status_frame.hide()
            self._collapse_btn.setText("▶")
            self._collapse_btn.setToolTip("Expand Sidebar")
            self._new_chat_btn.setText("＋")
            for page_id, (btn, label, icon) in self._buttons.items():
                btn.setText(icon)
        else:
            self.setFixedWidth(220)
            self._brand_title.show()
            self._status_frame.show()
            self._collapse_btn.setText("◀")
            self._collapse_btn.setToolTip("Collapse Sidebar")
            self._new_chat_btn.setText("＋  New Chat")
            for page_id, (btn, label, icon) in self._buttons.items():
                btn.setText(f"{icon}   {label}")
        self.collapse_toggled.emit(self._is_collapsed)

    def _on_nav_clicked(self, page_id: str):
        self._active_page = page_id
        self.page_changed.emit(page_id)

    def set_active_page(self, page_id: str):
        self._active_page = page_id
        if page_id in self._buttons:
            btn, _, _ = self._buttons[page_id]
            btn.setChecked(True)

    def set_status(self, text: str, state: str = "ready"):
        color = SUCCESS if state == "ready" else (WARNING if state == "busy" else ERROR)
        self._status_dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        self._status_text.setText(text)
        self._orb_icon.set_state("idle" if state == "ready" else ("thinking" if state == "busy" else "error"))