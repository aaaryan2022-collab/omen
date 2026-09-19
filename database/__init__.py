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


