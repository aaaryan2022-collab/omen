# ============================================
"""
Mock Email provider that generates realistic dummy data for development and CLI testing.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from providers.email.base import EmailProvider, EmailMessage
from app.config import config
from app.logging_config import logger


class MockEmailProvider(EmailProvider):
    """Provides sample fake inbox data to bypass real account requirements."""

    def __init__(self):
        self._inbox: List[EmailMessage] = []
        self._initialize_mock_inbox()

    def _initialize_mock_inbox(self):
        now = datetime.now()
        messages = [
            EmailMessage(
                id="m_1",
                from_address="professor.smith@university.edu",
                to_address=["me@personal.com"],
                subject="CS601: Advanced Algorithms - Midterm Results Published",
                body="Dear Student,\n\nThe midterm results for Advanced Algorithms are now available on the course portal. Please review and reach out if you notice any discrepancies.\n\nBest,\nProf. Smith",
                date=now - timedelta(hours=2),
                is_read=False,
                is_important=True,
                labels=["College"],
                raw_snippet="The midterm results for Advanced Algorithms are now available...",
            ),
            EmailMessage(
                id="m_2",
                from_address="manager.jones@company.com",
                to_address=["me@company.com"],
                subject="Urgent: Project Deliverable Review - Friday 6PM",
                body="Hi,\n\nPlease ensure the Q4 deliverable draft is prepared for review meeting on Friday at 6 PM. We need final sign-off before deployment.\n\nThanks,\nJones",
                date=now - timedelta(hours=5),
                is_read=False,
                is_important=True,
                labels=["Work"],
                raw_snippet="Please ensure the Q4 deliverable draft is prepared...",
            ),
            EmailMessage(
                id="m_3",
                from_address="newsletter@github.com",
                to_address=["me@personal.com"],
                subject="GitHub Weekly: What's New in Python Ecosystem",
                body="Check out the latest updates in the Python ecosystem this week, including new async features and performance improvements in popular frameworks.",
                date=now - timedelta(hours=24),
                is_read=True,
                is_important=False,
                labels=["Newsletter"],
                raw_snippet="Check out the latest updates in the Python ecosystem...",
            ),
            EmailMessage(
                id="m_4",
                from_address="no-reply@amazon.in",
                to_address=["me@personal.com"],
                subject="Your OMEN Laptop order has shipped!",
                body="Your recent order (Order #OMEN29384) has been dispatched and is expected to arrive by next week.",
                date=now - timedelta(days=1),
                is_read=False,
                is_important=False,
                labels=["Personal"],
                raw_snippet="Your recent order has been dispatched...",
            ),
            EmailMessage(
                id="m_5",
                from_address="HR@company.com",
                to_address=["me@company.com"],
                subject="Action Required: Annual Benefits Enrollment",
                body="The annual benefits enrollment window opens today. Please review your selections and confirm before October 15th.",
                date=now - timedelta(days=2),
                is_read=True,
                is_important=True,
                labels=["HR", "Work"],
                raw_snippet="Annual benefits enrollment window opens today...",
            ),
        ]
        self._inbox = messages

    def is_configured(self) -> bool:
        return True

    def _get_filtered(self, messages: List[EmailMessage], limit: int) -> List[EmailMessage]:
        return messages[:limit]

    def get_inbox(self, limit: int = 10) -> List[EmailMessage]:
        return self._inbox[:limit]

    def get_unread(self, limit: int = 10) -> List[EmailMessage]:
        unread = [m for m in self._inbox if not m.is_read]
        return unread[:limit]

    def search(self, query: str, limit: int = 10) -> List[EmailMessage]:
        q = query.lower()
        return [m for m in self._inbox if q in m.subject.lower() or q in m.body.lower()][:limit]

    def get_by_sender(self, sender: str, limit: int = 10) -> List[EmailMessage]:
        sender_l = sender.lower()
        return [m for m in self._inbox if sender_l in m.from_address.lower()][:limit]

    def get_by_keyword(self, keyword: str, limit: int = 10) -> List[EmailMessage]:
        k_l = keyword.lower()
        return [m for m in self._inbox if k_l in m.subject.lower() or k_l in m.body.lower()][:limit]

    def get_message(self, message_id: str) -> Optional[EmailMessage]:
        for m in self._inbox:
            if m.id == message_id:
                return m
        return None

    def summarize_emails(self, messages: List[EmailMessage]) -> str:
        if not messages:
            return "No emails to summarize."
        important = [m for m in messages if m.is_important]
        college = [m for m in messages if any("College" in l for l in m.labels)]
        deadline = [m for m in messages if "deadline" in m.subject.lower() or "urgent" in m.subject.lower() or "due" in m.body.lower()]

        summary_lines = [
            f"Total emails analyzed: {len(messages)}.",
            f"{len(important)} appear important.",
            f"{len(college)} related to college.",
            f"{len(deadline)} mention deadlines or urgent deliverables.",
            "\nSubjects:",
            *[f" - [{'IMPORTANT' if m.is_important else 'note'}] {m.subject}" for m in messages]
        ]
        return "\n".join(summary_lines)


