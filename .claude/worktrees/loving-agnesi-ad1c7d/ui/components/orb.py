"""OMEN Orb — minimal animated status indicator."""
import math
from PySide6.QtCore import Qt, QTimer, QRectF, Property
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import QWidget

from ui.design.tokens import ACCENT, ACCENT_SOFT, BG, R_SM


class Orb(QWidget):
    """Orb with states: idle, listening, thinking, speaking, processing, error."""

    def __init__(self, parent=None, size=28):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._state = "idle"
        self._t = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)  # 50fps lightweight

    def set_state(self, s: str):
        self._state = s
        self._t = 0.0

    def _tick(self):
        self._t += 0.02
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._state
        cx, cy, r = self.width()/2, self.height()/2, self.width()/2 - 2

        # Core circle — subtle
        p.setPen(QPen(QColor(BG), 0))
        p.setBrush(QBrush(QColor("#0F0F10")))
        p.drawEllipse(QRectF(cx-r, cy-r, 2*r, 2*r))

        # Inner dot — breathing pulse by state
        breath = 0.5 + 0.5 * math.sin(self._t * 2) if s == "idle" else 0.7

        if s == "listening":
            breath = 0.6 + 0.4 * abs(math.sin(self._t * 3))
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#3B82F6"))
            grad.setColorAt(1, QColor("#1E3A8A"))
        elif s == "thinking":
            breath = 0.5 + 0.1 * math.sin(self._t)
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#3B82F6"))
            grad.setColorAt(1, QColor("#0F172A"))
        elif s == "speaking":
            breath = 0.4 + 0.3 * abs(math.sin(self._t * 2.5))
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#60A5FA"))
            grad.setColorAt(1, QColor("#1E40AF"))
        elif s == "processing":
            breath = 0.5 + 0.15 * math.sin(self._t * 4)
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#3B82F6"))
            grad.setColorAt(1, QColor("#0F172A"))
        elif s == "error":
            breath = 0.3 + 0.2 * math.sin(self._t * 1.5)
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#EF4444"))
            grad.setColorAt(1, QColor("#7F1D1D"))
        else:  # idle
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0, QColor("#3B82F6"))
            grad.setColorAt(1, QColor("#0F172A"))

        dot_r = max(2, r * breath * 0.7)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(ACCENT).lighter(120), 0.5))
        p.drawEllipse(QRectF(cx - dot_r, cy - dot_r, 2*dot_r, 2*dot_r))
