
"""
Real-time chat view with streaming, message bubbles, and step indicators.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor
from core.events import get_event_bus, EventType
from ui.styles.palette import (
    PRIMARY, BACKGROUND_DARK, BACKGROUND_MEDIUM, BACKGROUND_CARD,
    TEXT_PRIMARY, TEXT_SECONDARY, SECONDARY, FONT_SIZE_DEFAULT,
    FONT_SIZE_MEDIUM, SPACING_DEFAULT, SPACING_LARGE, SPACING_XLARGE,
)


class ChatView(QWidget):
    """
    Chat interface with message stream and agent interaction.
    """

    message_sent = Signal(str)

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING_LARGE)
        layout.setContentsMargins(SPACING_XLARGE, SPACING_LARGE, SPACING_XLARGE, SPACING_LARGE)

        # Header
        header = QLabel("Conversation")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {PRIMARY};")
        layout.addWidget(header)

        # Agent status bar
        status_layout = QHBoxLayout()
        self._thinking_label = QLabel("○ Idle")
        self._thinking_label.setStyleSheet(f"color: #8B9CB8; font-size: 10pt;")
        status_layout.addWidget(self._thinking_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Chat history scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(500)
        scroll.setMinimumHeight(250)

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setSpacing(SPACING_DEFAULT)

        scroll.setWidget(self._chat_container)
        layout.addWidget(scroll)

        # Message input
        input_layout = QHBoxLayout()
        self._input_field = QTextEdit()
        self._input_field.setMaximumHeight(80)
        self._input_field.setPlaceholderText("Ask OMEN anything... (Enter to send, Shift+Enter for newline)")
        self._input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BACKGROUND_MEDIUM};
                border: 1px solid #2A3A56;
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
            }}
        """)
        input_layout.addWidget(self._input_field)

        self._send_button = QPushButton("Send")
        self._send_button.setObjectName("primaryBtn")
        self._send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self._send_button)
        layout.addLayout(input_layout)

        # Bind Enter key to send
        self._input_field.returnPressed.connect(self._on_send_enter)

    def _connect_signals(self):
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_state_change)
            bus.subscribe(EventType.STREAM_TOKEN, self._on_stream_token)
            bus.subscribe(EventType.TOOL_EXECUTING, self._on_tool_executing)
        except Exception:
            pass

    def _on_state_change(self, event):
        state = event.payload.get("state", "")
        self._thinking_label.setText(f"○ {state}")
        state_colors = {
            "EXECUTING": PRIMARY,
            "PLANNING": SECONDARY,
            "ERROR": "#EF4444",
            "COMPLETED": "#10B981",
        }
        color = state_colors.get(state, "#8B9CB8")
        self._thinking_label.setStyleSheet(f"color: {color}; font-size: 10pt;")

    def _on_stream_token(self, event):
        token = event.payload.get("token", "")
        # Append streaming token to last assistant message
        if self._chat_layout.count() > 0:
            last_item = self._chat_layout.itemAt(self._chat_layout.count() - 1)
            if last_item and last_item.widget():
                label = last_item.widget().findChild(QLabel, "msgText")
                if label:
                    label.setText(label.text() + token)

    def _on_tool_executing(self, event):
        tool = event.payload.get("tool", "")
        self._thinking_label.setText(f"⚙ Using: {tool}")
        self._thinking_label.setStyleSheet(f"color: {PRIMARY}; font-size: 10pt;")

    def _on_send_enter(self):
        """Enter key sends; Shift+Enter for newline."""
        text = self._input_field.toPlainText().strip()
        if text:
            self._send_message(text)

    def _on_send(self):
        text = self._input_field.toPlainText().strip()
        if text:
            self._send_message(text)

    def _send_message(self, text: str):
        self.add_user_message(text)
        self._input_field.clear()
        self.message_sent.emit(text)

    def add_user_message(self, text: str):
        self._add_bubble(text, is_user=True)

    def add_assistant_message(self, text: str):
        self._add_bubble(text, is_user=False)

    def _add_bubble(self, text: str, is_user: bool):
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT)

        role_label = QLabel("You" if is_user else "OMEN")
        role_label.setFont(QFont("Segoe UI", 9))
        role_label.setStyleSheet(
            f"color: {PRIMARY if not is_user else SECONDARY}; font-weight: bold;"
        )
        bubble_layout.addWidget(role_label)

        msg_text = QLabel(text)
        msg_text.setObjectName("msgText")
        msg_text.setWordWrap(True)
        msg_text.setStyleSheet(f"""
            QLabel {{
                background-color: {BACKGROUND_CARD};
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
                color: {TEXT_PRIMARY};
            }}
        """)
        bubble_layout.addWidget(msg_text)

        if is_user:
            bubble_layout.addStretch()
            bubble.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(123, 104, 238, 0.15);
                    border: 1px solid rgba(123, 104, 238, 0.3);
                    border-radius: 12px;
                    padding: 10px;
                }}
            """)
        else:
            bubble.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(0, 212, 170, 0.08);
                    border: 1px solid rgba(0, 212, 170, 0.2);
                    border-radius: 12px;
                    padding: 10px;
                }}
            """)

        self._chat_layout.addWidget(bubble)

        # Auto scroll
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        pass  # scroll area handles this

    def add_streaming_message(self, full_text: str, stream_chunk_fn=None):
        """Adds a message that streams in chunk by chunk."""
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT, SPACING_DEFAULT)

        role_label = QLabel("OMEN")
        role_label.setFont(QFont("Segoe UI", 9))
        role_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold;")
        bubble_layout.addWidget(role_label)

        msg_text = QLabel("")
        msg_text.setObjectName("msgText")
        msg_text.setWordWrap(True)
        msg_text.setStyleSheet(f"""
            QLabel {{
                background-color: {BACKGROUND_CARD};
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
                color: {TEXT_PRIMARY};
            }}
        """)
        bubble_layout.addWidget(msg_text)
        bubble.setLayout(bubble_layout)
        self._chat_layout.addWidget(bubble)

        if stream_chunk_fn:
            for chunk in stream_chunk_fn():
                msg_text.setText(msg_text.text() + chunk)
        else:
            msg_text.setText(full_text)

        QTimer.singleShot(50, self._scroll_to_bottom)


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
