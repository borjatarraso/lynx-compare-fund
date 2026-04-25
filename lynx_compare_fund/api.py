"""Public API for lynx-compare-fund.

Stable functions and types for scripts and other tools to call.

Example
-------
>>> from lynx_fund.core.storage import set_mode
>>> set_mode("production")
>>> from lynx_compare_fund.api import compare_funds
>>> result = compare_funds("VTI", "ITOT")
>>> result.winner_ticker
'VTI'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from lynx_compare_fund.engine import ComparisonResult, compare
from lynx_fund.core.analyzer import run_full_analysis
from lynx_fund.models import FundReport


def compare_funds(ticker_a: str, ticker_b: str, *,
                 refresh: bool = False) -> ComparisonResult:
    """Fetch both ETFs (using the current storage mode) and compare them."""
    report_a = run_full_analysis(ticker_a, refresh=refresh, download_news=False)
    report_b = run_full_analysis(ticker_b, refresh=refresh, download_news=False)
    return compare(report_a, report_b)


def compare_reports(a: FundReport, b: FundReport) -> ComparisonResult:
    """Compare two already-fetched :class:`FundReport` objects."""
    return compare(a, b)


@dataclass
class ComparisonView:
    """Light wrapper around :class:`ComparisonResult` for display helpers."""
    result: ComparisonResult

    @property
    def sections(self):
        return self.result.sections

    @property
    def winner(self) -> str:
        return self.result.winner_ticker

    def section_named(self, name: str):
        for s in self.result.sections:
            if s.name.lower() == name.lower():
                return s
        return None

    def summary(self) -> dict:
        r = self.result
        return {
            "ticker_a": r.ticker_a, "ticker_b": r.ticker_b,
            "name_a": r.name_a, "name_b": r.name_b,
            "overall_winner": r.overall_winner,
            "winner_ticker": r.winner_ticker,
            "sections_won_a": r.sections_won_a,
            "sections_won_b": r.sections_won_b,
            "sections_tied": r.sections_tied,
            "total_wins_a": r.total_wins_a,
            "total_wins_b": r.total_wins_b,
            "total_ties": r.total_ties,
            "warnings": [{"level": w.level, "message": w.message} for w in r.warnings],
            "holdings_overlap_pct": r.holdings_overlap_pct,
        }
