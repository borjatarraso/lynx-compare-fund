"""Export helper tests."""

from __future__ import annotations

import json

from lynx_compare_fund.engine import compare
from lynx_compare_fund.export import to_html, to_json, to_text


def test_to_json_is_parseable(report_vti, report_itot):
    result = compare(report_vti, report_itot)
    payload = to_json(result)
    data = json.loads(payload)
    assert data["ticker_a"] == "VFIAX"
    assert data["ticker_b"] == "FXAIX"


def test_to_text_contains_tickers(report_vti, report_itot):
    result = compare(report_vti, report_itot)
    text = to_text(result)
    assert "VFIAX" in text
    assert "FXAIX" in text


def test_to_html_contains_html_tags(report_vti, report_itot):
    result = compare(report_vti, report_itot)
    html = to_html(result)
    assert "<html" in html.lower()
    assert "VFIAX" in html
