#!/usr/bin/env python3
"""Position size calculator for leveraged intraday instruments.

Computes the position size that keeps the loss at a defined stop-loss
distance within a fixed percentage of account equity (fixed-fractional
risk model), plus the margin required and effective leverage.

Includes presets for the instruments most commonly day-traded by retail
accounts: NASDAQ 100 (CFD and Micro future MNQ) and Gold/XAUUSD (CFD and
Micro future MGC).

Standard library only. No market data or API calls — prices and stop
distances are inputs.
"""

import argparse
import json
import sys

# value_per_point = account-currency P&L for a 1.0 point move per 1 unit/contract
# margin_leverage = typical maximum retail leverage (ESMA caps for CFDs)
INSTRUMENT_PRESETS = {
    "nasdaq-cfd": {
        "label": "NASDAQ 100 CFD (US Tech 100)",
        "value_per_point": 1.0,     # per 1 contract/lot of 1 EUR-per-point
        "unit": "EUR/point contracts",
        "max_leverage": 20,          # ESMA cap for major indices
        "typical_spread_points": 2.0,
    },
    "mnq": {
        "label": "Micro E-mini NASDAQ 100 future (MNQ)",
        "value_per_point": 2.0,      # USD 2 per point per contract
        "unit": "contracts",
        "max_leverage": None,        # margin-based, broker-defined
        "typical_spread_points": 0.5,
    },
    "xauusd-cfd": {
        "label": "Gold CFD (XAU/USD)",
        "value_per_point": 1.0,      # per 1 oz, 1.0 = 1 USD move per oz
        "unit": "oz",
        "max_leverage": 20,          # ESMA cap for gold
        "typical_spread_points": 0.3,
    },
    "mgc": {
        "label": "Micro Gold future (MGC)",
        "value_per_point": 10.0,     # USD 10 per 1.0 move per contract (10 oz)
        "unit": "contracts",
        "max_leverage": None,
        "typical_spread_points": 0.2,
    },
}

MAX_RECOMMENDED_RISK_PCT = 2.0


def calculate(capital, risk_pct, stop_points, price, instrument, broker_leverage=None):
    preset = INSTRUMENT_PRESETS[instrument]
    risk_eur = capital * risk_pct / 100.0
    loss_per_unit = stop_points * preset["value_per_point"]

    if loss_per_unit <= 0:
        raise ValueError("Stop distance must be positive")

    units = risk_eur / loss_per_unit
    notional = units * price * (preset["value_per_point"] if instrument in ("mnq", "mgc") else 1.0)
    # For futures the point value already scales the contract; notional approximation:
    if instrument == "mnq":
        notional = units * price * 2.0
    elif instrument == "mgc":
        notional = units * price * 10.0
    else:
        notional = units * price

    effective_leverage = notional / capital if capital > 0 else 0.0
    leverage_cap = broker_leverage or preset["max_leverage"]
    margin_required = notional / leverage_cap if leverage_cap else None
    spread_cost = preset["typical_spread_points"] * preset["value_per_point"] * units
    # adverse move (in % of price) that erases the whole account at this size
    wipeout_move_pct = capital / notional * 100.0 if notional > 0 else None
    max_notional = capital * leverage_cap if leverage_cap else None

    warnings = []
    if risk_pct > MAX_RECOMMENDED_RISK_PCT:
        warnings.append(
            f"Risk of {risk_pct}% per trade exceeds the professional standard "
            f"of 0.5-2%. At {risk_pct}% per trade, 5 consecutive losses cost "
            f"{5 * risk_pct:.0f}% of the account. Consecutive losses are "
            "normal, not exceptional (see monte_carlo_simulator.py)."
        )
    esma_cap = preset["max_leverage"]
    if broker_leverage and esma_cap and broker_leverage > esma_cap:
        warnings.append(
            f"Broker leverage of {broker_leverage:.0f}x exceeds the ESMA retail "
            f"cap of {esma_cap}x — this is an offshore or 'professional client' "
            "account. EU protections likely do NOT apply: no negative balance "
            "protection (losses can exceed the deposit and become debt), no "
            "deposit insurance, no ESMA/BaFin recourse against the broker. "
            "Leverage does not change the strategy's expectancy; it only "
            "enables position sizes whose gap risk exceeds the account."
        )
    if not broker_leverage and esma_cap and effective_leverage > esma_cap:
        warnings.append(
            f"Required position implies leverage of {effective_leverage:.0f}x, "
            f"above the ESMA retail cap of {esma_cap}x for this "
            "instrument. The trade as planned is NOT executable on an EU "
            "retail account — the stop is too tight or the risk target too "
            "large for the capital."
        )
    if margin_required and margin_required > capital * 0.5:
        warnings.append(
            f"Margin requirement (EUR {margin_required:,.0f}) exceeds 50% of "
            "capital. One adverse gap can trigger a margin call."
        )
    if wipeout_move_pct is not None and wipeout_move_pct < 1.0:
        warnings.append(
            f"GAP RISK: an adverse move of only {wipeout_move_pct:.2f}% wipes "
            "out the entire account at this position size. Stop-loss orders do "
            "NOT protect against gaps and news spikes — the fill happens at "
            "the next available price, not at the stop level."
        )
    if spread_cost > risk_eur * 0.1:
        warnings.append(
            f"Spread/round-trip cost (~EUR {spread_cost:.2f}) eats more than "
            "10% of the risked amount — the stop is too tight relative to "
            "trading costs."
        )

    return {
        "inputs": {
            "capital_eur": capital,
            "risk_per_trade_pct": risk_pct,
            "stop_distance_points": stop_points,
            "instrument_price": price,
            "instrument": preset["label"],
        },
        "risk_per_trade_eur": round(risk_eur, 2),
        "position_size": round(units, 2),
        "position_unit": preset["unit"],
        "notional_exposure_eur": round(notional, 2),
        "effective_leverage": round(effective_leverage, 1),
        "margin_required_eur": round(margin_required, 2) if margin_required else "broker-defined (futures)",
        "leverage_cap_used": leverage_cap,
        "max_notional_at_leverage_eur": round(max_notional, 2) if max_notional else None,
        "account_wipeout_move_pct": round(wipeout_move_pct, 3) if wipeout_move_pct else None,
        "estimated_spread_cost_eur": round(spread_cost, 2),
        "warnings": warnings,
    }


