#!/usr/bin/env python3
"""Score a C-level candidate against the A/A assessment methodology.

Deterministic arithmetic, no model calls. Weights, thresholds and the
mandate-specific profiles mirror ../SKILL.md; a drift between the two is a bug.

Usage:
    python3 aa_score.py --interaktiv
    python3 aa_score.py --s1 18 --s2 7 --s3 20 --s4 8 --s5 12 --s6 9 --s7 11
    python3 aa_score.py --interaktiv --mandatstyp nachfolge
    python3 aa_score.py --s1 18 ... --knockout zahlenkenntnis
    python3 aa_score.py --s1 18 ... --json

Exit codes: 0 = shortlist-worthy, 1 = below threshold or knocked out.
"""

import argparse
import json
import sys

SIGNALE = [
    ("s1", "ertragsmechanik", "Ertragsmechanik verstanden"),
    ("s2", "herstellerspannung", "Haelt Hersteller-Spannung aus"),
    ("s3", "fachkraefte", "Zieht Fachkraefte an und haelt sie"),
    ("s4", "entscheidung", "Entscheidet unter Unvollstaendigkeit"),
    ("s5", "inhaberfamilie", "Anschlussfaehig an eine Inhaberfamilie"),
    ("s6", "flaeche", "Operative Glaubwuerdigkeit auf der Flaeche"),
    ("s7", "transformation", "Umgesetzte Transformation"),
]

# Base weights, and per-mandate deviations. Every profile must sum to 100.
GEWICHTE = {
    "standard":      {"s1": 20, "s2": 10, "s3": 20, "s4": 10, "s5": 15, "s6": 10, "s7": 15},
    "sanierung":     {"s1": 20, "s2": 10, "s3": 20, "s4": 15, "s5":  5, "s6": 10, "s7": 20},
    "nachfolge":     {"s1": 20, "s2":  5, "s3": 20, "s4": 10, "s5": 25, "s6": 10, "s7": 10},
    "wachstum":      {"s1": 25, "s2":  5, "s3": 25, "s4":  5, "s5": 15, "s6": 10, "s7": 15},
    "markenwechsel": {"s1": 20, "s2": 20, "s3": 20, "s4": 10, "s5": 10, "s6":  5, "s7": 15},
}

KNOCKOUTS = {
    "integritaet": "Integritaet",
    "lustlosigkeit": "Lustlosigkeit",
    "zahlenkenntnis": "Fehlende Zahlenkenntnis",
}

SCHWELLEN = [
    (85, "Shortlist ohne Vorbehalt"),
    (70, "Shortlist mit benanntem Entwicklungsfeld"),
    (55, "Longlist, zweites Gespraech erforderlich"),
    (0,  "Nicht weiterverfolgen"),
]


def einordnen(score):
    for grenze, text in SCHWELLEN:
        if score >= grenze:
            return text
    return SCHWELLEN[-1][1]


def pruefe_profile():
    """Guard against a weight profile that no longer sums to 100."""
    fehler = []
    for name, weights in GEWICHTE.items():
        total = sum(weights.values())
        if total != 100:
            fehler.append(f"{name}={total}")
        missing = {key for key, _, _ in SIGNALE} - set(weights)
        if missing:
            fehler.append(f"{name} fehlen {sorted(missing)}")
    return fehler


def frage_interaktiv(weights):
    werte = {}
    print("Punkte je Signal eingeben. Leer lassen, wenn kein Beleg vorliegt.\n")
    for key, _slug, label in SIGNALE:
        maximum = weights[key]
        while True:
            raw = input(f"  {label} (0-{maximum}): ").strip()
            if raw == "":
                werte[key] = None
                break
            try:
                value = int(raw)
            except ValueError:
                print("    Ganze Zahl erwarten.")
                continue
            if 0 <= value <= maximum:
                werte[key] = value
                break
            print(f"    Zwischen 0 und {maximum}.")
    return werte


