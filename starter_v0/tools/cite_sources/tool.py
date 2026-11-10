from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def cite_sources(claims: list[dict[str, str]], *, sources: Sequence[dict[str, Any]] = ()) -> dict[str, Any]:
    """Match each requested quote against the collected text at the same URL."""
    if not isinstance(claims, list) or not claims:
        return {"error": "invalid_input", "message": "Provide a non-empty claims list."}

    citations = []
    unsupported = []
    for claim in claims:
        fields = ("claim", "url", "quote")
        if not isinstance(claim, dict) or any(
            not isinstance(claim.get(field), str) or not claim[field].strip()
            for field in fields
        ):
            return {"error": "invalid_input", "message": "Each claim needs claim, url, and quote strings."}

        url = claim["url"].strip()
        quote = " ".join(claim["quote"].split())
        candidates = [source for source in sources if source.get("url") == url]
        for source in candidates:
            summary = source.get("summary")
            if isinstance(summary, str) and quote in " ".join(summary.split()):
                citations.append({
                    "claim": claim["claim"],
                    "title": source.get("title") or url,
                    "url": url,
                    "quote": quote,
                })
                break
        else:
            unsupported.append({
                "claim": claim["claim"],
                "url": url,
                "reason": "quote_not_found" if candidates else "unknown_source",
            })

    return {
        "status": "insufficient_evidence" if unsupported else "ok",
        "citations": citations,
        "unsupported": unsupported,
    }
