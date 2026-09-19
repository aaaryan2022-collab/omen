# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Safe Browser Automation, Search, and URL Navigation.
"""

import webbrowser
import urllib.parse
from typing import Optional, Dict, Any, List
import requests
from pydantic import BaseModel, Field
import re
from tools.base import BaseTool, ToolResult
from safety.safety import sanitize_external_content
from app.constants import RiskLevel
from app.logging_config import logger


class LaunchUrlArgs(BaseModel):
    url: str = Field(description="Web URL to open in browser (e.g. 'https://youtube.com', 'https://github.com')")


class WebSearchArgs(BaseModel):
    query: str = Field(description="Search term or phrase to query on the web")
    open_in_browser: bool = Field(default=False, description="Whether to also open search results in user browser")


class ReadWebpageArgs(BaseModel):
    url: str = Field(description="URL of the webpage to scrape and summarize")


class LaunchUrlTool(BaseTool):
    name = "launch_url"
    description = "Opens a website URL in the user's default web browser."
    risk_level = RiskLevel.LOW
    args_schema = LaunchUrlArgs

    def execute(self, url: str, **kwargs) -> ToolResult:
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        try:
            webbrowser.open(url)
            return ToolResult(
                success=True,
                data={"url": url},
                message=f"Opened {url} in web browser."
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to open URL: {url}")


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Searches the web for information and returns relevant snippets."
    risk_level = RiskLevel.LOW
    args_schema = WebSearchArgs

    def execute(self, query: str, open_in_browser: bool = False, **kwargs) -> ToolResult:
        encoded = urllib.parse.quote(query)
        browser_url = f"https://www.google.com/search?q={encoded}"

        if open_in_browser:
            webbrowser.open(browser_url)

        # Query DuckDuckGo Instant Answer API for quick factual search
        try:
            ddg_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            res = requests.get(ddg_url, timeout=8, headers={"User-Agent": "OMEN-Assistant/1.0"})
            if res.status_code == 200:
                data = res.json()
                abstract = data.get("AbstractText", "")
                heading = data.get("Heading", "")
                related = [t.get("Text") for t in data.get("RelatedTopics", []) if "Text" in t][:4]

                summary_parts = []
                if heading and abstract:
                    summary_parts.append(f"**{heading}**: {abstract}")
                elif abstract:
                    summary_parts.append(abstract)

                if related:
                    summary_parts.append("\n**Related Info:**\n" + "\n".join([f"- {r}" for r in related]))

                if summary_parts:
                    content = "\n\n".join(summary_parts)
                    sanitized = sanitize_external_content(content, source_type="Web Search")
                    return ToolResult(
                        success=True,
                        data={"query": query, "abstract": abstract, "related": related},
                        message=sanitized
                    )
        except Exception as e:
            logger.debug(f"Instant search API fallback: {e}")

        # Fallback response
        msg = f"Web search initiated for '{query}'.\nSearch link: {browser_url}"
        return ToolResult(success=True, data={"query": query, "url": browser_url}, message=msg)


class ReadWebpageTool(BaseTool):
    name = "read_webpage"
    description = "Fetches and extracts readable text from a webpage."
    risk_level = RiskLevel.LOW
    args_schema = ReadWebpageArgs

    def execute(self, url: str, **kwargs) -> ToolResult:
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OMEN/1.0"})
            if res.status_code != 200:
                return ToolResult(success=False, error=f"HTTP {res.status_code} returned from {url}")

            # Basic HTML text cleaner
            html = res.text
            # Remove scripts, styles
            clean = re.sub(r"<(script|style).*?>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            clean = re.sub(r"<[^>]+>", " ", clean)
            # Normalize whitespace
            clean = re.sub(r"\s+", " ", clean).strip()
            preview = clean[:3000]

            sanitized = sanitize_external_content(preview, source_type=f"Webpage ({url})")
            return ToolResult(
                success=True,
                data={"url": url, "text_sample": preview},
                message=sanitized
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to fetch webpage: {url}")


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
