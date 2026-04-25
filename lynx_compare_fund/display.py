"""Rich console display for fund comparison results.

Mirrors :mod:`lynx_compare.display` so the head-to-head fund comparison
looks indistinguishable in vibe from the equity comparison tool:
* Centered header `Panel` with `◆ LYNX COMPARE FUND ◆` title.
* Comparability warnings rendered as blinking banners.
* Profile card is a `Table(box=DOUBLE_EDGE, border_style="bright_blue")`
  with three columns (A / metric / B).
* Each section is a `Table(box=HEAVY_HEAD, border_style="bright_blue")`
  with five columns (val_a · arrow · metric · arrow · val_b) and a
  per-section result row.
* A `Section Scoreboard` summary table.
* A centered final verdict `Panel` with crown icons.
"""

from __future__ import annotations

from lynx_investor_core.translations import t as _t  # i18n helper

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from lynx_compare_fund import SUITE_LABEL, __version__
from lynx_compare_fund.engine import ComparisonResult, SectionResult, Warning


# ---------------------------------------------------------------------------
# Unicode glyphs and palette (kept aligned with lynx-compare)
# ---------------------------------------------------------------------------
ARROW_WIN_LEFT = "\u25c0\u2501\u2501\u2501"     # ◀━━━
ARROW_WIN_RIGHT = "\u2501\u2501\u2501\u25b6"    # ━━━▶
ARROW_TIE = "\u25c0\u2550\u2550\u25b6"          # ◀══▶
ARROW_NA = "\u2500 \u2500 \u2500"               # ─ ─ ─
TROPHY = "\u2605"                                # ★
CROWN = "\u2654"                                 # ♔
CHECK = "\u2714"                                 # ✔
CROSS = "\u2718"                                 # ✘
DOT = "\u2022"                                   # •
DIAMOND = "\u25c6"                               # ◆
WARN = "\u26a0"                                  # ⚠

C_WIN = "bold green"
C_LOSE = "dim white"
C_TIE = "bold yellow"
C_NA = "dim"
C_HEADER = "bold cyan"
C_METRIC = "white"
C_BORDER = "bright_blue"

# Blink applies to the tag, not the message body — matches lynx-compare.
C_WARN_ASSET = "blink bold red"
C_WARN_DOMICILE = "blink bold #ff8800"
C_WARN_TIER = "blink bold yellow"
C_WARN_REPL = "blink bold yellow"

_WARN_STYLES: dict[str, tuple[str, str]] = {
    "asset_class": (C_WARN_ASSET, "red"),
    "domicile":    (C_WARN_DOMICILE, "#ff8800"),
    "replication": (C_WARN_REPL, "yellow"),
    "tier":        (C_WARN_TIER, "yellow"),
}


