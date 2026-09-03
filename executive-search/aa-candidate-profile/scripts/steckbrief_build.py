#!/usr/bin/env python3
"""Steckbrief-Generator und Compliance-Pruefer fuer A/A Executive Search.

Erzeugt aus einer strukturierten JSON-Datei ein kopierfreundliches
Kandidatenprofil (Vollprofil oder Blindprofil) und prueft es gegen die
Leitplanken aus references/agg-dsgvo-leitplanken.md.

Nur Standardbibliothek, Python 3.8+. Keine LLM-Aufrufe.

Beispiele:
    python3 steckbrief_build.py profil.json
    python3 steckbrief_build.py profil.json --modus blindprofil --out profil.md
    python3 steckbrief_build.py profil.json --check
    python3 steckbrief_build.py profil.json --check --json

Exit-Codes:
    0  keine Fehler (Warnungen moeglich)
    2  Fehler gefunden, Profil nicht freigabefaehig
    1  Bedienfehler (Datei fehlt, JSON kaputt)
"""

import argparse
import json
import re
import sys

MODI = ("vollprofil", "blindprofil")

# Feldnamen, die im Steckbrief nichts zu suchen haben.
# Bezug: AGG Paragraf 1 und DSGVO Artikel 9.
VERBOTENE_FELDER = {
    "foto": "Bewerbungsfoto",
    "photo": "Bewerbungsfoto",
    "bild": "Bewerbungsfoto",
    "geburtsdatum": "Geburtsdatum",
    "geburtsort": "Geburtsort",
    "birth_date": "Geburtsdatum",
    "familienstand": "Familienstand",
    "marital_status": "Familienstand",
    "kinder": "Kinderzahl",
    "children": "Kinderzahl",
    "staatsangehoerigkeit": "Staatsangehoerigkeit",
    "nationalitaet": "Staatsangehoerigkeit",
    "nationality": "Staatsangehoerigkeit",
    "religion": "Religionszugehoerigkeit",
    "konfession": "Religionszugehoerigkeit",
    "behinderung": "Behinderung",
    "schwerbehinderung": "Behinderung",
    "gesundheit": "Gesundheitsdaten",
    "health": "Gesundheitsdaten",
    "partei": "Politische Meinung",
    "gewerkschaft": "Gewerkschaftszugehoerigkeit",
    "sexuelle_orientierung": "Sexuelle Identitaet",
}

# Textmuster, die auf ein unzulaessiges Merkmal hindeuten.
# Tier "fehler" blockiert, Tier "warnung" verlangt eine bewusste Entscheidung.
TEXTMUSTER = [
    ("fehler", r"\bschwerbehind\w*", "Behinderung"),
    ("fehler", r"\bgrad der behinderung\b|\bgdb\s*\d", "Behinderung"),
    ("fehler", r"\bverheiratet\b|\bledig\b|\bgeschieden\b|\bverwitwet\b", "Familienstand"),
    ("fehler", r"\bstaatsangeh\w*|\bnationalit\w*", "Staatsangehoerigkeit"),
    ("fehler", r"\br(oe|ö)misch-katholisch\b|\bevangelisch\b|\bkonfession\w*", "Religionszugehoerigkeit"),
    ("fehler", r"\bgewerkschaft\w*", "Gewerkschaftszugehoerigkeit"),
    ("fehler", r"\bgeb(oren|\.)\s*(am\s*)?\d{1,2}\.\d{1,2}\.\d{4}", "Geburtsdatum"),
    ("warnung", r"\belternzeit\b|\bmutterschutz\b", "Elternzeit oder Mutterschutz"),
    ("warnung", r"\bschwanger\w*", "Schwangerschaft"),
    ("warnung", r"\bkrankheit\b|\berkrankung\b|\bburnout\b|\breha\b", "Gesundheitsdaten"),
]

PFLICHTBLOECKE = [
    ("mandat", "Block 1, Kopf"),
    ("summary", "Block 2, Executive Summary"),
    ("kandidat", "Block 3, Eckdaten"),
    ("werdegang", "Block 4, Werdegang"),
    ("kompetenzen", "Block 5, Kompetenzprofil"),
    ("passung", "Block 6, Passung zum Mandat"),
    ("risiken", "Block 9, Risiken und offene Punkte"),
    ("empfehlung", "Block 10, Empfehlung des Beraters"),
]

VERTRAULICHKEIT = (
    "Vertraulich. Dieses Kandidatenprofil wurde von A/A Executive Search "
    "ausschliesslich fuer den benannten Auftraggeber und die benannte Position "
    "erstellt. Weitergabe an Dritte nur nach schriftlicher Zustimmung."
)


