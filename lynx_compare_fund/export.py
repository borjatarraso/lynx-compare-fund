"""Export helpers for comparison results."""

from __future__ import annotations

import dataclasses
import io
import json

from rich.console import Console

from lynx_compare_fund.display import render_full_comparison
from lynx_compare_fund.engine import ComparisonResult


def to_json(result: ComparisonResult) -> str:
    """Render a :class:`ComparisonResult` to a JSON string."""
    return json.dumps(dataclasses.asdict(result), indent=2, default=str)


def to_text(result: ComparisonResult) -> str:
    """Render to plain text using Rich's file rendering."""
    buf = io.StringIO()
    console = Console(file=buf, width=120, force_terminal=False, record=False)
    render_full_comparison(console, result)
    return buf.getvalue()


def to_html(result: ComparisonResult) -> str:
    """Render to HTML via Rich's html recorder."""
    console = Console(record=True, width=120)
    render_full_comparison(console, result)
    return console.export_html(inline_styles=True, clear=True)


def save(result: ComparisonResult, path: str, format: str = "text") -> str:
    fmt = format.lower()
    if fmt == "json":
        text = to_json(result)
    elif fmt == "html":
        text = to_html(result)
    else:
        text = to_text(result)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
