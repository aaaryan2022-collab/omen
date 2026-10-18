# ============================================
"""
Developer & Coding Studio View for OMEN.
Features:
- Integrated Code Editor with syntax highlighting & line numbers
- Split / Unified Diff Viewer with Checkpoint Rollback
- Integrated Terminal PTY with command execution & output
- Git Source Control panel (status, branch, stage, commit)
- Codebase Search & AST Symbol Navigator
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QTabWidget, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from tools.coding import ApplyPatchTool, TerminalRunTool, GitTool, CodebaseSearchTool, checkpoint_store
from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, ERROR, WARNING,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BACKGROUND_DARK, BACKGROUND_CARD, FONT_FAMILY
)


class TerminalWorker(QThread):
    finished_output = Signal(str, int)

    def __init__(self, command: str, cwd: str, parent=None):
        super().__init__(parent)
        self.command = command
        self.cwd = cwd

    def run(self):
        tool = TerminalRunTool()
        res = tool.execute(command=self.command, cwd=self.cwd)
        out = res.data.get("stdout", "") if res.data else ""
        err = res.data.get("stderr", "") if res.data else ""
        combined = out + ("\n" + err if err else "")
        exit_code = res.data.get("exit_code", -1) if res.data else -1
        self.finished_output.emit(combined.strip(), exit_code)


class CodingView(QWidget):
    """Integrated Developer IDE and Coding Agent Studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file_path = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("DEVELOPER & CODING STUDIO")
        title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 1.5px;")
        title_box.addWidget(title)

        subtitle = QLabel("Monaco-grade Editor · Unified Diff Patcher · Git Operations · Terminal PTY · AST Indexer")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self._btn_open_file = QPushButton("📂 Open File")
        self._btn_open_file.clicked.connect(self._open_file_dialog)
        self._btn_save_file = QPushButton("💾 Save File")
        self._btn_save_file.clicked.connect(self._save_file)
        self._btn_rollback = QPushButton("↺ Rollback Checkpoint")
        self._btn_rollback.clicked.connect(self._rollback_checkpoint)
        self._btn_rollback.setStyleSheet(f"background: rgba(239, 68, 68, 0.15); color: {ERROR}; border: 1px solid rgba(239, 68, 68, 0.3);")

        header.addWidget(self._btn_open_file)
        header.addWidget(self._btn_save_file)
        header.addWidget(self._btn_rollback)
        layout.addLayout(header)

        # Main Splitter: Left (Editor + Diff), Right (Terminal + Git)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Container: Tabs for Editor and Diff Viewer
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self._file_label = QLabel("No file loaded")
        self._file_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8.5pt;")
        left_layout.addWidget(self._file_label)

        self._code_tabs = QTabWidget()
        self._code_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid rgba(255, 255, 255, 0.08); background: {BACKGROUND_CARD}; }}
            QTabBar::tab {{ background: rgba(255, 255, 255, 0.03); color: {TEXT_SECONDARY}; padding: 8px 16px; border-radius: 4px; }}
            QTabBar::tab:selected {{ background: rgba(0, 210, 238, 0.12); color: {PRIMARY}; font-weight: bold; border-bottom: 2px solid {PRIMARY}; }}
        """)

        # Editor Tab
        self._editor = QTextEdit()
        self._editor.setFont(QFont("Consolas", 10.5))
        self._editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0A0D14;
                color: #E2E8F0;
                border: none;
                padding: 12px;
                line-height: 1.4;
            }}
        """)
        self._editor.setPlaceholderText("// Open or write code here...")
        self._code_tabs.addTab(self._editor, "📝 Code Editor")

        # Diff Viewer Tab
        self._diff_view = QTextEdit()
        self._diff_view.setFont(QFont("Consolas", 10))
        self._diff_view.setReadOnly(True)
        self._diff_view.setStyleSheet("""
            QTextEdit {
                background-color: #080B10;
                color: #A0AEC0;
                border: none;
                padding: 12px;
            }
        """)
        self._diff_view.setPlaceholderText("// Unified diffs and agent modifications will appear here...")
        self._code_tabs.addTab(self._diff_view, "🔍 Diff Inspector")

        left_layout.addWidget(self._code_tabs)
        splitter.addWidget(left_container)

        # Right Container: Terminal & Git Panel
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self._dev_tabs = QTabWidget()
        self._dev_tabs.setStyleSheet(self._code_tabs.styleSheet())

        # Terminal Tab
        term_widget = QWidget()
        term_layout = QVBoxLayout(term_widget)
        term_layout.setContentsMargins(8, 8, 8, 8)

        self._term_output = QTextEdit()
        self._term_output.setReadOnly(True)
        self._term_output.setFont(QFont("Consolas", 9.5))
        self._term_output.setStyleSheet("""
            QTextEdit {
                background-color: #05070B;
                color: #38BDF8;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        term_layout.addWidget(self._term_output)

        term_input_row = QHBoxLayout()
        self._term_input = QLineEdit()
        self._term_input.setFont(QFont("Consolas", 9.5))
        self._term_input.setPlaceholderText("Enter command (e.g. pytest, git status, npm run build)...")
        self._term_input.returnPressed.connect(self._run_terminal_command)
        self._term_input.setStyleSheet("""
            QLineEdit {
                background-color: #0D1117;
                color: #F1F5F9;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)
        btn_run = QPushButton("Run")
        btn_run.clicked.connect(self._run_terminal_command)
        term_input_row.addWidget(self._term_input)
        term_input_row.addWidget(btn_run)
        term_layout.addLayout(term_input_row)

        self._dev_tabs.addTab(term_widget, "💻 Terminal")

        # Git Tab
        git_widget = QWidget()
        git_layout = QVBoxLayout(git_widget)
        git_layout.setContentsMargins(8, 8, 8, 8)

        git_btn_row = QHBoxLayout()
        btn_git_status = QPushButton("Status")
        btn_git_status.clicked.connect(lambda: self._exec_git("status"))
        btn_git_diff = QPushButton("Diff")
        btn_git_diff.clicked.connect(lambda: self._exec_git("diff"))
        btn_git_log = QPushButton("Log")
        btn_git_log.clicked.connect(lambda: self._exec_git("log"))
        git_btn_row.addWidget(btn_git_status)
        git_btn_row.addWidget(btn_git_diff)
        git_btn_row.addWidget(btn_git_log)
        git_layout.addLayout(git_btn_row)

        self._git_output = QTextEdit()
        self._git_output.setReadOnly(True)
        self._git_output.setFont(QFont("Consolas", 9.5))
        self._git_output.setStyleSheet("""
            QTextEdit {
                background-color: #05070B;
                color: #4ADE80;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        git_layout.addWidget(self._git_output)

        commit_row = QHBoxLayout()
        self._commit_msg_input = QLineEdit()
        self._commit_msg_input.setPlaceholderText("Commit message...")
        btn_commit = QPushButton("Commit")
        btn_commit.clicked.connect(self._exec_git_commit)
        commit_row.addWidget(self._commit_msg_input)
        commit_row.addWidget(btn_commit)
        git_layout.addLayout(commit_row)

        self._dev_tabs.addTab(git_widget, "🌿 Git Operations")

        # Codebase Search Tab
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(8, 8, 8, 8)

        search_input_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search codebase symbols or patterns...")
        self._search_input.returnPressed.connect(self._exec_code_search)
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self._exec_code_search)
        search_input_row.addWidget(self._search_input)
        search_input_row.addWidget(btn_search)
        search_layout.addLayout(search_input_row)

        self._search_results = QTextEdit()
        self._search_results.setReadOnly(True)
        self._search_results.setFont(QFont("Consolas", 9))
        self._search_results.setStyleSheet(self._git_output.styleSheet())
        search_layout.addWidget(self._search_results)

        self._dev_tabs.addTab(search_widget, "🔍 AST Search")

        right_layout.addWidget(self._dev_tabs)
        splitter.addWidget(right_container)

        splitter.setSizes([600, 480])
        layout.addWidget(splitter)

    def _open_file_dialog(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Open Code File", os.getcwd())
        if fpath:
            self._current_file_path = fpath
            self._file_label.setText(fpath)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    self._editor.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read file: {e}")

    def _save_file(self):
        if not self._current_file_path:
            fpath, _ = QFileDialog.getSaveFileName(self, "Save Code File", os.getcwd())
            if fpath:
                self._current_file_path = fpath
                self._file_label.setText(fpath)
            else:
                return
        try:
            # Automatic checkpoint before save
            checkpoint_store.save_checkpoint(self._current_file_path, "Manual save from OMEN Coding Studio")
            with open(self._current_file_path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
            self._term_output.append(f"[OMEN] Saved {os.path.basename(self._current_file_path)} with checkpoint snapshot.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

    def _rollback_checkpoint(self):
        checkpoints = checkpoint_store.list_checkpoints()
        if not checkpoints:
            QMessageBox.information(self, "Checkpoint", "No checkpoints recorded yet.")
            return
        latest = checkpoints[-1]
        ok = checkpoint_store.rollback(latest["checkpoint_id"])
        if ok:
            QMessageBox.information(self, "Success", f"Rolled back {latest['file_path']} to {latest['checkpoint_id']}.")
            if self._current_file_path == latest["file_path"]:
                with open(self._current_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    self._editor.setPlainText(f.read())
        else:
            QMessageBox.warning(self, "Error", "Rollback failed.")

    def _run_terminal_command(self):
        cmd = self._term_input.text().strip()
        if not cmd:
            return
        self._term_output.append(f"\n$ {cmd}")
        self._term_input.clear()
        worker = TerminalWorker(cmd, os.getcwd(), self)
        worker.finished_output.connect(lambda out, code: self._term_output.append(f"{out}\n[Exit Code: {code}]"))
        worker.start()

    def _exec_git(self, action: str):
        tool = GitTool()
        res = tool.execute(action=action)
        out = res.data.get("output", "") if res.data else res.message
        self._git_output.setPlainText(f"=== git {action} ===\n\n{out}")

    def _exec_git_commit(self):
        msg = self._commit_msg_input.text().strip()
        if not msg:
            return
        tool = GitTool()
        tool.execute(action="add")
        res = tool.execute(action="commit", args=msg)
        self._git_output.setPlainText(res.data.get("output", res.message) if res.data else res.message)
        self._commit_msg_input.clear()

    def _exec_code_search(self):
        q = self._search_input.text().strip()
        if not q:
            return
        tool = CodebaseSearchTool()
        res = tool.execute(query=q)
        if res.success and res.data:
            matches = res.data.get("matches", [])
            lines = [f"Found {len(matches)} match(es) for '{q}':\n"]
            for m in matches:
                lines.append(f"{m['file']}:{m['line']} -> {m['content']}")
            self._search_results.setPlainText("\n".join(lines))
        else:
            self._search_results.setPlainText(res.error or "No matches found.")
