# ============================================
"""
OMEN Command Core — premium geometric status indicator.
Subtle arcs, breathing pulse, state-driven color.
No neon glow overload, no generic glowing circle.
"""

import math
from PySide6.QtCore import QTimer, Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QRadialGradient, QBrush
from PySide6.QtWidgets import QWidget
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR, TEXT_PRIMARY


class CommandCore(QWidget):
    """Geometric OMEN core: 3 partial arcs + center dot.
    States: idle, listening, thinking, processing, speaking, error."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self.setMaximumSize(260, 260)
        self._phase = 0.0
        self._rotation = 0.0
        self._voice_level = 0.0
        self._voice_mode = "idle"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)  # 50 FPS — lightweight

    def _tick(self):
        self._phase += 0.02
        self._rotation += 0.3
        self._voice_level *= 0.92
        self.update()

    def set_voice_mode(self, mode: str):
        self._voice_mode = mode.lower()
        self.update()

    def set_voice_level(self, level: float):
        self._voice_level = max(0.0, min(1.0, level))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def _get_state_colors(self):
        if self._voice_mode == "listening":
            return PRIMARY, QColor(PRIMARY), "LISTENING"
        elif self._voice_mode == "thinking":
            return WARNING, QColor(WARNING), "THINKING"
        elif self._voice_mode == "speaking":
            return SECONDARY, QColor(SECONDARY), "SPEAKING"
        elif self._voice_mode == "processing":
            return PRIMARY, QColor(PRIMARY), "PROCESSING"
        elif self._voice_mode == "error":
            return ERROR, QColor(ERROR), "ALERT"
        else:
            return PRIMARY, QColor(PRIMARY), "READY"

    def paintEvent(self, event):
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) * 0.40

        accent, accent_qt, status_text = self._get_state_colors()

        # Breathing + voice energy
        energy = self._voice_level if self._voice_mode in ("listening", "speaking") else 0.0
        breath = 0.55 + 0.45 * math.sin(self._phase * 1.5)
        pulse = 1.0 + math.sin(self._phase) * (0.03 + energy * 0.12)

        # 1. Subtle outer glow — very restrained
        glow_r = r * 1.35
        glow = QRadialGradient(cx, cy, glow_r * 0.3)
        glow.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 18))
        glow.setColorAt(0.5, QColor(accent.red(), accent.green(), accent.blue(), 6))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2))

        # 2. Background disc — dark warm tone
        disc_grad = QRadialGradient(cx, cy, r)
        disc_grad.setColorAt(0.0, QColor("#0F0F12"))
        disc_grad.setColorAt(1.0, QColor("#08080A"))
        p.setBrush(QBrush(disc_grad))
        p.setPen(QPen(QColor("#1E1E24"), 0.8))
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # 3. Three partial arcs — geometric, not full circles
        arc_configs = [
            (r * 0.68 * pulse, accent, 1.4, 100),
            (r * 0.88 * pulse, QColor(accent.red(), accent.green(), accent.blue(), 80), 0.8, 60),
            (r * 0.50 * pulse, QColor(SECONDARY[:4] if len(SECONDARY) > 4 else SECONDARY), 1.0, 80),
        ]
        for arc_r, col, width, span in arc_configs:
            pen = QPen(col, width)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            start_angle = int(self._rotation * 16)  # QTimer units (16 = 1deg)
            span_angle = int(span * 16)
            p.drawArc(QRectF(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2),
                      start_angle, span_angle)

        # 4. Inner energy core
        core_r = r * 0.22 * pulse * (0.8 + breath)
        core_grad = QRadialGradient(cx, cy, core_r * 1.4)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 200))
        core_grad.setColorAt(0.3, QColor(accent.red(), accent.green(), accent.blue(), 180))
        core_grad.setColorAt(0.7, QColor(accent.red(), accent.green(), accent.blue(), 60))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(core_grad))
        p.setPen(QPen(accent, 0.5))
        p.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))

        # 5. Listening ring indicator
        if self._voice_mode == "listening":
            ring_r = r * 0.45 * (1.0 + 0.08 * math.sin(self._phase * 3))
            p.setPen(QPen(QColor(PRIMARY), 1.2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

        # 6. Thinking rotation arc
        if self._voice_mode == "thinking":
            think_r = r * 0.75
            p.setPen(QPen(QColor(WARNING), 0.8))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx - think_r, cy - think_r, think_r * 2, think_r * 2),
                      int(self._rotation * 16), 180)

        # 7. Speaking waveform dots
        if self._voice_mode == "speaking":
            dot_r = r * 0.72
            for i in range(6):
                angle = (i * 60 + self._rotation * 2) * math.pi / 180.0
                dx = math.cos(angle) * dot_r
                dy = math.sin(angle) * dot_r
                dot_size = 2.5 + energy * 3.0
                p.setBrush(QBrush(QColor(SECONDARY)))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(cx + dx, cy + dy), dot_size, dot_size)

        # 8. Status text beneath orb
        text_r = r * 1.05
        p.setPen(QColor(TEXT_PRIMARY))
        font = QFont("Segoe UI", 7, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        p.setFont(font)
        tw = p.fontMetrics().horizontalAdvance(status_text)
        p.drawText(QPointF(cx - tw / 2.0, cy + text_r + 14), status_text)

        p.end()
