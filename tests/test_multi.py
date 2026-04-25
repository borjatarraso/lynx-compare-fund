"""N-way comparison tests."""

from __future__ import annotations

from lynx_compare_fund.multi import compare_many_reports, pick_winners, score_for


def test_compare_many_ranks_best_first(report_vti, report_itot, report_bond):
    result = compare_many_reports([report_vti, report_itot, report_bond])
    tickers = [r.ticker for r in result.rankings]
    assert len(tickers) == 3
    # VFIAX or FXAIX should be the winner (both Equity with best return metrics
    # vs the bond ETF). Given VTI has bigger AUM and better returns, it wins.
    assert result.winner in {"VFIAX", "FXAIX"}


def test_fewer_than_two_returns_empty(report_vti):
    result = compare_many_reports([report_vti])
    assert result.rankings == []


def test_pick_winners_returns_dict(report_vti, report_itot):
    winners = pick_winners([report_vti, report_itot])
    assert "expense_ratio" in winners
    assert winners["aum"] == "VFIAX"  # bigger AUM


def test_score_stays_in_bounds(report_vti, report_itot):
    from lynx_compare_fund.multi import _METRIC_DIRECTION, _get
    vals = {
        k: [v for r in [report_vti, report_itot]
            if (v := _get(r, k)) is not None]
        for k in _METRIC_DIRECTION
    }
    normals = {k: (min(v), max(v)) for k, v in vals.items() if v}
    s1 = score_for(report_vti, normals)
    s2 = score_for(report_itot, normals)
    assert 0 <= s1 <= 1
    assert 0 <= s2 <= 1
