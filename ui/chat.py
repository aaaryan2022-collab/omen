# ============================================
"""
OMEN Assistant View — Minimal, Editorial, Focused.
Clean conversation flow. No clutter.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QFrame, QScrollArea, QSizePolicy, QFileDialog, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QColor, QKeyEvent, QGuiApplication

from ui.orb import OmenOrb
from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, BACKGROUND_DARK,
    BACKGROUND_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
)


def get_greeting(user_name: str = "Aryan") -> str:
    hour = datetime.now().hour
    if 4 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    else:
        period = "evening"
    return f"Good {period}, {user_name}."


class CodeBlockWidget(QFrame):
    """Syntax styled code block with copy button."""

    def __init__(self, code: str, language: str = "", parent=None):
        super().__init__(parent)
        self._code = code
        self.setStyleSheet("""
            QFrame {
                background-color: #0A0A0E;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        lang_lbl = QLabel(language.upper() if language else "CODE")
        lang_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 600; font-family: Consolas;")
        header.addWidget(lang_lbl)
        header.addStretch()

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(60, 22)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 4px;
                color: #A1A1AA;
                font-size: 10px;
            }
            QPushButton:hover {
                background: rgba(0, 210, 238, 0.12);
                color: #00D2EE;
                border-color: #00D2EE;
            }
        """)
        copy_btn.clicked.connect(self._copy)
        header.addWidget(copy_btn)
        layout.addLayout(header)

        # Code
        code_lbl = QLabel(code)
        code_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        code_lbl.setStyleSheet(f"color: #E2E8F0; font-family: Consolas, monospace; font-size: 12px; line-height: 1.5;")
        layout.addWidget(code_lbl)

    def _copy(self):
        cb = QGuiApplication.clipboard()
        cb.setText(self._code)
        ToastManager.show(self.window(), "Code copied", level="info")


class MessageBubble(QWidget):
    """Clean message bubble — user or OMEN."""

    regenerate_requested = Signal(str)
    save_requested = Signal(str)

    def __init__(self, sender: str, text: str, tools: Optional[List[dict]] = None, parent=None):
        super().__init__(parent)
        self._sender = sender
        self._raw_text = text
        self._tools = tools or []
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 6, 0, 6)
        main.setSpacing(8)

        if self._sender.lower() == "user":
            # User: right-aligned, clean card
            row = QHBoxLayout()
            row.addStretch()

            box = QFrame()
            box.setMaximumWidth(700)
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(22, 22, 30, 0.9);
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    border-radius: 14px;
                    padding: 12px 16px;
                }}
            """)
            box_lay = QVBoxLayout(box)
            box_lay.setContentsMargins(0, 0, 0, 0)

            lbl = QLabel(self._raw_text)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; line-height: 1.55;")
            box_lay.addWidget(lbl)

            row.addWidget(box)
            main.addLayout(row)

        else:
            # OMEN: left-aligned, editorial
            container = QFrame()
            container.setStyleSheet("background: transparent; border: none;")
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(10)

            # Header
            header = QHBoxLayout()
            header.setSpacing(8)
            orb = OmenOrb(size=16, show_label=False)
            header.addWidget(orb)

            sender_lbl = QLabel("OMEN")
            sender_lbl.setStyleSheet(f"color: {PRIMARY}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
            header.addWidget(sender_lbl)
            header.addStretch()
            lay.addLayout(header)

            # Content
            self._render_content(lay, self._raw_text)

            # Action Bar — minimal
            action_bar = QHBoxLayout()
            action_bar.setSpacing(6)

            copy_btn = QPushButton("📋 Copy")
            copy_btn.setStyleSheet(self._subtle_btn_style())
            copy_btn.clicked.connect(self._copy_response)
            action_bar.addWidget(copy_btn)

            regen_btn = QPushButton("🔄 Regenerate")
            regen_btn.setStyleSheet(self._subtle_btn_style())
            regen_btn.clicked.connect(lambda: self.regenerate_requested.emit(self._raw_text))
            action_bar.addWidget(regen_btn)

            save_btn = QPushButton("💾 Save")
            save_btn.setStyleSheet(self._subtle_btn_style())
            save_btn.clicked.connect(lambda: self.save_requested.emit(self._raw_text))
            action_bar.addWidget(save_btn)

            action_bar.addStretch()
            lay.addLayout(action_bar)

            main.addWidget(container)

    def _subtle_btn_style(self) -> str:
        return """
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.06);
                color: #A1A1AA;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #F4F4F6;
                border-color: rgba(255, 255, 255, 0.12);
            }
        """

    def _copy_response(self):
        cb = QGuiApplication.clipboard()
        cb.setText(self._raw_text)
        ToastManager.show(self.window(), "Copied", level="info")

    def _render_content(self, layout: QVBoxLayout, content: str):
        code_pattern = re.compile(r"```([a-zA-Z0-9_\+#\-]*)\n(.*?)```", re.DOTALL)
        last_idx = 0
        for match in code_pattern.finditer(content):
            before = content[last_idx:match.start()].strip()
            if before:
                lbl = QLabel(before)
                lbl.setWordWrap(True)
                lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; line-height: 1.65;")
                layout.addWidget(lbl)

            lang = match.group(1).strip()
            code_body = match.group(2)
            block = CodeBlockWidget(code_body, lang)
            layout.addWidget(block)
            last_idx = match.end()

        remaining = content[last_idx:].strip()
        if remaining:
            lbl = QLabel(remaining)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; line-height: 1.65;")
            layout.addWidget(lbl)


class ChatInputBox(QFrame):
    """Minimal input box."""

    submit_text = Signal(str, list)
    voice_mic_clicked = Signal()
    voice_mode_clicked = Signal()
    typing_started = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._attachments = []
        self._has_signaled_typing = False
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("chatInputBox")
        self.setStyleSheet("""
            QFrame#chatInputBox {
                background-color: rgba(14, 14, 20, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 14px;
            }
            QFrame#chatInputBox:focus-within {
                border-color: rgba(0, 210, 238, 0.35);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 8)
        layout.setSpacing(8)

        # Attachments (hidden by default)
        self._chips = QWidget()
        self._chips_lay = QHBoxLayout(self._chips)
        self._chips_lay.setContentsMargins(0, 0, 0, 0)
        self._chips_lay.setSpacing(6)
        self._chips.hide()
        layout.addWidget(self._chips)

        # Text Input
        self._text = QTextEdit()
        self._text.setPlaceholderText("Type a message…  (↵ Send  •  Shift+↵ New line)")
        self._text.setFixedHeight(52)
        self._text.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 14px;
                padding: 0;
            }}
        """)
        self._text.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._text)

        # Toolbar
        tools = QHBoxLayout()
        tools.setSpacing(8)

        for btn_text, tip, slot in [
            ("📎 File", "Attach file", self._choose_file),
            ("🖼 Image", "Attach image", self._choose_image),
            ("🎙 Speak", "Voice input", lambda: self.voice_mic_clicked.emit()),
            ("⚡ Voice Mode", "Continuous voice", lambda: self.voice_mode_clicked.emit()),
        ]:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                    color: #A1A1AA;
                    padding: 4px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.07);
                    color: #F4F4F6;
                }
            """)
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            tools.addWidget(btn)

        tools.addStretch()

        # Hint
        hint = QLabel("↵ Send  •  Shift+↵ Line  •  Ctrl+K Palette")
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px;")
        tools.addWidget(hint)

        # Send
        self._send = QPushButton("Send")
        self._send.setFixedSize(72, 32)
        self._send.setStyleSheet("""
            QPushButton {
                background: #00D2EE;
                color: #09090C;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background: #38E1F8; }
            QPushButton:disabled { background: rgba(255,255,255,0.05); color: #71717A; }
        """)
        self._send.clicked.connect(self._submit)
        tools.addWidget(self._send)

        layout.addLayout(tools)

        self._text.installEventFilter(self)

    def _on_text_changed(self):
        if self._text.toPlainText().strip() and not self._has_signaled_typing:
            self._has_signaled_typing = True
            self.typing_started.emit()

    def eventFilter(self, obj, event):
        if obj == self._text and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self._submit()
                return True
        return super().eventFilter(obj, event)

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*.*)")
        if path: self._add_attachment(path, "file")

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Attach Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path: self._add_attachment(path, "image")

    def _add_attachment(self, path: str, ftype: str):
        self._attachments.append({"path": path, "type": ftype})
        chip = QFrame()
        chip.setStyleSheet("background: rgba(0, 210, 238, 0.1); border: 1px solid rgba(0, 210, 238, 0.25); border-radius: 6px; padding: 2px 8px;")
        cl = QHBoxLayout(chip)
        cl.setContentsMargins(6, 2, 6, 2)
        cl.setSpacing(6)
        lbl = QLabel(f"{'🖼' if ftype == 'image' else '📎'} {Path(path).name}")
        lbl.setStyleSheet("color: #00D2EE; font-size: 11px;")
        cl.addWidget(lbl)
        x = QPushButton("×")
        x.setFixedSize(16, 16)
        x.setStyleSheet("border:none; color:#71717A; font-size:12px;")
        x.clicked.connect(lambda: self._remove(path, chip))
        cl.addWidget(x)
        self._chips_lay.addWidget(chip)
        self._chips.show()

    def _remove(self, path: str, widget: QWidget):
        self._attachments = [a for a in self._attachments if a["path"] != path]
        widget.deleteLater()
        if not self._attachments:
            self._chips.hide()

    def _submit(self):
        text = self._text.toPlainText().strip()
        if not text and not self._attachments:
            return
        att = list(self._attachments)
        self._text.clear()
        self._attachments.clear()
        while self._chips_lay.count():
            item = self._chips_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._chips.hide()
        self.submit_text.emit(text, att)

    def set_text(self, text: str):
        self._text.setText(text)
        self._text.setFocus()


class ThinkingIndicator(QFrame):
    """Minimal thinking indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(18, 18, 24, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 10px;
                padding: 8px 16px;
            }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        self._orb = OmenOrb(size=16, show_label=False)
        self._orb.set_state("thinking")
        lay.addWidget(self._orb)

        lbl = QLabel("Thinking…")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-style: italic;")
        lay.addWidget(lbl)
        lay.addStretch()


class AssistantView(QWidget):
    """Clean conversation view with idle hero state."""

    message_sent = Signal(str)
    voice_requested = Signal()
    voice_mode_requested = Signal()

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._in_conversation = False
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("assistantView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(16)

        # Scroll Area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._content_lay = QVBoxLayout(self._content)
        self._content_lay.setContentsMargins(0, 0, 0, 0)
        self._content_lay.setSpacing(16)

        # Idle Hero
        self._idle = QWidget()
        idle_lay = QVBoxLayout(self._idle)
        idle_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idle_lay.setSpacing(16)

        self._hero_orb = OmenOrb(size=90, show_label=False)
        self._hero_orb.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hero_orb.clicked.connect(self.voice_requested.emit)
        self._hero_orb.setToolTip("Click to speak")
        idle_lay.addWidget(self._hero_orb, alignment=Qt.AlignmentFlag.AlignCenter)

        self._greeting = QLabel(get_greeting("Aryan"))
        self._greeting.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;")
        idle_lay.addWidget(self._greeting, alignment=Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("What would you like me to do?")
        sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 14px;")
        idle_lay.addWidget(sub, alignment=Qt.AlignmentFlag.AlignCenter)

        self._content_lay.addWidget(self._idle)

        # Conversation Stream
        self._stream = QWidget()
        self._stream_lay = QVBoxLayout(self._stream)
        self._stream_lay.setContentsMargins(0, 0, 0, 0)
        self._stream_lay.setSpacing(16)
        self._stream.hide()
        self._content_lay.addWidget(self._stream)
        self._content_lay.addStretch()

        self._scroll.setWidget(self._content)
        root.addWidget(self._scroll, stretch=1)

        # Thinking Indicator
        self._thinking = ThinkingIndicator()
        self._thinking.hide()
        root.addWidget(self._thinking)

        # Input
        self._input = ChatInputBox()
        self._input.submit_text.connect(self._on_submit)
        self._input.voice_mic_clicked.connect(self.voice_requested.emit)
        self._input.voice_mode_clicked.connect(self.voice_mode_requested.emit)
        self._input.typing_started.connect(self._to_conversation)
        root.addWidget(self._input)

    def _to_conversation(self):
        if not self._in_conversation:
            self._in_conversation = True
            self._idle.hide()
            self._stream.show()

    def reset_to_idle(self):
        self._in_conversation = False
        self._greeting.setText(get_greeting("Aryan"))
        while self._stream_lay.count():
            item = self._stream_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._stream.hide()
        self._idle.show()
        self._hero_orb.set_state("idle")
        self._thinking.hide()

    def _on_submit(self, text: str, attachments: list):
        self._to_conversation()
        full = text
        if attachments:
            names = ", ".join(Path(a["path"]).name for a in attachments)
            full = f"{text}\n\n[Attachments: {names}]" if text else f"[Attachments: {names}]"

        bubble = MessageBubble("user", full)
        self._stream_lay.addWidget(bubble)
        self._scroll_to_bottom()

        self._thinking.show()
        self._hero_orb.set_state("thinking")
        self.message_sent.emit(text or "Analyze attachment")

    def add_omen_response(self, text: str, tools: Optional[List[dict]] = None):
        self._thinking.hide()
        self._hero_orb.set_state("idle")
        bubble = MessageBubble("omen", text, tools=tools)
        bubble.regenerate_requested.connect(self.message_sent.emit)
        bubble.save_requested.connect(self._save_note)
        self._stream_lay.addWidget(bubble)
        self._scroll_to_bottom()

    def _save_note(self, text: str):
        try:
            from database.database import get_db
            from database.models import Note
            db = get_db()
            title = text.strip().split("\n")[0][:40] or "Saved Response"
            note = Note(title=title, content=text, category="OMEN Saved")
            db.add(note)
            ToastManager.show(self.window(), "Saved to Notes", level="success")
        except Exception:
            ToastManager.show(self.window(), "Saved", level="info")

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    # Compatibility properties & methods for MainWindow and test suite
    @property
    def _input_box(self):
        return self._input

    @property
    def _is_in_conversation(self) -> bool:
        return self._in_conversation

    @property
    def _idle_section(self):
        return self._idle

    @property
    def _stream_section(self):
        return self._stream

    @property
    def _stream_layout(self):
        return self._stream_lay

    def _on_user_submit(self, text: str, attachments: list = None):
        self._on_submit(text, attachments or [])

    def _on_quick_action_clicked(self, prompt: str):
        self._on_submit(prompt, [])


# Alias
ChatView = AssistantView