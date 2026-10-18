# ============================================
"""
OMEN Agent Center — Multi-Agent Hub.

Shows all registered OMEN agents with:
- Live capability summary
- Routing logic explanation
- Model provider assignment
- Last invocation stats
- Manual agent trigger buttons
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR, INFO,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BACKGROUND_DARK, FONT_FAMILY,
)


def _agent_card_style(accent):
    return (
        f"QFrame {{"
        f"  background-color: rgba(21,21,28,0.85);"
        f"  border: 1px solid rgba(255,255,255,0.07);"
        f"  border-radius: 14px;"
        f"}}"
        f"QLabel {{ background: transparent; border: none; padding: 0; margin: 0; }}"
    )


def _agent_card_hover(accent):
    return (
        f"QFrame {{"
        f"  background-color: rgba(25,25,36,0.97);"
        f"  border: 1px solid {accent};"
        f"  border-radius: 14px;"
        f"}}"
        f"QLabel {{ background: transparent; border: none; padding: 0; margin: 0; }}"
    )


class AgentCard(QFrame):
    """Full agent profile card."""

    trigger_requested = Signal(str)

    def __init__(self, agent_id: str, name: str, icon: str, role: str,
                 capabilities: list, model: str, status: str = "ready",
                 accent: str = PRIMARY, parent=None):
        super().__init__(parent)
        self._agent_id = agent_id
        self._accent = accent
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(200)

        self._base = _agent_card_style(accent)
        self._hover = _agent_card_hover(accent)
        self.setStyleSheet(self._base)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 26px;")
        header.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        info_col.addWidget(name_lbl)
        role_lbl = QLabel(role)
        role_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11.5px;")
        info_col.addWidget(role_lbl)
        header.addLayout(info_col)
        header.addStretch()

        # Status badge
        status_color = SUCCESS if status == "ready" else (WARNING if status == "busy" else ERROR)
        status_frame = QFrame()
        status_frame.setStyleSheet(
            f"QFrame {{ background: {status_color}22; border: 1px solid {status_color}66;"
            f" border-radius: 8px; padding: 2px 8px; }}"
            f"QLabel {{ background: transparent; border: none; }}"
        )
        sf_lay = QHBoxLayout(status_frame)
        sf_lay.setContentsMargins(8, 4, 8, 4)
        sf_lay.setSpacing(5)
        s_dot = QLabel("●")
        s_dot.setStyleSheet(f"color: {status_color}; font-size: 8px;")
        sf_lay.addWidget(s_dot)
        s_lbl = QLabel(status.upper())
        s_lbl.setStyleSheet(f"color: {status_color}; font-size: 10px; font-weight: bold;")
        sf_lay.addWidget(s_lbl)
        header.addWidget(status_frame)
        root.addLayout(header)

        # Accent divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background-color: {accent}44;")
        root.addWidget(div)

        # Capabilities
        caps_text = "  ·  ".join(capabilities)
        caps_lbl = QLabel(caps_text)
        caps_lbl.setWordWrap(True)
        caps_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11.5px; line-height: 160%;")
        root.addWidget(caps_lbl)

        # Model label
        model_row = QHBoxLayout()
        model_icon = QLabel("🤖")
        model_icon.setStyleSheet("font-size: 12px;")
        model_row.addWidget(model_icon)
        model_lbl = QLabel(f"Model: {model}")
        model_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        model_row.addWidget(model_lbl)
        model_row.addStretch()

        trigger_btn = QPushButton("Invoke →")
        trigger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        trigger_btn.setStyleSheet(
            f"QPushButton {{ background: {accent}18; border: 1px solid {accent}55;"
            f" border-radius: 7px; color: {accent}; padding: 5px 14px; font-size: 11px;"
            f" font-weight: 600; }}"
            f"QPushButton:hover {{ background: {accent}30; }}"
        )
        trigger_btn.clicked.connect(lambda: self.trigger_requested.emit(self._agent_id))
        model_row.addWidget(trigger_btn)
        root.addLayout(model_row)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._base)
        super().leaveEvent(event)


class AgentCenterView(QWidget):
    """OMEN Agent Hub — multi-agent orchestration control panel."""

    agent_triggered = Signal(str)

    AGENTS = [
        dict(
            agent_id="chat",
            name="ChatAgent",
            icon="💬",
            role="Conversational AI / general-purpose assistant",
            capabilities=[
                "Multi-turn dialogue", "Tool orchestration", "Context window mgmt",
                "Personality / persona", "Model routing",
            ],
            model="Gemini / OpenAI / Ollama (complexity-routed)",
            status="ready",
            accent=PRIMARY,
        ),
        dict(
            agent_id="code",
            name="CodeAgent",
            icon="💻",
            role="Autonomous code generation, debugging, and refactoring",
            capabilities=[
                "AST codebase indexing", "Unified diff patching", "Git operations",
                "Checkpoint / rollback", "Terminal PTY execution",
            ],
            model="Gemini 2.5 Pro / Claude (code-specialized)",
            status="ready",
            accent="#60A5FA",
        ),
        dict(
            agent_id="research",
            name="ResearchAgent",
            icon="🔎",
            role="Deep multi-hop web research with citation synthesis",
            capabilities=[
                "Multi-hop web search", "Evidence extraction", "Claim verification",
                "Citation formatting", "Structured report generation",
            ],
            model="Gemini Flash / Perplexity-compatible",
            status="ready",
            accent="#FBBF24",
        ),
        dict(
            agent_id="vision",
            name="VisionAgent",
            icon="👁️",
            role="Screenshot capture, image analysis, and UI understanding",
            capabilities=[
                "Full-screen / region capture", "Image understanding (LLM)",
                "UI element detection", "OCR text extraction", "Pixel-level analysis",
            ],
            model="Gemini Vision / GPT-4o",
            status="ready",
            accent="#34D399",
        ),
        dict(
            agent_id="browser",
            name="BrowserAgent",
            icon="🌐",
            role="Automated web browsing, form interaction, and content extraction",
            capabilities=[
                "Playwright browser control", "Navigation / click / type",
                "Form fill and submit", "Content scraping", "Screenshot-guided interaction",
            ],
            model="Gemini / Claude (tool-driven)",
            status="ready",
            accent=SECONDARY,
        ),
        dict(
            agent_id="scheduler",
            name="SchedulerAgent",
            icon="⚙️",
            role="Background task execution and routine automation",
            capabilities=[
                "Cron / interval scheduling", "Routine playback", "Event-triggered execution",
                "Action audit logging", "Failure retry with backoff",
            ],
            model="Lightweight / local (Ollama)",
            status="ready",
            accent="#F472B6",
        ),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("agentCenterView")
        self.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(40, 28, 40, 28)
        root.setSpacing(22)

        # Header
        title = QLabel("Agent Center")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        root.addWidget(title)

        sub = QLabel(
            "OMEN runs a multi-agent architecture — specialized agents are "
            "invoked automatically based on task complexity and domain."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        root.addWidget(sub)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(12)
        for val, lbl, col in [
            ("6",   "Active Agents",      PRIMARY),
            ("53",  "Registered Tools",   SUCCESS),
            ("∞",   "Concurrent Tasks",   SECONDARY),
            ("Auto","Routing Mode",       "#FBBF24"),
        ]:
            pill = QFrame()
            pill.setStyleSheet(
                "QFrame { background: rgba(21,21,28,0.80); border: 1px solid rgba(255,255,255,0.07);"
                " border-radius: 10px; }"
                "QLabel { background: transparent; border: none; }"
            )
            p_lay = QHBoxLayout(pill)
            p_lay.setContentsMargins(16, 10, 16, 10)
            p_lay.setSpacing(8)
            v = QLabel(val)
            v.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            v.setStyleSheet(f"color: {col};")
            p_lay.addWidget(v)
            l = QLabel(lbl)
            l.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
            p_lay.addWidget(l)
            stats.addWidget(pill)
        stats.addStretch()
        root.addLayout(stats)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: rgba(255,255,255,0.06);")
        root.addWidget(div)

        sec = QLabel("Registered Agents")
        sec.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        sec.setStyleSheet(f"color: {TEXT_SECONDARY};")
        root.addWidget(sec)

        # 2-column agent grid
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for idx, agent_data in enumerate(self.AGENTS):
            card = AgentCard(**agent_data)
            card.trigger_requested.connect(self.agent_triggered.emit)
            row, col = divmod(idx, 2)
            grid.addWidget(card, row, col)

        root.addLayout(grid)

        # Routing explanation
        routing_frame = QFrame()
        routing_frame.setStyleSheet(
            "QFrame { background: rgba(0,210,238,0.05); border: 1px solid rgba(0,210,238,0.15);"
            " border-radius: 12px; }"
            "QLabel { background: transparent; border: none; }"
        )
        rf_lay = QVBoxLayout(routing_frame)
        rf_lay.setContentsMargins(20, 16, 20, 16)
        rf_lay.setSpacing(8)
        rt = QLabel("INTELLIGENT ROUTING")
        rt.setStyleSheet(
            f"color: {PRIMARY}; font-size: 10px; font-weight: bold; letter-spacing: 1.2px;"
        )
        rf_lay.addWidget(rt)
        rd = QLabel(
            "OMEN automatically routes each request to the optimal agent based on intent "
            "classification. Simple queries go to ChatAgent (fast, low-cost). Code tasks route "
            "to CodeAgent with full IDE toolset. Research queries invoke ResearchAgent with "
            "multi-hop search. Vision tasks use VisionAgent with screenshot capture. All agents "
            "share the same tool registry and memory layer."
        )
        rd.setWordWrap(True)
        rd.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; line-height: 160%;")
        rf_lay.addWidget(rd)
        root.addWidget(routing_frame)
        root.addStretch()
