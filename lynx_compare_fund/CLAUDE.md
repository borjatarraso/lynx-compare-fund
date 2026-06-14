# CLAUDE.md — lynx_compare_fund (compatibility facade)

## Responsibility (narrow)

This package is the **public face and compatibility facade** for the tool.
It owns three real things and re-exports everything else:

1. **Suite constants** — `lynx_compare_fund/__init__.py` defines
   `__version__`, `__author__`, `__year__`, `SUITE_NAME`,
   `SUITE_VERSION`, `SUITE_LABEL`, and a lazy `__getattr__` that exposes
   the engine/api names at the package top level.
2. **Entry points** — `__main__.py` (`main`, the `lynx-compare-fund`
   console script) and `plugin.py` (`register`, the
   `lynx_investor_suite.agents` plugin descriptor).
3. **Re-export shims** — `engine.py`, `multi.py`, `api.py`, `server.py`,
   `export.py`, `cli.py`, `display.py`, `about.py`, `interactive.py`.

## Public interface

The historical, documented import paths, all still valid:

```python
from lynx_compare_fund import compare_funds, ComparisonResult   # via __getattr__
from lynx_compare_fund.api import compare_funds, compare_reports, ComparisonView
from lynx_compare_fund.engine import compare
from lynx_compare_fund.cli import run_cli, build_parser
from lynx_compare_fund.server import run_server, build_app
```

## Conventions

- **Shims are uniform.** Each shim module is:

  ```python
  import sys
  from lynx_compare_<pkg> import <module> as _canonical
  sys.modules[__name__] = _canonical
  ```

  This makes `lynx_compare_fund.X` *the same module object* as its
  canonical home, so every attribute (public **and** private, e.g.
  `multi._get`) is preserved. When you add a module to a canonical package
  that needs the old path, add a shim in this exact shape.
- **Don't put real logic here.** New behavior belongs in `core`/`ui`/`web`.
  This package only forwards.
- `__init__.py` must not import the canonical packages at top level — it
  holds plain constants and lazy `__getattr__` to avoid import cycles
  (the canonical packages import `from lynx_compare_fund import <const>`).
- `plugin.py` advertises `package_module="lynx_compare_fund"` and
  `entry_point_module="lynx_compare_fund.__main__"`; keep those names.
