# ============================================
"""
News and Morning Briefing tool implementations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import psutil
from tools.base import BaseTool, ToolResult
from providers.news.rss_provider import get_news_provider
from productivity.tasks import get_task_manager
from productivity.reminders import get_reminder_manager
from app.constants import RiskLevel


class GetNewsHeadlinesArgs(BaseModel):
    category: str = Field(default="Technology", description="News topic: Technology, Artificial Intelligence, India, World, or Business")
    limit: int = Field(default=5, description="Number of headlines to return")


class SearchNewsArgs(BaseModel):
    query: str = Field(description="Search keyword for news")


class GetNewsHeadlinesTool(BaseTool):
    name = "get_news_headlines"
    description = "Fetches current news headlines by category (Technology, AI, India, World, Business)."
    risk_level = RiskLevel.LOW
    args_schema = GetNewsHeadlinesArgs

    def execute(self, category: str = "Technology", limit: int = 5, **kwargs) -> ToolResult:
        np = get_news_provider()
        articles = np.get_headlines(category=category, limit=limit)
        if not articles:
            return ToolResult(success=True, data=[], message=f"No recent news articles found for '{category}'.")

        lines = [f"- **{a.title}** ({a.source})\n  {a.summary[:150]}..." for a in articles]
        summary = f"### Top {category} News Headlines:\n" + "\n\n".join(lines)
        return ToolResult(
            success=True,
            data=[a.model_dump() for a in articles],
            message=summary
        )


class SearchNewsTool(BaseTool):
    name = "search_news"
    description = "Searches recent news headlines for a specific topic or keyword."
    risk_level = RiskLevel.LOW
    args_schema = SearchNewsArgs

    def execute(self, query: str, **kwargs) -> ToolResult:
        np = get_news_provider()
        articles = np.search_news(query=query)
        if not articles:
            return ToolResult(success=True, data=[], message=f"No news found matching '{query}'.")

        lines = [f"- **{a.title}** ({a.source})\n  {a.url}" for a in articles]
        return ToolResult(
            success=True,
            data=[a.model_dump() for a in articles],
            message=f"News matching '{query}':\n" + "\n".join(lines)
        )


class GetMorningBriefingTool(BaseTool):
    name = "get_morning_briefing"
    description = "Generates a comprehensive daily briefing covering date/time, tasks, reminders, system stats, and top news."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        now = datetime.now()
        greeting = "Good morning" if now.hour < 12 else ("Good afternoon" if now.hour < 18 else "Good evening")
        date_str = now.strftime("%A, %B %d, %Y (%I:%M %p)")

        # System telemetry
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f" | Battery: {battery.percent}%" if battery else ""

        # Tasks
        tm = get_task_manager()
        tasks = tm.get_upcoming(days=2)
        task_lines = [f"• {t.title} [Priority: {t.priority.value}]" + (f" (Due: {t.due_at.strftime('%I:%M %p')})" if t.due_at else "") for t in tasks[:4]]
        task_section = "\n".join(task_lines) if task_lines else "• No urgent tasks scheduled."

        # Reminders
        rm = get_reminder_manager()
        reminders = rm.list_active()
        reminder_lines = [f"• {r.title} at {r.trigger_time.strftime('%I:%M %p')}" for r in reminders[:3]]
        reminder_section = "\n".join(reminder_lines) if reminder_lines else "• No reminders pending."

        # News
        np = get_news_provider()
        tech_news = np.get_headlines(category="Technology", limit=2)
        news_lines = [f"• {n.title} ({n.source})" for n in tech_news]
        news_section = "\n".join(news_lines) if news_lines else "• No news updates currently available."

        briefing_text = (
            f"**{greeting}, User.** Here is your briefing for {date_str}:\n\n"
            f"📊 **System Status**: CPU: {cpu}% | RAM: {mem}%{bat_str}\n\n"
            f"📋 **Upcoming Tasks ({len(tasks)})**:\n{task_section}\n\n"
            f"⏰ **Active Reminders ({len(reminders)})**:\n{reminder_section}\n\n"
            f"📰 **Top Tech News**:\n{news_section}\n\n"
            f"OMEN is online and ready for your commands."
        )

        return ToolResult(
            success=True,
            data={
                "date": date_str,
                "task_count": len(tasks),
                "reminder_count": len(reminders),
                "cpu": cpu,
                "ram": mem
            },
            message=briefing_text
        )


