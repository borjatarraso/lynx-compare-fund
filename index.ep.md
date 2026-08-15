---
ep_version: 1
project: lynx-compare-fund
title: Lynx Compare Fund
status: PAUSED
last_touched: 2026-06-15
last_touched_text: 15 June 2026
section: sub
category: investments
generated: 2026-08-15
ep_locked: false   # set true and this file is never regenerated
---

# Lynx Compare Fund

> Compare fundamentals between funds

🟠 **PAUSED** · last touched **15 June 2026** (last commit)

---

## What this is

**Side-by-side comparison of two Exchange-Traded Funds with winner per section.**

Part of the [Lince Investor Suite](https://github.com/borjatarraso/lynx-dashboard). Depends on [lynx-fund](https://github.com/borjatarraso/lynx-fund) for data.

Strictly **Funds only**. Any non-ETF instrument is rejected at the underlying `lynx-fund` resolver.

Per-section winner is determined by metric-wins tally; overall winner by section wins, then metric-wins tie-break, else tie.

Shown as coloured panels when the two funds aren't an apples-to-apples match:

- **Asset class mismatch** (equity vs fixed income, etc.) — red
- **Domicile mismatch** (US vs IE vs LU, etc.) — orange
- **Replication mismatch** (physical vs synthetic) — yellow
- **Size-tier mismatch** — yellow

Approximate overlap (0..1) using `Σ min(weight_A, weight_B)` across shared symbols. Shown as a percentage in the overall summary.

from lynx_compare_fund.api import compare_funds result = compare_funds("VTI", "ITOT") print(result.winner_ticker)  # "VTI" for section in result.sections: print(section.name, section.winner, section.wins_a, section.wins_b) ```

BSD-3-Clause. See `LICENSE`.

This project is part of the **Lince Investor Suite**, authored and signed by

**Borja Tarraso** &lt;[borja.tarraso@member.fsf.org](mailto:borja.tarraso@member.fsf.org)&gt; Licensed under BSD-3-Clause.

Every report and export emitted by Suite tools includes this same signature in its footer. The shipped logo PNGs additionally carry the author's signature via steganography for provenance — please do not replace or re-encode the logo files.

<!-- LYNX-EP-FOOTER:BEGIN -->

New here, or coming back after a while? Read [`index.ep.md`](index.ep.md) (or open [`index.ep.html`](index.ep.html) in a browser) — the standard card that answers what this is, where to look first, and how to run it, in the same shape for every project.

🟠 **PAUSED** · last touched **15 June 2026**

<img src="https://www.cortex-university.com/static/brand/lince-logo.png" alt="Lince" width="96" height="96" align="left" style="margin-right:16px" />

**Lynx Compare Fund is proudly part of Lince.**

Part of the LINCE company · © All rights reserved

<!-- LYNX-EP-FOOTER:END -->

## Start here

- [`README.md`](README.md) — what the project is, in its own words
- [`CLAUDE.md`](CLAUDE.md) — working agreement for a session in this repo
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — module map and how the pieces fit
- [`ROADMAP.md`](ROADMAP.md) — where this is heading

## Run it

```bash
cd ~/claude/lince-investor/lynx-compare-fund
lynx-compare-fund                     # console entry point
lynx-compare-fund-server              # console entry point
python3 -m lynx_compare_fund          # runnable package
```

## The rest of it

**Directories**

- `docs/` — 6 entries
- `lynx_compare_core/` — 5 entries
- `lynx_compare_fund/` — 14 entries
- `lynx_compare_fund.egg-info/` — 6 entries
- `lynx_compare_ui/` — 10 entries
- `lynx_compare_web/` — 6 entries
- `tests/` — 12 entries

**Other documentation**

- [`CHANGELOG.md`](CHANGELOG.md)
- [`DESIGN.md`](DESIGN.md)

**`docs/`** holds 6 files.

**Build / config**: `pyproject.toml`

---

## Ownership

<img src="https://www.cortex-university.com/static/brand/lince-logo.png" alt="Lince" width="96" height="96" align="left" style="margin-right:16px" />

**Lynx Compare Fund is proudly part of Lince.**

| Company ID | Headquarters |
|---|---|
| 3015071-2 | Helsinki, Finland |

Part of the LINCE company · © All rights reserved


<sub>Standard entry-point card (`index.ep.md`, format v1) — generated 2026-08-15 by Lynx Factory. Regenerating overwrites this file unless `ep_locked: true`.</sub>
