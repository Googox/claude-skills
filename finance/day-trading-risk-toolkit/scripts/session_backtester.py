#!/usr/bin/env python3
"""Session opportunity analysis and opening-range-breakout backtest.

Takes continuous 1-minute OHLCV data (e.g. from Databento, columns:
dt, open, high, low, close, volume) and answers two questions for a
specific intraday trading window:

1. Opportunity ceiling: how much movement did the window actually offer,
   day by day, over the full history? This is the hard upper bound on
   what any strategy could have extracted — before assuming any edge.
2. Measured performance: backtest a simple, transparent opening-range
   breakout (ORB) setup through the window, with realistic spread/
   slippage costs, and report the ACTUAL win rate, expectancy, and R
   distribution — to replace assumed numbers with measured ones.

This is deliberately a simple, well-known setup, not a proprietary
strategy search. The point is to measure what a plausible baseline
approach achieves, honestly, including costs.

Standard library + pandas only.
"""

import argparse
import json
import sys
from datetime import datetime, time as dtime

import pandas as pd


def load_series(path):
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    df["dt"] = pd.to_datetime(df["dt"], utc=True)
    return df.sort_values("dt").reset_index(drop=True)


def to_session_tz(df, tz):
    df = df.copy()
    df["dt_local"] = df["dt"].dt.tz_convert(tz)
    df["date_local"] = df["dt_local"].dt.date
    return df


def window_slice(df, start_hm, end_hm):
    start_h, start_m = map(int, start_hm.split(":"))
    end_h, end_m = map(int, end_hm.split(":"))
    start_t, end_t = dtime(start_h, start_m), dtime(end_h, end_m)
    t = df["dt_local"].dt.time
    return df[(t >= start_t) & (t <= end_t)]


def opportunity_ceiling(df, tz, start_hm, end_hm, point_value, spread_points):
    """Per-day range and directional move available inside the window."""
    df = to_session_tz(df, tz)
    win = window_slice(df, start_hm, end_hm)
    if win.empty:
        return None

    daily = win.groupby("date_local").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
    )
    daily["range_points"] = daily["high"] - daily["low"]
    daily["net_move_points"] = (daily["close"] - daily["open"]).abs()
    daily["range_after_spread_eur"] = (daily["range_points"] - spread_points).clip(lower=0) * point_value
    daily["net_after_spread_eur"] = (daily["net_move_points"] - spread_points).clip(lower=0) * point_value

    n_days = len(daily)
    return {
        "window": f"{start_hm}-{end_hm} {tz}",
        "trading_days": n_days,
        "avg_range_points": round(daily["range_points"].mean(), 2),
        "avg_net_move_points": round(daily["net_move_points"].mean(), 2),
        "avg_max_extractable_eur_perfect_foresight": round(daily["range_after_spread_eur"].mean(), 2),
        "avg_extractable_eur_one_directional_trade": round(daily["net_after_spread_eur"].mean(), 2),
        "pct_days_move_exceeds_1000eur_target": round(
            100.0 * (daily["net_after_spread_eur"] >= 1000).mean(), 1
        ),
        "median_net_move_points": round(daily["net_move_points"].median(), 2),
    }


