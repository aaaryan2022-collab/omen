# ============================================
"""
OMEN Home View — Minimal, Focused, Beautiful.
Single centerpiece: Orb + Greeting + Omnibar. Zero clutter.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QPushButton, QSizePolicy, QProgressBar,
)
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QCursor, QLinearGradient

from ui.orb import OmenOrb
import psutil
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, WARNING, ERROR,
    BACKGROUND_DARK, BACKGROUND_CARD, BACKGROUND_HOVER, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, FONT_FAMILY,
)


class GlassCard(QFrame):
    """Clean frosted glass card."""

    def __init__(self, parent=None, radius: int = 14):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background-color: rgba(16, 16, 22, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: {radius}px;
            }}
            QLabel {{ background: transparent; border: none; font-family: {FONT_FAMILY}; }}
        """)


class SystemPill(QFrame):
    """Minimal system status indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 10px;
            }
        """)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(3000)
        self._update()

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(12)

        # Status dot
        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
        lay.addWidget(self._dot)

        self._label = QLabel("System OK")
        self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        lay.addWidget(self._label)

        lay.addStretch()

        # Model badge
        self._model = QLabel("🤖  Local")
        self._model.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; padding: 2px 8px; background: rgba(255,255,255,0.03); border-radius: 6px;")
        lay.addWidget(self._model)

    def _update(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            if cpu > 80 or ram > 85:
                self._dot.setStyleSheet(f"color: {WARNING}; font-size: 10px;")
                self._label.setText(f"High Load · CPU {int(cpu)}% · RAM {int(ram)}%")
                self._label.setStyleSheet(f"color: {WARNING}; font-size: 12px;")
            else:
                self._dot.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
                self._label.setText("System OK")
                self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        except Exception:
            pass


class VoicePill(QFrame):
    """Minimal voice status capsule."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 10px;
            }
            QFrame:hover {
                background: rgba(0, 210, 238, 0.05);
                border-color: rgba(0, 210, 238, 0.2);
            }
        """)
        self._build_ui()

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(10)

        self._icon = QLabel("🎙️")
        self._icon.setStyleSheet("font-size: 14px;")
        lay.addWidget(self._icon)

        self._text = QLabel("Voice Ready")
        self._text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        lay.addWidget(self._text)

        lay.addStretch()

        self._hint = QLabel("Click to speak")
        self._hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        lay.addWidget(self._hint)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_state(self, state: str, level: float = 0.0):
        if state == "listening":
            self._text.setText("Listening…")
            self._text.setStyleSheet("color: #00F5FF; font-weight: 600;")
            self._hint.setText("")
            self.setStyleSheet("background: rgba(0, 245, 255, 0.06); border-color: rgba(0, 245, 255, 0.3);")
        elif state == "thinking":
            self._text.setText("Thinking…")
            self._text.setStyleSheet("color: #A855F7; font-weight: 600;")
            self.setStyleSheet("background: rgba(168, 85, 247, 0.06); border-color: rgba(168, 85, 247, 0.3);")
        elif state == "speaking":
            self._text.setText("Speaking…")
            self._text.setStyleSheet("color: #10B981; font-weight: 600;")
            self.setStyleSheet("background: rgba(16, 185, 129, 0.06); border-color: rgba(16, 185, 129, 0.3);")
        else:
            self._text.setText("Voice Ready")
            self._text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 500;")
            self._hint.setText("Click to speak")
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(255, 255, 255, 0.04);
                    border-radius: 10px;
                }
                QFrame:hover {
                    background: rgba(0, 210, 238, 0.05);
                    border-color: rgba(0, 210, 238, 0.2);
                }
            """)


class Omnibar(QFrame):
    """Single unified input bar with mode pills."""

    submit_prompt = Signal(str, list)
    voice_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(720)
        self.setStyleSheet("""
            QFrame {
                background: rgba(16, 16, 22, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 16px;
            }
        """)
        self._mode = "chat"
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        # Input Row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask anything, assign a task, or start a workflow…")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 15px;
                font-family: {FONT_FAMILY};
                padding: 4px 0;
            }}
            QLineEdit::placeholder {{ color: {TEXT_DIM}; }}
        """)
        self._input.returnPressed.connect(self._submit)
        input_row.addWidget(self._input, 1)

        # Mic Button
        self._mic_btn = QPushButton("🎙️")
        self._mic_btn.setFixedSize(40, 40)
        self._mic_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(0, 210, 238, 0.15);
                border-color: #00D2EE;
            }
        """)
        self._mic_btn.clicked.connect(self.voice_toggle_requested.emit)
        input_row.addWidget(self._mic_btn)

        # Send Button
        self._send_btn = QPushButton("↑")
        self._send_btn.setFixedSize(40, 40)
        self._send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #00D2EE);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #06B6D4);
            }
        """)
        self._send_btn.clicked.connect(self._submit)
        input_row.addWidget(self._send_btn)

        lay.addLayout(input_row)

        # Mode Pills Row
        pills_row = QHBoxLayout()
        pills_row.setSpacing(6)

        self._pill_chat = self._make_pill("Chat", "💬", True)
        self._pill_research = self._make_pill("Research", "🔎")
        self._pill_code = self._make_pill("Code", "💻")
        self._pill_computer = self._make_pill("Computer", "🖥️")

        pills_row.addWidget(self._pill_chat)
        pills_row.addWidget(self._pill_research)
        pills_row.addWidget(self._pill_code)
        pills_row.addWidget(self._pill_computer)
        pills_row.addStretch()

        lay.addLayout(pills_row)

    def _make_pill(self, text: str, icon: str, checked: bool = False) -> QPushButton:
        btn = QPushButton(f"{icon}  {text}")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.03);
                color: {TEXT_SECONDARY};
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.07);
                color: {TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background: rgba(0, 210, 238, 0.12);
                color: {PRIMARY};
                border-color: rgba(0, 210, 238, 0.4);
                font-weight: 600;
            }}
        """)
        return btn

    def _submit(self):
        text = self._input.text().strip()
        if not text:
            return

        prefix = ""
        if self._pill_research.isChecked(): prefix = "[Research] "
        elif self._pill_code.isChecked(): prefix = "[Code] "
        elif self._pill_computer.isChecked(): prefix = "[Computer] "

        self._input.clear()
        self.submit_prompt.emit(f"{prefix}{text}", [])


class HomeView(QWidget):
    """Minimal Home View — Orb + Greeting + Omnibar. Nothing else."""

    nav_requested = Signal(str)
    submit_prompt = Signal(str, list)
    voice_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        # Top Row: System Pill (left) + Voice Pill (right)
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        self._system_pill = SystemPill(self)
        top_row.addWidget(self._system_pill, alignment=Qt.AlignmentFlag.AlignLeft)

        top_row.addStretch()

        self._voice_pill = VoicePill(self)
        self._voice_pill.clicked.connect(self.voice_toggle_requested.emit)
        top_row.addWidget(self._voice_pill, alignment=Qt.AlignmentFlag.AlignRight)

        root.addLayout(top_row)
        root.addSpacing(40)

        # Center: Orb + Greeting + Omnibar
        center_col = QVBoxLayout()
        center_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_col.setSpacing(24)

        # Orb
        self._orb = OmenOrb(self, size=200, show_label=True)
        self._orb.clicked.connect(self.voice_toggle_requested.emit)
        self._orb.setToolTip("Click to start voice conversation")
        center_col.addWidget(self._orb, alignment=Qt.AlignmentFlag.AlignCenter)

        # Greeting
        self._greeting = QLabel(self._get_greeting())
        self._greeting.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._greeting.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        center_col.addWidget(self._greeting, alignment=Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        self._subtitle = QLabel("What can I help you with?")
        self._subtitle.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))
        self._subtitle.setStyleSheet(f"color: {TEXT_DIM};")
        center_col.addWidget(self._subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        center_col.addSpacing(16)

        # Omnibar
        self._omnibar = Omnibar(self)
        self._omnibar.submit_prompt.connect(self.submit_prompt.emit)
        self._omnibar.voice_toggle_requested.connect(self.voice_toggle_requested.emit)
        center_col.addWidget(self._omnibar, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addLayout(center_col)
        root.addStretch()

    def _get_greeting(self) -> str:
        hour = datetime.now().hour
        if 4 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"

    def set_voice_state(self, state: str, level: float = 0.0):
        self._orb.set_state(state)
        self._orb.set_voice_level(level)
        self._voice_pill.set_state(state, level)