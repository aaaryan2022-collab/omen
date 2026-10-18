# ============================================
"""
Unified Voice-First Gmail Tool — one tool, natural language, unread-first.
Handles: check, search, categorize, recall, read detail — all by voice.
"""

import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult, RiskLevel
from providers.email.base import EmailProvider, get_email_provider
from voice.tts import OmenTTS
from app.config import config
from app.logging_config import logger


class VoiceEmailArgs(BaseModel):
    """Natural language query for email."""
    query: str = Field(..., description="Voice command: 'check email', 'find from amazon', 'read important', 'read that'")


class VoiceEmailTool(BaseTool):
    """
    Single entry point for all voice email interactions.
    Parses intent → executes → speaks result.
    """

    name = "voice_email"
    description = (
        "Voice-first Gmail interface. Examples: "
        "'check my email' (unread), 'read important emails', "
        "'find emails from amazon', 'search for invoice', "
        "'read the first one', 'read email 2'."
    )
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = VoiceEmailArgs

    _CATEGORY_MAP = {
        "important": "is:important",
        "promotions": "category:promotions",
        "promos": "category:promotions",
        "social": "category:social",
        "updates": "category:updates",
        "forums": "category:forums",
        "starred": "is:starred",
        "snoozed": "is:snoozed",
        "sent": "in:sent",
        "drafts": "in:drafts",
        "spam": "in:spam",
        "trash": "in:trash",
    }

    def __init__(self):
        super().__init__()
        self._tts = OmenTTS() if config.voice_enabled else None
        self._last_results: List[Dict] = []
        self._last_query: str = ""

    def execute(self, query: str) -> ToolResult:
        """Parse natural language and execute appropriate email action."""
        q = query.lower().strip()
        self._last_query = q

        try:
            provider: EmailProvider = get_email_provider()
            if not provider.is_configured():
                msg = "Gmail not connected. Please authorize in Settings → Security."
                self._speak(msg)
                return ToolResult(success=False, message=msg)

            # Route based on intent
            if self._is_detail_request(q):
                return self._read_detail(provider, q)

            if self._is_search_request(q):
                return self._search_emails(provider, q)

            if self._is_category_request(q):
                return self._read_category(provider, q)

            # Default: "check email" → unread inbox
            return self._read_unread(provider)

        except Exception as e:
            logger.error(f"Voice email error: {e}")
            return ToolResult(success=False, error=str(e))

    # ──────────────────────────────────────────────
    # Intent Detection
    # ──────────────────────────────────────────────

    def _is_detail_request(self, q: str) -> bool:
        patterns = [
            r"^read\s+(?:the\s+)?(?:first|second|third|\d+)(?:\s+one)?$",
            r"^read\s+email\s+\d+$",
            r"^open\s+(?:the\s+)?(?:first|second|third|\d+)$",
            r"^details?$",
            r"^read\s+that$",
            r"^read\s+it$",
        ]
        return any(re.match(p, q) for p in patterns)

    def _is_search_request(self, q: str) -> bool:
        patterns = [
            r"^(find|search|look for)\s+",
            r"^emails?\s+(?:from|by)\s+",
            r"^who\s+(?:sent|emailed)",
        ]
        return any(re.match(p, q) for p in patterns)

    def _is_category_request(self, q: str) -> bool:
        patterns = [
            r"^read\s+(?:my\s+)?(?:important|promotions?|promos|social|updates?|forums?|starred|sent|drafts?|spam|trash)$",
            r"^show\s+(?:my\s+)?(?:important|promotions?|promos|social|updates?|forums?|starred|sent|drafts?|spam|trash)$",
        ]
        return any(re.match(p, q) for p in patterns)

    # ──────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────

    def _read_unread(self, provider: EmailProvider) -> ToolResult:
        """Default: unread inbox, max 5."""
        emails = provider.get_unread(limit=5)
        return self._format_and_speak(emails, "unread")

    def _read_category(self, provider: EmailProvider, q: str) -> ToolResult:
        """Read emails by category (important, promotions, etc.)."""
        category = self._extract_category(q)
        query = self._CATEGORY_MAP.get(category, "in:inbox")
        emails = provider.search(query, limit=7)
        return self._format_and_speak(emails, category)

    def _search_emails(self, provider: EmailProvider, q: str) -> ToolResult:
        """Search by sender or keyword."""
        search_term = self._extract_search_term(q)
        emails = provider.search(search_term, limit=7)
        label = f"matching '{search_term}'"
        return self._format_and_speak(emails, label)

    def _read_detail(self, provider: EmailProvider, q: str) -> ToolResult:
        """Read full content of a specific email from last results or fetch new."""
        index = self._extract_index(q)

        # If we have cached results from last query, use those
        if self._last_results and index < len(self._last_results):
            email_data = self._last_results[index]
            full_text = self._build_full_text(email_data)
            self._speak(full_text)
            return ToolResult(success=True, data=email_data, message=full_text)

        # Otherwise fetch fresh unread and pick index
        emails = provider.get_unread(limit=10)
        if not emails or index >= len(emails):
            msg = "No email at that position."
            self._speak(msg)
            return ToolResult(success=False, message=msg)

        email = emails[index]
        full_text = self._build_full_text({
            "from": email.from_address,
            "subject": email.subject,
            "body": email.body,
            "date": email.date.strftime("%B %d at %I:%M %p") if email.date else "Unknown",
        })
        self._speak(full_text)
        return ToolResult(success=True, data=email, message=full_text)

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _format_and_speak(self, emails: List, label: str) -> ToolResult:
        if not emails:
            msg = f"No {label} emails found."
            self._speak(msg)
            return ToolResult(success=True, message=msg)

        # Categorize for summary
        counts = {}
        for e in emails:
            cat = self._categorize(e)
            counts[cat] = counts.get(cat, 0) + 1

        # Build spoken summary
        parts = [f"Found {len(emails)} {label} emails."]
        for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
            if count:
                parts.append(f"{count} {cat}.")
        parts.append("Say 'read first', 'read second', or 'read email 3' for details.")
        spoken = " ".join(parts)

        # Cache for follow-up
        self._last_results = [
            {
                "from": e.from_address,
                "subject": e.subject,
                "body": e.body[:2000],
                "date": e.date.strftime("%B %d at %I:%M %p") if e.date else "Unknown",
                "important": e.is_important,
                "labels": e.labels,
            }
            for e in emails
        ]

        self._speak(spoken)
        return ToolResult(success=True, data=self._last_results, message=spoken)

    def _categorize(self, email) -> str:
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

    def _extract_category(self, q: str) -> str:
        for cat in self._CATEGORY_MAP:
            if cat in q:
                return cat
        return "all"

    def _extract_search_term(self, q: str) -> str:
        # Remove command words, keep the search term
        q = re.sub(r"^(find|search|look for)\s+", "", q)
        q = re.sub(r"^emails?\s+(?:from|by)\s+", "", q)
        q = re.sub(r"^who\s+(?:sent|emailed)\s+", "", q)
        return q.strip()

    def _extract_index(self, q: str) -> int:
        # "first" → 0, "second" → 1, "third" → 2, "email 3" → 2
        ordinals = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4}
        for word, idx in ordinals.items():
            if word in q:
                return idx
        match = re.search(r"(\d+)", q)
        if match:
            return int(match.group(1)) - 1  # 1-based → 0-based
        return 0

    def _build_full_text(self, email: Dict) -> str:
        return (
            f"From {email['from']}. "
            f"Subject: {email['subject']}. "
            f"Received {email['date']}. "
            f"{email['body'][:1500]}"
        )

    def _speak(self, text: str):
        if self._tts and self._tts.is_available:
            self._tts.speak(text, interrupt=True)


# Auto-register decorator
from tools.registry import tool

@tool(
    name="voice_email",
    description="Voice-first Gmail: check unread, read important, find from sender, search keyword, read detail.",
    risk_level=RiskLevel.LOW,
    permission_tag="email",
)
def voice_email(query: str) -> ToolResult:
    """Function wrapper for the VoiceEmailTool."""
    return VoiceEmailTool().execute(query)