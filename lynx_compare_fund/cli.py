"""Command-line interface for lynx-compare-fund.

Mirrors the flag vocabulary of ``lynx-compare`` (``-p``/``-t``,
``-i``/``-tui``/``-x``, ``--timeout`` / ``--no-reports`` / ``--no-news``
/ ``--export`` / ``--about`` / ``--version``) plus the JSON convenience
flag retained from the previous ETF-only CLI.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Optional

from lynx_compare_fund import SUITE_LABEL, __author__, __version__, __year__


DEFAULT_TIMEOUT = 30


def _ticker_completer(prefix, **kw):
    try:
        from lynx_fund.core.storage import list_cached_tickers
        items = list_cached_tickers() or []
        return [t["ticker"] for t in items if t["ticker"].startswith(prefix.upper())]
    except Exception:
        return []


def _positive_timeout(value: str) -> int:
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value} is not an integer") from exc
    if n < 5:
        raise argparse.ArgumentTypeError(
            f"timeout must be >= 5 seconds (got {n})",
        )
    return n


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lynx-compare-fund",
        description=(
            "Lynx Compare Fund — Side-by-side fund comparison.\n"
            "Produces a per-section and overall winner across Costs, Income,\n"
            "Size & Liquidity, Performance, Diversification, Risk, and\n"
            "Tracking. Stocks, mutual funds, and index funds are rejected at\n"
            "the resolver level.\n\n"
            "One of --production-mode (-p) or --testing-mode (-t) is required\n"
            "for analysis (defaults to production for one-shot commands)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lynx-compare-fund -p VTI ITOT                CLI comparison\n"
            "  lynx-compare-fund -p VOO SPY --refresh        Force fresh data\n"
            "  lynx-compare-fund -t IVV SPY                  Testing mode\n"
            "  lynx-compare-fund -p -i                       Interactive mode\n"
            "  lynx-compare-fund -p -tui                     Textual UI\n"
            "  lynx-compare-fund -p -x                       Graphical UI\n"
            "  lynx-compare-fund -p VTI ITOT --timeout 60    Set 60s timeout\n"
            "  lynx-compare-fund -p VTI ITOT --export r.html Export to HTML\n"
            "  lynx-compare-fund -p VTI ITOT --json          JSON summary\n"
            "  lynx-compare-fund --about                     Developer & license info\n"
        ),
    )

    # --- Execution mode (one required for analysis; --about bypasses) ---
    run_mode = parser.add_mutually_exclusive_group()
    run_mode.add_argument(
        "-p", "--production-mode",
        action="store_const", const="production", dest="run_mode",
        help="Production mode: use cached data from the lynx-fund data/ store",
    )
    run_mode.add_argument(
        "-t", "--testing-mode",
        action="store_const", const="testing", dest="run_mode",
        help="Testing mode: always fetch fresh data (uses data_test/)",
    )

    # --- Positional: two ETFs ---
    a_arg = parser.add_argument("ticker_a", nargs="?",
                                help="First fund ticker or ISIN")
    b_arg = parser.add_argument("ticker_b", nargs="?",
                                help="Second fund ticker or ISIN")
    a_arg.completer = _ticker_completer
    b_arg.completer = _ticker_completer

    # --- Interface mode ---
    ui_mode = parser.add_mutually_exclusive_group()
    ui_mode.add_argument(
        "-i", "--interactive-mode",
        action="store_true", dest="interactive",
        help="Launch the interactive REPL",
    )
    ui_mode.add_argument(
        "-tui", "--tui-mode", "--textual-ui",
        action="store_true", dest="tui",
        help="Launch the Textual terminal UI",
    )
    ui_mode.add_argument(
        "-x", "--graphical-mode", "--gui",
        action="store_true", dest="gui",
        help="Launch the Tkinter graphical UI",
    )

    # --- Data / analysis options ---
    parser.add_argument(
        "--timeout", type=_positive_timeout, default=DEFAULT_TIMEOUT,
        metavar="SECS",
        help=f"Timeout per fund (default: {DEFAULT_TIMEOUT}, min: 5)",
    )
    parser.add_argument(
        "--refresh", action="store_true",
        help="Force fresh data download (ignore cache)",
    )
    parser.add_argument(
        "--no-news", action="store_true",
        help="Skip news fetching",
    )
    parser.add_argument(
        "--no-reports", action="store_true",
        help="Skip ancillary fund reports",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose output",
    )

    # --- Output ---
    parser.add_argument(
        "--json", action="store_true",
        help="Print result as JSON and exit",
    )
    parser.add_argument(
        "--export", metavar="FILE",
        help="Export comparison to file (format from extension: .html, .pdf, .txt)",
    )

    # --- Info ---
    parser.add_argument(
        "--about", action="store_true",
        help="Show developer and license information",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}  |  {SUITE_LABEL}  ({__year__}) by {__author__}",
    )

    # Shared --language flag (us / es / it / de / fr / fa).
    try:
        from lynx_investor_core.translations import add_language_argument
        add_language_argument(parser)
    except ImportError:
        pass

    return parser


# ---------------------------------------------------------------------------
# Timeout-guarded analysis
# ---------------------------------------------------------------------------

class AnalysisTimeoutError(Exception):
    """Raised when a single fund analysis exceeds the configured timeout."""


def _run_etf_analysis(identifier: str, args) -> object:
    """Run a single fund analysis with a timeout guard."""
    from lynx_fund.core.analyzer import run_full_analysis

    def _do():
        return run_full_analysis(
            identifier=identifier,
            download_news=not getattr(args, "no_news", False),
            refresh=getattr(args, "refresh", False),
        )

    timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_do)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeout as exc:
            raise AnalysisTimeoutError(
                f"Analysis for '{identifier}' timed out after {timeout}s. "
                f"The ticker/ISIN may be invalid or the network is slow.\n"
                f"  Tip: use --timeout {timeout * 2} to increase the limit."
            ) from exc


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------

def run_cli(argv: Optional[list] = None) -> int:
    parser = build_parser()
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args(argv)
    try:
        from lynx_investor_core.translations import apply_args as _apply_lang
        _apply_lang(args)
    except ImportError:
        pass

    from rich.console import Console
    errc = Console(stderr=True)

    # --- Standalone About (no mode required) -------------------------------
    if args.about:
        from rich.panel import Panel
        from lynx_compare_fund.about import about_text
        console = Console()
        console.print()
        console.print(Panel(
            about_text(),
            title="[bold cyan]About Lynx Compare Fund[/]",
            border_style="cyan",
            padding=(1, 2),
        ))
        console.print()
        return 0

    # --- Easter egg shortcut: bare trigger word as a ticker ----------------
    from lynx_compare_fund.about import check_easter_egg, easter_egg_text
    candidates = [t for t in (args.ticker_a, args.ticker_b) if t]
    for c in candidates:
        if check_easter_egg(c):
            from rich.panel import Panel
            console = Console()
            console.print()
            console.print(Panel(
                f"[green]{easter_egg_text()}[/]",
                title="[bold yellow]You found it![/]",
                border_style="yellow",
                padding=(0, 2),
            ))
            console.print()
            return 0

    if args.run_mode is None:
        args.run_mode = "production"

    from lynx_fund.core.storage import set_mode
    set_mode(args.run_mode)

    mode_label = (
        "[bold green]PRODUCTION[/]" if args.run_mode == "production"
        else "[bold yellow]TESTING[/]"
    )
    errc.print(f"Mode: {mode_label}  |  Timeout: {args.timeout}s per fund")

    # --- UI dispatch -------------------------------------------------------
    if args.gui:
        from lynx_compare_fund.gui.app import run_gui
        return run_gui(args.ticker_a, args.ticker_b)
    if args.tui:
        from lynx_compare_fund.tui.app import run_tui
        return run_tui(args.ticker_a, args.ticker_b)
    if args.interactive:
        from lynx_compare_fund.interactive import run_interactive
        return run_interactive(args)

    # --- Console mode ------------------------------------------------------
    if not args.ticker_a or not args.ticker_b:
        parser.print_help()
        return 1

    return _cmd_compare(args)


# ---------------------------------------------------------------------------
# Compare command
# ---------------------------------------------------------------------------

def _cmd_compare(args) -> int:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from lynx_compare_fund.engine import compare as engine_compare
    from lynx_compare_fund.display import render_full_comparison
    from lynx_fund.core.ticker import NotAFundError

    console = Console()
    errc = Console(stderr=True)
    a, b = args.ticker_a, args.ticker_b

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=errc,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Analysing {a} (timeout {args.timeout}s)...", total=None,
            )
            report_a = _run_etf_analysis(a, args)
            progress.update(task,
                            description=f"Analysing {b} (timeout {args.timeout}s)...")
            report_b = _run_etf_analysis(b, args)
            progress.update(task, description="Comparing...")

        result = engine_compare(report_a, report_b)
    except NotAFundError as exc:
        errc.print(f"[bold red]{exc}[/]")
        return 2
    except AnalysisTimeoutError as exc:
        errc.print(f"[bold red]Timeout:[/] {exc}")
        return 1
    except ValueError as exc:
        errc.print(f"[bold red]Error:[/] {exc}")
        return 2

    if args.json:
        import json
        from lynx_compare_fund.api import ComparisonView
        print(json.dumps(ComparisonView(result).summary(), indent=2, default=str))
        return 0

    render_full_comparison(console, result)

    if args.export:
        path = _do_export(result, args.export)
        if path:
            errc.print(f"[bold green]Exported to:[/] {path}")
    return 0


def _do_export(result, target: str) -> Optional[str]:
    """Export the comparison rendering. Mirrors lynx-compare's flow."""
    import io as _io
    import os
    from pathlib import Path
    from rich.console import Console
    from lynx_compare_fund.display import render_full_comparison

    fmt_shortcuts = {"html": ".html", "pdf": ".pdf", "text": ".txt", "txt": ".txt"}
    if target in fmt_shortcuts:
        ext = fmt_shortcuts[target]
        path = Path(f"lynx-compare-fund-{result.a.profile.ticker.lower()}-vs-"
                    f"{result.b.profile.ticker.lower()}{ext}")
    else:
        path = Path(target)
        ext = os.path.splitext(target)[1].lower() or ".html"
        if not os.path.splitext(target)[1]:
            path = path.with_suffix(".html")

    from lynx_investor_core.author_footer import text_footer, html_footer

    buf = _io.StringIO()
    render_full_comparison(Console(file=buf, width=120, force_terminal=False), result)
    text = buf.getvalue() + text_footer(SUITE_LABEL)

    fmt = {".html": "html", ".htm": "html", ".pdf": "pdf",
           ".txt": "text"}.get(ext, "html")

    if fmt == "text":
        path.write_text(text, encoding="utf-8")
        return str(path)
    if fmt == "html":
        html = (
            f"<html><head><meta charset='utf-8'>"
            f"<title>Lynx Compare Fund — {result.a.profile.ticker} vs "
            f"{result.b.profile.ticker}</title>"
            f"<style>body{{background:#1e1e2e;color:#cdd6f4;"
            f"font-family:monospace;padding:18px}}pre{{white-space:pre-wrap}}</style>"
            f"</head><body><pre>{text}</pre>"
            f"{html_footer(SUITE_LABEL)}"
            f"</body></html>"
        )
        path.write_text(html, encoding="utf-8")
        return str(path)
    if fmt == "pdf":
        try:
            from weasyprint import HTML  # type: ignore
            html = (f"<html><body><pre style='font-family:monospace;'>{text}"
                    f"</pre>{html_footer(SUITE_LABEL)}</body></html>")
            HTML(string=html).write_pdf(str(path))
            return str(path)
        except ImportError:
            from rich.console import Console as _C
            _C(stderr=True).print(
                "[yellow]PDF export requires weasyprint. Install "
                "lynx-compare-fund[pdf] to enable it.[/]"
            )
            return None
    return None


if __name__ == "__main__":
    sys.exit(run_cli())
