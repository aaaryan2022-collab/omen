# ============================================
"""
OMEN Assistant & Conversation Deck.
Features:
- Dynamic context-aware greeting ("Good afternoon, Aryan.")
- Hero idle state with OmenOrb, large command box, and 6 quick action cards
- Smooth transition to conversation view
- Editorial-native AI responses with Markdown, code blocks, copy/regenerate/save actions
- Tool/action execution telemetry chips
- File and image attachment support
- Non-intrusive "OMEN is thinking..." indicator
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QFrame, QScrollArea, QSizePolicy, QFileDialog, QGraphicsDropShadowEffect,
    QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QColor, QKeyEvent, QGuiApplication

from ui.orb import OmenOrb
from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, PRIMARY_LIGHT, SECONDARY, BACKGROUND_DARK,
    BACKGROUND_CARD, BACKGROUND_HOVER, BORDER, BORDER_ACTIVE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, SUCCESS, WARNING,
)


def get_greeting(user_name: str = "Aryan") -> str:
    """Return time-based greeting."""
    hour = datetime.now().hour
    if 4 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    else:
        period = "evening"
    return f"Good {period}, {user_name}."


class QuickActionCard(QFrame):
    """Interactive suggestion card with subtle hover micro-interaction."""

    clicked = Signal(str)

    def __init__(self, title: str, subtitle: str, icon: str, prompt: str, parent=None):
        super().__init__(parent)
        self._prompt = prompt
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 10px 14px;
            }
            QFrame:hover {
                background-color: rgba(27, 27, 36, 0.95);
                border-color: rgba(0, 210, 238, 0.35);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        text_layout.addWidget(t_lbl)

        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        text_layout.addWidget(s_lbl)

        layout.addLayout(text_layout, stretch=1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._prompt)
        super().mousePressEvent(event)


class CodeBlockWidget(QFrame):
    """Syntax styled code snippet with a one-click copy button."""

    def __init__(self, code: str, language: str = "", parent=None):
        super().__init__(parent)
        self._code = code
        self.setStyleSheet("""
            QFrame {
                background-color: #0D0D12;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # Header bar
        header = QHBoxLayout()
        lang_lbl = QLabel(language.upper() if language else "CODE")
        lang_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: bold; font-family: Consolas;")
        header.addWidget(lang_lbl)
        header.addStretch()

        self._copy_btn = QPushButton("Copy Code")
        self._copy_btn.setFixedSize(76, 22)
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 4px;
                color: #A1A1AA;
                font-size: 10.5px;
            }
            QPushButton:hover {
                background: rgba(0, 210, 238, 0.15);
                color: #00D2EE;
                border-color: #00D2EE;
            }
        """)
        self._copy_btn.clicked.connect(self._copy)
        header.addWidget(self._copy_btn)
        layout.addLayout(header)

        # Code content
        code_lbl = QLabel(code)
        code_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        code_lbl.setStyleSheet(f"color: #E2E8F0; font-family: Consolas, monospace; font-size: 12px; line-height: 1.4;")
        layout.addWidget(code_lbl)

    def _copy(self):
        cb = QGuiApplication.clipboard()
        cb.setText(self._code)
        self._copy_btn.setText("Copied!")
        QTimer.singleShot(1500, lambda: self._copy_btn.setText("Copy Code"))


class ToolTelemetryChip(QFrame):
    """Subtle badge displaying executed tools and status."""

    def __init__(self, tool_name: str, status: str = "Completed", detail: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 210, 238, 0.06);
                border: 1px solid rgba(0, 210, 238, 0.20);
                border-radius: 6px;
                padding: 4px 10px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        icon = QLabel("⚡")
        icon.setStyleSheet(f"color: {PRIMARY}; font-size: 11px;")
        layout.addWidget(icon)

        text = QLabel(f"Executed: <b>{tool_name}</b> · {status} {f'({detail})' if detail else ''}")
        text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(text)
        layout.addStretch()


class MessageBubble(QWidget):
    """Native editorial message rendering."""

    regenerate_requested = Signal(str)
    save_requested = Signal(str)

    def __init__(self, sender: str, text: str, tools: Optional[List[dict]] = None, parent=None):
        super().__init__(parent)
        self._sender = sender
        self._raw_text = text
        self._tools = tools or []
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 4, 0, 8)
        main_layout.setSpacing(6)

        if self._sender.lower() == "user":
            # User message: Minimalist clean card aligned right
            user_row = QHBoxLayout()
            user_row.addStretch()

            box = QFrame()
            box.setMaximumWidth(680)
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(28, 28, 38, 0.95);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 10px 16px;
                }}
            """)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 0, 0, 0)

            lbl = QLabel(self._raw_text)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13.5px; line-height: 1.5;")
            box_layout.addWidget(lbl)

            user_row.addWidget(box)
            main_layout.addLayout(user_row)

        else:
            # OMEN Response: Editorial native layout
            omen_container = QFrame()
            omen_container.setStyleSheet(f"""
                QFrame {{
                    background: transparent;
                    border: none;
                }}
            """)
            o_layout = QVBoxLayout(omen_container)
            o_layout.setContentsMargins(0, 6, 0, 6)
            o_layout.setSpacing(10)

            # Header with small OMEN orb icon
            header = QHBoxLayout()
            header.setSpacing(8)
            orb = OmenOrb(size=18, show_label=False)
            header.addWidget(orb)

            sender_lbl = QLabel("OMEN")
            sender_lbl.setStyleSheet(f"color: {PRIMARY}; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
            header.addWidget(sender_lbl)
            header.addStretch()

            o_layout.addLayout(header)

            # Tool telemetry chips if any tools were executed
            for t in self._tools:
                t_name = t.get("tool", "Action")
                t_status = t.get("status", "Completed")
                chip = ToolTelemetryChip(t_name, t_status)
                o_layout.addWidget(chip)

            # Render text and code blocks
            self._render_formatted_content(o_layout, self._raw_text)

            # Action Bar (Copy, Regenerate, Save)
            action_bar = QHBoxLayout()
            action_bar.setSpacing(8)
            action_bar.setContentsMargins(0, 4, 0, 0)

            copy_btn = QPushButton("📋 Copy")
            copy_btn.setToolTip("Copy response to clipboard")
            self._style_subtle_btn(copy_btn)
            copy_btn.clicked.connect(self._copy_response)
            action_bar.addWidget(copy_btn)

            regen_btn = QPushButton("🔄 Regenerate")
            regen_btn.setToolTip("Ask OMEN to regenerate this answer")
            self._style_subtle_btn(regen_btn)
            regen_btn.clicked.connect(lambda: self.regenerate_requested.emit(self._raw_text))
            action_bar.addWidget(regen_btn)

            save_btn = QPushButton("💾 Save to Notes")
            save_btn.setToolTip("Save response into OMEN Notes")
            self._style_subtle_btn(save_btn)
            save_btn.clicked.connect(lambda: self.save_requested.emit(self._raw_text))
            action_bar.addWidget(save_btn)

            action_bar.addStretch()
            o_layout.addLayout(action_bar)

            main_layout.addWidget(omen_container)

    def _style_subtle_btn(self, btn: QPushButton):
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: #A1A1AA;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                color: #F4F4F6;
                border-color: rgba(255, 255, 255, 0.16);
            }
        """)

    def _copy_response(self):
        cb = QGuiApplication.clipboard()
        cb.setText(self._raw_text)
        ToastManager.show(self.window(), "Response copied to clipboard", level="info")

    def _render_formatted_content(self, layout: QVBoxLayout, content: str):
        # Extract code blocks
        code_pattern = re.compile(r"```([a-zA-Z0-9_\+#\-]*)\n(.*?)```", re.DOTALL)
        last_idx = 0
        for match in code_pattern.finditer(content):
            before = content[last_idx:match.start()].strip()
            if before:
                lbl = QLabel(before)
                lbl.setWordWrap(True)
                lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13.5px; line-height: 1.6;")
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
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13.5px; line-height: 1.6;")
            layout.addWidget(lbl)


class ChatInputBox(QFrame):
    """Command input box with attachment support, mic, voice mode, and send."""

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
                background-color: rgba(18, 18, 25, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
            }
            QFrame#chatInputBox:focus-within {
                border-color: rgba(0, 210, 238, 0.45);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(6)

        # Attachment chips container
        self._chips_container = QWidget()
        self._chips_layout = QHBoxLayout(self._chips_container)
        self._chips_layout.setContentsMargins(0, 0, 0, 0)
        self._chips_layout.setSpacing(6)
        self._chips_container.hide()
        layout.addWidget(self._chips_container)

        # Text input area
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Ask OMEN anything, plan an objective, or assign a task...")
        self._text_edit.setFixedHeight(48)
        self._text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 13.5px;
                padding: 0;
            }}
        """)
        self._text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._text_edit)

        # Toolbar Row
        tools_row = QHBoxLayout()
        tools_row.setContentsMargins(0, 4, 0, 0)
        tools_row.setSpacing(8)

        # File Attachment
        self._attach_file_btn = QPushButton("📎 File")
        self._style_tool_btn(self._attach_file_btn)
        self._attach_file_btn.setToolTip("Attach a workspace document or script")
        self._attach_file_btn.clicked.connect(self._choose_file)
        tools_row.addWidget(self._attach_file_btn)

        # Image Attachment
        self._attach_img_btn = QPushButton("🖼 Image")
        self._style_tool_btn(self._attach_img_btn)
        self._attach_img_btn.setToolTip("Attach an image for vision processing")
        self._attach_img_btn.clicked.connect(self._choose_image)
        tools_row.addWidget(self._attach_img_btn)

        # Mic button
        self._mic_btn = QPushButton("🎙 Speak")
        self._style_tool_btn(self._mic_btn)
        self._mic_btn.setToolTip("Capture voice utterance")
        self._mic_btn.clicked.connect(self.voice_mic_clicked.emit)
        tools_row.addWidget(self._mic_btn)

        # Dedicated Voice Mode
        self._voice_mode_btn = QPushButton("⚡ Voice Mode")
        self._style_tool_btn(self._voice_mode_btn)
        self._voice_mode_btn.setToolTip("Switch to immersive voice dialogue")
        self._voice_mode_btn.clicked.connect(self.voice_mode_clicked.emit)
        tools_row.addWidget(self._voice_mode_btn)

        tools_row.addStretch()

        # Keyboard Shortcut Hint
        hint_lbl = QLabel("↵ Send · Shift+↵ Line · Ctrl+Space Palette")
        hint_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10.5px;")
        tools_row.addWidget(hint_lbl)

        # Send Button
        self._send_btn = QPushButton("Send ↗")
        self._send_btn.setFixedSize(76, 30)
        self._send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D2EE;
                color: #09090C;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #38E1F8;
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.05);
                color: #71717A;
            }
        """)
        self._send_btn.clicked.connect(self._submit)
        tools_row.addWidget(self._send_btn)

        layout.addLayout(tools_row)

        # Event filter for Enter key
        self._text_edit.installEventFilter(self)

    def _style_tool_btn(self, btn: QPushButton):
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                color: #A1A1AA;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.09);
                color: #F4F4F6;
            }
        """)

    def _on_text_changed(self):
        text = self._text_edit.toPlainText().strip()
        if text and not self._has_signaled_typing:
            self._has_signaled_typing = True
            self.typing_started.emit()

    def eventFilter(self, obj, event):
        if obj == self._text_edit and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._submit()
                    return True
        return super().eventFilter(obj, event)

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Attach File to OMEN", "", "All Files (*.*)")
        if path:
            self._add_attachment(path, "file")

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Attach Image to OMEN", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            self._add_attachment(path, "image")

    def _add_attachment(self, file_path: str, file_type: str):
        self._attachments.append({"path": file_path, "type": file_type})
        chip = QFrame()
        chip.setStyleSheet("""
            QFrame {
                background: rgba(0, 210, 238, 0.12);
                border: 1px solid rgba(0, 210, 238, 0.3);
                border-radius: 6px;
                padding: 2px 6px;
            }
        """)
        c_lay = QHBoxLayout(chip)
        c_lay.setContentsMargins(4, 2, 4, 2)
        c_lay.setSpacing(4)
        name = Path(file_path).name
        lbl = QLabel(f"{'🖼' if file_type == 'image' else '📎'} {name}")
        lbl.setStyleSheet("color: #00D2EE; font-size: 11px;")
        c_lay.addWidget(lbl)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(14, 14)
        del_btn.setStyleSheet("border:none; color:#71717A; font-size:12px;")
        del_btn.clicked.connect(lambda: self._remove_attachment(file_path, chip))
        c_lay.addWidget(del_btn)

        self._chips_layout.addWidget(chip)
        self._chips_container.show()

    def _remove_attachment(self, path: str, widget: QWidget):
        self._attachments = [a for a in self._attachments if a["path"] != path]
        widget.deleteLater()
        if not self._attachments:
            self._chips_container.hide()

    def _submit(self):
        text = self._text_edit.toPlainText().strip()
        if not text and not self._attachments:
            return
        attachments = list(self._attachments)
        self._text_edit.clear()
        self._attachments.clear()
        # Clean chips
        while self._chips_layout.count():
            item = self._chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._chips_container.hide()
        self.submit_text.emit(text, attachments)

    def set_text(self, text: str):
        self._text_edit.setText(text)
        self._text_edit.setFocus()