def _fmt_money_short(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
    except (TypeError, ValueError):
        return str(val)
    av = abs(v)
    neg = v < 0
    if av >= 1_000_000_000_000:
        s = f"${av / 1_000_000_000_000:,.2f}T"
    elif av >= 1_000_000_000:
        s = f"${av / 1_000_000_000:,.2f}B"
    elif av >= 1_000_000:
        s = f"${av / 1_000_000:,.2f}M"
    else:
        s = f"${av:,.0f}"
    return f"-{s}" if neg else s


# ---------------------------------------------------------------------------
# Value / arrow styling
# ---------------------------------------------------------------------------

def _styled_value(text: str, winner: str, side: str) -> Text:
    """Style a metric value. Always uses a 2-char prefix so columns align."""
    if winner == "na":
        return Text(f"  {text}", style=C_NA)
    if winner == "tie":
        return Text(f"  {text}", style=C_TIE)
    if winner == side:
        return Text(f"{CHECK} {text}", style=C_WIN)
    return Text(f"  {text}", style=C_LOSE)


def _styled_arrow(winner: str) -> Text:
    if winner == "a":
        return Text(f" {ARROW_WIN_LEFT} ", style=C_WIN)
    if winner == "b":
        return Text(f" {ARROW_WIN_RIGHT} ", style=C_WIN)
    if winner == "tie":
        return Text(f" {ARROW_TIE} ", style=C_TIE)
    return Text(f" {ARROW_NA} ", style=C_NA)


def _section_arrow(winner: str, ticker_a: str, ticker_b: str) -> Text:
    t = Text()
    if winner == "a":
        t.append(f" {TROPHY} ", style="bold yellow")
        t.append(f"{ARROW_WIN_LEFT} {ticker_a} ", style=C_WIN)
    elif winner == "b":
        t.append(f" {ticker_b} {ARROW_WIN_RIGHT}", style=C_WIN)
        t.append(f" {TROPHY} ", style="bold yellow")
    else:
        t.append(f" {ARROW_TIE} TIE ", style=C_TIE)
    return t


# ---------------------------------------------------------------------------
# Header banner
# ---------------------------------------------------------------------------

def render_header(console: Console, cr: ComparisonResult) -> None:
    """Centered head-to-head banner — same shape as lynx-compare."""
    inner = Text(justify="center")
    inner.append(f"\n{cr.name_a or cr.ticker_a}", style="bold white")
    inner.append(f"  ({cr.ticker_a})", style="cyan")
    inner.append("     vs     ", style="bold yellow")
    inner.append(f"{cr.name_b or cr.ticker_b}", style="bold white")
    inner.append(f"  ({cr.ticker_b})\n", style="cyan")

    panel = Panel(
        Align.center(inner),
        title=f"[bold cyan]{DIAMOND} LYNX COMPARE FUND {DIAMOND}[/]",
        subtitle="[dim]Side-by-side Exchange-Traded Fund analysis[/]",
        border_style="cyan",
        padding=(0, 4),
    )
    console.print(panel)


# ---------------------------------------------------------------------------
# Comparability warnings
# ---------------------------------------------------------------------------

def render_warnings(console: Console, cr: ComparisonResult) -> None:
    """Render comparability warnings as compact banners.

    The level tag blinks (where the terminal honours it); the message
    body is steady so it remains readable, exactly like lynx-compare.
    """
    if not cr.warnings:
        return
    for w in cr.warnings:
        blink_style, border_color = _WARN_STYLES.get(
            w.level, (C_WARN_TIER, "yellow"),
        )
        steady_style = blink_style.replace("blink ", "")
        tag = w.level.replace("_", " ").upper()
        body = Text(justify="center")
        body.append(f"{WARN} {tag} MISMATCH ", style=blink_style)
        body.append(f" {w.message} ", style=steady_style)
        body.append(f" {tag} MISMATCH {WARN}", style=blink_style)
        console.print(Panel(
            body,
            border_style=border_color,
            padding=(0, 2),
            expand=True,
        ))


# ---------------------------------------------------------------------------
# Profile card (3-column DOUBLE_EDGE table)
# ---------------------------------------------------------------------------

def render_profile(console: Console, cr: ComparisonResult) -> None:
    t = Table(
        box=box.DOUBLE_EDGE,
        border_style=C_BORDER,
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 3),
        title=f"[bold white]{DOT} Fund Profile {DOT}[/]",
        title_style="bold",
    )
    t.add_column(cr.ticker_a, justify="right", ratio=3, style="bold white")
    t.add_column("", justify="center", ratio=2, style="bold cyan")
    t.add_column(cr.ticker_b, justify="left", ratio=3, style="bold white")

    t.add_row(cr.name_a or "—", "Name", cr.name_b or "—")
    t.add_row(cr.tier_a or "—", "Tier", cr.tier_b or "—")
    t.add_row(_fmt_money_short(cr.aum_a), "AUM", _fmt_money_short(cr.aum_b))
    t.add_row(cr.asset_class_a or "—", "Asset Class", cr.asset_class_b or "—")
    t.add_row(cr.domicile_a or "—", "Domicile", cr.domicile_b or "—")
    console.print(t)


# ---------------------------------------------------------------------------
# Section table (5-column HEAVY_HEAD)
# ---------------------------------------------------------------------------

