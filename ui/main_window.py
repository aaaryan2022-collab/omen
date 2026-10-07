# ============================================
from memory.fact_memory import FactMemory
from security.permissions_v5 import SCOPES, PermissionManager
from automation.routines import RoutineStore
from history.action_log import ActionLog
from voice.wakeword import WakeWord
from app.agent_orch import AgentOrch
"""
Main Application Window for OMEN — Premium Desktop AI Assistant.
Aesthetic inspired by Linear, Raycast, and Arc.
Dark-first interface, translucent glass panels, subtle electric cyan accents.
Features:
- Collapsible Sidebar with New Chat, Tasks, Calendar, Notes, Files, System, Settings
- Hero Assistant View with dynamic greeting, 6 quick actions, and conversation stream
- Raycast Command Palette (Ctrl + Space)
- Floating Desktop Mini Widget (Ctrl + M)
- Dedicated Voice Dialogue Mode with live visualization
- Toast Notification Feedback
- Multi-threaded Agent Execution
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QFrame, QSizePolicy, QApplication,
)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QRectF
from PySide6.QtGui import QFont, QKeySequence, QPainter, QPen, QColor, QRadialGradient, QBrush, QShortcut

from core.events import get_event_bus, EventType
from core.agent import Agent
from ui.sidebar import Sidebar
from ui.chat import AssistantView
from ui.views.tasks_view import TasksView
from ui.views.calendar_view import CalendarView
from ui.views.notes_view import NotesView
from ui.views.files_view import FilesView
from ui.views.system_view import SystemView
from ui.views.settings_view import SettingsView
from ui.command_palette import CommandPalette
from ui.mini_widget import MiniWidget
from ui.voice_overlay import VoiceOverlay
from ui.toast import ToastManager
from ui.orb import OmenOrb
from voice.stt import OmenSTT
from voice.tts import OmenTTS
from ui.styles.palette import (
    PRIMARY, PRIMARY_DIM, SECONDARY, SUCCESS, ERROR, WARNING,
    BACKGROUND_DARK, BACKGROUND_CARD, BORDER, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_DIM,
)


class HoloBackground(QWidget):
    """Subtle deep dark background — minimal depth gradient, no distracting noise."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Deep warm dark gradient
        bg_grad = QRadialGradient(w / 2.0, h / 2.0, max(w, h) * 0.75)
        bg_grad.setColorAt(0.0, QColor("#0C0C10"))
        bg_grad.setColorAt(0.65, QColor("#09090C"))
        bg_grad.setColorAt(1.0, QColor("#060608"))
        painter.fillRect(self.rect(), QBrush(bg_grad))

        # Very subtle ambient cyan glow at top center
        ambient = QRadialGradient(w / 2.0, 0, w * 0.45)
        ambient.setColorAt(0.0, QColor(0, 210, 238, 12))
        ambient.setColorAt(0.6, QColor(0, 210, 238, 3))
        ambient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(ambient))
        painter.drawEllipse(QRectF(w * 0.1, -h * 0.2, w * 0.8, h * 0.6))

        painter.end()


class VoiceWorker(QThread):
    """Capture microphone utterance off the main GUI thread."""
    transcript = Signal(str)
    unavailable = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener = None

    def run(self):
        self._listener = OmenSTT()
        if not self._listener.is_available:
            self.unavailable.emit("No usable microphone backend is available.")
            return
        text = self._listener.listen_once()
        if text and text.strip():
            self.transcript.emit(text.strip())
        else:
            self.unavailable.emit(self._listener.last_error or "No speech was detected.")

    def cancel(self):
        if self._listener:
            self._listener.stop()


class VoiceMeter(QThread):
    """Microphone audio energy meter."""
    level = Signal(float)

    def run(self):
        try:
            import sounddevice as sd

            def on_audio(indata, frames, time_info, status):
                del frames, time_info, status
                try:
                    samples = memoryview(indata).cast("h")
                    if samples:
                        rms = (sum(float(sample) ** 2 for sample in samples) / len(samples)) ** 0.5
                        self.level.emit(min(1.0, rms / 8000.0))
                except Exception:
                    self.level.emit(0.0)

            with sd.RawInputStream(
                samplerate=16000,
                blocksize=512,
                channels=1,
                dtype="int16",
                callback=on_audio,
            ):
                while not self.isInterruptionRequested():
                    self.msleep(35)
        except Exception:
            self.level.emit(0.0)

    def stop(self):
        self.requestInterruption()
        self.wait(800)


