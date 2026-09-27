"""
Tasks & Schedule View — Holographic Task Command Center.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QListWidget, QListWidgetItem, QFrame,
    QDialog, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from productivity.tasks import get_task_manager
from database.models import Task
from app.constants import TaskPriority, TaskStatus
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, ERROR, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class TasksView(QWidget):
    """Futuristic Task & Goal Management Deck."""

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._tm = get_task_manager()
        self._filter_status = None
        self._setup_ui()
        self.refresh_tasks()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("OPERATIONAL TASKS")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        subtitle = QLabel("Direct mission objectives, priority deadlines & productivity goals.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        # New Task Button
        add_btn = QPushButton("+ NEW OBJECTIVE")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._open_add_dialog)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Filter Chips Bar
        filters = QHBoxLayout()
        filters.setSpacing(10)
        self._btn_all = QPushButton("ALL")
        self._btn_all.clicked.connect(lambda: self._set_filter(None))
        self._btn_pending = QPushButton("PENDING")
        self._btn_pending.clicked.connect(lambda: self._set_filter(TaskStatus.PENDING))
        self._btn_completed = QPushButton("COMPLETED")
        self._btn_completed.clicked.connect(lambda: self._set_filter(TaskStatus.COMPLETED))

        filters.addWidget(self._btn_all)
        filters.addWidget(self._btn_pending)
        filters.addWidget(self._btn_completed)
        filters.addStretch()

        # Quick Add Input Bar
        self._quick_input = QLineEdit()
        self._quick_input.setPlaceholderText("Quick task title (press Enter to create)...")
        self._quick_input.returnPressed.connect(self._quick_create_task)
        filters.addWidget(self._quick_input, stretch=1)

        layout.addLayout(filters)

        # Task List Area
        self._task_list = QListWidget()
        self._task_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 6px;
                margin-bottom: 4px;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.02);
            }}
            QListWidget::item:hover {{
                background-color: rgba(0, 240, 255, 0.06);
            }}
        """)
        layout.addWidget(self._task_list)

    def _set_filter(self, status):
        self._filter_status = status
        self.refresh_tasks()

    def refresh_tasks(self):
        self._task_list.clear()
        tasks = self._tm.list_tasks(status=self._filter_status)

        if not tasks:
            empty_item = QListWidgetItem("No operational objectives found for this filter.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor(148, 163, 184))
            self._task_list.addItem(empty_item)
            return

        for task in tasks:
            item_widget = self._create_task_item_widget(task)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self._task_list.addItem(list_item)
            self._task_list.setItemWidget(list_item, item_widget)

    def _create_task_item_widget(self, task: Task) -> QWidget:
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 26, 43, 0.9);
                border: 1px solid #1E2C48;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Priority marker
        prio_colors = {
            TaskPriority.URGENT: "#FF0055",
            TaskPriority.HIGH: "#FFB703",
            TaskPriority.MEDIUM: "#00F0FF",
            TaskPriority.LOW: "#64748B",
        }
        prio_color = prio_colors.get(task.priority, "#00F0FF")
        prio_label = QLabel(f"[{task.priority.value[:3]}]")
        prio_label.setStyleSheet(f"color: {prio_color}; font-weight: bold; font-family: Consolas;")
        layout.addWidget(prio_label)

        # Title & Category
        title_box = QVBoxLayout()
        title_label = QLabel(task.title)
        is_done = task.status == TaskStatus.COMPLETED
        if is_done:
            title_label.setStyleSheet("color: #64748B; text-decoration: line-through; font-size: 11pt;")
        else:
            title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11pt; font-weight: 600;")
        title_box.addWidget(title_label)

        meta_text = f"Category: {task.category}"
        if task.due_at:
            meta_text += f"  ·  Due: {task.due_at.strftime('%a, %b %d at %I:%M %p')}"
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet("color: #94A3B8; font-size: 8.5pt;")
        title_box.addWidget(meta_label)
        layout.addLayout(title_box, stretch=1)

        # Complete / Delete actions
        if not is_done:
            done_btn = QPushButton("✓ Done")
            done_btn.setStyleSheet(f"color: {SUCCESS}; border-color: rgba(0, 255, 157, 0.4);")
            done_btn.clicked.connect(lambda _, tid=task.id: self._complete_task(tid))
            layout.addWidget(done_btn)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("dangerBtn")
        del_btn.setFixedWidth(32)
        del_btn.clicked.connect(lambda _, tid=task.id: self._delete_task(tid))
        layout.addWidget(del_btn)

        return widget

    def _quick_create_task(self):
        text = self._quick_input.text().strip()
        if text:
            self._tm.add_task(title=text)
            self._quick_input.clear()
            self.refresh_tasks()

    def _open_add_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("New Objective")
        dlg.resize(400, 260)
        dlg_layout = QVBoxLayout(dlg)

        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Objective title...")
        dlg_layout.addWidget(QLabel("Title:"))
        dlg_layout.addWidget(title_edit)

        prio_combo = QComboBox()
        for p in TaskPriority:
            prio_combo.addItem(p.value, p)
        prio_combo.setCurrentText("MEDIUM")
        dlg_layout.addWidget(QLabel("Priority:"))
        dlg_layout.addWidget(prio_combo)

        due_edit = QLineEdit()
        due_edit.setPlaceholderText("e.g. 'tomorrow 7pm', 'in 3 hours', 'Friday'")
        dlg_layout.addWidget(QLabel("Due Time (Natural text):"))
        dlg_layout.addWidget(due_edit)

        btn_box = QHBoxLayout()
        create_btn = QPushButton("Create Objective")
        create_btn.setObjectName("primaryBtn")
        create_btn.clicked.connect(lambda: self._submit_dialog(dlg, title_edit.text(), prio_combo.currentText(), due_edit.text()))
        btn_box.addWidget(create_btn)
        dlg_layout.addLayout(btn_box)
        dlg.exec()

    def _submit_dialog(self, dlg, title, priority, due):
        if title.strip():
            self._tm.add_task(title=title.strip(), priority=priority, due_at=due.strip() or None)
            dlg.accept()
            self.refresh_tasks()

    def _complete_task(self, task_id):
        self._tm.complete_task(task_id)
        self.refresh_tasks()

    def _delete_task(self, task_id):
        self._tm.delete_task(task_id)
        self.refresh_tasks()