def render_section(section: SectionResult, ticker_a: str,
                   ticker_b: str, *, console: Console) -> None:
    if section.winner == "a":
        badge = f"  [{C_WIN}]{TROPHY} {ticker_a} wins {ARROW_WIN_LEFT}[/]"
    elif section.winner == "b":
        badge = f"  [{C_WIN}]{ARROW_WIN_RIGHT} {ticker_b} wins {TROPHY}[/]"
    else:
        badge = f"  [{C_TIE}]{ARROW_TIE} Tie[/]"

    section_title = f"[bold white]{DOT} {section.name.upper()} {DOT}[/]{badge}"

    t = Table(
        title=section_title,
        box=box.HEAVY_HEAD,
        border_style=C_BORDER,
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 2),
        show_lines=False,
    )
    t.add_column(f"[bold]{ticker_a}[/]", justify="right", ratio=3, no_wrap=True)
    t.add_column("", justify="center", width=8, no_wrap=True)
    t.add_column(_t("metric"), justify="center", ratio=3, no_wrap=True, style="bold")
    t.add_column("", justify="center", width=8, no_wrap=True)
    t.add_column(f"[bold]{ticker_b}[/]", justify="left", ratio=3, no_wrap=True)

    for m in section.metrics:
        val_a = _styled_value(m.fmt_a or "—", m.winner, "a")
        val_b = _styled_value(m.fmt_b or "—", m.winner, "b")
        arrow = _styled_arrow(m.winner)
        if m.winner == "a":
            t.add_row(val_a, arrow, Text(m.label, style=C_METRIC), Text(""), val_b)
        elif m.winner == "b":
            t.add_row(val_a, Text(""), Text(m.label, style=C_METRIC), arrow, val_b)
        elif m.winner == "tie":
            t.add_row(val_a, arrow, Text(m.label, style=C_METRIC), arrow, val_b)
        else:
            t.add_row(
                val_a,
                Text(f" {ARROW_NA} ", style=C_NA),
                Text(m.label, style="dim"),
                Text(f" {ARROW_NA} ", style=C_NA),
                val_b,
            )

    # Section result summary row
    t.add_section()
    score_a = f"{section.wins_a}{CHECK}  {section.wins_b}{CROSS}  {section.ties}{DOT}"
    score_b = f"{section.wins_b}{CHECK}  {section.wins_a}{CROSS}  {section.ties}{DOT}"

    if section.winner == "a":
        t.add_row(
            Text(score_a, style=C_WIN),
            _section_arrow("a", ticker_a, ticker_b),
            Text("SECTION RESULT", style="bold"),
            Text(""),
            Text(score_b, style=C_LOSE),
        )
    elif section.winner == "b":
        t.add_row(
            Text(score_a, style=C_LOSE),
            Text(""),
            Text("SECTION RESULT", style="bold"),
            _section_arrow("b", ticker_a, ticker_b),
            Text(score_b, style=C_WIN),
        )
    else:
        t.add_row(
            Text(score_a, style=C_TIE),
            _section_arrow("tie", ticker_a, ticker_b),
            Text("SECTION RESULT", style="bold"),
            _section_arrow("tie", ticker_a, ticker_b),
            Text(score_b, style=C_TIE),
        )

    console.print(t)
    console.print()


def render_sections(console: Console, cr: ComparisonResult) -> None:
    """Render each section table in turn (back-compat with the test suite)."""
    for section in cr.sections:
        render_section(section, cr.ticker_a, cr.ticker_b, console=console)


# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------

