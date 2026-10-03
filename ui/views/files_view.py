# ============================================
"""
OMEN Workspace Files Deck.
Clean file inspector and workspace browser.
Features:
- Workspace tree / directory search
- File preview and metadata (size, lines, modified)
- "Summarize with OMEN" button triggering autonomous analysis
- Quick filter by extension (.py, .md, .json, .txt, etc.)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QTextEdit,
    QSplitter,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, BACKGROUND_DARK, BACKGROUND_CARD,
)


class FilesView(QWidget):
    """Clean workspace file browser and previewer."""

    summarize_requested = Signal(str)

    def __init__(self, workspace_path: str = "e:/OMEN", parent=None):
        super().__init__(parent)
        self._workspace = Path(workspace_path)
        self._files = []
        self._build_ui()
        self._scan_workspace()

    def _build_ui(self):
        self.setObjectName("filesView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        t_lbl = QLabel("Workspace & Files")
        t_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_box.addWidget(t_lbl)

        sub_lbl = QLabel(f"Browsing: {self._workspace.resolve()} · Local file operations")
        sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)
        header.addStretch()

        refresh_btn = QPushButton("↻ Refresh Workspace")
        refresh_btn.clicked.connect(self._scan_workspace)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Splitter Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(255, 255, 255, 0.05);
                width: 1px;
            }
        """)

        # Left: Search & Files List
        left_pane = QWidget()
        l_layout = QVBoxLayout(left_pane)
        l_layout.setContentsMargins(0, 0, 14, 0)
        l_layout.setSpacing(10)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Filter workspace files...")
        self._search_input.textChanged.connect(self._filter_files)
        l_layout.addWidget(self._search_input)

        self._files_list = QListWidget()
        self._files_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgba(21, 21, 28, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 6px;
                margin-bottom: 2px;
                color: {TEXT_PRIMARY};
                font-family: Consolas, Segoe UI;
                font-size: 12.5px;
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
        self._files_list.currentRowChanged.connect(self._on_file_selected)
        l_layout.addWidget(self._files_list)
        splitter.addWidget(left_pane)

        # Right: File Details & Preview
        right_pane = QWidget()
        r_layout = QVBoxLayout(right_pane)
        r_layout.setContentsMargins(14, 0, 0, 0)
        r_layout.setSpacing(10)

        preview_card = QFrame()
        preview_card.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 14px;
            }
        """)
        pc_layout = QVBoxLayout(preview_card)
        pc_layout.setContentsMargins(10, 10, 10, 10)
        pc_layout.setSpacing(10)

        # File Title & Meta
        meta_row = QHBoxLayout()
        self._file_name_lbl = QLabel("Select a file to inspect")
        self._file_name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 600;")
        meta_row.addWidget(self._file_name_lbl)
        meta_row.addStretch()

        self._summarize_btn = QPushButton("⚡ Summarize with OMEN")
        self._summarize_btn.setObjectName("primaryBtn")
        self._summarize_btn.clicked.connect(self._summarize_file)
        self._summarize_btn.hide()
        meta_row.addWidget(self._summarize_btn)
        pc_layout.addLayout(meta_row)

        self._file_meta_lbl = QLabel("")
        self._file_meta_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        pc_layout.addWidget(self._file_meta_lbl)

        # File Content Preview
        self._preview_edit = QTextEdit()
        self._preview_edit.setReadOnly(True)
        self._preview_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0D0D12;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                color: #CBD5E1;
                font-family: Consolas, monospace;
                font-size: 12px;
                line-height: 1.4;
            }}
        """)
        pc_layout.addWidget(self._preview_edit, stretch=1)

        r_layout.addWidget(preview_card)
        splitter.addWidget(right_pane)

        splitter.setSizes([300, 560])
        layout.addWidget(splitter, stretch=1)

    def _scan_workspace(self):
        self._files.clear()
        self._files_list.clear()

        ignore_dirs = {".git", ".claude", "__pycache__", ".pytest_cache", "logs"}
        try:
            for root, dirs, files in os.walk(self._workspace):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(self._workspace)
                    self._files.append((str(rel_p).replace("\\", "/"), full_p))
        except Exception:
            pass

        self._files.sort(key=lambda x: x[0])
        for rel_name, _ in self._files:
            self._files_list.addItem(rel_name)

        if self._files:
            self._files_list.setCurrentRow(0)

    def _filter_files(self, query: str):
        query = query.lower()
        for i in range(self._files_list.count()):
            item = self._files_list.item(i)
            item.setHidden(query not in item.text().lower())

    def _on_file_selected(self, row: int):
        if 0 <= row < len(self._files):
            rel_name, full_path = self._files[row]
            self._selected_path = full_path
            self._file_name_lbl.setText(rel_name)
            self._summarize_btn.show()

            try:
                st = full_path.stat()
                size_kb = st.st_size / 1024.0
                mod_str = datetime.fromtimestamp(st.st_mtime).strftime("%b %d, %Y %I:%M %p")
                self._file_meta_lbl.setText(f"Size: {size_kb:.1f} KB  ·  Modified: {mod_str}")

                if st.st_size < 300 * 1024:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read(4000)
                    self._preview_edit.setPlainText(content)
                else:
                    self._preview_edit.setPlainText("[Large file — preview truncated for performance]")
            except Exception as e:
                self._preview_edit.setPlainText(f"Unable to read file: {e}")

    def _summarize_file(self):
        if hasattr(self, "_selected_path"):
            path_str = str(self._selected_path)
            self.summarize_requested.emit(path_str)
            ToastManager.show(self.window(), f"Sent {self._selected_path.name} to OMEN", level="info")