class Befund:
    def __init__(self, tier, ort, text):
        self.tier = tier
        self.ort = ort
        self.text = text

    def as_dict(self):
        return {"tier": self.tier, "ort": self.ort, "text": self.text}

    def __str__(self):
        marke = {"fehler": "FEHLER ", "warnung": "WARNUNG", "hinweis": "HINWEIS"}[self.tier]
        return "%s  %-28s %s" % (marke, self.ort, self.text)


def walk(node, pfad=""):
    """Liefert (pfad, key, value) fuer jedes Blatt und jeden Key im Baum."""
    if isinstance(node, dict):
        for key, value in node.items():
            unterpfad = "%s.%s" % (pfad, key) if pfad else str(key)
            yield unterpfad, str(key), value
            for item in walk(value, unterpfad):
                yield item
    elif isinstance(node, list):
        for index, value in enumerate(node):
            unterpfad = "%s[%d]" % (pfad, index)
            yield unterpfad, None, value
            for item in walk(value, unterpfad):
                yield item


def modus_bestimmen(daten, override):
    if override:
        return override
    modus = str(daten.get("mandat", {}).get("modus", "")).strip().lower()
    return modus if modus in MODI else "vollprofil"


def pruefe(daten, modus):
    befunde = []

    for schluessel, blockname in PFLICHTBLOECKE:
        wert = daten.get(schluessel)
        if not wert:
            befunde.append(Befund("fehler", schluessel, "%s fehlt oder ist leer." % blockname))

    summary = daten.get("summary") or []
    if isinstance(summary, list) and 0 < len(summary) < 5:
        befunde.append(Befund(
            "warnung", "summary",
            "Executive Summary hat %d von 5 Saetzen. Fehlt der Vorbehaltssatz?" % len(summary)))

    if not daten.get("empfehlung", {}).get("begruendung"):
        befunde.append(Befund("warnung", "empfehlung", "Empfehlung ohne Begruendung."))

    if not daten.get("offene_fragen"):
        befunde.append(Befund("warnung", "offene_fragen",
                              "Keine offenen Fragen fuer das naechste Gespraech hinterlegt."))

    if daten.get("assessment") in (None, {}, []):
        befunde.append(Befund("hinweis", "assessment",
                              "A/A-Assessment nicht enthalten. Block 7 wird ausgelassen."))

    for eintrag in daten.get("werdegang") or []:
        if not isinstance(eintrag, dict):
            continue
        label = "%s-%s" % (eintrag.get("von", "?"), eintrag.get("bis", "?"))
        if not eintrag.get("ergebnisse"):
            befunde.append(Befund("warnung", "werdegang %s" % label,
                                  "Station ohne messbares Ergebnis. Interviewstoff."))

    for eintrag in daten.get("passung") or []:
        if isinstance(eintrag, dict) and not eintrag.get("beleg"):
            befunde.append(Befund("warnung", "passung",
                                  "Anforderung '%s' ohne Beleg." % eintrag.get("anforderung", "?")))

    # Freigabe und Jahrgang
    kandidat = daten.get("kandidat") or {}
    freigabe = daten.get("freigabe") or {}
    if modus == "vollprofil" and not freigabe.get("einwilligung_dokumentiert"):
        befunde.append(Befund("fehler", "freigabe",
                              "Vollprofil ohne dokumentierte Einwilligung des Kandidaten."))
    if kandidat.get("jahrgang") and not kandidat.get("jahrgang_einwilligung"):
        befunde.append(Befund("fehler", "kandidat.jahrgang",
                              "Jahrgang genannt, aber keine Einwilligung hinterlegt."))

    # Blindmodus
    if modus == "blindprofil":
        if kandidat.get("name"):
            befunde.append(Befund("hinweis", "kandidat.name",
                                  "Klarname liegt in den Quelldaten und wird im Blindprofil "
                                  "nicht ausgegeben. Ausgabedatei vor Versand gegenlesen."))
        for eintrag in daten.get("werdegang") or []:
            if isinstance(eintrag, dict) and eintrag.get("unternehmen") and not eintrag.get("unternehmenstyp"):
                befunde.append(Befund(
                    "fehler", "werdegang",
                    "Blindprofil: '%s' ohne Typisierung. Unternehmenstyp ergaenzen."
                    % eintrag["unternehmen"]))
        name = str(kandidat.get("name") or "").strip()
        namensteile = [t for t in name.split() if len(t) > 2]
        for pfad, _key, wert in walk(daten):
            if not isinstance(wert, str) or pfad == "kandidat.name":
                continue
            for teil in namensteile:
                if teil.lower() in wert.lower():
                    befunde.append(Befund(
                        "fehler", pfad,
                        "Blindprofil: Namensbestandteil '%s' steht im Freitext und wird "
                        "mit ausgegeben. Umformulieren." % teil))
                    break
        befunde.append(Befund("hinweis", "blindprofil",
                              "Identifizierbarkeit manuell pruefen: Kombination aus Region, "
                              "Groesse und Nische kann re-identifizieren."))

    # Verbotene Felder und Textmuster
    for pfad, key, wert in walk(daten):
        if key and key.lower().lstrip("_") in VERBOTENE_FELDER:
            befunde.append(Befund("fehler", pfad,
                                  "Unzulaessiges Merkmal: %s. Feld entfernen."
                                  % VERBOTENE_FELDER[key.lower().lstrip("_")]))
        if isinstance(wert, str):
            klein = wert.lower()
            for tier, muster, merkmal in TEXTMUSTER:
                if re.search(muster, klein):
                    befunde.append(Befund(tier, pfad,
                                          "Textstelle deutet auf %s hin. Pruefen und ggf. streichen."
                                          % merkmal))
    return befunde


