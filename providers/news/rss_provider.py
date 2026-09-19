# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
RSS-based News Provider with multi-category feeds and caching.
"""

from typing import List, Dict, Optional
from datetime import datetime
import time
import feedparser
from providers.news.base import NewsProvider, NewsItem
from database.repositories import NewsCacheRepository
from database.models import NewsArticle
from app.logging_config import logger


# Reliable RSS feed sources for major categories
FEED_SOURCES: Dict[str, List[Dict[str, str]]] = {
    "Technology": [
        {"url": "https://feeds.feedburner.com/TechCrunch/", "source": "TechCrunch"},
        {"url": "http://feeds.arstechnica.com/arstechnica/index", "source": "Ars Technica"},
        {"url": "https://news.ycombinator.com/rss", "source": "Hacker News"},
    ],
    "Artificial Intelligence": [
        {"url": "https://feeds.feedburner.com/TechCrunch/", "source": "TechCrunch AI"},
        {"url": "https://www.technologyreview.com/feed/", "source": "MIT Tech Review"},
    ],
    "India": [
        {"url": "https://www.thehindu.com/news/national/feeder/default.rss", "source": "The Hindu"},
        {"url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "source": "Times of India"},
    ],
    "World": [
        {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC News"},
        {"url": "http://rss.cnn.com/rss/edition_world.rss", "source": "CNN World"},
    ],
    "Business": [
        {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
        {"url": "https://www.thehindu.com/business/feeder/default.rss", "source": "The Hindu Business"},
    ],
}


class RSSNewsProvider(NewsProvider):
    """Fetches, parses, and caches real-time news headlines."""

    def __init__(self, cache_repo: Optional[NewsCacheRepository] = None):
        self.cache_repo = cache_repo or NewsCacheRepository()

    def get_headlines(self, category: str = "Technology", limit: int = 10) -> List[NewsItem]:
        # Normalize category
        cat_key = self._match_category(category)
        sources = FEED_SOURCES.get(cat_key, FEED_SOURCES["Technology"])

        articles: List[NewsItem] = []
        for src in sources:
            try:
                feed = feedparser.parse(src["url"])
                for entry in feed.entries[:limit]:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "")
                    summary = entry.get("summary", "") or entry.get("description", "")
                    # Clean html from summary
                    import re
                    clean_summary = re.sub(r"<[^>]+>", "", summary).strip()[:300]

                    if title and link:
                        articles.append(NewsItem(
                            title=title,
                            source=src["source"],
                            url=link,
                            category=cat_key,
                            summary=clean_summary,
                            published_at=datetime.now(),
                        ))
                    if len(articles) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Failed to fetch RSS from {src['url']}: {e}")

            if len(articles) >= limit:
                break

        # Save to database cache
        if articles:
            db_articles = [
                NewsArticle(
                    title=a.title,
                    source=a.source,
                    url=a.url,
                    category=a.category,
                    published_at=a.published_at,
                    summary=a.summary
                )
                for a in articles
            ]
            self.cache_repo.save_articles(db_articles)
            return articles

        # Fallback to cached articles from DB if network fails
        cached = self.cache_repo.get_by_category(cat_key, limit=limit)
        return [
            NewsItem(
                title=c.title,
                source=c.source,
                url=c.url,
                category=c.category,
                summary=c.summary,
                published_at=c.published_at,
            )
            for c in cached
        ]

    def search_news(self, query: str, limit: int = 10) -> List[NewsItem]:
        all_news = self.get_headlines("Technology", limit=15) + self.get_headlines("World", limit=15)
        q_lower = query.lower()
        matches = [a for a in all_news if q_lower in a.title.lower() or q_lower in a.summary.lower()]
        return matches[:limit]

    def _match_category(self, cat: str) -> str:
        c_lower = cat.lower()
        if "tech" in c_lower:
            return "Technology"
        if "ai" in c_lower or "artificial" in c_lower or "machine learning" in c_lower:
            return "Artificial Intelligence"
        if "india" in c_lower:
            return "India"
        if "business" in c_lower or "finance" in c_lower:
            return "Business"
        if "world" in c_lower or "global" in c_lower:
            return "World"
        return "Technology"


_news_provider_instance: Optional[RSSNewsProvider] = None


def get_news_provider() -> RSSNewsProvider:
    global _news_provider_instance
    if _news_provider_instance is None:
        _news_provider_instance = RSSNewsProvider()
    return _news_provider_instance


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
