# Risk Rules

These rules exist to be applied when they are inconvenient. A rule that is
suspended on a strong-looking setup is not a rule, it is a preference.

## The six hard limits

1. **Risk per trade: 0.5 percent of account, 1.0 percent maximum.**
   At 1 percent, a six-trade losing streak costs roughly 6 percent. Losing
   streaks of six are ordinary at a 50 percent hit rate; the probability of
   at least one such streak across 100 trades is high.

2. **Daily loss limit: 2R. Trading stops for the day when it is reached.**
   Not "one more to get it back". The limit is the point at which judgement
   is already impaired.

3. **Maximum 2 trades per day.**
   Frequency is where intraday edges die. A scarcity constraint forces
   selection.

4. **Minimum reward-to-risk: 1.5, measured to a structural target.**
   Below 1.5 the required hit rate exceeds what is realistically achievable
   after costs. The target must be a level that exists on the chart, not a
   number that makes the ratio work.

5. **No position within 30 minutes of a high-impact release.**
   CPI, NFP, FOMC. A stop is a request, not a guarantee, when liquidity
   vanishes.

6. **Weekly loss limit: 5R. The week ends when it is reached.**
   This is the circuit breaker between a bad week and a damaged account.

## Stop placement

The stop belongs at the price that proves the idea wrong, and nowhere else.
Placing it where the loss feels tolerable, then sizing to that, inverts the
logic: it guarantees stops sit in noise. Find the invalidation level first,
then let `position_sizer.py` decide the size. If the resulting size is
uncomfortably small, the correct response is a smaller position, not a
tighter stop.

## Break-even hit rate by reward-to-risk

Before costs. The right column is what the system must actually beat.

| Reward-to-risk | Break-even hit rate |
|----------------|---------------------|
| 1.0 | 50.0% |
| 1.5 | 40.0% |
| 2.0 | 33.3% |
| 2.5 | 28.6% |
| 3.0 | 25.0% |

This table is why the reward-to-risk floor matters more than signal quality.
At 1:2, a 50 percent hit rate produces +0.5R per trade before costs. At 1:1,
the same 50 percent produces zero before costs and a loss after them.

## Escalation and de-escalation of size

- Increase risk only after 30 logged trades with a net expectancy above
  +0.15R, and then by no more than 0.25 percentage points at a time.
- Halve risk immediately after a 5R drawdown, and restore it only after
  10 subsequent trades at positive expectancy.
- Never increase size to recover a drawdown. That reverses the correct
  relationship between confidence and evidence.

## The three questions before every entry

1. Where is the price that proves me wrong, and am I willing to be wrong there?
2. What is the structural target, and is it at least 1.5 times the distance to my stop?
3. Would I take this trade if the last one had been a loss?

Question three is the one that catches revenge trades. It is also the one
most often skipped.

## Handling an automated pre-session briefing

Aaron runs an unpaid make.com automation that sends a formatted XAUUSD
briefing before the 09:00 preparation window. It is self-built against
whatever data source the automation queries, not a vetted provider, so it
gets the same treatment as any unverified input: useful for context, never
for a decision.

**Extract and treat as unverified context:** D1 and H4 trend direction, DXY,
US10Y, risk sentiment, prior day high and low, key levels, ATR, and the
scheduled news items. Lay this next to the live chart reading; never state
any of these figures as confirmed, since their source and freshness cannot
be checked from here.

**Discard entirely, every time:** any block that pairs a directional bias
with an entry zone, stop-loss, take-profit and a confidence label (the
briefing formats these as "London Session" / "New York Session" blocks).
These are ready-made trade signals from an unaudited source, structurally
identical to the percentage-based buy/sell indicator on Aaron's TradingView
chart that this project already rejected. They do not enter the analysis,
do not inform the bias, and are not mentioned in the handover line, even
when they are part of what Aaron pastes in. If a session's actual decision
already looks pre-formed before the 09:30 or 15:45 window runs its own
protocol on the live screenshot, say so plainly: a decision made at 08:55
is not an analysis made at 09:30, it is a confirmation search.
