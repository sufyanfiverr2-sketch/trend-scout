"""Free, keyless live-web trend fetchers.

Pulls real-time signals from public feeds and APIs so we never have to rely on
paid tools or stale model knowledge:
- Google Trends (daily trending searches for Pakistan / Global)
- Reddit RSS (top posts this week from r/memes, r/wholesomememes, r/Instagrammarketing, r/ProgrammerHumor)
- Social Media Today news RSS (what's changing on Instagram / TikTok)
- Hacker News / Dev.to (only when tech niche is selected)
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

import httpx

UA = {"User-Agent": "TrendScout/1.0 (university society marketing tool)"}
TIMEOUT = 10.0


@dataclass
class TrendSignal:
    source: str
    title: str
    context: str = ""
    url: str = ""


def _strip_tags(html: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", clean).strip()


def fetch_google_trends(geo: str = "PK", limit: int = 6) -> List[TrendSignal]:
    """Daily trending searches from Google Trends RSS."""
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            desc = _strip_tags(item.findtext("description") or "")
            link = (item.findtext("link") or "").strip()
            traffic = ""
            for child in item:
                if child.tag.endswith("approx_traffic"):
                    traffic = child.text or ""
            ctx = f"({traffic} searches) {desc}" if traffic else desc
            if title:
                signals.append(TrendSignal(f"Google Trends ({geo})", title, ctx[:160], link))
    except Exception:
        pass
    return signals


def fetch_reddit_rss(subreddit: str, limit: int = 5) -> List[TrendSignal]:
    """Top posts this week via Reddit's public Atom feed."""
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=week"
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns)[:limit]:
            title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
            link_el = entry.find("atom:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            if title:
                signals.append(TrendSignal(f"r/{subreddit}", title, "", link))
    except Exception:
        pass
    return signals


def fetch_hn_top(limit: int = 5) -> List[TrendSignal]:
    """Top stories on Hacker News via free Algolia API."""
    url = "https://hn.algolia.com/api/v1/search?tags=front_page"
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(headers=UA, timeout=TIMEOUT) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            data = resp.json()
        for hit in data.get("hits", [])[:limit]:
            title = hit.get("title") or ""
            points = hit.get("points") or 0
            comments = hit.get("num_comments") or 0
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if title:
                signals.append(
                    TrendSignal("Hacker News", title, f"{points} pts, {comments} comments", link)
                )
    except Exception:
        pass
    return signals


def fetch_devto_top(limit: int = 5) -> List[TrendSignal]:
    """Trending developer articles this week on Dev.to."""
    url = f"https://dev.to/api/articles?top=7&per_page={limit}"
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(headers=UA, timeout=TIMEOUT) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
        for a in resp.json():
            title = a.get("title") or ""
            tags = ", ".join(a.get("tag_list") or [])
            link = a.get("url") or ""
            reactions = a.get("positive_reactions_count") or 0
            if title:
                signals.append(
                    TrendSignal("Dev.to", title, f"tags: {tags} | {reactions} reactions", link)
                )
    except Exception:
        pass
    return signals


def fetch_social_media_news(limit: int = 4) -> List[TrendSignal]:
    """Latest Instagram/TikTok platform & algorithm updates from Social Media Today."""
    url = "https://www.socialmediatoday.com/feeds/news/"
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = _strip_tags(item.findtext("description") or "")[:140]
            if title:
                signals.append(TrendSignal("Social Media News", title, desc, link))
    except Exception:
        pass
    return signals


def collect_live_signals(region: str = "Pakistan", niche: str = "General / Fun / Non-tech") -> List[TrendSignal]:
    """Gather live signals based on society niche.
    For non-tech/funny, focuses on memes, campus humor, and social trends.
    """
    geo = "PK" if "pak" in region.lower() else "US"
    signals: List[TrendSignal] = []
    signals.extend(fetch_google_trends(geo, limit=6))
    signals.extend(fetch_reddit_rss("Instagrammarketing", limit=3))
    signals.extend(fetch_social_media_news(limit=3))

    is_tech = any(keyword in niche.lower() for keyword in ["tech", "coding", "computing", "ai", "cyber", "robotics"])
    if is_tech:
        signals.extend(fetch_reddit_rss("ProgrammerHumor", limit=5))
        signals.extend(fetch_hn_top(limit=4))
        signals.extend(fetch_devto_top(limit=4))
    else:
        signals.extend(fetch_reddit_rss("memes", limit=5))
        signals.extend(fetch_reddit_rss("wholesomememes", limit=4))

    return signals


def signals_to_prompt(signals: List[TrendSignal]) -> str:
    """Format signals as prompt context so Gemini knows what's happening right now."""
    if not signals:
        return ""
    lines = ["Here are LIVE signals pulled from the web in the last few hours:"]
    for s in signals:
        extra = f" — {s.context}" if s.context else ""
        lines.append(f"- [{s.source}] {s.title}{extra}")
    return "\n".join(lines)
