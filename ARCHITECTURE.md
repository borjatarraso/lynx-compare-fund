# Architecture

How the pieces of **lynx-compare-fund** fit together. This is a tour of
what exists today, not a wish-list. Per-package detail is in each
package's `CLAUDE.md`.

## One-paragraph summary

Two fund tickers go in; a section-by-section comparison with per-section
and overall winners comes out. Data is fetched by the upstream `lynx-fund`
package; the pure comparison happens in `lynx_compare_core`; results are
presented by `lynx_compare_ui` (CLI/REPL/TUI/GUI) or `lynx_compare_web`
(Python API / REST / export). `lynx_compare_fund` is a thin facade that
preserves the original import paths and holds the entry points.

## Package map & dependency direction

```
                 ┌─────────────────────────┐
                 │   lynx_compare_fund      │  facade: constants,
                 │  (facade / entry points) │  __main__, plugin, shims
                 └────────────┬─────────────┘
              bare "from lynx_compare_fund import <const>"
                              │ (constants only)
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ lynx_compare_ │   │ lynx_compare_web │   │ lynx_compare_core│
│      ui       │   │  api/server/     │   │  engine + multi  │
│ cli/display/  │◀──│  export          │──▶│  (pure domain)   │
│ repl/tui/gui  │   │                  │   │                  │
└───────┬───────┘   └────────┬─────────┘   └────────┬─────────┘
        └───────────────┬────┴───────────────────────┘
                        ▼
                  ┌───────────┐
                  │ lynx-fund │  (upstream: data fetch + FundReport model)
                  └───────────┘
```

Rules (enforced by convention, see each `CLAUDE.md`):

- `lynx_compare_core` depends on **nothing** in this repo (only `lynx-fund`).
- `lynx_compare_web` depends on `core`, and on `ui.display` for rendered
  text/HTML exports.
- `lynx_compare_ui` depends on `core`, and lazily on `web.api`.
- Every package may read **suite constants** from the facade with
  `from lynx_compare_fund import <const>`; that is the only edge back to
  the facade, and the facade's `__init__` deliberately imports none of the
  canonical packages at top level (avoids a cycle).

## The facade pattern

The four-package split was done **without changing public import paths**.
Each old module name under `lynx_compare_fund/` is now a shim:

```python
import sys
from lynx_compare_core import engine as _canonical
sys.modules[__name__] = _canonical
```

Aliasing through `sys.modules` makes `lynx_compare_fund.engine` *identical*
to `lynx_compare_core.engine`, so public and private attributes alike are
preserved. Tests and the `pyproject.toml` entry points still reference the
`lynx_compare_fund.*` paths.

## Dataflow: a single comparison

1. **Entry** — `lynx-compare-fund VTI ITOT` → `lynx_compare_fund.__main__:main`
   → `lynx_compare_ui.cli.run_cli`.
2. **Mode** — `run_cli` sets the storage mode via
   `lynx_fund.core.storage.set_mode` (`-p` production / `-t` testing).
3. **Fetch** — each ticker is resolved and analysed by
   `lynx_fund.core.analyzer.run_full_analysis` (non-funds raise
   `NotAFundError`).
4. **Compare** — `lynx_compare_core.engine.compare(a, b)` produces a
   `ComparisonResult` (sections, metric winners, warnings, overall winner,
   holdings overlap).
5. **Present** — `lynx_compare_ui.display.render_full_comparison` prints it
   with Rich (or `--json` / `--export`, or a UI mode launches the
   REPL/TUI/GUI).

The REST path is the same `compare` core behind
`lynx_compare_web.api.compare_funds`, exposed at `POST /compare`.

## External dependencies

- `lynx-fund` — data fetch, storage modes, `FundReport` model, ticker
  resolution (the funds-only gate lives here).
- `lynx-investor-core` — translations (`t`), author/footer helpers, the
  plugin `SectorAgent` descriptor, GUI `ClickDebouncer`.
- `rich` (rendering), `textual` (TUI), `flask` (server), `tkinter` (GUI,
  stdlib), `argcomplete` (CLI completion). `weasyprint` is optional (PDF).

## Tests

`tests/` exercises the public `lynx_compare_fund.*` surface (engine, multi,
api, cli, display, export, server, about, plugin) — which keeps the facade
honest. Run `python -m pytest -q` (42 tests).
