#!/usr/bin/env python3
"""Deterministic pre-trade confluence scorer for XAUUSD day trading.

The scorer answers one question: has this setup earned a position, or is it
boredom wearing a chart? It is rule arithmetic, not prediction. Identical
inputs always produce an identical verdict, which is the point: it removes
the discretion that turns a plan into a whim.

Hard vetoes override the score entirely. A high score with an open veto is
still NO TRADE.

Usage:
    python3 setup_scorer.py --htf-trend aligned --structure-break yes \
        --at-key-level yes --pullback yes --session overlap \
        --rr 2.3 --news-window no --daily-loss-hit no --momentum yes

    python3 setup_scorer.py --interactive
    python3 setup_scorer.py --list-criteria
"""

import argparse
import json
import sys

# Weighted confluence criteria. Weights reflect how strongly each factor is
# associated with the trader's own journal results over time -- they are a
# starting point to be recalibrated from real data, not a discovered truth.
CRITERIA = [
    {
        "key": "htf_trend",
        "weight": 20,
        "prompt": "Higher timeframe (H1/H4) trend versus your intended direction",
        "choices": {"aligned": 1.0, "neutral": 0.4, "against": 0.0},
        "note": "Counter-trend intraday gold trades need a much better reason "
                "than a nice-looking candle.",
    },
    {
        "key": "structure_break",
        "weight": 15,
        "prompt": "Break of structure on your entry timeframe in your direction",
        "choices": {"yes": 1.0, "unclear": 0.3, "no": 0.0},
        "note": "Without a break of structure you are guessing at a reversal.",
    },
    {
        "key": "at_key_level",
        "weight": 15,
        "prompt": "Entry sits at a marked level (prior day high/low, session "
                  "high/low, tested support or resistance)",
        "choices": {"yes": 1.0, "near": 0.5, "no": 0.0},
        "note": "Entries in the middle of a range have no natural stop.",
    },
    {
        "key": "pullback",
        "weight": 12,
        "prompt": "Entering on a pullback rather than chasing an extended move",
        "choices": {"yes": 1.0, "partial": 0.5, "no": 0.0},
        "note": "Chasing widens the stop and shrinks the R-multiple at once.",
    },
    {
        "key": "momentum",
        "weight": 10,
        "prompt": "Momentum or indicator reading confirms the direction",
        "choices": {"yes": 1.0, "mixed": 0.4, "no": 0.0},
        "note": "Confirmation is a tiebreaker, never the reason for the trade.",
    },
    {
        "key": "session",
        "weight": 10,
        "prompt": "Trading session",
        "choices": {"overlap": 1.0, "london": 0.8, "newyork": 0.8,
                    "asia": 0.3, "offhours": 0.0},
        "note": "Gold's liquidity concentrates in London and the London/NY "
                "overlap. Thin sessions produce wide spreads and false breaks.",
    },
    {
        "key": "volatility",
        "weight": 8,
        "prompt": "Current range/ATR supports the target being reachable today",
        "choices": {"yes": 1.0, "tight": 0.3, "no": 0.0},
        "note": "A 3R target inside a day that has already spent its range is "
                "arithmetic fiction.",
    },
    {
        "key": "plan_match",
        "weight": 10,
        "prompt": "This setup matches a setup type written in your plan before today",
        "choices": {"yes": 1.0, "loosely": 0.4, "no": 0.0},
        "note": "An improvised setup cannot be evaluated by your journal later.",
    },
]

CRITERIA_BY_KEY = {c["key"]: c for c in CRITERIA}
TOTAL_WEIGHT = sum(c["weight"] for c in CRITERIA)

MIN_RR = 1.5

BANDS = [
    (75, "TAKE", "Full planned risk. The setup carries its own justification."),
    (60, "TAKE REDUCED", "Half your normal risk. Confluence is adequate, not strong."),
    (45, "WATCH", "No position. Mark the level and wait for the missing piece."),
    (0, "NO TRADE", "Not a setup. Taking it is a decision to donate."),
]


