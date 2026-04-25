"""Lynx Compare Fund — Side-by-side Exchange-Traded Fund comparison tool.

Public API
----------
>>> from lynx_fund.core.storage import set_mode
>>> set_mode("production")
>>>
>>> from lynx_compare_fund.api import compare_funds, compare_reports
>>> result = compare_funds("VTI", "ITOT")
>>> result.winner_ticker
'VTI'
"""

__version__ = "6.0.0"
__author__ = "Borja Tarraso <borja.tarraso@member.fsf.org>"
__year__ = "2026"

SUITE_NAME = "Lince Investor Suite"
SUITE_VERSION = "6.0.0"
SUITE_LABEL = f"{SUITE_NAME} v{SUITE_VERSION}"


def __getattr__(name: str):
    """Lazy imports to avoid circular-import issues with cli.py."""
    _api_names = {"compare_funds", "compare_reports", "ComparisonView"}
    _engine_names = {
        "ComparisonResult", "MetricResult", "SectionResult",
        "Warning", "compare",
    }
    if name in _api_names:
        from lynx_compare_fund import api
        return getattr(api, name)
    if name in _engine_names:
        from lynx_compare_fund import engine
        return getattr(engine, name)
    raise AttributeError(f"module 'lynx_compare_fund' has no attribute {name!r}")


__all__ = [
    "compare_funds",
    "compare_reports",
    "ComparisonView",
    "ComparisonResult",
    "MetricResult",
    "SectionResult",
    "Warning",
    "compare",
]
