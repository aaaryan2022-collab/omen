# ============================================
"""
Main Application Window for OMEN — Minimal, Beautiful, Focused.
Aesthetic: Linear / Arc / Raycast — Deep dark, subtle cyan, generous whitespace.
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
from ui.views.home_view import HomeView
from ui.views.coding_view import CodingView
from ui.views.research_view import ResearchView
from ui.views.vision_view import VisionView
from ui.views.skills_mcp_view import SkillsMcpView
from ui.views.activity_view import ActivityView
from ui.views.agent_center_view import AgentCenterView
from ui.views.command_center_view import CommandCenterView
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
    """Clean deep dark background — single radial gradient, zero noise."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bg_grad = QRadialGradient(w / 2.0, h / 2.0, max(w, h) * 0.7)
        bg_grad.setColorAt(0.0, QColor("#0B0B0F"))
        bg_grad.setColorAt(0.5, QColor("#09090C"))
        bg_grad.setColorAt(1.0, QColor("#060608"))
        painter.fillRect(self.rect(), QBrush(bg_grad))

        # Single subtle ambient glow
        ambient = QRadialGradient(w / 2.0, 0, w * 0.5)
        ambient.setColorAt(0.0, QColor(0, 210, 238, 8))
        ambient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(ambient))
        painter.drawEllipse(QRectF(w * 0.15, -h * 0.15, w * 0.7, h * 0.45))
        painter.end()


class VoiceWorker(QThread):
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
                samplerate=16000, blocksize=512, channels=1, dtype="int16", callback=on_audio,
            ):
                while not self.isInterruptionRequested():
                    self.msleep(35)
        except Exception:
            self.level.emit(0.0)

    def stop(self):
        self.requestInterruption()
        self.wait(800)


