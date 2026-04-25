# Lynx Compare Fund

**Side-by-side comparison of two Exchange-Traded Funds with winner per section.**

Part of the [Lince Investor Suite](https://github.com/borjatarraso/lynx-dashboard).
Depends on [lynx-fund](https://github.com/borjatarraso/lynx-fund) for data.

## Scope

Strictly **Funds only**. Any non-ETF instrument is rejected at the
underlying `lynx-fund` resolver.

## Install

```bash
pip install -e .
```

## Quickstart

```bash
lynx-compare-fund -p VTI ITOT                # Compare two ETFs
lynx-compare-fund -p VOO SPY --refresh        # Force fresh data
lynx-compare-fund -t IVV SPY                  # Testing mode
lynx-compare-fund -p VTI ITOT --json          # JSON output
lynx-compare-fund -p -i                       # Interactive REPL
lynx-compare-fund -p -tui                     # Textual TUI
lynx-compare-fund -p -x                       # Tkinter GUI
lynx-compare-fund-server                      # REST API on :5054
```

## Sections & winners

Per-section winner is determined by metric-wins tally; overall winner by
section wins, then metric-wins tie-break, else tie.

| Section | Metrics | Direction |
|---------|---------|-----------|
| **Costs** | TER, management fee, spread, est. $ cost / $10k / yr | lower wins |
| **Income** | Dividend yield, SEC yield; policy/frequency shown as info | higher yield wins |
| **Size & Liquidity** | AUM, avg volume, avg $ volume, fund age, shares, premium/discount | higher / closer-to-zero wins |
| **Performance** | 1M / 3M / YTD / 1Y / 3Y / 5Y / 10Y returns, Sharpe, Sortino | higher wins |
| **Diversification** | Holdings count, top-10 concentration, sector HHI, sector & country counts | more holdings / lower concentration wins |
| **Risk** | Volatility (1Y / 3Y), max drawdown, beta (closer to 1) | lower / closer to 1 wins |
| **Tracking** | Tracking error, tracking difference, R² | lower / closer-to-zero / higher wins |

## Warnings

Shown as coloured panels when the two funds aren't an apples-to-apples match:

- **Asset class mismatch** (equity vs fixed income, etc.) — red
- **Domicile mismatch** (US vs IE vs LU, etc.) — orange
- **Replication mismatch** (physical vs synthetic) — yellow
- **Size-tier mismatch** — yellow

## Holdings overlap

Approximate overlap (0..1) using `Σ min(weight_A, weight_B)` across
shared symbols. Shown as a percentage in the overall summary.

## Public API

```python
from lynx_fund.core.storage import set_mode
set_mode("production")

from lynx_compare_fund.api import compare_funds
result = compare_funds("VTI", "ITOT")
print(result.winner_ticker)  # "VTI"
for section in result.sections:
    print(section.name, section.winner, section.wins_a, section.wins_b)
```

## REST API

```bash
lynx-compare-fund-server
# POST /compare  {"a": "VTI", "b": "ITOT", "mode": "production"}
# GET  /health
# GET  /version
```

## License

BSD-3-Clause. See `LICENSE`.

---

## Author and signature

This project is part of the **Lince Investor Suite**, authored and signed by

> **Borja Tarraso** &lt;[borja.tarraso@member.fsf.org](mailto:borja.tarraso@member.fsf.org)&gt;
> Licensed under BSD-3-Clause.

Every report and export emitted by Suite tools includes this same
signature in its footer. The shipped logo PNGs additionally carry the
author's signature via steganography for provenance — please do not
replace or re-encode the logo files.
