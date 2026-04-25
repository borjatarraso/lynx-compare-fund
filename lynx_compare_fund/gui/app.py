"""Tkinter GUI for Lynx Compare Fund.

Mirrors the visual identity of ``lynx-compare``: Catppuccin Mocha
palette, splash screen, themed top bar, themed scrolled output, About
dialog with the shared logos, and Suite-wide theme cycling.
"""

from __future__ import annotations

import io
import os
import platform as _plat
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from lynx_compare_fund import SUITE_LABEL, __version__, __year__
from lynx_compare_fund.about import (
    APP_NAME,
    DEVELOPER,
    DEVELOPER_EMAIL,
    LICENSE_NAME,
    get_about_text,
    get_logo_ascii,
)


# ---------------------------------------------------------------------------
# Colour palette (Catppuccin Mocha) — matches lynx-compare.
# ---------------------------------------------------------------------------
BG = "#1e1e2e"
BG_SURFACE = "#242438"
BG_CARD = "#2a2a3d"
BG_INPUT = "#313147"
BG_HOVER = "#3a3a52"
FG = "#cdd6f4"
FG_DIM = "#6c7086"
FG_WIN = "#a6e3a1"
FG_LOSE = "#585b70"
FG_TIE = "#f9e2af"
ACCENT = "#89b4fa"
ACCENT2 = "#cba6f7"
BORDER = "#45475a"
BORDER_LIGHT = "#585b70"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_ACTIVE = "#74c7ec"
BTN_DANGER = "#f38ba8"
BTN_SUBTLE = "#45475a"
BTN_SUBTLE_FG = "#bac2de"
TROPHY_COL = "#f9e2af"
CROWN_COL = "#a6e3a1"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
SPLASH_BG = "#181825"

DIAMOND = "\u25c6"
TROPHY = "\u2605"
CROWN = "\u2654"
BULLET = "\u2022"

if _plat.system() == "Windows":
    _FAMILY = "Segoe UI"
    _MONO = "Consolas"
elif _plat.system() == "Darwin":
    _FAMILY = "Helvetica"
    _MONO = "Menlo"
else:
    _FAMILY = "Noto Sans"
    _MONO = "Noto Sans Mono"

FONT = (_FAMILY, 11)
FONT_BOLD = (_FAMILY, 11, "bold")
FONT_SMALL = (_FAMILY, 10)
FONT_TITLE = (_FAMILY, 18, "bold")
FONT_SECTION = (_FAMILY, 12, "bold")
FONT_SPLASH = (_FAMILY, 28, "bold")
FONT_SPLASH_SUB = (_FAMILY, 12)
FONT_VERDICT = (_FAMILY, 14, "bold")
FONT_BTN = (_FAMILY, 10, "bold")
FONT_MONO = (_MONO, 10)


_IMG_DIR = Path(__file__).resolve().parent.parent / "img"
_LOGO_SM = _IMG_DIR / "logo_sm_quarter_green.png"
_LOGO_MD = _IMG_DIR / "logo_sm_green.png"


# ---------------------------------------------------------------------------
# Splash screen
# ---------------------------------------------------------------------------

