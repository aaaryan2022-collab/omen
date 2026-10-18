# ============================================
"""
OMEN Right Inspector Panel — Agent Activity, Live Tools & Context HUD.
Matches the NOVA right-sidebar specification:
- Real-time Agent Activity stepper (sub-steps, active step, progress bar)
- Live Tools execution monitor (Browser, Terminal, File System, Code)
- Recent Tasks quick overview
- Model switch & Voice state pill controls
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QCursor

from productivity.tasks import get_task_manager
from database.models import Task
from app.constants import TaskStatus
from core.events import get_event_bus, EventType
from ui.styles.palette import (
    PRIMARY, PRIMARY_LIGHT, SECONDARY, SUCCESS, WARNING, ERROR,
    BACKGROUND_DARK, BACKGROUND_CARD, BACKGROUND_HOVER, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, FONT_FAMILY,
)


class ActivityStepItem(QWidget):
    """Single step in the Agent Activity stepper."""

    def __init__(self, title: str, status: str = "pending", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 3, 4, 3)
        lay.setSpacing(8)

        # Status icon / indicator
        self._indicator = QLabel()
        self._title_lbl = QLabel(title)
        self._title_lbl.setFont(QFont("Segoe UI", 9.5))

        self.set_status(status)
        lay.addWidget(self._indicator)
        lay.addWidget(self._title_lbl)
        lay.addStretch()

    def set_status(self, status: str):
        if status == "completed":
            self._indicator.setText("✓")
            self._indicator.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: bold;")
            self._title_lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        elif status == "active":
            self._indicator.setText("◉")
            self._indicator.setStyleSheet(f"color: {PRIMARY}; font-size: 11px; font-weight: bold;")
            self._title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600;")
        else:
            self._indicator.setText("○")
            self._indicator.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px;")
            self._title_lbl.setStyleSheet(f"color: {TEXT_DIM};")


class LiveToolItem(QFrame):
    """Active tool execution badge with duration timer."""

    def __init__(self, tool_name: str, detail: str, duration_str: str = "Active", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 6px 10px;
            }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(8)

        icon_map = {
            "browser": "🌐",
            "terminal": "⚡",
            "filesystem": "📁",
            "code": "💻",
            "research": "🔎",
            "vision": "👁️",
        }
        icon = icon_map.get(tool_name.lower(), "🔧")
        i_lbl = QLabel(icon)
        i_lbl.setStyleSheet("font-size: 14px;")
        lay.addWidget(i_lbl)

        col = QVBoxLayout()
        col.setSpacing(1)
        name_lbl = QLabel(tool_name.title())
        name_lbl.setFont(QFont("Segoe UI", 9.5, QFont.Weight.DemiBold))
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        col.addWidget(name_lbl)

        det_lbl = QLabel(detail)
        det_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px;")
        col.addWidget(det_lbl)
        lay.addLayout(col)
        lay.addStretch()

        time_tag = QLabel(duration_str)
        time_tag.setStyleSheet(f"color: {PRIMARY}; font-size: 9.5px; font-weight: 500;")
        lay.addWidget(time_tag)


class SupervisorPanel(QWidget):
    """
    Right Collapsible Inspector & Agent Activity Panel.
    """

    view_all_activity = Signal()
    view_all_tasks = Signal()
    model_switch_requested = Signal()
    voice_toggle_requested = Signal()

    def __init__(self, supervisor=None, parent=None):
        super().__init__(parent)
        self._supervisor = supervisor
        self.setObjectName("supervisorPanel")
        self.setFixedWidth(280)
        self._build_ui()
        self._setup_event_listeners()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget#supervisorPanel {{
                background-color: {BACKGROUND_DARK};
                border-left: 1px solid rgba(255, 255, 255, 0.06);
            }}
            QLabel {{
                font-family: {FONT_FAMILY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(12)

        # -------------------------------------------------------------
        # Section 1: Agent Activity
        # -------------------------------------------------------------
        sec1_hdr = QHBoxLayout()
        s1_title = QLabel("🤖 Agent Activity")
        s1_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        s1_title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        sec1_hdr.addWidget(s1_title)
        sec1_hdr.addStretch()

        s1_link = QPushButton("View all")
        s1_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        s1_link.setStyleSheet(f"background: transparent; color: {PRIMARY}; font-size: 10px; border: none;")
        s1_link.clicked.connect(self.view_all_activity.emit)
        sec1_hdr.addWidget(s1_link)
        layout.addLayout(sec1_hdr)

        self._activity_card = QFrame()
        self._activity_card.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        ac_lay = QVBoxLayout(self._activity_card)
        ac_lay.setContentsMargins(10, 8, 10, 8)
        ac_lay.setSpacing(6)

        self._current_task_lbl = QLabel("Autonomous Agent Standby")
        self._current_task_lbl.setFont(QFont("Segoe UI", 9.5, QFont.Weight.DemiBold))
        self._current_task_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self._current_task_lbl.setWordWrap(True)
        ac_lay.addWidget(self._current_task_lbl)

        self._steps_container = QVBoxLayout()
        self._steps_container.setSpacing(3)
        self._step_items: List[ActivityStepItem] = []
        self._set_default_steps()
        ac_lay.addLayout(self._steps_container)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(3)
        self._progress_bar.setValue(100)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("""
            QProgressBar { background: rgba(255, 255, 255, 0.08); border-radius: 1.5px; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #00D2EE); }
        """)
        ac_lay.addWidget(self._progress_bar)
        layout.addWidget(self._activity_card)

        # -------------------------------------------------------------
        # Section 2: Live Tools
        # -------------------------------------------------------------
        s2_title = QLabel("🔧 Live Tools")
        s2_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        s2_title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(s2_title)

        self._tools_container = QVBoxLayout()
        self._tools_container.setSpacing(6)
        self._tools_container.addWidget(LiveToolItem("browser", "OpenAI documentation", "Live"))
        self._tools_container.addWidget(LiveToolItem("terminal", "Workspace health check", "23s"))
        self._tools_container.addWidget(LiveToolItem("filesystem", "Reading project files", "12s"))
        layout.addLayout(self._tools_container)

        # -------------------------------------------------------------
        # Section 3: Recent Tasks
        # -------------------------------------------------------------
        sec3_hdr = QHBoxLayout()
        s3_title = QLabel("✓ Recent Tasks")
        s3_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        s3_title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        sec3_hdr.addWidget(s3_title)
        sec3_hdr.addStretch()

        s3_link = QPushButton("View all")
        s3_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        s3_link.setStyleSheet(f"background: transparent; color: {PRIMARY}; font-size: 10px; border: none;")
        s3_link.clicked.connect(self.view_all_tasks.emit)
        sec3_hdr.addWidget(s3_link)
        layout.addLayout(sec3_hdr)

        self._tasks_box = QVBoxLayout()
        self._tasks_box.setSpacing(4)
        layout.addLayout(self._tasks_box)
        self.reload_recent_tasks()

        layout.addStretch()

        # -------------------------------------------------------------
        # Section 4: Quick Controls (Model Switch & Voice Toggle)
        # -------------------------------------------------------------
        controls_card = QFrame()
        controls_card.setStyleSheet("""
            QFrame {
                background: rgba(18, 18, 24, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 8px;
            }
        """)
        cc_lay = QVBoxLayout(controls_card)
        cc_lay.setContentsMargins(8, 6, 8, 6)
        cc_lay.setSpacing(6)

        # Model row
        m_row = QHBoxLayout()
        m_lbl = QLabel("🤖 Model: Mistral-Nemo")
        m_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px;")
        m_row.addWidget(m_lbl)
        m_row.addStretch()
        switch_btn = QPushButton("Switch")
        switch_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        switch_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                color: #F4F4F6;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9.5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.16);
            }
        """)
        switch_btn.clicked.connect(self.model_switch_requested.emit)
        m_row.addWidget(switch_btn)
        cc_lay.addLayout(m_row)

        # Voice row
        v_row = QHBoxLayout()
        v_lbl = QLabel("🎙️ Voice: Active")
        v_lbl.setStyleSheet(f"color: {SUCCESS}; font-size: 10px; font-weight: 500;")
        v_row.addWidget(v_lbl)
        v_row.addStretch()
        voice_toggle = QPushButton("Toggle")
        voice_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        voice_toggle.setStyleSheet("""
            QPushButton {
                background: rgba(0, 210, 238, 0.15);
                color: #00D2EE;
                border: 1px solid rgba(0, 210, 238, 0.35);
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9.5px;
            }
            QPushButton:hover {
                background: rgba(0, 210, 238, 0.25);
            }
        """)
        voice_toggle.clicked.connect(self.voice_toggle_requested.emit)
        v_row.addWidget(voice_toggle)
        cc_lay.addLayout(v_row)

        layout.addWidget(controls_card)

    def _set_default_steps(self):
        self._clear_steps()
        steps = [
            ("Searching sources", "completed"),
            ("Analyzing information", "active"),
            ("Compiling report", "pending"),
            ("Finalizing summary", "pending"),
        ]
        for title, status in steps:
            item = ActivityStepItem(title, status)
            self._step_items.append(item)
            self._steps_container.addWidget(item)

    def _clear_steps(self):
        while self._steps_container.count():
            item = self._steps_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._step_items.clear()

    def set_agent_task(self, title: str, steps: List[Dict[str, str]], progress_pct: int = 0):
        self._current_task_lbl.setText(title)
        self._clear_steps()
        for s in steps:
            item = ActivityStepItem(s.get("title", ""), s.get("status", "pending"))
            self._step_items.append(item)
            self._steps_container.addWidget(item)
        self._progress_bar.setValue(progress_pct)

    def reload_recent_tasks(self):
        while self._tasks_box.count():
            item = self._tasks_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tm = get_task_manager()
        tasks = tm.list_tasks(status=TaskStatus.PENDING, limit=4)
        if not tasks:
            tasks = [
                Task(id=1, title="Create project structure", priority="HIGH"),
                Task(id=2, title="Fix authentication bug", priority="MEDIUM"),
                Task(id=3, title="Research UI patterns", priority="LOW"),
            ]
        for t in tasks:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel("○")
            dot.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px;")
            row.addWidget(dot)

            lbl = QLabel(t.title)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px;")
            row.addWidget(lbl)
            row.addStretch()
            self._tasks_box.addLayout(row)

    def _setup_event_listeners(self):
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.TOOL_EXECUTING, self._on_tool_executing)
        except Exception:
            pass

    def _on_tool_executing(self, event):
        tool_name = event.payload.get("tool", "Tool")
        self._current_task_lbl.setText(f"Executing: {tool_name}")
        self._progress_bar.setValue(65)
