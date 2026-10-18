# ============================================
"""
OMEN Central 3D Particle Sphere — Core Identity Element.
Hardware-accelerated mathematical 3D particle system featuring:
- Fibonacci spherical lattice (480 dynamic 3D vertices)
- Real-time perspective projection with depth-sorting & volumetric bloom
- Voice-reactive displacement (amplitude + harmonic frequency deformation)
- Mouse interaction (drag to rotate with inertia, proximity gravity, click ripple)
- Orbital energy filaments & trailing photon sparks
- Distinct operational states: idle, listening, thinking, speaking, tool, success, error
"""

import math
import random
from typing import List, Dict, Any, Tuple
from PySide6.QtCore import QTimer, Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QColor, QRadialGradient, QBrush, QFont, QCursor, QLinearGradient
)
from PySide6.QtWidgets import QWidget
from ui.styles.palette import (
    PRIMARY, PRIMARY_LIGHT, SECONDARY, SUCCESS, WARNING, ERROR,
    TEXT_PRIMARY, TEXT_DIM, BACKGROUND_DARK,
)


class Particle3D:
    """A single particle in 3D spherical coordinates."""
    __slots__ = ("base_x", "base_y", "base_z", "phase", "speed", "size_factor", "seed", "color_offset")

    def __init__(self, x: float, y: float, z: float, i: int):
        self.base_x = x
        self.base_y = y
        self.base_z = z
        self.phase = random.uniform(0.0, math.pi * 2)
        self.speed = random.uniform(0.8, 1.6)
        self.size_factor = random.uniform(0.7, 1.4)
        self.seed = random.uniform(0.0, 100.0)
        self.color_offset = (i % 7) / 7.0


