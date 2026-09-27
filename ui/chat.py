# ============================================
"""
Real-time Chat Matrix View for OMEN.
Holographic message stream, tool execution indicators, and voice input integration.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QFrame, QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent
from PySide6.QtGui import QFont
from core.events import get_event_bus, EventType
from ui.styles.palette import (
    PRIMARY, SECONDARY, BACKGROUND_CARD, BACKGROUND_MEDIUM,
    TEXT_PRIMARY, TEXT_SECONDARY, SUCCESS, ERROR,
)


class ChatView(QWidget):
    """Futuristic Chat Matrix Interface."""

    message_sent = Signal(str)
    voice_requested = Signal()
    voice_cancelled = Signal()

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setObjectName("chatView")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(32, 24, 32, 24)

        # Header Section
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("NEURAL CHAT MATRIX")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        self._status_label = QLabel("○ AGENT READY · STANDBY")
        self._status_label.setStyleSheet("color: #00FF9D; font-size: 8.5pt; font-weight: bold; font-family: Consolas;")
        title_box.addWidget(self._status_label)
        header.addLayout(title_box)
        header.addStretch()

        clear_btn = QPushButton("CLEAR BUFFER")
        clear_btn.clicked.connect(self._clear_conversation)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        # Chat Stream Scroll Area
        scroll = QScrollArea()
        scroll.setObjectName("chatScroll")
        self._scroll = scroll
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
            }}
        """)

        self._chat_container = QWidget()
        self._chat_container.setStyleSheet("background-color: transparent;")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setSpacing(12)
        self._chat_layout.setContentsMargins(16, 16, 16, 16)
        self._chat_layout.addStretch()

        scroll.setWidget(self._chat_container)
        layout.addWidget(scroll, stretch=1)

        # Message Input Deck
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #0D131F;
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 4px;
            }
            QFrame:focus-within {
                border: 1px solid #00F0FF;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 4, 8, 4)
        input_layout.setSpacing(8)

        self._voice_button = QPushButton("🎙")
        self._voice_button.setObjectName("roundButton")
        self._voice_button.setToolTip("Speak to OMEN")
        self._voice_button.clicked.connect(self.voice_requested.emit)
        input_layout.addWidget(self._voice_button)

        self._input_field = QTextEdit()
        self._input_field.setMaximumHeight(65)
        self._input_field.setPlaceholderText("Transmit command or ask OMEN... (Enter to send, Shift+Enter for newline)")
        self._input_field.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                padding: 8px;
                font-size: 11pt;
                color: #F1F5F9;
            }
        """)
        input_layout.addWidget(self._input_field, stretch=1)

        self._send_button = QPushButton("SEND  →")
        self._send_button.setObjectName("primaryBtn")
        self._send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self._send_button)

        layout.addWidget(input_frame)

        # Enter key filter
        self._input_field.installEventFilter(self)

        # Voice Listening Overlay
        self._build_voice_overlay(layout)

    def _build_voice_overlay(self, parent_layout):
        self._voice_overlay = QFrame()
        self._voice_overlay.setObjectName("voiceOverlay")
        self._voice_overlay.setFixedHeight(64)
        overlay_layout = QHBoxLayout(self._voice_overlay)
        overlay_layout.setContentsMargins(18, 6, 14, 6)
        overlay_layout.setSpacing(10)

        self._voice_state = QLabel("LISTENING...")
        self._voice_state.setObjectName("voiceState")
        overlay_layout.addWidget(self._voice_state)

        bars = QWidget()
        bars_layout = QHBoxLayout(bars)
        bars_layout.setContentsMargins(8, 0, 8, 0)
        bars_layout.setSpacing(3)
        self._voice_bars = []
        for _ in range(28):
            bar = QFrame()
            bar.setObjectName("voiceBar")
            bar.setFixedWidth(3)
            bar.setFixedHeight(6)
            bars_layout.addWidget(bar, alignment=Qt.AlignmentFlag.AlignVCenter)
            self._voice_bars.append(bar)
        overlay_layout.addWidget(bars, stretch=1)

        cancel = QPushButton("CANCEL")
        cancel.setObjectName("dangerBtn")
        cancel.clicked.connect(self.voice_cancelled.emit)
        overlay_layout.addWidget(cancel)

        self._voice_timer = QTimer(self)
        self._voice_timer.timeout.connect(self._animate_voice_bars)
        self._voice_phase = 0
        self._voice_overlay.hide()
        parent_layout.addWidget(self._voice_overlay)

    def show_voice_overlay(self):
        self._voice_overlay.show()
        self._voice_state.setText("LISTENING...")
        self._voice_timer.start(80)

    def hide_voice_overlay(self):
        self._voice_timer.stop()
        self._voice_overlay.hide()

    def set_voice_state(self, state: str):
        self._voice_state.setText(state.upper())

    def _animate_voice_bars(self):
        self._voice_phase += 1
        for index, bar in enumerate(self._voice_bars):
            height = 6 + ((index * 6 + self._voice_phase * 5) % 28)
            bar.setFixedHeight(height)

    def _clear_conversation(self):
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _connect_signals(self):
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_state_change)
            bus.subscribe(EventType.TOOL_EXECUTING, self._on_tool_executing)
        except Exception:
            pass

    def _on_state_change(self, event):
        state = event.payload.get("state", "")
        self._status_label.setText(f"○ OMEN · {state}")

    def _on_tool_executing(self, event):
        tool = event.payload.get("tool", "")
        self._status_label.setText(f"⚙ EXECUTING · {tool}")

    def eventFilter(self, watched, event):
        if watched is self._input_field and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._on_send()
                return True
        return super().eventFilter(watched, event)

    def _on_send(self):
        text = self._input_field.toPlainText().strip()
        if text:
            self.add_user_message(text)
            self._input_field.clear()
            self.message_sent.emit(text)

    def add_user_message(self, text: str):
        self._add_bubble(text, is_user=True)

    def add_assistant_message(self, text: str, plan_steps=None):
        self._add_bubble(text, is_user=False, plan_steps=plan_steps)

    def _add_bubble(self, text: str, is_user: bool, plan_steps=None):
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 10, 12, 10)
        bubble_layout.setSpacing(6)

        # Header tag
        sender = "YOU" if is_user else "OMEN"
        sender_color = "#00F0FF" if not is_user else "#A355FF"
        header_lbl = QLabel(sender)
        header_lbl.setStyleSheet(f"color: {sender_color}; font-size: 8.5pt; font-weight: 800; font-family: Consolas; letter-spacing: 1px;")
        bubble_layout.addWidget(header_lbl)

        # Message body
        body_lbl = QLabel(text)
        body_lbl.setWordWrap(True)
        body_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11pt; line-height: 1.4;")
        bubble_layout.addWidget(body_lbl)

        # Plan step execution tags if present
        if plan_steps:
            for step in plan_steps:
                step_badge = QLabel(f"⚙ Tool: {step.tool} [{step.status.value}]")
                step_badge.setStyleSheet("color: #00FF9D; font-size: 8pt; font-family: Consolas; background: rgba(0,255,157,0.1); padding: 2px 6px; border-radius: 4px;")
                bubble_layout.addWidget(step_badge)

        if is_user:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: rgba(112, 0, 255, 0.12);
                    border: 1px solid rgba(112, 0, 255, 0.35);
                    border-radius: 10px;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 240, 255, 0.08);
                    border: 1px solid rgba(0, 240, 255, 0.25);
                    border-radius: 10px;
                }
            """)

        # Insert before bottom stretch
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self._scroll.verticalScrollBar().setValue(self._scroll.verticalScrollBar().maximum())