def evaluate(answers, rr, news_window, daily_loss_hit, trades_today, max_trades):
    """Score the setup and apply hard vetoes."""
    scored = []
    earned = 0.0

    for crit in CRITERIA:
        raw = answers.get(crit["key"])
        if raw is None:
            factor, label = 0.0, "unanswered"
        elif raw not in crit["choices"]:
            valid = ", ".join(sorted(crit["choices"]))
            raise ValueError("Invalid value '%s' for %s. Valid: %s"
                             % (raw, crit["key"], valid))
        else:
            factor, label = crit["choices"][raw], raw

        points = crit["weight"] * factor
        earned += points
        scored.append({
            "criterion": crit["key"],
            "prompt": crit["prompt"],
            "answer": label,
            "weight": crit["weight"],
            "points": round(points, 1),
            "note": crit["note"] if factor < 0.5 else None,
        })

    score = round((earned / TOTAL_WEIGHT) * 100.0, 1)

    vetoes = []
    if news_window:
        vetoes.append(
            "High-impact news inside the next 30 minutes. Gold gaps through "
            "stops on CPI, NFP and FOMC. Your stop is not a stop during a print.")
    if daily_loss_hit:
        vetoes.append(
            "Daily loss limit already reached. Every trade after this one is "
            "revenge, whatever it looks like on the chart.")
    if rr is not None and rr < MIN_RR:
        vetoes.append(
            "Reward-to-risk of %.2f is below the %.1f floor. At this ratio you "
            "need a hit rate you have not yet proven you have." % (rr, MIN_RR))
    if trades_today is not None and max_trades is not None and trades_today >= max_trades:
        vetoes.append(
            "Trade limit for today reached (%d of %d). Frequency is where "
            "day-trading edges go to die." % (trades_today, max_trades))

    unanswered = [s["criterion"] for s in scored if s["answer"] == "unanswered"]
    if unanswered:
        vetoes.append(
            "Unanswered criteria scored as zero: %s. Answer them or accept "
            "that the score understates and the setup is unexamined."
            % ", ".join(unanswered))

    if vetoes:
        verdict = "NO TRADE"
        rationale = "Hard veto in force. The score is irrelevant until it clears."
    else:
        for threshold, name, text in BANDS:
            if score >= threshold:
                verdict, rationale = name, text
                break

    weakest = sorted(
        [s for s in scored if s["points"] < s["weight"]],
        key=lambda s: (s["weight"] - s["points"]), reverse=True)[:3]

    return {
        "score": score,
        "max_score": 100,
        "verdict": verdict,
        "rationale": rationale,
        "rr": rr,
        "min_rr": MIN_RR,
        "vetoes": vetoes,
        "criteria": scored,
        "biggest_gaps": [
            {"criterion": s["criterion"], "lost_points": round(s["weight"] - s["points"], 1),
             "note": CRITERIA_BY_KEY[s["criterion"]]["note"]}
            for s in weakest],
    }


def render(result):
    lines = []
    lines.append("PRE-TRADE SETUP SCORE")
    lines.append("")
    lines.append("Score      %.1f / 100" % result["score"])
    if result["rr"] is not None:
        lines.append("R:R        %.2f  (floor %.1f)" % (result["rr"], result["min_rr"]))
    lines.append("Verdict    %s" % result["verdict"])
    lines.append("           %s" % result["rationale"])
    lines.append("")
    lines.append("SCORECARD")
    lines.append("%-18s %-12s %8s" % ("Criterion", "Answer", "Points"))
    for c in result["criteria"]:
        lines.append("%-18s %-12s %5.1f/%-3d"
                     % (c["criterion"], c["answer"], c["points"], c["weight"]))

    if result["vetoes"]:
        lines.append("")
        lines.append("HARD VETOES")
        for v in result["vetoes"]:
            lines.append("  ! " + v)

    gaps = [g for g in result["biggest_gaps"] if g["note"]]
    if gaps:
        lines.append("")
        lines.append("WHERE THIS SETUP IS WEAK")
        for g in gaps:
            lines.append("  - %s (-%.1f): %s" % (g["criterion"], g["lost_points"], g["note"]))

    lines.append("")
    lines.append("The score measures process discipline, not the probability of "
                 "the trade working. No score makes a losing trade wrong or a "
                 "winning trade right.")
    return "\n".join(lines)


def interactive():
    answers = {}
    print("Answer each criterion. Press Enter to leave one unanswered.\n")
    for crit in CRITERIA:
        valid = sorted(crit["choices"])
        while True:
            raw = input("%s\n  [%s] > " % (crit["prompt"], "/".join(valid))).strip().lower()
            if raw == "":
                break
            if raw in crit["choices"]:
                answers[crit["key"]] = raw
                break
            print("  Not a valid answer. Choose one of: %s" % ", ".join(valid))
        print("")
    return answers


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Deterministic pre-trade confluence scorer for XAUUSD.")
    for crit in CRITERIA:
        p.add_argument("--" + crit["key"].replace("_", "-"),
                       choices=sorted(crit["choices"]), default=None,
                       help=crit["prompt"])
    p.add_argument("--rr", type=float, default=None,
                   help="Reward-to-risk of the planned trade.")
    p.add_argument("--news-window", choices=["yes", "no"], default="no",
                   help="High-impact news within 30 minutes.")
    p.add_argument("--daily-loss-hit", choices=["yes", "no"], default="no",
                   help="Daily loss limit already reached.")
    p.add_argument("--trades-today", type=int, default=None,
                   help="Trades already taken today.")
    p.add_argument("--max-trades", type=int, default=2,
                   help="Maximum trades allowed per day (default 2).")
    p.add_argument("--interactive", action="store_true",
                   help="Prompt for each criterion instead of using flags.")
    p.add_argument("--list-criteria", action="store_true",
                   help="Print the criteria and weights, then exit.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a report.")
    args = p.parse_args(argv)

    if args.list_criteria:
        out = [{"key": c["key"], "weight": c["weight"], "prompt": c["prompt"],
                "choices": c["choices"], "note": c["note"]} for c in CRITERIA]
        print(json.dumps(out, indent=2) if args.json else
              "\n".join("%-18s %3d  %s" % (c["key"], c["weight"], c["prompt"]) for c in CRITERIA))
        return 0

    if args.interactive:
        answers = interactive()
    else:
        answers = {c["key"]: getattr(args, c["key"]) for c in CRITERIA}
        answers = {k: v for k, v in answers.items() if v is not None}

    try:
        result = evaluate(
            answers=answers, rr=args.rr,
            news_window=(args.news_window == "yes"),
            daily_loss_hit=(args.daily_loss_hit == "yes"),
            trades_today=args.trades_today, max_trades=args.max_trades)
    except ValueError as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
