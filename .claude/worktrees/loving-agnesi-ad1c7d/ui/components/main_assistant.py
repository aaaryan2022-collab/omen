"""Main Assistant — hero + command bar + quick actions + conversation."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QTextEdit, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QCursor

from ui.design.tokens import (
    BG, SURFACE, ELEVATED, CARD, BORDER, BORDER_HOVER,
    ACCENT, ACCENT_SOFT, TEXT, TEXT_DIM, TEXT_MUTED,
    FONT, FONT_MONO, R, R_SM, SHADOW, SHADOW_FLOAT
)
from ui.components.orb import Orb


class CommandBar(QWidget):
    """Bottom command input with mic, attach, send, voice mode."""
    send_clicked = Signal(str)
    voice_clicked = Signal()
    attach_file = Signal()
    attach_image = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(88)
        self.setStyleSheet(f"""
            background: {SURFACE};
            border-top: 1px solid {BORDER};
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        # Voice mode button
        self.btn_voice = QPushButton("🎤 Voice")
        self.btn_voice.setFixedHeight(48)
        self.btn_voice.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_SOFT};
                color: {ACCENT};
                border: 1px solid {ACCENT};
                border-radius: {R}px;
                padding: 0 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: rgba(59,130,246,0.18); }}
        """)
        self.btn_voice.clicked.connect(self.voice_clicked.emit)
        lay.addWidget(self.btn_voice)

        # Input field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask OMEN anything...  (Ctrl+Space)")
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {ELEVATED};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: {R}px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: {FONT};
            }}
            QLineEdit:focus {{
                border-color: {ACCENT};
            }}
        """)
        self.input.returnPressed.connect(self._on_send)
        lay.addWidget(self.input, 1)

        # Attach file
        self.btn_file = QPushButton("📎")
        self.btn_file.setFixedSize(40, 40)
        self.btn_file.setStyleSheet(f"""
            QPushButton {{ background: {ELEVATED}; border: 1px solid {BORDER}; border-radius: {R}px; font-size: 16px; }}
            QPushButton:hover {{ background: {SURFACE}; border-color: {BORDER_HOVER}; }}
        """)
        self.btn_file.clicked.connect(self.attach_file.emit)
        lay.addWidget(self.btn_file)

        # Attach image
        self.btn_image = QPushButton("🖼")
        self.btn_image.setFixedSize(40, 40)
        self.btn_image.setStyleSheet(f"""
            QPushButton {{ background: {ELEVATED}; border: 1px solid {BORDER}; border-radius: {R}px; font-size: 16px; }}
            QPushButton:hover {{ background: {SURFACE}; border-color: {BORDER_HOVER}; }}
        """)
        self.btn_image.clicked.connect(self.attach_image.emit)
        lay.addWidget(self.btn_image)

        # Send
        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(40, 40)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #09090B;
                border: none;
                border-radius: {R}px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #60A5FA; }}
        """)
        self.btn_send.clicked.connect(self._on_send)
        lay.addWidget(self.btn_send)

    def _on_send(self):
        text = self.input.text().strip()
        if text:
            self.send_clicked.emit(text)
            self.input.clear()

    def focus_input(self):
        self.input.setFocus()


class QuickActions(QWidget):
    """Interactive suggestion cards below command bar."""
    action_clicked = Signal(str)

    SUGGESTIONS = [
        ("Summarize my files", "📄"),
        ("Open my workspace", "💻"),
        ("Plan my day", "📅"),
        ("Write some code", "⌨️"),
        ("Check my tasks", "✅"),
        ("Explain something", "💡"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 8)
        lay.setSpacing(8)

        hint = QLabel("Quick actions")
        hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")
        lay.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(10)
        for text, icon in self.SUGGESTIONS:
            btn = QPushButton(f"{icon}  {text}")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {CARD};
                    color: {TEXT};
                    border: 1px solid {BORDER};
                    border-radius: {R}px;
                    padding: 10px 16px;
                    font-size: 13px;
                    font-family: {FONT};
                }}
                QPushButton:hover {{
                    background: {ELEVATED};
                    border-color: {ACCENT};
                }}
            """)
            btn.clicked.connect(lambda _, t=text: self.action_clicked.emit(t))
            row.addWidget(btn)
        lay.addLayout(row)


