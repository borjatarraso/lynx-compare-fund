# Exports

Two ways to serialise a `ComparisonResult`.

## Library helpers (`lynx_compare_web.export`)

Available via the facade path `lynx_compare_fund.export`:

| Function | Output |
|----------|--------|
| `to_json(result)` | `dataclasses.asdict` dumped to indented JSON. |
| `to_text(result)` | Plain text via a Rich file console (width 120). |
| `to_html(result)` | HTML via Rich's recorder, inline styles. |
| `save(result, path, format="text")` | Write `json` / `html` / `text` to `path`. |

```python
from lynx_compare_fund.api import compare_funds
from lynx_compare_fund.export import to_json, to_html
from lynx_fund.core.storage import set_mode

set_mode("production")
r = compare_funds("VTI", "ITOT")
open("out.html", "w").write(to_html(r))
```

## CLI export (`--export`)

`lynx-compare-fund -p VTI ITOT --export FILE` routes through
`lynx_compare_ui.cli._do_export`, which picks the format from the file
extension:

| Extension | Format |
|-----------|--------|
| `.html` (or none) | HTML |
| `.txt` | text |
| `.pdf` | PDF (requires the optional `weasyprint` extra) |

Text and HTML exports render through the same `display.render_full_comparison`
path as the terminal, so they match the on-screen output, with a suite
footer appended.
