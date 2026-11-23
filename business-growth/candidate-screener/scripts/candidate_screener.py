#!/usr/bin/env python3
"""Candidate Screener fuer Executive Search im Premium-Automobilhandel.

Erzeugt Suchstrings (Google X-Ray, LinkedIn, Xing) fuer manuelle Recherche
und fuehrt ein Kandidaten-Tracking (CSV). Kein Scraping, keine Netzwerkzugriffe,
keine LLM-Calls. Nur Python-Standardbibliothek.

Beispiele:
  python candidate_screener.py queries --plz 80331 --radius 50 \
      --orte "Muenchen,Augsburg,Rosenheim" --marken audi,bmw,mercedes
  python candidate_screener.py add --name "Max Muster" --funktion Verkaufsleiter \
      --autohaus "Autohaus X" --marke BMW --ort Augsburg --quelle "LinkedIn-Profil" \
      --url https://... --punkte 2,2,1,1
  python candidate_screener.py list --status neu
  python candidate_screener.py update 1 --status kontaktiert --followup 2026-12-08
  python candidate_screener.py due
"""
import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta

MARKEN = {
    "audi": ["Audi"],
    "bmw": ["BMW", "MINI"],
    "mercedes": ["Mercedes-Benz", "Mercedes", "Daimler"],
    "porsche": ["Porsche"],
    "volvo": ["Volvo"],
    "lexus": ["Lexus"],
}

ROLLEN = {
    "verkaufsleiter": ["Verkaufsleiter", "Verkaufsleitung", "Leiter Verkauf",
                       "Head of Sales", "Sales Manager", "Verkaufsdirektor"],
    "neuwagen": ["Neuwagenleiter", "Leiter Neuwagen", "Neuwagenverkaufsleiter"],
    "gebrauchtwagen": ["Gebrauchtwagenleiter", "Leiter Gebrauchtwagen",
                       "Leiter Used Cars"],
    "geschaeftsfuehrer": ["Geschaeftsfuehrer", "Geschäftsführer",
                          "Managing Director", "General Manager"],
    "vorstand": ["Vorstand", "Mitglied der Geschaeftsleitung",
                 "Geschäftsleitung", "Prokurist"],
}

STATUS = ["neu", "kontaktiert", "gespraech", "vorgestellt", "absage", "platziert"]
FIT = "ABC"
FIELDS = ["id", "name", "funktion", "autohaus", "marke", "ort", "datenquelle",
          "url", "punkte", "fit", "status", "erstkontakt", "followup",
          "loeschfrist", "notiz"]
DEFAULT_FILE = "kandidaten_tracking.csv"
LOESCH_TAGE = 180  # Vorschlag, mit Datenschutzberater abstimmen


# ---------- Suchstrings ----------
def _or(terms):
    return "(" + " OR ".join('"%s"' % t for t in terms) + ")"


def build_queries(plz, radius, orte, marken, rollen):
    brand_terms = [t for m in marken for t in MARKEN.get(m, [m])]
    role_terms = [t for r in rollen for t in ROLLEN.get(r, [r])]
    # Kurzfassung fuer Google (Limit ca. 32 Woerter): je 2 Rollenbegriffe, je 1 Markenbegriff
    short_roles = [t for r in rollen for t in ROLLEN.get(r, [r])[:2]]
    short_brands = [MARKEN.get(m, [m])[0] for m in marken]
    out = []
    geo = _or(orte) if orte else ""
    out.append({
        "typ": "Google X-Ray (LinkedIn)",
        "string": "site:linkedin.com/in %s %s %s" % (
            _or(short_roles), _or(short_brands), geo)})
    out.append({
        "typ": "Google X-Ray (Xing)",
        "string": "site:xing.com/profile %s %s %s" % (
            _or(short_roles), _or(short_brands), geo)})
    out.append({
        "typ": "LinkedIn Boolean (Recruiter/Sales Navigator, Titelfeld)",
        "string": "%s AND %s" % (_or(role_terms), _or(brand_terms))})
    out.append({
        "typ": "Standortfilter (in Recruiter/Sales Navigator setzen)",
        "string": "PLZ %s, Umkreis %s km" % (plz, radius)})
    if orte:
        for ort in orte:
            out.append({
                "typ": "Standort-Check Autohaeuser",
                "string": '%s Autohaus %s %s' % (
                    _or(brand_terms), ort, "Ansprechpartner Verkauf Team")})
    out.append({
        "typ": "Presse/Wechselsignale",
        "string": '%s %s (Neuer OR Nachfolge OR Uebernahme OR Verkauf OR '
                  'Restrukturierung) Autohaus %s' % (
                      _or(short_roles[:3]), _or(short_brands), geo)})
    return out


