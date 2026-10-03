# ============================================
"""
Raycast-Style Command Palette for OMEN.
Centered floating glass dialog accessible with Ctrl + Space.
Keyboard navigable (Up/Down, Enter, Esc), instant fuzzy-like filtering,
and fallback to "Ask OMEN: <query>".
"""

from typing import Callable, List, Dict, Any, Optional
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QFrame, QWidget, QGraphicsDropShadowEffect,
)
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, PRIMARY_LIGHT, SECONDARY, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_DIM, BACKGROUND_CARD, BORDER, GLASS_BACKGROUND,
)


class CommandPaletteItem(QWidget):
    """List item rendering for palette action."""

    def __init__(self, title: str, category: str, shortcut: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Title & Category
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        text_layout.addWidget(title_lbl)

        cat_lbl = QLabel(category)
        cat_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 600; text-transform: uppercase;")
        text_layout.addWidget(cat_lbl)

        layout.addLayout(text_layout, stretch=1)

        # Shortcut badge
        if shortcut:
            sc_lbl = QLabel(shortcut)
            sc_lbl.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    background: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 5px;
                    padding: 2px 6px;
                    font-size: 10.5px;
                    font-family: Consolas, monospace;
                }}
            """)
            layout.addWidget(sc_lbl)


class CommandPalette(QDialog):
    """Raycast-inspired centered glass command palette."""

    action_triggered = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(620, 420)

        self._actions = []
        self._build_ui()
        self._register_default_actions()
        self._filter_actions("")

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)

        # Glass Panel Container
        panel = QFrame()
        panel.setObjectName("palettePanel")
        panel.setStyleSheet(f"""
            QFrame#palettePanel {{
                background-color: rgba(18, 18, 25, 0.94);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 14px;
            }}
        """)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 12)
        panel_layout.setSpacing(12)

        # Search Bar Row
        search_row = QHBoxLayout()
        search_row.setContentsMargins(4, 0, 4, 0)
        search_row.setSpacing(10)

        search_icon = QLabel("◉")
        search_icon.setStyleSheet(f"color: {PRIMARY}; font-size: 14px;")
        search_row.addWidget(search_icon)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Type a command or ask OMEN anything...")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 15px;
                padding: 4px 0;
            }}
        """)
        self._search_input.textChanged.connect(self._filter_actions)
        search_row.addWidget(self._search_input, stretch=1)

        esc_hint = QLabel("ESC to exit")
        esc_hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        search_row.addWidget(esc_hint)

        panel_layout.addLayout(search_row)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); max-height: 1px; border: none;")
        panel_layout.addWidget(divider)

        # Action List
        self._list_widget = QListWidget()
        self._list_widget.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border-radius: 8px;
                margin-bottom: 3px;
                border: 1px solid transparent;
            }}
            QListWidget::item:selected {{
                background: rgba(0, 210, 238, 0.12);
                border: 1px solid rgba(0, 210, 238, 0.35);
            }}
            QListWidget::item:hover:!selected {{
                background: rgba(255, 255, 255, 0.04);
            }}
        """)
        self._list_widget.itemActivated.connect(self._on_item_activated)
        panel_layout.addWidget(self._list_widget, stretch=1)

        # Footer Row with Navigation Shortcuts
        footer = QHBoxLayout()
        footer.setContentsMargins(6, 4, 6, 0)
        footer_hint = QLabel("↑↓ Navigate   ↵ Select   Ctrl+Space Open")
        footer_hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        footer.addWidget(footer_hint)
        footer.addStretch()

        omen_tag = QLabel("OMEN Command Palette")
        omen_tag.setStyleSheet(f"color: {PRIMARY}; font-size: 10.5px; font-weight: 600;")
        footer.addWidget(omen_tag)

        panel_layout.addLayout(footer)
        root_layout.addWidget(panel)

    def _register_default_actions(self):
        self._actions = [
            {"id": "new_chat", "title": "New Conversation", "category": "Chat", "shortcut": "Ctrl+N"},
            {"id": "nav_chat", "title": "Open Assistant & Chat", "category": "Navigation", "shortcut": "Alt+1"},
            {"id": "nav_tasks", "title": "Open Tasks & Objectives", "category": "Navigation", "shortcut": "Alt+2"},
            {"id": "nav_calendar", "title": "Open Calendar & Schedule", "category": "Navigation", "shortcut": "Alt+3"},
            {"id": "nav_notes", "title": "Open Notes & Scratchpad", "category": "Navigation", "shortcut": "Alt+4"},
            {"id": "nav_files", "title": "Browse Files & Workspace", "category": "Navigation", "shortcut": "Alt+5"},
            {"id": "nav_system", "title": "System Telemetry & Hardware", "category": "Navigation", "shortcut": "Alt+6"},
            {"id": "nav_settings", "title": "Open Settings & AI Models", "category": "Navigation", "shortcut": "Ctrl+,"},
            {"id": "voice_mode", "title": "Start Voice Dialogue Mode", "category": "Voice", "shortcut": "Space"},
            {"id": "mini_mode", "title": "Switch to Desktop Mini Widget", "category": "Window", "shortcut": "Ctrl+M"},
            {"id": "create_task", "title": "Create New Task", "category": "Actions", "shortcut": "T"},
            {"id": "create_note", "title": "Create Quick Note", "category": "Actions", "shortcut": ""},
            {"id": "summarize_files", "title": "Summarize Workspace Files", "category": "AI Actions", "shortcut": ""},
            {"id": "plan_day", "title": "Plan My Day", "category": "AI Actions", "shortcut": ""},
            {"id": "stop_emergency", "title": "Emergency Stop Agent", "category": "Safety", "shortcut": "Ctrl+Shift+Esc"},
        ]

    def _filter_actions(self, query: str):
        query = query.strip().lower()
        self._list_widget.clear()

        # If user typed something not matching direct command, offer "Ask OMEN"
        if query:
            ask_item = QListWidgetItem()
            ask_widget = CommandPaletteItem(f"Ask OMEN: \"{query}\"", "AI Prompt", "↵")
            ask_item.setSizeHint(ask_widget.sizeHint())
            ask_item.setData(Qt.ItemDataRole.UserRole, {"id": "ask_prompt", "query": query})
            self._list_widget.addItem(ask_item)

        matches = []
        for a in self._actions:
            if not query or query in a["title"].lower() or query in a["category"].lower():
                matches.append(a)

        for a in matches:
            item = QListWidgetItem()
            widget = CommandPaletteItem(a["title"], a["category"], a.get("shortcut", ""))
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, a)
            self._list_widget.addItem(item)
            self._list_widget.setItemWidget(item, widget)

        if self._list_widget.count() > 0:
            self._list_widget.setCurrentRow(0)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.reject()
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_Tab):
            cur = self._list_widget.currentRow()
            if cur < self._list_widget.count() - 1:
                self._list_widget.setCurrentRow(cur + 1)
        elif key == Qt.Key.Key_Up:
            cur = self._list_widget.currentRow()
            if cur > 0:
                self._list_widget.setCurrentRow(cur - 1)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self._list_widget.currentItem()
            if item:
                self._on_item_activated(item)
        else:
            super().keyPressEvent(event)

    def _on_item_activated(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            action_id = data.get("id")
            self.action_triggered.emit(action_id, data)
        self.accept()

    def open_palette(self):
        self._search_input.clear()
        self._filter_actions("")
        self._search_input.setFocus()
        self.exec()
