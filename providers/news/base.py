# ============================================
"""
Base class for News Providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    category: str
    published_at: Optional[datetime] = None
    summary: str = ""


class NewsProvider(ABC):
    @abstractmethod
    def get_headlines(self, category: str = "Technology", limit: int = 10) -> List[NewsItem]:
        pass

    @abstractmethod
    def search_news(self, query: str, limit: int = 10) -> List[NewsItem]:
        pass


