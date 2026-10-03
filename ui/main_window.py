# ============================================
"""
Main Application Window for OMEN — premium editorial layout.
Dark charcoal + steel blue, restrained glassmorphism, clean hierarchy.
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QStatusBar, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve, QPointF, QRect, QRectF
from PySide6.QtGui import QFont, QKeySequence, QPainter, QPen, QColor, QLinearGradient, QRadialGradient, QBrush
from PySide6.QtGui import QKeySequence, QShortcut
from core.events import get_event_bus, EventType
from core.agent import Agent
from ui.sidebar import Sidebar, CollapsedSidebar
from ui.dashboard import DashboardView
from ui.chat import ChatView
from ui.views.tasks_view import TasksView
from ui.views.reminders_view import RemindersView
from ui.views.vision_view import VisionView
from ui.views.activity_view import ActivityView
from ui.views.settings_view import SettingsView
from voice.stt import OmenSTT
from voice.tts import OmenTTS
from ui.styles.palette import (
    PRIMARY, SECONDARY, SECONDARY_LIGHT, SUCCESS, ERROR, BACKGROUND_DARK,
    PRIMARY_GLOW, SECONDARY_GLOW, TERTIARY, TEXT_DIM, BORDER,
    BOX_SHADOW, FLOATING_SHADOW,
)


class HoloBackground(QWidget):
    """Subtle deep dark background — minimal animated depth.
    Restrained version: no scan lines, no particles, just depth gradient."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(60)  # Slower, more subtle ~16 FPS

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Deep warm dark gradient
        bg_grad = QRadialGradient(w / 2, h / 2, max(w, h) * 0.7)
        bg_grad.setColorAt(0.0, QColor("#0D0D10"))
        bg_grad.setColorAt(0.5, QColor("#09090B"))
        bg_grad.setColorAt(1.0, QColor("#050506"))
        painter.fillRect(self.rect(), QBrush(bg_grad))

        # Very subtle ambient glow — center only, no animation on it
        ambient = QRadialGradient(w / 2, h * 0.45, w * 0.25)
        ambient.setColorAt(0.0, QColor(59, 130, 246, 8))
        ambient.setColorAt(0.5, QColor(59, 130, 246, 3))
        ambient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(ambient))
        painter.drawEllipse(QRectF(w * 0.1, h * 0.15, w * 0.8, h * 0.7))

        painter.end()


