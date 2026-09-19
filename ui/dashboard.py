# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Home dashboard with system metrics, greeting, and status overview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from app.config import config
from app.logging_config import logger
from core.agent import Agent
from core.events import get_event_bus, EventType
from ui.styles.palette import (
    PRIMARY, BACKGROUND_DARK, BACKGROUND_MEDIUM, BACKGROUND_CARD,
    TEXT_PRIMARY, TEXT_SECONDARY, SUCCESS, WARNING, ERROR, FONT_SIZE_DEFAULT,
    FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, SPACING_DEFAULT, SPACING_LARGE, SPACING_XLARGE,
)


class DashboardView(QWidget):
    """
    Dashboard showing system telemetry, active tasks, reminders, and OMEN status.
    """

    refresh_requested = Signal()

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._setup_ui()
        self._setup_timers()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING_LARGE)
        layout.setContentsMargins(SPACING_XLARGE, SPACING_LARGE, SPACING_XLARGE, SPACING_LARGE)

        # Greeting
        greeting_layout = QHBoxLayout()
        self._greeting_label = QLabel("Good evening")
        self._greeting_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self._greeting_label.setStyleSheet(f"color: {PRIMARY};")
        greeting_layout.addWidget(self._greeting_label)

        self._status_label = QLabel("● Online")
        self._status_label.setStyleSheet(f"color: {SUCCESS}; font-size: 12pt;")
        greeting_layout.addStretch()
        greeting_layout.addWidget(self._status_label)
        layout.addLayout(greeting_layout)

        # System metrics grid
        layout.addWidget(self._build_section_label("System Status"))
        self._metric_grid = QGridLayout()
        self._metric_grid.setSpacing(SPACING_DEFAULT)

        self._cpu_label = QLabel("CPU: —")
        self._ram_label = QLabel("RAM: —")
        self._disk_label = QLabel("Disk: —")
        self._battery_label = QLabel("Battery: —")
        self._uptime_label = QLabel("Uptime: —")

        for widget in [self._cpu_label, self._ram_label, self._disk_label, self._battery_label, self._uptime_label]:
            widget.setStyleSheet(f"""
                QLabel {{
                    background-color: {BACKGROUND_CARD};
                    border: 1px solid #2A3A56;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                    font-size: 13pt;
                }}
            """)
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self._metric_grid.addWidget(self._cpu_label, 0, 0)
        self._metric_grid.addWidget(self._ram_label, 0, 1)
        self._metric_grid.addWidget(self._disk_label, 0, 2)
        self._metric_grid.addWidget(self._battery_label, 1, 0)
        self._metric_grid.addWidget(self._uptime_label, 1, 1)
        layout.addLayout(self._metric_grid)

        # Quick stats
        layout.addWidget(self._build_section_label("Quick Overview"))
        self._overview_label = QLabel("System running normally. No tasks due.")
        self._overview_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12pt;")
        self._overview_label.setWordWrap(True)
        layout.addWidget(self._overview_label)
        layout.addStretch()

    def _build_section_label(self, text: str) -> QLabel:
        label = QLabel(text.upper())
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 4px 0; letter-spacing: 1px;")
        return label

    def _setup_timers(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_metrics)
        self._refresh_timer.start(5000)  # Every 5 seconds
        self._refresh_metrics()

    def _connect_signals(self):
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_agent_state)
        except Exception:
            pass

    def _on_agent_state(self, event):
        state = event.payload.get("state", "")
        self._status_label.setText(f"● {state}")

    def _refresh_metrics(self):
        try:
            import psutil
            cpu_pct = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()

            self._cpu_label.setText(f"CPU: {cpu_pct:.1f}%")
            self._ram_label.setText(f"RAM: {ram.percent:.1f}%")
            self._disk_label.setText(f"Disk: {disk.percent:.1f}%")

            if battery:
                self._battery_label.setText(
                    f"Battery: {battery.percent}% {'🔋' if battery.power_plugged else '⚡'}"
                )
            else:
                self._battery_label.setText("Battery: N/A")

            self._uptime_label.setText("Uptime: System active")
        except Exception as e:
            logger.debug(f"Metric refresh: {e}")

    def update_greeting(self, text: str):
        self._greeting_label.setText(text)


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
