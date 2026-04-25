"""Interactive prompt mode for Lynx Compare Fund.

Mirrors :mod:`lynx_compare.interactive` (banner, mode panel, command set
including ``timeout`` / ``about`` / ``export`` / ``help`` / ``quit``,
with the same prompt styling) so users moving between Suite tools have
a consistent experience. Inputs accept fund tickers or ISINs.
"""

from __future__ import annotations

try:
    import readline as _readline  # noqa: F401 — arrow-key history
except ImportError:
    pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from lynx_compare_fund import __version__


console = Console()
errc = Console(stderr=True)


def run_interactive(args) -> int:
    """Run the interactive comparison loop."""
    from lynx_fund.core.storage import is_testing
    from lynx_compare_fund.cli import _run_etf_analysis, AnalysisTimeoutError

    console.print()
    console.print("[bold cyan]LYNX COMPARE FUND[/] -- Interactive Mode")
    console.print(f"[dim]Timeout: {args.timeout}s per fund[/]")
    console.print()

    if is_testing():
        console.print(Panel(
            "[bold yellow]TESTING MODE[/]\n"
            "Data is stored in [bold]data_test/[/] — production data is never touched.\n"
            "All fetches are fresh.",
            border_style="yellow",
        ))
    else:
        console.print(Panel(
            "[bold green]PRODUCTION MODE[/]\n"
            "Data is stored in [bold]data/[/] — cached analyses are reused automatically.",
            border_style="green",
        ))

    console.print()
    console.print("[dim]Commands:[/]")
    console.print("[dim]  Ctrl+C   Abort current / quit[/]")
    console.print("[dim]  quit     Exit the program[/]")
    console.print("[dim]  timeout  Change the timeout (e.g. 'timeout 60')[/]")
    console.print("[dim]  about    Show application info[/]")
    console.print("[dim]  export   Export last comparison (e.g. 'export r.html')[/]")
    console.print("[dim]  help     Show this menu[/]")
    console.print()

    last_result = None

    while True:
        try:
            etf_a = Prompt.ask(
                "[bold]Enter first fund[/] (ticker or ISIN)",
                console=console,
            ).strip()
            if etf_a.lower() in ("quit", "exit", "q"):
                break
            if not etf_a:
                continue
            if etf_a.lower().startswith("timeout"):
                _handle_timeout(etf_a, args)
                continue
            if etf_a.lower() in ("about", "help", "h", "?"):
                if etf_a.lower() == "about":
                    _show_about()
                else:
                    _show_help()
                continue
            if etf_a.lower().startswith("export"):
                _handle_export(etf_a, last_result)
                continue
            from lynx_compare_fund.about import check_easter_egg
            if check_easter_egg(etf_a):
                _show_easter_egg()
                continue

            etf_b = Prompt.ask(
                "[bold]Enter second fund[/] (ticker or ISIN)",
                console=console,
            ).strip()
            if etf_b.lower() in ("quit", "exit", "q"):
                break
            if not etf_b:
                continue
            if etf_b.lower().startswith("timeout"):
                _handle_timeout(etf_b, args)
                continue
            if etf_b.lower() == "about":
                _show_about()
                continue
            if etf_b.lower().startswith("export"):
                _handle_export(etf_b, last_result)
                continue
            if check_easter_egg(etf_b):
                _show_easter_egg()
                continue

            console.print()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=errc,
                transient=True,
            ) as progress:
                task = progress.add_task(
                    f"Analysing {etf_a} (timeout {args.timeout}s)...", total=None,
                )
                report_a = _run_etf_analysis(etf_a, args)
                progress.update(task,
                                description=f"Analysing {etf_b} (timeout {args.timeout}s)...")
                report_b = _run_etf_analysis(etf_b, args)
                progress.update(task, description="Comparing...")

            from lynx_compare_fund.engine import compare as engine_compare
            from lynx_compare_fund.display import render_full_comparison

            result = engine_compare(report_a, report_b)
            last_result = result
            render_full_comparison(console, result)

            console.print()
            console.print(
                "[dim]Type two more tickers to compare again, "
                "'timeout N' to change timeout, 'about' for info, "
                "'export <file>' to save, or 'quit' to exit.[/]"
            )
            console.rule(style="dim")
            console.print()

        except AnalysisTimeoutError as exc:
            console.print(f"[bold red]Timeout:[/] {exc}")
            try:
                new_timeout = IntPrompt.ask(
                    "[bold]Increase timeout?[/] Enter new seconds (or 0 to skip)",
                    default=0, console=console,
                )
                if new_timeout > 0:
                    args.timeout = new_timeout
                    console.print(f"[green]Timeout updated to {new_timeout}s[/]")
            except (KeyboardInterrupt, EOFError):
                pass
            console.print()
        except ValueError as exc:
            console.print(f"[bold red]Error:[/] {exc}")
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/]")
            break

    console.print("[dim]Goodbye.[/]")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handle_timeout(cmd: str, args) -> None:
    parts = cmd.strip().split()
    if len(parts) == 2:
        try:
            val = int(parts[1])
            if val > 0:
                args.timeout = val
                console.print(f"[green]Timeout updated to {val}s[/]")
                return
        except ValueError:
            pass
    console.print(
        f"[dim]Current timeout: {args.timeout}s. Usage: timeout 60[/]"
    )


def _show_help() -> None:
    console.print(Panel(
        "[bold]Commands:[/]\n"
        "  [bold]<ETF_A> ↵ <ETF_B>[/]    Compare two ETFs\n"
        "  [bold]timeout N[/]            Change timeout (seconds)\n"
        "  [bold]about[/]                Show application info\n"
        "  [bold]export <file>[/]        Export last comparison\n"
        "  [bold]help[/]                 Show this menu\n"
        "  [bold]quit[/]                 Exit",
        border_style="cyan",
        title="[bold]Help[/]",
    ))


def _show_about() -> None:
    from lynx_compare_fund.about import about_text
    console.print()
    console.print(Panel(
        about_text(),
        title="[bold cyan]About Lynx Compare Fund[/]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def _show_easter_egg() -> None:
    from lynx_compare_fund.about import easter_egg_text
    console.print()
    console.print(Panel(
        f"[green]{easter_egg_text()}[/]",
        title="[bold yellow]You found it![/]",
        border_style="yellow",
        padding=(0, 2),
    ))
    console.print()


def _handle_export(cmd: str, last_result) -> None:
    if last_result is None:
        console.print(
            "[yellow]No comparison results to export. Run a comparison first.[/]"
        )
        return

    parts = cmd.strip().split(maxsplit=1)
    arg = parts[1].strip() if len(parts) >= 2 else ""

    if not arg:
        console.print("[yellow]Usage: export <filename> (e.g. export r.html / r.pdf / r.txt)[/]")
        return

    from lynx_compare_fund.cli import _do_export
    path = _do_export(last_result, arg)
    if path:
        console.print(f"[green]Exported to: {path}[/]")
