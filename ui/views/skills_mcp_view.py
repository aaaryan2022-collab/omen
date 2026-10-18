# ============================================
"""
Skills & Model Context Protocol (MCP) Studio View for OMEN.
Features:
- Installed Skills Catalog with prompt instructions & required tools
- External MCP Server Manager (stdio / SSE)
- Discovered Tools explorer & live invocation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QTabWidget, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from core.skills.skills_registry import skills_registry, Skill
from core.mcp.mcp_client import mcp_manager
from ui.styles.palette import (
    PRIMARY, SECONDARY, SUCCESS, ERROR, WARNING,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BACKGROUND_DARK, BACKGROUND_CARD, FONT_FAMILY
)


class SkillsMcpView(QWidget):
    """Skills & Model Context Protocol (MCP) Management Studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._refresh_skills()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("SKILLS & MODEL CONTEXT PROTOCOL (MCP)")
        title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; letter-spacing: 1.5px;")
        title_box.addWidget(title)

        subtitle = QLabel("Modular Domain Skill Bundles · External MCP Server Discovery · Standardized Tool Protocols")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9pt;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid rgba(255, 255, 255, 0.08); background: {BACKGROUND_CARD}; }}
            QTabBar::tab {{ background: rgba(255, 255, 255, 0.03); color: {TEXT_SECONDARY}; padding: 8px 18px; border-radius: 4px; }}
            QTabBar::tab:selected {{ background: rgba(0, 210, 238, 0.12); color: {PRIMARY}; font-weight: bold; border-bottom: 2px solid {PRIMARY}; }}
        """)

        # Tab 1: Skills Registry
        skills_tab = QWidget()
        skills_layout = QVBoxLayout(skills_tab)
        skills_layout.setContentsMargins(12, 12, 12, 12)

        self._skills_table = QTableWidget(0, 4)
        self._skills_table.setHorizontalHeaderLabels(["Skill Name", "Category", "Required Tools", "Status"])
        self._skills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self._skills_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self._skills_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._skills_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self._skills_table.itemSelectionChanged.connect(self._on_skill_selected)
        skills_layout.addWidget(self._skills_table)

        self._skill_desc_viewer = QTextEdit()
        self._skill_desc_viewer.setFixedHeight(120)
        self._skill_desc_viewer.setReadOnly(True)
        self._skill_desc_viewer.setFont(QFont("Segoe UI", 9.5))
        self._skill_desc_viewer.setStyleSheet("""
            QTextEdit {
                background: #0B0E14;
                color: #CBD5E1;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self._skill_desc_viewer.setPlaceholderText("Select a skill to inspect its instructions and capabilities...")
        skills_layout.addWidget(self._skill_desc_viewer)

        tabs.addTab(skills_tab, "📦 Domain Skills")

        # Tab 2: MCP Servers
        mcp_tab = QWidget()
        mcp_layout = QVBoxLayout(mcp_tab)
        mcp_layout.setContentsMargins(12, 12, 12, 12)

        mcp_top = QHBoxLayout()
        self._mcp_name_input = QLineEdit()
        self._mcp_name_input.setPlaceholderText("Server Name (e.g. 'github_mcp')")
        self._mcp_cmd_input = QLineEdit()
        self._mcp_cmd_input.setPlaceholderText("Executable Command (e.g. 'npx' or 'python')")
        btn_add_mcp = QPushButton("➕ Connect MCP Server")
        btn_add_mcp.clicked.connect(self._connect_mcp_server)
        mcp_top.addWidget(self._mcp_name_input)
        mcp_top.addWidget(self._mcp_cmd_input)
        mcp_top.addWidget(btn_add_mcp)
        mcp_layout.addLayout(mcp_top)

        self._mcp_log = QTextEdit()
        self._mcp_log.setReadOnly(True)
        self._mcp_log.setFont(QFont("Consolas", 9.5))
        self._mcp_log.setStyleSheet("""
            QTextEdit {
                background: #080B10;
                color: #38BDF8;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self._mcp_log.setPlainText("MCP Server connections and discovered tools will appear here.\nCurrently active servers: " + ", ".join(mcp_manager.list_servers() or ["None"]))
        mcp_layout.addWidget(self._mcp_log)

        tabs.addTab(mcp_tab, "🔌 MCP Servers & External Tools")

        layout.addWidget(tabs)

    def _refresh_skills(self):
        skills = skills_registry.list_all()
        self._skills_table.setRowCount(len(skills))
        for row, s in enumerate(skills):
            self._skills_table.setItem(row, 0, QTableWidgetItem(s.name))
            self._skills_table.setItem(row, 1, QTableWidgetItem(s.category.upper()))
            self._skills_table.setItem(row, 2, QTableWidgetItem(", ".join(s.required_tools) if s.required_tools else "All Tools"))
            self._skills_table.setItem(row, 3, QTableWidgetItem("ENABLED" if s.enabled else "DISABLED"))

    def _on_skill_selected(self):
        row = self._skills_table.currentRow()
        if row >= 0:
            name_item = self._skills_table.item(row, 0)
            if name_item:
                skill = skills_registry.get(name_item.text())
                if skill:
                    self._skill_desc_viewer.setPlainText(
                        f"Description: {skill.description}\n\nPrompt Instructions:\n{skill.instructions}"
                    )

    def _connect_mcp_server(self):
        name = self._mcp_name_input.text().strip()
        cmd = self._mcp_cmd_input.text().strip()
        if not name or not cmd:
            QMessageBox.warning(self, "Input Error", "Please provide both server name and command.")
            return
        client = mcp_manager.register_server(name, cmd)
        ok = client.connect()
        if ok:
            self._mcp_log.append(f"Successfully connected to MCP Server: {name}")
            self._mcp_name_input.clear()
            self._mcp_cmd_input.clear()
        else:
            self._mcp_log.append(f"Failed to connect to MCP Server: {name}")
