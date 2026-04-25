"""Display rendering smoke tests."""

from __future__ import annotations

import io

from rich.console import Console

from lynx_compare_fund.display import (
    render_about,
    render_full_comparison,
    render_header,
    render_overall,
    render_sections,
    render_warnings,
)
from lynx_compare_fund.engine import compare


def test_render_full_comparison(report_vti, report_itot):
    buf = io.StringIO()
    console = Console(file=buf, width=140, force_terminal=False)
    result = compare(report_vti, report_itot)
    render_full_comparison(console, result)
    out = buf.getvalue()
    assert "VFIAX" in out
    assert "FXAIX" in out
    assert "Costs" in out
    assert "Performance" in out


def test_render_warnings_when_present(report_vti, report_bond):
    buf = io.StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    render_warnings(console, compare(report_vti, report_bond))
    out = buf.getvalue()
    assert "MISMATCH" in out or "mismatch" in out.lower()


def test_render_overall_identifies_winner(report_vti, report_itot):
    buf = io.StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    render_overall(console, compare(report_vti, report_itot))
    out = buf.getvalue()
    assert "Overall" in out


def test_render_about():
    buf = io.StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    render_about(console)
    out = buf.getvalue()
    assert "Lynx Compare Fund" in out