def render_scoreboard(console: Console, cr: ComparisonResult) -> None:
    t = Table(
        box=box.SIMPLE_HEAVY,
        border_style="cyan",
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 2),
        title=f"[bold white]{DOT} Section Scoreboard {DOT}[/]",
    )
    t.add_column("Section", justify="center", ratio=2, style="bold")
    t.add_column(cr.ticker_a, justify="center", ratio=1)
    t.add_column("Winner", justify="center", ratio=1)
    t.add_column(cr.ticker_b, justify="center", ratio=1)

    for s in cr.sections:
        if s.winner == "a":
            winner_cell = Text(f"{ARROW_WIN_LEFT} {cr.ticker_a}", style=C_WIN)
            a_cell = Text(f"{s.wins_a}W", style=C_WIN)
            b_cell = Text(f"{s.wins_b}W", style=C_LOSE)
        elif s.winner == "b":
            winner_cell = Text(f"{cr.ticker_b} {ARROW_WIN_RIGHT}", style=C_WIN)
            a_cell = Text(f"{s.wins_a}W", style=C_LOSE)
            b_cell = Text(f"{s.wins_b}W", style=C_WIN)
        else:
            winner_cell = Text(f"{ARROW_TIE} Tie", style=C_TIE)
            a_cell = Text(f"{s.wins_a}W", style=C_TIE)
            b_cell = Text(f"{s.wins_b}W", style=C_TIE)
        t.add_row(s.name, a_cell, winner_cell, b_cell)

    console.print(t)
    console.print()


# ---------------------------------------------------------------------------
# Overall winner
# ---------------------------------------------------------------------------

def render_overall(console: Console, cr: ComparisonResult) -> None:
    sw_a = f"{cr.sections_won_a:>2}"
    sw_b = f"{cr.sections_won_b:<2}"
    mw_a = f"{cr.total_wins_a:>2}"
    mw_b = f"{cr.total_wins_b:<2}"

    lines = Text(justify="center")
    lines.append("\n")

    lines.append("Sections Won     ", style="bold")
    lines.append(f"{cr.ticker_a} ", style="cyan")
    lines.append(sw_a, style="bold white")
    lines.append("  :  ", style="dim")
    lines.append(sw_b, style="bold white")
    lines.append(f" {cr.ticker_b}", style="cyan")
    if cr.sections_tied:
        lines.append(f"   ({cr.sections_tied} tied)", style="yellow")
    lines.append("\n")

    lines.append("Metric Wins      ", style="bold")
    lines.append(f"{cr.ticker_a} ", style="cyan")
    lines.append(mw_a, style="bold white")
    lines.append("  :  ", style="dim")
    lines.append(mw_b, style="bold white")
    lines.append(f" {cr.ticker_b}", style="cyan")
    if cr.total_ties:
        lines.append(f"   ({cr.total_ties} tied)", style="yellow")
    lines.append("\n")

    if cr.holdings_overlap_pct is not None:
        lines.append("Holdings Overlap ", style="bold")
        lines.append(f"{cr.holdings_overlap_pct * 100:.1f}%",
                     style="bold cyan")
        lines.append("\n")
    lines.append("\n")

    if cr.overall_winner == "a":
        lines.append(
            f"{CROWN}  {ARROW_WIN_LEFT}  OVERALL WINNER:  "
            f"{cr.name_a or cr.ticker_a} ({cr.ticker_a})  {CROWN}",
            style="bold green",
        )
        border = "green"
    elif cr.overall_winner == "b":
        lines.append(
            f"{CROWN}  OVERALL WINNER:  "
            f"{cr.name_b or cr.ticker_b} ({cr.ticker_b})  "
            f"{ARROW_WIN_RIGHT}  {CROWN}",
            style="bold green",
        )
        border = "green"
    else:
        lines.append(f"{ARROW_TIE}  IT'S A TIE  {ARROW_TIE}",
                     style="bold yellow")
        border = "yellow"

    lines.append("\n")

    panel = Panel(
        Align.center(lines),
        title=f"[bold white]{TROPHY} FINAL VERDICT {TROPHY}[/]",
        subtitle="[dim]Overall result across every section[/]",
        border_style=border,
        padding=(1, 4),
    )
    console.print(panel)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_passive_verdict(console: Console, cr: ComparisonResult) -> None:
    """Render the passive-investor head-to-head scorecard.

    Pulls the per-fund pass/warn/fail counts the engine attached to *cr*
    and recommends the better leg for a buy-and-hold investor.
    """
    if (
        cr.passive_pass_a == cr.passive_warn_a == cr.passive_fail_a == 0
        and cr.passive_pass_b == cr.passive_warn_b == cr.passive_fail_b == 0
    ):
        return  # Nothing to show.

    if cr.passive_winner == "a":
        verdict = (
            f"[bold green]{TROPHY} {cr.ticker_a}[/] is the better fit for a "
            "buy-and-hold passive investor."
        )
        border = "green"
    elif cr.passive_winner == "b":
        verdict = (
            f"[bold green]{TROPHY} {cr.ticker_b}[/] is the better fit for a "
            "buy-and-hold passive investor."
        )
        border = "green"
    else:
        verdict = (
            f"[bold yellow]{ARROW_TIE} Both funds score equally[/] on the "
            "passive checklist."
        )
        border = "yellow"

    body = Text(justify="center")
    body.append("\n")
    body.append("Passive-investor checklist  ", style="bold")
    body.append(f"{cr.ticker_a} ", style="cyan")
    body.append(f"{cr.passive_pass_a}", style="bold green")
    body.append("✓ ")
    body.append(f"{cr.passive_warn_a}", style="bold yellow")
    body.append("⚠ ")
    body.append(f"{cr.passive_fail_a}", style="bold red")
    body.append("✘    vs    ")
    body.append(f"{cr.passive_pass_b}", style="bold green")
    body.append("✓ ")
    body.append(f"{cr.passive_warn_b}", style="bold yellow")
    body.append("⚠ ")
    body.append(f"{cr.passive_fail_b}", style="bold red")
    body.append("✘ ")
    body.append(f"{cr.ticker_b}", style="cyan")
    body.append("\n\n")
    body.append_text(Text.from_markup(verdict))
    body.append("\n\n")
    body.append(
        "Based on TER, AUM, fund age, tracking error, spread, top-10 "
        "concentration, holdings count, replication, distribution, "
        "premium/discount, sharpe, max drawdown, leverage, securities "
        "lending and (where present) UCITS.",
        style="dim",
    )

    console.print(Panel(
        Align.center(body),
        title=f"[bold white]{TROPHY} PASSIVE-INVESTOR VERDICT {TROPHY}[/]",
        subtitle="[dim]Boglehead-style buy-and-hold scorecard[/]",
        border_style=border,
        padding=(1, 4),
    ))