def main():
    ap = argparse.ArgumentParser(description="A/A C-Level-Assessment-Scoring.")
    for key, _slug, label in SIGNALE:
        ap.add_argument(f"--{key}", type=int, metavar="N", help=label)
    ap.add_argument("--mandatstyp", choices=sorted(GEWICHTE), default="standard",
                    help="Gewichtungsprofil (Standard: standard)")
    ap.add_argument("--knockout", default="",
                    help="Komma-Liste: " + ", ".join(KNOCKOUTS))
    ap.add_argument("--kandidat", default="", help="Name fuer die Ausgabe")
    ap.add_argument("--interaktiv", action="store_true", help="Werte abfragen")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    fehler = pruefe_profile()
    if fehler:
        print("ABBRUCH: Gewichtungsprofile fehlerhaft: " + "; ".join(fehler),
              file=sys.stderr)
        return 2

    weights = GEWICHTE[args.mandatstyp]

    ko_raw = [k.strip().lower() for k in args.knockout.split(",") if k.strip()]
    unbekannt = [k for k in ko_raw if k not in KNOCKOUTS]
    if unbekannt:
        print(f"ABBRUCH: unbekannte Knock-outs {unbekannt}. "
              f"Erlaubt: {sorted(KNOCKOUTS)}", file=sys.stderr)
        return 2

    if args.interaktiv:
        werte = frage_interaktiv(weights)
    else:
        werte = {key: getattr(args, key) for key, _s, _l in SIGNALE}
        for key, _s, label in SIGNALE:
            value = werte[key]
            if value is not None and not 0 <= value <= weights[key]:
                print(f"ABBRUCH: {key} ({label}) muss zwischen 0 und "
                      f"{weights[key]} liegen, war {value}.", file=sys.stderr)
                return 2

    belegt = {k: v for k, v in werte.items() if v is not None}
    luecken = [label for key, _s, label in SIGNALE if werte[key] is None]
    score = sum(belegt.values())
    max_belegt = sum(weights[k] for k in belegt)
    stand = "final" if not luecken else "vorlaeufig"

    if ko_raw:
        einordnung = "KNOCK-OUT, sofortiges Aus"
    elif luecken:
        einordnung = f"{einordnen(score)} (vorlaeufig, {len(luecken)} Signal(e) ohne Beleg)"
    else:
        einordnung = einordnen(score)

    if args.as_json:
        print(json.dumps({
            "kandidat": args.kandidat or None,
            "mandatstyp": args.mandatstyp,
            "score": score,
            "maximal_erreichbar_belegt": max_belegt,
            "signale": {slug: werte[key] for key, slug, _l in SIGNALE},
            "gewichte": {slug: weights[key] for key, slug, _l in SIGNALE},
            "luecken": luecken,
            "assessment_stand": stand,
            "knockouts": [KNOCKOUTS[k] for k in ko_raw],
            "einordnung": einordnung,
        }, ensure_ascii=False, indent=2))
        return 0 if (score >= 70 and not ko_raw and not luecken) else 1

    name = args.kandidat or "Kandidat"
    print(f"\nA/A C-Level-Assessment: {name}")
    print(f"Gewichtungsprofil: {args.mandatstyp}")
    print("=" * 58)
    for key, _slug, label in SIGNALE:
        value = werte[key]
        shown = "kein Beleg" if value is None else f"{value:>3} / {weights[key]:<3}"
        print(f"  {label:<42} {shown}")
    print("-" * 58)
    print(f"  {'Score':<42} {score:>3} / 100")
    if luecken:
        print(f"  {'davon belegt':<42} {score:>3} / {max_belegt}")

    if ko_raw:
        print("\n  KNOCK-OUT: " + ", ".join(KNOCKOUTS[k] for k in ko_raw))
        print("  Sofortiges Aus. Der Score ist irrelevant und kauft nicht frei.")
    else:
        print(f"\n  Einordnung: {einordnung}")
    if luecken:
        print("\n  Ohne Beleg, daher nicht bewertet:")
        for label in luecken:
            print(f"    - {label}")
        print("  Ein aus Annahmen hochgerechneter Score waere schlechter als dieser.")

    print("\n  Frontmatter fuer den Vault:")
    print(f"    assessment_score: {score if not ko_raw else ''}")
    print(f"    assessment_stand: {stand if not ko_raw else 'final'}")
    print(f"    knockout: {'true' if ko_raw else 'false'}")
    if ko_raw:
        print(f"    knockout_grund: {ko_raw[0]}")
    for key, slug, _l in SIGNALE:
        print(f"    sig_{slug}: {werte[key] if werte[key] is not None else ''}")
    if args.mandatstyp != "standard":
        print(f"    gewichtung_abweichend: {args.mandatstyp}")
    print()
    return 0 if (score >= 70 and not ko_raw and not luecken) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(130)
