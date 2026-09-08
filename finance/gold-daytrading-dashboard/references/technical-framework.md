# Technical Framework

The vocabulary and the small set of setups used in every analysis. A closed
list is deliberate: setups that are not on it cannot be scored, journalled,
or evaluated for expectancy, which makes them unmeasurable by construction.

## Reading order

Analysis moves from slow to fast, never the reverse. A five-minute chart read
without its higher timeframe context produces a confident opinion about noise.

1. **H4** -- the day's directional bias and the levels that matter
2. **H1** -- the working trend and the structure being traded
3. **M15** -- the setup and the level
4. **M5** -- the entry trigger only, never the reason for the trade

## Market structure

- **Uptrend**: successive higher highs and higher lows.
- **Downtrend**: successive lower highs and lower lows.
- **Range**: neither, and the honest description of a large share of trading
  hours.
- **Break of structure (BOS)**: a close beyond the prior swing point in the
  direction of the trend. Continuation.
- **Change of character (CHoCH)**: the first break against the prevailing
  sequence. A warning, not yet a reversal, and not an entry on its own.

The word "close" is doing real work in both definitions. A wick through a
level is not a break.

## Levels worth marking

In descending order of usefulness for intraday gold:

1. Prior day high and low
2. Current session high and low
3. Levels with at least two prior reactions
4. The prior day's close
5. Round numbers at 50 and 100 USD increments, which attract stop clusters

A level nobody has reacted to is a line, not a level.

## The four permitted setups

Every trade must be classified as one of these before entry, so the journal
can later evaluate each independently.

### 1. Trend pullback
Trend established on H1, price retraces to a level or a moving average, then
shows rejection. Entry on the rejection, stop beyond the retracement extreme,
target the prior swing. The highest-quality setup available intraday and the
one most often skipped in favour of something more exciting.

### 2. Level rejection
Price reaches a marked level from the reference list and is rejected with a
clear wick or an engulfing close. Entry on the close, stop beyond the wick,
target the opposite side of the range. Requires a genuine level, not a line.

### 3. Break and retest
Price closes beyond a level, returns to it, and holds. Entry on the hold,
stop beyond the retest low or high, target the next structural level. The
retest is not optional; entering on the break is chasing.

### 4. Session open continuation
The London or New York open produces a directional move that clears the prior
session's range and holds. Entry on the first pullback, stop beyond the open
range, target the next structural level. Time-limited and only valid in the
first 90 minutes of the session.

Anything not on this list is logged as `unclassified` and reviewed
separately. If unclassified trades come to dominate the journal, the plan has
stopped governing behaviour.

## Indicators

Indicators confirm, they do not decide. Each is a transformation of price,
which means none of them contains information price does not already carry.

- **EMA 20 / EMA 50**: dynamic support and resistance, trend context. Useful
  as a location filter.
- **RSI 14**: divergence is worth noting, absolute levels are not. "Overbought"
  in a strong trend is a description of strength, not a sell signal.
- **ATR 14**: the only reliable input for whether a target is reachable in the
  remaining session, and for sanity-checking stop width.
- **Volume**: on spot gold CFDs this is broker tick volume, not exchange
  volume. Treat it as a weak proxy and never as confirmation on its own.

If an indicator's parameters are not printed on the screenshot, its values
cannot be cited. Estimating an RSI reading from the shape of a line is
fabrication.

## Recurring intraday patterns

**Assumption flagged:** these are widely described tendencies in gold, useful
as context. They are not statistically validated here, they vary by regime,
and none is a basis for a trade on its own.

- The Asian session frequently ranges; that range's high and low often serve
  as reference levels for the London session.
- The London open often produces the day's directional move or a false break
  that sets up the reversal.
- The London/NY overlap carries the deepest liquidity and the largest
  sustained moves.
- Scheduled US data reprices gold in seconds, and the first move is frequently
  reversed within the following hour.
