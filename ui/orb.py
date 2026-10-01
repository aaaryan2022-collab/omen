"""
Holographic ARC Reactor / OMEN Command Core.
3D rotating cube with layered depth rings, chromatic pulse, and sound-reactive lasers.
"""

import math
from PySide6.QtCore import QTimer, Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QLinearGradient, QRadialGradient, QBrush
from PySide6.QtWidgets import QWidget
from ui.styles.palette import PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR


class CommandCore(QWidget):
    """Holographic 3D HologramVisualizer — rotating cube with chromatic rings."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.setMaximumSize(480, 480)
        self._phase = 0.0
        self._rotation = 0.0
        self._voice_level = 0.0
        self._voice_mode = "idle"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)  # 60 FPS

    def _tick(self):
        self._phase += 0.04
        self._rotation += 1.8
        self._voice_level *= 0.85
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

    def _get_state_colors(self):
        if self._voice_mode == "listening":
            return QColor(0, 240, 255), QColor(0, 240, 255, 140), "LISTENING"
        elif self._voice_mode == "thinking":
            return QColor(255, 183, 3), QColor(255, 183, 3, 140), "PROCESSING"
        elif self._voice_mode == "speaking":
            return QColor(112, 0, 255), QColor(112, 0, 255, 150), "SPEAKING"
        elif self._voice_mode == "error":
            return QColor(255, 0, 85), QColor(255, 0, 85, 160), "ALERT"
        else:
            return QColor(0, 240, 255), QColor(0, 240, 255, 90), "ONLINE"

    def paintEvent(self, event):
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) * 0.42

        accent, glow_c, status_text = self._get_state_colors()

        energy = self._voice_level if self._voice_mode in ("listening", "speaking") else 0.12
        pulse = 1.0 + math.sin(self._phase) * (0.05 + energy * 0.18)

        # 1. Outer holographic field
        glow = QRadialGradient(cx, cy, r * 1.4)
        glow.setColorAt(0.0, glow_c)
        glow.setColorAt(0.4, QColor(accent.red(), accent.green(), accent.blue(), 30))
        glow.setColorAt(0.8, QColor(0, 0, 0, 12))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - r * 1.4, cy - r * 1.4, r * 2.8, r * 2.8))

        # 2. Rotating 3D wireframe cube (projected)
        rot = self._rotation
        cube_size = r * 0.75
        points = []
        for px in (-cube_size, cube_size):
            for py in (-cube_size, cube_size):
                for pz in (-cube_size, cube_size):
                    x3 = px
                    y3 = py * 0.707 - pz * 0.707
                    z3 = py * 0.707 + pz * 0.707
                    zfac = 1.0 / (z3 * 0.3 + 3.0)
                    sx = cx + x3 * zfac * 0.5
                    sy = cy + y3 * zfac * 0.5
                    points.append((sx, sy, z3))

        # Edges (12)
        edges = [(0, 1), (2, 3), (4, 5), (6, 7),
                 (0, 4), (1, 5), (2, 6), (3, 7),
                 (0, 2), (1, 3), (4, 6), (5, 7)]
        edge_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 120), 1.6)
        p.setPen(edge_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i, j in edges:
            p.drawLine(points[i][0], points[i][1], points[j][0], points[j][1])

        # 3. Layered rotating rings (chromatic)
        rings = [
            (r * 0.16 * pulse, QColor(accent.red(), accent.green(), accent.blue(), 180), 2.8),
            (r * 0.32 * pulse, QColor(SECONDARY[:4] or "#7000FF"), 1.8),
            (r * 0.55 * pulse, QColor(255, 0, 170, 120), 1.2),
        ]
        for rad, col, width in rings:
            pen = QPen(col, width, Qt.PenStyle.SolidLine)
            p.setPen(pen)
            p.drawEllipse(QRectF(cx - rad, cy - rad, rad * 2, rad * 2))

        # 4. Inner energy core
        core_r = r * 0.28 * pulse
        core_grad = QRadialGradient(cx, cy, core_r * 1.3)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        core_grad.setColorAt(0.25, accent)
        core_grad.setColorAt(0.6, QColor(accent.red(), accent.green(), accent.blue(), 140))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(core_grad))
        p.setPen(QPen(accent, 1.2))
        p.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))

        # 5. Orbiting energy nodes
        node_r = r * 0.58
        for i in range(4):
            angle = (i * 90.0) * math.pi / 180.0 + self._phase * 0.5
            nx = cx + math.cos(angle) * node_r
            ny = cy + math.sin(angle) * node_r
            size = 6.0 + math.sin(self._phase + i) * 2.0
            p.setBrush(QBrush(accent))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(nx - size/2, ny - size/2, size, size))

        # 6. Status text
        p.setPen(QColor(241, 245, 249, 230))
        font = QFont("Consolas", 9, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        p.setFont(font)
        tw = p.fontMetrics().horizontalAdvance(status_text)
        p.drawText(QPointF(cx - tw/2, cy + r * 0.92), status_text)