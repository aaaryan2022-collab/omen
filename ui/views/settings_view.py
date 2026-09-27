"""
Settings & System Configuration View for OMEN.
Allows adjusting voice attributes, models, directories, and persona presets.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSlider, QCheckBox, QComboBox, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.config import config
from voice.tts import OmenTTS
from ui.styles.palette import PRIMARY, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class SettingsView(QWidget):
    """OMEN System Configuration Deck."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tts = OmenTTS()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("SYSTEM SETTINGS & PERSONA CONFIGURATION")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        subtitle = QLabel("Configure OMEN voice synthesis, Ollama LLM provider endpoints, and safety controls.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        save_btn = QPushButton("💾 SAVE CONFIGURATION")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_settings)
        header.addWidget(save_btn)
        layout.addLayout(header)

        # Scrollable Settings Container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        container = QWidget()
        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(16)

        # 1. Voice & Speech Synthesis Card
        voice_card = QFrame()
        voice_card.setStyleSheet(f"background-color: {BACKGROUND_CARD}; border: 1px solid #1E2C48; border-radius: 12px; padding: 16px;")
        vc_layout = QVBoxLayout(voice_card)
        vc_title = QLabel("🔊 VOICE SYNTHESIS & AUDITORY PARAMETERS")
        vc_title.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-family: Consolas;")
        vc_layout.addWidget(vc_title)

        # Voice Enable
        self._chk_voice = QCheckBox("Enable OMEN Voice Responses")
        self._chk_voice.setChecked(config.voice_enabled)
        self._chk_voice.setStyleSheet("color: #F1F5F9; font-size: 10.5pt;")
        vc_layout.addWidget(self._chk_voice)

        # Voice Selector
        voice_sel_box = QHBoxLayout()
        voice_sel_box.addWidget(QLabel("Active TTS Voice Profile:"))
        self._voice_combo = QComboBox()
        voices = self._tts.get_voices()
        for v in voices:
            self._voice_combo.addItem(f"{v.name} ({v.language})", v.id)
        if config.voice_index < len(voices):
            self._voice_combo.setCurrentIndex(config.voice_index)
        voice_sel_box.addWidget(self._voice_combo, stretch=1)
        vc_layout.addLayout(voice_sel_box)

        # Speed Slider
        speed_box = QHBoxLayout()
        speed_box.addWidget(QLabel("Speech Rate (WPM):"))
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(100, 250)
        self._speed_slider.setValue(config.voice_rate)
        self._speed_val = QLabel(f"{config.voice_rate} WPM")
        self._speed_slider.valueChanged.connect(lambda val: self._speed_val.setText(f"{val} WPM"))
        speed_box.addWidget(self._speed_slider, stretch=1)
        speed_box.addWidget(self._speed_val)
        vc_layout.addLayout(speed_box)

        test_voice_btn = QPushButton("Test Voice Synthesis")
        test_voice_btn.clicked.connect(self._test_voice)
        vc_layout.addWidget(test_voice_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        form_layout.addWidget(voice_card)

        # 2. LLM & Intelligence Endpoint Card
        llm_card = QFrame()
        llm_card.setStyleSheet(f"background-color: {BACKGROUND_CARD}; border: 1px solid #1E2C48; border-radius: 12px; padding: 16px;")
        llm_layout = QVBoxLayout(llm_card)
        llm_title = QLabel("🧠 LOCAL AI BRAIN & INFERENCE ENDPOINT")
        llm_title.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-family: Consolas;")
        llm_layout.addWidget(llm_title)

        url_box = QHBoxLayout()
        url_box.addWidget(QLabel("Ollama Server URL:"))
        self._ollama_url = QLineEdit(config.ollama_base_url)
        url_box.addWidget(self._ollama_url, stretch=1)
        llm_layout.addLayout(url_box)

        model_box = QHBoxLayout()
        model_box.addWidget(QLabel("Default LLM Model:"))
        self._ollama_model = QLineEdit(config.ollama_model)
        model_box.addWidget(self._ollama_model, stretch=1)
        llm_layout.addLayout(model_box)

        vision_box = QHBoxLayout()
        vision_box.addWidget(QLabel("Vision Model:"))
        self._vision_model = QLineEdit(config.ollama_vision_model)
        vision_box.addWidget(self._vision_model, stretch=1)
        llm_layout.addLayout(vision_box)

        form_layout.addWidget(llm_card)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _test_voice(self):
        text = "Hello Axion. All core OMEN systems are online and functioning at optimal efficiency."
        self._tts.speak(text)

    def _save_settings(self):
        config.voice_enabled = self._chk_voice.isChecked()
        config.voice_rate = self._speed_slider.value()
        config.voice_index = self._voice_combo.currentIndex()
        config.ollama_base_url = self._ollama_url.text().strip()
        config.ollama_model = self._ollama_model.text().strip()
        config.ollama_vision_model = self._vision_model.text().strip()