def format_human(result):
    i = result["inputs"]
    out = []
    out.append("=" * 68)
    out.append("POSITION SIZE CALCULATION (fixed-fractional risk)")
    out.append("=" * 68)
    out.append(f"Instrument:         {i['instrument']}")
    out.append(f"Capital:            EUR {i['capital_eur']:,.0f}")
    out.append(f"Risk per trade:     {i['risk_per_trade_pct']}% = EUR {result['risk_per_trade_eur']:,.2f}")
    out.append(f"Stop distance:      {i['stop_distance_points']} points @ price {i['instrument_price']:,}")
    out.append("-" * 68)
    out.append(f"Position size:      {result['position_size']} {result['position_unit']}")
    out.append(f"Notional exposure:  EUR {result['notional_exposure_eur']:,.2f}")
    out.append(f"Effective leverage: {result['effective_leverage']}x")
    margin = result["margin_required_eur"]
    out.append(
        f"Margin required:    EUR {margin:,.2f}" if isinstance(margin, (int, float))
        else f"Margin required:    {margin}"
    )
    out.append(f"Est. spread cost:   EUR {result['estimated_spread_cost_eur']}")
    if result["account_wipeout_move_pct"] is not None:
        out.append(f"Account wiped by:   {result['account_wipeout_move_pct']}% adverse move (gaps ignore stops)")
    if result["warnings"]:
        out.append("-" * 68)
        out.append("WARNINGS:")
        for w in result["warnings"]:
            out.append(f"  ! {w}")
    out.append("=" * 68)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate position size from account risk and stop distance"
    )
    parser.add_argument("--capital", type=float, required=True, help="Account equity in EUR")
    parser.add_argument("--risk-pct", type=float, default=1.0, help="Risk per trade as %% of equity (default: 1.0)")
    parser.add_argument("--stop-points", type=float, required=True, help="Stop-loss distance in points/USD")
    parser.add_argument("--price", type=float, required=True, help="Current instrument price")
    parser.add_argument(
        "--instrument",
        choices=sorted(INSTRUMENT_PRESETS),
        default="nasdaq-cfd",
        help="Instrument preset (default: nasdaq-cfd)",
    )
    parser.add_argument(
        "--leverage",
        type=float,
        help="Broker's max leverage, e.g. 500 for a 500:1 offshore account "
        "(default: instrument's ESMA retail cap)",
    )
    parser.add_argument("--format", choices=["human", "json"], default="human")
    args = parser.parse_args()

    if args.capital <= 0 or args.stop_points <= 0 or args.price <= 0:
        print("Error: capital, stop-points and price must be positive", file=sys.stderr)
        return 2
    if args.leverage is not None and args.leverage <= 0:
        print("Error: --leverage must be positive", file=sys.stderr)
        return 2

    result = calculate(
        args.capital, args.risk_pct, args.stop_points, args.price,
        args.instrument, broker_leverage=args.leverage,
    )
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
