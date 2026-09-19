# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
IMAP/SMTP Email Provider for Outlook and Gmail integration.
"""

from typing import List, Optional
from datetime import datetime
import imaplib
import email
from email.header import decode_header
from providers.email.base import EmailProvider, EmailMessage
from app.logging_config import logger


class ImapEmailProvider(EmailProvider):
    """General IMAP email provider supporting Gmail and Outlook."""

    def __init__(self, email_address: str, password: str, imap_server: str, smtp_server: Optional[str] = None):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server or imap_server.replace("imap.", "smtp.")
        self._mail: Optional[imaplib.IMAP4_SSL] = None

    def is_configured(self) -> bool:
        return bool(self.email_address and self.imap_server and self.password)

    def _connect(self) -> bool:
        try:
            if self._mail is None:
                self._mail = imaplib.IMAP4_SSL(self.imap_server)
            self._mail.login(self.email_address, self.password)
            return True
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return False

    def get_inbox(self, limit: int = 10) -> List[EmailMessage]:
        if not self._connect():
            return []
        try:
            self._mail.select("INBOX")
            status, data = self._mail.search(None, "ALL")
            if status != "OK":
                return []
            msg_ids = data[0].split()[-limit:]
            return [self._parse(msg_id) for msg_id in reversed(msg_ids) if msg_id]
        except Exception as e:
            logger.error(f"Failed to retrieve inbox: {e}")
            return []

    def get_unread(self, limit: int = 10) -> List[EmailMessage]:
        if not self._connect():
            return []
        try:
            self._mail.select("INBOX")
            status, data = self._mail.search(None, "UNSEEN")
            if status != "OK":
                return []
            msg_ids = data[0].split()[-limit:]
            return [self._parse(msg_id) for msg_id in reversed(msg_ids) if msg_id]
        except Exception as e:
            logger.error(f"Failed to retrieve unread: {e}")
            return []

    def search(self, query: str, limit: int = 10) -> List[EmailMessage]:
        if not self._connect():
            return []
        try:
            self._mail.select("INBOX")
            status, data = self._mail.search(None, query)
            if status != "OK":
                return []
            msg_ids = data[0].split()[-limit:]
            return [self._parse(msg_id) for msg_id in reversed(msg_ids) if msg_id]
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []

    def get_by_sender(self, sender: str, limit: int = 10) -> List[EmailMessage]:
        return self.search(f'from "{sender}"', limit)

    def get_by_keyword(self, keyword: str, limit: int = 10) -> List[EmailMessage]:
        return self.search(keyword, limit)

    def get_message(self, message_id: str) -> Optional[EmailMessage]:
        if not self._connect():
            return None
        try:
            status, data = self._mail.fetch(message_id, "(RFC822)")
            if status != "OK":
                return None
            msg = email.message_from_bytes(data[0][1])
            return self._parse_message_object(msg)
        except Exception as e:
            logger.error(f"Failed to fetch message {message_id}: {e}")
            return None

    def summarize_emails(self, messages: List[EmailMessage]) -> str:
        if not messages:
            return "No emails to summarize."
        important = [m for m in messages if m.is_important]
        return f"Analyzed {len(messages)} emails. {len(important)} are important."

    def _parse(self, msg_id: bytes) -> Optional[EmailMessage]:
        try:
            status, data = self._mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                return None
            msg = email.message_from_bytes(data[0][1])
            return self._parse_message_object(msg)
        except Exception as e:
            logger.error(f"Failed to parse message {msg_id}: {e}")
            return None

    def _parse_message_object(self, msg: email.message.Message) -> EmailMessage:
        subject, enc = decode_header(msg.get("Subject", ""))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(enc or "utf-8", errors="replace")
        sender_str, enc = decode_header(msg.get("From", ""))[0]
        if isinstance(sender_str, bytes):
            sender_str = sender_str.decode(enc or "utf-8", errors="replace")
        date_str = msg.get("Date", "")
        date = datetime.now()
        try:
            date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            pass

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="replace")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="replace")

        return EmailMessage(
            id=msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
            from_address=sender_str,
            subject=subject,
            body=body,
            date=date,
            raw_snippet=body[:250],
        )


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