class SplashScreen:
    def __init__(self, root: tk.Tk, on_done) -> None:
        self.root = root
        self.on_done = on_done
        self.frame = tk.Frame(root, bg=SPLASH_BG)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame.lift()

        center = tk.Frame(self.frame, bg=SPLASH_BG)
        center.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        tk.Label(center, text=f"{DIAMOND}  {DIAMOND}  {DIAMOND}",
                 font=(_FAMILY, 26), bg=SPLASH_BG, fg=ACCENT).pack(pady=(0, 10))

        tk.Label(center, text="LYNX  COMPARE  FUND", font=FONT_SPLASH,
                 bg=SPLASH_BG, fg=FG).pack(pady=(0, 4))
        tk.Label(center, text="Side-by-side fund comparison",
                 font=FONT_SPLASH_SUB, bg=SPLASH_BG, fg=ACCENT).pack(pady=(0, 24))

        tk.Label(
            center,
            text=f"v{__version__}  {BULLET}  {__year__}  {BULLET}  {DEVELOPER}",
            font=FONT_SMALL, bg=SPLASH_BG, fg=FG_DIM,
        ).pack(pady=(0, 4))
        tk.Label(center, text=SUITE_LABEL, font=FONT_SMALL,
                 bg=SPLASH_BG, fg=FG_DIM).pack(pady=(0, 30))

        self.bar_frame = tk.Frame(center, bg=BORDER, height=3, width=260)
        self.bar_frame.pack(pady=(0, 8))
        self.bar_frame.pack_propagate(False)
        self.bar_fill = tk.Frame(self.bar_frame, bg=ACCENT, height=3, width=0)
        self.bar_fill.place(x=0, y=0, relheight=1)

        self.loading = tk.Label(center, text="Loading...", font=FONT_SMALL,
                                bg=SPLASH_BG, fg=FG_DIM)
        self.loading.pack()

        self._progress = 0
        self._animate()

    def _animate(self) -> None:
        self._progress = min(100, self._progress + 8)
        self.bar_fill.place(x=0, y=0, relheight=1,
                            width=int(260 * self._progress / 100))
        if self._progress >= 100:
            self.root.after(180, self._fade_out)
        else:
            self.root.after(35, self._animate)

    def _fade_out(self) -> None:
        try:
            self.frame.destroy()
        except tk.TclError:
            pass
        if self.on_done:
            self.on_done()


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

def _apply_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Lynx.TButton",
                    background=BTN_BG, foreground=BTN_FG,
                    font=FONT_BTN, borderwidth=0, padding=(12, 6),
                    relief="flat")
    style.map("Lynx.TButton",
              background=[("active", BTN_ACTIVE), ("pressed", BTN_ACTIVE)],
              foreground=[("active", BTN_FG), ("pressed", BTN_FG)])
    style.configure("Subtle.TButton",
                    background=BTN_SUBTLE, foreground=BTN_SUBTLE_FG,
                    font=FONT_BTN, borderwidth=0, padding=(10, 5),
                    relief="flat")
    style.map("Subtle.TButton",
              background=[("active", BORDER_LIGHT), ("pressed", BORDER_LIGHT)],
              foreground=[("active", FG), ("pressed", FG)])
    style.configure("Lynx.TEntry",
                    fieldbackground=BG_INPUT, background=BG_INPUT,
                    foreground=FG, insertcolor=FG, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, padding=4)
    style.configure("Lynx.TFrame", background=BG)
    style.configure("Surface.TFrame", background=BG_SURFACE)
    style.configure("Lynx.TLabel", background=BG, foreground=FG, font=FONT)
    style.configure("Title.TLabel", background=BG, foreground=FG, font=FONT_TITLE)
    style.configure("Sub.TLabel", background=BG, foreground=ACCENT,
                    font=(_FAMILY, 12))
    style.configure("Dim.TLabel", background=BG, foreground=FG_DIM, font=FONT_SMALL)

    root.configure(bg=BG)
    return style


# ---------------------------------------------------------------------------
# Main GUI
# ---------------------------------------------------------------------------

