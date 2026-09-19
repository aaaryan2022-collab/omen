"""
Supervisor panel — PySide6 widget for modular oversight monitoring.
No Stark artifacts.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.supervisor import Supervisor
from ui.styles.palette import PRIMARY, BACKGROUND_DARK, BACKGROUND_CARD, TEXT_PRIMARY, SPACING_DEFAULT, SPACING_LARGE


class SupervisorPanel(QWidget):
    """UI panel for supervisor oversight state and recovery actions."""

    recovery_requested = Signal(str)

    def __init__(self, supervisor: Supervisor, parent=None):
        super().__init__(parent)
        self._supervisor = supervisor
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT)
        layout.setSpacing(SPACING_LARGE)

        header = QLabel("Supervisor")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {PRIMARY};")
        layout.addWidget(header)

        status_frame = QFrame()
        status_frame.setStyleSheet(f"background-color: {BACKGROUND_CARD}; border-radius: 8px; padding: 12px;")
        status_layout = QVBoxLayout(status_frame)

        self._state_label = QLabel("State: Monitoring")
        self._state_label.setStyleSheet("color: #00D4AA; font-weight: bold; font-size: 12pt;")
        status_layout.addWidget(self._state_label)

        self._log_text = QTextEdit()
        self._log_text.setMaximumHeight(120)
        self._log_text.setPlaceholderText("Supervisor state log...")
        status_layout.addWidget(self._log_text)

        layout.addWidget(status_frame)

        btn_layout = QHBoxLayout()
        recover_btn = QPushButton("Recover")
        recover_btn.setObjectName("primaryBtn")
        recover_btn.clicked.connect(lambda: self.recovery_requested.emit("manual_recovery"))
        btn_layout.addWidget(recover_btn)
        layout.addLayout(btn_layout)

    def update_state(self, state_text: str):
        self._state_label.setText(f"State: {state_text}")
        self._log_text.append(state_text)
