"""Plugin entry-point tests."""

from __future__ import annotations

from lynx_compare_fund.plugin import register


def test_register_returns_agent():
    a = register()
    assert a.name == "lynx-compare-fund"
    assert a.short_name == "compare-etf"
    assert a.prog_name == "lynx-compare-fund"
    assert a.package_module == "lynx_compare_fund"
    assert "ETF" in a.tagline
