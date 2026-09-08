# XAUUSD Instrument Facts

Reference sheet for spot gold as traded through a retail CFD or spot broker.
Contract details vary by broker. Verify every line below against your own
broker's contract specification before sizing a single trade.

## Contract convention

| Item | Standard convention |
|------|--------------------|
| Symbol | XAUUSD (spot gold against US dollar) |
| Quote | US dollars per troy ounce |
| Standard lot | 100 troy ounces |
| Mini lot | 10 troy ounces (0.10 lots) |
| Micro lot | 1 troy ounce (0.01 lots) |
| Value of a 1.00 USD price move | 100 USD per standard lot |
| Typical quote precision | Two decimals (0.01 USD) |

A 10 USD move against a 1.00 lot position is 1,000 USD. Gold routinely moves
10 to 30 USD in a single session. Position size, not conviction, is what
keeps that survivable.

## Currency exposure for a EUR account

Gold is priced in USD. A EUR-denominated account carries two exposures at
once: the gold price and EURUSD. Profit and loss is computed in USD and
converted at the prevailing rate, so the EUR result of a winning gold trade
can shrink if the dollar weakens in the meantime.

Position sizing must therefore convert the EUR risk budget into USD before
computing lots. `scripts/position_sizer.py` does this via `--usd-rate`
(account-currency units per one USD).

## Costs

Costs are the reason a 50 percent hit rate at 1:1 loses money.

- **Spread**: typically 0.15 to 0.50 USD per ounce in liquid hours, wider in
  the Asian session and around news. On a 7.50 USD stop, a 0.30 USD spread is
  4 percent of the risk consumed at entry.
- **Commission**: broker-dependent, often charged per lot per side.
- **Swap / financing**: charged on positions held past the daily rollover.
  Irrelevant for genuine intraday trading, material if a "day trade" becomes
  an overnight hold because the trader will not accept the loss.

Measure your real round-trip cost from broker statements and feed it into
`trade_journal.py --cost-r`. The 0.05R default is a placeholder.

## Sessions

Times are approximate and shift with daylight saving in each region. Verify
against your platform clock; the ranges below are given in Central European
Time during European summer time (CEST, UTC+2).

| Session | CEST (approx.) | Character for gold |
|---------|----------------|--------------------|
| Asia | 01:00 to 09:00 | Thin liquidity, wider spreads, range-bound more often than not, prone to false breaks |
| London | 09:00 to 18:00 | Liquidity arrives, the day's directional move often begins |
| London/NY overlap | 15:30 to 18:00 | Deepest liquidity, tightest spreads, largest sustained moves |
| New York | 15:30 to 22:00 | Driven by US data and dollar flow |

If the intention is a small number of high-quality trades, the overlap is
where they live. Trading gold at 23:00 CEST is a decision to accept worse
prices for less opportunity.

## What actually moves gold

Gold is primarily a real-interest-rate and dollar instrument, with a
secondary risk-premium component.

- **US inflation prints (CPI, PPI)** and **labour data (NFP)**: the largest
  scheduled intraday moves. Stops are not reliable through these releases.
- **FOMC decisions, minutes and Fed speakers**: expectations about real rates
  move gold more than the decision itself.
- **US dollar index and US real yields**: the dominant day-to-day drivers.
  Gold and real yields are usually inversely related.
- **Geopolitical escalation**: sharp, fast, and typically mean-reverting once
  the headline is absorbed.
- **Central bank buying and ETF flows**: structurally important, rarely the
  cause of an intraday move.

**Assumption flagged:** the relationships above are the conventional
description of gold's drivers and hold over long samples. They are not
reliable on any individual day, and they are not a forecasting tool.

## Known limits of screenshot-based analysis

A chart image supports analysis of structure, levels and visible indicator
values. It does not support:

- Verification that the image is current. A screenshot ages from the moment
  it is taken.
- Reading the order book, spread, or actual fill quality.
- Confirming indicator parameters unless they are printed on the chart.
- Any claim about what price will do next.

Every screenshot must carry its timestamp and timeframe, or the analysis
rests on an unstated assumption about both.
