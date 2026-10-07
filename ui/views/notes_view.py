# ============================================
"""
OMEN Notes & Scratchpad Deck.
Minimalist, distraction-free markdown notes interface.
Features:
- Dual-pane layout: Note index on left, editor on right
- Search notes
- Live editing with title and markdown body
- Quick save and export
- Toast confirmations
"""

from datetime import datetime
from typing import List, Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFrame,
    QSplitter,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, BACKGROUND_DARK, BACKGROUND_CARD, BORDER,
)


class NotesView(QWidget):
    """Clean notes and markdown scratchpad."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._notes = [
            {
                "id": "n1",
                "title": "OMEN Architecture & Tool Integration",
                "content": "# OMEN System Architecture\n\nOMEN coordinates local autonomous tools via an asynchronous supervisor loop:\n- UI Layer (PySide6 with Glassmorphism)\n- Core Agent & EventBus\n- Tool Registry & Security Layer\n- Hardware Telemetry & Audio Pipeline",
                "date": "Today, 10:15 AM",
            },
            {
                "id": "n2",
                "title": "Pair Programming Priorities",
                "content": "1. Verify PySide6 headless rendering\n2. Refine keyboard shortcuts and command palette\n3. Optimize system telemetry polling rate\n4. Add high-DPI desktop support",
                "date": "Yesterday",
            },
        ]
        self._current_index = 0
        self._build_ui()
        self._load_note(0)

    def _build_ui(self):
        self.setObjectName("notesView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        t_lbl = QLabel("Notes & Scratchpad")
        t_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_box.addWidget(t_lbl)

        sub_lbl = QLabel("Instant markdown notes, AI responses, and scratchpad ideas.")
        sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)
        header.addStretch()

        new_btn = QPushButton("＋ New Note")
        new_btn.setObjectName("primaryBtn")
        new_btn.clicked.connect(self._create_new_note)
        header.addWidget(new_btn)
        layout.addLayout(header)

        # Splitter Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(255, 255, 255, 0.05);
                width: 1px;
            }
        """)

        # Left: Search & Notes List
        left_pane = QWidget()
        l_layout = QVBoxLayout(left_pane)
        l_layout.setContentsMargins(0, 0, 14, 0)
        l_layout.setSpacing(10)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search notes...")
        self._search_input.textChanged.connect(self._filter_notes)
        l_layout.addWidget(self._search_input)

        self._notes_list = QListWidget()
        self._notes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgba(21, 21, 28, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 4px;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 210, 238, 0.12);
                border: 1px solid rgba(0, 210, 238, 0.3);
                color: #00D2EE;
            }}
            QListWidget::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 0.04);
            }}
        """)
        self._notes_list.currentRowChanged.connect(self._load_note)
        l_layout.addWidget(self._notes_list)
        splitter.addWidget(left_pane)

        # Right: Editor Pane
        right_pane = QWidget()
        r_layout = QVBoxLayout(right_pane)
        r_layout.setContentsMargins(14, 0, 0, 0)
        r_layout.setSpacing(10)

        editor_card = QFrame()
        editor_card.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 14px;
            }
        """)
        ec_layout = QVBoxLayout(editor_card)
        ec_layout.setContentsMargins(10, 10, 10, 10)
        ec_layout.setSpacing(10)

        # Note Title Input
        self._title_edit = QLineEdit()
        self._title_edit.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                color: {TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                padding: 4px 0 8px 0;
            }}
        """)
        ec_layout.addWidget(self._title_edit)

        # Note Content Editor
        self._content_edit = QTextEdit()
        self._content_edit.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 13.5px;
                font-family: Consolas, Segoe UI;
                line-height: 1.5;
            }}
        """)
        ec_layout.addWidget(self._content_edit, stretch=1)

        # Action bar
        act_row = QHBoxLayout()
        self._del_btn = QPushButton("Delete Note")
        self._del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.15);
            }
        """)
        self._del_btn.clicked.connect(self._delete_current_note)
        act_row.addWidget(self._del_btn)
        act_row.addStretch()

        save_btn = QPushButton("Save Note")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_current_note)
        act_row.addWidget(save_btn)

        ec_layout.addLayout(act_row)
        r_layout.addWidget(editor_card)
        splitter.addWidget(right_pane)

        splitter.setSizes([260, 600])
        layout.addWidget(splitter, stretch=1)

        self._refresh_list()

    def _refresh_list(self):
        self._notes_list.clear()
        for n in self._notes:
            self._notes_list.addItem(n["title"])
        if self._notes:
            self._notes_list.setCurrentRow(0)

    def _filter_notes(self, query: str):
        query = query.lower()
        for i in range(self._notes_list.count()):
            item = self._notes_list.item(i)
            item.setHidden(query not in item.text().lower())

    def _load_note(self, row: int):
        if 0 <= row < len(self._notes):
            self._current_index = row
            note = self._notes[row]
            self._title_edit.setText(note["title"])
            self._content_edit.setText(note["content"])

    def _create_new_note(self):
        new_note = {
            "id": f"n_{int(datetime.now().timestamp())}",
            "title": "Untitled Note",
            "content": "",
            "date": "Just now",
        }
        self._notes.insert(0, new_note)
        self._refresh_list()
        self._notes_list.setCurrentRow(0)
        self._title_edit.setFocus()
        ToastManager.show(self.window(), "New note created", level="info")

    def _save_current_note(self):
        if 0 <= self._current_index < len(self._notes):
            self._notes[self._current_index]["title"] = self._title_edit.text().strip() or "Untitled Note"
            self._notes[self._current_index]["content"] = self._content_edit.toPlainText()
            item = self._notes_list.item(self._current_index)
            if item:
                item.setText(self._notes[self._current_index]["title"])
            ToastManager.show(self.window(), "Note saved", level="success")

    def _delete_current_note(self):
        if 0 <= self._current_index < len(self._notes):
            self._notes.pop(self._current_index)
            self._refresh_list()
            ToastManager.show(self.window(), "Note deleted", level="warning")
