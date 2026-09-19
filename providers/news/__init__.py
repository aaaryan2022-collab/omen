# ============================================
"""
News providers for OMEN.
"""

from providers.news.base import NewsProvider, NewsItem
from providers.news.rss_provider import RSSNewsProvider, get_news_provider

__all__ = ["NewsProvider", "NewsItem", "RSSNewsProvider", "get_news_provider"]


