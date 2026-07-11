#!/usr/bin/env python3
"""CSV-based trading journal with statistical honesty built in.

Logs trades to a plain CSV file and computes performance statistics —
including a 95% confidence interval on the win rate, which shows how many
trades are actually needed before a claimed win rate ("65-85%") is
statistically credible.

Subcommands:
  init   Create a new journal CSV
  add    Append a trade
  stats  Compute performance statistics

Standard library only. The CSV is portable to Excel/Sheets.
"""

import argparse
import csv
import json
import os
import sys
from datetime import date

COLUMNS = [
    "date",
    "instrument",
    "direction",
    "entry",
    "exit",
    "size",
    "pnl_eur",
    "risk_eur",
    "setup",
    "notes",
]


def wilson_interval(wins, n, z=1.96):
    """95% Wilson score confidence interval for a win rate."""
    if n == 0:
        return (0.0, 1.0)
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = (z / denom) * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (max(0.0, center - margin), min(1.0, center + margin))


def cmd_init(args):
    if os.path.exists(args.file) and not args.force:
        print(f"Error: {args.file} already exists (use --force to overwrite)", file=sys.stderr)
        return 2
    with open(args.file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(COLUMNS)
    print(f"Journal created: {args.file}")
    return 0


def cmd_add(args):
    if not os.path.exists(args.file):
        print(f"Error: journal {args.file} not found — run 'init' first", file=sys.stderr)
        return 2
    row = [
        args.date or date.today().isoformat(),
        args.instrument,
        args.direction,
        args.entry,
        args.exit,
        args.size,
        args.pnl,
        args.risk,
        args.setup or "",
        args.notes or "",
    ]
    with open(args.file, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    print(f"Trade logged: {args.instrument} {args.direction} P&L EUR {args.pnl:+.2f}")
    return 0


def load_trades(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        trades = []
        for row in reader:
            try:
                trades.append(
                    {
                        "date": row["date"],
                        "instrument": row["instrument"],
                        "pnl": float(row["pnl_eur"]),
                        "risk": float(row["risk_eur"]) if row.get("risk_eur") else None,
                    }
                )
            except (KeyError, ValueError) as exc:
                print(f"Warning: skipping malformed row {row}: {exc}", file=sys.stderr)
        return trades


def compute_stats(trades):
    n = len(trades)
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    total_pnl = sum(t["pnl"] for t in trades)

    win_rate = len(wins) / n if n else 0.0
    ci_low, ci_high = wilson_interval(len(wins), n)

    avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0.0
    avg_loss = sum(t["pnl"] for t in losses) / len(losses) if losses else 0.0
    gross_profit = sum(t["pnl"] for t in wins)
    gross_loss = abs(sum(t["pnl"] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
    expectancy = total_pnl / n if n else 0.0

    # max drawdown of the cumulative P&L curve
    cum = peak = max_dd = 0.0
    worst_streak = streak = 0
    for t in trades:
        cum += t["pnl"]
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
        if t["pnl"] <= 0:
            streak += 1
            worst_streak = max(worst_streak, streak)
        else:
            streak = 0

    return {
        "trades": n,
        "total_pnl_eur": round(total_pnl, 2),
        "win_rate_observed": round(win_rate, 3),
        "win_rate_95pct_confidence_interval": [round(ci_low, 3), round(ci_high, 3)],
        "avg_win_eur": round(avg_win, 2),
        "avg_loss_eur": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor else None,
        "expectancy_eur_per_trade": round(expectancy, 2),
        "max_drawdown_eur": round(max_dd, 2),
        "worst_loss_streak": worst_streak,
    }


def cmd_stats(args):
    if not os.path.exists(args.file):
        print(f"Error: journal {args.file} not found", file=sys.stderr)
        return 2
    trades = load_trades(args.file)
    if not trades:
        print("No trades logged yet.")
        return 0
    stats = compute_stats(trades)

    if args.format == "json":
        print(json.dumps(stats, indent=2))
        return 0

    ci = stats["win_rate_95pct_confidence_interval"]
    print("=" * 68)
    print("TRADING JOURNAL STATISTICS")
    print("=" * 68)
    print(f"Trades logged:      {stats['trades']}")
    print(f"Total P&L:          EUR {stats['total_pnl_eur']:+,.2f}")
    print(f"Win rate:           {stats['win_rate_observed']:.1%}")
    print(f"  95% CI:           {ci[0]:.1%} - {ci[1]:.1%}")
    print(f"Avg win / loss:     EUR {stats['avg_win_eur']:+,.2f} / EUR {stats['avg_loss_eur']:+,.2f}")
    pf = stats["profit_factor"]
    print(f"Profit factor:      {pf if pf is not None else 'n/a (no losses yet)'}")
    print(f"Expectancy:         EUR {stats['expectancy_eur_per_trade']:+,.2f} per trade")
    print(f"Max drawdown:       EUR {stats['max_drawdown_eur']:,.2f}")
    print(f"Worst loss streak:  {stats['worst_loss_streak']}")
    print("-" * 68)
    width = ci[1] - ci[0]
    if width > 0.15:
        print(
            f"NOTE: with only {stats['trades']} trades the true win rate could be "
            f"anywhere between {ci[0]:.0%} and {ci[1]:.0%}. Claims like 'my win "
            "rate is 65-85%' need 100+ logged trades to be credible. Keep "
            "logging before increasing position size."
        )
    print("=" * 68)
    return 0


def main():
    parser = argparse.ArgumentParser(description="CSV trading journal with honest statistics")
    parser.add_argument("--file", default="trading_journal.csv", help="Journal CSV path (default: trading_journal.csv)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new journal")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing file")

    p_add = sub.add_parser("add", help="Log a trade")
    p_add.add_argument("--date", help="Trade date YYYY-MM-DD (default: today)")
    p_add.add_argument("--instrument", required=True, help="e.g. NAS100, XAUUSD")
    p_add.add_argument("--direction", choices=["long", "short"], required=True)
    p_add.add_argument("--entry", type=float, required=True)
    p_add.add_argument("--exit", type=float, required=True)
    p_add.add_argument("--size", type=float, required=True, help="Position size (units/contracts)")
    p_add.add_argument("--pnl", type=float, required=True, help="Realized P&L in EUR incl. costs")
    p_add.add_argument("--risk", type=float, required=True, help="EUR risked at the stop")
    p_add.add_argument("--setup", help="Setup name, e.g. 'opening range breakout'")
    p_add.add_argument("--notes", help="Free-form notes")

    p_stats = sub.add_parser("stats", help="Compute statistics")
    p_stats.add_argument("--format", choices=["human", "json"], default="human")

    args = parser.parse_args()
    return {"init": cmd_init, "add": cmd_add, "stats": cmd_stats}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
