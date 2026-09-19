# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Database package for OMEN.
"""

from database.database import Database, get_db
from database.models import (
    Task,
    Reminder,
    Memory,
    Conversation,
    Message,
    ActionLog,
    NewsArticle,
    SettingRecord,
)
from database.repositories import (
    TaskRepository,
    ReminderRepository,
    MemoryRepository,
    ConversationRepository,
    ActionLogRepository,
    SettingsRepository,
    NewsCacheRepository,
)

__all__ = [
    "Database",
    "get_db",
    "Task",
    "Reminder",
    "Memory",
    "Conversation",
    "Message",
    "ActionLog",
    "NewsArticle",
    "SettingRecord",
    "TaskRepository",
    "ReminderRepository",
    "MemoryRepository",
    "ConversationRepository",
    "ActionLogRepository",
    "SettingsRepository",
    "NewsCacheRepository",
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
