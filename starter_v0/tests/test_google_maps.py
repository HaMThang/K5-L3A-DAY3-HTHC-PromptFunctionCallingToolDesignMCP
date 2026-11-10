from urllib.parse import parse_qs, urlsplit

import pytest

from tools import TOOL_FUNCTIONS


def test_google_maps_encodes_a_vietnamese_place_and_address():
    place = "Bảo tàng Lịch sử, TP. Hồ Chí Minh"
    result = TOOL_FUNCTIONS["google_maps"](place)
    url = urlsplit(result["url"])

    assert (url.scheme, url.netloc, url.path) == ("https", "www.google.com", "/maps/search/")
    assert parse_qs(url.query) == {"api": ["1"], "query": [place]}


def test_google_maps_keeps_reserved_characters_inside_the_query():
    result = TOOL_FUNCTIONS["google_maps"]("  Cafe A&B  #2 ")
    assert parse_qs(urlsplit(result["url"]).query) == {"api": ["1"], "query": ["Cafe A&B #2"]}


@pytest.mark.parametrize("place", ["  ", None, "Đ" * 2048])
def test_google_maps_rejects_invalid_input(place):
    assert TOOL_FUNCTIONS["google_maps"](place)["error"] == "invalid_input"
