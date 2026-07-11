# Trading Plan — [Name] — [Date]

> A plan that is not written down does not exist. A rule that has no
> predefined consequence is a suggestion, not a rule. Fill in every field
> BEFORE the first trade; change it only outside market hours, in writing.

## 1. Capital & Risk Limits (non-negotiable)

| Field | Value |
|-------|-------|
| Trading capital (money I can lose entirely without changing my life) | EUR ______ |
| Risk per trade (0.5-2% of equity) | ____ % = EUR ______ |
| Max trades per day | ______ |
| **Daily loss limit** (stop trading for the day when hit) | EUR ______ |
| **Weekly loss limit** (stop trading for the week when hit) | EUR ______ |
| **Drawdown circuit breaker** (stop live trading, back to demo, review plan) | ____ % from equity peak |
| Months of living expenses saved OUTSIDE trading capital | ______ |

## 2. Instruments & Sessions

| Instrument | Session (with time zone!) | Max concurrent positions |
|------------|---------------------------|--------------------------|
| | | |
| | | |

- [ ] I have checked for economic news releases (CPI, FOMC, NFP) in my
      session windows and will NOT hold positions through them.

## 3. Setups (one block per setup)

### Setup A: [name, e.g. "opening range breakout"]
- **Entry condition (objective, no interpretation):**
- **Stop-loss placement (defined before entry):**
- **Take-profit / exit rule:**
- **Minimum risk/reward accepted:** 1 : ____
- **Invalidation (when I do NOT take the trade):**

## 4. Execution Checklist (before every entry)

- [ ] Setup conditions met exactly as written above
- [ ] Position size computed from stop distance (`position_size_calculator.py`)
- [ ] EUR at risk ≤ my per-trade limit
- [ ] Daily loss limit not yet reached
- [ ] Stop-loss order placed IN THE PLATFORM (not mental)
- [ ] No news release within the expected holding time

## 5. Journal Commitment

- [ ] Every trade logged the same day (`trading_journal.py add`), including
      costs, even the embarrassing ones — especially the embarrassing ones
- [ ] Weekly: run `trading_journal.py stats`, note win-rate confidence
      interval and expectancy in the review log below
- [ ] No size increase before 100+ trades at current size show positive
      expectancy after costs

## 6. Go-Live Gates

| Gate | Criterion | Status |
|------|-----------|--------|
| G1 | Monte Carlo of plan parameters: risk of ruin < 1%, avg max DD < 15% | ☐ |
| G2 | 100+ demo trades logged; expectancy positive after costs | ☐ |
| G3 | Win-rate 95% confidence interval entirely above break-even rate | ☐ |
| G4 | Daily/weekly loss limits respected in demo 100% of the time | ☐ |
| G5 | Live with MINIMUM size for first 50 trades | ☐ |

Break-even win rate for my average risk/reward `1:R` is `1/(1+R)`
(e.g. 1:1 → 50%, 1:1.5 → 40%) — plus costs.

## 7. Weekly Review Log

| Week | Trades | P&L | Win rate (CI) | Expectancy | Rule violations | Action |
|------|--------|-----|---------------|------------|-----------------|--------|
| | | | | | | |

## 8. Personal Rules

- If I violate any rule in this plan: flat immediately, done for the day,
  written post-mortem before the next session.
- I do not add to losing positions. Ever.
- I do not remove or widen a stop. Ever.
- Trading income is not income until it is withdrawn and taxed. I do not
  quit other income sources based on unrealized or short-run results.

Signature: ______________________  Date: ____________
