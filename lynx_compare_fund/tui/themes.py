"""Custom Textual themes for the lynx-compare-fund TUI.

Re-exports the house :class:`lynx-dark` / :class:`lynx-light` themes
from :mod:`lynx_fund.tui.themes` so the compare-etf TUI matches the rest
of the Suite without duplicating constants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from lynx_fund.tui.themes import (
    HOUSE_THEMES,
    LYNX_DARK,
    LYNX_LIGHT,
    THEME_NAMES,
    register_all_themes,
)

if TYPE_CHECKING:  # pragma: no cover
    from textual.app import App


__all__ = [
    "HOUSE_THEMES",
    "LYNX_DARK",
    "LYNX_LIGHT",
    "THEME_NAMES",
    "register_all_themes",
]
