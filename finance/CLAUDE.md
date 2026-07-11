# Finance Skills - Claude Code Guidance

This guide covers the finance skill and its Python automation tools.

## Finance Skills Overview

**Available Skills:**
1. **financial-analyst/** - Financial statement analysis, ratio analysis, DCF valuation, budgeting, forecasting (4 Python tools)
2. **day-trading-risk-toolkit/** - Risk management for intraday trading: Monte Carlo strategy stress-testing, fixed-fractional position sizing, statistically honest trade journaling (3 Python tools)

**Total Tools:** 7 Python automation tools, 4 knowledge bases, 6 templates

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

### 5. Monte Carlo Simulator (`day-trading-risk-toolkit/scripts/monte_carlo_simulator.py`)

**Purpose:** Stress-test a day trading plan by simulating thousands of equity curves

**Features:**
- Risk of ruin, final-equity percentiles, drawdown distribution
- Losing-streak probabilities and expectancy (R-multiples)
- Percent-of-equity or fixed-EUR risk modes, per-trade cost modeling
- Plain-language interpretation with go/no-go guidance

**Usage:**
```bash
python day-trading-risk-toolkit/scripts/monte_carlo_simulator.py --capital 10000 --win-rate 0.65 --rr 1.5 --risk-pct 1
python day-trading-risk-toolkit/scripts/monte_carlo_simulator.py --capital 10000 --win-rate 0.55 --rr 1.0 --risk-eur 1000 --format json
```

### 6. Position Size Calculator (`day-trading-risk-toolkit/scripts/position_size_calculator.py`)

**Purpose:** Fixed-fractional position sizing for leveraged intraday instruments

**Features:**
- Presets for NASDAQ 100 (CFD, MNQ) and Gold (CFD, MGC)
- Effective leverage, margin, and spread-cost estimation
- Warnings for oversized risk, ESMA leverage cap violations, margin overload

**Usage:**
```bash
python day-trading-risk-toolkit/scripts/position_size_calculator.py --capital 10000 --risk-pct 1 --stop-points 40 --price 21500 --instrument nasdaq-cfd
```

### 7. Trading Journal (`day-trading-risk-toolkit/scripts/trading_journal.py`)

**Purpose:** CSV trade journal with statistically honest performance metrics

**Features:**
- Win rate with 95% Wilson confidence interval (exposes small-sample illusions)
- Expectancy, profit factor, max drawdown, worst loss streak
- `init` / `add` / `stats` subcommands; CSV portable to Excel/Sheets

**Usage:**
```bash
python day-trading-risk-toolkit/scripts/trading_journal.py init
python day-trading-risk-toolkit/scripts/trading_journal.py add --instrument NAS100 --direction long --entry 21500 --exit 21540 --size 2.5 --pnl 95 --risk 100
python day-trading-risk-toolkit/scripts/trading_journal.py stats --format json
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

---

**Last Updated:** February 2026
**Skills Deployed:** 1/1 finance skills production-ready
**Total Tools:** 4 Python automation tools