def backtest_orb(df, tz, start_hm, end_hm, opening_minutes, stop_points, target_r,
                  point_value, spread_points, slippage_points):
    """Opening range breakout: define range in first N minutes of the window,
    enter on a break of the high/low, exit at stop or target_r * stop distance."""
    df = to_session_tz(df, tz)
    win = window_slice(df, start_hm, end_hm)
    if win.empty:
        return None

    start_h, start_m = map(int, start_hm.split(":"))
    or_end = (datetime.combine(datetime.today(), dtime(start_h, start_m))
              + pd.Timedelta(minutes=opening_minutes)).time()

    trades = []
    for day, day_df in win.groupby("date_local"):
        day_df = day_df.sort_values("dt_local")
        or_bars = day_df[day_df["dt_local"].dt.time <= or_end]
        rest = day_df[day_df["dt_local"].dt.time > or_end]
        if or_bars.empty or rest.empty:
            continue

        or_high = or_bars["high"].max()
        or_low = or_bars["low"].min()
        entry_price = None
        direction = None

        for _, bar in rest.iterrows():
            if entry_price is None:
                if bar["high"] > or_high:
                    entry_price = or_high + slippage_points
                    direction = "long"
                elif bar["low"] < or_low:
                    entry_price = or_low - slippage_points
                    direction = "short"
                if entry_price is not None:
                    stop_price = (entry_price - stop_points if direction == "long"
                                  else entry_price + stop_points)
                    target_price = (entry_price + stop_points * target_r if direction == "long"
                                     else entry_price - stop_points * target_r)
                continue

            if direction == "long":
                if bar["low"] <= stop_price:
                    trades.append({"date": day, "direction": direction, "result": "loss", "r": -1.0})
                    break
                if bar["high"] >= target_price:
                    trades.append({"date": day, "direction": direction, "result": "win", "r": target_r})
                    break
            else:
                if bar["high"] >= stop_price:
                    trades.append({"date": day, "direction": direction, "result": "loss", "r": -1.0})
                    break
                if bar["low"] <= target_price:
                    trades.append({"date": day, "direction": direction, "result": "win", "r": target_r})
                    break
        else:
            if entry_price is not None:
                last_close = rest.iloc[-1]["close"]
                r = ((last_close - entry_price) / stop_points if direction == "long"
                     else (entry_price - last_close) / stop_points)
                trades.append({"date": day, "direction": direction, "result": "timeout", "r": round(r, 2)})

    if not trades:
        return {"trades": 0, "note": "No breakouts triggered in this window/period"}

    tdf = pd.DataFrame(trades)
    cost_r = spread_points / stop_points  # round-trip cost expressed in R
    tdf["r_after_costs"] = tdf["r"] - cost_r

    wins = (tdf["r_after_costs"] > 0).sum()
    n = len(tdf)
    win_rate = wins / n
    avg_r = tdf["r_after_costs"].mean()
    eur_per_r = stop_points * point_value

    return {
        "setup": f"Opening Range Breakout ({opening_minutes}min range, {target_r}R target, {stop_points}pt stop)",
        "window": f"{start_hm}-{end_hm} {tz}",
        "trades": int(n),
        "win_rate_observed": round(win_rate, 3),
        "avg_R_after_costs": round(avg_r, 3),
        "expectancy_eur_per_trade_at_1pct_risk_10k": round(avg_r * eur_per_r * 0.01 * 100, 2),
        "long_trades": int((tdf["direction"] == "long").sum()),
        "short_trades": int((tdf["direction"] == "short").sum()),
        "timeouts": int((tdf["result"] == "timeout").sum()),
        "best_R": round(tdf["r_after_costs"].max(), 2),
        "worst_R": round(tdf["r_after_costs"].min(), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Session opportunity analysis + ORB backtest on historical futures data")
    parser.add_argument("--file", required=True, help="Path to continuous 1m OHLCV parquet/csv (columns: dt,open,high,low,close,volume)")
    parser.add_argument("--tz", required=True, help="Session timezone, e.g. 'America/New_York' or 'Europe/Berlin'")
    parser.add_argument("--start", required=True, help="Window start HH:MM in --tz")
    parser.add_argument("--end", required=True, help="Window end HH:MM in --tz")
    parser.add_argument("--point-value", type=float, required=True, help="EUR/USD value of 1.0 price point per contract/unit")
    parser.add_argument("--spread-points", type=float, default=2.0, help="Round-trip spread in points (default: 2.0)")
    parser.add_argument("--slippage-points", type=float, default=1.0, help="Entry slippage in points (default: 1.0)")
    parser.add_argument("--opening-minutes", type=int, default=15, help="Opening range length in minutes (default: 15)")
    parser.add_argument("--stop-points", type=float, default=40.0, help="Stop distance in points (default: 40)")
    parser.add_argument("--target-r", type=float, default=1.5, help="Target as multiple of stop distance (default: 1.5)")
    parser.add_argument("--format", choices=["human", "json"], default="human")
    args = parser.parse_args()

    df = load_series(args.file)

    ceiling = opportunity_ceiling(df, args.tz, args.start, args.end, args.point_value, args.spread_points)
    backtest = backtest_orb(
        df, args.tz, args.start, args.end, args.opening_minutes,
        args.stop_points, args.target_r, args.point_value,
        args.spread_points, args.slippage_points,
    )

    result = {"opportunity_ceiling": ceiling, "orb_backtest": backtest}

    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
        return 0

    print("=" * 68)
    print("SESSION OPPORTUNITY CEILING")
    print("=" * 68)
    if ceiling:
        for k, v in ceiling.items():
            print(f"{k:45s} {v}")
    print("-" * 68)
    print("This is the theoretical MAXIMUM extractable with perfect")
    print("foresight and a single directional trade. No real strategy")
    print("reaches this; it only bounds what is possible.")
    print("=" * 68)
    print("\nORB BACKTEST (measured, not assumed)")
    print("=" * 68)
    if backtest and backtest.get("trades"):
        for k, v in backtest.items():
            print(f"{k:45s} {v}")
    else:
        print(backtest.get("note", "no trades"))
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
