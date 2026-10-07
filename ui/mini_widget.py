# ============================================
"""
OMEN Desktop Mini Widget.
Ultra-compact floating desktop companion.
Draggable, frameless, translucent glass pill with OMEN orb, microphone button,
and live status indicator. Clicking the orb expands to full interface.
"""

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from ui.orb import OmenOrb
from ui.styles.palette import (
    PRIMARY, SUCCESS, WARNING, TEXT_PRIMARY, TEXT_DIM, GLASS_CARD,
)


class MiniWidget(QWidget):
    """Movable desktop widget with OMEN orb and mic toggle."""

    expand_requested = Signal()
    mic_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(54)
        self.setMinimumWidth(210)

        self._drag_position = QPoint()
        self._build_ui()

    def _build_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self._pill = QFrame()
        self._pill.setObjectName("miniPill")
        self._pill.setStyleSheet("""
            QFrame#miniPill {
                background-color: rgba(14, 14, 20, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 26px;
            }
            QFrame#miniPill:hover {
                border-color: rgba(0, 210, 238, 0.35);
            }
        """)

        layout = QHBoxLayout(self._pill)
        layout.setContentsMargins(8, 6, 12, 6)
        layout.setSpacing(10)

        # 1. Compact OMEN Orb
        self._orb = OmenOrb(size=38, show_label=False)
        self._orb.setCursor(Qt.CursorShape.PointingHandCursor)
        self._orb.clicked.connect(self.expand_requested.emit)
        self._orb.setToolTip("Click to expand OMEN full interface")
        layout.addWidget(self._orb)

        # 2. Text Status Indicator
        self._status_label = QLabel("OMEN · Ready")
        self._status_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11.5px; font-weight: 600;")
        layout.addWidget(self._status_label, stretch=1)

        # 3. Mic Button
        self._mic_btn = QPushButton("🎙")
        self._mic_btn.setFixedSize(30, 30)
        self._mic_btn.setToolTip("Start voice interaction")
        self._mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                color: #00D2EE;
                font-size: 13px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(0, 210, 238, 0.18);
                border-color: #00D2EE;
            }
        """)
        self._mic_btn.clicked.connect(self.mic_clicked.emit)
        layout.addWidget(self._mic_btn)

        # 4. Expand Button
        expand_btn = QPushButton("↗")
        expand_btn.setFixedSize(26, 26)
        expand_btn.setToolTip("Expand to Full Assistant (Ctrl+M)")
        expand_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #71717A;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #F4F4F6;
            }
        """)
        expand_btn.clicked.connect(self.expand_requested.emit)
        layout.addWidget(expand_btn)

        root_layout.addWidget(self._pill)

    def set_state(self, state: str):
        self._orb.set_state(state)
        state_names = {
            "idle": "OMEN · Ready",
            "listening": "Listening...",
            "thinking": "Thinking...",
            "speaking": "Speaking...",
            "processing": "Processing...",
            "error": "Alert",
        }
        text = state_names.get(state.lower(), f"OMEN · {state.capitalize()}")
        self._status_label.setText(text)

        if state.lower() == "listening":
            self._status_label.setStyleSheet("color: #00D2EE; font-size: 11.5px; font-weight: 600;")
        elif state.lower() == "thinking":
            self._status_label.setStyleSheet("color: #FBBF24; font-size: 11.5px; font-weight: 600;")
        else:
            self._status_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11.5px; font-weight: 600;")

    def set_voice_level(self, level: float):
        self._orb.set_voice_level(level)

    # Mouse drag window handling
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