class ThinkingIndicator(QFrame):
    """Subtle animated 'OMEN is thinking...' bar (no giant spinner)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(21, 21, 28, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 6px 14px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        self._orb = OmenOrb(size=18, show_label=False)
        self._orb.set_state("thinking")
        layout.addWidget(self._orb)

        self._text_lbl = QLabel("OMEN is thinking...")
        self._text_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-style: italic;")
        layout.addWidget(self._text_lbl)
        layout.addStretch()


class AssistantView(QWidget):
    """Primary OMEN Assistant Area with Hero Idle state and Conversation Stream."""

    message_sent = Signal(str)
    voice_requested = Signal()
    voice_mode_requested = Signal()

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._is_in_conversation = False
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("assistantView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 20, 36, 20)
        root_layout.setSpacing(16)

        # Scroll Area for stream or idle content
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(14)

        # 1. Hero Idle Section
        self._idle_section = QWidget()
        idle_layout = QVBoxLayout(self._idle_section)
        idle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idle_layout.setSpacing(14)

        idle_layout.addSpacing(16)

        # OMEN Hero Orb
        self._hero_orb = OmenOrb(size=110, show_label=False)
        self._hero_orb.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hero_orb.clicked.connect(self.voice_requested.emit)
        self._hero_orb.setToolTip("Click to speak with OMEN")
        idle_layout.addWidget(self._hero_orb, alignment=Qt.AlignmentFlag.AlignCenter)

        # Greeting
        self._greeting_label = QLabel(get_greeting("Aryan"))
        self._greeting_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)
        idle_layout.addWidget(self._greeting_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("What would you like me to take care of?")
        subtitle.setStyleSheet(f"color: {TEXT_DIM}; font-size: 14px;")
        idle_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        idle_layout.addSpacing(12)

        # Quick Actions Grid (2x3 cards)
        cards_container = QWidget()
        cards_container.setMaximumWidth(760)
        cards_grid = QHBoxLayout(cards_container)
        cards_grid.setSpacing(12)

        col1 = QVBoxLayout()
        col1.setSpacing(10)
        col2 = QVBoxLayout()
        col2.setSpacing(10)

        actions = [
            ("Summarize my files", "Inspect active workspace documents", "📄", "Summarize the key files and structure in this workspace.", col1),
            ("Open my workspace", "Review repository status & recent tasks", "📁", "Analyze my current workspace and list what needs attention.", col2),
            ("Plan my day", "Organize schedule, priorities & goals", "📅", "Help me plan my day, organize my highest priorities and scheduled tasks.", col1),
            ("Write some code", "Generate clean, production-grade solutions", "⚡", "I want to pair-program on a feature. What can we build?", col2),
            ("Check my tasks", "Review pending items and deadlines", "✓", "Show my pending tasks and upcoming deadlines.", col1),
            ("Explain something", "Deep dive into architecture or concept", "💡", "Explain the architecture of OMEN and how the local engine coordinates tools.", col2),
        ]

        for title, sub, icon, prompt, col in actions:
            card = QuickActionCard(title, sub, icon, prompt)
            card.clicked.connect(self._on_quick_action_clicked)
            col.addWidget(card)

        cards_grid.addLayout(col1)
        cards_grid.addLayout(col2)
        idle_layout.addWidget(cards_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self._content_layout.addWidget(self._idle_section)

        # 2. Conversation Stream Container (hidden until user speaks or types)
        self._stream_section = QWidget()
        self._stream_layout = QVBoxLayout(self._stream_section)
        self._stream_layout.setContentsMargins(0, 0, 0, 0)
        self._stream_layout.setSpacing(14)
        self._stream_section.hide()

        self._content_layout.addWidget(self._stream_section)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content_widget)
        root_layout.addWidget(self._scroll, stretch=1)

        # 3. Thinking Indicator (hidden by default)
        self._thinking_indicator = ThinkingIndicator()
        self._thinking_indicator.hide()
        root_layout.addWidget(self._thinking_indicator)

        # 4. Command Input Box
        self._input_box = ChatInputBox()
        self._input_box.submit_text.connect(self._on_user_submit)
        self._input_box.voice_mic_clicked.connect(self.voice_requested.emit)
        self._input_box.voice_mode_clicked.connect(self.voice_mode_requested.emit)
        self._input_box.typing_started.connect(self._transition_to_conversation)
        root_layout.addWidget(self._input_box)

    def _on_quick_action_clicked(self, prompt: str):
        self._transition_to_conversation()
        self._input_box.set_text(prompt)
        self._on_user_submit(prompt, [])

    def _transition_to_conversation(self):
        if not self._is_in_conversation:
            self._is_in_conversation = True
            self._idle_section.hide()
            self._stream_section.show()

    def reset_to_idle(self):
        """Reset view back to greeting / idle mode for a fresh conversation."""
        self._is_in_conversation = False
        self._greeting_label.setText(get_greeting("Aryan"))
        # Clear stream items
        while self._stream_layout.count():
            item = self._stream_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._stream_section.hide()
        self._idle_section.show()
        self._hero_orb.set_state("idle")
        self._thinking_indicator.hide()

    def _on_user_submit(self, text: str, attachments: list):
        self._transition_to_conversation()
        full_text = text
        if attachments:
            att_names = ", ".join(Path(a["path"]).name for a in attachments)
            full_text = f"{text}\n\n[Attachments: {att_names}]" if text else f"[Attachments: {att_names}]"

        # Add user message bubble
        bubble = MessageBubble("user", full_text)
        self._stream_layout.addWidget(bubble)
        self._scroll_to_bottom()

        # Show thinking indicator
        self.set_thinking(True)
        self.message_sent.emit(text or "Analyze attachment")

    def add_omen_response(self, text: str, tools: Optional[List[dict]] = None):
        self.set_thinking(False)
        bubble = MessageBubble("omen", text, tools=tools)
        bubble.regenerate_requested.connect(self.message_sent.emit)
        bubble.save_requested.connect(self._save_to_notes)
        self._stream_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _save_to_notes(self, text: str):
        try:
            from database.database import get_db
            from database.models import Note
            db = get_db()
            title = text.strip().split("\n")[0][:40] or "Saved Response"
            note = Note(title=title, content=text, category="OMEN Saved")
            db.add(note)
            ToastManager.show(self.window(), "Saved to Notes", level="success")
        except Exception as e:
            ToastManager.show(self.window(), f"Saved locally: {e}", level="info")

    def set_thinking(self, is_thinking: bool):
        if is_thinking:
            self._thinking_indicator.show()
            self._hero_orb.set_state("thinking")
        else:
            self._thinking_indicator.hide()
            self._hero_orb.set_state("idle")
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))


# Backward compatibility alias
ChatView = AssistantView
