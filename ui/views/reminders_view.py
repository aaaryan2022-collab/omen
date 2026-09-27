"""
Reminders & Alarms View — Timeline Alert Deck.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from productivity.reminders import get_reminder_manager
from database.models import Reminder
from ui.styles.palette import PRIMARY, SECONDARY, WARNING, ERROR, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class RemindersView(QWidget):
    """Futuristic Scheduled Reminders & Alert Hub."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rm = get_reminder_manager()
        self._setup_ui()
        self.refresh_reminders()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("SCHEDULED ALERTS & REMINDERS")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        subtitle = QLabel("Autonomous cron alarms, verbal reminders & priority triggers.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # Quick Add Reminder Bar
        quick_box = QHBoxLayout()
        quick_box.setSpacing(10)
        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Reminder alert (e.g., 'Take medication', 'Join team standup')...")
        self._time_input = QLineEdit()
        self._time_input.setPlaceholderText("Trigger time (e.g., 'in 25 minutes', 'tomorrow 9am')...")
        self._time_input.returnPressed.connect(self._create_reminder)

        add_btn = QPushButton("+ SCHEDULE ALERT")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._create_reminder)

        quick_box.addWidget(self._title_input, stretch=2)
        quick_box.addWidget(self._time_input, stretch=1)
        quick_box.addWidget(add_btn)
        layout.addLayout(quick_box)

        # Reminders List
        self._reminders_list = QListWidget()
        self._reminders_list.setStyleSheet(f"""
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
        layout.addWidget(self._reminders_list)

    def refresh_reminders(self):
        self._reminders_list.clear()
        reminders = self._rm.list_active()

        if not reminders:
            empty_item = QListWidgetItem("No active scheduled alerts in buffer.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor(148, 163, 184))
            self._reminders_list.addItem(empty_item)
            return

        for reminder in reminders:
            item_widget = self._create_reminder_widget(reminder)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self._reminders_list.addItem(list_item)
            self._reminders_list.setItemWidget(list_item, item_widget)

    def _create_reminder_widget(self, reminder: Reminder) -> QWidget:
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

        icon_label = QLabel("⏰")
        icon_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(icon_label)

        title_box = QVBoxLayout()
        title_label = QLabel(reminder.title)
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11pt; font-weight: 600;")
        title_box.addWidget(title_label)

        time_str = reminder.trigger_time.strftime("%A, %b %d at %I:%M %p")
        meta_label = QLabel(f"Triggers: {time_str}  ·  Status: {reminder.status.value}")
        meta_label.setStyleSheet(f"color: {PRIMARY}; font-size: 8.5pt; font-family: Consolas;")
        title_box.addWidget(meta_label)
        layout.addLayout(title_box, stretch=1)

        del_btn = QPushButton("Cancel")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(lambda _, rid=reminder.id: self._cancel_reminder(rid))
        layout.addWidget(del_btn)

        return widget

    def _create_reminder(self):
        title = self._title_input.text().strip()
        trigger_time = self._time_input.text().strip()
        if title and trigger_time:
            self._rm.set_reminder(title=title, trigger_time=trigger_time)
            self._title_input.clear()
            self._time_input.clear()
            self.refresh_reminders()

    def _cancel_reminder(self, reminder_id):
        self._rm.delete_reminder(reminder_id)
        self.refresh_reminders()
