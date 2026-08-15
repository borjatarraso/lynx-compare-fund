# CLAUDE.md — lynx-compare-fund

Project-level guidance for agents. Keep it terse; per-package detail lives
in each package's own `CLAUDE.md` (linked below).

## Purpose

Side-by-side comparison of **two Exchange-Traded Funds**. Given two
tickers/ISINs it fetches both via `lynx-fund`, scores them metric by
metric, and picks a winner for every section (Costs, Income, Liquidity,
Performance, Diversification, Risk, Tracking) plus an overall winner.
Non-ETF instruments (stocks, mutual/index funds) are rejected at the
`lynx-fund` resolver level. Part of the Lince Investor Suite.

## Layout

The codebase is split into four top-level Python packages. Dependencies
flow one way: `ui` and `web` depend on `core`; nothing depends on `ui`
except `web.export` (for the shared renderer); `core` depends on neither.

| Package | Responsibility | Detail |
|---------|----------------|--------|
| `lynx_compare_core/` | Pure comparison engine + multi-fund ranking. No I/O, no presentation. | [core CLAUDE.md](lynx_compare_core/CLAUDE.md) |
| `lynx_compare_ui/` | All human-facing layers: CLI, Rich renderer, REPL, Textual TUI, Tkinter GUI, branding, `img/` assets. | [ui CLAUDE.md](lynx_compare_ui/CLAUDE.md) |
| `lynx_compare_web/` | Programmatic API, Flask REST server, JSON/HTML/text exporters. | [web CLAUDE.md](lynx_compare_web/CLAUDE.md) |
| `lynx_compare_fund/` | Compatibility **facade**: suite constants, `__main__`, plugin registration, and re-export shims for every moved module. | [facade CLAUDE.md](lynx_compare_fund/CLAUDE.md) |

`tests/` mirrors the historical `lynx_compare_fund.*` import paths.
`docs/` holds reference docs; see also `ARCHITECTURE.md` and `ROADMAP.md`.

## Build / test

```bash
pip install -e .                 # editable install (regenerates the import finder)
python -m pytest -q              # full suite (42 tests)
python -m pytest -q -p no:randomly   # deterministic order when debugging
```

Entry points (declared in `pyproject.toml`):

```bash
lynx-compare-fund -p VTI ITOT    # CLI  -> lynx_compare_fund.__main__:main
lynx-compare-fund-server         # REST -> lynx_compare_fund.server:run_server
```

After adding/removing a top-level package or moving assets, **re-run
`pip install -e .`** so the editable finder's `MAPPING` is regenerated;
otherwise the new package is not importable outside `pytest`.

## Conventions a new agent should follow

- **The split is a facade, not a rename.** The public, documented import
  path stays `lynx_compare_fund.*` (e.g. `from lynx_compare_fund.api import
  compare_funds`). Canonical code lives in the `core`/`ui`/`web` packages;
  `lynx_compare_fund/*.py` are thin shims that alias the canonical module
  via `sys.modules[__name__] = _canonical`. Do not break these paths — the
  test-suite and entry points rely on them.
- **Suite constants live only in `lynx_compare_fund/__init__.py`**
  (`__version__`, `SUITE_LABEL`, etc.). Every package imports them from
  there with `from lynx_compare_fund import ...` (bare, no submodule). This
  is the one intentional dependency from a canonical package back onto the
  facade; keep it.
- **Respect the dependency direction** in the table above. Don't make
  `core` import `ui`/`web`/the facade's submodules.
- Keep behavior and public APIs stable; this project is a released
  (`6.0.0`) suite member. Funds-only scope is enforced upstream in
  `lynx-fund` — don't re-implement instrument filtering here.
- Run the full test-suite before committing; all 42 tests must stay green.

<!-- LYNX-EP-NOTE:BEGIN -->

## Entry-point card — keep it current

This project carries `index.ep.md` (and `index.ep.html`), the standard card
that answers what this is, where to look first, and how to run it. Every
project in `~/claude/` has one in the same shape, so jumping between them
does not mean re-learning where to look.

**When work here changes any of the following, refresh the card:**

- what the project is or does (title, one-line purpose, description)
- the file someone should open first
- the command that starts it
- the top-level layout or where the documentation lives

Refresh it with:

```bash
python3 ~/claude/lynx_factory/web/tools/gen_ep_index.py --only <this-project>
```

That regenerates from this repo's own README/CLAUDE.md plus the Lynx Factory
ledger — it does not invent anything, so fixing the card usually means fixing
the README first. The README's ownership footer is refreshed by the same
command.

To hand-write a card and stop it being regenerated, set `ep_locked: true` in
its front matter.

<!-- LYNX-EP-NOTE:END -->
