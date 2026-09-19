# ============================================
"""
EventBus for internal OMEN signaling.
"""

from enum import Enum
from typing import Callable, List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EventType(str, Enum):
    AGENT_STATE_CHANGE = "AGENT_STATE_CHANGE"
    TOOL_EXECUTING = "TOOL_EXECUTING"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    STREAM_TOKEN = "STREAM_TOKEN"
    CONVERSATION_NEW = "CONVERSATION_NEW"
    CONVERSATION_UPDATED = "CONVERSATION_UPDATED"
    REMINDER_FIRED = "REMINDER_FIRED"
    TASK_CREATED = "TASK_CREATED"
    ERROR = "ERROR"


class Event(BaseModel):
    type: EventType
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class EventBus:
    """PubSub implementation for event-driven UI and core updates."""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {et: [] for et in EventType}
        self._history: List[Event] = []

    def emit(self, event_type: EventType, payload: Dict[str, Any] = None):
        event = Event(type=event_type, payload=payload or {})
        self.publish(event)

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        self._subscribers[event_type].append(callback)

    def publish(self, event: Event):
        self._history.append(event)
        for cb in self._subscribers.get(event.type, []):
            try:
                cb(event)
            except Exception as e:
                pass

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[Event]:
        if event_type:
            return [e for e in self._history if e.type == event_type][-limit:]
        return self._history[-limit:]

_bus_instance = None


def get_event_bus() -> EventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance


