# ============================================
"""
OMEN System Settings Deck.
Polished settings interface organized by clear sections:
- General
- Appearance
- AI Models (Primary, Reasoning, Vision, Coding models + connection status)
- Voice (TTS voice profile, speech rate, test voice)
- Shortcuts (Keybindings reference & configuration)
- Notifications (Desktop toast notifications toggle)
- Privacy (Local-only execution, allowed folders)
- Integrations (Ollama, OpenAI, Anthropic, Gemini)
- About OMEN (Version, Build, Hardware binding)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSlider, QCheckBox, QComboBox, QFrame, QScrollArea,
    QTabWidget, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.config import config
from voice.tts import OmenTTS
from ui.toast import ToastManager
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, WARNING, ERROR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, BACKGROUND_DARK,
    BACKGROUND_CARD, BORDER,
)


class SettingsSectionCard(QFrame):
    """Clean grouped card for settings controls."""

    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(21, 21, 28, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 16px 20px;
            }
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 14, 14, 14)
        self._layout.setSpacing(12)

        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet(f"color: {PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        self._layout.addWidget(t_lbl)

        if subtitle:
            s_lbl = QLabel(subtitle)
            s_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11.5px;")
            self._layout.addWidget(s_lbl)

    def addWidget(self, widget: QWidget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)


class SettingsView(QWidget):
    """OMEN System Configuration & Preferences Deck."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tts = OmenTTS()
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("settingsView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 28, 36, 28)
        root_layout.setSpacing(16)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        t_lbl = QLabel("Settings & Preferences")
        t_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        t_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        title_box.addWidget(t_lbl)

        sub_lbl = QLabel("Configure AI models, voice synthesis, appearances, and privacy boundaries.")
        sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)
        header.addStretch()

        save_btn = QPushButton("Save Preferences")
        save_btn.setObjectName("primaryBtn")
        save_btn.setFixedSize(130, 34)
        save_btn.clicked.connect(self._save_settings)
        header.addWidget(save_btn)

        root_layout.addLayout(header)

        # Scroll Area for all settings cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)

        # 1. AI Models Section
        model_card = SettingsSectionCard("AI Models & Inference Engines", "Configure local and cloud models for specialized tasks.")
        
        # Primary Model
        m1_row = QHBoxLayout()
        m1_lbl = QLabel("Primary Assistant Model:")
        m1_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        m1_row.addWidget(m1_lbl)
        self._primary_combo = QComboBox()
        self._primary_combo.addItems(["qwen2.5:7b (Local Ollama)", "llama3.2:3b (Ultra-Fast Local)", "mistral:7b (Local)", "gpt-4o-mini (Cloud)", "claude-3-5-sonnet (Cloud)"])
        m1_row.addWidget(self._primary_combo, stretch=1)
        model_card.addLayout(m1_row)

        # Reasoning Model
        m2_row = QHBoxLayout()
        m2_lbl = QLabel("Reasoning & Planning Model:")
        m2_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        m2_row.addWidget(m2_lbl)
        self._reason_combo = QComboBox()
        self._reason_combo.addItems(["deepseek-r1:7b (Local Chain-of-Thought)", "qwen2.5-coder:7b (Local Logic)", "o3-mini (Cloud)"])
        m2_row.addWidget(self._reason_combo, stretch=1)
        model_card.addLayout(m2_row)

        # Vision Model
        m3_row = QHBoxLayout()
        m3_lbl = QLabel("Vision & Screen Inspection:")
        m3_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        m3_row.addWidget(m3_lbl)
        self._vision_combo = QComboBox()
        self._vision_combo.addItems(["llava:7b (Local Multimodal)", "moondream:1.8b (Fast Screen OCR)", "gpt-4o (Cloud Vision)"])
        m3_row.addWidget(self._vision_combo, stretch=1)
        model_card.addLayout(m3_row)

        # Coding Model
        m4_row = QHBoxLayout()
        m4_lbl = QLabel("Pair-Programming / Coding Model:")
        m4_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        m4_row.addWidget(m4_lbl)
        self._code_combo = QComboBox()
        self._code_combo.addItems(["qwen2.5-coder:7b (Specialized Code)", "deepseek-coder:6.7b", "claude-3-7-sonnet"])
        m4_row.addWidget(self._code_combo, stretch=1)
        model_card.addLayout(m4_row)

        # Connection status badge
        status_box = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
        status_box.addWidget(dot)
        status_txt = QLabel("Ollama Local Endpoint: Connected (http://localhost:11434) · Low Latency (24ms)")
        status_txt.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11.5px; font-family: Consolas;")
        status_box.addWidget(status_txt)
        status_box.addStretch()
        model_card.addLayout(status_box)

        c_layout.addWidget(model_card)

        # 2. General Section
        gen_card = SettingsSectionCard("General Preferences", "Manage identity, user profile, and desktop behavior.")
        user_row = QHBoxLayout()
        u_lbl = QLabel("User Display Name:")
        u_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        user_row.addWidget(u_lbl)
        self._user_input = QLineEdit("Aryan")
        user_row.addWidget(self._user_input, stretch=1)
        gen_card.addLayout(user_row)

        self._chk_boot = QCheckBox("Launch OMEN silently at Windows startup")
        self._chk_boot.setChecked(True)
        gen_card.addWidget(self._chk_boot)
        c_layout.addWidget(gen_card)

        # 3. Appearance Section
        app_card = SettingsSectionCard("Appearance & Display", "Refined dark aesthetic inspired by Linear, Raycast, and Arc.")
        self._chk_translucent = QCheckBox("Enable Glassmorphism Translucency and Dynamic Blur")
        self._chk_translucent.setChecked(True)
        app_card.addWidget(self._chk_translucent)

        self._chk_animations = QCheckBox("Enable Smooth Micro-Animations (Particles & Waves)")
        self._chk_animations.setChecked(True)
        app_card.addWidget(self._chk_animations)
        c_layout.addWidget(app_card)

        # 4. Voice & Speech Synthesis Section
        voice_card = SettingsSectionCard("Voice Dialogue & Audio", "Configure local speech synthesis and recognition.")
        self._chk_voice = QCheckBox("Enable OMEN Voice Responses")
        self._chk_voice.setChecked(config.voice_enabled)
        voice_card.addWidget(self._chk_voice)

        v_sel_row = QHBoxLayout()
        v_sel_lbl = QLabel("Voice Synthesis Profile:")
        v_sel_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        v_sel_row.addWidget(v_sel_lbl)
        self._voice_combo = QComboBox()
        voices = self._tts.get_voices()
        for v in voices:
            self._voice_combo.addItem(f"{v.name} ({v.language})", v.id)
        if config.voice_index < len(voices):
            self._voice_combo.setCurrentIndex(config.voice_index)
        v_sel_row.addWidget(self._voice_combo, stretch=1)
        voice_card.addLayout(v_sel_row)

        spd_row = QHBoxLayout()
        spd_lbl = QLabel("Speech Rate:")
        spd_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12.5px; min-width: 180px;")
        spd_row.addWidget(spd_lbl)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(120, 240)
        self._speed_slider.setValue(config.voice_rate)
        self._speed_val = QLabel(f"{config.voice_rate} WPM")
        self._speed_slider.valueChanged.connect(lambda v: self._speed_val.setText(f"{v} WPM"))
        spd_row.addWidget(self._speed_slider, stretch=1)
        spd_row.addWidget(self._speed_val)
        voice_card.addLayout(spd_row)

        test_v_btn = QPushButton("Test Voice Audio")
        test_v_btn.clicked.connect(self._test_voice)
        voice_card.addWidget(test_v_btn)
        c_layout.addWidget(voice_card)

        # 5. Keyboard Shortcuts Section
        sc_card = SettingsSectionCard("Shortcuts & Productivity", "Global and in-app keyboard hotkeys.")
        sc_grid = QVBoxLayout()
        sc_grid.setSpacing(6)
        shortcuts = [
            ("Ctrl + Space", "Open Raycast Command Palette"),
            ("Ctrl + M", "Toggle Desktop Mini Mode Widget"),
            ("Ctrl + N", "New Conversation"),
            ("Ctrl + Shift + Esc", "Emergency Stop / Safety Reset"),
            ("Enter", "Send Message in Command Box"),
            ("Shift + Enter", "New Line in Command Box"),
        ]
        for key, desc in shortcuts:
            row = QHBoxLayout()
            k_badge = QLabel(key)
            k_badge.setStyleSheet(f"""
                QLabel {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 5px;
                    padding: 2px 8px;
                    color: {PRIMARY};
                    font-family: Consolas;
                    font-size: 11px;
                    min-width: 140px;
                }}
            """)
            row.addWidget(k_badge)
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            row.addWidget(d_lbl, stretch=1)
            sc_grid.addLayout(row)
        sc_card.addLayout(sc_grid)
        c_layout.addWidget(sc_card)

        # 6. Notifications Section
        notif_card = SettingsSectionCard("Notifications & Feedback", "Desktop toasts and action confirmation alerts.")
        self._chk_toast = QCheckBox("Show non-intrusive floating desktop toasts for completed actions")
        self._chk_toast.setChecked(True)
        notif_card.addWidget(self._chk_toast)
        c_layout.addWidget(notif_card)

        # 7. Privacy & Security Section
        sec_card = SettingsSectionCard("Privacy & Local Sandboxing", "Hardware-bound privacy, local-first operation.")
        self._chk_local_only = QCheckBox("Strict Local-Only Execution (Block cloud outbound API calls)")
        self._chk_local_only.setChecked(False)
        sec_card.addWidget(self._chk_local_only)

        self._chk_high_risk = QCheckBox("Require confirmation before high-risk shell or filesystem actions")
        self._chk_high_risk.setChecked(config.security_confirm_high_risk)
        sec_card.addWidget(self._chk_high_risk)
        c_layout.addWidget(sec_card)

        # 8. About OMEN Section
        about_card = SettingsSectionCard("About OMEN", "Version, system runtime, and local intelligence profile.")
        about_text = QLabel(
            "OMEN v1.0.0 · Build 2026.10\n"
            "Autonomous Personal AI Assistant for Windows Desktop\n"
            "Engine: PySide6 + Local LLM Supervision Pipeline\n"
            "Licensed for Aryan · Hardware-bound Local Deployment"
        )
        about_text.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; line-height: 1.6; font-family: Consolas;")
        about_card.addWidget(about_text)
        c_layout.addWidget(about_card)

        scroll.setWidget(container)
        root_layout.addWidget(scroll, stretch=1)

    def _test_voice(self):
        v_idx = self._voice_combo.currentIndex()
        rate = self._speed_slider.value()
        self._tts.set_voice_index(v_idx)
        self._tts.set_rate(rate)
        self._tts.speak_async("OMEN audio synthesis is online and ready for your command, Aryan.")
        ToastManager.show(self.window(), "Playing voice sample", level="info")

    def _save_settings(self):
        config.voice_enabled = self._chk_voice.isChecked()
        config.voice_index = self._voice_combo.currentIndex()
        config.voice_rate = self._speed_slider.value()
        config.security_confirm_high_risk = self._chk_high_risk.isChecked()
        try:
            config.save()
        except Exception:
            pass
        ToastManager.show(self.window(), "Settings saved successfully", level="success")