def zeile(label, wert):
    return "%s: %s" % (label, wert) if wert else None


def render(daten, modus):
    mandat = daten.get("mandat") or {}
    kandidat = daten.get("kandidat") or {}
    freigabe = daten.get("freigabe") or {}
    blind = modus == "blindprofil"
    out = []

    out.append("Kandidaten-Steckbrief")
    out.append("")
    out.append("Block 1, Kopf")
    out.append("")
    for label, wert in [
        ("Mandat und Position", mandat.get("position")),
        ("Auftraggeber", mandat.get("auftraggeber")),
        ("Profil-ID", mandat.get("profil_id")),
        ("Datum", mandat.get("datum")),
    ]:
        z = zeile(label, wert)
        if z:
            out.append(z)
    if mandat.get("berater"):
        out.append("Berater: %s, A/A Executive Search" % mandat["berater"])
    out.append("Modus: %s" % ("Blindprofil, anonymisiert" if blind else "Vollprofil mit Freigabe"))
    if not blind and freigabe.get("einwilligung_datum"):
        out.append("Freigabe des Kandidaten dokumentiert am %s" % freigabe["einwilligung_datum"])
    out.append(VERTRAULICHKEIT)
    out.append("")

    out.append("Block 2, Executive Summary")
    out.append("")
    out.append(" ".join(daten.get("summary") or ["Nicht erfasst."]))
    out.append("")

    out.append("Block 3, Eckdaten")
    out.append("")
    if not blind and kandidat.get("name"):
        out.append("Name: %s" % kandidat["name"])
    if kandidat.get("jahrgang") and kandidat.get("jahrgang_einwilligung"):
        out.append("Jahrgang: %s, Einwilligung zur Nennung liegt vor" % kandidat["jahrgang"])
    for label, schluessel in [
        ("Wohnregion", "wohnregion"),
        ("Mobilitaet", "mobilitaet"),
        ("Aktuelle Fuehrungsspanne", "fuehrungsspanne"),
        ("Budget- oder Ergebnisverantwortung", "ergebnisverantwortung"),
        ("Verfuegbarkeit", "verfuegbarkeit"),
        ("Kuendigungsfrist", "kuendigungsfrist"),
    ]:
        z = zeile(label, kandidat.get(schluessel))
        if z:
            out.append(z)
    if kandidat.get("sprachen"):
        out.append("Sprachen: %s" % ", ".join(kandidat["sprachen"]))
    out.append("")

    out.append("Block 4, Werdegang")
    out.append("")
    for eintrag in daten.get("werdegang") or []:
        firma = eintrag.get("unternehmenstyp") if blind else (
            eintrag.get("unternehmen") or eintrag.get("unternehmenstyp"))
        kopf = "%s bis %s, %s" % (eintrag.get("von", "?"), eintrag.get("bis", "?"), firma or "?")
        if eintrag.get("groesse"):
            kopf += ", %s" % eintrag["groesse"]
        out.append(kopf)
        if eintrag.get("rolle"):
            out.append("Rolle: %s" % eintrag["rolle"])
        if eintrag.get("verantwortung"):
            out.append("Verantwortung: %s" % eintrag["verantwortung"])
        ergebnisse = eintrag.get("ergebnisse") or []
        out.append("Ergebnisse: %s" % ("; ".join(ergebnisse) if ergebnisse
                                       else "Im Lebenslauf keine Kennzahlen angegeben, im Interview zu erheben."))
        out.append("")
    luecken = daten.get("luecken") or []
    out.append("Luecken: %s" % (" ".join(luecken) if luecken else "Nicht geprueft."))
    out.append("")

    out.append("Block 5, Kompetenzprofil")
    out.append("")
    kompetenzen = daten.get("kompetenzen") or {}
    for label, schluessel in [("Fachkompetenz", "fachlich"),
                              ("Fuehrungskompetenz", "fuehrung"),
                              ("Branchenkompetenz", "branche")]:
        werte = kompetenzen.get(schluessel) or []
        if werte:
            out.append("%s: %s" % (label, "; ".join(werte)))
    out.append("")

    out.append("Block 6, Passung zum Mandat")
    out.append("")
    for eintrag in daten.get("passung") or []:
        out.append("%s: %s. Beleg: %s" % (
            eintrag.get("anforderung", "?"),
            eintrag.get("status", "nicht bewertet"),
            eintrag.get("beleg", "offen")))
    out.append("")

    assessment = daten.get("assessment")
    if assessment:
        out.append("Block 7, A/A-Assessment")
        out.append("")
        if isinstance(assessment, dict):
            for key, value in assessment.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                out.append("%s: %s" % (key, value))
        else:
            out.append(str(assessment))
        out.append("")

    out.append("Block 8, Motivation und Wechselgrund")
    out.append("")
    out.append(daten.get("motivation") or "Nicht erfasst, im Gespraech zu klaeren.")
    out.append("")

    out.append("Block 9, Risiken und offene Punkte")
    out.append("")
    for risiko in daten.get("risiken") or ["Nicht erfasst."]:
        out.append(risiko)
    fragen = daten.get("offene_fragen") or []
    if fragen:
        out.append("Im naechsten Gespraech zu klaeren: %s" % "; ".join(fragen))
    out.append("")

    out.append("Block 10, Empfehlung des Beraters")
    out.append("")
    empfehlung = daten.get("empfehlung") or {}
    out.append("%s, weil %s" % (
        empfehlung.get("votum", "Votum offen"),
        empfehlung.get("begruendung", "Begruendung fehlt.")))

    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Erzeugt und prueft einen Kandidaten-Steckbrief fuer A/A Executive Search.")
    parser.add_argument("profil", help="JSON-Datei mit den Kandidatendaten")
    parser.add_argument("--modus", choices=MODI,
                        help="ueberschreibt mandat.modus aus der JSON-Datei")
    parser.add_argument("--check", action="store_true",
                        help="nur pruefen, kein Steckbrief")
    parser.add_argument("--json", action="store_true", dest="als_json",
                        help="Pruefergebnis maschinenlesbar ausgeben")
    parser.add_argument("--out", help="Ausgabedatei statt stdout")
    args = parser.parse_args(argv)

    try:
        with open(args.profil, "r", encoding="utf-8") as handle:
            daten = json.load(handle)
    except FileNotFoundError:
        print("Datei nicht gefunden: %s" % args.profil, file=sys.stderr)
        return 1
    except json.JSONDecodeError as err:
        print("JSON nicht lesbar: %s" % err, file=sys.stderr)
        return 1

    modus = modus_bestimmen(daten, args.modus)
    befunde = pruefe(daten, modus)
    fehler = [b for b in befunde if b.tier == "fehler"]

    if args.check:
        if args.als_json:
            print(json.dumps({
                "modus": modus,
                "freigabefaehig": not fehler,
                "anzahl": {
                    "fehler": len(fehler),
                    "warnung": len([b for b in befunde if b.tier == "warnung"]),
                    "hinweis": len([b for b in befunde if b.tier == "hinweis"]),
                },
                "befunde": [b.as_dict() for b in befunde],
            }, ensure_ascii=False, indent=2))
        else:
            print("Pruefung Steckbrief, Modus %s" % modus)
            print("")
            if befunde:
                for befund in befunde:
                    print(befund)
            else:
                print("Keine Befunde.")
            print("")
            print("Ergebnis: %s" % ("nicht freigabefaehig, %d Fehler" % len(fehler)
                                    if fehler else "freigabefaehig, keine Fehler"))
        return 2 if fehler else 0

    text = render(daten, modus)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("Geschrieben: %s" % args.out, file=sys.stderr)
    else:
        sys.stdout.write(text)

    if fehler:
        print("", file=sys.stderr)
        print("ACHTUNG, %d Fehler in der Compliance-Pruefung. Vor Versand beheben:"
              % len(fehler), file=sys.stderr)
        for befund in fehler:
            print("  %s" % befund, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
