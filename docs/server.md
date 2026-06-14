# REST server

Defined in `lynx_compare_web/server.py`. Entry point:
`lynx-compare-fund-server` → `lynx_compare_fund.server:run_server`
(default `127.0.0.1:5054`).

```bash
lynx-compare-fund-server
# or programmatically:
python -c "from lynx_compare_fund.server import run_server; run_server(port=5054)"
```

## Endpoints

| Method | Path | Body | Success |
|--------|------|------|---------|
| GET | `/health` | — | `{"status": "ok", "version": <v>}` |
| GET | `/version` | — | `{"name": "lynx-compare-fund", "version": <v>}` |
| POST | `/compare` | `{"a", "b", "mode"?, "refresh"?}` | full `ComparisonResult` as a dict |

`mode` defaults to `"production"`; `refresh` defaults to `false`.

## Error contract

| Status | When |
|--------|------|
| `400` | Missing `a`/`b`, or an invalid storage `mode`. |
| `422` | A ticker resolves to a non-fund instrument (`NotAFundError`). |

## Example

```bash
curl -s localhost:5054/compare \
  -H 'content-type: application/json' \
  -d '{"a":"VTI","b":"ITOT","mode":"production"}'
```

The result is `dataclasses.asdict(ComparisonResult)` — the same structure
the CLI renders and the exporters serialise.
