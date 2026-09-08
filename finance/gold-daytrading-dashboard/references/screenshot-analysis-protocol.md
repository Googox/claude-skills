# Screenshot Analysis Protocol

The fixed procedure for turning a chart screenshot into a structured
assessment. The protocol exists so that every analysis is comparable to every
other one, and so that the boundary between observation and assumption is
never blurred by fluent prose.

## Step 0: Admissibility check

Before any analysis, confirm the screenshot carries:

- **Symbol** (XAUUSD or equivalent)
- **Timeframe** of the chart
- **Timestamp or the current candle's time**
- **Price axis** legible enough to read levels
- **Indicator parameters**, if indicators are to be referenced

If any of these is missing, say so and analyse only what remains supportable.
Do not infer a timeframe from candle appearance. Do not estimate the time
from the number of candles.

**Staleness statement is mandatory.** Every analysis opens with how old the
screenshot is and what that means. Gold can move 5 to 15 USD on the M5 in the
minutes between capture and response. An analysis delivered against a
fifteen-minute-old screenshot is commentary on the past.

## Step 1: Separate facts from assumptions

Two explicit lists, always:

- **Observed**: what is legible in the image. Price levels, candle structure,
  printed indicator values, marked levels, session boundaries.
- **Assumed**: everything else. Higher timeframe context not shown, indicator
  parameters not printed, the news calendar, the current spread, whether the
  screenshot is current.

Anything that cannot go in the first list is stated as an assumption or left
out. A reading that requires an unstated assumption is not an analysis.

## Step 2: Structure

Read the chart in this order, and report it in this order:

1. **Higher timeframe context** (if supplied): trend direction, position
   within the larger range.
2. **Market structure on the entry timeframe**: the sequence of highs and
   lows. Higher highs with higher lows, lower highs with lower lows, or
   neither. Name the specific swing points by price.
3. **Key levels**: prior day high and low, session high and low, levels with
   at least two touches. Give prices, not adjectives.
4. **Current location**: where price sits relative to those levels. Mid-range
   is a valid and common answer, and usually argues for no trade.

## Step 3: Bias

One of exactly three outcomes. "Kein Trade" is the default and requires no
justification; the other two do.

- **LONG** with the specific reason
- **SHORT** with the specific reason
- **NO TRADE** because structure is unclear, price is mid-range, the reward
  to risk does not clear 1.5, or a hard veto applies

If the honest answer is that the chart shows nothing actionable, that is the
answer. Manufacturing a bias to be useful is the single most damaging thing
this protocol can do.

## Step 4: Trade parameters

Only if the bias is LONG or SHORT.

| Parameter | Rule |
|-----------|------|
| Entry | A specific price or a narrow zone, with the trigger that activates it |
| Stop | At the structural invalidation level, never at a round loss amount |
| Target 1 | The nearest structural level, typically for partial exit |
| Target 2 | The next structural level |
| R:R | Computed to Target 1. Below 1.5 the trade is void |
| Invalidation | The condition under which the whole idea is abandoned before entry |

Run the numbers through `scripts/position_sizer.py`. Do not state a position
size that has not been computed.

## Step 5: Confidence and counter-case

Two mandatory closing elements:

- **Confidence**, stated as low, medium or high, with the reason. High
  confidence requires higher-timeframe alignment, a clean structural level,
  and reward to risk above 2. It is rare.
- **The counter-case**: the strongest argument against the bias, stated
  seriously. If no counter-case can be constructed, the analysis is
  incomplete, not the setup strong.

## Step 6: Mandatory closing statement

Every analysis ends with the same disclosure, unabbreviated:

> This is a structured reading of a static image, not a forecast and not
> investment advice. It carries no verified edge. The decision, the position
> and the outcome are yours.

## Output template

```
STALENESS: screenshot timestamp <x>, analysed at <y>, age <n> minutes.
OBSERVED: <legible facts, with prices>
ASSUMED: <every assumption, named>
STRUCTURE: <HTF context / swing sequence / key levels / current location>
BIAS: LONG | SHORT | NO TRADE  -- <reason>
ENTRY: <price or zone + trigger>
STOP: <price> -- invalidation because <structural reason>
TARGET 1: <price>   TARGET 2: <price>
R:R to T1: <value>  (floor 1.5)
POSITION: <lots, from position_sizer.py>
CONFIDENCE: low | medium | high -- <reason>
COUNTER-CASE: <the strongest argument against this bias>
VETOES: <news window / daily limit / trade count / none>
DISCLOSURE: <closing statement, verbatim>
```

## Things this protocol will not do

- Produce a bias when the chart does not support one
- Quote an indicator value that is not legible in the image
- Treat a screenshot as current without a timestamp
- Assign a probability to the trade working
- Recommend increasing size to recover a loss
