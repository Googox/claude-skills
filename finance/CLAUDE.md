# Finance Skills - Claude Code Guidance

This guide covers the finance skills and their Python automation tools.

## Finance Skills Overview

**Available Skills:**
1. **financial-analyst/** - Financial statement analysis, ratio analysis, DCF valuation, budgeting, forecasting (4 Python tools)
2. **steuerrechner-selbststaendigkeit/** - German tax calculator for self-employed sole traders (EÜR): USt, GewSt (configurable Hebesatz), ESt, Soli, KiSt incl. §35 EStG credit, plus monthly Qonto reserve transfers (1 Python tool, German-language docs)

3. **gold-daytrading-dashboard/** - Decision support for XAUUSD intraday trading: fixed screenshot analysis protocol, deterministic position sizing and R-multiple math, rule-based setup scoring with hard vetoes, trade journal with expectancy verdict (3 Python tools, private use only, not investment advice)

**Total Tools:** 8 Python automation tools, 10 knowledge bases, 10 templates

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

### 6. Position Sizer (`gold-daytrading-dashboard/scripts/position_sizer.py`)

**Purpose:** Compute XAUUSD position size, risk in account currency, and the R-multiple ladder

**Features:**
- Lot sizing from account balance, risk percent, entry and structural stop
- EUR account handling via USD conversion rate
- Take-profit ladder at 1R, 1.5R, 2R, 3R with profit in both currencies
- Reward-to-risk scoring of a concrete target against a 1.5 floor
- Warnings for stops inside spread noise, excessive risk percent, lot-rounding drift

**Usage:**
```bash
python3 gold-daytrading-dashboard/scripts/position_sizer.py --balance 25000 --risk-pct 0.5 --entry 2412.50 --stop 2405 --target 2430 --usd-rate 0.92
python3 gold-daytrading-dashboard/scripts/position_sizer.py --balance 25000 --entry 2412.50 --stop 2405 --json
```

### 7. Setup Scorer (`gold-daytrading-dashboard/scripts/setup_scorer.py`)

**Purpose:** Score a trade setup against weighted confluence criteria before entry

**Features:**
- Eight weighted criteria (HTF trend, structure break, key level, pullback, momentum, session, volatility, plan match)
- Hard vetoes that override the score: news window, daily loss limit, R:R below 1.5, trade count
- Verdict bands: TAKE, TAKE REDUCED, WATCH, NO TRADE
- Unanswered criteria score as zero and are flagged explicitly
- Interactive mode for use away from the terminal

**Usage:**
```bash
python3 gold-daytrading-dashboard/scripts/setup_scorer.py --htf-trend aligned --structure-break yes --at-key-level yes --pullback yes --session overlap --rr 2.3
python3 gold-daytrading-dashboard/scripts/setup_scorer.py --interactive
```

### 8. Trade Journal (`gold-daytrading-dashboard/scripts/trade_journal.py`)

**Purpose:** Log closed trades and measure realised expectancy in R

**Features:**
- R-multiple computed from entry, stop and actual exit
- Expectancy gross and net of assumed transaction cost
- Break-even hit rate implied by realised win/loss sizes
- Max drawdown in R, longest losing streak, profit factor
- Breakdown by setup, session, direction or plan adherence
- Blunt verdict after 30 trades, including NEGATIVE EXPECTANCY

**Usage:**
```bash
python3 gold-daytrading-dashboard/scripts/trade_journal.py add --entry 2412.50 --stop 2405 --exit 2427.50 --setup breakout --session overlap
python3 gold-daytrading-dashboard/scripts/trade_journal.py stats --by setup
```

**Scope note:** The gold-daytrading-dashboard skill is built for private use.
It has no live market data, no verified predictive edge, and is not investment
advice. Screenshot analysis is latency-bound and explicitly labelled as such
throughout the package.

**Last Updated:** September 2026
**Skills Deployed:** 3/3 finance skills production-ready
**Total Tools:** 8 Python automation tools
