# Changelog

## 6.0.0 — 2026-04-26

**Major release synchronising the entire Lince Investor Suite.**

### What's new across the Suite

- **lynx-fund** — brand-new mutual / index fund analysis tool, rejecting
  ETFs and stocks at the resolver level. Surfaces share classes, loads,
  12b-1 fees, manager tenure, persistence, capital-gains tax drag, and
  20-rule passive-investor checklist with tailored tips.
- **lynx-compare-fund** — head-to-head comparison for two mutual / index
  funds. Adds a Boglehead-style Passive-Investor Verdict, plus warnings
  for active-vs-passive, UCITS, soft- / hard-close, and distribution-
  policy mismatches.
- **lynx-theme** — visual theme editor for the entire Suite (GUI + TUI
  only). Edit colours, fonts, alignment, bold / italic / underline /
  blink / marquee for 15 styled areas with live preview. Three built-in
  read-only reference themes (`lynx-mocha`, `lynx-latte`,
  `lynx-high-contrast`). Sets the default theme persisted to
  `$XDG_CONFIG_HOME/lynx-theme/default.json`.
- **i18n** — every Suite CLI now accepts `--language=us|es|it|de|fr|fa`
  and persists the user's choice to `$XDG_CONFIG_HOME/lynx/language.json`.
  GUI apps mount a small bottom-right language toggle (left-click
  cycles, right-click opens a chooser); TUI apps bind `g` to cycle.
  Honours `LYNX_LANG` for ad-hoc shells.
- **Author signature footer** — every txt / html / pdf export now ends
  with the Suite-wide author block: *Borja Tarraso
  &lt;borja.tarraso@member.fsf.org&gt;*. Provided by the new
  `lynx_investor_core.author_footer` module.

### Dashboard

- Two new APP launchables (Lynx Fund, Lynx Compare Fund, Lynx Theme),
  raising the catalogue to **8 apps + 11 sector agents = 19
  launchables**.
- Per-app launch dialect (`run_mode_dialect`, `ui_mode_flags`,
  `accepts_identifier`) so the launcher emits argv each app
  understands; lynx-theme + lynx-portfolio launch correctly from every
  mode.
- `--recommend` now rejects empty queries instead of silently passing.

### Bug fixes

- `__main__.py` of every fund / compare-fund / etf / compare-etf entry
  point now propagates `run_cli`'s return code so non-zero exits are
  visible to shell scripts and CI pipelines.
- Stale-install hygiene: pyproject editable installs now overwrite
  cached site-packages copies cleanly.
- Cosmetic clean-up: remaining "ETF" labels in fund / compare-fund
  GUI / TUI / interactive prompts → "Fund".
- Validation: empty positional ticker, missing second comparison
  ticker, and `--recommend ""` now exit non-zero with a clear message.


## 1.0.0 — 2026-04-24

**First release.**

Side-by-side ETF comparison tool, part of the Lince Investor Suite.
Cloned from the lynx-compare scaffold but rewritten for ETFs: uses
`lynx-fund` for data, replaces fundamental-analysis metrics (valuation,
profitability, solvency, moat, intrinsic value) with ETF-native
sections (costs, income, liquidity, performance, diversification, risk,
tracking).

**Scope**

- Strictly ETFs. Scope is enforced at the underlying `lynx-fund`
  resolver level; non-ETFs never reach the comparison engine.

**Features**

- Seven sections with per-section winners: Costs, Income, Size &
  Liquidity, Performance, Diversification, Risk, Tracking.
- Overall winner by sections-won tally with metric-wins tiebreak.
- Four comparability warnings: asset-class, domicile, replication,
  size-tier.
- Approximate holdings overlap (sum-of-minimum-weights).
- Full four-mode support: console, interactive REPL, Textual TUI,
  Tkinter GUI.
- Flask REST API (`lynx-compare-fund-server`) on port 5054.
- Exports: JSON / text / HTML.
- Registered as a Suite plugin (`lynx_investor_suite.agents` group).

**Tests**

- 42 pytest tests covering engine logic, public API, display rendering,
  warnings, N-way compare, CLI parsing, export, Flask server, plugin
  registration.
