# ============================================
"""
Mock LLM Provider for testing and development without Ollama.
"""

import json
import re
from typing import Dict, Any, List, Optional, Generator
from providers.llm.base import LLMProvider, LLMResponse, ToolCallRequest
from app.config import config
from app.logging_config import logger

# Default tool-call-like response for common OMEN tools
_MOCK_TOOL_RESPONSES: Dict[str, str] = {
    "get_system_info": '{"cpu": "Intel i7-12700K", "ram_gb": 32, "disk_gb": 512, "battery_pct": 87}',
    "get_cpu_usage": '{"cpu_percent": 23.5}',
    "get_memory_usage": '{"memory_percent": 41.2, "available_gb": 18.8}',
    "get_disk_usage": '{"disk_percent": 62.3, "free_gb": 192.5}',
    "get_battery_status": '{"charging": false, "percent": 87, "estimated_hours": 4.5}',
    "get_running_processes": '{"processes": [{"name": "chrome.exe", "cpu": 5.2}, {"name": "code.exe", "cpu": 3.1}]}',
    "add_task": '{"task_id": 1, "title": "New Task", "status": "PENDING"}',
    "list_tasks": '{"tasks": [{"id": 1, "title": "Test task", "status": "PENDING"}]}',
    "complete_task": '{"task_id": 1, "status": "COMPLETED"}',
    "delete_task": '{"task_id": 1, "deleted": true}',
    "set_reminder": '{"reminder_id": 1, "time": "2026-09-20T19:00:00", "message": "Reminder set"}',
    "list_reminders": '{"reminders": []}',
    "cancel_reminder": '{"reminder_id": 1, "cancelled": true}',
    "start_pomodoro": '{"session_id": 1, "state": "WORK", "duration_minutes": 25}',
    "get_pomodoro_status": '{"state": "IDLE", "current_session": null}',
    "search_files": '{"files": []}',
    "read_file": '{"content": "File contents here."}',
    "create_file": '{"path": "test.txt", "created": true}',
    "create_folder": '{"path": "new_folder", "created": true}',
    "rename_file": '{"old": "old.txt", "new": "new.txt", "renamed": true}',
    "move_file": '{"source": "a.txt", "dest": "b.txt", "moved": true}',
    "copy_file": '{"source": "a.txt", "dest": "copy.txt", "copied": true}',
    "delete_file": '{"path": "test.txt", "deleted": true, "moved_to_trash": true}',
    "launch_url": '{"url": "https://example.com", "opened": true}',
    "get_news_headlines": '{"articles": [{"title": "Test News", "source": "Test"}]}',
    "get_morning_briefing": '{"briefing": "Good morning. You have 2 tasks and 1 reminder today."}',
    "get_inbox": '{"emails": [{"from": "test@example.com", "subject": "Test"}]}',
}

_MOCK_CONVERSATIONAL_RESPONSES = [
    "I understand. Let me help you with that.",
    "Done — I've handled everything you asked for.",
    "Got it. I'll take care of that right away.",
    "Sure, here's what I found: Your system is running smoothly with 41% memory usage.",
    "I've created the task and reminder as you requested.",
    "Your morning briefing: You have 2 tasks due today, CPU at 23%, and weather is clear.",
    "I've scheduled your reminder for tomorrow at 7 PM.",
    "All set! I've completed your request successfully.",
]


class MockLLMProvider(LLMProvider):
    """Mock LLM for testing — returns canned responses matching tool schemas."""

    def __init__(self):
        self._call_index = 0

    def check_connection(self) -> bool:
        return True

    def list_models(self) -> List[str]:
        return ["mock-omen-v1"]

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        user_query = self._extract_last_user_message(messages)
        logger.debug(f"Mock LLM processing: {user_query[:80]}")

        # Detect tool call requests from natural language
        tool_calls = self._detect_tool_calls(user_query, tools)

        if tool_calls:
            return LLMResponse(
                content="Executing your request...",
                tool_calls=tool_calls,
                raw_response={"mock": True},
            )

        import random
        response_text = random.choice(_MOCK_CONVERSATIONAL_RESPONSES)
        return LLMResponse(content=response_text, raw_response={"mock": True})

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        user_query = self._extract_last_user_message(messages)
        tool_calls = self._detect_tool_calls(user_query, tools)

        if tool_calls:
            yield "Executing"
            yield " your "
            yield "request..."
        else:
            import random
            text = random.choice(_MOCK_CONVERSATIONAL_RESPONSES)
            for word in text.split():
                yield word + " "

    def _extract_last_user_message(self, messages: List[Dict[str, str]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    def _detect_tool_calls(self, query: str, tools: Optional[List[Dict[str, Any]]]) -> List[ToolCallRequest]:
        if not tools:
            return []
        q = query.lower()
        detected: List[Dict[str, Any]] = []
        tool_name_map = {
            "add task": "add_task",
            "create task": "add_task",
            "list tasks": "list_tasks",
            "my tasks": "list_tasks",
            "set reminder": "set_reminder",
            "remind me": "set_reminder",
            "start pomodoro": "start_pomodoro",
            "system info": "get_system_info",
            "cpu usage": "get_cpu_usage",
            "memory usage": "get_memory_usage",
            "disk usage": "get_disk_usage",
            "battery": "get_battery_status",
            "news": "get_news_headlines",
            "briefing": "get_morning_briefing",
            "open ": "launch_url",
            "search ": "search_files",
            "read file": "read_file",
            "email": "get_inbox",
        }
        for phrase, tool_name in tool_name_map.items():
            if phrase in q:
                detected.append({"name": tool_name, "arguments": {}})
        return detected


