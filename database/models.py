# ============================================
"""
Database Models and Dataclasses for OMEN.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.constants import TaskPriority, TaskStatus, ReminderStatus, RiskLevel


class Task(BaseModel):
    """Productivity task model."""
    id: Optional[int] = None
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    category: str = "General"
    due_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    notes: str = ""


class Reminder(BaseModel):
    """Scheduled reminder model."""
    id: Optional[int] = None
    title: str
    message: str = ""
    trigger_time: datetime
    status: ReminderStatus = ReminderStatus.SCHEDULED
    recurring_cron: Optional[str] = None
    is_recurring: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    fired_at: Optional[datetime] = None
    associated_task_id: Optional[int] = None


class Memory(BaseModel):
    """Persistent user and system memory item."""
    id: Optional[int] = None
    category: str = "user_preference"  # user_preference, project, fact, habit, context
    key: str
    value: str
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    is_active: bool = True


class Conversation(BaseModel):
    """Chat session."""
    id: Optional[int] = None
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_archived: bool = False


class Message(BaseModel):
    """Individual message within a conversation."""
    id: Optional[int] = None
    conversation_id: int
    role: str  # user, assistant, system, tool
    content: str
    thought: Optional[str] = None
    tool_calls: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.now)


class ActionLog(BaseModel):
    """Audit log entry for tool executions and security actions."""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_name: str
    arguments: str  # JSON string
    risk_level: RiskLevel
    status: str  # SUCCESS, FAILED, CONFIRMATION_REJECTED, EMERGENCY_STOPPED
    result: str = ""
    duration_ms: int = 0
    error: Optional[str] = None


class NewsArticle(BaseModel):
    """Cached news headline."""
    id: Optional[int] = None
    title: str
    source: str
    url: str
    category: str
    published_at: Optional[datetime] = None
    summary: str = ""
    cached_at: datetime = Field(default_factory=datetime.now)


class SettingRecord(BaseModel):
    """Key-value setting persisted in database."""
    key: str
    value: str
    updated_at: datetime = Field(default_factory=datetime.now)


