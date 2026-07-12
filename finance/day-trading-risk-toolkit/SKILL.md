---
name: day-trading-risk-toolkit
description: Risk management, Monte Carlo stress-testing, position sizing, and statistically honest performance tracking for intraday trading (indices, gold). Validates whether a trading plan is survivable BEFORE real money is at risk.
---

# Day Trading Risk Toolkit

## Overview

A risk-first toolkit for aspiring and active day traders. It does **not**
generate trading signals and does **not** promise profits. Instead it answers
the three questions that decide whether a trader survives:

1. **Is my plan mathematically survivable?** (Monte Carlo simulation of the
   full outcome distribution — not just the best case)
2. **How large may this position be?** (fixed-fractional position sizing with
   leverage and margin checks)
3. **Is my edge real?** (trade journal with confidence intervals — separates
   statistical evidence from lucky streaks)

**Who this is for:** retail traders on instruments like NASDAQ 100 and
Gold/XAUUSD (CFDs or micro futures), and anyone evaluating whether a trading
plan or profit target is realistic.

## The Reality Check (read this first)

Independent research is unambiguous about retail day trading outcomes:

- A study of Brazilian futures day traders (Chague & De-Losso, FGV, 2020)
  found **97% of individuals who persisted for 300+ days lost money**; fewer
  than 1% earned more than a bank teller's salary.
- Regulators require CFD brokers to disclose loss rates; typical published
  figures are **70-80% of retail accounts lose money**.
- A daily profit target of 10% of account equity implies (compounded over 250
  trading days) turning EUR 10,000 into over EUR 200 trillion in one year.
  No fund in history has done this. If a target compounds to an impossible
  number, the target — not the effort — is the problem.

Professional risk standards this toolkit enforces in its warnings:

| Parameter | Professional standard | Common beginner error |
|-----------|----------------------|----------------------|
| Risk per trade | 0.5-2% of equity | 10%+ (implied by aggressive daily targets) |
| Realistic monthly return | 1-5% is very good | 200%+/month expected |
| Trades needed to prove a win rate | 100+ logged | 10-20 demo trades |
| Max drawdown tolerated by plan | defined in advance | discovered in panic |

## 5-Phase Workflow

### Phase 1: Stress-Test the Plan (before any real money)
- Write down the plan's parameters: win rate, risk/reward, risk per trade,
  trades per day, costs per trade
- Run `monte_carlo_simulator.py` with those parameters
- Run it again with the win rate 10-15 points LOWER (costs and slippage
  degrade every backtest)
- If risk of ruin > 1% or average max drawdown > 20%: reduce risk per trade
  and repeat. If expectancy is negative, the plan has no edge to size.

### Phase 2: Define Position Sizing Rules
- Fix risk per trade at 0.5-2% of equity — never more
- For each setup, derive position size from the stop distance with
  `position_size_calculator.py`
- Check the leverage and margin warnings: a plan that requires leverage above
  the ESMA retail cap (20x indices/gold) is not executable as designed

### Phase 3: Paper Trade and Log Everything
- Trade the plan on a demo account exactly as written for at least 100 trades
- Log every trade with `trading_journal.py add` — including costs
- Do not change position size or rules mid-sample

### Phase 4: Evaluate with Statistics, Not Feelings
- Run `trading_journal.py stats` — the Wilson confidence interval shows
  whether the observed win rate is evidence or noise
- Compare the real expectancy per trade against the Monte Carlo assumptions
- Only if the real, cost-inclusive numbers survive Phase 1's stress test
  should any real money be considered — starting with the minimum size

### Phase 5: Ongoing Risk Governance
- Re-run stats weekly; stop trading and review after any 5-loss streak or a
  drawdown beyond the plan's predefined limit
- Increase size only after 100+ additional trades confirm the edge at the
  current size
- Withdraw profits on a schedule; never add funds to "win back" losses

## Tools

### 1. Session Backtester (`scripts/session_backtester.py`)

Takes continuous 1-minute OHLCV history (e.g. exported from Databento as
front-month continuous futures) and answers two questions for a specific
intraday window: (a) the opportunity ceiling — how much movement the window
actually offered, day by day, with perfect foresight; (b) a measured
backtest of a transparent Opening Range Breakout baseline with realistic
spread/slippage costs — replacing an assumed win rate with a measured one.

