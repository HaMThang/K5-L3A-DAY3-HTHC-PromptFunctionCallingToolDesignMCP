import pytest

from tools import TOOL_FUNCTIONS
from tools.ai_newsletter import tool


newsletter = TOOL_FUNCTIONS["ai_newsletter"]


def test_searches_news_and_renders_unique_source_links(monkeypatch):
    def search(**kwargs):
        assert kwargs == {"query": "AI agents", "topic": "news", "timeframe": "week", "max_results": 3}
        item = {"url": "https://example.org/news", "title": "Agent evaluation", "summary": "New benchmark."}
        return {"items": [item, item, {"url": None, "summary": "Missing source"}]}

    monkeypatch.setattr(tool, "web_search", search)
    result = newsletter("  AI agents ", "week", 3)

    assert result["item_count"] == 1
    assert "New benchmark." in result["markdown"]
    assert result["markdown"].count("https://example.org/news") == 1


@pytest.mark.parametrize("args", [("", "day", 5), ("AI", "today", 5), ("AI", "day", True)])
def test_rejects_invalid_arguments(args):
    assert newsletter(*args)["error"] == "invalid_input"


def test_returns_lookup_error(monkeypatch):
    error = {"error": "RuntimeError", "message": "Missing TAVILY_API_KEY env var"}
    monkeypatch.setattr(tool, "web_search", lambda **kwargs: error)

    assert newsletter() == error


def test_reports_no_usable_sources(monkeypatch):
    monkeypatch.setattr(tool, "web_search", lambda **kwargs: {"items": [{"url": "file:///news"}]})

    assert newsletter()["error"] == "insufficient_evidence"