class AgentWorker(QThread):
    """Execute autonomous agent request off the main GUI thread."""
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, agent: Agent, prompt: str, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._prompt = prompt

    def run(self):
        try:
            self.completed.emit(self._agent.process(self._prompt))
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    """Primary OMEN Desktop Application Window."""

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._continuous_voice_active = False

        self._setup_window()
        self._build_ui()
        self._setup_subcomponents()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowTitle("OMEN — Personal AI Assistant")
        self.setMinimumSize(1100, 680)
        self.resize(1340, 840)
        self.setObjectName("mainWindow")

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        self._central_layout = QHBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)

        # Ambient layered background
        self._holo_bg = HoloBackground(central)
        self._holo_bg.setGeometry(central.rect())
        self._holo_bg.lower()

        # Status Bar
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_DIM};
                border-top: 1px solid rgba(255, 255, 255, 0.05);
                font-size: 11px;
            }}
        """)
        self.statusBar().showMessage("OMEN Ready · Press Ctrl+Space for Command Palette")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        try:
            central = self.centralWidget()
            if central and hasattr(self, '_holo_bg'):
                self._holo_bg.setGeometry(central.rect())
            if hasattr(self, '_voice_overlay') and self._voice_overlay.isVisible():
                self._voice_overlay.setGeometry(central.rect())
        except Exception:
            pass

    def _build_ui(self):
        # 1. Left Sidebar
        self._sidebar = Sidebar(self)
        self._central_layout.addWidget(self._sidebar)
        # UPGRADE-v2: expanded nav — Home/Chat/Agents/Tasks/Memory/Projects/Browser/Screen/Code/Automation/Activity/Models/Plugins/Settings

        # 2. Main Container
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setStyleSheet(f"""
            QFrame#topbar {{
                background-color: {BACKGROUND_DARK};
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding: 6px 20px;
            }}
        """)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(16, 6, 16, 6)
        tb_layout.setSpacing(12)

        # Mini Command Palette Trigger
        self._palette_trigger_btn = QPushButton("🔍  Type a command or ask OMEN...   Ctrl+Space")
        self._palette_trigger_btn.setFixedWidth(360)
        self._palette_trigger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 8px;
                color: #71717A;
                text-align: left;
                padding: 6px 14px;
                font-size: 11.5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.07);
                border-color: rgba(0, 210, 238, 0.3);
                color: #EDEDEF;
            }
        """)
        self._palette_trigger_btn.clicked.connect(self._open_command_palette)
        tb_layout.addWidget(self._palette_trigger_btn)

        tb_layout.addStretch()

        # Mini Widget Button
        mini_btn = QPushButton("◱ Mini Mode")
        mini_btn.setToolTip("Switch to compact floating desktop widget (Ctrl+M)")
        mini_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                color: #A1A1AA;
                padding: 5px 12px;
                font-size: 11.5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                color: #F4F4F6;
            }
        """)
        mini_btn.clicked.connect(self._toggle_mini_mode)
        tb_layout.addWidget(mini_btn)

        # System Status
        self._top_status = QLabel("● ONLINE")
        self._model_display = QLabel("Model: ollama/llama3")
        self._agent_display = QLabel("Agent: ChatAgent")
        self._top_status.setStyleSheet(f"color: {SUCCESS}; font-size: 10px; font-weight: bold;")
        tb_layout.addWidget(self._top_status)

        content_layout.addWidget(topbar)

        # Emergency Stop Banner
        self._emergency_banner = QLabel("🛑 EMERGENCY STOP ACTIVE — Tool execution halted. Press Esc to reset.")
        self._emergency_banner.setHidden(True)
        self._emergency_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(239, 68, 68, 0.90);
                color: white;
                font-weight: bold;
                font-size: 11pt;
                padding: 8px;
                text-align: center;
            }
        """)
        content_layout.addWidget(self._emergency_banner)

        # Stack of Views
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack, stretch=1)
        self._central_layout.addWidget(content_container, stretch=1)

        # Initialize All Views
        self._assistant_view = AssistantView(self._agent)
        self._tasks_view = TasksView(self._agent)
        self._calendar_view = CalendarView()
        self._notes_view = NotesView()
        self._files_view = FilesView()
        self._system_view = SystemView()
        self._settings_view = SettingsView()

        self._views_map = {
            "chat": self._assistant_view,
            "tasks": self._tasks_view,
            "calendar": self._calendar_view,
            "notes": self._notes_view,
            "files": self._files_view,
            "system": self._system_view,
            "settings": self._settings_view,
        }

        for view in self._views_map.values():
            self._stack.addWidget(view)

        self._stack.setCurrentWidget(self._assistant_view)

    def _setup_subcomponents(self):
        # 1. Raycast Command Palette
        self._palette = CommandPalette(self)
        self._palette.action_triggered.connect(self._on_palette_action)

        # 2. Desktop Mini Widget
        self._mini_widget = MiniWidget()
        self._mini_widget.expand_requested.connect(self._restore_from_mini)
        self._mini_widget.mic_clicked.connect(self._capture_voice_single)

        # 3. Dedicated Voice Overlay
        central = self.centralWidget()
        self._voice_overlay = VoiceOverlay(central)
        self._voice_overlay.setGeometry(central.rect())
        self._voice_overlay.hide()
        self._voice_overlay.close_requested.connect(self._close_voice_mode)
        self._voice_overlay.interrupted.connect(self._cancel_voice)

    def _connect_signals(self):
        # Sidebar navigation & actions
        self._sidebar.page_changed.connect(self._switch_page)
        self._sidebar.new_conversation_requested.connect(self._new_conversation)

        # Assistant View
        self._assistant_view.message_sent.connect(self._process_message)
        self._assistant_view.voice_requested.connect(self._capture_voice_single)
        self._assistant_view.voice_mode_requested.connect(self._open_voice_mode)

        # Files View summarize action
        self._files_view.summarize_requested.connect(self._summarize_file_request)

        # Keyboard shortcuts
        sc_palette = QShortcut(QKeySequence("Ctrl+Space"), self)
        sc_palette.activated.connect(self._open_command_palette)

        sc_mini = QShortcut(QKeySequence("Ctrl+M"), self)
        sc_mini.activated.connect(self._toggle_mini_mode)

        sc_new = QShortcut(QKeySequence("Ctrl+N"), self)
        sc_new.activated.connect(self._new_conversation)

        sc_esc = QShortcut(QKeySequence("Ctrl+Shift+Escape"), self)
        sc_esc.activated.connect(self._trigger_emergency)

        # Event Bus
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_agent_state)
            bus.subscribe(EventType.ERROR, self._on_error)
        except Exception:
            pass

    def _switch_page(self, page_id: str):
        if page_id in self._views_map:
            self._stack.setCurrentWidget(self._views_map[page_id])
            self._sidebar.set_active_page(page_id)

    def _new_conversation(self):
        self._switch_page("chat")
        self._assistant_view.reset_to_idle()
        ToastManager.show(self, "New conversation initialized", level="info")

    def _open_command_palette(self):
        # Center palette over main window
        px = self.x() + (self.width() - self._palette.width()) // 2
        py = self.y() + (self.height() - self._palette.height()) // 2
        self._palette.move(px, py)
        self._palette.open_palette()

    def _on_palette_action(self, action_id: str, data: dict):
        if action_id == "ask_prompt":
            query = data.get("query", "")
            self._switch_page("chat")
            self._assistant_view._input_box.set_text(query)
            self._assistant_view._on_user_submit(query, [])
        elif action_id == "new_chat":
            self._new_conversation()
        elif action_id.startswith("nav_"):
            target = action_id.replace("nav_", "")
            self._switch_page(target)
        elif action_id == "voice_mode":
            self._open_voice_mode()
        elif action_id == "mini_mode":
            self._toggle_mini_mode()
        elif action_id == "create_task":
            self._switch_page("tasks")
        elif action_id == "create_note":
            self._switch_page("notes")
            self._notes_view._create_new_note()
        elif action_id == "summarize_files":
            self._switch_page("files")
        elif action_id == "plan_day":
            self._switch_page("chat")
            self._assistant_view._on_quick_action_clicked("Help me plan my day, organize my highest priorities and scheduled tasks.")
        elif action_id == "stop_emergency":
            self._trigger_emergency()

    def _toggle_mini_mode(self):
        self.hide()
        # Position mini widget in bottom-right corner of screen
        geo = QApplication.primaryScreen().availableGeometry()
        self._mini_widget.move(geo.width() - 250, geo.height() - 80)
        self._mini_widget.show()
        ToastManager.show(self._mini_widget, "OMEN Mini Mode Active", level="omen")

    def _restore_from_mini(self):
        self._mini_widget.hide()
        self.show()
        self.raise_()
        self.activateWindow()

    def _open_voice_mode(self):
        central = self.centralWidget()
        self._voice_overlay.setGeometry(central.rect())
        self._voice_overlay.show()
        self._voice_overlay.set_voice_state("listening")
        self._capture_voice_turn()

    def _close_voice_mode(self):
        self._cancel_voice()
        self._voice_overlay.hide()

    def _capture_voice_single(self):
        self._continuous_voice_active = False
        self._capture_voice_turn()

    def _capture_voice_turn(self):
        self._sidebar.set_status("Listening...", "busy")
        self._mini_widget.set_state("listening")
        self.statusBar().showMessage("Listening for speech...")

        # Voice meter
        self._voice_meter = VoiceMeter(self)
        self._voice_meter.level.connect(self._on_voice_level)
        self._voice_meter.start()

        # Voice worker
        self._voice_worker = VoiceWorker(self)
        self._voice_worker.transcript.connect(self._on_voice_transcript)
        self._voice_worker.unavailable.connect(self._on_voice_unavailable)
        self._voice_worker.start()

    def _on_voice_level(self, level: float):
        self._mini_widget.set_voice_level(level)
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_audio_level(level)

    def _cancel_voice(self):
        self._continuous_voice_active = False
        if hasattr(self, "_voice_worker") and self._voice_worker.isRunning():
            self._voice_worker.cancel()
            self._voice_worker.requestInterruption()
        self._stop_voice_meter()
        self._sidebar.set_status("OMEN v1.0 · Ready", "ready")
        self._mini_widget.set_state("idle")
        self.statusBar().showMessage("OMEN Ready")

    def _on_voice_transcript(self, transcript: str):
        self._stop_voice_meter()
        self.statusBar().showMessage("Processing utterance...")
        self._mini_widget.set_state("thinking")
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("thinking", transcript)

        self._switch_page("chat")
        self._assistant_view._on_user_submit(transcript, [])

    def _on_voice_unavailable(self, reason: str):
        self._stop_voice_meter()
        self._sidebar.set_status("OMEN v1.0 · Ready", "ready")
        self._mini_widget.set_state("idle")
        self.statusBar().showMessage(f"Voice input ended: {reason}")
        if self._voice_overlay.isVisible():
            self._voice_overlay.update_transcript(f"Voice ended: {reason}")

    def _stop_voice_meter(self):
        if hasattr(self, "_voice_meter") and self._voice_meter.isRunning():
            self._voice_meter.stop()

    def _summarize_file_request(self, file_path: str):
        self._switch_page("chat")
        prompt = f"Please examine and summarize this workspace file:\n{file_path}"
        self._assistant_view._input_box.set_text(prompt)
        self._assistant_view._on_user_submit(prompt, [{"path": file_path, "type": "file"}])

    def _process_message(self, prompt: str):
        self._sidebar.set_status("OMEN thinking...", "busy")
        self._mini_widget.set_state("thinking")
        self.statusBar().showMessage("OMEN is thinking...")

        self._agent_worker = AgentWorker(self._agent, prompt, self)
        self._agent_worker.completed.connect(self._on_agent_completed)
        self._agent_worker.failed.connect(self._on_agent_failed)
        self._agent_worker.start()

    def _on_agent_completed(self, result):
        self._sidebar.set_status("OMEN v1.0 · Ready", "ready")
        self._mini_widget.set_state("idle")
        self.statusBar().showMessage("OMEN Ready")

        response = result.get("response_text") or "Action completed."
        plan = result.get("plan")
        tools_executed = []
        if plan and plan.steps:
            for s in plan.steps:
                tools_executed.append({"tool": s.tool, "status": s.status.value})

        self._assistant_view.add_omen_response(response, tools=tools_executed)

        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("speaking", response)

        # Voice audio if enabled
        if self._agent.tts and self._agent.tts.is_available:
            self._agent.tts.speak_async(response)

        ToastManager.show(self, "OMEN completed the action", level="success")

    def _on_agent_failed(self, error: str):
        self._sidebar.set_status("Error", "error")
        self._mini_widget.set_state("error")
        self.statusBar().showMessage(f"Error: {error}")
        self._assistant_view.add_omen_response(f"An error occurred while executing the request:\n{error}")
        ToastManager.show(self, "Execution failed", level="error")

    def _trigger_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.trigger()
        self._emergency_banner.setHidden(False)
        self._assistant_view.add_omen_response("🛑 EMERGENCY PROTOCOL ACTIVATED. All background tool operations halted.")
        ToastManager.show(self, "Emergency stop engaged", level="error")

    def reset_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.reset()
        self._emergency_banner.setHidden(True)
        ToastManager.show(self, "Emergency reset", level="success")

    def _on_agent_state(self, event):
        state = event.payload.get("state", "")
        if state == "ERROR":
            self.statusBar().showMessage("Agent encountered an error.", 4000)

    def _on_error(self, event):
        err = event.payload.get("error", "An error occurred.")
        self.statusBar().showMessage(f"Notice: {err}", 4000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self._emergency_banner.isVisible():
                self.reset_emergency()
            elif self._voice_overlay.isVisible():
                self._close_voice_mode()
        super().keyPressEvent(event)