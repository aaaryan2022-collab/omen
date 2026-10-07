# ============================================
"""
OMEN Calendar & Schedule Deck.
Clean agenda and time-block interface.
Features:
- Current date & upcoming timeline
- Time-block slots (Morning, Afternoon, Evening)
- Interactive event creator
- Quick filters (Today, This Week)
- Toast notifications
"""

from datetime import datetime, date, timedelta
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QDialog, QComboBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from productivity.tasks import parse_natural_date
from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_DIM, BACKGROUND_DARK, BACKGROUND_CARD,
)


class AgendaEventCard(QFrame):
    """Clean scheduled agenda item."""

    delete_requested = Signal(str)

    def __init__(self, event_id: str, title: str, time_str: str, tag: str = "Meeting", parent=None):
        super().__init__(parent)
        self._id = event_id
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 10px 14px;
            }
            QFrame:hover {
                border-color: rgba(0, 210, 238, 0.25);
                background-color: rgba(27, 27, 36, 0.90);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Time
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet(f"color: {PRIMARY}; font-size: 12.5px; font-weight: bold; font-family: Consolas;")
        layout.addWidget(time_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        layout.addWidget(title_lbl, stretch=1)

        # Tag
        tag_lbl = QLabel(tag)
        tag_lbl.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.05);
                color: #A1A1AA;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
            }
        """)
        layout.addWidget(tag_lbl)

        # Del
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("border:none; color:#71717A; font-size:11px;")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._id))
        layout.addWidget(del_btn)


class CalendarView(QWidget):
    """Clean agenda calendar interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events = [
            {"id": "ev1", "title": "System Architecture Review with OMEN", "time": "09:30 AM", "tag": "Focus"},
            {"id": "ev2", "title": "Productivity Sprint & Code Review", "time": "02:00 PM", "tag": "Development"},
            {"id": "ev3", "title": "Daily Standup & Objective Alignment", "time": "05:00 PM", "tag": "Sync"},
        ]
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("calendarView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        t_lbl = QLabel("Calendar & Schedule")
        t_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_box.addWidget(t_lbl)

        today_str = datetime.now().strftime("%A, %B %d, %Y")
        sub_lbl = QLabel(f"Today is {today_str} · 3 scheduled events")
        sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)
        header.addStretch()

        layout.addLayout(header)

        # Quick Add Event Bar
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

        self._input_title = QLineEdit()
        self._input_title.setPlaceholderText("Schedule an event (e.g. 'Deep Work Session at 4pm')...")
        self._input_title.setStyleSheet("background: transparent; border: none; font-size: 13px;")
        self._input_title.returnPressed.connect(self._add_event)
        add_layout.addWidget(self._input_title, stretch=1)

        self._tag_select = QComboBox()
        self._tag_select.addItems(["Focus", "Meeting", "Development", "Personal"])
        add_layout.addWidget(self._tag_select)

        add_btn = QPushButton("＋ Add Event")
        add_btn.setObjectName("primaryBtn")
        add_btn.setFixedSize(96, 32)
        add_btn.clicked.connect(self._add_event)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_bar)

        # Scroll Area for Agenda items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self._event_container = QWidget()
        self._event_container.setStyleSheet("background: transparent;")
        self._event_layout = QVBoxLayout(self._event_container)
        self._event_layout.setContentsMargins(0, 0, 0, 0)
        self._event_layout.setSpacing(8)
        self._event_layout.addStretch()

        scroll.setWidget(self._event_container)
        layout.addWidget(scroll, stretch=1)

        self._render_events()

    def _render_events(self):
        while self._event_layout.count() > 1:
            item = self._event_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, ev in enumerate(self._events):
            card = AgendaEventCard(ev["id"], ev["title"], ev["time"], ev["tag"])
            card.delete_requested.connect(self._delete_event)
            self._event_layout.insertWidget(idx, card)

    def _add_event(self):
        text = self._input_title.text().strip()
        if not text:
            return
        tag = self._tag_select.currentText()
        time_str = "03:00 PM"
        parsed = parse_natural_date(text)
        if parsed:
            time_str = parsed.strftime("%I:%M %p")

        ev_id = f"ev_{int(datetime.now().timestamp())}"
        self._events.append({"id": ev_id, "title": text, "time": time_str, "tag": tag})
        self._input_title.clear()
        self._render_events()
        ToastManager.show(self.window(), "Calendar updated", level="success")

    def _delete_event(self, ev_id: str):
        self._events = [e for e in self._events if e["id"] != ev_id]
        self._render_events()
        ToastManager.show(self.window(), "Event removed", level="info")