def render_full_comparison(console: Console, cr: ComparisonResult) -> None:
    console.print()
    render_header(console, cr)
    console.print()

    render_warnings(console, cr)
    if cr.warnings:
        console.print()

    render_profile(console, cr)
    console.print()

    render_sections(console, cr)
    render_scoreboard(console, cr)
    render_overall(console, cr)
    render_passive_verdict(console, cr)
    console.print()


def render_about(console: Console) -> None:
    """Render the About panel matching lynx-compare's layout."""
    from lynx_compare_fund.about import (
        APP_NAME,
        DEVELOPER,
        DEVELOPER_EMAIL,
        LICENSE_NAME,
        LICENSE_TEXT,
        get_about_text,
        get_logo_ascii,
    )
    about = get_about_text()
    logo = get_logo_ascii()

    console.print()
    if logo:
        console.print(Panel(f"[green]{logo}[/]", border_style="green"))
    console.print(Panel(
        f"[bold blue]{about['name']} v{about['version']}[/]\n"
        f"[dim]Part of {about['suite']} v{about['suite_version']}[/]\n"
        f"[dim]Released {about['year']}[/]\n\n"
        f"[bold]Developed by:[/] {DEVELOPER}\n"
        f"[bold]Contact:[/]      {DEVELOPER_EMAIL}\n"
        f"[bold]License:[/]      {LICENSE_NAME}\n\n"
        f"[dim]{about['description']}[/]",
        title="[bold]About[/]",
        border_style="blue",
    ))
    console.print(Panel(
        LICENSE_TEXT,
        title="[bold]BSD 3-Clause License[/]",
        border_style="dim",
    ))
    console.print()


# Back-compat alias used by the GUI / TUI.
display_comparison = render_full_comparison
