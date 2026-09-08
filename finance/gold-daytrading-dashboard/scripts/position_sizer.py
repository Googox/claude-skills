#!/usr/bin/env python3
"""Position sizing and R-multiple calculator for XAUUSD (spot gold).

Deterministic risk math only. No market data, no forecasting, no LLM calls.
Every number the trader needs before entering a trade, derived from four
inputs: account balance, risk percent, entry price, stop price.

Contract convention used here:
    1 standard lot XAUUSD = 100 troy ounces
    A 1.00 USD move in the gold price = 100.00 USD per standard lot
    Minimum broker step defaults to 0.01 lots (= 1 ounce)

Usage:
    python3 position_sizer.py --balance 25000 --risk-pct 0.5 \
        --entry 2412.50 --stop 2405.00 --usd-rate 0.92

    python3 position_sizer.py --balance 25000 --risk-pct 0.5 \
        --entry 2412.50 --stop 2418.00 --direction short --json
"""

import argparse
import json
import math
import sys

OUNCES_PER_LOT = 100.0

# Below this stop distance (in USD per ounce) the stop sits inside normal
# spread and tick noise for gold. Not a hard block, but a loud warning.
MIN_SANE_STOP_USD = 3.0

# R multiples that get a take-profit level printed by default.
DEFAULT_R_TARGETS = (1.0, 1.5, 2.0, 3.0)

# A trade is only worth taking if the structural target is at least this far.
MIN_ACCEPTABLE_RR = 1.5


def floor_to_step(value, step):
    """Round down to the nearest broker lot step, avoiding float drift."""
    if step <= 0:
        raise ValueError("step must be positive")
    return math.floor((value + 1e-9) / step) * step


def size_position(balance, risk_pct, entry, stop, direction,
                  usd_rate=1.0, lot_step=0.01, max_lots=None):
    """Return the full risk picture for one trade.

    balance and all account-currency figures are in the trader's account
    currency. usd_rate is how many account-currency units one USD buys
    (EUR account with EURUSD at 1.087 -> usd_rate 0.92).
    """
    if balance <= 0:
        raise ValueError("balance must be positive")
    if risk_pct <= 0:
        raise ValueError("risk-pct must be positive")
    if usd_rate <= 0:
        raise ValueError("usd-rate must be positive")
    if entry <= 0 or stop <= 0:
        raise ValueError("entry and stop must be positive prices")
    if abs(entry - stop) < 1e-9:
        raise ValueError("entry and stop cannot be the same price")

    inferred = "long" if stop < entry else "short"
    if direction == "auto":
        direction = inferred
    elif direction != inferred:
        raise ValueError(
            "direction '%s' contradicts the stop: a %s stop at %.2f must sit "
            "%s the entry at %.2f" % (
                direction, direction, stop,
                "below" if direction == "long" else "above", entry))

    stop_distance = abs(entry - stop)

    risk_account_target = balance * (risk_pct / 100.0)
    risk_usd_target = risk_account_target / usd_rate

    # USD risked per lot if the stop is hit.
    risk_usd_per_lot = stop_distance * OUNCES_PER_LOT
    raw_lots = risk_usd_target / risk_usd_per_lot
    lots = floor_to_step(raw_lots, lot_step)

    capped = False
    if max_lots is not None and lots > max_lots:
        lots = floor_to_step(max_lots, lot_step)
        capped = True

    ounces = lots * OUNCES_PER_LOT
    risk_usd_actual = lots * risk_usd_per_lot
    risk_account_actual = risk_usd_actual * usd_rate
    risk_pct_actual = (risk_account_actual / balance) * 100.0
    value_per_dollar_move = ounces  # USD P&L per 1.00 USD move in gold

    sign = 1.0 if direction == "long" else -1.0
    targets = []
    for r in DEFAULT_R_TARGETS:
        price = entry + sign * r * stop_distance
        profit_usd = r * risk_usd_actual
        targets.append({
            "r_multiple": r,
            "price": round(price, 2),
            "profit_usd": round(profit_usd, 2),
            "profit_account": round(profit_usd * usd_rate, 2),
        })

    warnings = []
    if lots <= 0:
        warnings.append(
            "Position size rounds to zero at a lot step of %.2f. The stop is "
            "too wide for this account and risk percent. Widen risk, reduce "
            "the stop distance, or skip the trade." % lot_step)
    if stop_distance < MIN_SANE_STOP_USD:
        warnings.append(
            "Stop distance is only %.2f USD. Gold spreads and tick noise "
            "routinely cover that range, so this stop is likely to be taken "
            "out by noise rather than by being wrong." % stop_distance)
    if risk_pct > 2.0:
        warnings.append(
            "Risking %.2f percent on a single trade. Above 2 percent, a "
            "normal losing streak of six trades costs more than a quarter of "
            "the account." % risk_pct)
    if capped:
        warnings.append(
            "Position capped at the max-lots limit, so actual risk (%.2f "
            "percent) is below the requested %.2f percent."
            % (risk_pct_actual, risk_pct))
    if lots > 0 and abs(risk_pct_actual - risk_pct) / risk_pct > 0.10 and not capped:
        warnings.append(
            "Lot rounding moved actual risk to %.2f percent versus the "
            "requested %.2f percent." % (risk_pct_actual, risk_pct))

    return {
        "direction": direction,
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "stop_distance_usd": round(stop_distance, 2),
        "lots": round(lots, 2),
        "ounces": round(ounces, 2),
        "value_per_usd_move": round(value_per_dollar_move, 2),
        "risk_usd": round(risk_usd_actual, 2),
        "risk_account": round(risk_account_actual, 2),
        "risk_pct_actual": round(risk_pct_actual, 3),
        "risk_pct_requested": risk_pct,
        "usd_rate": usd_rate,
        "targets": targets,
        "min_acceptable_rr": MIN_ACCEPTABLE_RR,
        "warnings": warnings,
    }


