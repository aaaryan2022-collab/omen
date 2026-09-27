"""
Holographic Command Deck & Telemetry Dashboard for OMEN.
"""

from datetime import datetime
import psutil
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame, QGridLayout,
)
from app.hardware import get_hardware_profile
from core.agent import Agent
from core.events import EventType, get_event_bus
from ui.orb import CommandCore
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, WARNING, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class DashboardView(QWidget):
    """Futuristic Command Deck with live telemetry and voice controls."""

    voice_requested = Signal()
    continuous_voice_requested = Signal()
    chat_requested = Signal()
    vision_requested = Signal()
    tasks_requested = Signal()
    briefing_requested = Signal()

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._build_ui()
        self._connect_events()

    def _build_ui(self):
        self.setObjectName("dashboardView")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(18)

        # 1. Header Bar with Brand & Live Clock
        header = QHBoxLayout()
        brand_box = QVBoxLayout()
        brand_label = QLabel("OMEN COMMAND DECK")
        brand_label.setObjectName("hudBrand")
        brand_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        brand_label.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 3px;")
        brand_box.addWidget(brand_label)

        subtitle = QLabel("LOCAL AUTONOMOUS INTELLIGENCE & HARDWARE MATRIX")
        subtitle.setObjectName("hudSubtitle")
        brand_box.addWidget(subtitle)
        header.addLayout(brand_box)
        header.addStretch()

        clock_box = QVBoxLayout()
        self._time_label = QLabel()
        self._time_label.setObjectName("hudTime")
        self._date_label = QLabel()
        self._date_label.setObjectName("hudDate")
        clock_box.addWidget(self._time_label, alignment=Qt.AlignmentFlag.AlignRight)
        clock_box.addWidget(self._date_label, alignment=Qt.AlignmentFlag.AlignRight)
        header.addLayout(clock_box)
        layout.addLayout(header)

        # 2. Live Telemetry HUD Bar (4 Cards: CPU, RAM, DISK, BATTERY/GPU)
        telemetry_grid = QHBoxLayout()
        telemetry_grid.setSpacing(14)

        self._card_cpu = self._create_telemetry_card("CPU LOAD", "-- %", "Multicore Active")
        self._card_ram = self._create_telemetry_card("SYSTEM MEMORY", "-- GB", "Host RAM Usage")
        self._card_disk = self._create_telemetry_card("LOCAL STORAGE", "-- GB", "Primary Drive Free")
        self._card_gpu = self._create_telemetry_card("GPU ENGINE", "ONLINE", "RTX Acceleration")

        telemetry_grid.addWidget(self._card_cpu["frame"])
        telemetry_grid.addWidget(self._card_ram["frame"])
        telemetry_grid.addWidget(self._card_disk["frame"])
        telemetry_grid.addWidget(self._card_gpu["frame"])
        layout.addLayout(telemetry_grid)

        # 3. Center Holographic Core Section
        layout.addStretch(1)
        core_box = QVBoxLayout()
        core_box.setSpacing(14)
        self._core = CommandCore()
        self._core.setCursor(Qt.CursorShape.PointingHandCursor)
        self._core.setToolTip("Click to activate Voice Dialogue")
        self._core.clicked.connect(self.voice_requested.emit)
        core_box.addWidget(self._core, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._status_label = QLabel("SYSTEM IDLE · AWAITING VOICE INPUT")
        self._status_label.setObjectName("hudStatus")
        self._status_label.setStyleSheet("color: #00F0FF; font-family: Consolas; font-weight: bold; letter-spacing: 2px;")
        core_box.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(core_box)
        layout.addStretch(1)

        # 4. Quick Action Command Deck
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 26, 43, 0.65);
                border: 1px solid #1E2C48;
                border-radius: 14px;
                padding: 10px 16px;
            }
        """)
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setSpacing(12)

        btn_convo = QPushButton("🎙 2-WAY VOICE CONVO")
        btn_convo.setObjectName("primaryBtn")
        btn_convo.setToolTip("Start continuous conversational voice loop (human-to-human flow)")
        btn_convo.clicked.connect(self.continuous_voice_requested.emit)
        actions_layout.addWidget(btn_convo)

        btn_vision = QPushButton("👁 SCREEN SCAN")
        btn_vision.clicked.connect(self.vision_requested.emit)
        actions_layout.addWidget(btn_vision)

        btn_brief = QPushButton("🌅 DAILY BRIEFING")
        btn_brief.clicked.connect(self.briefing_requested.emit)
        actions_layout.addWidget(btn_brief)

        btn_chat = QPushButton("💬 CHAT MATRIX")
        btn_chat.clicked.connect(self.chat_requested.emit)
        actions_layout.addWidget(btn_chat)

        layout.addWidget(actions_frame)

        # Timers
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._refresh_clock)
        self._clock_timer.start(1000)
        self._refresh_clock()

        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._refresh_telemetry)
        self._telemetry_timer.start(2500)
        self._refresh_telemetry()

    def _create_telemetry_card(self, title: str, val: str, sub: str) -> dict:
        frame = QFrame()
        frame.setObjectName("hudCard")
        frame.setStyleSheet("""
            QFrame#hudCard {
                background-color: rgba(18, 26, 43, 0.85);
                border: 1px solid #1E2C48;
                border-radius: 10px;
                padding: 10px 14px;
            }
            QFrame#hudCard:hover {
                border: 1px solid #00F0FF;
            }
        """)
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(4, 4, 4, 4)
        v_layout.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 8pt; font-weight: bold; letter-spacing: 1.5px; font-family: Consolas;")
        v_layout.addWidget(lbl_title)

        lbl_val = QLabel(val)
        lbl_val.setStyleSheet("color: #00F0FF; font-size: 14pt; font-weight: bold; font-family: Consolas;")
        v_layout.addWidget(lbl_val)

        lbl_sub = QLabel(sub)
        lbl_sub.setStyleSheet("color: #94A3B8; font-size: 8pt;")
        v_layout.addWidget(lbl_sub)

        return {"frame": frame, "val": lbl_val, "sub": lbl_sub}

    def _connect_events(self):
        try:
            get_event_bus().subscribe(EventType.AGENT_STATE_CHANGE, self._on_agent_state)
        except Exception:
            pass

    def _refresh_clock(self):
        now = datetime.now()
        self._time_label.setText(now.strftime("%I:%M:%S %p"))
        self._date_label.setText(now.strftime("%A, %B %d, %Y").upper())

    def _refresh_telemetry(self):
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            self._card_cpu["val"].setText(f"{cpu}%")

            mem = psutil.virtual_memory()
            used_gb = round(mem.used / (1024**3), 1)
            total_gb = round(mem.total / (1024**3), 1)
            self._card_ram["val"].setText(f"{used_gb}/{total_gb} GB")

            disk = psutil.disk_usage("C:\\" if psutil.WINDOWS else "/")
            free_gb = round(disk.free / (1024**3), 1)
            self._card_disk["val"].setText(f"{free_gb} GB")

            profile = get_hardware_profile()
            gpu_name = profile.gpu_name or "CPU Mode"
            if len(gpu_name) > 16:
                gpu_name = gpu_name[:16] + ".."
            self._card_gpu["val"].setText(gpu_name)
        except Exception:
            pass

    def _on_agent_state(self, event):
        state = event.payload.get("state", "").replace("_", " ")
        if state:
            self._status_label.setText(f"OMEN STATE · {state}")
            self._core.set_voice_mode(state.lower())

    def set_voice_mode(self, mode: str):
        self._core.set_voice_mode(mode)
        if mode == "listening":
            self._status_label.setText("LISTENING FOR VOICE COMMAND...")
        elif mode == "thinking":
            self._status_label.setText("PROCESSING NEURAL RESPONSE...")
        elif mode == "speaking":
            self._status_label.setText("OMEN VOCAL SYNTHESIS ACTIVE...")
        else:
            self._status_label.setText("SYSTEM ONLINE · READY")
