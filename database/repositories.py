# ============================================
"""
Data Access Repositories for OMEN SQLite Database.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
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
from app.constants import TaskStatus, ReminderStatus, RiskLevel, TaskPriority


class TaskRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def create(self, task: Task) -> Task:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (title, description, priority, status, category, due_at, created_at, completed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.priority.value if hasattr(task.priority, "value") else str(task.priority),
                    task.status.value if hasattr(task.status, "value") else str(task.status),
                    task.category,
                    task.due_at.isoformat() if task.due_at else None,
                    task.created_at.isoformat(),
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.notes,
                ),
            )
            task.id = cursor.lastrowid
        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        conn = self.db.get_connection()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None

    def list_all(self, status: Optional[TaskStatus] = None, limit: int = 100) -> List[Task]:
        conn = self.db.get_connection()
        if status:
            val = status.value if hasattr(status, "value") else str(status)
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY due_at ASC NULLS LAST, created_at DESC LIMIT ?",
                (val, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY due_at ASC NULLS LAST, created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def get_due_today_or_upcoming(self, days: int = 7) -> List[Task]:
        conn = self.db.get_connection()
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE status != 'COMPLETED' AND status != 'CANCELLED'
            ORDER BY due_at ASC NULLS LAST, priority DESC
            LIMIT 50
            """
        ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def update(self, task: Task) -> bool:
        if not task.id:
            return False
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, status = ?, category = ?,
                    due_at = ?, completed_at = ?, notes = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.description,
                    task.priority.value if hasattr(task.priority, "value") else str(task.priority),
                    task.status.value if hasattr(task.status, "value") else str(task.status),
                    task.category,
                    task.due_at.isoformat() if task.due_at else None,
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.notes,
                    task.id,
                ),
            )
            return cursor.rowcount > 0

    def complete_task(self, task_id: int) -> bool:
        conn = self.db.get_connection()
        now_str = datetime.now().isoformat()
        with conn:
            cursor = conn.execute(
                "UPDATE tasks SET status = 'COMPLETED', completed_at = ? WHERE id = ?",
                (now_str, task_id),
            )
            return cursor.rowcount > 0

    def delete(self, task_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def search(self, query: str) -> List[Task]:
        conn = self.db.get_connection()
        param = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ? OR notes LIKE ? ORDER BY created_at DESC",
            (param, param, param)
        ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def _row_to_task(self, row: Any) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            priority=TaskPriority(row["priority"]) if row["priority"] in TaskPriority.__members__.values() else TaskPriority.MEDIUM,
            status=TaskStatus(row["status"]) if row["status"] in TaskStatus.__members__.values() else TaskStatus.PENDING,
            category=row["category"] or "General",
            due_at=datetime.fromisoformat(row["due_at"]) if row["due_at"] else None,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            notes=row["notes"] or "",
        )


class ReminderRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def create(self, reminder: Reminder) -> Reminder:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO reminders (title, message, trigger_time, status, recurring_cron, is_recurring, created_at, fired_at, associated_task_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reminder.title,
                    reminder.message,
                    reminder.trigger_time.isoformat(),
                    reminder.status.value if hasattr(reminder.status, "value") else str(reminder.status),
                    reminder.recurring_cron,
                    1 if reminder.is_recurring else 0,
                    reminder.created_at.isoformat(),
                    reminder.fired_at.isoformat() if reminder.fired_at else None,
                    reminder.associated_task_id,
                ),
            )
            reminder.id = cursor.lastrowid
        return reminder

    def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        conn = self.db.get_connection()
        row = conn.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
        return self._row_to_reminder(row) if row else None

    def list_active(self) -> List[Reminder]:
        conn = self.db.get_connection()
        rows = conn.execute(
            "SELECT * FROM reminders WHERE status = 'SCHEDULED' ORDER BY trigger_time ASC"
        ).fetchall()
        return [self._row_to_reminder(r) for r in rows]

    def list_all(self, limit: int = 50) -> List[Reminder]:
        conn = self.db.get_connection()
        rows = conn.execute(
            "SELECT * FROM reminders ORDER BY trigger_time DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [self._row_to_reminder(r) for r in rows]

    def mark_fired(self, reminder_id: int) -> bool:
        conn = self.db.get_connection()
        now_str = datetime.now().isoformat()
        with conn:
            cursor = conn.execute(
                "UPDATE reminders SET status = 'FIRED', fired_at = ? WHERE id = ?",
                (now_str, reminder_id),
            )
            return cursor.rowcount > 0

    def dismiss(self, reminder_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                "UPDATE reminders SET status = 'DISMISSED' WHERE id = ?",
                (reminder_id,),
            )
            return cursor.rowcount > 0

    def delete(self, reminder_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            return cursor.rowcount > 0

    def _row_to_reminder(self, row: Any) -> Reminder:
        return Reminder(
            id=row["id"],
            title=row["title"],
            message=row["message"] or "",
            trigger_time=datetime.fromisoformat(row["trigger_time"]),
            status=ReminderStatus(row["status"]) if row["status"] in ReminderStatus.__members__.values() else ReminderStatus.SCHEDULED,
            recurring_cron=row["recurring_cron"],
            is_recurring=bool(row["is_recurring"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            fired_at=datetime.fromisoformat(row["fired_at"]) if row["fired_at"] else None,
            associated_task_id=row["associated_task_id"],
        )


class MemoryRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def set_memory(self, category: str, key: str, value: str, confidence: float = 1.0) -> Memory:
        conn = self.db.get_connection()
        now = datetime.now().isoformat()
        with conn:
            conn.execute(
                """
                INSERT INTO memories (category, key, value, confidence, created_at, updated_at, access_count, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 0, 1)
                ON CONFLICT(category, key) DO UPDATE SET
                    value = excluded.value,
                    confidence = excluded.confidence,
                    updated_at = excluded.updated_at,
                    is_active = 1
                """,
                (category, key, value, confidence, now, now),
            )
        return self.get_by_key(category, key)  # type: ignore

    def get_by_key(self, category: str, key: str) -> Optional[Memory]:
        conn = self.db.get_connection()
        row = conn.execute(
            "SELECT * FROM memories WHERE category = ? AND key = ? AND is_active = 1",
            (category, key)
        ).fetchone()
        if row:
            # Increment access count
            with conn:
                conn.execute("UPDATE memories SET access_count = access_count + 1 WHERE id = ?", (row["id"],))
            return self._row_to_memory(row)
        return None

    def list_all(self, category: Optional[str] = None, limit: int = 100) -> List[Memory]:
        conn = self.db.get_connection()
        if category:
            rows = conn.execute(
                "SELECT * FROM memories WHERE category = ? AND is_active = 1 ORDER BY updated_at DESC LIMIT ?",
                (category, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM memories WHERE is_active = 1 ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def search(self, query: str) -> List[Memory]:
        conn = self.db.get_connection()
        param = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM memories WHERE is_active = 1 AND (key LIKE ? OR value LIKE ? OR category LIKE ?) ORDER BY updated_at DESC",
            (param, param, param)
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def delete(self, memory_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cursor.rowcount > 0

    def clear_all(self) -> bool:
        conn = self.db.get_connection()
        with conn:
            conn.execute("DELETE FROM memories")
        return True

    def _row_to_memory(self, row: Any) -> Memory:
        return Memory(
            id=row["id"],
            category=row["category"],
            key=row["key"],
            value=row["value"],
            confidence=float(row["confidence"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
            access_count=int(row["access_count"]),
            is_active=bool(row["is_active"]),
        )


class ConversationRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def create_conversation(self, title: str = "New Conversation") -> Conversation:
        conn = self.db.get_connection()
        now = datetime.now().isoformat()
        with conn:
            cursor = conn.execute(
                "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                (title, now, now),
            )
            conv_id = cursor.lastrowid
        return Conversation(id=conv_id, title=title, created_at=datetime.fromisoformat(now), updated_at=datetime.fromisoformat(now))

    def get_or_create_active(self) -> Conversation:
        conn = self.db.get_connection()
        row = conn.execute(
            "SELECT * FROM conversations WHERE is_archived = 0 ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if row:
            return Conversation(
                id=row["id"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                is_archived=bool(row["is_archived"]),
            )
        return self.create_conversation("Main Conversation")

    def add_message(self, message: Message) -> Message:
        conn = self.db.get_connection()
        now = datetime.now().isoformat()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, thought, tool_calls, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message.conversation_id,
                    message.role,
                    message.content,
                    message.thought,
                    message.tool_calls,
                    now,
                ),
            )
            message.id = cursor.lastrowid
            # Update conversation timestamp
            conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, message.conversation_id))
        return message

    def get_recent_messages(self, conversation_id: int, limit: int = 20) -> List[Message]:
        conn = self.db.get_connection()
        rows = conn.execute(
            """
            SELECT * FROM (
                SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?
            ) ORDER BY created_at ASC
            """,
            (conversation_id, limit),
        ).fetchall()
        return [
            Message(
                id=r["id"],
                conversation_id=r["conversation_id"],
                role=r["role"],
                content=r["content"],
                thought=r["thought"],
                tool_calls=r["tool_calls"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def clear_conversation(self, conversation_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        return True


class ActionLogRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def log_action(self, log: ActionLog) -> ActionLog:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO action_logs (timestamp, tool_name, arguments, risk_level, status, result, duration_ms, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log.timestamp.isoformat(),
                    log.tool_name,
                    log.arguments,
                    log.risk_level.value if hasattr(log.risk_level, "value") else str(log.risk_level),
                    log.status,
                    log.result,
                    log.duration_ms,
                    log.error,
                ),
            )
            log.id = cursor.lastrowid
        return log

    def list_recent(self, limit: int = 100) -> List[ActionLog]:
        conn = self.db.get_connection()
        rows = conn.execute(
            "SELECT * FROM action_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            ActionLog(
                id=r["id"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                tool_name=r["tool_name"],
                arguments=r["arguments"],
                risk_level=RiskLevel(r["risk_level"]) if r["risk_level"] in RiskLevel.__members__.values() else RiskLevel.LOW,
                status=r["status"],
                result=r["result"] or "",
                duration_ms=int(r["duration_ms"]),
                error=r["error"],
            )
            for r in rows
        ]


class SettingsRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        conn = self.db.get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set(self, key: str, value: str):
        conn = self.db.get_connection()
        now = datetime.now().isoformat()
        with conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, now),
            )

    def get_all(self) -> Dict[str, str]:
        conn = self.db.get_connection()
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}


class NewsCacheRepository:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def save_articles(self, articles: List[NewsArticle]):
        conn = self.db.get_connection()
        with conn:
            for a in articles:
                conn.execute(
                    """
                    INSERT INTO news_cache (title, source, url, category, published_at, summary, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title = excluded.title,
                        summary = excluded.summary,
                        cached_at = excluded.cached_at
                    """,
                    (
                        a.title,
                        a.source,
                        a.url,
                        a.category,
                        a.published_at.isoformat() if a.published_at else None,
                        a.summary,
                        a.cached_at.isoformat(),
                    ),
                )

    def get_by_category(self, category: str, limit: int = 20) -> List[NewsArticle]:
        conn = self.db.get_connection()
        rows = conn.execute(
            "SELECT * FROM news_cache WHERE category = ? ORDER BY published_at DESC NULLS LAST, cached_at DESC LIMIT ?",
            (category, limit),
        ).fetchall()
        return [
            NewsArticle(
                id=r["id"],
                title=r["title"],
                source=r["source"],
                url=r["url"],
                category=r["category"],
                published_at=datetime.fromisoformat(r["published_at"]) if r["published_at"] else None,
                summary=r["summary"] or "",
                cached_at=datetime.fromisoformat(r["cached_at"]),
            )
            for r in rows
        ]


