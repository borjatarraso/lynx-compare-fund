# Roadmap

Possible future work, clearly separated from what exists today (see
`ARCHITECTURE.md` for the current state). Nothing here is a commitment or a
description of shipped behavior; items are framed as ideas and known gaps.

## Known gaps / cleanup

- **Packaging of the ASCII logo.** `about.py` loads `img/logo_ascii.txt`
  at runtime, but `[tool.setuptools.package-data]` only declares
  `img/*.png`. This works in editable/source installs (files load from the
  tree); a built wheel may omit the `.txt`. Consider adding `img/*.txt` to
  `package-data` (left unchanged for now to avoid altering release
  packaging behavior).
- **Backward-compat shims for `tui`/`gui` subpackages.** The facade keeps
  shims for the historically public modules, but not for
  `lynx_compare_fund.tui` / `lynx_compare_fund.gui` (no test or entry point
  referenced them). Add shim subpackages if an external caller needs them.

## Possible enhancements

- **Multi-fund CLI surface.** `lynx_compare_core.multi` already ranks N
  funds (`compare_many_reports`, `pick_winners`), but the CLI only wires up
  the two-fund path. A `compare-many` subcommand could expose it.
- **PDF export end to end.** `weasyprint` is an optional dependency and
  `_do_export` recognises `.pdf`; verifying/documenting the full PDF path
  is a candidate.
- **Server surface.** `POST /compare` exists; a multi-fund ranking
  endpoint and machine-readable section/metric metadata could follow.

## Non-goals

- Re-implementing instrument resolution or data fetching — that stays in
  `lynx-fund`.
- Broadening scope beyond ETFs. The tool is intentionally funds-only.