```bash
python scripts/session_backtester.py --file nq_continuous_1m.parquet \
  --tz America/New_York --start 09:30 --end 11:00 --point-value 2.0 \
  --spread-points 2 --slippage-points 1 --stop-points 40 --target-r 1.5

python scripts/session_backtester.py --file gc_continuous_1m.parquet \
  --tz Europe/Berlin --start 15:30 --end 18:00 --point-value 10.0 \
  --spread-points 0.3 --slippage-points 0.2 --stop-points 5 --target-r 1.5
```

Requires `pandas` (only non-stdlib dependency in this toolkit, needed for
the datetime/timezone handling and grouping efficient columnar data
requires). Input file must have columns `dt, open, high, low, close,
volume`; `dt` must be timezone-aware (UTC).

### 2. Monte Carlo Simulator (`scripts/monte_carlo_simulator.py`)

Simulates 10,000 possible equity curves from strategy parameters. Reports
risk of ruin, final-equity percentiles, drawdown distribution, and
losing-streak probabilities, with plain-language interpretation.

```bash
# The plan as dreamed: 75% win rate, EUR 1000 risk per trade on EUR 10k
python scripts/monte_carlo_simulator.py --capital 10000 --win-rate 0.75 --rr 1.0 --risk-eur 1000

# The same edge with professional 1% risk sizing
python scripts/monte_carlo_simulator.py --capital 10000 --win-rate 0.75 --rr 1.0 --risk-pct 1

# Stress test: what if the real win rate is only 55%?
python scripts/monte_carlo_simulator.py --capital 10000 --win-rate 0.55 --rr 1.0 --risk-pct 1 --format json
```

### 3. Position Size Calculator (`scripts/position_size_calculator.py`)

Fixed-fractional position sizing with presets for NASDAQ 100 (CFD, MNQ
future) and Gold (CFD, MGC future). Warns on excessive risk, leverage above
ESMA retail caps, margin overload, and stops too tight for trading costs.

```bash
# NASDAQ CFD: EUR 10k account, 1% risk, 40-point stop at price 21500
python scripts/position_size_calculator.py --capital 10000 --risk-pct 1 --stop-points 40 --price 21500 --instrument nasdaq-cfd

# Gold CFD: 1% risk, USD 5 stop at price 2650
python scripts/position_size_calculator.py --capital 10000 --risk-pct 1 --stop-points 5 --price 2650 --instrument xauusd-cfd

# Offshore account with 500:1 leverage — shows gap-risk and missing-protection warnings
python scripts/position_size_calculator.py --capital 25000 --risk-pct 4 --stop-points 40 --price 21500 --instrument nasdaq-cfd --leverage 500
```

### 4. Trading Journal (`scripts/trading_journal.py`)

CSV-based journal (portable to Excel/Sheets) computing win rate **with a 95%
confidence interval**, expectancy, profit factor, max drawdown, and worst
loss streak. The confidence interval is the honesty mechanism: with 20
trades, an observed 65% win rate could truly be anywhere from ~43% to ~82%.

```bash
python scripts/trading_journal.py init
python scripts/trading_journal.py add --instrument NAS100 --direction long \
  --entry 21500 --exit 21540 --size 2.5 --pnl 95 --risk 100 --setup "opening range breakout"
python scripts/trading_journal.py stats
python scripts/trading_journal.py stats --format json
```

## Resources

- `references/risk-management-basics.md` — expectancy math, drawdown
  arithmetic, leverage and ESMA caps, cost drag, session characteristics
  (NASDAQ open, XAU London/NY overlap), realistic benchmarks, safer paths
  (funded/prop accounts, longer timeframes, index investing as baseline)
- `assets/trading-plan-template.md` — fill-in trading plan covering setups,
  risk limits, daily loss limit, drawdown circuit breakers, and review cadence

## What This Skill Deliberately Does NOT Do

- **No signal generation, no "strategy that wins"** — an edge cannot be
  downloaded; it must be measured (Phase 3-4)
- **No live broker/API integration** — automation of an unproven strategy
  only automates losses; prove the edge on paper first
- **No profit promises** — the honest baseline expectation for retail day
  trading is a loss; this toolkit exists to make the risk visible and
  survivable for those who proceed anyway

## Success Criteria

A user of this skill should be able to:
- Reject or resize an unsurvivable plan **before** funding an account
- State their risk per trade, daily loss limit, and drawdown circuit breaker
- Distinguish a statistically proven edge from a lucky streak
- Know the exact EUR amount at risk before every single trade
