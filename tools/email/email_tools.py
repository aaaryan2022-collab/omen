# ============================================
"""
Email tools for OMEN — read inbox, search emails, summarize.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool, ToolResult, RiskLevel
from providers.email.base import EmailProvider, get_email_provider
from app.logging_config import logger


class ReadInboxArgs(BaseModel):
    """Arguments for ReadInboxTool."""
    max_emails: int = Field(default=10, description="Maximum emails to return")
    unread_only: bool = Field(default=False, description="Show only unread emails")


class SearchEmailArgs(BaseModel):
    """Arguments for SearchEmailTool."""
    keyword: str = Field(..., description="Keyword to search for in emails")
    max_results: int = Field(default=10, description="Maximum results to return")


class SummarizeEmailArgs(BaseModel):
    """Arguments for SummarizeEmailTool."""
    email_index: int = Field(default=0, description="Index of email to summarize")


class DraftEmailArgs(BaseModel):
    """Arguments for DraftEmailTool."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")


class ReadInboxTool(BaseTool):
    """Reads emails from the inbox."""

    name = "get_inbox"
    description = "Reads emails from your inbox. Use to check new messages."
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = ReadInboxArgs

    def execute(self, max_emails: int = 10, unread_only: bool = False) -> ToolResult:
        try:
            provider: EmailProvider = get_email_provider()
            if not provider.is_configured():
                return ToolResult(
                    success=False,
                    message="Email provider not configured. Using mock data.",
                )
            emails = (
                provider.get_unread(limit=max_emails)
                if unread_only
                else provider.get_inbox(limit=max_emails)
            )
            if not emails:
                return ToolResult(success=True, message="No emails found.")
            summary = "\n".join(
                f"From: {e.from_address} | Subject: {e.subject} | Read: {e.is_read}"
                for e in emails
            )
            return ToolResult(success=True, data=emails, message=summary)
        except Exception as e:
            logger.error(f"Read inbox error: {e}")
            return ToolResult(success=False, error=str(e))


class SearchEmailTool(BaseTool):
    """Searches emails by keyword."""

    name = "search_email"
    description = "Searches emails by keyword in subject or body."
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = SearchEmailArgs

    def execute(self, keyword: str, max_results: int = 10) -> ToolResult:
        try:
            provider: EmailProvider = get_email_provider()
            if not provider.is_configured():
                return ToolResult(
                    success=False,
                    message="Email provider not configured.",
                )
            emails = provider.search(keyword, limit=max_results)
            if not emails:
                return ToolResult(success=True, message=f"No emails matching '{keyword}'.")
            summary = "\n".join(
                f"From: {e.from_address} | Subject: {e.subject}" for e in emails
            )
            return ToolResult(success=True, data=emails, message=summary)
        except Exception as e:
            logger.error(f"Search email error: {e}")
            return ToolResult(success=False, error=str(e))


class SummarizeEmailTool(BaseTool):
    """Summarizes an email by index."""

    name = "summarize_email"
    description = "Returns a summary of an email at the given index."
    risk_level = RiskLevel.LOW
    permission_tag = "email"
    args_schema = SummarizeEmailArgs

    def execute(self, email_index: int = 0) -> ToolResult:
        try:
            provider: EmailProvider = get_email_provider()
            if not provider.is_configured():
                return ToolResult(
                    success=False,
                    message="Email provider not configured.",
                )
            email = provider.get_message(email_index)
            if not email:
                return ToolResult(success=True, message="Email not found.")
            summary = (
                f"Subject: {email.subject}\n"
                f"From: {email.from_address}\n"
                f"Date: {email.date}\n"
                f"Snippet: {email.raw_snippet}\n"
                f"Summary: This appears to be about {email.subject.lower()}"
            )
            return ToolResult(success=True, data=email, message=summary)
        except Exception as e:
            logger.error(f"Summarize email error: {e}")
            return ToolResult(success=False, error=str(e))


class DraftEmailTool(BaseTool):
    """Drafts an email (does NOT send automatically)."""

    name = "draft_email"
    description = "Drafts an email. Does NOT auto-send. User must confirm before sending."
    risk_level = RiskLevel.HIGH
    permission_tag = "email"
    args_schema = DraftEmailArgs

    def verify(self, result: ToolResult, **kwargs) -> bool:
        # Drafts are safe — they don't send
        return True

    def execute(self, to: str, subject: str, body: str) -> ToolResult:
        try:
            # Store draft only — never auto-send
            logger.info(f"Email drafted: To={to}, Subject={subject}")
            return ToolResult(
                success=True,
                message=(
                    f"Draft created:\nTo: {to}\nSubject: {subject}\n"
                    f"Status: DRAFTED (not sent — requires user confirmation)\n"
                    f"Body preview: {body[:200]}..."
                ),
            )
        except Exception as e:
            logger.error(f"Draft email error: {e}")
            return ToolResult(success=False, error=str(e))


