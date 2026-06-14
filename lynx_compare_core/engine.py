"""Fund comparison engine.

Takes two ``FundReport`` objects (produced by ``lynx_fund.core.analyzer``)
and produces a side-by-side comparison: per-metric winners, per-section
winners, and an overall winner.

Sections:
    Costs               — TER, spread, estimated $ cost
    Income              — yield, SEC yield, policy
    Size & Liquidity    — AUM, volume, fund age, spread
    Performance         — 1Y/3Y/5Y returns, Sharpe, Sortino, CAGR
    Diversification     — holdings count, top-10 concentration, sector HHI
    Risk                — volatility, drawdown, beta
    Tracking            — tracking error, tracking difference, R²
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from lynx_fund.models import FundReport


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MetricResult:
    key: str
    label: str
    value_a: Any
    value_b: Any
    winner: str
    fmt_a: str = ""
    fmt_b: str = ""


@dataclass
class SectionResult:
    name: str
    metrics: list[MetricResult] = field(default_factory=list)
    wins_a: int = 0
    wins_b: int = 0
    ties: int = 0
    winner: str = "tie"


@dataclass
class Warning:
    level: str
    message: str


@dataclass
class ComparisonResult:
    ticker_a: str
    ticker_b: str
    name_a: str = ""
    name_b: str = ""
    aum_a: Optional[float] = None
    aum_b: Optional[float] = None
    tier_a: str = ""
    tier_b: str = ""
    asset_class_a: str = ""
    asset_class_b: str = ""
    domicile_a: str = ""
    domicile_b: str = ""
    sections: list[SectionResult] = field(default_factory=list)
    warnings: list[Warning] = field(default_factory=list)
    total_wins_a: int = 0
    total_wins_b: int = 0
    total_ties: int = 0
    sections_won_a: int = 0
    sections_won_b: int = 0
    sections_tied: int = 0
    overall_winner: str = "tie"
    holdings_overlap_pct: Optional[float] = None
    # ── Passive-investor head-to-head scorecard ─────────────────────────
    passive_pass_a: int = 0
    passive_warn_a: int = 0
    passive_fail_a: int = 0
    passive_pass_b: int = 0
    passive_warn_b: int = 0
    passive_fail_b: int = 0
    passive_winner: str = "tie"        # which fund the checklist favours
    passive_summary: str = ""           # human-readable head-to-head note

    @property
    def winner_ticker(self) -> str:
        if self.overall_winner == "a":
            return self.ticker_a
        if self.overall_winner == "b":
            return self.ticker_b
        return "tie"


# ---------------------------------------------------------------------------
# Metric direction catalogue
# ---------------------------------------------------------------------------

_METRIC_DIRECTION = {
    # Costs — lower is better
    "expense_ratio": "lower",
    "management_fee": "lower",
    "performance_fee": "lower",
    "spread_bps": "lower",
    "median_spread_30d_bps": "lower",
    "estimated_cost_10k_year1": "lower",
    "estimated_cost_10k_year10": "lower",
    "portfolio_turnover_pct": "lower",
    "total_cost_of_ownership_bps": "lower",
    "creation_fee_bps": "lower",
    "redemption_fee_bps": "lower",
    # Income — higher yield wins; tax efficiency higher = better
    "dividend_yield": "higher",
    "sec_yield_30d": "higher",
    "distribution_frequency": "info",
    "distribution_policy": "info",
    "qualified_dividend_pct": "higher",
    "cap_gain_distributions_3y_avg": "lower",
    "tax_efficiency_score": "higher",
    # Liquidity
    "aum": "higher",
    "avg_volume": "higher",
    "avg_dollar_volume": "higher",
    "fund_age_years": "higher",
    "shares_outstanding": "higher",
    "premium_discount_pct": "abs_lower",
    "median_premium_discount_1y": "abs_lower",
    "max_premium_1y": "abs_lower",
    "max_discount_1y": "abs_lower",
    "mean_abs_deviation_1y": "lower",
    "net_flows_1y": "higher",
    "authorised_participants": "higher",
    # Performance
    "return_1m": "higher",
    "return_3m": "higher",
    "return_ytd": "higher",
    "return_1y": "higher",
    "return_3y": "higher",
    "return_5y": "higher",
    "return_10y": "higher",
    "cagr_since_inception": "higher",
    "sharpe_1y": "higher",
    "sharpe_3y": "higher",
    "sortino_3y": "higher",
    "calmar_3y": "higher",
    "info_ratio_3y": "higher",
    "treynor_3y": "higher",
    "up_capture_3y": "higher",
    "down_capture_3y": "lower",   # less drawdown vs benchmark = better
    "best_quarter": "higher",
    "worst_quarter": "higher",    # worst is negative; closer to 0 = "higher"
    "recovery_days_from_max_dd": "lower",
    # Diversification
    "holdings_count": "higher",
    "effective_holdings": "higher",
    "top1_concentration": "lower",
    "top5_concentration": "lower",
    "top10_concentration": "lower",
    "top25_concentration": "lower",
    "herfindahl_sector": "lower",
    "herfindahl_holdings": "lower",
    "sector_count": "higher",
    "country_count": "higher",
    # Bond-specific (info-only — different fund objectives, not winners)
    "duration_years": "info",
    "yield_to_maturity": "info",
    "avg_credit_rating": "info",
    # Risk
    "volatility_1y": "lower",
    "volatility_3y": "lower",
    "max_drawdown_3y": "higher",  # drawdowns are negative; closer to 0 = higher
    "beta_3y": "beta",
    "beta_vs_benchmark": "beta",
    "correlation_sp500_3y": "info",
    "tracking_error": "lower",
    "tracking_difference": "abs_lower",
    "r_squared": "higher",
    "downside_deviation_3y": "lower",
    # Tail risk — VaR/CVaR are negative; "higher" = less negative = better
    "var_95_1y": "higher",
    "cvar_95_1y": "higher",
    "skewness_3y": "info",      # interpretation depends on portfolio
    "kurtosis_3y": "lower",     # fatter tails worse for buy-and-hold
}

_INFO_ONLY = {
    "distribution_frequency",
    "distribution_policy",
    "duration_years",
    "yield_to_maturity",
    "avg_credit_rating",
    "correlation_sp500_3y",
    "skewness_3y",
}


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _fmt_pct(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{v*100:.2f}%"
    except Exception:
        return str(v)


def _fmt_num(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{v:.2f}"
    except Exception:
        return str(v)


def _fmt_money(v) -> str:
    if v is None:
        return "—"
    try:
        a = abs(v)
        if a >= 1e12:
            return f"${v/1e12:.2f}T"
        if a >= 1e9:
            return f"${v/1e9:.2f}B"
        if a >= 1e6:
            return f"${v/1e6:.2f}M"
        return f"${v:,.0f}"
    except Exception:
        return str(v)


def _fmt_int(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{int(v):,}"
    except Exception:
        return str(v)


def _fmt_bps(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{v:.1f} bps"
    except Exception:
        return str(v)


def _fmt_years(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{v:.1f} yr"
    except Exception:
        return str(v)


def _fmt_string(v) -> str:
    return "—" if v is None else str(v)


_FORMATTERS = {
    "expense_ratio": _fmt_pct,
    "management_fee": _fmt_pct,
    "performance_fee": _fmt_pct,
    "spread_bps": _fmt_bps,
    "median_spread_30d_bps": _fmt_bps,
    "estimated_cost_10k_year1": lambda v: ("—" if v is None else f"${v:.2f}"),
    "estimated_cost_10k_year10": lambda v: ("—" if v is None else f"${v:.2f}"),
    "portfolio_turnover_pct": _fmt_pct,
    "total_cost_of_ownership_bps": _fmt_bps,
    "creation_fee_bps": _fmt_bps,
    "redemption_fee_bps": _fmt_bps,
    "dividend_yield": _fmt_pct,
    "sec_yield_30d": _fmt_pct,
    "distribution_frequency": _fmt_string,
    "distribution_policy": _fmt_string,
    "qualified_dividend_pct": _fmt_pct,
    "cap_gain_distributions_3y_avg": _fmt_pct,
    "tax_efficiency_score": _fmt_num,
    "aum": _fmt_money,
    "avg_volume": _fmt_int,
    "avg_dollar_volume": _fmt_money,
    "fund_age_years": _fmt_years,
    "shares_outstanding": _fmt_int,
    "premium_discount_pct": _fmt_pct,
    "median_premium_discount_1y": _fmt_pct,
    "max_premium_1y": _fmt_pct,
    "max_discount_1y": _fmt_pct,
    "mean_abs_deviation_1y": _fmt_pct,
    "net_flows_1y": _fmt_money,
    "authorised_participants": _fmt_int,
    "return_1m": _fmt_pct,
    "return_3m": _fmt_pct,
    "return_ytd": _fmt_pct,
    "return_1y": _fmt_pct,
    "return_3y": _fmt_pct,
    "return_5y": _fmt_pct,
    "return_10y": _fmt_pct,
    "cagr_since_inception": _fmt_pct,
    "sharpe_1y": _fmt_num,
    "sharpe_3y": _fmt_num,
    "sortino_3y": _fmt_num,
    "calmar_3y": _fmt_num,
    "info_ratio_3y": _fmt_num,
    "treynor_3y": _fmt_num,
    "up_capture_3y": _fmt_num,
    "down_capture_3y": _fmt_num,
    "best_quarter": _fmt_pct,
    "worst_quarter": _fmt_pct,
    "recovery_days_from_max_dd": (
        lambda v: "—" if v is None else f"{int(v):,} days"
    ),
    "holdings_count": _fmt_int,
    "effective_holdings": _fmt_num,
    "top1_concentration": _fmt_pct,
    "top5_concentration": _fmt_pct,
    "top10_concentration": _fmt_pct,
    "top25_concentration": _fmt_pct,
    "herfindahl_sector": _fmt_num,
    "herfindahl_holdings": _fmt_num,
    "sector_count": _fmt_int,
    "country_count": _fmt_int,
    "duration_years": _fmt_years,
    "yield_to_maturity": _fmt_pct,
    "avg_credit_rating": _fmt_string,
    "volatility_1y": _fmt_pct,
    "volatility_3y": _fmt_pct,
    "max_drawdown_3y": _fmt_pct,
    "beta_3y": _fmt_num,
    "beta_vs_benchmark": _fmt_num,
    "correlation_sp500_3y": _fmt_num,
    "tracking_error": _fmt_pct,
    "tracking_difference": _fmt_pct,
    "r_squared": _fmt_num,
    "downside_deviation_3y": _fmt_pct,
    "var_95_1y": _fmt_pct,
    "cvar_95_1y": _fmt_pct,
    "skewness_3y": _fmt_num,
    "kurtosis_3y": _fmt_num,
}


# ---------------------------------------------------------------------------
# Core comparison logic
# ---------------------------------------------------------------------------

def _compare_metric(key: str, a: Any, b: Any) -> str:
    if key in _INFO_ONLY:
        return "na"
    if a is None and b is None:
        return "na"
    if a is None:
        return "b"
    if b is None:
        return "a"

    direction = _METRIC_DIRECTION.get(key, "higher")
    if direction == "info":
        return "na"

    try:
        fa = float(a)
        fb = float(b)
    except (TypeError, ValueError):
        if str(a) == str(b):
            return "tie"
        return "na"

    if abs(fa - fb) < 1e-12:
        return "tie"
    if direction == "higher":
        return "a" if fa > fb else "b"
    if direction == "lower":
        return "a" if fa < fb else "b"
    if direction == "abs_lower":
        return "a" if abs(fa) < abs(fb) else "b"
    if direction == "beta":
        return "a" if abs(fa - 1.0) < abs(fb - 1.0) else "b"
    return "a" if fa > fb else "b"


def _format(key: str, v: Any) -> str:
    fmt = _FORMATTERS.get(key, _fmt_num)
    return fmt(v)


def _build_metric(key: str, label: str, va: Any, vb: Any) -> MetricResult:
    winner = _compare_metric(key, va, vb)
    return MetricResult(
        key=key, label=label,
        value_a=va, value_b=vb,
        winner=winner,
        fmt_a=_format(key, va),
        fmt_b=_format(key, vb),
    )


def _section(name: str, metrics: list[MetricResult]) -> SectionResult:
    wa = sum(1 for m in metrics if m.winner == "a")
    wb = sum(1 for m in metrics if m.winner == "b")
    ties = sum(1 for m in metrics if m.winner == "tie")
    if wa > wb:
        winner = "a"
    elif wb > wa:
        winner = "b"
    else:
        winner = "tie"
    return SectionResult(name=name, metrics=metrics,
                        wins_a=wa, wins_b=wb, ties=ties, winner=winner)


def _get(obj, attr, default=None):
    if obj is None:
        return default
    return getattr(obj, attr, default)


def _costs_section(a: FundReport, b: FundReport) -> SectionResult:
    ca, cb = a.costs, b.costs
    return _section("Costs", [
        _build_metric("expense_ratio", "Expense Ratio (TER)",
                      _get(ca, "expense_ratio"), _get(cb, "expense_ratio")),
        _build_metric("management_fee", "Management Fee",
                      _get(ca, "management_fee"), _get(cb, "management_fee")),
        _build_metric("performance_fee", "Performance Fee",
                      _get(ca, "performance_fee"), _get(cb, "performance_fee")),
        _build_metric("spread_bps", "Bid-Ask Spread (1d)",
                      _get(ca, "spread_bps"), _get(cb, "spread_bps")),
        _build_metric("median_spread_30d_bps", "Bid-Ask Spread (30d med)",
                      _get(ca, "median_spread_30d_bps"),
                      _get(cb, "median_spread_30d_bps")),
        _build_metric("portfolio_turnover_pct", "Portfolio Turnover",
                      _get(ca, "portfolio_turnover_pct"),
                      _get(cb, "portfolio_turnover_pct")),
        _build_metric("total_cost_of_ownership_bps", "Total Cost of Ownership",
                      _get(ca, "total_cost_of_ownership_bps"),
                      _get(cb, "total_cost_of_ownership_bps")),
        _build_metric("estimated_cost_10k_year1", "Est. $ cost / $10k / 1y",
                      _get(ca, "estimated_cost_10k_year1"),
                      _get(cb, "estimated_cost_10k_year1")),
        _build_metric("estimated_cost_10k_year10", "Est. $ cost / $10k / 10y",
                      _get(ca, "estimated_cost_10k_year10"),
                      _get(cb, "estimated_cost_10k_year10")),
    ])


def _income_section(a: FundReport, b: FundReport) -> SectionResult:
    ia, ib = a.income, b.income
    return _section("Income", [
        _build_metric("dividend_yield", "Dividend Yield (TTM)",
                      _get(ia, "dividend_yield"), _get(ib, "dividend_yield")),
        _build_metric("sec_yield_30d", "SEC 30-day Yield",
                      _get(ia, "sec_yield_30d"), _get(ib, "sec_yield_30d")),
        _build_metric("distribution_frequency", "Distribution Frequency",
                      _get(ia, "distribution_frequency"), _get(ib, "distribution_frequency")),
        _build_metric("distribution_policy", "Distribution Policy",
                      _get(ia, "distribution_policy"), _get(ib, "distribution_policy")),
        _build_metric("qualified_dividend_pct", "Qualified Dividends",
                      _get(ia, "qualified_dividend_pct"),
                      _get(ib, "qualified_dividend_pct")),
        _build_metric("cap_gain_distributions_3y_avg", "Cap-Gain Distributions (3Y avg)",
                      _get(ia, "cap_gain_distributions_3y_avg"),
                      _get(ib, "cap_gain_distributions_3y_avg")),
        _build_metric("tax_efficiency_score", "Tax Efficiency Score",
                      _get(ia, "tax_efficiency_score"),
                      _get(ib, "tax_efficiency_score")),
    ])


def _liquidity_section(a: FundReport, b: FundReport) -> SectionResult:
    la, lb = a.liquidity, b.liquidity
    return _section("Size & Liquidity", [
        _build_metric("aum", "AUM", _get(la, "aum"), _get(lb, "aum")),
        _build_metric("avg_volume", "Avg Daily Volume",
                      _get(la, "avg_volume"), _get(lb, "avg_volume")),
        _build_metric("avg_dollar_volume", "Avg Daily $ Volume",
                      _get(la, "avg_dollar_volume"), _get(lb, "avg_dollar_volume")),
        _build_metric("fund_age_years", "Fund Age",
                      _get(la, "fund_age_years"), _get(lb, "fund_age_years")),
        _build_metric("shares_outstanding", "Shares Outstanding",
                      _get(la, "shares_outstanding"), _get(lb, "shares_outstanding")),
        _build_metric("premium_discount_pct", "Premium / Discount (spot)",
                      _get(la, "premium_discount_pct"),
                      _get(lb, "premium_discount_pct")),
        _build_metric("median_premium_discount_1y", "Median Prem/Disc (1Y)",
                      _get(la, "median_premium_discount_1y"),
                      _get(lb, "median_premium_discount_1y")),
        _build_metric("mean_abs_deviation_1y", "Mean |Prem/Disc| (1Y)",
                      _get(la, "mean_abs_deviation_1y"),
                      _get(lb, "mean_abs_deviation_1y")),
        _build_metric("authorised_participants", "Authorised Participants",
                      _get(la, "authorised_participants"),
                      _get(lb, "authorised_participants")),
        _build_metric("net_flows_1y", "Net Flows (1Y)",
                      _get(la, "net_flows_1y"), _get(lb, "net_flows_1y")),
    ])


def _performance_section(a: FundReport, b: FundReport) -> SectionResult:
    pa, pb = a.performance, b.performance
    return _section("Performance", [
        _build_metric("return_1m", "1M Return", _get(pa, "return_1m"), _get(pb, "return_1m")),
        _build_metric("return_3m", "3M Return", _get(pa, "return_3m"), _get(pb, "return_3m")),
        _build_metric("return_ytd", "YTD Return", _get(pa, "return_ytd"), _get(pb, "return_ytd")),
        _build_metric("return_1y", "1Y Return", _get(pa, "return_1y"), _get(pb, "return_1y")),
        _build_metric("return_3y", "3Y CAGR", _get(pa, "return_3y"), _get(pb, "return_3y")),
        _build_metric("return_5y", "5Y CAGR", _get(pa, "return_5y"), _get(pb, "return_5y")),
        _build_metric("return_10y", "10Y CAGR", _get(pa, "return_10y"), _get(pb, "return_10y")),
        _build_metric("sharpe_1y", "Sharpe (1Y)", _get(pa, "sharpe_1y"), _get(pb, "sharpe_1y")),
        _build_metric("sharpe_3y", "Sharpe (3Y)", _get(pa, "sharpe_3y"), _get(pb, "sharpe_3y")),
        _build_metric("sortino_3y", "Sortino (3Y)", _get(pa, "sortino_3y"), _get(pb, "sortino_3y")),
    ])


def _diversification_section(a: FundReport, b: FundReport) -> SectionResult:
    aa, ab = a.allocation, b.allocation
    return _section("Diversification", [
        _build_metric("holdings_count", "Holdings Count",
                      _get(aa, "holdings_count"), _get(ab, "holdings_count")),
        _build_metric("effective_holdings", "Effective Holdings (1/HHI)",
                      _get(aa, "effective_holdings"), _get(ab, "effective_holdings")),
        _build_metric("top1_concentration", "Top-1 Concentration",
                      _get(aa, "top1_concentration"), _get(ab, "top1_concentration")),
        _build_metric("top5_concentration", "Top-5 Concentration",
                      _get(aa, "top5_concentration"), _get(ab, "top5_concentration")),
        _build_metric("top10_concentration", "Top-10 Concentration",
                      _get(aa, "top10_concentration"), _get(ab, "top10_concentration")),
        _build_metric("top25_concentration", "Top-25 Concentration",
                      _get(aa, "top25_concentration"), _get(ab, "top25_concentration")),
        _build_metric("herfindahl_sector", "Sector HHI",
                      _get(aa, "herfindahl_sector"), _get(ab, "herfindahl_sector")),
        _build_metric("herfindahl_holdings", "Holdings HHI",
                      _get(aa, "herfindahl_holdings"), _get(ab, "herfindahl_holdings")),
        _build_metric("sector_count", "Sector Count",
                      _get(aa, "sector_count"), _get(ab, "sector_count")),
        _build_metric("country_count", "Country Count",
                      _get(aa, "country_count"), _get(ab, "country_count")),
    ])


def _risk_section(a: FundReport, b: FundReport) -> SectionResult:
    ra, rb = a.risk, b.risk
    return _section("Risk", [
        _build_metric("volatility_1y", "Volatility (1Y)",
                      _get(ra, "volatility_1y"), _get(rb, "volatility_1y")),
        _build_metric("volatility_3y", "Volatility (3Y)",
                      _get(ra, "volatility_3y"), _get(rb, "volatility_3y")),
        _build_metric("downside_deviation_3y", "Downside Deviation (3Y)",
                      _get(ra, "downside_deviation_3y"),
                      _get(rb, "downside_deviation_3y")),
        _build_metric("max_drawdown_3y", "Max Drawdown (3Y)",
                      _get(ra, "max_drawdown_3y"), _get(rb, "max_drawdown_3y")),
        _build_metric("beta_3y", "Beta (3Y)",
                      _get(ra, "beta_3y"), _get(rb, "beta_3y")),
    ])


def _capture_section(a: FundReport, b: FundReport) -> SectionResult:
    pa, pb = a.performance, b.performance
    return _section("Capture & Recovery", [
        _build_metric("up_capture_3y", "Up Capture (3Y)",
                      _get(pa, "up_capture_3y"), _get(pb, "up_capture_3y")),
        _build_metric("down_capture_3y", "Down Capture (3Y)",
                      _get(pa, "down_capture_3y"), _get(pb, "down_capture_3y")),
        _build_metric("calmar_3y", "Calmar (3Y)",
                      _get(pa, "calmar_3y"), _get(pb, "calmar_3y")),
        _build_metric("info_ratio_3y", "Information Ratio (3Y)",
                      _get(pa, "info_ratio_3y"), _get(pb, "info_ratio_3y")),
        _build_metric("treynor_3y", "Treynor (3Y)",
                      _get(pa, "treynor_3y"), _get(pb, "treynor_3y")),
        _build_metric("best_quarter", "Best Quarter",
                      _get(pa, "best_quarter"), _get(pb, "best_quarter")),
        _build_metric("worst_quarter", "Worst Quarter",
                      _get(pa, "worst_quarter"), _get(pb, "worst_quarter")),
        _build_metric("recovery_days_from_max_dd", "Recovery Days from Max DD",
                      _get(pa, "recovery_days_from_max_dd"),
                      _get(pb, "recovery_days_from_max_dd")),
    ])


def _tail_risk_section(a: FundReport, b: FundReport) -> SectionResult:
    ra, rb = a.risk, b.risk
    return _section("Tail Risk", [
        _build_metric("var_95_1y", "VaR (1d, 95%)",
                      _get(ra, "var_95_1y"), _get(rb, "var_95_1y")),
        _build_metric("cvar_95_1y", "CVaR / Expected Shortfall (95%)",
                      _get(ra, "cvar_95_1y"), _get(rb, "cvar_95_1y")),
        _build_metric("skewness_3y", "Skewness (3Y)",
                      _get(ra, "skewness_3y"), _get(rb, "skewness_3y")),
        _build_metric("kurtosis_3y", "Excess Kurtosis (3Y)",
                      _get(ra, "kurtosis_3y"), _get(rb, "kurtosis_3y")),
    ])


def _tracking_section(a: FundReport, b: FundReport) -> SectionResult:
    ra, rb = a.risk, b.risk
    return _section("Tracking", [
        _build_metric("tracking_error", "Tracking Error",
                      _get(ra, "tracking_error"), _get(rb, "tracking_error")),
        _build_metric("tracking_difference", "Tracking Difference",
                      _get(ra, "tracking_difference"), _get(rb, "tracking_difference")),
        _build_metric("r_squared", "R² vs benchmark",
                      _get(ra, "r_squared"), _get(rb, "r_squared")),
    ])


# ---------------------------------------------------------------------------
# Holdings overlap
# ---------------------------------------------------------------------------

def holdings_overlap(a: FundReport, b: FundReport) -> Optional[float]:
    """Approximate holdings overlap (0..1) using sum of minimum weights.

    Uses holding.symbol where present, else holding.name. Returns None
    if either side has no usable holdings.
    """
    ha = {(_symbol(h)): (h.weight or 0) for h in (a.holdings or []) if _symbol(h)}
    hb = {(_symbol(h)): (h.weight or 0) for h in (b.holdings or []) if _symbol(h)}
    if not ha or not hb:
        return None
    common = set(ha) & set(hb)
    return float(sum(min(ha[s], hb[s]) for s in common))


def _symbol(h) -> str:
    return (getattr(h, "symbol", None) or getattr(h, "name", "") or "").upper()


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def _warnings_for(a: FundReport, b: FundReport) -> list[Warning]:
    out: list[Warning] = []
    pa, pb = a.profile, b.profile

    if pa.asset_class and pb.asset_class and pa.asset_class != pb.asset_class:
        out.append(Warning(
            level="asset_class",
            message=(
                f"Asset-class mismatch: {pa.ticker} is {pa.asset_class}, "
                f"{pb.ticker} is {pb.asset_class}. Not an apples-to-apples comparison."
            ),
        ))
    if pa.domicile and pb.domicile and pa.domicile != pb.domicile:
        out.append(Warning(
            level="domicile",
            message=(
                f"Domicile mismatch: {pa.ticker} in {pa.domicile}, "
                f"{pb.ticker} in {pb.domicile}. Tax treatment differs."
            ),
        ))
    # ── Active vs Index style mismatch (fund-specific) ──────────────────
    if (pa.is_index_fund is not None and pb.is_index_fund is not None
            and pa.is_index_fund != pb.is_index_fund):
        idx, act = (pa.ticker, pb.ticker) if pa.is_index_fund else (pb.ticker, pa.ticker)
        out.append(Warning(
            level="style",
            message=(
                f"Active-vs-passive mismatch: {idx} is an index fund, "
                f"{act} is actively managed. Different cost / tax / persistence profiles."
            ),
        ))
    # ── Tier mismatch (informational) ───────────────────────────────────
    if pa.tier != pb.tier:
        out.append(Warning(
            level="tier",
            message=(
                f"Size-tier mismatch: {pa.ticker} is {pa.tier.value}, "
                f"{pb.ticker} is {pb.tier.value}."
            ),
        ))
    # ── UCITS / EU eligibility ──────────────────────────────────────────
    if pa.ucits is not None and pb.ucits is not None and pa.ucits != pb.ucits:
        eu_yes, eu_no = (pa.ticker, pb.ticker) if pa.ucits else (pb.ticker, pa.ticker)
        out.append(Warning(
            level="ucits",
            message=(
                f"UCITS mismatch: {eu_yes} is UCITS-compliant, {eu_no} is not. "
                "EU retail brokers may refuse the non-UCITS leg."
            ),
        ))
    # ── Open / soft-closed / hard-closed mismatch ───────────────────────
    if pa.hard_closed != pb.hard_closed and (pa.hard_closed or pb.hard_closed):
        closed, open_ = (pa.ticker, pb.ticker) if pa.hard_closed else (pb.ticker, pa.ticker)
        out.append(Warning(
            level="closure",
            message=(
                f"Subscription mismatch: {closed} is hard-closed, "
                f"{open_} is open. New investors can only buy the open one."
            ),
        ))
    elif pa.soft_closed != pb.soft_closed and (pa.soft_closed or pb.soft_closed):
        soft, open_ = (pa.ticker, pb.ticker) if pa.soft_closed else (pb.ticker, pa.ticker)
        out.append(Warning(
            level="closure",
            message=(
                f"Subscription mismatch: {soft} is soft-closed (existing holders only), "
                f"{open_} is open."
            ),
        ))
    # ── Distribution policy (Acc vs Dist) ───────────────────────────────
    pol_a = (pa.distribution_policy or "").lower()
    pol_b = (pb.distribution_policy or "").lower()
    pol_kind = lambda p: ("acc" if "accum" in p else "dist" if "distribut" in p else "")
    ka, kb = pol_kind(pol_a), pol_kind(pol_b)
    if ka and kb and ka != kb:
        out.append(Warning(
            level="distribution",
            message=(
                f"Distribution mismatch: {pa.ticker} is {pa.distribution_policy}, "
                f"{pb.ticker} is {pb.distribution_policy}. "
                "Accumulating compounds inside the fund; Distributing pays cash."
            ),
        ))
    return out


def _passive_scorecard(a: FundReport, b: FundReport) -> tuple[
    int, int, int, int, int, int, str, str
]:
    """Run the passive checklist for both funds and return per-fund counts.

    Returns ``(pass_a, warn_a, fail_a, pass_b, warn_b, fail_b,
    winner, summary)``. *winner* is "a", "b", or "tie".
    """
    try:
        from lynx_fund.passive_checklist import run_passive_checklist, summarize_status
    except ImportError:
        return (0, 0, 0, 0, 0, 0, "tie", "")

    list_a = a.passive_checklist or run_passive_checklist(a)
    list_b = b.passive_checklist or run_passive_checklist(b)
    sa = summarize_status(list_a)
    sb = summarize_status(list_b)

    # A fund "wins" the passive scorecard if it has more passes and no more fails.
    pa = sa.get("pass", 0); pb = sb.get("pass", 0)
    fa = sa.get("fail", 0); fb = sb.get("fail", 0)

    if fa < fb or (fa == fb and pa > pb):
        winner = "a"
    elif fb < fa or (fb == fa and pb > pa):
        winner = "b"
    else:
        winner = "tie"

    summary = (
        f"{a.profile.ticker}: {pa}✓ {sa.get('warn',0)}⚠ {fa}✘   "
        f"vs   "
        f"{b.profile.ticker}: {pb}✓ {sb.get('warn',0)}⚠ {fb}✘"
    )

    return (
        pa, sa.get("warn", 0), fa,
        pb, sb.get("warn", 0), fb,
        winner, summary,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compare(a: FundReport, b: FundReport) -> ComparisonResult:
    """Diff two fund reports and return a fully-populated ComparisonResult."""
    sections = [
        _costs_section(a, b),
        _income_section(a, b),
        _liquidity_section(a, b),
        _performance_section(a, b),
        _capture_section(a, b),
        _diversification_section(a, b),
        _risk_section(a, b),
        _tail_risk_section(a, b),
        _tracking_section(a, b),
    ]

    total_a = sum(s.wins_a for s in sections)
    total_b = sum(s.wins_b for s in sections)
    total_ties = sum(s.ties for s in sections)

    sections_a = sum(1 for s in sections if s.winner == "a")
    sections_b = sum(1 for s in sections if s.winner == "b")
    sections_tied = sum(1 for s in sections if s.winner == "tie")

    if sections_a > sections_b:
        overall = "a"
    elif sections_b > sections_a:
        overall = "b"
    elif total_a > total_b:
        overall = "a"
    elif total_b > total_a:
        overall = "b"
    else:
        overall = "tie"

    pa, wa, fa, pb, wb, fb, passive_winner, passive_summary = _passive_scorecard(a, b)

    return ComparisonResult(
        ticker_a=a.profile.ticker,
        ticker_b=b.profile.ticker,
        name_a=a.profile.name or "",
        name_b=b.profile.name or "",
        aum_a=a.profile.aum,
        aum_b=b.profile.aum,
        tier_a=a.profile.tier.value if a.profile.tier else "",
        tier_b=b.profile.tier.value if b.profile.tier else "",
        asset_class_a=a.profile.asset_class or "",
        asset_class_b=b.profile.asset_class or "",
        domicile_a=a.profile.domicile or "",
        domicile_b=b.profile.domicile or "",
        sections=sections,
        warnings=_warnings_for(a, b),
        total_wins_a=total_a,
        total_wins_b=total_b,
        total_ties=total_ties,
        sections_won_a=sections_a,
        sections_won_b=sections_b,
        sections_tied=sections_tied,
        overall_winner=overall,
        holdings_overlap_pct=holdings_overlap(a, b),
        passive_pass_a=pa, passive_warn_a=wa, passive_fail_a=fa,
        passive_pass_b=pb, passive_warn_b=wb, passive_fail_b=fb,
        passive_winner=passive_winner,
        passive_summary=passive_summary,
    )
