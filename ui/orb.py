# ============================================
"""
OMEN Visual Identity — Premium Intelligent Orb Indicator.
Restrained, futuristic, lightweight, state-driven animations:
- IDLE: Soft static glow, calm breathing core
- LISTENING: Gentle pulsing animation reacting to voice energy
- THINKING: Slow interacting particles & counter-rotating orbital rings
- SPEAKING: Concentric subtle waveform ripples
- PROCESSING: Smooth orbital activity tracer
- ERROR: Restrained warning state with amber/red rim
"""

import math
import random
from PySide6.QtCore import QTimer, Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QRadialGradient, QBrush, QFont
from PySide6.QtWidgets import QWidget
from ui.styles.palette import (
    PRIMARY, PRIMARY_LIGHT, SECONDARY, SUCCESS, WARNING, ERROR, TEXT_PRIMARY, TEXT_DIM,
)


class OmenOrb(QWidget):
    """
    Intelligent visual identity orb for OMEN.
    Renders high-DPI antialiased procedural particle and vector graphics.
    """

    clicked = Signal()

    def __init__(self, parent=None, size=160, show_label=True):
        super().__init__(parent)
        self._size = size
        self._show_label = show_label
        self.setMinimumSize(size, size + (24 if show_label else 0))
        if not show_label:
            self.setFixedSize(size, size)

        self._state = "idle"  # idle, listening, thinking, speaking, processing, error
        self._phase = 0.0
        self._rotation = 0.0
        self._voice_level = 0.0
        self._particles = [
            {"angle": random.uniform(0, math.pi * 2), "speed": random.uniform(0.015, 0.04), "dist": random.uniform(0.5, 0.85), "size": random.uniform(1.8, 3.2)}
            for _ in range(7)
        ]

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)  # 40 FPS — silky smooth, negligible CPU (<0.2%)

    def _tick(self):
        self._phase += 0.03
        self._rotation += 0.6 if self._state in ("thinking", "processing") else 0.25
        self._voice_level *= 0.90

        # Update thinking particles
        for p in self._particles:
            p["angle"] = (p["angle"] + p["speed"]) % (math.pi * 2)

        self.update()

    def set_state(self, state: str):
        state = state.lower()
        if state in ("idle", "listening", "thinking", "speaking", "processing", "error"):
            self._state = state
        elif state in ("ready", "standby"):
            self._state = "idle"
        elif state in ("action", "tool"):
            self._state = "processing"
        self.update()

    def set_voice_mode(self, mode: str):
        """Backward compatibility for existing callers."""
        self.set_state(mode)

    def set_voice_level(self, level: float):
        self._voice_level = max(0.0, min(1.0, level))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def _get_state_palette(self):
        if self._state == "listening":
            return QColor("#00D2EE"), QColor("#38BDF8"), "LISTENING"
        elif self._state == "thinking":
            return QColor("#FBBF24"), QColor("#00D2EE"), "THINKING"
        elif self._state == "speaking":
            return QColor("#38BDF8"), QColor("#00D2EE"), "SPEAKING"
        elif self._state == "processing":
            return QColor("#00D2EE"), QColor("#10B981"), "PROCESSING"
        elif self._state == "error":
            return QColor("#EF4444"), QColor("#F59E0B"), "ALERT"
        else:
            return QColor("#00D2EE"), QColor("#38BDF8"), "READY"

    def paintEvent(self, event):
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx = w / 2.0
        # If label is shown, keep orb centered in top square area
        cy = (w / 2.0) if self._show_label else (h / 2.0)
        r = min(w, (w if self._show_label else h)) * 0.38

        primary_c, secondary_c, label_text = self._get_state_palette()

        breath = 0.5 + 0.5 * math.sin(self._phase)
        energy = self._voice_level if self._state in ("listening", "speaking") else 0.0

        # 1. Ambient Outer Halo (Subtle, non-distracting)
        halo_r = r * (1.35 + (0.15 * energy if self._state == "listening" else 0.05 * breath))
        halo = QRadialGradient(cx, cy, halo_r)
        halo_alpha = 35 if self._state in ("listening", "speaking") else (45 if self._state == "thinking" else 22)
        halo.setColorAt(0.0, QColor(primary_c.red(), primary_c.green(), primary_c.blue(), halo_alpha))
        halo.setColorAt(0.5, QColor(primary_c.red(), primary_c.green(), primary_c.blue(), int(halo_alpha * 0.35)))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(halo))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - halo_r, cy - halo_r, halo_r * 2, halo_r * 2))

        # 2. Translucent Glass Spherical Disk
        disc_grad = QRadialGradient(cx - r * 0.25, cy - r * 0.25, r * 1.2)
        disc_grad.setColorAt(0.0, QColor(24, 24, 32, 235))
        disc_grad.setColorAt(0.75, QColor(13, 13, 18, 245))
        disc_grad.setColorAt(1.0, QColor(7, 7, 10, 255))
        p.setBrush(QBrush(disc_grad))
        rim_color = QColor(255, 255, 255, 18)
        if self._state == "error":
            rim_color = QColor(239, 68, 68, 120)
        elif self._state in ("listening", "speaking"):
            rim_color = QColor(primary_c.red(), primary_c.green(), primary_c.blue(), 90)
        p.setPen(QPen(rim_color, 1.0))
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # 3. State-Specific Animated Elements
        if self._state == "idle":
            # Soft static glow + subtle concentric micro-orbit
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(primary_c.red(), primary_c.green(), primary_c.blue(), 60), 1.0))
            inner_ring_r = r * 0.72
            p.drawEllipse(QRectF(cx - inner_ring_r, cy - inner_ring_r, inner_ring_r * 2, inner_ring_r * 2))

            # Small accent arcs
            p.setPen(QPen(primary_c, 1.4))
            p.drawArc(QRectF(cx - r * 0.88, cy - r * 0.88, r * 1.76, r * 1.76), int(self._rotation * 8), 45 * 16)
            p.drawArc(QRectF(cx - r * 0.88, cy - r * 0.88, r * 1.76, r * 1.76), int((self._rotation * 8) + 180 * 16), 45 * 16)

        elif self._state == "listening":
            # Gentle pulsing animation reacting to voice
            pulse_mult = 1.0 + energy * 0.25 + 0.05 * math.sin(self._phase * 3)
            ring_r = r * 0.65 * pulse_mult
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(primary_c, 1.6))
            p.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

            outer_pulse_r = r * 0.88 * (1.0 + energy * 0.18)
            p.setPen(QPen(QColor(secondary_c.red(), secondary_c.green(), secondary_c.blue(), 100), 1.0))
            p.drawEllipse(QRectF(cx - outer_pulse_r, cy - outer_pulse_r, outer_pulse_r * 2, outer_pulse_r * 2))

        elif self._state == "thinking":
            # Slow rotating interacting particles & counter-orbiting arcs
            p.setBrush(Qt.BrushStyle.NoBrush)
            arc_r = r * 0.78
            p.setPen(QPen(primary_c, 1.4))
            p.drawArc(QRectF(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2), int(self._rotation * 16), 110 * 16)
            p.setPen(QPen(secondary_c, 1.2))
            p.drawArc(QRectF(cx - (arc_r * 0.85), cy - (arc_r * 0.85), arc_r * 1.7, arc_r * 1.7), int(-self._rotation * 22), 80 * 16)

            # Particles
            p.setPen(Qt.PenStyle.NoPen)
            for part in self._particles:
                px = cx + math.cos(part["angle"]) * (r * part["dist"])
                py = cy + math.sin(part["angle"]) * (r * part["dist"])
                p.setBrush(QBrush(QColor(primary_c.red(), primary_c.green(), primary_c.blue(), 210)))
                p.drawEllipse(QPointF(px, py), part["size"], part["size"])

        elif self._state == "speaking":
            # Subtle waveform / ripple animation
            p.setBrush(Qt.BrushStyle.NoBrush)
            for i in range(3):
                wave_r = r * (0.42 + i * 0.22 + 0.1 * math.sin(self._phase * 4 + i))
                alpha = int(max(20, 180 - (i * 65) + energy * 60))
                p.setPen(QPen(QColor(primary_c.red(), primary_c.green(), primary_c.blue(), min(255, alpha)), 1.2))
                p.drawEllipse(QRectF(cx - wave_r, cy - wave_r, wave_r * 2, wave_r * 2))

        elif self._state == "processing":
            # Small activity tracker orbit
            p.setBrush(Qt.BrushStyle.NoBrush)
            track_r = r * 0.75
            p.setPen(QPen(QColor(255, 255, 255, 25), 1.0))
            p.drawEllipse(QRectF(cx - track_r, cy - track_r, track_r * 2, track_r * 2))

            # Active tracer dot & tail
            p.setPen(QPen(primary_c, 2.0))
            p.drawArc(QRectF(cx - track_r, cy - track_r, track_r * 2, track_r * 2), int(self._rotation * 24), 70 * 16)

            tracer_rad = self._rotation * 24 * (math.pi / (180.0 * 16.0))
            tx = cx + math.cos(tracer_rad) * track_r
            ty = cy - math.sin(tracer_rad) * track_r
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(primary_c))
            p.drawEllipse(QPointF(tx, ty), 3.2, 3.2)

        elif self._state == "error":
            # Restrained warning state
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(239, 68, 68, 200), 1.6))
            err_r = r * 0.78
            p.drawEllipse(QRectF(cx - err_r, cy - err_r, err_r * 2, err_r * 2))

        # 4. Central Luminous Core
        core_r = r * (0.24 + (0.04 * breath) + (0.1 * energy))
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        core_grad.setColorAt(0.4, QColor(primary_c.red(), primary_c.green(), primary_c.blue(), 200))
        core_grad.setColorAt(0.85, QColor(primary_c.red(), primary_c.green(), primary_c.blue(), 60))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(core_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))

        # 5. Optional Minimal Status Subtitle
        if self._show_label and h > w:
            font = QFont("Segoe UI", 7, QFont.Weight.Bold)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.8)
            p.setFont(font)
            p.setPen(QColor(TEXT_DIM))
            tw = p.fontMetrics().horizontalAdvance(label_text)
            text_y = cy + r + 20
            p.drawText(QPointF(cx - tw / 2.0, text_y), label_text)

        p.end()


# Alias for backward compatibility
CommandCore = OmenOrb
