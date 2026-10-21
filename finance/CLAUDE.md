# Finance Skills - Claude Code Guidance

This guide covers the finance skills and their Python automation tools.

## Finance Skills Overview

**Available Skills:**
1. **financial-analyst/** - Financial statement analysis, ratio analysis, DCF valuation, budgeting, forecasting (4 Python tools)
2. **steuerrechner-selbststaendigkeit/** - German tax calculator for self-employed sole traders (EÜR): USt, GewSt (configurable Hebesatz), ESt, Soli, KiSt incl. §35 EStG credit, plus monthly Qonto reserve transfers (1 Python tool, German-language docs)
3. **cfd-intraday-analyst/** - Opening-range-breakout analysis for XAU/USD and NAS100 CFDs (London + NY open, long and short): entry signal on bar close, exit plan, lot sizing, 10,000-run replay plus real-session history, daily-limit PASS/BLOCK. Analysis only, never places orders (1 Python tool, German-language docs)

**Total Tools:** 6 Python automation tools, 9 knowledge bases, 8 templates

## Python Automation Tools

### 1. Ratio Calculator (`financial-analyst/scripts/ratio_calculator.py`)

**Purpose:** Calculate and interpret financial ratios from statement data

**Features:**
- Profitability ratios (ROE, ROA, Gross/Operating/Net Margin)
- Liquidity ratios (Current, Quick, Cash)
- Leverage ratios (Debt-to-Equity, Interest Coverage, DSCR)
- Efficiency ratios (Asset/Inventory/Receivables Turnover, DSO)
- Valuation ratios (P/E, P/B, P/S, EV/EBITDA, PEG)
- Built-in interpretation and benchmarking

**Usage:**
```bash
python financial-analyst/scripts/ratio_calculator.py financial_data.json
python financial-analyst/scripts/ratio_calculator.py financial_data.json --format json
```

### 2. DCF Valuation (`financial-analyst/scripts/dcf_valuation.py`)

**Purpose:** Discounted Cash Flow enterprise and equity valuation

**Features:**
- Revenue and cash flow projections
- WACC calculation (CAPM-based)
- Terminal value (perpetuity growth and exit multiple methods)
- Enterprise and equity value derivation
- Two-way sensitivity analysis
- No external dependencies (uses math/statistics)

**Usage:**
```bash
python financial-analyst/scripts/dcf_valuation.py valuation_data.json
python financial-analyst/scripts/dcf_valuation.py valuation_data.json --format json
```

### 3. Budget Variance Analyzer (`financial-analyst/scripts/budget_variance_analyzer.py`)

**Purpose:** Analyze actual vs budget vs prior year performance

**Features:**
- Variance calculation (actual vs budget, actual vs prior year)
- Materiality threshold filtering
- Favorable/unfavorable classification
- Department and category breakdown

**Usage:**
```bash
python financial-analyst/scripts/budget_variance_analyzer.py budget_data.json
python financial-analyst/scripts/budget_variance_analyzer.py budget_data.json --format json
```

### 4. Forecast Builder (`financial-analyst/scripts/forecast_builder.py`)

**Purpose:** Driver-based revenue forecasting and cash flow projection

**Features:**
- Driver-based revenue forecast model
- 13-week cash flow projection
- Scenario modeling (base/bull/bear)
- Trend analysis from historical data

**Usage:**
```bash
python financial-analyst/scripts/forecast_builder.py forecast_data.json
python financial-analyst/scripts/forecast_builder.py forecast_data.json --format json
```

### 5. Steuerrechner Selbstständigkeit (`steuerrechner-selbststaendigkeit/scripts/steuerrechner.py`)

**Purpose:** Project all German business taxes from monthly revenue/expenses and derive monthly reserve transfers for a Qonto sub-account structure

**Features:**
- Umsatzsteuer (19 %, Vorsteuer estimate or exact, Kleinunternehmer option)
- Gewerbesteuer (24,500 € allowance, 3.5 % Messzahl, configurable Hebesatz — default 320 % / Wiggensbach)
- Einkommensteuer §32a EStG (2025 exact, 2026 parameters), Vorsorge deduction
- §35 EStG Gewerbesteuer credit, Solidaritätszuschlag (Freigrenze + Milderungszone), Kirchensteuer
- Scenario table across revenue levels, JSON profile with CLI overrides
- German number formatting, text and JSON output

**Usage:**
```bash
python3 steuerrechner-selbststaendigkeit/scripts/steuerrechner.py --umsatz 12500 --ausgaben 2800 --kv-monat 850
python3 steuerrechner-selbststaendigkeit/scripts/steuerrechner.py --tabelle 6000:16000:2000 --kostenquote 0.25
python3 steuerrechner-selbststaendigkeit/scripts/steuerrechner.py --umsatz 12500 --ausgaben 2800 --format json
```

### 6. CFD Intraday Analyst (`cfd-intraday-analyst/scripts/cfd_analyst.py`)

**Purpose:** Opening-range-breakout workflow for XAU/USD and NAS100 CFDs (e.g. Vantage/MT5), from signal to sized, risk-checked plan, without any broker connection

**Features:**
- London (08:00 London) and NY (09:30 New York) sessions with built-in EU/UK/US DST rules, output in German time
- Long and short signals on 5-minute bar close outside the opening range
- Stops: range midpoint, opposite side, ATR, percent, price; targets as R multiple
- Lot sizing from risk per trade, stop distance, spread and broker contract specs (required config, never defaulted)
- Replay: 10,000 bootstrapped sessions (fixed seed) plus the same rule on every past session, break-even verdict
- Risk gate: reward:risk, entry window, signal age, trades per day, daily loss limit, spread share
- Data: Yahoo GC=F/NQ=F futures as proxy, or MT5 CSV export (M1/M5, server-time offset)
- Offline self-test on synthetic data

**Usage:**
```bash
python3 cfd-intraday-analyst/scripts/cfd_analyst.py selftest
python3 cfd-intraday-analyst/scripts/cfd_analyst.py entry --instrument XAUUSD --session london --write
python3 cfd-intraday-analyst/scripts/cfd_analyst.py exit --stop or-mid --target 2R --write
python3 cfd-intraday-analyst/scripts/cfd_analyst.py replay --format json
```

**Documented exception:** `fetch` (and the automatic refresh in `entry`/`exit`/`replay`) calls Yahoo Finance over the network; everything else runs locally, and `--data` / `mt5-import` work fully offline.

## Quality Standards

**All finance Python tools must:**
- Use standard library only (math, statistics, json, argparse)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes
- Process files locally (no API calls)
- Include argparse CLI with `--help` support

## Related Skills

- **C-Level:** Strategic financial decision-making -> `../c-level-advisor/`
- **Business & Growth:** Revenue operations, sales metrics -> `../business-growth/`
- **Product Team:** Budget allocation, RICE scoring -> `../product-team/`

---

**Last Updated:** October 2026
**Skills Deployed:** 3/3 finance skills production-ready
**Total Tools:** 6 Python automation tools