def cmd_queries(a):
    marken = [m.strip().lower() for m in a.marken.split(",") if m.strip()]
    rollen = [r.strip().lower() for r in a.rollen.split(",") if r.strip()]
    orte = [o.strip() for o in a.orte.split(",") if o.strip()] if a.orte else []
    res = build_queries(a.plz, a.radius, orte, marken, rollen)
    if a.format == "json":
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("Suchstrings | PLZ %s | Umkreis %s km | Marken: %s | Rollen: %s\n"
              % (a.plz, a.radius, ", ".join(marken), ", ".join(rollen)))
        for i, q in enumerate(res, 1):
            print("%d. %s\n   %s\n" % (i, q["typ"], q["string"]))
        print("Hinweis: Strings manuell ausfuehren. Kein automatisiertes "
              "Auslesen von LinkedIn/Xing (AGB).")
        print("Hinweis: Der Umkreis wird nicht berechnet. Entweder in "
              "Recruiter/Sales Navigator filtern oder Orte via --orte angeben.")


# ---------- Tracking ----------
def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def score_to_fit(punkte):
    s = sum(punkte)
    return "A" if s >= 6 else "B" if s >= 4 else "C"


def parse_punkte(s):
    try:
        p = [int(x) for x in s.split(",")]
    except ValueError:
        raise SystemExit("--punkte: vier Zahlen 0-2, z.B. 2,2,1,1")
    if len(p) != 4 or any(x < 0 or x > 2 for x in p):
        raise SystemExit("--punkte: genau vier Werte, je 0-2 "
                         "(Marke, Verantwortung, Wechselsignal, Erreichbarkeit)")
    return p


def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("Datum im Format JJJJ-MM-TT: %s" % s)
    return s


def cmd_add(a):
    rows = load(a.file)
    if not a.datenquelle and not a.quelle:
        raise SystemExit("--quelle ist Pflicht (Herkunft der Daten, Art. 14 DSGVO)")
    punkte = parse_punkte(a.punkte) if a.punkte else None
    fit = score_to_fit(punkte) if punkte else (a.fit or "")
    nid = max([int(r["id"]) for r in rows] + [0]) + 1
    rows.append({
        "id": str(nid), "name": a.name, "funktion": a.funktion or "",
        "autohaus": a.autohaus or "", "marke": a.marke or "", "ort": a.ort or "",
        "datenquelle": a.datenquelle or a.quelle, "url": a.url or "",
        "punkte": ",".join(map(str, punkte)) if punkte else "",
        "fit": fit, "status": "neu", "erstkontakt": "", "followup": "",
        "loeschfrist": "", "notiz": a.notiz or ""})
    save(a.file, rows)
    print("Kandidat %d angelegt (Fit %s)." % (nid, fit or "offen"))


def cmd_update(a):
    rows = load(a.file)
    row = next((r for r in rows if r["id"] == str(a.id)), None)
    if not row:
        raise SystemExit("ID %s nicht gefunden." % a.id)
    if a.status:
        if a.status not in STATUS:
            raise SystemExit("Status: " + ", ".join(STATUS))
        row["status"] = a.status
        if a.status == "kontaktiert" and not row["erstkontakt"]:
            row["erstkontakt"] = date.today().isoformat()
    if a.followup:
        row["followup"] = valid_date(a.followup)
    if a.fit:
        if a.fit.upper() not in FIT:
            raise SystemExit("Fit: A, B oder C")
        row["fit"] = a.fit.upper()
    if a.notiz:
        row["notiz"] = (row["notiz"] + " | " if row["notiz"] else "") + a.notiz
    if row["status"] in ("absage",) or a.status == "absage":
        row["loeschfrist"] = (date.today() + timedelta(days=LOESCH_TAGE)).isoformat()
    save(a.file, rows)
    print("Kandidat %s aktualisiert." % a.id)