def run_gui(ticker_a: str | None = None, ticker_b: str | None = None,
            args=None) -> int:
    """Launch the Tkinter GUI for Lynx Compare Fund."""
    root = tk.Tk()
    root.title(f"{APP_NAME} v{__version__}")
    root.geometry("1200x780")
    root.minsize(960, 640)

    _apply_style(root)

    try:
        from lynx_investor_core.gui_themes import ThemeCycler, SUITE_GUI_THEMES, apply_theme
        # Register user-saved lynx_theme JSON themes (~/.config/lynx-theme)
        try:
            from lynx_theme.storage import register_user_themes as _reg_user_themes
            _reg_user_themes()
        except Exception:
            pass
        cycler = ThemeCycler(root, start="lynx-theme")
        try:
            apply_theme(root, theme="lynx-theme")
        except Exception:
            pass
    except Exception:
        cycler = None
        SUITE_GUI_THEMES = []

    state = {"busy": False, "q": queue.Queue(), "result": None}

    # ── Menu ────────────────────────────────────────────────────────────
    menubar = tk.Menu(root, bg=BG_SURFACE, fg=FG, activebackground=ACCENT,
                      activeforeground=BTN_FG, tearoff=0)
    file_menu = tk.Menu(menubar, tearoff=0, bg=BG_SURFACE, fg=FG,
                        activebackground=ACCENT, activeforeground=BTN_FG)
    file_menu.add_command(label="About", command=lambda: _show_about_dialog(root))
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit, accelerator="Ctrl+Q")
    menubar.add_cascade(label="File", menu=file_menu)

    theme_menu = tk.Menu(menubar, tearoff=0, bg=BG_SURFACE, fg=FG,
                         activebackground=ACCENT, activeforeground=BTN_FG)
    if cycler is not None:
        for name in (SUITE_GUI_THEMES or []):
            theme_menu.add_command(
                label=name,
                command=lambda n=name: cycler.set(n) if hasattr(cycler, "set") else None,
            )
    menubar.add_cascade(label="Themes", menu=theme_menu)
    root.config(menu=menubar)

    # ── Hero ────────────────────────────────────────────────────────────
    hero = ttk.Frame(root, style="Lynx.TFrame", padding=(16, 14, 16, 8))
    hero.pack(fill=tk.X)

    logo_img = None
    if _LOGO_SM.exists():
        try:
            logo_img = tk.PhotoImage(file=str(_LOGO_SM))
            logo_lbl = tk.Label(hero, image=logo_img, bg=BG, borderwidth=0)
            logo_lbl.image = logo_img
            logo_lbl.pack(side=tk.LEFT, padx=(0, 14))
        except tk.TclError:
            logo_img = None

    titles = ttk.Frame(hero, style="Lynx.TFrame")
    titles.pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(titles, text=f"{TROPHY}  Lynx Compare Fund",
              style="Title.TLabel").pack(anchor=tk.W)
    ttk.Label(titles, text="Head-to-head Exchange-Traded Fund analysis",
              style="Sub.TLabel").pack(anchor=tk.W)
    ttk.Label(titles,
              text=f"v{__version__}  {BULLET}  {SUITE_LABEL}",
              style="Dim.TLabel").pack(anchor=tk.W, pady=(2, 0))

    ttk.Button(hero, text="Quit", style="Subtle.TButton",
               command=root.quit).pack(side=tk.RIGHT, padx=(8, 0))

    # ── Search bar ──────────────────────────────────────────────────────
    bar = ttk.Frame(root, style="Lynx.TFrame", padding=(16, 4, 16, 8))
    bar.pack(fill=tk.X)

    ttk.Label(bar, text="Fund A:", style="Lynx.TLabel").pack(side=tk.LEFT, padx=(0, 4))
    var_a = tk.StringVar(value=ticker_a or "")
    e_a = ttk.Entry(bar, textvariable=var_a, width=14, style="Lynx.TEntry", font=FONT)
    e_a.pack(side=tk.LEFT, padx=(0, 12))

    ttk.Label(bar, text="Fund B:", style="Lynx.TLabel").pack(side=tk.LEFT, padx=(0, 4))
    var_b = tk.StringVar(value=ticker_b or "")
    e_b = ttk.Entry(bar, textvariable=var_b, width=14, style="Lynx.TEntry", font=FONT)
    e_b.pack(side=tk.LEFT, padx=(0, 12))

    cmp_btn = ttk.Button(bar, text="Compare", style="Lynx.TButton")
    cmp_btn.pack(side=tk.LEFT, padx=(0, 4))

    refresh_btn = ttk.Button(bar, text="Refresh", style="Subtle.TButton")
    refresh_btn.pack(side=tk.LEFT, padx=(0, 4))

    export_btn = ttk.Button(bar, text="Export…", style="Subtle.TButton")
    export_btn.pack(side=tk.LEFT, padx=(0, 12))

    status_var = tk.StringVar(value="Ready.")
    status_lbl = tk.Label(bar, textvariable=status_var, bg=BG, fg=FG_DIM,
                          font=FONT_SMALL)
    status_lbl.pack(side=tk.LEFT, padx=(8, 0))

    # ── Output ──────────────────────────────────────────────────────────
    out_wrap = tk.Frame(root, bg=BG)
    out_wrap.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

    out = tk.Text(out_wrap, wrap=tk.WORD, font=FONT_MONO,
                  bg=BG_CARD, fg=FG, insertbackground=FG,
                  selectbackground=ACCENT, selectforeground=BTN_FG,
                  borderwidth=0, padx=14, pady=10)
    sb = ttk.Scrollbar(out_wrap, orient=tk.VERTICAL, command=out.yview)
    out.configure(yscrollcommand=sb.set, state=tk.DISABLED)
    out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    out.tag_configure("ok", foreground=GREEN)
    out.tag_configure("err", foreground=RED)
    out.tag_configure("dim", foreground=FG_DIM)
    out.tag_configure("trophy", foreground=TROPHY_COL)

    welcome = (
        f"{APP_NAME} v{__version__}\n"
        f"{SUITE_LABEL}\n\n"
        "Enter two fund tickers (e.g. VTI and ITOT) and press Compare. "
        "Stocks, mutual funds and index funds are rejected at the resolver "
        "level."
    )

    def _write(text: str, tag: str | None = None) -> None:
        out.configure(state=tk.NORMAL)
        out.delete("1.0", tk.END)
        if tag:
            out.insert(tk.END, text, tag)
        else:
            out.insert(tk.END, text)
        out.configure(state=tk.DISABLED)

    _write(welcome, "dim")

    # ── Compare driver ─────────────────────────────────────────────────
    def _start(refresh: bool = False) -> None:
        a = var_a.get().strip()
        b = var_b.get().strip()
        if not a or not b or state["busy"]:
            return
        state["busy"] = True
        cmp_btn.state(["disabled"])
        refresh_btn.state(["disabled"])
        status_var.set(f"Comparing {a} vs {b}…")
        status_lbl.configure(fg=ACCENT)

        def _worker():
            try:
                from rich.console import Console
                from lynx_compare_fund.engine import compare as engine_compare
                from lynx_compare_fund.display import render_full_comparison
                from lynx_fund.core.analyzer import run_full_analysis
                from lynx_fund.core.ticker import NotAFundError

                try:
                    report_a = run_full_analysis(identifier=a, refresh=refresh)
                    report_b = run_full_analysis(identifier=b, refresh=refresh)
                except NotAFundError as exc:
                    state["q"].put(("error", str(exc)))
                    return
                except ValueError as exc:
                    state["q"].put(("error", str(exc)))
                    return

                result = engine_compare(report_a, report_b)
                buf = io.StringIO()
                console = Console(file=buf, width=120, force_terminal=False)
                render_full_comparison(console, result)
                state["q"].put(("ok", buf.getvalue(), result))
            except Exception as exc:  # noqa: BLE001
                state["q"].put(("error", f"{type(exc).__name__}: {exc}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _drain():
        try:
            while True:
                payload = state["q"].get_nowait()
                kind = payload[0]
                if kind == "ok":
                    text = payload[1]
                    state["result"] = payload[2] if len(payload) > 2 else None
                    _write(text)
                    status_var.set("Done.")
                    status_lbl.configure(fg=GREEN)
                else:
                    _write(f"Error:\n\n{payload[1]}", "err")
                    status_var.set("Error.")
                    status_lbl.configure(fg=RED)
                state["busy"] = False
                cmp_btn.state(["!disabled"])
                refresh_btn.state(["!disabled"])
        except queue.Empty:
            pass
        root.after(120, _drain)

    def _export():
        result = state.get("result")
        if not result:
            messagebox.showinfo("Export", "Run a comparison first.", parent=root)
            return
        path = filedialog.asksaveasfilename(
            parent=root,
            title="Export comparison report",
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("HTML", "*.html"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            from lynx_compare_fund.cli import _do_export
            saved = _do_export(result, path)
            if saved:
                messagebox.showinfo("Export", f"Saved to:\n{saved}", parent=root)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Export", f"Failed: {exc}", parent=root)

    cmp_btn.configure(command=lambda: _start(False))
    refresh_btn.configure(command=lambda: _start(True))
    export_btn.configure(command=_export)
    for w in (e_a, e_b):
        w.bind("<Return>", lambda _e: _start(False))
    root.bind_all("<Control-q>", lambda _e: root.quit())
    root.bind_all("<Control-r>", lambda _e: _start(True))

    def _after_splash():
        e_a.focus_set()
        if ticker_a and ticker_b:
            root.after(150, lambda: _start(False))

    if os.environ.get("LYNX_NO_SPLASH") == "1":
        _after_splash()
    else:
        SplashScreen(root, on_done=_after_splash)

    root.after(120, _drain)
    # Bottom-right language toggle (US/ES/IT/DE/FR/FA).
    try:
        from lynx_investor_core.lang_widget import mount_tk_language_button
        mount_tk_language_button(root)
    except ImportError:
        pass

    root.mainloop()
    return 0


# ---------------------------------------------------------------------------
# About dialog
# ---------------------------------------------------------------------------

def _show_about_dialog(parent: tk.Tk) -> None:
    win = tk.Toplevel(parent)
    win.title(f"About — {APP_NAME}")
    win.configure(bg=BG)
    win.transient(parent)
    win.geometry("680x540")

    about = get_about_text()
    logo_ascii = get_logo_ascii()

    logo_img = None
    if _LOGO_MD.exists():
        try:
            logo_img = tk.PhotoImage(file=str(_LOGO_MD))
            tk.Label(win, image=logo_img, bg=BG, borderwidth=0).pack(pady=(18, 6))
        except tk.TclError:
            logo_img = None

    if not logo_img and logo_ascii:
        tk.Label(win, text=logo_ascii, font=(_MONO, 9),
                 bg=BG, fg=GREEN, justify=tk.LEFT).pack(pady=(18, 6))

    tk.Label(win, text=f"{about['name']} v{about['version']}",
             font=(_FAMILY, 16, "bold"), bg=BG, fg=ACCENT).pack(pady=(6, 0))
    tk.Label(win, text=f"Part of {about['suite']} v{about['suite_version']}",
             font=FONT_SMALL, bg=BG, fg=FG_DIM).pack()
    tk.Label(win, text=f"Released {about['year']}",
             font=FONT_SMALL, bg=BG, fg=FG_DIM).pack(pady=(0, 12))

    info = tk.Frame(win, bg=BG)
    info.pack(padx=24, pady=4, fill=tk.X)
    rows = [
        ("Developed by:", DEVELOPER),
        ("Contact:", DEVELOPER_EMAIL),
        ("License:", LICENSE_NAME),
    ]
    for r, (k, v) in enumerate(rows):
        tk.Label(info, text=k, font=FONT_BOLD, bg=BG, fg=FG, anchor=tk.W).grid(
            row=r, column=0, sticky=tk.W,
        )
        tk.Label(info, text=v, font=FONT, bg=BG, fg=FG, anchor=tk.W).grid(
            row=r, column=1, sticky=tk.W, padx=(8, 0),
        )

    tk.Label(win, text=about["description"], font=FONT_SMALL,
             bg=BG, fg=FG_DIM, wraplength=620, justify=tk.LEFT).pack(
        padx=24, pady=(14, 8), fill=tk.X,
    )

    ttk.Button(win, text="Close", style="Lynx.TButton",
               command=win.destroy).pack(pady=(8, 18))

    if logo_img:
        win._logo_ref = logo_img
    win.bind("<Escape>", lambda _e: win.destroy())
    win.focus_set()


_about = _show_about_dialog
