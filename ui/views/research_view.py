# ============================================
"""
Deep Research & Web Investigation Studio View for OMEN.
Features:
- Multi-query search decomposition
- Live investigation progress
- Evidence extraction & citations viewer
- Structured Markdown report generator
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from core.research.deep_research import deep_research_agent, ResearchReport
from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BACKGROUND_DARK, BACKGROUND_CARD, FONT_FAMILY
)


class ResearchWorker(QThread):
    report_ready = Signal(object)
    failed = Signal(str)

    def __init__(self, topic: str, max_sources: int = 5, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.max_sources = max_sources

    def run(self):
        try:
            report = deep_research_agent.conduct_research(self.topic, self.max_sources)
            self.report_ready.emit(report)
        except Exception as e:
            self.failed.emit(str(e))


class ResearchView(QWidget):
    """Deep Research & Web Investigation Studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("DEEP RESEARCH & WEB SYNTHESIS STUDIO")
        title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 1.5px;")
        title_box.addWidget(title)

        subtitle = QLabel("Multi-hop Query Planning · Recursive Web Scraping · Evidence Citations · Report Synthesis")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # Input Row
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_CARD};
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        card_layout = QHBoxLayout(search_card)

        self._topic_input = QLineEdit()
        self._topic_input.setFont(QFont(FONT_FAMILY, 11))
        self._topic_input.setPlaceholderText("Enter research topic (e.g. 'Advances in Quantum Error Correction 2026')...")
        self._topic_input.returnPressed.connect(self._start_research)
        self._topic_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.04);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)

        self._btn_research = QPushButton("🔎 Start Deep Research")
        self._btn_research.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        self._btn_research.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 210, 238, 0.15);
                color: {PRIMARY};
                border: 1px solid {PRIMARY};
                border-radius: 6px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 210, 238, 0.25);
            }}
        """)
        self._btn_research.clicked.connect(self._start_research)

        card_layout.addWidget(self._topic_input)
        card_layout.addWidget(self._btn_research)
        layout.addWidget(search_card)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{ border: none; background: rgba(255, 255, 255, 0.05); }}
            QProgressBar::chunk {{ background: {PRIMARY}; }}
        """)
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        # Main Splitter: Left (Report Viewer), Right (Evidence & Citations)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Report Viewer
        report_box = QWidget()
        rep_layout = QVBoxLayout(report_box)
        rep_layout.setContentsMargins(0, 0, 0, 0)

        rep_label = QLabel("📑 Synthesized Research Report")
        rep_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 10pt;")
        rep_layout.addWidget(rep_label)

        self._report_viewer = QTextEdit()
        self._report_viewer.setFont(QFont("Segoe UI", 10.5))
        self._report_viewer.setReadOnly(True)
        self._report_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #0B0E14;
                color: #E2E8F0;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                padding: 16px;
                line-height: 1.5;
            }
        """)
        self._report_viewer.setPlaceholderText("Synthesized multi-source research report will appear here...")
        rep_layout.addWidget(self._report_viewer)
        splitter.addWidget(report_box)

        # Citations Table
        cite_box = QWidget()
        cite_layout = QVBoxLayout(cite_box)
        cite_layout.setContentsMargins(0, 0, 0, 0)

        cite_label = QLabel("🔗 Source Evidence & Citations")
        cite_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 10pt;")
        cite_layout.addWidget(cite_label)

        self._citations_table = QTableWidget(0, 3)
        self._citations_table.setHorizontalHeaderLabels(["Title", "URL", "Snippet"])
        self._citations_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self._citations_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self._citations_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._citations_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #07090E;
                color: {TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                gridline-color: rgba(255, 255, 255, 0.04);
            }}
            QHeaderView::section {{
                background-color: #0E121B;
                color: {TEXT_SECONDARY};
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)
        cite_layout.addWidget(self._citations_table)
        splitter.addWidget(cite_box)

        splitter.setSizes([650, 450])
        layout.addWidget(splitter)

    def _start_research(self):
        topic = self._topic_input.text().strip()
        if not topic:
            return
        self._btn_research.setEnabled(False)
        self._progress.show()
        self._report_viewer.setPlainText(f"Investigating '{topic}' across web sources...")
        self._citations_table.setRowCount(0)

        worker = ResearchWorker(topic, max_sources=5, parent=self)
        worker.report_ready.connect(self._on_report_ready)
        worker.failed.connect(self._on_failed)
        worker.start()

    def _on_report_ready(self, report: ResearchReport):
        self._btn_research.setEnabled(True)
        self._progress.hide()
        self._report_viewer.setMarkdown(report.full_markdown)

        self._citations_table.setRowCount(len(report.citations))
        for row, c in enumerate(report.citations):
            self._citations_table.setItem(row, 0, QTableWidgetItem(c.title))
            self._citations_table.setItem(row, 1, QTableWidgetItem(c.source_url))
            self._citations_table.setItem(row, 2, QTableWidgetItem(c.snippet))

    def _on_failed(self, err: str):
        self._btn_research.setEnabled(True)
        self._progress.hide()
        self._report_viewer.setPlainText(f"Research failed: {err}")
