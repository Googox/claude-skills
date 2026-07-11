# Risk Management Basics for Intraday Trading

Expert knowledge base for the day-trading-risk-toolkit. Covers the arithmetic
that decides survival, instrument-specific facts for NASDAQ 100 and Gold, and
realistic benchmarks.

## 1. Expectancy — the Only Number That Matters

Every strategy reduces to one formula:

```
Expectancy per trade = (WinRate x AvgWin) - (LossRate x AvgLoss) - Costs
```

- Positive expectancy + correct sizing = survivable strategy
- Negative expectancy = **no position sizing, discipline, or psychology can
  save it**; losses are a mathematical certainty over enough trades
- Costs (spread, commission, slippage, financing) are paid on EVERY trade,
  win or lose. At 2 trades/day, 500 trades/year, EUR 5 of cost per trade is
  EUR 2,500/year — 25% of a EUR 10,000 account, silently.

**Worked example — the "EUR 1,000/day from EUR 10,000" plan:**
2 trades/day must average EUR +500 each. At a 75% win rate with 1:1
risk/reward: `0.75W - 0.25W = 0.5W = 500` → each trade must risk **EUR 1,000
= 10% of the account**. That is 5-20x the professional risk standard, and it
assumes an elite edge (see §5) is already proven.

## 2. Drawdown Arithmetic Is Asymmetric

| Loss | Gain required to recover |
|------|--------------------------|
| -10% | +11% |
| -20% | +25% |
| -30% | +43% |
| -50% | +100% |
| -70% | +233% |

Losing streaks are normal, not exceptional. Probability of at least 5
consecutive losses somewhere within 500 trades:

| True win rate | P(5+ loss streak in a year) |
|---------------|------------------------------|
| 65% | ~82% |
| 75% | ~30% |
| 85% | ~3% |

At 10% risk per trade, the near-certain 5-loss streak at a 65% win rate means
a ~40-50% drawdown in one bad week. Most traders break their rules (or their
account) at that point. At 1% risk per trade the same streak costs ~5%.

## 3. Position Sizing: the Fixed-Fractional Standard

```
Position size = (Equity x Risk%) / (StopDistance x ValuePerPoint)
```

- **Professional standard: 0.5-2% of equity per trade.** Full-time
  discretionary traders commonly use 0.25-1%.
- Risk is defined by the stop-loss, not by hope. No stop = undefined risk =
  not a trade, a gamble.
- A daily loss limit (e.g. 2-3% of equity, i.e. 2-3 losing trades) stops the
  worst days early. The best traders' edge is partly that their bad days are
  small.

## 4. Leverage, Margin, and EU Retail Rules (ESMA)

CFD leverage caps for EU retail clients (ESMA product intervention measures):

| Instrument class | Max leverage |
|------------------|--------------|
| Major FX pairs | 30:1 |
| Major indices (incl. NASDAQ 100), gold | 20:1 |
| Other commodities, minor indices | 10:1 |
| Individual stocks | 5:1 |
| Crypto | 2:1 |

Consequences for a EUR 10,000 account:
- Max notional on NASDAQ/gold CFDs: EUR 200,000. A 0.5% adverse move on full
  leverage = EUR 1,000 = 10% of the account.
- Brokers must provide negative balance protection (retail cannot lose more
  than the account), but margin close-out at 50% of required margin means
  volatile moves liquidate positions at the worst prices.
- Micro futures (MNQ: USD 2/point; MGC: USD 10/point) are an alternative with
  tighter spreads but require meaningful intraday margin per contract; a EUR
  10,000 account supports only very small futures positions with proper risk.

## 5. Realistic Benchmarks

- **Chague & De-Losso (FGV Brazil, 2020):** of ~20,000 futures day traders
  tracked, 97% of those persisting 300+ days lost money; ~1.1% earned more
  than minimum wage; ~0.5% earned more than a bank teller.
