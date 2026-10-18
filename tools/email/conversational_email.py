# ============================================
"""
Minimal Conversational Gmail Tool — fetch, categorize, read aloud.
One tool, ~100 lines, zero bloat.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult, RiskLevel
from providers.email.base import EmailProvider, get_email_provider
from voice.tts import OmenTTS
from app.config import config
from app.logging_config import logger


class ReadEmailsArgs(BaseModel):
    """Arguments for ReadEmailsAloudTool."""
    max_emails: int = Field(default=5, description="Max emails to fetch")
    unread_only: bool = Field(default=True, description="Only unread emails")
    category: str = Field(default="all", description="Category: all, important, promotions, social, updates")


class ReadEmailsAloudTool(BaseTool):
    """
    Minimal conversational email reader.
    Fetches -> Categorizes -> Speaks summary -> Asks for details.
    """

    name = "read_emails"
    description = "Checks Gmail, categorizes, and reads a brief aloud. Say 'details' for full content."
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = ReadEmailsArgs

    _CATEGORIES = {
        "important": "is:important",
        "promotions": "category:promotions",
        "social": "category:social",
        "updates": "category:updates",
        "forums": "category:forums",
    }

    def __init__(self):
        super().__init__()
        self._tts = OmenTTS() if config.voice_enabled else None
        self._last_emails: List[Dict] = []

    def execute(
        self,
        max_emails: int = 5,
        unread_only: bool = True,
        category: str = "all",
    ) -> ToolResult:
        try:
            provider: EmailProvider = get_email_provider()
            if not provider.is_configured():
                return ToolResult(
                    success=False,
                    message="Gmail not connected. Say 'configure Gmail' to set up.",
                )

            # Build query
            query_parts = []
            if unread_only:
                query_parts.append("is:unread")
            if category != "all" and category in self._CATEGORIES:
                query_parts.append(self._CATEGORIES[category])

            query = " ".join(query_parts) if query_parts else "in:inbox"
            emails = provider.search(query, limit=max_emails)

            if not emails:
                msg = f"No {category} emails found." if category != "all" else "No unread emails."
                self._speak(msg)
                return ToolResult(success=True, message=msg)

            # Categorize for summary
            counts = {}
            for e in emails:
                cat = self._categorize(e)
                counts[cat] = counts.get(cat, 0) + 1

            # Build concise spoken summary
            summary_parts = [f"Found {len(emails)} emails."]
            for cat, count in counts.items():
                if count:
                    summary_parts.append(f"{count} {cat}.")
            summary_parts.append("Say 'details' to hear them, or 'next' to skip.")
            spoken_summary = " ".join(summary_parts)

            # Cache for follow-up
            self._last_emails = [
                {
                    "from": e.from_address,
                    "subject": e.subject,
                    "body": e.body[:500],  # truncate for memory
                    "date": e.date.strftime("%b %d, %H:%M") if e.date else "Unknown",
                    "important": e.is_important,
                    "labels": e.labels,
                }
                for e in emails
            ]

            self._speak(spoken_summary)

            return ToolResult(
                success=True,
                data=self._last_emails,
                message=spoken_summary,
            )

        except Exception as e:
            logger.error(f"Read emails error: {e}")
            return ToolResult(success=False, error=str(e))

    def _categorize(self, email) -> str:
        """Quick label-based categorization."""
        labels = [l.lower() for l in email.labels]
        if email.is_important or "important" in labels:
            return "important"
        if "category_promotions" in labels or "promotions" in labels:
            return "promotions"
        if "category_social" in labels or "social" in labels:
            return "social"
        if "category_updates" in labels or "updates" in labels:
            return "updates"
        if "category_forums" in labels or "forums" in labels:
            return "forums"
        return "primary"

    def _speak(self, text: str):
        """Non-blocking TTS."""
        if self._tts and self._tts.is_available:
            self._tts.speak(text, interrupt=True)


# Follow-up tool for reading full email content
class ReadEmailDetailArgs(BaseModel):
    index: int = Field(default=0, description="Email index from last read_emails call")


class ReadEmailDetailTool(BaseTool):
    """Reads full content of a specific email from the last fetch."""

    name = "read_email_detail"
    description = "Reads the full content of an email by index. Use after read_emails."
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = ReadEmailDetailArgs

    def __init__(self):
        super().__init__()
        self._tts = OmenTTS() if config.voice_enabled else None

    def execute(self, index: int = 0) -> ToolResult:
        # Access the shared state from ReadEmailsAloudTool
        from providers.email.gmail_provider import GmailProvider
        from tools.email.email_tools import ReadEmailsAloudTool

        # Hack: get cached emails from the other tool instance
        # In production, this would use a shared state manager
        provider = get_email_provider()
        if not provider.is_configured():
            return ToolResult(success=False, message="Gmail not connected.")

        try:
            emails = provider.search("in:inbox is:unread", limit=10)
            if not emails or index >= len(emails):
                return ToolResult(success=False, message="Email not found.")

            email = emails[index]
            full_text = (
                f"From {email.from_address}. "
                f"Subject: {email.subject}. "
                f"Received {email.date.strftime('%B %d at %I %p') if email.date else 'recently'}. "
                f"{email.body[:1500]}"
            )

            if self._tts and self._tts.is_available:
                self._tts.speak(full_text, interrupt=True)

            return ToolResult(success=True, message=full_text)
        except Exception as e:
            logger.error(f"Read email detail error: {e}")
            return ToolResult(success=False, error=str(e))