class AgentWorker(QThread):
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
    """Primary OMEN Desktop Application Window — Minimal & Focused."""

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._continuous_voice_active = False
        self._setup_window()
        self._build_ui()
        self._setup_subcomponents()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowTitle("OMEN")
        self.setMinimumSize(1000, 640)
        self.resize(1280, 800)
        self.setObjectName("mainWindow")

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        self._central_layout = QHBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)

        # Background
        self._holo_bg = HoloBackground(central)
        self._holo_bg.setGeometry(central.rect())
        self._holo_bg.lower()

        # Status Bar — minimal
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: transparent;
                color: {TEXT_DIM};
                border: none;
                font-size: 11px;
                padding: 0 16px;
            }}
        """)
        self.statusBar().showMessage("Ready  •  Ctrl+K for Command Palette")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        central = self.centralWidget()
        if central and hasattr(self, '_holo_bg'):
            self._holo_bg.setGeometry(central.rect())
        if hasattr(self, '_voice_overlay') and self._voice_overlay.isVisible():
            self._voice_overlay.setGeometry(central.rect())

    def _build_ui(self):
        # 1. Sidebar — Clean & Minimal
        self._sidebar = Sidebar(self)
        self._central_layout.addWidget(self._sidebar)

        # 2. Main Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar — Search + Essentials only
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setStyleSheet(f"""
            QFrame#topbar {{
                background-color: rgba(9, 9, 12, 0.85);
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }}
        """)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(16, 8, 16, 8)
        tb_layout.setSpacing(12)

        # Search Trigger (Ctrl+K)
        self._palette_trigger_btn = QPushButton("🔍  Search…   Ctrl+K")
        self._palette_trigger_btn.setFixedWidth(320)
        self._palette_trigger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                color: #71717A;
                text-align: left;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                border-color: rgba(0, 210, 238, 0.25);
                color: #EDEDEF;
            }
        """)
        self._palette_trigger_btn.clicked.connect(self._open_command_palette)
        tb_layout.addWidget(self._palette_trigger_btn)

        tb_layout.addStretch()

        # Model indicator (clickable -> settings)
        self._model_btn = QPushButton("🤖  Local Model")
        self._model_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                color: #A1A1AA;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                color: white;
            }
        """)
        self._model_btn.clicked.connect(lambda: self._switch_page("settings"))
        tb_layout.addWidget(self._model_btn)

        # Mini Mode
        mini_btn = QPushButton("◱")
        mini_btn.setToolTip("Mini Mode (Ctrl+M)")
        mini_btn.setFixedSize(32, 32)
        mini_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                color: #A1A1AA;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #F4F4F6;
            }
        """)
        mini_btn.clicked.connect(self._toggle_mini_mode)
        tb_layout.addWidget(mini_btn)

        content_layout.addWidget(topbar)

        # Emergency Banner
        self._emergency_banner = QLabel("🛑 EMERGENCY STOP ACTIVE — Press Esc to reset")
        self._emergency_banner.setHidden(True)
        self._emergency_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(239, 68, 68, 0.9);
                color: white;
                font-weight: 600;
                font-size: 12px;
                padding: 10px;
                text-align: center;
            }
        """)
        content_layout.addWidget(self._emergency_banner)

        # View Stack
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack, stretch=1)
        self._central_layout.addWidget(content_container, stretch=1)

        # Initialize Views — Complete 15 Modular View Suite
        self._home_view = HomeView()
        self._assistant_view = AssistantView(self._agent)
        self._tasks_view = TasksView(self._agent)
        self._calendar_view = CalendarView()
        self._notes_view = NotesView()
        self._files_view = FilesView()
        self._system_view = SystemView()
        self._settings_view = SettingsView()
        self._coding_view = CodingView()
        self._research_view = ResearchView()
        self._vision_view = VisionView()
        self._skills_view = SkillsMcpView()
        self._activity_view = ActivityView()
        self._agent_center_view = AgentCenterView()
        self._command_center_view = CommandCenterView()

        self._views_map = {
            "home":     self._home_view,
            "chat":     self._assistant_view,
            "tasks":    self._tasks_view,
            "calendar": self._calendar_view,
            "notes":    self._notes_view,
            "files":    self._files_view,
            "system":   self._system_view,
            "settings": self._settings_view,
            "coding":   self._coding_view,
            "research": self._research_view,
            "vision":   self._vision_view,
            "skills":   self._skills_view,
            "activity": self._activity_view,
            "agents":   self._agent_center_view,
            "command":  self._command_center_view,
        }

        for view in self._views_map.values():
            self._stack.addWidget(view)

        self._stack.setCurrentWidget(self._home_view)

    def _setup_subcomponents(self):
        # Command Palette
        self._palette = CommandPalette(self)
        self._palette.action_triggered.connect(self._on_palette_action)

        # Mini Widget
        self._mini_widget = MiniWidget()
        self._mini_widget.expand_requested.connect(self._restore_from_mini)
        self._mini_widget.mic_clicked.connect(self._capture_voice_single)

        # Voice Overlay
        central = self.centralWidget()
        self._voice_overlay = VoiceOverlay(central)
        self._voice_overlay.setGeometry(central.rect())
        self._voice_overlay.hide()
        self._voice_overlay.close_requested.connect(self._close_voice_mode)
        self._voice_overlay.interrupted.connect(self._cancel_voice)

    def _connect_signals(self):
        self._sidebar.page_changed.connect(self._switch_page)
        self._sidebar.new_conversation_requested.connect(self._new_conversation)

        self._home_view.nav_requested.connect(self._switch_page)
        self._home_view.submit_prompt.connect(self._on_home_prompt_submitted)
        self._home_view.voice_toggle_requested.connect(self._toggle_continuous_voice)

        self._assistant_view.message_sent.connect(self._process_message)
        self._assistant_view.voice_requested.connect(self._capture_voice_single)
        self._assistant_view.voice_mode_requested.connect(self._open_voice_mode)

        self._files_view.summarize_requested.connect(self._summarize_file_request)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+Space"), self).activated.connect(self._open_command_palette)
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self._open_command_palette)
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(self._toggle_mini_mode)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._new_conversation)
        QShortcut(QKeySequence("Ctrl+Shift+Escape"), self).activated.connect(self._trigger_emergency)

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
        ToastManager.show(self, "New conversation", level="info")

    def _open_command_palette(self):
        px = self.x() + (self.width() - self._palette.width()) // 2
        py = self.y() + (self.height() - self._palette.height()) // 2
        self._palette.move(px, py)
        self._palette.open_palette()

    def _on_palette_action(self, action_id: str, data: dict):
        if action_id == "ask_prompt":
            self._switch_page("chat")
            self._assistant_view._input_box.set_text(data.get("query", ""))
            self._assistant_view._on_user_submit(data.get("query", ""), [])
        elif action_id == "new_chat":
            self._new_conversation()
        elif action_id.startswith("nav_"):
            self._switch_page(action_id.replace("nav_", ""))
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
        geo = QApplication.primaryScreen().availableGeometry()
        self._mini_widget.move(geo.width() - 250, geo.height() - 80)
        self._mini_widget.show()
        ToastManager.show(self._mini_widget, "Mini Mode Active", level="omen")

    def _restore_from_mini(self):
        self._mini_widget.hide()
        self.show()
        self.raise_()
        self.activateWindow()

    def _toggle_continuous_voice(self):
        if self._continuous_voice_active:
            self._cancel_voice()
            ToastManager.show(self, "Voice mode ended", level="info")
        else:
            self._continuous_voice_active = True
            ToastManager.show(self, "Voice mode active — speak freely", level="success")
            self._capture_voice_turn()

    def _open_voice_mode(self):
        self._toggle_continuous_voice()

    def _close_voice_mode(self):
        self._cancel_voice()
        self._voice_overlay.hide()

    def _capture_voice_single(self):
        # Enable continuous conversation by default so speech flows naturally like talking to a person
        self._continuous_voice_active = True
        self._capture_voice_turn()

    def _capture_voice_turn(self):
        self._sidebar.set_status("Listening...", "busy")
        self._mini_widget.set_state("listening")
        self._home_view.set_voice_state("listening")
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("listening")
        self.statusBar().showMessage("Listening...")

        self._voice_meter = VoiceMeter(self)
        self._voice_meter.level.connect(self._on_voice_level)
        self._voice_meter.start()

        self._voice_worker = VoiceWorker(self)
        self._voice_worker.transcript.connect(self._on_voice_transcript)
        self._voice_worker.unavailable.connect(self._on_voice_unavailable)
        self._voice_worker.start()

    def _on_voice_level(self, level: float):
        self._mini_widget.set_voice_level(level)
        self._home_view.set_voice_state("listening", level)
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_audio_level(level)

    def _cancel_voice(self):
        self._continuous_voice_active = False
        if hasattr(self, "_voice_worker") and self._voice_worker.isRunning():
            self._voice_worker.cancel()
            self._voice_worker.requestInterruption()
        self._stop_voice_meter()
        self._sidebar.set_status("Ready", "ready")
        self._mini_widget.set_state("idle")
        self._home_view.set_voice_state("idle")
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("idle")
        self.statusBar().showMessage("Ready")

    def _on_voice_transcript(self, transcript: str):
        self._stop_voice_meter()
        self.statusBar().showMessage(f"Heard: {transcript}")
        self._mini_widget.set_state("thinking")
        self._home_view.set_voice_state("thinking")
        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("thinking", transcript)

        lower = transcript.strip().lower()
        dismissal_phrases = (
            "exit voice", "quit voice", "stop listening", "goodbye", "bye omen",
            "cancel voice", "that's all", "thank you omen", "go to sleep",
            "sleep now", "dismissed", "stop conversation",
        )
        if any(term in lower for term in dismissal_phrases):
            self._cancel_voice()
            if self._agent.tts and self._agent.tts.is_available:
                self._agent.tts.speak("Goodbye, sir.")
            ToastManager.show(self, "Voice conversation ended", level="info")
            return

        self._switch_page("chat")
        self._assistant_view._on_user_submit(transcript, [])

    def _on_voice_unavailable(self, reason: str):
        self._stop_voice_meter()
        self._sidebar.set_status("Ready", "ready")
        self.statusBar().showMessage(f"Voice: {reason}")
        if self._voice_overlay.isVisible():
            self._voice_overlay.update_transcript(f"Voice: {reason}")

        if self._continuous_voice_active:
            self._home_view.set_voice_state("idle")
            # Automatically resume listening after pause so the conversation stays alive
            QTimer.singleShot(750, self._capture_voice_turn)
        else:
            self._mini_widget.set_state("idle")
            self._home_view.set_voice_state("idle")

    def _resume_continuous_voice(self):
        if self._continuous_voice_active:
            if self._voice_overlay.isVisible():
                self._voice_overlay.set_voice_state("listening", "Listening for your reply...")
            QTimer.singleShot(400, self._capture_voice_turn)
        else:
            self._home_view.set_voice_state("idle")
            if self._voice_overlay.isVisible():
                self._voice_overlay.set_voice_state("idle")

    def _stop_voice_meter(self):
        if hasattr(self, "_voice_meter") and self._voice_meter.isRunning():
            self._voice_meter.stop()

    def _summarize_file_request(self, file_path: str):
        self._switch_page("chat")
        prompt = f"Please examine and summarize this file:\n{file_path}"
        self._assistant_view._input_box.set_text(prompt)
        self._assistant_view._on_user_submit(prompt, [{"path": file_path, "type": "file"}])

    def _process_message(self, prompt: str):
        self._sidebar.set_status("Thinking...", "busy")
        self._mini_widget.set_state("thinking")
        self._home_view.set_voice_state("thinking")
        self.statusBar().showMessage("Thinking...")

        self._agent_worker = AgentWorker(self._agent, prompt, self)
        self._agent_worker.completed.connect(self._on_agent_completed)
        self._agent_worker.failed.connect(self._on_agent_failed)
        self._agent_worker.start()

    def _on_agent_completed(self, result):
        self._sidebar.set_status("Ready", "ready")
        self._mini_widget.set_state("idle")
        self.statusBar().showMessage("Ready")

        response = result.get("response_text") or "Done."
        plan = result.get("plan")
        tools_executed = []
        if plan and plan.steps:
            for s in plan.steps:
                tools_executed.append({"tool": s.tool, "status": s.status.value})

        self._assistant_view.add_omen_response(response, tools=tools_executed)

        if self._voice_overlay.isVisible():
            self._voice_overlay.set_voice_state("speaking", response)

        # In continuous voice conversation, speak the reply then seamlessly re-arm mic for user's next words
        if self._continuous_voice_active:
            self._home_view.set_voice_state("speaking")
            if self._agent.tts and self._agent.tts.is_available:
                self._agent.tts.speak(response, on_done=self._resume_continuous_voice)
            else:
                # If TTS not available or finished, resume listening seamlessly
                QTimer.singleShot(1000, self._resume_continuous_voice)
        elif self._agent.tts and self._agent.tts.is_available:
            self._agent.tts.speak(response)

        ToastManager.show(self, "Completed", level="success")

    def _on_home_prompt_submitted(self, prompt: str, attachments: list):
        self._switch_page("chat")
        self._assistant_view._on_user_submit(prompt, attachments)

    def _on_agent_failed(self, error: str):
        self._sidebar.set_status("Error", "error")
        self._mini_widget.set_state("error")
        self.statusBar().showMessage(f"Error: {error}")
        self._assistant_view.add_omen_response(f"Error:\n{error}")
        ToastManager.show(self, "Execution failed", level="error")

    def _trigger_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.trigger()
        self._emergency_banner.setHidden(False)
        self._assistant_view.add_omen_response("🛑 EMERGENCY STOP ACTIVATED")
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
            self.statusBar().showMessage("Agent error", 4000)

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