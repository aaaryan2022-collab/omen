# ============================================
"""
Abstract Email Provider interface for OMEN.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    id: Optional[str] = None
    from_address: str
    to_addresses: List[str] = Field(default_factory=list)
    subject: str
    body: str
    date: Optional[datetime] = None
    is_read: bool = False
    is_important: bool = False
    labels: List[str] = Field(default_factory=list)
    raw_snippet: str = ""


class EmailProvider(ABC):
    """Abstract interface for reading, searching, and analyzing emails."""

    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def get_inbox(self, limit: int = 10) -> List[EmailMessage]:
        pass

    @abstractmethod
    def get_unread(self, limit: int = 10) -> List[EmailMessage]:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[EmailMessage]:
        pass

    @abstractmethod
    def get_by_sender(self, sender: str, limit: int = 10) -> List[EmailMessage]:
        pass

    @abstractmethod
    def get_by_keyword(self, keyword: str, limit: int = 10) -> List[EmailMessage]:
        pass

    @abstractmethod
    def get_message(self, message_id: str) -> Optional[EmailMessage]:
        pass

    @abstractmethod
    def summarize_emails(self, messages: List[EmailMessage]) -> str:
        pass


