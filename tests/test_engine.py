"""Engine comparison tests."""

from __future__ import annotations

from lynx_compare_fund.engine import (
    _compare_metric,
    compare,
    holdings_overlap,
)


class TestCompareMetric:
    def test_higher_wins(self):
        assert _compare_metric("return_1y", 0.2, 0.1) == "a"
        assert _compare_metric("return_1y", 0.1, 0.2) == "b"

    def test_lower_wins_for_cost(self):
        assert _compare_metric("expense_ratio", 0.0003, 0.001) == "a"

    def test_tie(self):
        assert _compare_metric("return_1y", 0.1, 0.1) == "tie"

    def test_na_both_none(self):
        assert _compare_metric("return_1y", None, None) == "na"

    def test_one_missing_wins_other(self):
        assert _compare_metric("return_1y", None, 0.1) == "b"
        assert _compare_metric("return_1y", 0.1, None) == "a"

    def test_abs_lower(self):
        assert _compare_metric("tracking_difference", 0.0001, -0.0005) == "a"

    def test_beta_closer_to_one(self):
        assert _compare_metric("beta_3y", 1.05, 1.2) == "a"

    def test_info_only_metric_is_na(self):
        assert _compare_metric("distribution_frequency", "Quarterly", "Annual") == "na"


class TestCompareReports:
    def test_sections_present(self, report_vti, report_itot):
        r = compare(report_vti, report_itot)
        names = [s.name for s in r.sections]
        assert "Costs" in names
        assert "Income" in names
        assert "Size & Liquidity" in names
        assert "Performance" in names
        assert "Diversification" in names
        assert "Risk" in names
        assert "Tracking" in names

    def test_overall_winner_picked(self, report_vti, report_itot):
        r = compare(report_vti, report_itot)
        # VTI has bigger AUM, more holdings, better returns → wins overall.
        assert r.overall_winner == "a"
        assert r.winner_ticker == "VFIAX"

    def test_warnings_when_asset_class_differs(self, report_vti, report_bond):
        r = compare(report_vti, report_bond)
        levels = {w.level for w in r.warnings}
        assert "asset_class" in levels

    def test_no_warnings_when_identical_profile(self, report_vti, report_itot):
        r = compare(report_vti, report_itot)
        # Both US-domiciled, both Equity, both Physical, both MEGA tier.
        assert r.warnings == []

    def test_tie_when_reports_equal(self, report_vti):
        r = compare(report_vti, report_vti)
        assert r.overall_winner == "tie"
        for s in r.sections:
            # Every metric compares equal → "tie" or "na" for info-only.
            assert s.wins_a == 0
            assert s.wins_b == 0


class TestHoldingsOverlap:
    def test_identical_holdings(self, report_vti):
        overlap = holdings_overlap(report_vti, report_vti)
        assert overlap == report_vti.holdings[0].weight + report_vti.holdings[1].weight

    def test_empty(self, report_vti):
        from lynx_fund.models import FundReport, FundProfile
        empty = FundReport(profile=FundProfile(ticker="X", name="X"))
        assert holdings_overlap(empty, report_vti) is None
