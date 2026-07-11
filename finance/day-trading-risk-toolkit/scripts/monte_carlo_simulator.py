#!/usr/bin/env python3
"""Monte Carlo simulator for day trading strategies.

Simulates thousands of possible equity curves from a trading strategy's
core parameters (win rate, risk/reward ratio, risk per trade, costs) and
reports risk of ruin, drawdown distribution, losing-streak probabilities,
and final-equity percentiles.

Purpose: stress-test a trading plan BEFORE risking real money. A daily
profit target only tells you the best case — this tool shows the full
distribution of outcomes, including the bad ones.

Standard library only. No market data or API calls.
"""

import argparse
import json
import random
import statistics
import sys


def wilson_interval(wins, n, z=1.96):
    """95% Wilson score confidence interval for an observed win rate."""
    if n == 0:
        return (0.0, 1.0)
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = (z / denom) * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (max(0.0, center - margin), min(1.0, center + margin))


def simulate(params, rng):
    """Run one equity curve. Returns (final_equity, max_drawdown, ruined, max_loss_streak)."""
    equity = params["capital"]
    peak = equity
    max_dd = 0.0
    streak = 0
    max_streak = 0
    ruin_level = params["capital"] * params["ruin_pct"] / 100.0
    total_trades = params["days"] * params["trades_per_day"]

    for _ in range(total_trades):
        if equity <= ruin_level:
            return equity, max_dd, True, max_streak

        if params["risk_mode"] == "percent":
            risk = equity * params["risk_pct"] / 100.0
        else:
            risk = params["risk_eur"]

        if rng.random() < params["win_rate"]:
            equity += risk * params["rr"] - params["cost_per_trade"]
            streak = 0
        else:
            equity -= risk + params["cost_per_trade"]
            streak += 1
            max_streak = max(max_streak, streak)

        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak)

    return equity, max_dd, equity <= ruin_level, max_streak


def run_simulation(params):
    rng = random.Random(params["seed"])
    finals, drawdowns, streaks = [], [], []
    ruins = 0

    for _ in range(params["runs"]):
        final, dd, ruined, max_streak = simulate(params, rng)
        finals.append(final)
        drawdowns.append(dd)
        streaks.append(max_streak)
        if ruined:
            ruins += 1

    finals.sort()

    def pct(p):
        return finals[min(len(finals) - 1, int(len(finals) * p))]

    risk_desc = (
        f"{params['risk_pct']}% of equity"
        if params["risk_mode"] == "percent"
        else f"EUR {params['risk_eur']:,.0f} fixed"
    )
    ev_per_trade = (
        params["win_rate"] * params["rr"] - (1 - params["win_rate"])
    )  # in R multiples, before costs

    return {
        "inputs": {
            "capital_eur": params["capital"],
            "win_rate": params["win_rate"],
            "risk_reward_ratio": params["rr"],
            "risk_per_trade": risk_desc,
            "cost_per_trade_eur": params["cost_per_trade"],
            "trades_per_day": params["trades_per_day"],
            "trading_days": params["days"],
            "simulation_runs": params["runs"],
        },
        "expectancy_R_before_costs": round(ev_per_trade, 3),
        "risk_of_ruin_pct": round(100.0 * ruins / params["runs"], 2),
        "final_equity_eur": {
            "p5_worst": round(pct(0.05)),
            "p25": round(pct(0.25)),
            "median": round(pct(0.50)),
            "p75": round(pct(0.75)),
            "p95_best": round(pct(0.95)),
        },
        "max_drawdown_pct": {
            "mean": round(100 * statistics.mean(drawdowns), 1),
            "worst_5pct_of_runs": round(
                100 * sorted(drawdowns)[int(len(drawdowns) * 0.95)], 1
            ),
        },
        "loss_streaks": {
            "mean_longest_streak": round(statistics.mean(streaks), 1),
            "pct_of_runs_with_5plus_losses_in_a_row": round(
                100.0 * sum(1 for s in streaks if s >= 5) / len(streaks), 1
            ),
        },
    }


def build_verdict(result):
    """Plain-language interpretation of the simulation."""
    lines = []
    ev = result["expectancy_R_before_costs"]
    if ev <= 0:
        lines.append(
            "NEGATIVE EXPECTANCY: with these parameters the strategy loses money "
            "on average. No position sizing can fix a negative edge — ruin is a "
            "question of time, not luck."
        )
    ror = result["risk_of_ruin_pct"]
    if ror >= 5:
        lines.append(
            f"Risk of ruin is {ror}%. Anything above ~1% means the position size "
            "is too large for the edge. Reduce risk per trade."
        )
    dd = result["max_drawdown_pct"]["mean"]
    if dd >= 20:
        lines.append(
            f"Average maximum drawdown is {dd}%. A {dd:.0f}% loss requires a "
            f"{100 * dd / (100 - dd):.0f}% gain just to get back to break-even. "
            "Most traders abandon a strategy (or worse, revenge-trade) long "
            "before surviving a drawdown like this."
        )
    streak = result["loss_streaks"]["pct_of_runs_with_5plus_losses_in_a_row"]
    if streak >= 25:
        lines.append(
            f"{streak}% of simulated years contain 5+ consecutive losses. "
            "The trading plan must define in advance what happens then."
        )
    lines.append(
        "CRITICAL CAVEAT: this simulation ASSUMES the win rate you entered is "
        "real. A win rate is only credible after 100+ logged trades (see "
        "trading_journal.py, which computes the confidence interval). Claimed "
        "win rates from demo accounts, backtests without costs, or short "
        "streaks are not evidence."
    )
    return lines


