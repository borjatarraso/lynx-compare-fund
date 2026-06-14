# CLAUDE.md — lynx_compare_ui

## Responsibility (narrow)

Everything a **person** interacts with. Takes a `ComparisonResult` from
`lynx_compare_core` and presents it; parses CLI args and orchestrates a
run. No comparison math lives here, and no HTTP.

## Modules

- `cli.py` — argparse front end and run orchestration (`build_parser`,
  `run_cli`, `_run_etf_analysis`, `_do_export`, `AnalysisTimeoutError`).
- `display.py` — Rich renderer (`render_full_comparison` and the
  `render_*` section helpers).
- `interactive.py` — prompt-driven REPL (`run_interactive`).
- `about.py` — branding/license metadata + ASCII logo loader + easter egg.
- `tui/` — Textual terminal UI (`tui/app.py:run_tui`, `tui/themes.py`).
- `gui/` — Tkinter desktop UI (`gui/app.py:run_gui`).
- `img/` — shipped logo assets (declared as `package-data` in pyproject).

## Public interface

Invoked through the CLI and the facade shims `lynx_compare_fund.cli`,
`.display`, `.about`, `.interactive`. Tests import `build_parser`,
`render_full_comparison`, and `get_about_text` via those paths.

## Conventions

- **Assets are loaded relative to `__file__`**, not via package resources:
  `about.py` reads `img/logo_ascii.txt` from its own dir, and
  `gui/app.py` reads PNGs from `__file__.parent.parent/"img"`. If you move
  these files, the `img/` directory must move with them, and
  `[tool.setuptools.package-data]` must keep pointing at `lynx_compare_ui`.
- **User-visible strings are localized** through
  `lynx_investor_core.translations.t` (imported as `_t`). Add new strings
  to the translation layer; don't hard-code English in widgets.
- Heavy/optional UI deps (`textual`, `tkinter`, `rich.Console`) are
  imported **inside functions**, not at module top level, so a headless
  CLI/JSON run never pays for them. Preserve this lazy-import pattern.
- Allowed dependencies: `lynx_compare_core` (engine), `lynx_compare_web`
  (the API, used lazily by `cli`/`tui`), other `lynx_compare_ui` modules,
  and suite constants via `from lynx_compare_fund import ...`.
