from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools.format.tool import render_digest
from tools.lookup.tool import web_search


def ai_newsletter(topic: str = "AI", timeframe: str = "day", max_items: int = 5) -> dict[str, Any]:
    """Search for AI news and render a Markdown digest with source links."""
    if not isinstance(topic, str) or not topic.strip():
        return {"error": "invalid_input", "message": "Provide a newsletter topic."}
    if timeframe not in ("day", "week", "month", "year"):
        return {"error": "invalid_input", "message": "Use day, week, month, or year."}
    if type(max_items) is not int or not 1 <= max_items <= 10:
        return {"error": "invalid_input", "message": "max_items must be an integer from 1 to 10."}

    topic = " ".join(topic.split())
    result = web_search(query=topic, topic="news", timeframe=timeframe, max_results=max_items)
    if "error" in result:
        return {"error": result["error"], "message": result["message"]}

    items = []
    seen_urls = set()
    for item in result["items"]:
        url = item.get("url")
        summary = item.get("summary") or item.get("title")
        if not isinstance(url, str) or not isinstance(summary, str) or not summary.strip():
            continue
        try:
            parsed_url = urlsplit(url)
        except ValueError:
            continue
        if parsed_url.scheme not in ("https", "http") or not parsed_url.hostname or url in seen_urls:
            continue
        seen_urls.add(url)
        items.append(item)
        if len(items) == max_items:
            break

    if not items:
        return {"error": "insufficient_evidence", "message": "No news items with usable sources were found."}

    digest = render_digest(items, template="daily_ai_vn", headline=f"Bản tin AI — {topic}")
    return {
        "topic": topic,
        "timeframe": timeframe,
        "markdown": digest["markdown"],
        "item_count": digest["item_count"],
        "items": items,
    }
