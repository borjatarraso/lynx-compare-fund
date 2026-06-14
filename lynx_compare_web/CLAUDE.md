# CLAUDE.md — lynx_compare_web

## Responsibility (narrow)

The **non-terminal** ways into the comparison engine: a stable Python API,
an HTTP server, and serialisers. Thin glue over `lynx_compare_core` — it
fetches/wraps results and renders them; it contains no comparison math.

## Modules

- `api.py` — the documented public API.
- `server.py` — Flask REST server.
- `export.py` — serialisers for a `ComparisonResult`.

## Public interface

`api.py`:
- `compare_funds(ticker_a, ticker_b, *, refresh=False) -> ComparisonResult`
  — fetches both funds (current storage mode) and compares.
- `compare_reports(a, b) -> ComparisonResult` — compare two already-fetched
  `FundReport`s.
- `ComparisonView` — light display wrapper (`.sections`, `.winner`,
  `.summary()`).

`server.py`:
- `build_app()` -> Flask app with `GET /health`, `GET /version`,
  `POST /compare` (JSON body `{a, b, mode?, refresh?}`).
- `run_server(host="127.0.0.1", port=5054, debug=False)` — the
  `lynx-compare-fund-server` entry point.

`export.py`:
- `to_json`, `to_text`, `to_html`, `save(result, path, format)`.

Surfaced through the facade as `lynx_compare_fund.api`, `.server`,
`.export`. The server entry point is declared as
`lynx_compare_fund.server:run_server` in `pyproject.toml`.

## Conventions

- Allowed dependencies: `lynx_compare_core` (engine), `lynx_compare_ui`
  (`export` reuses `display.render_full_comparison` for text/HTML), suite
  constants via `from lynx_compare_fund import __version__`.
- Flask and the `lynx_fund.core` storage/ticker helpers are imported
  **inside** `build_app` so importing the package stays cheap and
  side-effect free.
- HTTP error contract in `server.py`: `400` for bad input / bad mode,
  `422` for a non-fund instrument (`NotAFundError`). Keep these codes
  stable for clients.
- Exports go through Rich's recorder (`record=True` / file console) so
  text and HTML render identically to the terminal output.
