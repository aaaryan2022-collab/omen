# ============================================
"""
OMEN Toast Notification System.
Small non-intrusive glass toasts for quick action confirmations.
Auto-dismissing, smooth fade animation, positioned in bottom-right corner.
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect, QPushButton
from ui.styles.palette import (
    PRIMARY, SUCCESS, WARNING, ERROR, INFO, TEXT_PRIMARY, TEXT_SECONDARY,
    GLASS_CARD, BORDER,
)


class ToastNotification(QWidget):
    """Floating translucent toast notification."""

    def __init__(self, message: str, level: str = "success", parent=None, duration_ms: int = 3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._duration_ms = duration_ms

        icon_char = "✓"
        accent_color = SUCCESS
        if level == "info":
            icon_char = "ℹ"
            accent_color = INFO
        elif level == "warning":
            icon_char = "⚠"
            accent_color = WARNING
        elif level == "error":
            icon_char = "✕"
            accent_color = ERROR
        elif level == "omen":
            icon_char = "◉"
            accent_color = PRIMARY

        self.setStyleSheet(f"""
            QWidget#toastRoot {{
                background-color: rgba(18, 18, 24, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-left: 3px solid {accent_color};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("toastRoot")
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(14, 10, 14, 10)
        c_layout.setSpacing(10)

        # Icon
        icon_lbl = QLabel(icon_char)
        icon_lbl.setStyleSheet(f"color: {accent_color}; font-size: 13px; font-weight: bold;")
        c_layout.addWidget(icon_lbl)

        # Message
        text_lbl = QLabel(message)
        text_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; font-weight: 500;")
        c_layout.addWidget(text_lbl)

        # Dismiss
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #71717A;
                border: none;
                font-size: 14px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #EDEDEF;
            }
        """)
        close_btn.clicked.connect(self.close)
        c_layout.addWidget(close_btn)

        layout.addWidget(container)
        self.adjustSize()

        # Opacity animation
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity")
        self._anim.setDuration(220)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-dismiss timer
        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self._fade_out)

    def show_toast(self):
        self.show()
        self._anim.start()
        self._dismiss_timer.start(self._duration_ms)

    def _fade_out(self):
        self._anim.stop()
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.close)
        self._anim.start()


class ToastManager:
    """Manages active toasts inside a parent window."""

    _active_toasts = []

    @classmethod
    def show(cls, parent: QWidget, message: str, level: str = "success", duration_ms: int = 3200):
        if not parent:
            return
        toast = ToastNotification(message, level=level, parent=parent, duration_ms=duration_ms)

        # Position at bottom-right of parent
        pw = parent.width()
        ph = parent.height()
        tw = toast.sizeHint().width()
        th = toast.sizeHint().height()

        margin_right = 24
        margin_bottom = 28
        toast.move(pw - tw - margin_right, ph - th - margin_bottom)
        toast.show_toast()
        cls._active_toasts.append(toast)
