"""Branding / about metadata for lynx-compare-fund.

Mirrors :mod:`lynx_compare.about` so the user experience is consistent
across the Suite — same logo loader, ``about_lines()`` /
``about_text()`` helpers, and the same easter-egg vocabulary.
"""

from __future__ import annotations

import os

from lynx_compare_fund import (
    SUITE_LABEL,
    SUITE_NAME,
    SUITE_VERSION,
    __author__,
    __version__,
    __year__,
)


# ---------------------------------------------------------------------------
# Developer and license metadata
# ---------------------------------------------------------------------------

APP_NAME = "Lynx Compare Fund"
APP_DESCRIPTION = "Side-by-side fund comparison tool"
DEVELOPER = "Borja Tarraso"
DEVELOPER_EMAIL = "borja.tarraso@member.fsf.org"
LICENSE_NAME = "BSD 3-Clause License"
LICENSE_SPDX = "BSD-3-Clause"


LICENSE_TEXT = f"""\
BSD 3-Clause License

Copyright (c) {__year__}, {DEVELOPER} <{DEVELOPER_EMAIL}>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


# ---------------------------------------------------------------------------
# Logo loading
# ---------------------------------------------------------------------------

def _load_logo() -> str:
    """Load the ASCII logo shipped under ``img/``."""
    logo_path = os.path.join(os.path.dirname(__file__), "img", "logo_ascii.txt")
    try:
        with open(logo_path, encoding="utf-8") as f:
            return f.read().rstrip()
    except OSError:
        return ""


def get_logo_ascii() -> str:
    """Public alias for the ASCII logo, mirroring lynx-fundamental."""
    return _load_logo()


# ---------------------------------------------------------------------------
# Structured & flat About text
# ---------------------------------------------------------------------------

def get_about_text() -> dict:
    """Structured About info — used by GUI / TUI dialogs and tests."""
    return {
        "name": APP_NAME,
        "suite": SUITE_NAME,
        "suite_version": SUITE_VERSION,
        "suite_label": SUITE_LABEL,
        "version": __version__,
        "author": DEVELOPER,
        "email": DEVELOPER_EMAIL,
        "year": __year__,
        "license": LICENSE_SPDX,
        "license_text": LICENSE_TEXT,
        "description": (
            "Side-by-side comparison of two Exchange-Traded Funds. "
            "Computes a winner for every section (Costs, Income, Liquidity, "
            "Performance, Diversification, Risk, Tracking) plus an overall "
            "winner. Stocks, mutual funds and index funds are rejected at the "
            "resolver level.\n\n"
            "Part of the Lince Investor Suite."
        ),
    }


def about_lines() -> list[str]:
    """Return About information as a list of plain-text lines."""
    lines: list[str] = []
    logo = _load_logo()
    if logo:
        lines.append(logo)
        lines.append("")
    lines.extend([
        f"{APP_NAME} v{__version__}",
        f"Part of {SUITE_LABEL}",
        f"{APP_DESCRIPTION}",
        "",
        f"Developer:  {DEVELOPER}",
        f"Email:      {DEVELOPER_EMAIL}",
        f"Year:       {__year__}",
        f"License:    {LICENSE_NAME}",
        "",
        LICENSE_TEXT.rstrip(),
    ])
    return lines


def about_text() -> str:
    """Flat-string About information."""
    return "\n".join(about_lines())


# ---------------------------------------------------------------------------
# Easter egg (same trigger vocabulary as lynx-compare)
# ---------------------------------------------------------------------------

EASTER_EGG_TRIGGERS = {"lynx", "meow", "paw"}

EASTER_EGG_ART = r"""
        /\_/\
       ( o.o )
        > ^ <       _
       /|   |\     | |   _   _ _ __ __  __
      (_|   |_)    | |  | | | | '_ \\ \/ /
        |   |      | |__| |_| | | | |>  <
        |___|      |_____\__, |_| |_/_/\_\
       /     \           |___/
      / LYNX  \    Fund Comparison
     /  COMPARE\   Cost · Performance · Risk
    /___________\
       |  |  |     "Costs eat your alpha —
       |  |  |      know thy expense ratio."
      _|  |  |_
     (_/  |  \_)   -- Happy investing! --
          |
"""


def check_easter_egg(text: str) -> bool:
    """Return True if *text* matches an easter-egg trigger."""
    return text.strip().lower() in EASTER_EGG_TRIGGERS


def easter_egg_text() -> str:
    """Return the ASCII-art easter egg payload."""
    return EASTER_EGG_ART
