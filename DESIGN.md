# Design notes

Why the code is shaped the way it is. Records decisions already made in
the codebase; it is not a roadmap (see `ROADMAP.md`).

## Why a four-package split with a facade

The tool started as a single flat `lynx_compare_fund` package. As the
CLI, REPL, TUI, GUI, REST server and exporters accumulated, three distinct
concerns became clear: **pure comparison logic**, **human-facing
presentation**, and **programmatic/transport access**. Splitting them into
`lynx_compare_core`, `lynx_compare_ui` and `lynx_compare_web` lets an agent
load only the slice it needs.

The constraint was that the package is a released suite member (`6.0.0`):
the documented import paths (`from lynx_compare_fund.api import
compare_funds`), the test-suite, and the `pyproject.toml` entry points all
reference `lynx_compare_fund.*`. So `lynx_compare_fund` was kept as a
**compatibility facade** rather than renamed away.

## Why `sys.modules` aliasing for shims

A re-export shim could `from x import *`, but that drops underscore-private
names — and `tests/test_multi.py` imports `_METRIC_DIRECTION` and `_get`.
Aliasing the whole module object:

```python
sys.modules[__name__] = _canonical
```

makes `lynx_compare_fund.multi` *be* `lynx_compare_core.multi`, preserving
every attribute and module identity. Uniform, total, and future-proof.

## Why suite constants live only in the facade `__init__`

`__version__`, `SUITE_LABEL` etc. are read by all three canonical
packages. Keeping them in `lynx_compare_fund/__init__.py` — which imports
none of the canonical packages at top level — gives every package one safe
edge back to the facade without a cycle. The facade's lazy `__getattr__`
exposes engine/api names at the top level on demand for the same reason.

## Why optional/heavy imports are function-local

`flask`, `textual`, `tkinter`, and even `rich.Console` are imported inside
the functions that need them, not at module top. A headless
`--json`/`--export` run, or simply importing the API, never pays for GUI
or server stacks. This is a deliberate pattern to preserve.

## Why assets load relative to `__file__`

`about.py` and `gui/app.py` read `img/` files by path relative to their own
location rather than via `importlib.resources`. The trade-off: the `img/`
directory must travel with those modules (it now lives in
`lynx_compare_ui/img/`, declared as `package-data`).

## Scope decision: funds only

Instrument filtering is **not** re-implemented here. `lynx-fund`'s resolver
raises `NotAFundError` for non-ETF instruments; the CLI maps that to a
user error and the server maps it to HTTP `422`. Comparison code assumes
it only ever sees funds.
