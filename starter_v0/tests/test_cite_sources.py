from chat import execute_tool_call
from providers.base import ToolCall
from tools.cite_sources.tool import cite_sources


URL = "https://example.org/paper"
CLAIM = {"claim": "Three datasets were used.", "url": URL, "quote": "three datasets"}
SOURCE = {"title": "Evaluation study", "url": URL, "summary": "We evaluated three\ndatasets."}


def test_cites_quote_from_collected_source():
    result = cite_sources([CLAIM], sources=[SOURCE])

    assert result["status"] == "ok"
    assert result["citations"] == [{**CLAIM, "title": "Evaluation study"}]


def test_rejects_url_that_was_not_collected():
    result = cite_sources([{**CLAIM, "url": "https://example.org/other"}], sources=[SOURCE])

    assert result["status"] == "insufficient_evidence"
    assert result["unsupported"][0]["reason"] == "unknown_source"


def test_rejects_quote_missing_from_collected_source():
    result = cite_sources([{**CLAIM, "quote": "five datasets"}], sources=[SOURCE])

    assert result["status"] == "insufficient_evidence"
    assert result["unsupported"][0]["reason"] == "quote_not_found"


def test_rejects_blank_quote():
    assert cite_sources([{**CLAIM, "quote": " "}])["error"] == "invalid_input"


def test_chat_uses_previous_tool_results_instead_of_model_supplied_sources():
    call = ToolCall(name="cite_sources", args={"claims": [CLAIM], "sources": [SOURCE]})
    assert execute_tool_call(call)["result"]["status"] == "insufficient_evidence"

    events = [{"tool": "papers", "result": {"items": [SOURCE]}}]
    assert execute_tool_call(call, events)["result"]["status"] == "ok"
