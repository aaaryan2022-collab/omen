"""
Holographic ARC Reactor / OMEN Command Core.
Renders real-time rotating energy rings, particle pulse waves, and sound-reactive lasers.
"""

import math
from PySide6.QtCore import QTimer, Qt, Signal, QRectF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR


class CommandCore(QWidget):
    """Holographic Sci-Fi ARC Reactor Visualizer with sound-reactive animation."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.setMaximumSize(460, 460)
        self._phase = 0.0
        self._rotation1 = 0.0
        self._rotation2 = 0.0
        self._rotation3 = 0.0
        self._voice_level = 0.0
        self._voice_mode = "idle"  # idle, listening, thinking, speaking, error
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)  # ~33 FPS smooth animation

    def _tick(self):
        self._phase = (self._phase + 0.04) % (math.pi * 2)
        # Counter-rotating rings at different speeds
        self._rotation1 = (self._rotation1 + 1.2) % 360
        self._rotation2 = (self._rotation2 - 1.8) % 360
        self._rotation3 = (self._rotation3 + 0.8) % 360
        # Smooth decay of voice level
        self._voice_level *= 0.88
        self.update()

    def set_voice_mode(self, mode: str):
        self._voice_mode = mode.lower()
        self.update()

    def set_voice_level(self, level: float):
        self._voice_level = max(self._voice_level * 0.5, min(1.0, level))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        base_radius = min(self.width(), self.height()) * 0.42

        # State color resolution
        if self._voice_mode == "listening":
            accent = QColor(0, 240, 255)       # Cyan
            glow_c = QColor(0, 240, 255, 140)
            status_text = "LISTENING"
        elif self._voice_mode == "thinking":
            accent = QColor(255, 183, 3)       # Gold/Amber
            glow_c = QColor(255, 183, 3, 140)
            status_text = "PROCESSING"
        elif self._voice_mode == "speaking":
            accent = QColor(112, 0, 255)       # Violet Neon
            glow_c = QColor(112, 0, 255, 150)
            status_text = "SPEAKING"
        elif self._voice_mode == "error":
            accent = QColor(255, 0, 85)        # Red Alert
            glow_c = QColor(255, 0, 85, 160)
            status_text = "ALERT"
        else:
            accent = QColor(0, 240, 255)       # Default Core Cyan
            glow_c = QColor(0, 240, 255, 90)
            status_text = "ONLINE"

        # Energy pulse calculation from sine wave + audio reactive boost
        energy = self._voice_level if self._voice_mode in ("listening", "speaking") else 0.15
        pulse = 1.0 + math.sin(self._phase) * (0.05 + energy * 0.15)
        radius = base_radius * (1.0 + energy * 0.25)

        # 1. Outer Holographic Glow Field
        glow_grad = QRadialGradient(center_x, center_y, radius * 1.3)
        glow_grad.setColorAt(0.0, glow_c)
        glow_grad.setColorAt(0.35, QColor(accent.red(), accent.green(), accent.blue(), 40))
        glow_grad.setColorAt(0.75, QColor(0, 0, 0, 15))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(center_x - radius * 1.3, center_y - radius * 1.3, radius * 2.6, radius * 2.6))

        # 2. Outer Segmented Ring (Rotating clockwise)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._rotation1)
        outer_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 120), 1.8)
        painter.setPen(outer_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        num_segments = 24
        for i in range(num_segments):
            angle = (i * 360.0 / num_segments) * math.pi / 180.0
            x1 = math.cos(angle) * (radius * 0.95)
            y1 = math.sin(angle) * (radius * 0.95)
            x2 = math.cos(angle) * (radius * 1.02)
            y2 = math.sin(angle) * (radius * 1.02)
            painter.drawLine(x1, y1, x2, y2)
        painter.restore()

        # 3. Middle High-Tech Arc Ring (Rotating counter-clockwise)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._rotation2)
        mid_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 180), 2.5)
        painter.setPen(mid_pen)
        mid_r = radius * 0.78
        for arc_start in (0, 90, 180, 270):
            painter.drawArc(QRectF(-mid_r, -mid_r, mid_r * 2, mid_r * 2), arc_start * 16, 60 * 16)
        painter.restore()

        # 4. Inner Orbit Ring with Laser Beacons
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._rotation3)
        inner_r = radius * 0.55
        painter.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 90), 1.2, Qt.PenStyle.DashLine))
        painter.drawEllipse(QRectF(-inner_r, -inner_r, inner_r * 2, inner_r * 2))
        
        # Draw 3 orbiting energy nodes
        for node_i in range(3):
            n_angle = (node_i * 120.0) * math.pi / 180.0
            nx = math.cos(n_angle) * inner_r
            ny = math.sin(n_angle) * inner_r
            painter.setBrush(QBrush(accent))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(nx - 4, ny - 4, 8, 8))
        painter.restore()

        # 5. Core ARC Reactor Center
        core_r = radius * 0.28 * pulse
        core_grad = QRadialGradient(center_x, center_y, core_r * 1.4)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        core_grad.setColorAt(0.3, accent)
        core_grad.setColorAt(0.7, QColor(accent.red(), accent.green(), accent.blue(), 100))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(QPen(accent, 1.5))
        painter.drawEllipse(QRectF(center_x - core_r, center_y - core_r, core_r * 2, core_r * 2))

        # 6. Center Status Indicator Label
        painter.setPen(QColor(241, 245, 249, 220))
        font = QFont("Consolas", 8, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(
            QRectF(center_x - 60, center_y - 8, 120, 16),
            Qt.AlignmentFlag.AlignCenter,
            status_text,
        )