def evaluate_target(result, target_price):
    """Score a concrete take-profit level against the trade's risk."""
    entry = result["entry"]
    stop_distance = result["stop_distance_usd"]
    direction = result["direction"]

    reward = (target_price - entry) if direction == "long" else (entry - target_price)
    if reward <= 0:
        return {
            "target_price": round(target_price, 2),
            "reward_usd_per_oz": round(reward, 2),
            "rr": 0.0,
            "verdict": "INVALID",
            "reason": "Target sits on the wrong side of the entry.",
        }

    rr = reward / stop_distance
    if rr >= result["min_acceptable_rr"]:
        verdict, reason = "OK", "Reward-to-risk clears the %.1f minimum." % result["min_acceptable_rr"]
    else:
        verdict, reason = "NO TRADE", (
            "Reward-to-risk of %.2f is below the %.1f minimum. At this ratio a "
            "50 percent hit rate loses money after costs."
            % (rr, result["min_acceptable_rr"]))

    return {
        "target_price": round(target_price, 2),
        "reward_usd_per_oz": round(reward, 2),
        "rr": round(rr, 2),
        "profit_usd": round(rr * result["risk_usd"], 2),
        "profit_account": round(rr * result["risk_account"], 2),
        "verdict": verdict,
        "reason": reason,
    }


def render(result, currency, target_eval=None):
    lines = []
    lines.append("XAUUSD POSITION SIZING")
    lines.append("")
    lines.append("Direction        %s" % result["direction"].upper())
    lines.append("Entry            %.2f USD" % result["entry"])
    lines.append("Stop             %.2f USD" % result["stop"])
    lines.append("Stop distance    %.2f USD per ounce" % result["stop_distance_usd"])
    lines.append("")
    lines.append("Position size    %.2f lots  (%.0f oz)" % (result["lots"], result["ounces"]))
    lines.append("P&L per 1 USD    %.2f USD" % result["value_per_usd_move"])
    lines.append("Risk if stopped  %.2f USD  =  %.2f %s  (%.2f%% of account)"
                 % (result["risk_usd"], result["risk_account"], currency,
                    result["risk_pct_actual"]))
    lines.append("")
    lines.append("TAKE PROFIT LADDER")
    lines.append("%-6s %-12s %-14s %s" % ("R", "Price", "Profit USD", "Profit " + currency))
    for t in result["targets"]:
        lines.append("%-6s %-12.2f %-14.2f %.2f"
                     % (("%.1fR" % t["r_multiple"]), t["price"],
                        t["profit_usd"], t["profit_account"]))

    if target_eval:
        lines.append("")
        lines.append("YOUR TARGET")
        lines.append("Target price     %.2f USD" % target_eval["target_price"])
        lines.append("Reward-to-risk   %.2f" % target_eval["rr"])
        lines.append("Verdict          %s" % target_eval["verdict"])
        lines.append("                 %s" % target_eval["reason"])

    if result["warnings"]:
        lines.append("")
        lines.append("WARNINGS")
        for w in result["warnings"]:
            lines.append("  - " + w)

    lines.append("")
    lines.append("This is arithmetic, not a recommendation. It says how much a "
                 "trade costs when wrong, not whether the trade is right.")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Position sizing and R-multiple math for XAUUSD.")
    p.add_argument("--balance", type=float, required=True,
                   help="Account balance in account currency.")
    p.add_argument("--risk-pct", type=float, default=0.5,
                   help="Percent of the account risked on this trade (default 0.5).")
    p.add_argument("--entry", type=float, required=True, help="Entry price in USD.")
    p.add_argument("--stop", type=float, required=True, help="Stop-loss price in USD.")
    p.add_argument("--target", type=float, default=None,
                   help="Optional take-profit price to score against the stop.")
    p.add_argument("--direction", choices=["auto", "long", "short"], default="auto",
                   help="Trade direction; inferred from the stop by default.")
    p.add_argument("--usd-rate", type=float, default=1.0,
                   help="Account-currency units per 1 USD. EUR account with "
                        "EURUSD at 1.087 -> 0.92. Default 1.0 (USD account).")
    p.add_argument("--currency", default="EUR", help="Account currency label (default EUR).")
    p.add_argument("--lot-step", type=float, default=0.01,
                   help="Smallest lot increment your broker accepts (default 0.01).")
    p.add_argument("--max-lots", type=float, default=None,
                   help="Optional hard cap on position size in lots.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a report.")
    args = p.parse_args(argv)

    try:
        result = size_position(
            balance=args.balance, risk_pct=args.risk_pct, entry=args.entry,
            stop=args.stop, direction=args.direction, usd_rate=args.usd_rate,
            lot_step=args.lot_step, max_lots=args.max_lots)
    except ValueError as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 2

    target_eval = evaluate_target(result, args.target) if args.target else None

    if args.json:
        payload = dict(result)
        payload["currency"] = args.currency
        if target_eval:
            payload["target_evaluation"] = target_eval
        print(json.dumps(payload, indent=2))
    else:
        print(render(result, args.currency, target_eval))

    return 0


if __name__ == "__main__":
    sys.exit(main())
