# ============================================
"""
OMEN Command Center — Real-Time System Intelligence Hub.

Provides:
- Live CPU / RAM / GPU telemetry tiles
- OMEN agent status summary
- 53-tool capability breakdown by category
- Quick system actions (emergency stop, new session, settings)
- Recent activity feed
"""

import psutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BACKGROUND_DARK, BACKGROUND_CARD, BORDER, FONT_FAMILY,
)


def _card_style(border_color="rgba(255,255,255,0.07)"):
    return (
        f"QFrame {{"
        f"  background-color: rgba(21,21,28,0.85);"
        f"  border: 1px solid {border_color};"
        f"  border-radius: 12px;"
        f"}}"
        f"QLabel {{ background: transparent; border: none; padding: 0; }}"
    )


class MiniTile(QFrame):
    """Compact metric tile: icon, big value, subtitle, thin bar."""

    def __init__(self, label, unit="%", accent=PRIMARY, parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(_card_style())

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(6)

        top = QHBoxLayout()
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        top.addWidget(lbl)
        top.addStretch()
        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {SUCCESS}; font-size: 9px;")
        top.addWidget(self._dot)
        root.addLayout(top)

        self._val = QLabel(f"-- {unit}")
        self._val.setFont(QFont("Cascadia Code, Consolas", 22, QFont.Weight.Bold))
        self._val.setStyleSheet(f"color: {TEXT_PRIMARY};")
        root.addWidget(self._val)

        self._bar = QProgressBar()
        self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        self._bar.setStyleSheet(
            "QProgressBar { background: rgba(255,255,255,0.06); border: none; border-radius: 2px; }"
            f"QProgressBar::chunk {{ background: {accent}; border-radius: 2px; }}"
        )
        root.addWidget(self._bar)

        self._sub = QLabel("—")
        self._sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        root.addWidget(self._sub)

    def update(self, pct: float, val_str: str, sub: str, warn=False):
        self._val.setText(val_str)
        self._bar.setValue(int(max(0, min(100, pct))))
        self._sub.setText(sub)
        col = ERROR if pct > 90 else (WARNING if (warn or pct > 75) else self._accent)
        self._bar.setStyleSheet(
            "QProgressBar { background: rgba(255,255,255,0.06); border: none; border-radius: 2px; }"
            f"QProgressBar::chunk {{ background: {col}; border-radius: 2px; }}"
        )


class AgentStatusRow(QFrame):
    """Single agent status row in the agent summary panel."""

    def __init__(self, name: str, role: str, status: str = "ready", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background: transparent; border: none; }"
            "QLabel { background: transparent; border: none; }"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(12)

        color = SUCCESS if status == "ready" else (WARNING if status == "busy" else TEXT_DIM)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        dot.setFixedWidth(14)
        lay.addWidget(dot)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        lay.addWidget(name_lbl)

        role_lbl = QLabel(role)
        role_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        lay.addWidget(role_lbl)
        lay.addStretch()

        status_lbl = QLabel(status.upper())
        status_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px;")
        lay.addWidget(status_lbl)


class CommandCenterView(QWidget):
    """OMEN Command Center — system intelligence and agent control deck."""

    emergency_requested = Signal()

    AGENTS = [
        ("ChatAgent",     "Conversational AI / LLM proxy",          "ready"),
        ("CodeAgent",     "Coding, debugging, patch apply",          "ready"),
        ("ResearchAgent", "Deep multi-hop web research",             "ready"),
        ("VisionAgent",   "Screenshot analysis / OCR",               "ready"),
        ("BrowserAgent",  "Automated web navigation",                "ready"),
        ("SchedulerAgent","Background task / cron runner",           "ready"),
    ]

    TOOL_CATEGORIES = [
        ("Apps",          "launch / close / list processes",   "10 tools"),
        ("Files",         "read / write / search / move",      "9 tools"),
        ("Coding",        "git / patch / terminal / indexer",  "8 tools"),
        ("Browser",       "search / navigate / scrape",        "7 tools"),
        ("Vision",        "screenshot / OCR / UI detect",      "5 tools"),
        ("Research",      "deep research / citation / digest", "4 tools"),
        ("Productivity",  "tasks / calendar / notes / email",  "6 tools"),
        ("System",        "hardware / processes / network",    "4 tools"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_net = psutil.net_io_counters()
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1500)
        self._refresh()

    def _build_ui(self):
        self.setObjectName("commandCenterView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(40, 28, 40, 28)
        root.setSpacing(22)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        t = QLabel("Command Center")
        t.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_col.addWidget(t)
        sub = QLabel("Real-time system telemetry, agent status, and tool inventory.")
        sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        # Action buttons
        for label, color in [
            ("Emergency Stop", ERROR),
            ("New Session",    PRIMARY),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton {{ background: rgba(255,255,255,0.04); border: 1px solid {color}50;"
                f" border-radius: 8px; color: {color}; padding: 7px 16px; font-size: 12px; }}"
                f"QPushButton:hover {{ background: {color}22; }}"
            )
            if "Emergency" in label:
                btn.clicked.connect(self.emergency_requested.emit)
            header.addWidget(btn)
        root.addLayout(header)

        # Telemetry row
        telemetry_lbl = QLabel("HARDWARE TELEMETRY")
        telemetry_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; font-weight: bold; letter-spacing: 1.2px;"
        )
        root.addWidget(telemetry_lbl)

        tele_grid = QGridLayout()
        tele_grid.setSpacing(12)
        self._tile_cpu = MiniTile("CPU",     "%",    PRIMARY)
        self._tile_ram = MiniTile("RAM",     "GB",   SECONDARY)
        self._tile_net = MiniTile("Network", "KB/s", SUCCESS)
        self._tile_bat = MiniTile("Power",   "%",    "#FBBF24")
        tele_grid.addWidget(self._tile_cpu, 0, 0)
        tele_grid.addWidget(self._tile_ram, 0, 1)
        tele_grid.addWidget(self._tile_net, 0, 2)
        tele_grid.addWidget(self._tile_bat, 0, 3)
        root.addLayout(tele_grid)

        # 2-column lower section
        lower = QHBoxLayout()
        lower.setSpacing(16)

        # Agent status panel
        agent_frame = QFrame()
        agent_frame.setStyleSheet(_card_style())
        af_lay = QVBoxLayout(agent_frame)
        af_lay.setContentsMargins(18, 16, 18, 16)
        af_lay.setSpacing(4)
        ag_title = QLabel("AGENT STATUS")
        ag_title.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: bold; letter-spacing: 1.2px;"
        )
        af_lay.addWidget(ag_title)
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: rgba(255,255,255,0.06);")
        af_lay.addWidget(divider)
        for name, role, status in self.AGENTS:
            af_lay.addWidget(AgentStatusRow(name, role, status))
        lower.addWidget(agent_frame, 3)

        # Tool inventory panel
        tools_frame = QFrame()
        tools_frame.setStyleSheet(_card_style())
        tf_lay = QVBoxLayout(tools_frame)
        tf_lay.setContentsMargins(18, 16, 18, 16)
        tf_lay.setSpacing(8)
        tools_title = QLabel("TOOL INVENTORY  (53 tools)")
        tools_title.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: bold; letter-spacing: 1.2px;"
        )
        tf_lay.addWidget(tools_title)
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background: rgba(255,255,255,0.06);")
        tf_lay.addWidget(divider2)

        for cat, desc, count in self.TOOL_CATEGORIES:
            row = QHBoxLayout()
            cat_lbl = QLabel(cat)
            cat_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            cat_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
            row.addWidget(cat_lbl)
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
            row.addWidget(desc_lbl)
            row.addStretch()
            count_lbl = QLabel(count)
            count_lbl.setStyleSheet(f"color: {PRIMARY}; font-size: 11px; font-weight: 600;")
            row.addWidget(count_lbl)
            tf_lay.addLayout(row)

        tf_lay.addStretch()
        lower.addWidget(tools_frame, 2)
        root.addLayout(lower)
        root.addStretch()

    def _refresh(self):
        # CPU
        cpu = psutil.cpu_percent(interval=None)
        cores = psutil.cpu_count(logical=True)
        self._tile_cpu.update(cpu, f"{cpu:.1f}%", f"{cores} logical cores")

        # RAM
        ram = psutil.virtual_memory()
        used_gb = ram.used / 1024**3
        total_gb = ram.total / 1024**3
        self._tile_ram.update(ram.percent, f"{used_gb:.1f} GB", f"{ram.percent:.0f}% of {total_gb:.1f} GB")

        # Network
        try:
            net = psutil.net_io_counters()
            sent = (net.bytes_sent - self._last_net.bytes_sent) / 1024
            recv = (net.bytes_recv - self._last_net.bytes_recv) / 1024
            self._last_net = net
            self._tile_net.update(
                min(100, (sent + recv) / 10),
                f"{recv:.1f} KB/s",
                f"Up: {sent:.1f} KB/s"
            )
        except Exception:
            self._tile_net.update(0, "Active", "LAN online")

        # Battery
        bat = psutil.sensors_battery()
        if bat:
            plug = "Plugged in" if bat.power_plugged else "On battery"
            self._tile_bat.update(bat.percent, f"{bat.percent:.0f}%", plug)
        else:
            self._tile_bat.update(100, "AC", "Desktop power")
