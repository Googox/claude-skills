---
name: gold-daytrading-dashboard
description: Structured decision support for XAUUSD day trading. Analyses chart screenshots against a fixed protocol, computes position size and R-multiples deterministically, scores setups against a rule-based confluence model, and measures realised expectancy from a trade journal. For private use only; not investment advice.
---

# Gold Day Trading Dashboard

## Overview

A decision-support toolkit for discretionary intraday trading in spot gold
(XAUUSD). It converts an unstructured impulse ("should I buy here?") into a
documented, comparable, reviewable decision, and then measures whether those
decisions actually made money.

The skill is built on one premise: the expectancy of a trading system comes
from the R-multiple, not the hit rate. A 50 percent hit rate at 1:1 loses
money after costs; the same 50 percent at 1:2 returns +0.5R per trade before
costs. Everything in this package therefore optimises the ratio, the risk and
the record, and treats signal generation as the least reliable component.

## Scope and honest limits

Read this section before using anything else in the package.

**What the skill does**
- Applies one fixed analysis protocol to every screenshot, so readings are
  comparable across days and cannot drift with mood.
- Separates what is legible in an image from what is being assumed.
- Computes position size, R-multiples and take-profit ladders exactly.
- Applies hard vetoes that the trader cannot argue with in the moment.
- Reports realised expectancy honestly, including when it is negative.

**What the skill does not do, and cannot**
- It has no live market data. A screenshot is historical the moment it is
  captured, and gold can move 5 to 15 USD on the M5 while an analysis is
  being written. This latency is structural and cannot be engineered away.
- It cannot verify that a screenshot is current, correctly scaled, or
  complete.
- Indicator values read from an image are estimates. Values whose parameters
  are not printed on the chart cannot be cited at all.
- It has no demonstrated predictive edge. No claim in this package should be
  read as evidence that screenshot analysis produces positive expectancy.
- It is not investment advice and carries no licence. Issuing these
  assessments to third parties systematically moves into regulated
  investment advice under German KWG and WpIG. This package is for the
  author's private use.

**The most valuable component is the journal**, because it is the only part
that can tell the trader something true. After 30 trades it will produce a
verdict, and that verdict may be to stop.

## 5-Phase Workflow

### Phase 1: Pre-session preparation
- Fill in `assets/daily-plan-template.md` before the market opens, not during it.
- Mark prior day high and low, and the Asian session range.
- Write the H4 and H1 bias in one sentence each, in advance.
- Check the economic calendar and note high-impact release times.
- Confirm the risk budget and how many of the day's two trades remain.

### Phase 2: Screenshot analysis
- Supply the chart with symbol, timeframe, timestamp and a legible price axis.
- Follow `references/screenshot-analysis-protocol.md` exactly, including the
  mandatory staleness statement and the observed-versus-assumed split.
- Produce one of three outcomes: LONG, SHORT, or NO TRADE. NO TRADE is the
  default and never requires justification.
- State the counter-case. An analysis without one is incomplete.

### Phase 3: Scoring and sizing
- Score the setup with `scripts/setup_scorer.py`. Hard vetoes override the
  score entirely.
- Compute size with `scripts/position_sizer.py` from account balance, risk
  percent, entry and structural stop. Never estimate a position size.
- Verify reward-to-risk to the first structural target clears 1.5. Below that
  the trade is void regardless of how good it looks.

### Phase 4: Execution and logging
- Place the stop at the invalidation level chosen in Phase 2, then size to it.
  Never the reverse.
- Log the trade with `scripts/trade_journal.py add` within ten minutes of the
  exit, while the reasoning is still accurate rather than reconstructed.
- Answer `--followed-plan` honestly, especially on winning trades. An off-plan
  winner is a process failure that happened to pay.

### Phase 5: Review
- Weekly: `trade_journal.py stats --by setup` and `--by session`.
- Read off-plan trades individually. Discipline usually binds before analysis does.
- After 30 trades, act on the verdict. A negative net expectancy over an
  adequate sample is evidence, and the expensive response is to continue
  unchanged.
- Track hours spent. Expectancy per hour is the number that decides whether
  this activity earns its place against alternative uses of the same time.

## Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `scripts/position_sizer.py` | Position size, risk in account currency, R-multiple ladder | `--balance 25000 --risk-pct 0.5 --entry 2412.50 --stop 2405 --target 2430 --usd-rate 0.92` |
| `scripts/setup_scorer.py` | Weighted confluence score with hard vetoes | `--htf-trend aligned --structure-break yes --at-key-level yes --rr 2.3` |
| `scripts/trade_journal.py` | Trade log, expectancy, drawdown, verdict | `stats --by setup` |

All scripts are Python 3.8+, standard library only, and support `--json`.
None calls a model or fetches data; identical inputs always produce identical
output. That determinism is what makes the record trustworthy.

## References

| File | Content |
|------|---------|
| `references/screenshot-analysis-protocol.md` | The fixed six-step procedure and output template |
| `references/risk-rules.md` | Six hard limits, stop placement, break-even table |
| `references/technical-framework.md` | Reading order, structure vocabulary, the four permitted setups |
| `references/xauusd-instrument-facts.md` | Contract specification, costs, sessions, drivers |

## Assets

| File | Use |
|------|-----|
| `assets/daily-plan-template.md` | Written before the session opens |
| `assets/pre-trade-checklist.md` | Answered before every entry |
| `assets/trade-journal-template.csv` | Journal schema for `trade_journal.py` |

## The six hard limits

Repeated here because they are the part most likely to be abandoned first.

1. Risk per trade: 0.5 percent, 1.0 percent maximum
2. Daily loss limit: 2R, then trading stops for the day
3. Maximum 2 trades per day
4. Minimum reward-to-risk 1.5 to a structural target
5. No position within 30 minutes of a high-impact release
6. Weekly loss limit: 5R

## Anti-patterns

- Placing the stop where the loss feels acceptable, then calling it structural
- Moving a stop away from price to avoid being wrong
- Taking a trade because the session has been quiet
- Citing an indicator value that is not legible on the screenshot
- Treating a screenshot as current without a timestamp
- Increasing size to recover a drawdown
- Drawing conclusions from fewer than 30 logged trades
- Logging `followed_plan=yes` on a trade that was improvised and won

## Disclosure

This package produces structured readings of static images. It is not a
forecast, carries no verified edge, and is not investment advice. It is built
for private use. The decision, the position and the outcome belong to the
trader.
