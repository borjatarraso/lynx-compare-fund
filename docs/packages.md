# Package layout

lynx-compare-fund is four top-level Python packages plus a test suite.

| Package | What it holds |
|---------|----------------|
| `lynx_compare_core` | `engine.py` (two-fund `compare`), `multi.py` (N-fund ranking). Pure domain logic, depends only on `lynx-fund`. |
| `lynx_compare_ui` | `cli.py`, `display.py`, `interactive.py`, `about.py`, `tui/`, `gui/`, `img/`. All human-facing surfaces. |
| `lynx_compare_web` | `api.py`, `server.py`, `export.py`. Python API, Flask REST server, serialisers. |
| `lynx_compare_fund` | Compatibility facade: suite constants, `__main__`, `plugin`, and re-export shims for every moved module. |

## Dependency direction

```
ui  ──▶ core
web ──▶ core,  web ──▶ ui.display
all ──▶ lynx_compare_fund   (suite constants only)
core ──▶ (nothing in-repo; only lynx-fund)
```

See the per-package `CLAUDE.md` for the rules, and `../ARCHITECTURE.md`
for the full diagram and dataflow.

## Import paths

The historical `lynx_compare_fund.*` paths are all preserved by shims, so
both of these work and refer to the same code:

```python
from lynx_compare_fund.engine import compare   # facade shim (documented)
from lynx_compare_core.engine import compare    # canonical home
```
