"""TODO(student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO(student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](
        question="Bạn muốn xem tài khoản nào?",
        response_type="choice",
        options=["sama", "elonmusk"],
    )
    assert result["options"] == ["sama", "elonmusk"]
    assert result["awaiting_user"] is True
    assert result["response_type"] == "choice"


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Tin 1", "url": "https://a.com/1", "section": "A"},
        {"title": "Tin 2", "url": "https://b.com/2", "section": "B"},
        {"title": "Tin 3", "url": "https://a.com/3", "section": "A"},
    ]
    md = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]
    assert md.count("## A") == 1
    assert md.count("## B") == 1



def test_format_thread_numbers_items() -> None:
    items = [{"title": "Tin 1"}, {"title": "Tin 2"}, {"title": "Tin 3"}]
    md = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"]
    parts = md.split("\n\n")
    assert parts[0].startswith("1/")
    assert parts[1].startswith("2/")
    assert parts[2].startswith("3/")



def test_format_empty_items_does_not_crash() -> None:
    assert TOOL_FUNCTIONS["format"](items=None)["item_count"] == 0
    assert TOOL_FUNCTIONS["format"](items=[])["item_count"] == 0



# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Chuẩn bị: key giả + server giả trả lời "ok"
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123")
    calls = fake_http(FakeResponse({"ok": True}))

    # Gọi tool
    result = TOOL_FUNCTIONS["send"](text="Bản tin AI", confirmed=True)

    # Chiều 1: request gửi đi
    assert len(calls) == 1                                  # gửi đúng 1 lần, không gửi trùng
    assert calls[0]["method"] == "POST"
    assert "test-token" in calls[0]["url"]                  # URL có token
    assert calls[0]["json"]["chat_id"] == "-100123"         # gửi đúng channel
    assert calls[0]["json"]["text"] == "Bản tin AI"         # gửi đúng nội dung
    # Chiều 2: kết quả trả về
    assert result["status"] == "sent"



def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))           # KHÔNG setenv, nên thiếu token
    result = TOOL_FUNCTIONS["send"](text="Bản tin AI", confirmed=True)

    assert result["error"] == "RuntimeError"                # trả về dict lỗi, không crash
    assert "TELEGRAM_BOT_TOKEN" in result["message"]        # thông báo nói rõ thiếu gì
    assert calls == []                                      # không có request nào được gửi



# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    TOOL_FUNCTIONS["lookup"](query="AI", timeframe=None)
    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI"



# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nNội dung bài viết",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))
    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://www.example.com/post"
    assert item["source"] == "example.com"                  # tool tự bỏ "www."
    assert item["summary"] == "# Hello\nNội dung bài viết"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))
    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")
    assert len(result["items"][0]["summary"]) == 4000



# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    raw = [{"text": "không có id", "screen_name": "sama"}]                     # 1 item lỗi
    raw += [{"tweet_id": str(i), "text": f"Tweet {i}", "screen_name": "sama"} for i in range(1, 7)]  # 6 item tốt
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"]["screenname"] == "sama"
    assert len(result["items"]) == 3
    assert [it["url"] for it in result["items"]] == [
        "https://x.com/sama/status/1",
        "https://x.com/sama/status/2",
        "https://x.com/sama/status/3",
    ]



def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))
    TOOL_FUNCTIONS["social_search"](query="GPT-5", search_type="Top")
    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "GPT-5", "search_type": "Top"}



# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert TOOL_FUNCTIONS["policy"](query="")["results"] == []
    assert TOOL_FUNCTIONS["policy"](query="   ")["results"] == []



def test_policy_area_filter_only_returns_that_area() -> None:
    result = TOOL_FUNCTIONS["policy"](query="personal data email", policy_area="data_privacy", top_k=5)
    assert len(result["results"]) > 0
    for hit in result["results"]:
        assert hit["policy_area"] == "data_privacy"



def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = TOOL_FUNCTIONS["policy"](query="injection probe citation", policy_area="source_citation", top_k=10)
    probe = [h for h in result["results"] if h["section"] == "Injection probe"]
    assert len(probe) == 1
    hit = probe[0]
    assert any("viral tweet" in line for line in hit["untrusted_text"])
    assert "viral tweet" not in hit["facts"]



# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path() -> None:
    pytest.skip(TODO)


def test_my_new_tool_bad_input_from_model() -> None:
    pytest.skip(TODO)


def test_my_new_tool_failure_returns_error_dict() -> None:
    pytest.skip(TODO)
