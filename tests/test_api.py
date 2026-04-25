"""Public API tests."""

from __future__ import annotations

from lynx_compare_fund.api import ComparisonView, compare_reports


def test_compare_reports_returns_result(report_vti, report_itot):
    r = compare_reports(report_vti, report_itot)
    assert r.ticker_a == "VFIAX"
    assert r.ticker_b == "FXAIX"


def test_comparison_view_summary(report_vti, report_itot):
    r = compare_reports(report_vti, report_itot)
    view = ComparisonView(result=r)
    s = view.summary()
    assert s["ticker_a"] == "VFIAX"
    assert s["ticker_b"] == "FXAIX"
    assert s["winner_ticker"] in {"VFIAX", "FXAIX", "tie"}
    assert isinstance(s["warnings"], list)


def test_section_named(report_vti, report_itot):
    view = ComparisonView(result=compare_reports(report_vti, report_itot))
    assert view.section_named("Costs") is not None
    assert view.section_named("costs") is not None
    assert view.section_named("nonexistent") is None