class VoiceWorker(QThread):
    """Capture one microphone utterance without blocking the Qt event loop."""
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
    """Read a low-cost microphone level stream for the Command Core animation."""
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
    """Run an agent request away from the GUI thread."""
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
    """
    Primary OMEN Desktop Command Deck — premium editorial dark UI.
    """

    def __init__(self, agent: Agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._continuous_voice_active = False
        self._sidebar_collapsed = False
        self._setup_window()
        self._build_ui()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowTitle("OMEN — Personal AI Assistant")
        self.setMinimumSize(1100, 660)
        self.resize(1360, 820)
        self.setObjectName("mainWindow")

        # Central widget with dark background
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        self._central_layout = QHBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)

        # Background lives behind everything
        self._holo_bg = HoloBackground(central)
        self._holo_bg.setGeometry(central.rect())
        self._holo_bg.lower()

        # Emergency stop banner
        self._emergency_banner = QLabel("🛑 EMERGENCY STOP ACTIVE — Press CTRL+SHIFT+ESC or CTRL+ALT+Q to reset")
        self._emergency_banner.setHidden(True)
        self._emergency_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(239, 68, 68, 0.95);
                color: white;
                font-weight: 900;
                font-size: 11pt;
                padding: 8px;
                letter-spacing: 2px;
                text-align: center;
            }
        """)
        self._central_layout.addWidget(self._emergency_banner)

        # Status bar — minimal
        self.statusBar().setStyleSheet(f"background-color: {BACKGROUND_DARK}; color: {TEXT_DIM}; border-top: 1px solid #1E1E24;")
        self.statusBar().showMessage("OMEN Ready")

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        try:
            central = self.centralWidget()
            if central and hasattr(self, '_holo_bg'):
                self._holo_bg.setGeometry(central.rect())
        except Exception:
            pass

    def _build_ui(self):
        # Sidebar with collapse/expand toggle
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._switch_page)
        self._central_layout.addWidget(self._sidebar)

        # Main Content Stack
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Header Bar — clean dark, minimal
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setStyleSheet(f"""
            QFrame#topbar {{
                background: {BACKGROUND_DARK};
                border-bottom: 1px solid {BORDER};
                padding: 8px 20px;
            }}
        """)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(16, 6, 16, 6)
        topbar_layout.setSpacing(14)

        # Brand
        deck_label = QLabel("◉ OMEN")
        deck_label.setFont(QFont("Inter, Segoe UI", 16, QFont.Weight.Bold))
        deck_label.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 2px;")
        topbar_layout.addWidget(deck_label)

        # Mode label
        mode_label = QLabel("PERSONAL AI ASSISTANT  ·  LOCAL HARDWARE BOUND")
        mode_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt; letter-spacing: 1.5px;")
        topbar_layout.addWidget(mode_label)
        topbar_layout.addStretch()

        # Status indicator
        self._top_status = QLabel("● SYSTEM READY")
        self._top_status.setStyleSheet(f"color: {SUCCESS}; font-size: 8.5pt; font-weight: 600;")
        topbar_layout.addWidget(self._top_status)
        content_layout.addWidget(topbar)

        # Emergency banner
        self._emergency_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(239, 68, 68, 0.85);
                color: white;
                font-weight: 900;
                font-size: 11pt;
                padding: 8px;
                letter-spacing: 2px;
                text-align: center;
                border: 1px solid rgba(255, 0, 85, 0.5);
                border-radius: 6px;
            }
        """)
        content_layout.addWidget(self._emergency_banner)

        # Stack of all views
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack)
        self._central_layout.addWidget(content_container)

        # Initialize all views
        self._dashboard = DashboardView(self._agent)
        self._chat = ChatView(self._agent)
        self._tasks_view = TasksView(self._agent)
        self._reminders_view = RemindersView()
        self._vision_view = VisionView(self._agent)
        self._activity_view = ActivityView()
        self._settings_view = SettingsView()

        self._views_map = {
            "dashboard": self._dashboard,
            "chat": self._chat,
            "tasks": self._tasks_view,
            "reminders": self._reminders_view,
            "vision": self._vision_view,
            "activity": self._activity_view,
            "settings": self._settings_view,
        }

        for view in self._views_map.values():
            self._stack.addWidget(view)

        self._stack.setCurrentWidget(self._dashboard)

    def _connect_signals(self):
        self._sidebar.page_changed.connect(self._switch_page)
        self._chat.message_sent.connect(self._process_chat_message)
        self._chat.voice_requested.connect(self._capture_voice_single)
        self._chat.voice_cancelled.connect(self._cancel_voice)
        self._dashboard.voice_requested.connect(self._capture_voice_single)
        self._dashboard.continuous_voice_requested.connect(self._toggle_continuous_voice)
        self._dashboard.chat_requested.connect(lambda: self._switch_page("chat"))
        self._dashboard.vision_requested.connect(lambda: self._switch_page("vision"))
        self._dashboard.tasks_requested.connect(lambda: self._switch_page("tasks"))
        self._dashboard.briefing_requested.connect(self._trigger_daily_briefing)

        # Global emergency shortcuts
        esc_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Escape"), self)
        esc_shortcut.activated.connect(self._trigger_emergency)
        alt_q_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Q"), self)
        alt_q_shortcut.activated.connect(self._trigger_emergency)

        # Event bus
        try:
            bus = get_event_bus()
            bus.subscribe(EventType.AGENT_STATE_CHANGE, self._on_agent_state)
            bus.subscribe(EventType.ERROR, self._on_error)
        except Exception:
            pass

    def _switch_page(self, page_id: str):
        if page_id in self._views_map:
            target_widget = self._views_map[page_id]
            self._stack.setCurrentWidget(target_widget)
            self._sidebar.set_active_page(page_id)

    def _process_chat_message(self, prompt: str):
        self._chat._send_button.setEnabled(False)
        self._dashboard.set_voice_mode("thinking")
        self._agent_worker = AgentWorker(self._agent, prompt, self)
        self._agent_worker.completed.connect(self._on_agent_completed)
        self._agent_worker.failed.connect(self._on_agent_failed)
        self._agent_worker.finished.connect(lambda: self._chat._send_button.setEnabled(True))
        self._agent_worker.start()

    def _toggle_continuous_voice(self):
        if self._continuous_voice_active:
            self._continuous_voice_active = False
            self._cancel_voice()
            self.statusBar().showMessage("2-Way Voice Dialogue Deactivated")
        else:
            self._continuous_voice_active = True
            self.statusBar().showMessage("🎙 2-Way Conversational Voice Mode Active (Speak naturally)")
            self._capture_voice_turn()

    def _capture_voice_single(self):
        self._continuous_voice_active = False
        self._capture_voice_turn()

    def _capture_voice_turn(self):
        self._chat.show_voice_overlay()
        self._dashboard.set_voice_mode("listening")
        self._chat.set_voice_state("Listening")
        self._voice_meter = VoiceMeter(self)
        self._voice_meter.level.connect(self._dashboard._core.set_voice_level)
        self._voice_meter.start()
        self._voice_worker = VoiceWorker(self)
        self._voice_worker.transcript.connect(self._on_voice_transcript)
        self._voice_worker.unavailable.connect(self._on_voice_unavailable)
        self._voice_worker.start()

    def _cancel_voice(self):
        self._continuous_voice_active = False
        if hasattr(self, "_voice_worker") and self._voice_worker.isRunning():
            self._voice_worker.cancel()
            self._voice_worker.requestInterruption()
        self._stop_voice_meter()
        self._dashboard.set_voice_mode("idle")
        self._chat.hide_voice_overlay()
        if hasattr(self._dashboard, '_core'):
            self._dashboard._core.set_voice_level(0.0)

    def _on_voice_transcript(self, transcript: str):
        self._stop_voice_meter()
        self._dashboard.set_voice_mode("thinking")
        self._chat.set_voice_state("Thinking")
        self._chat.hide_voice_overlay()
        self._chat.add_user_message(transcript)
        self._agent_worker = AgentWorker(self._agent, transcript, self)
        self._agent_worker.completed.connect(self._on_agent_completed)
        self._agent_worker.failed.connect(self._on_agent_failed)
        self._agent_worker.start()

    def _on_voice_unavailable(self, reason: str):
        self._stop_voice_meter()
        self._dashboard.set_voice_mode("idle")
        self._chat.hide_voice_overlay()
        self.statusBar().showMessage(f"Voice input ended: {reason}")
        if self._continuous_voice_active:
            QTimer.singleShot(1500, self._capture_voice_turn)

    def _on_agent_completed(self, result):
        response = result.get("response_text") or "Command executed successfully."
        plan = result.get("plan")
        steps = plan.steps if plan else None
        self._chat.add_assistant_message(response, plan_steps=steps)
        self._dashboard.set_voice_mode("speaking")
        if self._agent.tts and self._agent.tts.is_available:
            self._agent.tts.speak(response)
        words = len(response.split())
        est_duration_ms = max(2000, int((words / 2.8) * 1000) + 800)
        QTimer.singleShot(est_duration_ms, self._on_speech_finished)

    def _on_speech_finished(self):
        self._dashboard.set_voice_mode("idle")
        if self._continuous_voice_active:
            QTimer.singleShot(1500, self._capture_voice_turn)

    def _stop_voice_meter(self):
        if hasattr(self, "_voice_meter") and self._voice_meter.isRunning():
            self._voice_meter.stop()

    def _on_agent_failed(self, error: str):
        self._chat.add_assistant_message(f"Execution error: {error}")
        self._dashboard.set_voice_mode("error")
        QTimer.singleShot(3000, lambda: self._dashboard.set_voice_mode("idle"))

    def _trigger_daily_briefing(self):
        res = self._agent.executor.registry.execute_tool("get_morning_briefing", {})
        if res.success:
            self._chat.add_assistant_message(res.message)
            self._switch_page("chat")
            if self._agent.tts and self._agent.tts.is_available:
                self._agent.tts.speak(res.message)

    def _trigger_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.trigger()
        self._emergency_banner.setHidden(False)
        self._chat.add_assistant_message("🛑 EMERGENCY PROTOCOL ACTIVATED. All background jobs and tool actions halted.")

    def reset_emergency(self):
        from safety.emergency_stop import get_emergency_stop
        stop = get_emergency_stop()
        stop.reset()
        self._emergency_banner.setHidden(True)

    def _on_agent_state(self, event):
        state = event.payload.get("state", "")
        if state == "ERROR":
            self.statusBar().showMessage("Agent encountered an error.", 5000)

    def _on_error(self, event):
        err = event.payload.get("error", "An error occurred.")
        self.statusBar().showMessage(f"System notice: {err}", 5000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._emergency_banner.isVisible():
            self.reset_emergency()
        super().keyPressEvent(event)