- **CFD broker disclosures (EU-mandated):** typically 70-80% of retail
  accounts lose money.
- **World-class fund benchmarks:** the best hedge funds in history averaged
  ~30-70% per YEAR (Medallion, gross). A "modest" EUR 1,000/day on EUR 10,000
  is ~2,500% per year without compounding — 35x the best fund ever.
- **Credible retail success:** consistently profitable retail day traders —
  the rare ones — typically target 1-5% per month on their risk capital, with
  drawdowns respected and months of loss expected.

A claimed win rate is only evidence after **100+ logged trades including all
costs** (the journal tool computes the confidence interval). A 65% win rate
observed over 20 trades is statistically compatible with a true rate of ~43%.

## 6. Session Characteristics (the User's Chosen Windows)

**NASDAQ 100, US cash open (15:30-17:00 CET / 9:30-11:00 ET):**
- Highest volume and volatility of the US session; opening range moves fast
- Spreads on CFDs widen at the open; slippage on stops is common
- News (economic data at 14:30/16:00 CET) can gap through stops
- Typical intraday range 0.5-1.5%; stop distances under ~20-40 points get
  stopped by noise

**Gold/XAUUSD (15:30-18:00 CET — the London/New York overlap):**
- Deepest liquidity of the day; COMEX open and US data drive direction
- Highly sensitive to USD, real yields, and geopolitical headlines — a
  headline can move USD 10-20 in minutes, straight through a stop
- Margin requirements rise around FOMC and CPI releases

Note: the user's stated windows ("NASDAQ 9:30-11:00, XAU 15:30-18:00") mix
time zones — NASDAQ 9:30-11:00 ET **is** 15:30-17:00 CET, the same clock
hours as the gold window. Both sessions overlap in real time; trading both
simultaneously doubles concurrent risk and attention load.

## 7. Cost Drag — the Silent Edge Killer

Per round trip on a typical retail CFD account:
- NASDAQ 100: ~2 points spread (~EUR 2 per EUR 1/point contract) + slippage
- XAUUSD: ~USD 0.3 spread per oz + slippage
- Overnight financing if held past session (avoid for intraday plans)

A strategy that backtests at 60% wins with 1:1 R/R has its edge roughly
halved by realistic costs on tight intraday stops. **Always re-run the Monte
Carlo simulation with the win rate reduced by 5-15 points to account for
this.**

## 8. Safer Paths for the Same Ambition

For someone determined to build trading skill without risking ruin:

1. **Demo first, statistically:** 100+ logged paper trades before any real
   money; the journal's confidence interval decides, not feelings.
2. **Funded/prop accounts:** evaluation firms provide capital (with strict
   drawdown rules) so personal savings are not the risk buffer. The
   evaluation fee caps the downside — but note that these firms profit
   because most participants fail the drawdown rules; treat the fee as
   tuition, not an investment.
3. **Longer timeframes:** swing trading (days-weeks) has lower cost drag,
   less noise, and is compatible with a job — no dependence on trading
   income while learning.
4. **Baseline comparison:** EUR 10,000 in a broad index ETF has returned
   ~7-10%/year historically with zero hours of work. Any trading plan must
   honestly beat that risk-adjusted, after costs and taxes, to make sense.
5. **Income realism:** financial independence from trading requires capital.
   Even an excellent, proven 5%/month edge on EUR 10,000 is EUR 500/month
   before taxes. The reliable path is: prove the edge small → grow capital
   from other income → scale slowly.

## 9. Tax Note (Germany)

Gains from CFDs and futures are capital income (Kapitalerträge), generally
subject to Abgeltungsteuer (25% + Solidaritätszuschlag, plus church tax where
applicable). Loss offset rules for derivatives have changed repeatedly in
recent years — a trader must confirm the current treatment with a
Steuerberater before assuming net-income figures. "EUR 1,000/day" is a
pre-tax fantasy twice over.
