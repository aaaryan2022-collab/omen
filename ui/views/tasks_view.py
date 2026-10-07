# ============================================
"""
OMEN Tasks Management Deck.
Clean, elegant task productivity interface inspired by Linear and Things.
Sections:
- Today's Tasks
- Upcoming
- Completed
Features:
- Checkbox with smooth completion styling
- Priority badges (High / Medium / Low)
- Due date & reminder badge
- Edit dialog & delete actions
- Natural language quick-add bar
- Toast confirmations
"""

from datetime import datetime, date, timedelta
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QScrollArea, QDialog,
    QCheckBox, QMessageBox, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QColor

from productivity.tasks import get_task_manager, parse_natural_date
from database.models import Task
from app.constants import TaskPriority, TaskStatus
from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, WARNING, ERROR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, BACKGROUND_DARK,
    BACKGROUND_CARD, BACKGROUND_HOVER, BORDER,
)


class TaskItemCard(QFrame):
    """Clean task row with priority badge, date, edit, and delete controls."""

    toggled = Signal(str, bool)
    edit_requested = Signal(object)
    delete_requested = Signal(str)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self._task = task
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 6px 12px;
            }
            QFrame:hover {
                background-color: rgba(27, 27, 36, 0.95);
                border-color: rgba(0, 210, 238, 0.25);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        # 1. Checkbox
        self._chk = QCheckBox()
        is_done = task.status == TaskStatus.COMPLETED
        self._chk.setChecked(is_done)
        self._chk.toggled.connect(self._on_toggled)
        layout.addWidget(self._chk)

        # 2. Priority indicator badge
        p_color = ERROR if task.priority == TaskPriority.HIGH else (
            PRIMARY if task.priority == TaskPriority.MEDIUM else TEXT_DIM
        )
        p_badge = QLabel(task.priority.value.upper())
        p_badge.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {p_color};
                border: 1px solid {p_color};
                border-radius: 4px;
                padding: 1px 6px;
                font-size: 9.5px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(p_badge)

        # 3. Task Title
        self._title_lbl = QLabel(task.title)
        self._update_title_style(is_done)
        layout.addWidget(self._title_lbl, stretch=1)

        # 4. Due Date & Reminder indicator
        due_val = getattr(task, "due_at", None) or getattr(task, "due_date", None)
        if due_val:
            due_str = due_val.strftime("%b %d, %I:%M %p") if isinstance(due_val, datetime) else str(due_val)
            due_lbl = QLabel(f"📅 {due_str}")
            due_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
            layout.addWidget(due_lbl)

        # 5. Edit Button
        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(22, 22)
        edit_btn.setToolTip("Edit task")
        self._style_icon_btn(edit_btn)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._task))
        layout.addWidget(edit_btn)

        # 6. Delete Button
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.setToolTip("Delete task")
        self._style_icon_btn(del_btn, is_danger=True)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._task.id))
        layout.addWidget(del_btn)

    def _style_icon_btn(self, btn: QPushButton, is_danger: bool = False):
        hover_col = "#EF4444" if is_danger else "#00D2EE"
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: #71717A;
                font-size: 12px;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {hover_col};
            }}
        """)

    def _update_title_style(self, is_done: bool):
        if is_done:
            self._title_lbl.setStyleSheet(f"color: {TEXT_DIM}; text-decoration: line-through; font-size: 13px;")
        else:
            self._title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")

    def _on_toggled(self, checked: bool):
        self._update_title_style(checked)
        self.toggled.emit(self._task.id, checked)


class EditTaskDialog(QDialog):
    """Minimal dialog to edit a task."""

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.setFixedSize(400, 260)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Task Title:"))
        self._title_input = QLineEdit(task.title)
        layout.addWidget(self._title_input)

        layout.addWidget(QLabel("Priority:"))
        self._priority_combo = QComboBox()
        self._priority_combo.addItems(["Low", "Medium", "High"])
        idx = 0
        if task.priority == TaskPriority.MEDIUM:
            idx = 1
        elif task.priority == TaskPriority.HIGH:
            idx = 2
        self._priority_combo.setCurrentIndex(idx)
        layout.addWidget(self._priority_combo)

        layout.addWidget(QLabel("Due Date / Deadline (Natural text):"))
        due_val = getattr(task, "due_at", None) or getattr(task, "due_date", None)
        self._due_input = QLineEdit(str(due_val) if due_val else "")
        self._due_input.setPlaceholderText("e.g. tomorrow at 5pm, next friday")
        layout.addWidget(self._due_input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def get_data(self):
        pri_map = {"Low": TaskPriority.LOW, "Medium": TaskPriority.MEDIUM, "High": TaskPriority.HIGH}
        due = parse_natural_date(self._due_input.text().strip())
        return {
            "title": self._title_input.text().strip(),
            "priority": pri_map.get(self._priority_combo.currentText(), TaskPriority.MEDIUM),
            "due_at": due,
        }


class TasksView(QWidget):
    """Master Tasks Management Deck for OMEN."""

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._tm = get_task_manager()
        self._current_tab = "today"  # today, upcoming, completed
        self._build_ui()
        self.refresh_tasks()

    def _build_ui(self):
        self.setObjectName("tasksView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        t_lbl = QLabel("Tasks & Objectives")
        t_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_box.addWidget(t_lbl)

        sub_lbl = QLabel("Intelligent daily agenda, priority deadlines, and autonomous tracking.")
        sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)
        header.addStretch()

        layout.addLayout(header)

        # Quick Add Task Bar
        add_bar = QFrame()
        add_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 4px 8px;
            }
        """)
        add_layout = QHBoxLayout(add_bar)
        add_layout.setContentsMargins(8, 4, 8, 4)
        add_layout.setSpacing(10)

        self._quick_input = QLineEdit()
        self._quick_input.setPlaceholderText("Add a task... (e.g. 'Submit report tomorrow 5pm')")
        self._quick_input.setStyleSheet("background: transparent; border: none; font-size: 13px;")
        self._quick_input.returnPressed.connect(self._create_task)
        add_layout.addWidget(self._quick_input, stretch=1)

        self._pri_select = QComboBox()
        self._pri_select.addItems(["Medium", "High", "Low"])
        add_layout.addWidget(self._pri_select)

        add_btn = QPushButton("＋ Add Task")
        add_btn.setObjectName("primaryBtn")
        add_btn.setFixedSize(96, 32)
        add_btn.clicked.connect(self._create_task)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_bar)

        # Section Tabs: Today / Upcoming / Completed
        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)

        self._tab_today = QPushButton("Today's Tasks")
        self._tab_upcoming = QPushButton("Upcoming")
        self._tab_completed = QPushButton("Completed")

        self._tab_buttons = [
            ("today", self._tab_today),
            ("upcoming", self._tab_upcoming),
            ("completed", self._tab_completed),
        ]

        for tab_id, btn in self._tab_buttons:
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda chk, tid=tab_id: self._set_tab(tid))
            self._style_tab_btn(btn)
            tab_row.addWidget(btn)

        tab_row.addStretch()
        layout.addLayout(tab_row)

        # Scroll Area for Task Cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._list_container = QWidget()
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_container)
        layout.addWidget(self._scroll, stretch=1)

        self._set_tab("today")

    def _style_tab_btn(self, btn: QPushButton):
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                color: #A1A1AA;
                padding: 6px 14px;
                font-size: 12.5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
                color: #F4F4F6;
            }
            QPushButton:checked {
                background: rgba(0, 210, 238, 0.14);
                border-color: rgba(0, 210, 238, 0.4);
                color: #00D2EE;
                font-weight: 600;
            }
        """)

    def _set_tab(self, tab_id: str):
        self._current_tab = tab_id
        for tid, btn in self._tab_buttons:
            btn.setChecked(tid == tab_id)
        self.refresh_tasks()

    def _create_task(self):
        text = self._quick_input.text().strip()
        if not text:
            return

        due = parse_natural_date(text)
        pri_text = self._pri_select.currentText()
        pri_map = {"Low": TaskPriority.LOW, "Medium": TaskPriority.MEDIUM, "High": TaskPriority.HIGH}
        pri = pri_map.get(pri_text, TaskPriority.MEDIUM)

        clean_title = text
        for token in ["tomorrow", "today", "tonight", "at 5pm", "at 6pm", "at 9am", "in 1 hour", "in 2 hours"]:
            clean_title = clean_title.replace(token, "").strip()

        task = self._tm.add_task(title=clean_title or text, due_at=due, priority=pri)
        self._quick_input.clear()
        ToastManager.show(self.window(), "Task created", level="success")
        self.refresh_tasks()

    def refresh_tasks(self):
        # Clear list
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_tasks = self._tm.list_tasks(status=None)
        now = datetime.now()
        today_date = now.date()

        filtered_tasks = []
        for t in all_tasks:
            due_val = getattr(t, "due_at", None) or getattr(t, "due_date", None)
            if self._current_tab == "completed":
                if t.status == TaskStatus.COMPLETED:
                    filtered_tasks.append(t)
            elif self._current_tab == "today":
                if t.status != TaskStatus.COMPLETED:
                    if due_val is None or (isinstance(due_val, datetime) and due_val.date() <= today_date):
                        filtered_tasks.append(t)
            elif self._current_tab == "upcoming":
                if t.status != TaskStatus.COMPLETED:
                    if isinstance(due_val, datetime) and due_val.date() > today_date:
                        filtered_tasks.append(t)

        if not filtered_tasks:
            empty_lbl = QLabel(f"No {self._current_tab} tasks. You're completely clear.")
            empty_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; padding: 20px 0;")
            self._list_layout.insertWidget(0, empty_lbl)
            return

        for idx, task in enumerate(filtered_tasks):
            card = TaskItemCard(task)
            card.toggled.connect(self._on_task_toggled)
            card.edit_requested.connect(self._on_task_edit)
            card.delete_requested.connect(self._on_task_delete)
            self._list_layout.insertWidget(idx, card)

    def _on_task_toggled(self, task_id, is_completed: bool):
        if is_completed:
            self._tm.complete_task(task_id)
        else:
            if hasattr(self._tm.repo, "update"):
                t = self._tm.repo.get(task_id)
                if t:
                    t.status = TaskStatus.PENDING
                    t.completed_at = None
                    self._tm.repo.update(t)
        msg = "Task completed" if is_completed else "Task marked pending"
        ToastManager.show(self.window(), msg, level="success")
        QTimer.singleShot(250, self.refresh_tasks)

    def _on_task_edit(self, task: Task):
        dlg = EditTaskDialog(task, self)
        if dlg.exec():
            data = dlg.get_data()
            task.title = data["title"]
            task.priority = data["priority"]
            task.due_at = data["due_at"]
            if hasattr(self._tm.repo, "update"):
                self._tm.repo.update(task)
            ToastManager.show(self.window(), "Task updated", level="info")
            self.refresh_tasks()

    def _on_task_delete(self, task_id):
        self._tm.delete_task(task_id)
        ToastManager.show(self.window(), "Task deleted", level="warning")
        self.refresh_tasks()
