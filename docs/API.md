# Lynx Compare Fund — API reference

## Public entry points

### `lynx_compare_fund.api.compare_funds(a, b, *, refresh=False) -> ComparisonResult`

Fetches both ETFs through `lynx_fund` and returns a fully-populated
`ComparisonResult`.

```python
from lynx_fund.core.storage import set_mode
from lynx_compare_fund.api import compare_funds

set_mode("production")
result = compare_funds("VTI", "ITOT")
print(result.winner_ticker, result.sections_won_a, result.sections_won_b)
for section in result.sections:
    print(section.name, section.winner)
```

### `lynx_compare_fund.api.compare_reports(a, b) -> ComparisonResult`

Like `compare_funds` but takes already-fetched `FundReport` objects.

### `lynx_compare_fund.api.ComparisonView`

Light wrapper exposing `sections`, `winner`, `section_named(name)` and
`summary()` (a JSON-safe dict).

## Engine

### `lynx_compare_fund.engine.compare(a, b) -> ComparisonResult`

Pure in-memory diff of two reports. No I/O. This is what `compare_funds`
delegates to after fetching.

### Data types

- `MetricResult` — key, label, value_a, value_b, winner (`"a"` /
  `"b"` / `"tie"` / `"na"`), fmt_a, fmt_b.
- `SectionResult` — name, metrics, wins_a, wins_b, ties, winner.
- `Warning` — level (`"asset_class"` / `"domicile"` / `"replication"`
  / `"tier"`), message.
- `ComparisonResult` — full result with `winner_ticker` property.

## N-way comparison

### `lynx_compare_fund.multi.compare_many(tickers) -> MultiCompareResult`

Fetch + rank many ETFs across a standard metric set.

### `lynx_compare_fund.multi.compare_many_reports(reports)`

Same, with already-fetched reports.

## REST API

`lynx-compare-fund-server` exposes:

| Method | Path | Body | Response |
|--------|------|------|----------|
| GET | `/health` | — | `{"status": "ok", "version": ...}` |
| GET | `/version` | — | `{"name": "lynx-compare-fund", "version": ...}` |
| POST | `/compare` | `{"a": "VTI", "b": "ITOT", "mode": "production", "refresh": false}` | full ComparisonResult as dict |

Errors: `400` for missing tickers or bad mode; `422` if a ticker
resolves to a non-ETF instrument.

## Export

`lynx_compare_fund.export.to_json(result) / to_text(result) /
to_html(result) / save(result, path, format)`.

## Plugin registration

```toml
[project.entry-points."lynx_investor_suite.agents"]
compare-etf = "lynx_compare_fund.plugin:register"
```
