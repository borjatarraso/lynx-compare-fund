# CLI reference

Defined in `lynx_compare_ui/cli.py` (`build_parser`). Entry point:
`lynx-compare-fund` → `lynx_compare_fund.__main__:main`.

```
lynx-compare-fund [mode] [ticker_a] [ticker_b] [options]
```

## Run mode (pick one)

| Flag | Effect |
|------|--------|
| `-p`, `--production-mode` | Use cached data from the `lynx-fund` `data/` store. |
| `-t`, `--testing-mode` | Always fetch fresh data (uses `data_test/`). |

## Positional

- `ticker_a`, `ticker_b` — fund ticker or ISIN (optional; prompted/!needed
  by the UI modes).

## UI modes (instead of a one-shot comparison)

| Flag | Launches |
|------|----------|
| `-i`, `--interactive-mode` | Prompt-driven REPL (`interactive.run_interactive`). |
| `-tui`, `--tui-mode` | Textual terminal UI (`tui/app.run_tui`). |
| `-x`, `--graphical-mode`, `--gui` | Tkinter desktop UI (`gui/app.run_gui`). |

## Output / behavior options

| Flag | Effect |
|------|--------|
| `--refresh` | Force fresh data download (ignore cache). |
| `--timeout N` | Per-fund timeout in seconds (default from `DEFAULT_TIMEOUT`, min 5). |
| `--no-news` | Skip news fetching. |
| `--no-reports` | Skip ancillary fund reports. |
| `--json` | Print the result as JSON and exit. |
| `--export FILE` | Export to a file; format from extension (`.html`, `.pdf`, `.txt`). |
| `--about` | Show developer/license info. |
| `--verbose`, `-v` | Verbose output. |
| `--version` | Print version and exit. |

## Examples

```bash
lynx-compare-fund -p VTI ITOT            # compare, production data
lynx-compare-fund -p VOO SPY --refresh   # force fresh data
lynx-compare-fund -p VTI ITOT --json     # machine-readable
lynx-compare-fund -p VTI ITOT --export out.html
lynx-compare-fund -p -tui                # Textual UI
```
