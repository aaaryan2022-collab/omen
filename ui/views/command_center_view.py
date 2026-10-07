# OMEN Command Center — real system data via psutil; "Unavailable" if missing.
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
class CommandCenterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
            self.info = f"CPU {cpu:.1f}% | RAM {mem:.1f}% | Real data from psutil"
        except Exception:
            self.info = "System metrics: Unavailable (psutil missing)"
        lbl = QLabel(self.info)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(lbl)