class OmenOrb(QWidget):
    """
    Central 3D Particle Sphere identity widget for OMEN.
    Full interactive 3D particle engine with audio and mouse reactivity.
    """

    clicked = Signal()
    stateChanged = Signal(str)

    # State Color Palettes: (Primary Glow, Core Spark, Secondary Filament, State Title)
    STATE_PALETTES = {
        "idle": (QColor("#8B5CF6"), QColor("#00D2EE"), QColor("#6366F1"), "READY"),
        "listening": (QColor("#00F5FF"), QColor("#FFFFFF"), QColor("#38BDF8"), "LISTENING"),
        "thinking": (QColor("#A855F7"), QColor("#F59E0B"), QColor("#EC4899"), "THINKING"),
        "speaking": (QColor("#00E5FF"), QColor("#10B981"), QColor("#38BDF8"), "SPEAKING"),
        "processing": (QColor("#F59E0B"), QColor("#FBBF24"), QColor("#00D2EE"), "EXECUTING"),
        "tool": (QColor("#F59E0B"), QColor("#FBBF24"), QColor("#00D2EE"), "EXECUTING"),
        "success": (QColor("#10B981"), QColor("#34D399"), QColor("#6EE7B7"), "COMPLETED"),
        "error": (QColor("#EF4444"), QColor("#F87171"), QColor("#DC2626"), "ALERT"),
    }

    def __init__(self, parent=None, size: int = 240, show_label: bool = True):
        super().__init__(parent)
        self._size = size
        self._show_label = show_label
        self.setMinimumSize(size, size + (32 if show_label else 0))
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self._state = "idle"
        self._time = 0.0
        self._voice_level = 0.0
        self._target_voice_level = 0.0

        # 3D Euler angles & momentum
        self._rot_x = 0.25
        self._rot_y = 0.0
        self._vel_x = 0.0
        self._vel_y = 0.006  # gentle idle auto-spin
        self._mouse_down = False
        self._last_mouse_pos = QPointF(0, 0)
        self._hover_pos = QPointF(-1000, -1000)
        self._click_ripple = 0.0

        # Generate Fibonacci 3D Particle Lattice
        self._num_particles = 440
        self._particles: List[Particle3D] = []
        golden_angle = math.pi * (3.0 - math.sqrt(5.0))
        for i in range(self._num_particles):
            y = 1.0 - (i / float(self._num_particles - 1)) * 2.0
            radius_at_y = math.sqrt(max(0.0, 1.0 - y * y))
            theta = golden_angle * i
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            self._particles.append(Particle3D(x, y, z, i))

        # Orbiting filaments sparks (trailing photon points)
        self._ring_sparks = [
            {"angle": random.uniform(0, math.pi * 2), "speed": random.uniform(0.02, 0.04), "tilt": 0.45}
            for _ in range(12)
        ]

        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._time += 0.025

        # Smooth voice envelope decay
        self._voice_level += (self._target_voice_level - self._voice_level) * 0.25
        self._target_voice_level *= 0.88

        # Decay click ripple
        if self._click_ripple > 0:
            self._click_ripple = max(0.0, self._click_ripple - 0.035)

        # Apply rotation momentum
        if not self._mouse_down:
            base_speed = 0.024 if self._state in ("thinking", "processing", "tool") else 0.007
            self._rot_y += self._vel_y
            self._rot_x += self._vel_x
            self._vel_y += (base_speed - self._vel_y) * 0.05
            self._vel_x *= 0.92
        else:
            self._rot_y += self._vel_y
            self._rot_x += self._vel_x

        # Update orbiting ring sparks
        for spark in self._ring_sparks:
            spark["angle"] = (spark["angle"] + spark["speed"]) % (math.pi * 2)

        self.update()

    def set_state(self, state: str):
        state = state.lower().strip()
        if state in self.STATE_PALETTES:
            self._state = state
        elif state in ("ready", "standby"):
            self._state = "idle"
        elif state in ("action", "busy"):
            self._state = "processing"
        self.stateChanged.emit(self._state)
        self.update()

    def set_voice_mode(self, mode: str):
        """Compatibility wrapper."""
        self.set_state(mode)

    def set_voice_level(self, level: float):
        lvl = max(0.0, min(1.0, level))
        self._voice_level = lvl
        self._target_voice_level = lvl
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_down = True
            self._last_mouse_pos = event.position()
            self._click_ripple = 1.0
            self.clicked.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._hover_pos = event.position()
        if self._mouse_down:
            delta = event.position() - self._last_mouse_pos
            self._last_mouse_pos = event.position()
            self._vel_y = delta.x() * 0.008
            self._vel_x = -delta.y() * 0.008
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_down = False
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self._hover_pos = QPointF(-1000, -1000)
        self._mouse_down = False
        super().leaveEvent(event)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        sphere_h = h - (32 if self._show_label else 0)
        cx, cy = w / 2.0, sphere_h / 2.0
        base_radius = min(w, sphere_h) * 0.36

        primary_col, spark_col, secondary_col, title_text = self.STATE_PALETTES.get(
            self._state, self.STATE_PALETTES["idle"]
        )

        # 1. Volumetric Deep Core Glow
        breathe = math.sin(self._time * 2.0) * 0.08 + 1.0
        active_boost = 1.0 + (self._voice_level * 0.7) + (self._click_ripple * 0.5)
        glow_rad = base_radius * 1.35 * breathe * active_boost

        core_glow = QRadialGradient(cx, cy, glow_rad)
        glow_alpha = 48 if self._state in ("listening", "speaking", "thinking") else 32
        glow_col = QColor(primary_col.red(), primary_col.green(), primary_col.blue(), glow_alpha)
        core_glow.setColorAt(0.0, glow_col)
        core_glow.setColorAt(0.45, QColor(primary_col.red(), primary_col.green(), primary_col.blue(), glow_alpha // 3))
        core_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(core_glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - glow_rad, cy - glow_rad, glow_rad * 2, glow_rad * 2))

        # 2. Orbital Energy Filaments (Equatorial Rings)
        self._draw_orbital_rings(painter, cx, cy, base_radius, primary_col, secondary_col)

        # 3. 3D Particle Matrix (Fibonacci Lattice with depth sort)
        cos_y, sin_y = math.cos(self._rot_y), math.sin(self._rot_y)
        cos_x, sin_x = math.cos(self._rot_x), math.sin(self._rot_x)

        fov = 360.0
        projected: List[Tuple[float, float, float, float, float, QColor]] = []

        # Cursor gravity in 2D widget plane
        dx_h = self._hover_pos.x() - cx
        dy_h = self._hover_pos.y() - cy
        hover_dist = math.sqrt(dx_h * dx_h + dy_h * dy_h)

        for p in self._particles:
            # Base harmonic breathing displacement
            t_wave = math.sin(self._time * p.speed + p.phase)
            harmonic_disp = t_wave * 0.06

            # Audio reactive pulse
            audio_disp = 0.0
            if self._state in ("listening", "speaking"):
                audio_disp = math.sin(self._time * 10.0 + p.seed) * self._voice_level * 0.35

            # Ripple wave from click
            ripple_disp = 0.0
            if self._click_ripple > 0:
                dist_from_equator = abs(p.base_y)
                ripple_disp = math.sin(self._click_ripple * 6.0 - dist_from_equator * 4.0) * self._click_ripple * 0.22

            r = base_radius * (1.0 + harmonic_disp + audio_disp + ripple_disp)
            px = p.base_x * r
            py = p.base_y * r
            pz = p.base_z * r

            # Rotate around Y axis
            x1 = px * cos_y + pz * sin_y
            y1 = py
            z1 = -px * sin_y + pz * cos_y

            # Rotate around X axis
            x2 = x1
            y2 = y1 * cos_x - z1 * sin_x
            z2 = y1 * sin_x + z1 * cos_x

            # Perspective projection
            scale = fov / (fov + z2)
            screen_x = cx + x2 * scale
            screen_y = cy + y2 * scale

            # Mouse attraction/deflection
            if hover_dist < base_radius * 1.5:
                mdx = screen_x - self._hover_pos.x()
                mdy = screen_y - self._hover_pos.y()
                mdist = math.sqrt(mdx * mdx + mdy * mdy)
                if mdist < 90.0 and mdist > 1.0:
                    force = (1.0 - mdist / 90.0) * 8.0
                    screen_x += (mdx / mdist) * force
                    screen_y += (mdy / mdist) * force

            # Depth alpha & color interpolate
            depth_factor = (z2 + base_radius) / (2.0 * base_radius)
            depth_factor = max(0.0, min(1.0, depth_factor))

            alpha = int(35 + depth_factor * 215)
            if depth_factor > 0.65:
                # Foreground sparks
                col = QColor(spark_col.red(), spark_col.green(), spark_col.blue(), alpha)
                pt_size = (1.8 + depth_factor * 2.6) * p.size_factor
            else:
                # Mid & background particles
                col = QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha)
                pt_size = (1.0 + depth_factor * 2.0) * p.size_factor

            projected.append((z2, screen_x, screen_y, pt_size, depth_factor, col))

        # Sort particles back-to-front (depth buffer simulation)
        projected.sort(key=lambda item: item[0])

        # Draw Back Particles (z < 0)
        for z, sx, sy, psize, depth, col in projected:
            if z <= 0:
                painter.setBrush(QBrush(col))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRectF(sx - psize / 2.0, sy - psize / 2.0, psize, psize))

        # Draw Inner Luminescent Nucleus
        nucleus_r = base_radius * 0.38 * (1.0 + self._voice_level * 0.25)
        nucleus_grad = QRadialGradient(cx, cy, nucleus_r)
        nucleus_grad.setColorAt(0.0, QColor(spark_col.red(), spark_col.green(), spark_col.blue(), 180))
        nucleus_grad.setColorAt(0.5, QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 90))
        nucleus_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(nucleus_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - nucleus_r, cy - nucleus_r, nucleus_r * 2, nucleus_r * 2))

        # Draw Front Particles (z > 0) with crisp bloom halos
        for z, sx, sy, psize, depth, col in projected:
            if z > 0:
                # Subtle halo around brighter foreground particles
                if depth > 0.75:
                    halo_col = QColor(col.red(), col.green(), col.blue(), int(col.alpha() * 0.35))
                    painter.setBrush(QBrush(halo_col))
                    painter.drawEllipse(QRectF(sx - psize * 1.4, sy - psize * 1.4, psize * 2.8, psize * 2.8))

                painter.setBrush(QBrush(col))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRectF(sx - psize / 2.0, sy - psize / 2.0, psize, psize))

        # 4. Status Indicator Capsule Label (Optional)
        if self._show_label:
            self._draw_state_label(painter, w, h, primary_col, title_text)

        painter.end()

    def _draw_orbital_rings(self, painter: QPainter, cx: float, cy: float, r: float, c1: QColor, c2: QColor):
        """Draws inclined elliptical orbital energy rings with trailing photon nodes."""
        ring_r = r * 1.18
        painter.save()
        painter.translate(cx, cy)

        # Primary Ring 1 (inclined at 25 deg)
        painter.rotate(24)
        pen1 = QPen(QColor(c1.red(), c1.green(), c1.blue(), 42), 1.2)
        pen1.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen1)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-ring_r, -ring_r * 0.32, ring_r * 2, ring_r * 0.64))

        # Secondary Ring 2 (counter-inclined at -38 deg)
        painter.rotate(-62)
        pen2 = QPen(QColor(c2.red(), c2.green(), c2.blue(), 30), 1.0)
        painter.setPen(pen2)
        painter.drawEllipse(QRectF(-ring_r * 1.08, -ring_r * 0.24, ring_r * 2.16, ring_r * 0.48))

        # Orbiting photon sparks
        for spark in self._ring_sparks:
            ang = spark["angle"]
            px = math.cos(ang) * ring_r
            py = math.sin(ang) * ring_r * 0.32
            alpha = int(140 + math.sin(ang) * 90)
            painter.setBrush(QBrush(QColor(255, 255, 255, alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(px - 1.5, py - 1.5, 3.0, 3.0))

        painter.restore()

    def _draw_state_label(self, painter: QPainter, w: int, h: int, color: QColor, title: str):
        """Presents a clean, high-DPI status pill beneath the sphere."""
        label_w = 120
        label_h = 24
        lx = (w - label_w) / 2.0
        ly = h - 28.0

        # Background pill
        pill_rect = QRectF(lx, ly, label_w, label_h)
        pill_bg = QColor(14, 14, 20, 190)
        painter.setBrush(QBrush(pill_bg))
        pill_pen = QPen(QColor(color.red(), color.green(), color.blue(), 60), 1.0)
        painter.setPen(pill_pen)
        painter.drawRoundedRect(pill_rect, 12.0, 12.0)

        # Pulsing dot
        dot_r = 3.5
        dot_x = lx + 16.0
        dot_y = ly + label_h / 2.0
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(dot_x, dot_y), dot_r, dot_r)

        # Status text
        painter.setPen(QColor(TEXT_PRIMARY))
        font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        painter.setFont(font)
        painter.drawText(
            QRectF(lx + 26.0, ly, label_w - 32.0, label_h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            title,
        )
