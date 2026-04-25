"""Shared test fixtures for fund comparison tests."""

from __future__ import annotations

import pytest

from lynx_fund.models import (
    AllocationMetrics,
    CostMetrics,
    FundProfile,
    FundReport,
    FundSizeTier,
    Holding,
    IncomeMetrics,
    LiquidityMetrics,
    PerformanceMetrics,
    RiskProfile,
)


def _report(ticker: str, **overrides) -> FundReport:
    defaults = dict(
        name=f"{ticker} Fund",
        aum=10e9,
        tier=FundSizeTier.LARGE,
        asset_class="Equity",
        domicile="US",
        fund_type="Mutual Fund",
        is_index_fund=True,
        expense_ratio=0.0005,
        dividend_yield=0.015,
        fund_age_years=10.0,
        return_1y=0.15,
        return_3y=0.1,
        return_5y=0.12,
        sharpe_3y=0.75,
        holdings_count=500,
        top10_concentration=0.25,
        herfindahl_sector=0.15,
        sector_count=11,
        country_count=1,
        volatility_3y=0.16,
        max_drawdown_3y=-0.22,
        beta_3y=1.0,
        tracking_error=0.0005,
        tracking_difference=-0.0003,
        r_squared=0.99,
    )
    defaults.update(overrides)

    profile = FundProfile(
        ticker=ticker,
        name=defaults["name"],
        aum=defaults["aum"],
        tier=defaults["tier"],
        asset_class=defaults["asset_class"],
        domicile=defaults["domicile"],
        fund_type=defaults["fund_type"],
        is_index_fund=defaults["is_index_fund"],
    )
    return FundReport(
        profile=profile,
        costs=CostMetrics(expense_ratio=defaults["expense_ratio"]),
        income=IncomeMetrics(dividend_yield=defaults["dividend_yield"]),
        liquidity=LiquidityMetrics(
            aum=defaults["aum"],
            fund_age_years=defaults["fund_age_years"],
        ),
        performance=PerformanceMetrics(
            return_1y=defaults["return_1y"],
            return_3y=defaults["return_3y"],
            return_5y=defaults["return_5y"],
            sharpe_3y=defaults["sharpe_3y"],
        ),
        allocation=AllocationMetrics(
            holdings_count=defaults["holdings_count"],
            top10_concentration=defaults["top10_concentration"],
            herfindahl_sector=defaults["herfindahl_sector"],
            sector_count=defaults["sector_count"],
            country_count=defaults["country_count"],
        ),
        risk=RiskProfile(
            volatility_3y=defaults["volatility_3y"],
            max_drawdown_3y=defaults["max_drawdown_3y"],
            beta_3y=defaults["beta_3y"],
            tracking_error=defaults["tracking_error"],
            tracking_difference=defaults["tracking_difference"],
            r_squared=defaults["r_squared"],
        ),
        holdings=[Holding(symbol="AAPL", weight=0.07), Holding(symbol="MSFT", weight=0.06)],
    )


@pytest.fixture
def report_vti() -> FundReport:
    return _report(
        "VFIAX", aum=400e9, expense_ratio=0.0004,
        fund_age_years=23.0, holdings_count=500,
        top10_concentration=0.32, return_3y=0.115, return_5y=0.122,
        tier=FundSizeTier.MEGA,
    )


@pytest.fixture
def report_itot() -> FundReport:
    return _report(
        "FXAIX", aum=300e9, expense_ratio=0.00015,
        fund_age_years=35.0, holdings_count=500,
        top10_concentration=0.32, return_3y=0.107, return_5y=0.118,
        tier=FundSizeTier.MEGA,
    )


@pytest.fixture
def report_bond() -> FundReport:
    return _report(
        "VBTLX", aum=100e9, expense_ratio=0.0005,
        fund_age_years=17.0,
        asset_class="Fixed Income",
        return_1y=0.04, return_3y=0.01, return_5y=0.02,
        volatility_3y=0.06, max_drawdown_3y=-0.15,
        holdings_count=10000,
        tier=FundSizeTier.MEGA,
    )
