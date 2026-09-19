
"""
Main application window: sidebar, content stack, context bar, emergency stop.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QStatusBar, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from core.events import get_event_bus, EventType
from core.agent import Agent
from ui.sidebar import Sidebar
from ui.dashboard import DashboardView
from ui.chat import ChatView
from ui.styles.palette import PRIMARY, BACKGROUND_DARK, TEXT_PRIMARY, SPACING_DEFAULT, SPACING_LARGE, SPACING_XLARGE


class MainWindow(QMainWindow):
    """
    Primary OMEN desktop window.
    """

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._setup_window()
        self._build_ui()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowTitle("OMEN — AI Assistant")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        self.setStyleSheet("background-color: #0A0E17;")

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        self._central_layout = QHBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)

        # Emergency stop banner
        self._emergency_banner = QLabel("🛑 EMERGENCY STOP ACTIVE — Press CTRL+SHIFT+ESC or CTRL+ALT+Q to reset")
        self._emergency_banner.setHidden(True)
        self._emergency_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(220, 38, 38, 0.9);
                color: white;
                font-weight: bold;
                font-size: 14pt;
                padding: 12px;
                text-align: center;
            }
        """)

        # Status bar
        self.statusBar().setStyleSheet("background-color: #111827; color: #8B9CB8;")

    def _build_ui(self):
        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.setFixedWidth(240)
        self._central_layout.addWidget(self._sidebar)

        # Content area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Emergency banner at top
        content_layout.addWidget(self._emergency_banner)

        # Stack of views
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack)

        self._central_layout.addWidget(content_container)

        # Initialize views
        self._dashboard = DashboardView(self._agent)
        self._chat = ChatView(self._agent)
        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._chat)

    def _connect_signals(self):
        self._sidebar.page_changed.connect(self._switch_page)

        # Emergency stop shortcut
        from PySide6.QtGui import QShortcut
        esc_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Escape"), self)
        esc_shortcut.activated.connect(self._trigger_emergency)

        alt_q_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Q"), self)
        alt_q_shortcut.activated.connect(self._trigger_emergency)

        # Event bus for state changes
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_agent_state)
            bus.subscribe(EventType.ERROR, self._on_error)
        except Exception:
            pass

    def _switch_page(self, page_id: str):
        pages = {
            "dashboard": self._dashboard,
            "chat": self._chat,
        }
        if page_id in pages:
            self._stack.addWidget(pages[page_id])
            self._stack.setCurrentWidget(pages[page_id])

    def _trigger_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.trigger()
        self._emergency_banner.setHidden(False)
        self._chat.add_assistant_message("🛑 EMERGENCY STOP triggered. All operations halted. Use CTRL+SHIFT+ESC or CTRL+ALT+Q to reset.")

    def _on_agent_state(self, event):
        state = event.payload.get("state", "")
        if state == "ERROR":
            self._emergency_banner.setHidden(False)

    def _on_error(self, event):
        self._emergency_banner.setHidden(False)

    def reset_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.reset()
        self._emergency_banner.setHidden(True)

    def keyPressEvent(self, event):
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key.Key_Escape:
            if self._emergency_banner.isVisible():
                self.reset_emergency()
        super().keyPressEvent(event)


