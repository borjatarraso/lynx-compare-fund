"""About metadata tests."""

from __future__ import annotations

from lynx_compare_fund import SUITE_LABEL, __author__, __version__


def test_version_is_set():
    assert __version__


def test_author_is_borja():
    assert "Borja Tarraso" in __author__


def test_suite_label():
    assert SUITE_LABEL.startswith("Lince Investor Suite")


def test_about_text():
    from lynx_compare_fund.about import get_about_text
    t = get_about_text()
    assert t["name"] == "Lynx Compare Fund"
    desc = t["description"]
    assert "ETF" in desc or "Exchange-Traded" in desc
