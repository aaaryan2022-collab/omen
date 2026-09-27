"""Read-only Gmail API provider using user-authorized OAuth credentials."""

import base64
import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Optional

from app.config import config
from providers.email.base import EmailMessage, EmailProvider
from security.credential_store import get_credential_store


class GmailProvider(EmailProvider):
    """Gmail reader. Sending, deleting, and modifying messages are intentionally absent."""

    def __init__(self):
        self._service = None

    def _load_service(self):
        if self._service is not None:
            return self._service
        try:
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials

            raw = get_credential_store().get_credential("gmail_oauth")
            if not raw:
                raise RuntimeError("Gmail is not authorized. Add OAuth credentials through Settings first.")
            credentials = Credentials.from_authorized_user_info(json.loads(raw), config.gmail_scopes.split())
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                get_credential_store().set_credential("gmail_oauth", credentials.to_json())
            if not credentials.valid:
                raise RuntimeError("Gmail authorization has expired and needs reauthorization.")
            self._service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
            return self._service
        except ImportError as exc:
            raise RuntimeError("Install Gmail OAuth dependencies to enable Gmail access.") from exc

    def is_configured(self) -> bool:
        return bool(get_credential_store().get_credential("gmail_oauth"))

    def get_inbox(self, limit: int = 10) -> List[EmailMessage]:
        return self._list_messages("in:inbox", limit)

    def get_unread(self, limit: int = 10) -> List[EmailMessage]:
        return self._list_messages("in:inbox is:unread", limit)

    def search(self, query: str, limit: int = 10) -> List[EmailMessage]:
        return self._list_messages(query, limit)

    def get_by_sender(self, sender: str, limit: int = 10) -> List[EmailMessage]:
        return self._list_messages(f"from:{sender}", limit)

    def get_by_keyword(self, keyword: str, limit: int = 10) -> List[EmailMessage]:
        return self._list_messages(keyword, limit)

    def get_message(self, message_id: str) -> Optional[EmailMessage]:
        service = self._load_service()
        raw = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        return self._parse_message(raw)

    def summarize_emails(self, messages: List[EmailMessage]) -> str:
        important = [message for message in messages if message.is_important]
        return f"Analyzed {len(messages)} Gmail messages; {len(important)} are marked important."

    def _list_messages(self, query: str, limit: int) -> List[EmailMessage]:
        service = self._load_service()
        response = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
        return [self._parse_message(item) for item in response.get("messages", [])]

    def _parse_message(self, message: dict) -> EmailMessage:
        service = self._load_service()
        if "payload" not in message:
            message = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
        headers = {item["name"].lower(): item["value"] for item in message.get("payload", {}).get("headers", [])}
        body = self._extract_body(message.get("payload", {}))
        date = None
        if headers.get("date"):
            try:
                date = parsedate_to_datetime(headers["date"])
            except (TypeError, ValueError, IndexError):
                date = datetime.now()
        labels = message.get("labelIds", [])
        return EmailMessage(
            id=message.get("id"),
            from_address=headers.get("from", ""),
            to_addresses=[headers["to"]] if headers.get("to") else [],
            subject=headers.get("subject", "(no subject)"),
            body=body,
            date=date,
            is_read="UNREAD" not in labels,
            is_important="IMPORTANT" in labels,
            labels=labels,
            raw_snippet=message.get("snippet", ""),
        )

    @staticmethod
    def _extract_body(payload: dict) -> str:
        parts = payload.get("parts", [])
        if parts:
            for part in parts:
                body = GmailProvider._extract_body(part)
                if body:
                    return body
        data = payload.get("body", {}).get("data")
        if not data:
            return ""
        return base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")