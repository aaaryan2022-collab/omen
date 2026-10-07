# ============================================
"""
Dedicated Voice Interaction Deck for OMEN.
Calm, futuristic, spacious voice dialogue overlay.
Centered OMEN Orb, subtle audio waveform visualization, live transcription,
and instant interruption support.
"""

import math
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from ui.orb import OmenOrb
from ui.styles.palette import (
    PRIMARY, PRIMARY_LIGHT, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, BACKGROUND_DARK,
)


class AudioVisualizer(QWidget):
    """Subtle symmetrical waveform visualizer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setMinimumWidth(320)
        self._level = 0.0
        self._phase = 0.0
        self._bars = 28

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)

    def _tick(self):
        self._phase += 0.12
        self._level *= 0.92
        self.update()

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))
        self.update()

    def paintEvent(self, event):
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        mid_y = h / 2.0
        bar_w = 4.0
        spacing = (w - (self._bars * bar_w)) / (self._bars + 1)

        for i in range(self._bars):
            x = spacing + i * (bar_w + spacing)
            # Symmetrical Gaussian-like envelope
            dist_from_center = abs(i - (self._bars / 2.0)) / (self._bars / 2.0)
            envelope = math.cos(dist_from_center * (math.pi / 2.0))

            wave = math.sin(self._phase + i * 0.35)
            bar_h = 4.0 + (wave * 0.3 + 0.7) * (self._level * 36.0 + 3.0) * envelope

            alpha = int(120 + 135 * envelope * (self._level + 0.2))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 210, 238, min(255, alpha))))
            p.drawRoundedRect(QRectF(x, mid_y - bar_h / 2.0, bar_w, bar_h), 2.0, 2.0)

        p.end()


class VoiceOverlay(QWidget):
    """Dedicated voice mode overlay with centered OMEN orb and transcript."""

    close_requested = Signal()
    interrupted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("voiceOverlay")
        self.setStyleSheet(f"background-color: rgba(9, 9, 12, 0.96);")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Top Bar with Exit
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        exit_btn = QPushButton("✕ Close Voice Mode")
        exit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #A1A1AA;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.12);
                color: #F4F4F6;
            }
        """)
        exit_btn.clicked.connect(self.close_requested.emit)
        top_bar.addWidget(exit_btn)
        layout.addLayout(top_bar)

        layout.addStretch(1)

        # Center Container
        center_box = QVBoxLayout()
        center_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_box.setSpacing(18)

        # 1. Hero OMEN Orb
        self._orb = OmenOrb(size=150, show_label=False)
        self._orb.set_state("listening")
        center_box.addWidget(self._orb, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Status Title
        self._status_label = QLabel("Listening...")
        self._status_label.setStyleSheet(f"""
            color: {PRIMARY};
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        center_box.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. Audio Visualizer
        self._visualizer = AudioVisualizer()
        center_box.addWidget(self._visualizer, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. Live Transcription
        self._transcript_box = QFrame()
        self._transcript_box.setMaximumWidth(580)
        self._transcript_box.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 12px 18px;
            }
        """)
        t_layout = QVBoxLayout(self._transcript_box)
        t_layout.setContentsMargins(10, 10, 10, 10)

        self._transcript_label = QLabel("Speak naturally — OMEN is listening...")
        self._transcript_label.setWordWrap(True)
        self._transcript_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._transcript_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            line-height: 1.5;
        """)
        t_layout.addWidget(self._transcript_label)
        center_box.addWidget(self._transcript_box, alignment=Qt.AlignmentFlag.AlignCenter)

        # 5. Interrupt / Control Hint
        control_row = QHBoxLayout()
        control_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_row.setSpacing(14)

        self._interrupt_btn = QPushButton("⏹ Tap to Interrupt")
        self._interrupt_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid rgba(239, 68, 68, 0.4);
                color: #EF4444;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 12.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.28);
            }
        """)
        self._interrupt_btn.clicked.connect(self.interrupted.emit)
        control_row.addWidget(self._interrupt_btn)

        center_box.addLayout(control_row)
        layout.addLayout(center_box)

        layout.addStretch(1)

        # Footer Hint
        hint_label = QLabel("Press Space to speak · Esc to close")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11.5px;")
        layout.addWidget(hint_label)

    def set_voice_state(self, state: str, text: str = ""):
        state = state.lower()
        self._orb.set_state(state)

        titles = {
            "listening": "Listening...",
            "thinking": "OMEN is thinking...",
            "speaking": "OMEN is responding...",
            "idle": "OMEN Ready",
        }
        self._status_label.setText(titles.get(state, state.capitalize()))

        if state == "speaking":
            self._status_label.setStyleSheet(f"color: {SECONDARY}; font-size: 20px; font-weight: 600;")
        elif state == "thinking":
            self._status_label.setStyleSheet("color: #FBBF24; font-size: 20px; font-weight: 600;")
        else:
            self._status_label.setStyleSheet(f"color: {PRIMARY}; font-size: 20px; font-weight: 600;")

        if text:
            self._transcript_label.setText(text)

    def set_audio_level(self, level: float):
        self._orb.set_voice_level(level)
        self._visualizer.set_level(level)

    def update_transcript(self, text: str):
        self._transcript_label.setText(text)