def format_human(result):
    i = result["inputs"]
    out = []
    out.append("=" * 68)
    out.append("MONTE CARLO STRATEGY SIMULATION")
    out.append("=" * 68)
    out.append(f"Capital:            EUR {i['capital_eur']:,.0f}")
    out.append(f"Win rate (assumed): {i['win_rate']:.0%}")
    out.append(f"Risk/reward:        1:{i['risk_reward_ratio']}")
    out.append(f"Risk per trade:     {i['risk_per_trade']}")
    out.append(f"Costs per trade:    EUR {i['cost_per_trade_eur']}")
    out.append(
        f"Horizon:            {i['trading_days']} days x "
        f"{i['trades_per_day']} trades = "
        f"{i['trading_days'] * i['trades_per_day']} trades"
    )
    out.append(f"Simulations:        {i['simulation_runs']:,}")
    out.append("-" * 68)
    out.append(f"Expectancy:         {result['expectancy_R_before_costs']:+.2f} R per trade (before costs)")
    out.append(f"Risk of ruin:       {result['risk_of_ruin_pct']}%")
    fe = result["final_equity_eur"]
    out.append("Final equity:")
    out.append(f"  worst 5%:         EUR {fe['p5_worst']:,}")
    out.append(f"  median:           EUR {fe['median']:,}")
    out.append(f"  best 5%:          EUR {fe['p95_best']:,}")
    dd = result["max_drawdown_pct"]
    out.append(f"Max drawdown:       {dd['mean']}% average, {dd['worst_5pct_of_runs']}% in worst 5% of runs")
    ls = result["loss_streaks"]
    out.append(
        f"Loss streaks:       longest streak averages {ls['mean_longest_streak']} losses; "
        f"{ls['pct_of_runs_with_5plus_losses_in_a_row']}% of runs see 5+ in a row"
    )
    out.append("-" * 68)
    out.append("INTERPRETATION:")
    for line in build_verdict(result):
        out.append(f"  * {line}")
    out.append("=" * 68)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Monte Carlo simulation of a day trading strategy"
    )
    parser.add_argument("--capital", type=float, default=10_000, help="Starting capital in EUR (default: 10000)")
    parser.add_argument("--win-rate", type=float, required=True, help="Assumed win rate, e.g. 0.65")
    parser.add_argument("--rr", type=float, default=1.0, help="Risk/reward ratio, e.g. 1.5 means wins are 1.5x losses (default: 1.0)")
    parser.add_argument("--risk-pct", type=float, help="Risk per trade as %% of current equity (recommended: 0.5-2)")
    parser.add_argument("--risk-eur", type=float, help="Fixed risk per trade in EUR (alternative to --risk-pct)")
    parser.add_argument("--cost-per-trade", type=float, default=5.0, help="Spread/slippage/commission per trade in EUR (default: 5)")
    parser.add_argument("--trades-per-day", type=int, default=2, help="Trades per day (default: 2)")
    parser.add_argument("--days", type=int, default=250, help="Trading days to simulate (default: 250 = 1 year)")
    parser.add_argument("--ruin-pct", type=float, default=50.0, help="Equity %% of start considered 'ruin' (default: 50)")
    parser.add_argument("--runs", type=int, default=10_000, help="Number of simulations (default: 10000)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--format", choices=["human", "json"], default="human")
    args = parser.parse_args()

    if not 0 < args.win_rate < 1:
        print("Error: --win-rate must be between 0 and 1 (e.g. 0.65)", file=sys.stderr)
        return 2
    if (args.risk_pct is None) == (args.risk_eur is None):
        print("Error: specify exactly one of --risk-pct or --risk-eur", file=sys.stderr)
        return 2

    params = {
        "capital": args.capital,
        "win_rate": args.win_rate,
        "rr": args.rr,
        "risk_mode": "percent" if args.risk_pct is not None else "fixed",
        "risk_pct": args.risk_pct or 0.0,
        "risk_eur": args.risk_eur or 0.0,
        "cost_per_trade": args.cost_per_trade,
        "trades_per_day": args.trades_per_day,
        "days": args.days,
        "ruin_pct": args.ruin_pct,
        "runs": args.runs,
        "seed": args.seed,
    }

    result = run_simulation(params)
    if args.format == "json":
        result["interpretation"] = build_verdict(result)
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
