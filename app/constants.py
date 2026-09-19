# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Constants, Enums, and System Defaults for OMEN.
"""

from enum import Enum
from pathlib import Path
import os


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AgentState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReminderStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    FIRED = "FIRED"
    DISMISSED = "DISMISSED"
    SNOOZED = "SNOOZED"


class PomodoroState(str, Enum):
    IDLE = "IDLE"
    WORK = "WORK"
    SHORT_BREAK = "SHORT_BREAK"
    LONG_BREAK = "LONG_BREAK"
    PAUSED = "PAUSED"


class NewsCategory(str, Enum):
    TOP = "Top Headlines"
    TECH = "Technology"
    AI = "Artificial Intelligence"
    INDIA = "India"
    WORLD = "World"
    BUSINESS = "Business"
    SCIENCE = "Science"


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
DB_PATH = DATA_DIR / "omen.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Default Windows Application Aliases (executable names / launch commands)
DEFAULT_APP_ALIASES = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "file explorer": "explorer",
    "terminal": "wt",
    "windows terminal": "wt",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "spotify": "spotify",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "task manager": "taskmgr",
}

# Emergency Stop Default Hotkey
EMERGENCY_STOP_HOTKEY = "<ctrl>+<shift>+<esc>"

# User directories to whitelist by default
USER_HOME = Path.home()
DEFAULT_ALLOWED_DIRS = [
    str(USER_HOME / "Documents"),
    str(USER_HOME / "Downloads"),
    str(USER_HOME / "Desktop"),
    str(PROJECT_ROOT),
]


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
