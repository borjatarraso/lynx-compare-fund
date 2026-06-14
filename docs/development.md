# Development

## Install

```bash
pip install -e .
```

This editable install generates an import finder under `site-packages`
(`__editable___lynx_compare_fund_*_finder.py`) whose `MAPPING` lists the
top-level packages. **After adding/removing a top-level package or moving
package assets, re-run `pip install -e .`** so the finder is regenerated —
otherwise the new package is importable under `pytest` (repo root on
`sys.path`) but not from an arbitrary working directory.

## Test

```bash
python -m pytest -q                  # full suite (42 tests)
python -m pytest -q -p no:randomly   # deterministic order for debugging
python -m pytest tests/test_engine.py -q
```

Tests pin the language to English (see `tests/conftest.py`) and import the
public `lynx_compare_fund.*` surface, which keeps the facade shims honest.

## Adding a backward-compat shim

When you add a module to a canonical package that needs to keep an old
`lynx_compare_fund.X` path, drop this in `lynx_compare_fund/X.py`:

```python
import sys
from lynx_compare_<pkg> import X as _canonical
sys.modules[__name__] = _canonical
```

## Optional extras

```bash
pip install -e ".[pdf]"    # weasyprint, for PDF export
pip install -e ".[test]"   # robotframework
pip install -e ".[all]"
```

## Conventions

- Keep the one-way dependency direction (`../ARCHITECTURE.md`).
- Import heavy/optional deps (flask, textual, tkinter, rich Console)
  inside functions, not at module top.
- Don't put logic in the `lynx_compare_fund` facade — it only forwards.