def cmd_list(a):
    rows = load(a.file)
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    if a.fit:
        rows = [r for r in rows if r["fit"] == a.fit.upper()]
    rows.sort(key=lambda r: (r["fit"] or "Z", int(r["id"])))
    if a.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("Keine Eintraege.")
        return
    for r in rows:
        print("#%-3s [%s] %-12s %s | %s | %s %s | Follow-up: %s" % (
            r["id"], r["fit"] or "-", r["status"], r["name"], r["funktion"],
            r["marke"], r["autohaus"], r["followup"] or "-"))


def cmd_due(a):
    today = date.today().isoformat()
    rows = [r for r in load(a.file)
            if r["followup"] and r["followup"] <= today
            and r["status"] not in ("absage", "platziert")]
    rows.sort(key=lambda r: r["followup"])
    purge = [r for r in load(a.file) if r["loeschfrist"] and r["loeschfrist"] <= today]
    print("Faellige Follow-ups (%d):" % len(rows))
    for r in rows:
        print("  #%s %s (%s) faellig seit %s" % (
            r["id"], r["name"], r["status"], r["followup"]))
    if purge:
        print("\nLoeschfrist erreicht (%d):" % len(purge))
        for r in purge:
            print("  #%s %s seit %s" % (r["id"], r["name"], r["loeschfrist"]))


def cmd_delete(a):
    rows = load(a.file)
    keep = [r for r in rows if r["id"] != str(a.id)]
    if len(keep) == len(rows):
        raise SystemExit("ID %s nicht gefunden." % a.id)
    save(a.file, keep)
    print("Kandidat %s geloescht." % a.id)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", default=DEFAULT_FILE, help="Tracking-CSV")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("queries", help="Suchstrings erzeugen")
    q.add_argument("--plz", required=True)
    q.add_argument("--radius", type=int, default=50)
    q.add_argument("--orte", default="", help="Komma-getrennt, Orte im Umkreis")
    q.add_argument("--marken", default="audi,bmw,mercedes")
    q.add_argument("--rollen", default="verkaufsleiter,geschaeftsfuehrer,vorstand")
    q.add_argument("--format", choices=["text", "json"], default="text")
    q.set_defaults(fn=cmd_queries)

    ad = sub.add_parser("add", help="Kandidat anlegen")
    ad.add_argument("--name", required=True)
    ad.add_argument("--funktion")
    ad.add_argument("--autohaus")
    ad.add_argument("--marke")
    ad.add_argument("--ort")
    ad.add_argument("--quelle", help="Herkunft der Daten (Pflicht)")
    ad.add_argument("--datenquelle", help=argparse.SUPPRESS)
    ad.add_argument("--url")
    ad.add_argument("--punkte", help="4 Werte 0-2: Marke,Verantwortung,"
                    "Wechselsignal,Erreichbarkeit")
    ad.add_argument("--fit", help="A/B/C manuell")
    ad.add_argument("--notiz")
    ad.set_defaults(fn=cmd_add)

    u = sub.add_parser("update", help="Kandidat aktualisieren")
    u.add_argument("id", type=int)
    u.add_argument("--status")
    u.add_argument("--followup", help="JJJJ-MM-TT")
    u.add_argument("--fit")
    u.add_argument("--notiz")
    u.set_defaults(fn=cmd_update)

    l = sub.add_parser("list", help="Kandidaten anzeigen")
    l.add_argument("--status")
    l.add_argument("--fit")
    l.add_argument("--format", choices=["text", "json"], default="text")
    l.set_defaults(fn=cmd_list)

    d = sub.add_parser("due", help="Faellige Follow-ups und Loeschfristen")
    d.set_defaults(fn=cmd_due)

    x = sub.add_parser("delete", help="Kandidat loeschen")
    x.add_argument("id", type=int)
    x.set_defaults(fn=cmd_delete)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
