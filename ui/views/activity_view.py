"""
Activity & System Telemetry View for OMEN.
Displays live action audit logs, process monitors, and hardware state.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
import psutil
from database.repositories import ActionLogRepository
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, ERROR, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class ActivityView(QWidget):
    """System Activity, Action Audit & Process Manager."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audit_repo = ActionLogRepository()
        self._setup_ui()
        self._refresh_all()

        # Telemetry update timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_processes)
        self._timer.start(3000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("SYSTEM TELEMETRY & AUDIT LOGS")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        subtitle = QLabel("Live action audit trail, tool executions, and system process telemetry.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        refresh_btn = QPushButton("↻ REFRESH")
        refresh_btn.clicked.connect(self._refresh_all)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Top Section: Action Logs Table
        log_frame = QFrame()
        log_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        log_layout = QVBoxLayout(log_frame)
        log_label = QLabel("RECENT EXECUTIONS & SECURITY AUDIT TRAIL")
        log_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 9pt; font-family: Consolas;")
        log_layout.addWidget(log_label)

        self._log_table = QTableWidget(0, 5)
        self._log_table.setHorizontalHeaderLabels(["Timestamp", "Tool", "Risk", "Status", "Duration"])
        self._log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._log_table.setStyleSheet("""
            QTableWidget {
                background-color: #0D131F;
                border: none;
                gridline-color: #1A263D;
                color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #121A2B;
                color: #94A3B8;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        log_layout.addWidget(self._log_table)
        layout.addWidget(log_frame, stretch=1)

        # Bottom Section: Process Telemetry Table
        proc_frame = QFrame()
        proc_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        proc_layout = QVBoxLayout(proc_frame)
        proc_label = QLabel("TOP SYSTEM PROCESS CONSUMERS")
        proc_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 9pt; font-family: Consolas;")
        proc_layout.addWidget(proc_label)

        self._proc_table = QTableWidget(0, 4)
        self._proc_table.setHorizontalHeaderLabels(["PID", "Process Name", "Memory %", "CPU %"])
        self._proc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._proc_table.setStyleSheet("""
            QTableWidget {
                background-color: #0D131F;
                border: none;
                gridline-color: #1A263D;
                color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #121A2B;
                color: #94A3B8;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        proc_layout.addWidget(self._proc_table)
        layout.addWidget(proc_frame, stretch=1)

    def _refresh_all(self):
        self._refresh_logs()
        self._refresh_processes()

    def _refresh_logs(self):
        logs = self._audit_repo.list_recent(limit=25)
        self._log_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            time_str = log.timestamp.strftime("%H:%M:%S")
            self._log_table.setItem(row, 0, QTableWidgetItem(time_str))
            self._log_table.setItem(row, 1, QTableWidgetItem(log.tool_name))
            self._log_table.setItem(row, 2, QTableWidgetItem(str(log.risk_level.value if hasattr(log.risk_level, 'value') else log.risk_level)))

            status_item = QTableWidgetItem(log.status)
            if log.status == "SUCCESS":
                status_item.setForeground(QColor(0, 255, 157))
            else:
                status_item.setForeground(QColor(255, 0, 85))
            self._log_table.setItem(row, 3, status_item)

            self._log_table.setItem(row, 4, QTableWidgetItem(f"{log.duration_ms}ms"))

    def _refresh_processes(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        top = sorted(procs, key=lambda x: x.get('memory_percent') or 0, reverse=True)[:15]

        self._proc_table.setRowCount(len(top))
        for row, p in enumerate(top):
            self._proc_table.setItem(row, 0, QTableWidgetItem(str(p.get('pid'))))
            self._proc_table.setItem(row, 1, QTableWidgetItem(str(p.get('name'))))
            mem_pct = round(p.get('memory_percent') or 0, 1)
            self._proc_table.setItem(row, 2, QTableWidgetItem(f"{mem_pct}%"))
            cpu_pct = round(p.get('cpu_percent') or 0, 1)
            self._proc_table.setItem(row, 3, QTableWidgetItem(f"{cpu_pct}%"))
