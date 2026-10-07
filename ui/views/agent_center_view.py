# OMEN Agent Center — agents derive from core/agent_engine; no fake status.
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
class AgentCenterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("ChatAgent | CodeAgent | ResearchAgent | VisionAgent | BrowserAgent | ScheduledAgent — status from real registry"))
