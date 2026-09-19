# ============================================
"""
Email provider integrations for OMEN.
"""

from providers.email.base import EmailProvider, EmailMessage
from providers.email.mock_email import MockEmailProvider
from providers.email.imap_provider import ImapEmailProvider

__all__ = ["EmailProvider", "EmailMessage", "MockEmailProvider", "ImapEmailProvider"]


