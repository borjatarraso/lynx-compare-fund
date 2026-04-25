"""Entry-point registration for the Lince Investor Suite plugin system."""

from __future__ import annotations

from lynx_investor_core.plugins import SectorAgent

from lynx_compare_fund import __version__


def register() -> SectorAgent:
    """Return this tool's descriptor for the plugin registry."""
    return SectorAgent(
        name="lynx-compare-fund",
        short_name="compare-etf",
        sector="Fund Comparison",
        tagline="Side-by-side comparison of two ETFs across every lens",
        prog_name="lynx-compare-fund",
        version=__version__,
        package_module="lynx_compare_fund",
        entry_point_module="lynx_compare_fund.__main__",
        entry_point_function="main",
        icon="\u2696",
    )
