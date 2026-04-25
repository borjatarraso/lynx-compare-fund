"""Textual TUI for Lynx Compare Fund.

Mirrors the look-and-feel of ``lynx-compare``: house ``lynx-dark`` /
``lynx-light`` themes plus the full Suite gallery, About modal with the
shared logo, mode-aware sub-title, and ``t`` to cycle themes.
"""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Label, Static

from lynx_compare_fund import SUITE_LABEL, __version__
from lynx_compare_fund.about import APP_NAME, get_about_text, get_logo_ascii
from lynx_compare_fund.tui.themes import THEME_NAMES, register_all_themes


# ---------------------------------------------------------------------------
# About modal
# ---------------------------------------------------------------------------

class AboutModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    DEFAULT_CSS = """
    AboutModal { align: center middle; }
    #about-dialog {
        width: 80%;
        height: 80%;
        max-width: 110;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    #about-title { text-align: center; padding: 1 0; }
    #about-scroll { height: 1fr; padding: 0 1; }
    #about-hint { text-align: center; color: $text-muted; padding-top: 1; }
    """

    def compose(self) -> ComposeResult:
        about = get_about_text()
        logo = get_logo_ascii()
        logo_block = f"[green]{logo}[/]\n\n" if logo else ""
        with Vertical(id="about-dialog"):
            yield Label(f"[bold blue]{about['name']}[/]", id="about-title")
            yield VerticalScroll(
                Static(
                    f"{logo_block}"
                    f"[bold blue]{about['name']} v{about['version']}[/]\n"
                    f"[dim]Part of {about['suite']} v{about['suite_version']}[/]\n"
                    f"[dim]Released {about['year']}[/]\n\n"
                    f"[bold]Developed by:[/] {about['author']}\n"
                    f"[bold]Contact:[/]      {about['email']}\n"
                    f"[bold]License:[/]      {about['license']}\n\n"
                    f"{about['description']}\n\n"
                    f"[bold cyan]BSD 3-Clause License[/]\n"
                    f"[dim]{about['license_text']}[/]",
                    id="about-content",
                ),
                id="about-scroll",
            )
            yield Label("[dim]Press Escape to close[/]", id="about-hint")

    def action_dismiss_modal(self) -> None:
        self.dismiss()


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

class LynxCompareFundApp(App):
    CSS = """
    Screen { background: $background; }
    #top {
        height: 3;
        padding: 0 1;
        background: $surface;
    }
    #top > Static { padding: 1 1 0 1; color: $accent; }
    #output { padding: 1 2; height: 1fr; }
    Input { width: 22%; }
    """

    BINDINGS = [
        Binding("ctrl+l", "clear", "Clear"),
        Binding("a", "about", "About"),
        Binding("t", "cycle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, ticker_a: str | None = None,
                 ticker_b: str | None = None) -> None:
        super().__init__()
        self._ticker_a = ticker_a
        self._ticker_b = ticker_b
        self._theme_idx = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="top"):
            yield Static("[bold]A:[/]")
            yield Input(placeholder="e.g. VTI", id="a")
            yield Static("[bold]B:[/]")
            yield Input(placeholder="e.g. ITOT", id="b")
        with VerticalScroll(id="output"):
            yield Static(
                f"[bold blue]{APP_NAME} v{__version__}[/]\n"
                f"[dim]{SUITE_LABEL}[/]\n\n"
                "Enter two fund tickers and press Enter on either field.\n"
                "[dim]Stocks, mutual funds and index funds are rejected at the resolver level.[/]\n\n"
                "[dim]Keys:  a = About    t = Cycle theme    q = Quit[/]",
                id="body",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"{APP_NAME} v{__version__}"
        self.sub_title = SUITE_LABEL

        try:
            register_all_themes(self)
        except Exception:
            pass

        for preferred in ("lynx-dark", "lynx-theme", "textual-dark"):
            try:
                self.theme = preferred
                if preferred in THEME_NAMES:
                    self._theme_idx = THEME_NAMES.index(preferred)
                break
            except Exception:
                continue

        if self._ticker_a:
            self.query_one("#a", Input).value = self._ticker_a
        if self._ticker_b:
            self.query_one("#b", Input).value = self._ticker_b
        if self._ticker_a and self._ticker_b:
            self.call_later(self._run, self._ticker_a, self._ticker_b)
        self.query_one("#a", Input).focus()

    def action_clear(self) -> None:
        self.query_one("#body", Static).update("[dim]Cleared.[/]")

    def action_about(self) -> None:
        self.push_screen(AboutModal())

    def action_cycle_theme(self) -> None:
        if not THEME_NAMES:
            return
        self._theme_idx = (self._theme_idx + 1) % len(THEME_NAMES)
        name = THEME_NAMES[self._theme_idx]
        try:
            self.theme = name
            self.notify(f"Theme: {name}", timeout=2)
        except Exception:
            pass

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        a = self.query_one("#a", Input).value.strip()
        b = self.query_one("#b", Input).value.strip()
        if not a or not b:
            return
        await self._run(a, b)

    async def _run(self, a: str, b: str) -> None:
        body = self.query_one("#body", Static)
        body.update(f"[cyan]Comparing {a} vs {b}...[/]")

        def _do():
            from lynx_compare_fund.api import compare_funds
            from lynx_compare_fund.display import render_full_comparison
            from lynx_fund.core.ticker import NotAFundError
            console = Console(record=True, width=120)
            try:
                result = compare_funds(a, b)
            except NotAFundError as exc:
                return f"[bold red]{exc}[/]"
            except ValueError as exc:
                return f"[bold red]Error:[/] {exc}"
            render_full_comparison(console, result)
            return console.export_text(clear=True, styles=True)

        text = await self.run_worker(_do, thread=True).wait()
        body.update(Text.from_ansi(text))


def run_tui(ticker_a: str | None = None, ticker_b: str | None = None) -> int:
    app = LynxCompareFundApp(ticker_a=ticker_a, ticker_b=ticker_b)
    app.run()
    return 0
