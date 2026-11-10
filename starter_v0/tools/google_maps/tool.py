from __future__ import annotations

from urllib.parse import urlencode


def google_maps(place: str) -> dict[str, str]:
    """Build a Google Maps search URL from a place name or address."""
    if not isinstance(place, str) or not place.strip():
        return {"error": "invalid_input", "message": "Provide a place name or address."}

    place = " ".join(place.split())
    query = urlencode({"api": 1, "query": place})
    url = f"https://www.google.com/maps/search/?{query}"
    if len(url) > 2048:
        return {"error": "invalid_input", "message": "Use a shorter place name or address."}
    return {"place": place, "url": url}
