# CLAUDE.md — lynx_compare_core

## Responsibility (narrow)

The **pure domain core**: turn resolved fund reports into structured
comparison results. No terminal output, no HTTP, no file I/O, no argparse.
Its only external dependency is `lynx-fund` (for the `FundReport` model and
`run_full_analysis` used by ranking).

## Modules

- `engine.py` — the head-to-head comparison of **two** funds.
- `multi.py` — normalised scoring + ranking across **N** funds.

## Public interface

`engine.py`:
- `compare(a: FundReport, b: FundReport) -> ComparisonResult` — the entry point.
- `holdings_overlap(a, b) -> Optional[float]`.
- Dataclasses: `ComparisonResult`, `SectionResult`, `MetricResult`, `Warning`.

`multi.py`:
- `compare_many_reports(...)`, `pick_winners(...)`, `score_for(report, normals)`.
- Module-private but covered by tests: `_METRIC_DIRECTION`, `_get`.

These are surfaced to callers through the facade: `lynx_compare_fund.engine`
and `lynx_compare_fund.multi` re-export this package, and
`lynx_compare_fund.__init__.__getattr__` lazily exposes the engine
dataclasses + `compare` at the package top level.

## Conventions

- **Keep it pure.** No imports from `lynx_compare_ui`, `lynx_compare_web`,
  or `lynx_compare_fund` submodules. Importing suite constants with
  `from lynx_compare_fund import __version__` is acceptable, but these
  modules currently need none.
- Section/metric direction (`"higher"` / `"lower"` is better) is data
  declared at module level (e.g. `_METRIC_DIRECTION`, the engine's metric
  tables). Extend those tables rather than hard-coding comparisons.
- Results are plain dataclasses so they serialise cleanly
  (`dataclasses.asdict`) for the web/export layers — keep fields
  serialisable.
