#!/usr/bin/env python3
"""Trade journal and expectancy analysis for XAUUSD day trading.

This is the only part of the toolkit that can tell the trader the truth.
Everything else is preparation; this measures what actually happened. It
reports expectancy in R, because R is the only unit that survives changes in
account size and position size.

The verdict at the end is deliberately blunt. A journal that flatters is
worse than no journal.

Usage:
    python3 trade_journal.py add --date 2026-09-08 --direction long \
        --entry 2412.50 --stop 2405.00 --exit 2427.50 --setup breakout \
        --session overlap --score 94 --note "clean pullback into PDH"

    python3 trade_journal.py stats
    python3 trade_journal.py stats --by setup --json
    python3 trade_journal.py list --last 10
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "assets", "trade-journal.csv")

FIELDS = ["date", "direction", "entry", "stop", "exit", "r_multiple",
          "setup", "session", "score", "followed_plan", "note"]

# A statistically meaningless sample below this count. Any conclusion drawn
# from fewer trades is a story, not a result.
MIN_SAMPLE = 30

# Round-trip transaction cost as a fraction of R, used to show gross vs net.
# 0.05R is a rough placeholder for spread plus commission on a typical
# 7 to 10 USD stop; recalibrate it from real broker statements.
DEFAULT_COST_R = 0.05


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return [row for row in csv.DictReader(fh)]


def save(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def compute_r(entry, stop, exit_price, direction):
    """R-multiple actually realised, signed."""
    risk = abs(entry - stop)
    if risk < 1e-9:
        raise ValueError("entry and stop cannot be identical")
    move = (exit_price - entry) if direction == "long" else (entry - exit_price)
    return move / risk


def add_trade(path, args):
    direction = args.direction
    if direction == "auto":
        direction = "long" if args.stop < args.entry else "short"

    r = compute_r(args.entry, args.stop, args.exit, direction)
    rows = load(path)
    rows.append({
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "direction": direction,
        "entry": "%.2f" % args.entry,
        "stop": "%.2f" % args.stop,
        "exit": "%.2f" % args.exit,
        "r_multiple": "%.3f" % r,
        "setup": args.setup or "unclassified",
        "session": args.session or "unknown",
        "score": "" if args.score is None else str(args.score),
        "followed_plan": args.followed_plan,
        "note": args.note or "",
    })
    save(path, rows)
    print("Logged %s %s -> %s  =  %+.2fR   (%d trades on file)"
          % (direction, args.entry, args.exit, r, len(rows)))
    if args.followed_plan == "no":
        print("Marked as off-plan. These are the trades to read first when the "
              "expectancy comes out negative.")
    return 0


def summarise(rs, cost_r=DEFAULT_COST_R):
    """Core statistics for a list of R-multiples."""
    n = len(rs)
    if n == 0:
        return None

    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))

    hit_rate = len(wins) / n * 100.0
    avg_win = (gross_win / len(wins)) if wins else 0.0
    avg_loss = (gross_loss / len(losses)) if losses else 0.0
    expectancy = sum(rs) / n
    expectancy_net = expectancy - cost_r
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else float("inf")

    # Equity curve in R and maximum drawdown from peak.
    equity, peak, max_dd = 0.0, 0.0, 0.0
    for r in rs:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    # Longest losing streak, the number that actually breaks accounts.
    streak, worst_streak = 0, 0
    for r in rs:
        streak = streak + 1 if r <= 0 else 0
        worst_streak = max(worst_streak, streak)

    # Break-even hit rate implied by the realised win/loss sizes.
    if avg_win + avg_loss > 0:
        be_hit_rate = avg_loss / (avg_win + avg_loss) * 100.0
    else:
        be_hit_rate = float("nan")

    return {
        "trades": n,
        "hit_rate_pct": round(hit_rate, 1),
        "breakeven_hit_rate_pct": round(be_hit_rate, 1),
        "avg_win_r": round(avg_win, 2),
        "avg_loss_r": round(avg_loss, 2),
        "expectancy_r": round(expectancy, 3),
        "expectancy_r_net": round(expectancy_net, 3),
        "assumed_cost_r": cost_r,
        "total_r": round(sum(rs), 2),
        "profit_factor": (round(profit_factor, 2)
                          if profit_factor != float("inf") else None),
        "max_drawdown_r": round(max_dd, 2),
        "longest_losing_streak": worst_streak,
    }


def verdict(stats):
    n = stats["trades"]
    net = stats["expectancy_r_net"]

    if n < MIN_SAMPLE:
        return ("INSUFFICIENT DATA",
                "%d of %d trades. Nothing here is a result yet. Keep logging "
                "and do not change the system on the strength of this sample."
                % (n, MIN_SAMPLE))
    if net > 0.15:
        return ("POSITIVE EXPECTANCY",
                "Net %+.3fR per trade over %d trades. The system pays. Do not "
                "increase risk faster than the sample grows." % (net, n))
    if net > 0.0:
        return ("MARGINAL",
                "Net %+.3fR per trade. Above water, but inside the range where "
                "a run of bad luck or one cost increase erases it. Not yet a "
                "reason to size up." % net)
    return ("NEGATIVE EXPECTANCY",
            "Net %+.3fR per trade over %d trades. On this evidence the system "
            "loses money. The honest options are to stop, or to change one "
            "variable and re-measure over another %d trades. Continuing "
            "unchanged is the expensive option." % (net, n, MIN_SAMPLE))


def group_stats(rows, key, cost_r):
    groups = {}
    for row in rows:
        groups.setdefault(row.get(key) or "unknown", []).append(float(row["r_multiple"]))
    return {k: summarise(v, cost_r) for k, v in sorted(groups.items())}


def render_stats(stats, groups, group_key, off_plan):
    lines = []
    lines.append("TRADE JOURNAL STATISTICS")
    lines.append("")
    lines.append("Trades                  %d" % stats["trades"])
    lines.append("Hit rate                %.1f%%" % stats["hit_rate_pct"])
    lines.append("Break-even hit rate     %.1f%%   (what your R sizes require)"
                 % stats["breakeven_hit_rate_pct"])
    lines.append("Average win             %+.2fR" % stats["avg_win_r"])
    lines.append("Average loss            %-.2fR" % -stats["avg_loss_r"])
    lines.append("Expectancy gross        %+.3fR per trade" % stats["expectancy_r"])
    lines.append("Expectancy net          %+.3fR per trade  (cost %.2fR assumed)"
                 % (stats["expectancy_r_net"], stats["assumed_cost_r"]))
    lines.append("Total                   %+.2fR" % stats["total_r"])
    pf = stats["profit_factor"]
    lines.append("Profit factor           %s" % ("no losses yet" if pf is None else "%.2f" % pf))
    lines.append("Max drawdown            %.2fR" % stats["max_drawdown_r"])
    lines.append("Longest losing streak   %d trades" % stats["longest_losing_streak"])

    if groups:
        lines.append("")
        lines.append("BY %s" % group_key.upper())
        lines.append("%-16s %6s %8s %10s" % (group_key, "n", "hit%", "exp net R"))
        for name, s in groups.items():
            flag = "" if s["trades"] >= 10 else "  (thin sample)"
            lines.append("%-16s %6d %7.1f%% %+9.3f%s"
                         % (name[:16], s["trades"], s["hit_rate_pct"],
                            s["expectancy_r_net"], flag))

    if off_plan:
        lines.append("")
        lines.append("OFF-PLAN TRADES")
        lines.append("%d of %d trades were logged as off-plan, totalling %+.2fR."
                     % (off_plan["trades"], stats["trades"], off_plan["total_r"]))
        if off_plan["total_r"] < 0:
            lines.append("Removing them would have changed the total to %+.2fR. "
                         "Discipline, not analysis, is the binding constraint."
                         % (stats["total_r"] - off_plan["total_r"]))

    name, text = verdict(stats)
    lines.append("")
    lines.append("VERDICT: %s" % name)
    lines.append(text)
    return "\n".join(lines)


def stats_cmd(path, args):
    rows = load(path)
    if not rows:
        print("No trades logged yet. Journal file: %s" % os.path.normpath(path))
        return 0

    rs = [float(r["r_multiple"]) for r in rows]
    stats = summarise(rs, args.cost_r)
    groups = group_stats(rows, args.by, args.cost_r) if args.by else None

    off_rows = [r for r in rows if r.get("followed_plan") == "no"]
    off_plan = summarise([float(r["r_multiple"]) for r in off_rows], args.cost_r) if off_rows else None

    if args.json:
        payload = {"overall": stats, "verdict": dict(zip(("name", "text"), verdict(stats)))}
        if groups:
            payload["by_" + args.by] = groups
        if off_plan:
            payload["off_plan"] = off_plan
        print(json.dumps(payload, indent=2))
    else:
        print(render_stats(stats, groups, args.by or "", off_plan))
    return 0


def list_cmd(path, args):
    rows = load(path)
    if not rows:
        print("No trades logged yet.")
        return 0
    rows = rows[-args.last:] if args.last else rows
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    print("%-12s %-6s %9s %9s %9s %8s %-12s" %
          ("Date", "Dir", "Entry", "Stop", "Exit", "R", "Setup"))
    for r in rows:
        print("%-12s %-6s %9s %9s %9s %+8.2f %-12s"
              % (r["date"], r["direction"], r["entry"], r["stop"], r["exit"],
                 float(r["r_multiple"]), r["setup"][:12]))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Trade journal and expectancy analysis.")
    p.add_argument("--path", default=DEFAULT_PATH, help="Journal CSV path.")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Log a closed trade.")
    a.add_argument("--date", default=None, help="YYYY-MM-DD (default today).")
    a.add_argument("--direction", choices=["auto", "long", "short"], default="auto")
    a.add_argument("--entry", type=float, required=True)
    a.add_argument("--stop", type=float, required=True)
    a.add_argument("--exit", type=float, required=True, help="Actual exit price.")
    a.add_argument("--setup", default=None, help="Setup type from your plan.")
    a.add_argument("--session", default=None,
                   choices=["asia", "london", "overlap", "newyork", "offhours"])
    a.add_argument("--score", type=float, default=None, help="Pre-trade setup score.")
    a.add_argument("--followed-plan", choices=["yes", "no"], default="yes")
    a.add_argument("--note", default=None)

    s = sub.add_parser("stats", help="Expectancy and distribution statistics.")
    s.add_argument("--by", choices=["setup", "session", "direction", "followed_plan"],
                   default=None, help="Additional breakdown dimension.")
    s.add_argument("--cost-r", type=float, default=DEFAULT_COST_R,
                   help="Assumed round-trip cost in R (default %.2f)." % DEFAULT_COST_R)
    s.add_argument("--json", action="store_true")

    l = sub.add_parser("list", help="Show logged trades.")
    l.add_argument("--last", type=int, default=20)
    l.add_argument("--json", action="store_true")

    args = p.parse_args(argv)

    try:
        if args.cmd == "add":
            return add_trade(args.path, args)
        if args.cmd == "stats":
            return stats_cmd(args.path, args)
        return list_cmd(args.path, args)
    except ValueError as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
