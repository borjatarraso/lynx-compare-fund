"""N-way fund comparison (3+ funds).

Computes a normalised score per fund across a fixed set of "higher is better"
metrics and ranks them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from lynx_fund.core.analyzer import run_full_analysis
from lynx_fund.models import FundReport


# Metric keys with direction — duplicated intentionally from engine so this
# module is self-contained and can be reasoned about independently.
_METRIC_DIRECTION = {
    "expense_ratio": "lower",
    "spread_bps": "lower",
    "aum": "higher",
    "fund_age_years": "higher",
    "return_3y": "higher",
    "return_5y": "higher",
    "sharpe_3y": "higher",
    "volatility_3y": "lower",
    "max_drawdown_3y": "higher",
    "holdings_count": "higher",
    "top10_concentration": "lower",
}


@dataclass
class MultiRankEntry:
    ticker: str
    name: str
    score: float
    wins: int


@dataclass
class MultiCompareResult:
    rankings: list[MultiRankEntry]

    @property
    def winner(self) -> Optional[str]:
        if not self.rankings:
            return None
        return self.rankings[0].ticker


def _get(report: FundReport, key: str):
    # Flatten access into the same dataclass namespace.
    for attr in ("costs", "income", "liquidity", "performance", "allocation", "risk"):
        section = getattr(report, attr, None)
        if section is None:
            continue
        if hasattr(section, key):
            return getattr(section, key)
    return None


def score_for(report: FundReport, normals: dict[str, tuple[float, float]]) -> float:
    """Score a single fund across all ranked metrics.

    *normals* maps metric_key → (min_value, max_value) for scaling.
    """
    total = 0.0
    count = 0
    for key, direction in _METRIC_DIRECTION.items():
        v = _get(report, key)
        if v is None:
            continue
        lo, hi = normals.get(key, (v, v))
        if hi == lo:
            continue
        scaled = (v - lo) / (hi - lo)
        if direction == "lower":
            scaled = 1 - scaled
        total += max(0.0, min(1.0, scaled))
        count += 1
    return (total / count) if count else 0.0


def pick_winners(reports: list[FundReport]) -> dict[str, str]:
    """Return {metric_key: winning_ticker} for each ranked metric."""
    winners: dict[str, str] = {}
    for key, direction in _METRIC_DIRECTION.items():
        best_ticker = None
        best_value: Optional[float] = None
        for r in reports:
            v = _get(r, key)
            if v is None:
                continue
            if best_value is None:
                best_ticker, best_value = r.profile.ticker, v
                continue
            if direction == "higher" and v > best_value:
                best_ticker, best_value = r.profile.ticker, v
            elif direction == "lower" and v < best_value:
                best_ticker, best_value = r.profile.ticker, v
        if best_ticker is not None:
            winners[key] = best_ticker
    return winners


def compare_many_reports(reports: list[FundReport]) -> MultiCompareResult:
    """Rank many ETFs across a standard metric set."""
    if len(reports) < 2:
        return MultiCompareResult(rankings=[])

    # Build normalisers
    normals: dict[str, tuple[float, float]] = {}
    for key in _METRIC_DIRECTION:
        vals = [
            _get(r, key) for r in reports
            if _get(r, key) is not None
        ]
        if vals:
            normals[key] = (min(vals), max(vals))

    winners = pick_winners(reports)
    win_count: dict[str, int] = {}
    for w in winners.values():
        win_count[w] = win_count.get(w, 0) + 1

    entries = [
        MultiRankEntry(
            ticker=r.profile.ticker,
            name=r.profile.name or "",
            score=score_for(r, normals),
            wins=win_count.get(r.profile.ticker, 0),
        )
        for r in reports
    ]
    entries.sort(key=lambda e: (e.score, e.wins), reverse=True)
    return MultiCompareResult(rankings=entries)


def compare_many(tickers: list[str]) -> MultiCompareResult:
    """Fetch reports for each ticker and rank them."""
    reports = [run_full_analysis(t, download_news=False) for t in tickers]
    return compare_many_reports(reports)
