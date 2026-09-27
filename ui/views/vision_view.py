"""
Screen Vision & Multimodal Perception View for OMEN.
Allows real-time desktop snapshot analysis, target coordinate detection, and OCR summary.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap
from tools.vision import capture_screen_base64, analyze_screen, locate_screen_target
from tools.media.media_ops import TakeScreenshotTool
from ui.styles.palette import PRIMARY, SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND_CARD


class VisionWorker(QThread):
    analysis_ready = Signal(str, str)  # screenshot_path, analysis_text
    error = Signal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self._prompt = prompt

    def run(self):
        try:
            # Capture screenshot
            tool = TakeScreenshotTool()
            res = tool.execute(monitor=1)
            path = res.data.get("file_path") if res.success and res.data else ""

            # Run vision model
            try:
                analysis = analyze_screen(prompt=self._prompt)
            except Exception as e:
                analysis = f"Snapshot captured ({path}). Local Ollama vision model (moondream/llava) note: {e}"

            self.analysis_ready.emit(path, analysis)
        except Exception as exc:
            self.error.emit(str(exc))


class VisionView(QWidget):
    """Visual Multimodal Perception Deck."""

    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("MULTIMODAL VISION & SCREEN PERCEPTION")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        title_box.addWidget(title)

        subtitle = QLabel("On-demand screen inspection, OCR analysis, and visual UI target localization.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self._scan_btn = QPushButton("📷 CAPTURE & ANALYZE SCREEN")
        self._scan_btn.setObjectName("primaryBtn")
        self._scan_btn.clicked.connect(self._run_scan)
        header.addWidget(self._scan_btn)
        layout.addLayout(header)

        # Main Split Content
        content_split = QHBoxLayout()
        content_split.setSpacing(16)

        # Left: Screen Preview Frame
        preview_card = QFrame()
        preview_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        preview_layout = QVBoxLayout(preview_card)
        p_label = QLabel("DESKTOP VIEWPORT SCAN")
        p_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        preview_layout.addWidget(p_label)

        self._image_label = QLabel("Click 'Capture & Analyze Screen' to take an optical snapshot.")
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet("color: #64748B; font-size: 10pt; min-height: 280px;")
        self._image_label.setScaledContents(True)
        preview_layout.addWidget(self._image_label, stretch=1)
        content_split.addWidget(preview_card, stretch=3)

        # Right: Vision Analysis Result
        result_card = QFrame()
        result_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid #1E2C48;
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        result_layout = QVBoxLayout(result_card)
        r_label = QLabel("AI VISUAL INTERPRETATION")
        r_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        result_layout.addWidget(r_label)

        self._analysis_text = QTextEdit()
        self._analysis_text.setReadOnly(True)
        self._analysis_text.setPlaceholderText("Analysis results will appear here...")
        self._analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #0D131F;
                border: 1px solid #1E2C48;
                border-radius: 8px;
                padding: 12px;
                color: #F1F5F9;
                font-size: 10.5pt;
                line-height: 1.5;
            }
        """)
        result_layout.addWidget(self._analysis_text, stretch=1)
        content_split.addWidget(result_card, stretch=2)

        layout.addLayout(content_split)

    def _run_scan(self):
        self._scan_btn.setEnabled(False)
        self._scan_btn.setText("SCANNING SCREEN...")
        self._analysis_text.setText("Capturing high-resolution desktop frame and processing through vision engine...")

        self._worker = VisionWorker(prompt="Describe the contents of this screen in detail, identifying any active windows, text, and main UI elements.", parent=self)
        self._worker.analysis_ready.connect(self._on_analysis_ready)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(lambda: (self._scan_btn.setEnabled(True), self._scan_btn.setText("📷 CAPTURE & ANALYZE SCREEN")))
        self._worker.start()

    def _on_analysis_ready(self, img_path: str, analysis: str):
        if img_path and Path(img_path).exists():
            pix = QPixmap(img_path)
            self._image_label.setPixmap(pix.scaled(600, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self._analysis_text.setText(analysis)

    def _on_error(self, err: str):
        self._analysis_text.setText(f"Vision analysis failed: {err}")