class MessageBubble(QWidget):
    """Single message — user or OMEN."""
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        # Role label
        role_label = QLabel("You" if role == "user" else "OMEN")
        role_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600;")
        lay.addWidget(role_label)

        # Content
        self.content_label = QLabel(content)
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bg = CARD if role == "user" else SURFACE
        border_color = BORDER
        align = "right" if role == "user" else "left"
        self.content_label.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {TEXT};
                border: 1px solid {border_color};
                border-radius: {R}px;
                padding: 12px 16px;
                font-size: 14px;
                line-height: 1.6;
                font-family: {FONT};
            }}
        """)
        lay.addWidget(self.content_label)


class ConversationView(QWidget):
    """Scrollable conversation area with smooth transitions."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")

        self.container = QWidget()
        self.container_lay = QVBoxLayout(self.container)
        self.container_lay.setContentsMargins(24, 16, 24, 16)
        self.container_lay.setSpacing(16)
        self.container_lay.addStretch()

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.container)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: {BG}; border: none; }}
            QScrollBar:vertical {{
                background: transparent; width: 8px; margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {BORDER_HOVER}; }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.scroll)

    def add_message(self, role: str, content: str):
        # Remove stretch, add message, re-add stretch
        self.container_lay.takeAt(self.container_lay.count() - 1)
        bubble = MessageBubble(role, content)
        self.container_lay.addWidget(bubble)
        self.container_lay.addStretch()
        # Auto-scroll
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def show_thinking(self):
        self.add_message("assistant", "OMEN is thinking...")

    def clear(self):
        while self.container_lay.count() > 1:
            w = self.container_lay.takeAt(0).widget()
            if w:
                w.deleteLater()


class MainAssistant(QWidget):
    """Center panel: hero → conversation."""
    send = Signal(str)
    voice = Signal()
    quick_action = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self.in_conversation = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 0)
        lay.setSpacing(0)

        # Hero (idle state)
        self.hero = QWidget()
        hero_lay = QVBoxLayout(self.hero)
        hero_lay.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        hero_lay.setSpacing(20)

        self.orb = Orb(size=72)
        hero_lay.addWidget(self.orb, 0, Qt.AlignHCenter)

        self.greeting = QLabel("Good afternoon, Aryan.")
        self.greeting.setStyleSheet(f"color: {TEXT}; font-family: {FONT}; font-size: 28px; font-weight: 500;")
        hero_lay.addWidget(self.greeting, 0, Qt.AlignHCenter)

        self.subtitle = QLabel("What would you like me to take care of?")
        self.subtitle.setStyleSheet(f"color: {TEXT_DIM}; font-family: {FONT}; font-size: 15px;")
        hero_lay.addWidget(self.subtitle, 0, Qt.AlignHCenter)

        lay.addWidget(self.hero, 1)

        # Quick actions (shown in idle)
        self.quick_actions = QuickActions()
        self.quick_actions.action_clicked.connect(self.quick_action.emit)
        lay.addWidget(self.quick_actions)

        # Conversation (hidden initially)
        self.conversation = ConversationView()
        self.conversation.hide()
        lay.addWidget(self.conversation, 1)

        # Command bar
        self.command_bar = CommandBar()
        self.command_bar.send_clicked.connect(self._on_send)
        self.command_bar.voice_clicked.connect(self.voice.emit)
        lay.addWidget(self.command_bar)

    def _on_send(self, text: str):
        self._enter_conversation()
        self.conversation.add_message("user", text)
        self.conversation.show_thinking()
        self.send.emit(text)

    def _enter_conversation(self):
        if self.in_conversation:
            return
        self.in_conversation = True
        # Smooth fade hero out, conversation in
        self.hero.hide()
        self.quick_actions.hide()
        self.conversation.show()

    def add_omen_response(self, text: str):
        # Replace "thinking" with actual response
        self.conversation.container_lay.takeAt(self.conversation.container_lay.count() - 2).widget().deleteLater()
        self.conversation.add_message("assistant", text)
        self.orb.set_state("idle")

    def set_state(self, state: str):
        self.orb.set_state(state)

    def clear_conversation(self):
        self.in_conversation = False
        self.conversation.clear()
        self.conversation.hide()
        self.hero.show()
        self.quick_actions.show()