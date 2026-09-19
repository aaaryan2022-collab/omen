# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
SQLite Database connection manager and schema initialization.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional
from app.constants import DB_PATH
from app.logging_config import logger


class Database:
    """Thread-safe SQLite Database manager with WAL mode enabled."""

    _local = threading.local()

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a thread-local SQLite connection with dictionary row factory."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode and foreign keys for high concurrency and integrity
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            self._local.conn = conn
        return self._local.conn

    def close(self):
        """Closes thread-local connection if open."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            try:
                self._local.conn.close()
            except Exception:
                pass
            self._local.conn = None

    def init_db(self):
        """Initializes database schema and indexes."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        with conn:
            # Tasks Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT DEFAULT 'MEDIUM',
                    status TEXT DEFAULT 'PENDING',
                    category TEXT DEFAULT 'General',
                    due_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    notes TEXT DEFAULT ''
                );
            """)

            # Reminders Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT DEFAULT '',
                    trigger_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'SCHEDULED',
                    recurring_cron TEXT,
                    is_recurring INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fired_at TIMESTAMP,
                    associated_task_id INTEGER,
                    FOREIGN KEY(associated_task_id) REFERENCES tasks(id) ON DELETE SET NULL
                );
            """)

            # Memories Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'user_preference',
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(category, key)
                );
            """)

            # Conversations Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT DEFAULT 'New Conversation',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived INTEGER DEFAULT 0
                );
            """)

            # Messages Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    thought TEXT,
                    tool_calls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
            """)

            # Action Audit Log Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tool_name TEXT NOT NULL,
                    arguments TEXT DEFAULT '{}',
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT DEFAULT '',
                    duration_ms INTEGER DEFAULT 0,
                    error TEXT
                );
            """)

            # News Cache Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    published_at TIMESTAMP,
                    summary TEXT DEFAULT '',
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Settings KV Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Indexes for fast search
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_at);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_trigger ON reminders(trigger_time, status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_cat_key ON memories(category, key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action_logs_time ON action_logs(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_news_category ON news_cache(category);")

        conn.close()
        logger.info(f"Database initialized at {self.db_path}")


# Global database instance
_db_instance: Optional[Database] = None


def get_db(db_path: Optional[Path] = None) -> Database:
    """Returns the application database singleton."""
    global _db_instance
    if _db_instance is None or (db_path and _db_instance.db_path != db_path):
        _db_instance = Database(db_path)
    return _db_instance


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
