#!/usr/bin/env python3
"""
km_kostenrechner.py - Kilometerkosten-Rechner fuer privat geleaste Fahrzeuge,
die betrieblich mitgenutzt werden (Nutzungseinlage ins Einzelunternehmen).

Ermittelt aus den Fahrzeug-Gesamtkosten und der Jahresfahrleistung den
individuellen Kilometersatz, rechnet ihn gegen die 0,30-EUR-Pauschale und
leitet den abziehbaren Betriebsausgabenbetrag je Fahrtkategorie ab.

Standardbibliothek only. Keine Steuerberatung.
"""

import argparse
import csv
import json
import sys
from datetime import date, datetime

# --------------------------------------------------------------------------
# Steuerliche Parameter (Stand 2026) - jaehrlich pruefen
# --------------------------------------------------------------------------

PARAMETER = {
    2025: {"pauschale_dienstreise": 0.30, "entf_pauschale_bis20": 0.30, "entf_pauschale_ab21": 0.38},
    2026: {"pauschale_dienstreise": 0.30, "entf_pauschale_bis20": 0.38, "entf_pauschale_ab21": 0.38},
}
STANDARD_JAHR = 2026

KATEGORIEN = ("dienstreise", "betriebsstaette", "privat")

# Kostenarten, die NICHT in die Gesamtkosten gehoeren (Pruefhinweis)
NICHT_GESAMTKOSTEN = (
    "parkgebuehren", "maut", "faehre", "bussgeld", "verwarnungsgeld",
    "unfallkosten_privatfahrt", "insassenunfallversicherung_privat",
)


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------

def eur(betrag, nachkomma=2):
    """Deutsche Zahlenformatierung: 1.234,56"""
    s = f"{betrag:,.{nachkomma}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def zahl(wert, nachkomma=0):
    return eur(wert, nachkomma)


def prozent(anteil, nachkomma=1):
    """0.036 -> '3,6 %'"""
    return f"{eur(anteil * 100, nachkomma)} %"


def fehler(msg):
    print(f"FEHLER: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_datum(s):
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unlesbares Datum: {s!r} (erwartet JJJJ-MM-TT oder TT.MM.JJJJ)")


def monate_im_jahr(vertragsbeginn, laufzeit_monate, jahr):
    """Wie viele Vertragsmonate fallen in das Kalenderjahr?"""
    start = vertragsbeginn
    ende_monat_index = start.month - 1 + laufzeit_monate - 1
    ende_jahr = start.year + ende_monat_index // 12
    ende_monat = ende_monat_index % 12 + 1
    ende = date(ende_jahr, ende_monat, 1)

    treffer = 0
    for i in range(laufzeit_monate):
        idx = start.month - 1 + i
        m_jahr = start.year + idx // 12
        if m_jahr == jahr:
            treffer += 1
        if m_jahr > jahr:
            break
    return treffer, ende


# --------------------------------------------------------------------------
# Profil laden
# --------------------------------------------------------------------------

def lade_profil(pfad):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        fehler(f"Fahrzeugprofil nicht gefunden: {pfad}")
    except json.JSONDecodeError as e:
        fehler(f"Fahrzeugprofil ist kein gueltiges JSON: {e}")


def summe_block(block, name):
    if not isinstance(block, dict):
        fehler(f"Abschnitt '{name}' muss ein Objekt mit Kostenpositionen sein.")
    gesamt = 0.0
    for k, v in block.items():
        if not isinstance(v, (int, float)):
            fehler(f"Position '{name}.{k}' ist keine Zahl: {v!r}")
        if k.lower() in NICHT_GESAMTKOSTEN:
            print(
                f"WARNUNG: '{k}' gehoert nicht in die Fahrzeug-Gesamtkosten. "
                f"Reisenebenkosten und Bussgelder separat behandeln "
                f"(siehe references/gesamtkosten-katalog.md).",
                file=sys.stderr,
            )
        gesamt += float(v)
    return gesamt


# --------------------------------------------------------------------------
# Fahrtenbuch
# --------------------------------------------------------------------------

def lade_fahrtenbuch(pfad, jahr):
    """Liest Fahrtenbuch-CSV und aggregiert km je Kategorie."""
    fahrten = []
    try:
        with open(pfad, "r", encoding="utf-8-sig", newline="") as f:
            probe = f.read(2048)
            f.seek(0)
            trenner = ";" if probe.count(";") >= probe.count(",") else ","
            leser = csv.DictReader(f, delimiter=trenner)
            pflicht = {"datum", "km_stand_start", "km_stand_ende", "kategorie"}
            kopf = {(h or "").strip().lower() for h in (leser.fieldnames or [])}
            fehlend = pflicht - kopf
            if fehlend:
                fehler(
                    f"Fahrtenbuch: Pflichtspalten fehlen: {', '.join(sorted(fehlend))}. "
                    f"Vorlage: assets/fahrtenbuch-vorlage.csv"
                )
            for nr, zeile in enumerate(leser, start=2):
                z = {(k or "").strip().lower(): (v or "").strip() for k, v in zeile.items()}
                if not z.get("datum"):
                    continue
                try:
                    d = parse_datum(z["datum"])
                    start = int(float(z["km_stand_start"]))
                    ende = int(float(z["km_stand_ende"]))
                except ValueError as e:
                    fehler(f"Fahrtenbuch Zeile {nr}: {e}")
                kat = z.get("kategorie", "").lower()
                if kat not in KATEGORIEN:
                    fehler(
                        f"Fahrtenbuch Zeile {nr}: Kategorie '{kat}' unbekannt. "
                        f"Erlaubt: {', '.join(KATEGORIEN)}"
                    )
                if ende < start:
                    fehler(f"Fahrtenbuch Zeile {nr}: km-Stand Ende < Start ({ende} < {start})")
                if d.year != jahr:
                    continue
                fahrten.append({
                    "zeile": nr, "datum": d, "start": start, "ende": ende,
                    "km": ende - start, "kategorie": kat,
                    "ziel": z.get("ziel", ""), "zweck": z.get("zweck", ""),
                    "geschaeftspartner": z.get("geschaeftspartner", ""),
                })
    except FileNotFoundError:
        fehler(f"Fahrtenbuch nicht gefunden: {pfad}")

    if not fahrten:
        fehler(f"Fahrtenbuch enthaelt keine Fahrten fuer {jahr}.")

    fahrten.sort(key=lambda f: (f["datum"], f["start"]))
    return fahrten


def pruefe_fahrtenbuch(fahrten):
    """Formale Plausibilitaetspruefung - liefert Liste von Beanstandungen."""
    maengel = []
    vorher = None
    for f in fahrten:
        if vorher is not None:
            if f["start"] < vorher["ende"]:
                maengel.append(
                    f"Zeile {f['zeile']} ({f['datum']:%d.%m.%Y}): km-Stand Start {f['start']} "
                    f"liegt unter dem Endstand der Vorfahrt ({vorher['ende']}) - Ueberlappung."
                )
            elif f["start"] > vorher["ende"]:
                luecke = f["start"] - vorher["ende"]
                maengel.append(
                    f"Zeile {f['zeile']} ({f['datum']:%d.%m.%Y}): Luecke von {luecke} km "
                    f"zur Vorfahrt ({vorher['ende']} -> {f['start']}) - nicht erfasste Fahrt."
                )
        if f["kategorie"] == "dienstreise":
            if not f["ziel"]:
                maengel.append(f"Zeile {f['zeile']}: Dienstreise ohne Reiseziel.")
            if not f["zweck"]:
                maengel.append(f"Zeile {f['zeile']}: Dienstreise ohne Reisezweck.")
            if not f["geschaeftspartner"]:
                maengel.append(
                    f"Zeile {f['zeile']}: Dienstreise ohne aufgesuchten Geschaeftspartner."
                )
        if f["km"] == 0:
            maengel.append(f"Zeile {f['zeile']}: Fahrt mit 0 km.")
        vorher = f
    return maengel


# --------------------------------------------------------------------------
# Kernberechnung
# --------------------------------------------------------------------------

def berechne(profil, fahrten, jahr, monat=None):
    p = PARAMETER.get(jahr, PARAMETER[STANDARD_JAHR])
    steuer = profil.get("steuer", {})
    satz_dienstreise = float(steuer.get("pauschale_dienstreise_eur_km", p["pauschale_dienstreise"]))
    satz_entf_bis20 = float(steuer.get("entfernungspauschale_bis20_eur_km", p["entf_pauschale_bis20"]))
    satz_entf_ab21 = float(steuer.get("entfernungspauschale_ab21_eur_km", p["entf_pauschale_ab21"]))

    # --- Kostenblock: Leasing ---
    leasing = profil.get("leasing", {})
    rate = float(leasing.get("monatsrate", 0.0))
    sonderzahlung = float(leasing.get("sonderzahlung", 0.0))
    laufzeit = int(leasing.get("laufzeit_monate", 0) or 0)
    beginn_roh = leasing.get("vertragsbeginn")

    if sonderzahlung > 0 and laufzeit <= 0:
        fehler(
            "Leasingsonderzahlung angegeben, aber 'leasing.laufzeit_monate' fehlt. "
            "Die Sonderzahlung muss periodengerecht auf die Vertragslaufzeit verteilt "
            "werden (BFH VIII R 1/21, VI R 9/22)."
        )

    if beginn_roh and laufzeit > 0:
        beginn = parse_datum(beginn_roh)
        vertragsmonate, vertragsende = monate_im_jahr(beginn, laufzeit, jahr)
    else:
        beginn, vertragsende = None, None
        vertragsmonate = 12

    leasingraten_pa = rate * vertragsmonate
    sonderzahlung_pa = (sonderzahlung / laufzeit * vertragsmonate) if laufzeit else 0.0

    fix = summe_block(profil.get("fixkosten_pa", {}), "fixkosten_pa")
    var = summe_block(profil.get("variable_kosten_pa", {}), "variable_kosten_pa")

    gesamtkosten = leasingraten_pa + sonderzahlung_pa + fix + var

    # --- Fahrleistung ---
    fl = profil.get("fahrleistung", {})
    km_start = fl.get("km_stand_jahresbeginn")
    km_ende = fl.get("km_stand_jahresende")

    km_aus_fahrtenbuch = sum(f["km"] for f in fahrten)
    if km_start is not None and km_ende is not None:
        gesamt_km = int(km_ende) - int(km_start)
        if gesamt_km <= 0:
            fehler("Jahresfahrleistung aus km-Staenden ist 0 oder negativ.")
        quelle_km = "Kilometerstaende (Jahresanfang/-ende)"
    else:
        gesamt_km = km_aus_fahrtenbuch
        quelle_km = "Summe Fahrtenbuch"

    differenz_km = gesamt_km - km_aus_fahrtenbuch

    if gesamt_km <= 0:
        fehler("Gesamtfahrleistung ist 0 - Kilometersatz nicht berechenbar.")

    km_satz = gesamtkosten / gesamt_km

    # --- Kategorien ---
    km_kat = {k: 0 for k in KATEGORIEN}
    for f in fahrten:
        km_kat[f["kategorie"]] += f["km"]
    # nicht erfasste Kilometer gelten als privat (konservativ)
    km_kat["privat"] += max(differenz_km, 0)

    km_dienst = km_kat["dienstreise"]
    km_bs = km_kat["betriebsstaette"]
    km_privat = km_kat["privat"]

    betrieblich_km = km_dienst + km_bs
    betriebsanteil = betrieblich_km / gesamt_km

    # --- Abzug Dienstreisen: individueller Satz vs. Pauschale ---
    abzug_individuell = km_dienst * km_satz
    abzug_pauschal = km_dienst * satz_dienstreise
    guenstiger = "individuell" if abzug_individuell >= abzug_pauschal else "pauschal"
    abzug_dienstreise = max(abzug_individuell, abzug_pauschal)

    # --- Abzug Fahrten Wohnung <-> Betriebsstaette: nur Entfernungspauschale ---
    bs_cfg = steuer.get("betriebsstaette", {})
    arbeitstage = int(bs_cfg.get("tage", 0) or 0)
    entfernung = float(bs_cfg.get("entfernung_km_einfach", 0) or 0)
    if arbeitstage and entfernung:
        entf_km_gesamt = arbeitstage * entfernung
        bs_quelle = f"{arbeitstage} Tage x {zahl(entfernung, 1)} km einfache Entfernung"
    else:
        entfernung = 0.0
        entf_km_gesamt = km_bs / 2.0  # gefahrene km sind Hin- und Rueckweg
        bs_quelle = "gefahrene km aus Fahrtenbuch / 2"

    if entfernung and entfernung > 20:
        je_tag = 20 * satz_entf_bis20 + (entfernung - 20) * satz_entf_ab21
        abzug_betriebsstaette = je_tag * arbeitstage
    else:
        abzug_betriebsstaette = entf_km_gesamt * satz_entf_bis20

    # tatsaechliche Kosten der Betriebsstaettenfahrten (nur zum Vergleich)
    kosten_bs_tatsaechlich = km_bs * km_satz

    abzug_gesamt = abzug_dienstreise + abzug_betriebsstaette

    ergebnis = {
        "jahr": jahr,
        "kosten": {
            "leasingraten": round(leasingraten_pa, 2),
            "leasingsonderzahlung_anteil": round(sonderzahlung_pa, 2),
            "fixkosten": round(fix, 2),
            "variable_kosten": round(var, 2),
            "gesamtkosten": round(gesamtkosten, 2),
            "vertragsmonate_im_jahr": vertragsmonate,
            "vertragsende": vertragsende.isoformat() if vertragsende else None,
        },
        "fahrleistung": {
            "gesamt_km": gesamt_km,
            "quelle": quelle_km,
            "km_aus_fahrtenbuch": km_aus_fahrtenbuch,
            "differenz_km": differenz_km,
            "dienstreise_km": km_dienst,
            "betriebsstaette_km": km_bs,
            "privat_km": km_privat,
            "betriebsanteil": round(betriebsanteil, 4),
        },
        "kilometersatz": {
            "individuell": round(km_satz, 4),
            "pauschale_dienstreise": satz_dienstreise,
            "guenstigere_methode": guenstiger,
        },
        "abzug": {
            "dienstreise_individuell": round(abzug_individuell, 2),
            "dienstreise_pauschal": round(abzug_pauschal, 2),
            "dienstreise_angesetzt": round(abzug_dienstreise, 2),
            "betriebsstaette_entfernungspauschale": round(abzug_betriebsstaette, 2),
            "betriebsstaette_tatsaechliche_kosten": round(kosten_bs_tatsaechlich, 2),
            "betriebsstaette_basis": bs_quelle,
            "gesamt": round(abzug_gesamt, 2),
        },
        "monatlich": {
            "abzug_je_monat": round(abzug_gesamt / 12, 2),
            "km_dienst_je_monat": round(km_dienst / 12, 1),
        },
        "warnungen": warnungen(betriebsanteil, differenz_km, gesamt_km, laufzeit, sonderzahlung),
    }

    if monat:
        ergebnis["monatsabrechnung"] = monatsabrechnung(fahrten, monat, km_satz,
                                                       satz_dienstreise, guenstiger)
    return ergebnis


def monatsabrechnung(fahrten, monat, km_satz, satz_pauschal, methode):
    """Abrechnung fuer einen einzelnen Monat mit dem (vorlaeufigen) Kilometersatz."""
    try:
        jahr_m, mon_m = monat.split("-")
        jahr_m, mon_m = int(jahr_m), int(mon_m)
    except (ValueError, AttributeError):
        fehler(f"--monat erwartet Format JJJJ-MM, erhalten: {monat!r}")

    treffer = [f for f in fahrten if f["datum"].year == jahr_m and f["datum"].month == mon_m]
    km_dienst = sum(f["km"] for f in treffer if f["kategorie"] == "dienstreise")
    km_bs = sum(f["km"] for f in treffer if f["kategorie"] == "betriebsstaette")
    satz = km_satz if methode == "individuell" else satz_pauschal
    return {
        "monat": monat,
        "fahrten": len(treffer),
        "dienstreise_km": km_dienst,
        "betriebsstaette_km": km_bs,
        "angewandter_satz": round(satz, 4),
        "methode": methode,
        "betrag_dienstreisen": round(km_dienst * satz, 2),
        "hinweis": "Vorlaeufiger Satz - Jahresendabrechnung korrigiert auf den Ist-Satz.",
    }


def warnungen(betriebsanteil, differenz_km, gesamt_km, laufzeit, sonderzahlung):
    w = []
    if betriebsanteil > 0.50:
        w.append(
            f"Betrieblicher Nutzungsanteil {prozent(betriebsanteil)} liegt ueber 50 %. "
            "Ab dieser Schwelle behandelt die Finanzverwaltung das Fahrzeug regelmaessig "
            "als betriebliches Fahrzeug (voller Kostenabzug mit 1-%-Regelung oder "
            "Fahrtenbuch). Das hier gerechnete Nutzungseinlage-Modell passt dann nicht "
            "mehr - vor der Jahresabrechnung mit dem Steuerberater klaeren."
        )
    elif betriebsanteil > 0.40:
        w.append(
            f"Betrieblicher Nutzungsanteil {prozent(betriebsanteil)} naehert sich der "
            "50-%-Grenze. Fahrleistung im Blick behalten."
        )
    if betriebsanteil < 0.05 and betriebsanteil > 0:
        w.append(
            f"Nur {prozent(betriebsanteil)} betriebliche Nutzung. Der Aufwand fuer den "
            "Einzelnachweis lohnt sich haeufig nicht - die 0,30-EUR-Pauschale ohne "
            "Gesamtkostennachweis ist dann der einfachere Weg."
        )
    if differenz_km > 0:
        anteil = differenz_km / gesamt_km
        w.append(
            f"{zahl(differenz_km)} km ({prozent(anteil)}) sind im Fahrtenbuch nicht erfasst und "
            "wurden als Privatfahrten gewertet. Bei einem Einzelnachweis erwartet das "
            "Finanzamt eine lueckenlose Erfassung - Luecken schliessen."
        )
    elif differenz_km < 0:
        w.append(
            f"Das Fahrtenbuch weist {zahl(abs(differenz_km))} km MEHR aus als die "
            "Kilometerstaende hergeben. Kilometerstaende und Eintraege abgleichen."
        )
    if sonderzahlung > 0 and laufzeit > 0:
        w.append(
            "Die Leasingsonderzahlung wird periodengerecht auf die Vertragslaufzeit "
            "verteilt (BFH VIII R 1/21 vom 12.03.2024, VI R 9/22 vom 21.11.2024) - "
            "nicht im Zahlungsjahr voll angesetzt."
        )
    return w


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------

BREITE = 72


def zeile(links, rechts, breite=BREITE):
    """Zweispaltig mit Punktfuellung - bricht bei langen Labels nicht um."""
    fuell = breite - len(links) - len(rechts)
    if fuell < 2:
        return f"{links}\n{rechts:>{breite}}"
    return f"{links} {'.' * (fuell - 2)} {rechts}"


def ausgabe_text(e, profil, maengel):
    fz = profil.get("fahrzeug", {})
    k, f, s, a = e["kosten"], e["fahrleistung"], e["kilometersatz"], e["abzug"]

    print("=" * BREITE)
    print(f"KILOMETERKOSTEN-ABRECHNUNG {e['jahr']}")
    bez = fz.get("bezeichnung", "Fahrzeug")
    kz = fz.get("kennzeichen", "")
    print(f"{bez}{'  |  ' + kz if kz else ''}")
    print("=" * BREITE)

    print("\n1. FAHRZEUG-GESAMTKOSTEN")
    print("-" * BREITE)
    print(zeile(f"  Leasingraten ({k['vertragsmonate_im_jahr']} Monate)",
                f"{eur(k['leasingraten'])} EUR"))
    if k["leasingsonderzahlung_anteil"]:
        print(zeile("  Leasingsonderzahlung (Jahresanteil)",
                    f"{eur(k['leasingsonderzahlung_anteil'])} EUR"))
    print(zeile("  Fixkosten (Versicherung, Steuer, Stellplatz)",
                f"{eur(k['fixkosten'])} EUR"))
    print(zeile("  Variable Kosten (Kraftstoff, Wartung, Reifen)",
                f"{eur(k['variable_kosten'])} EUR"))
    print("-" * BREITE)
    print(zeile("  GESAMTKOSTEN", f"{eur(k['gesamtkosten'])} EUR"))

    print("\n2. FAHRLEISTUNG")
    print("-" * BREITE)
    print(zeile("  Gesamtfahrleistung", f"{zahl(f['gesamt_km'])} km"))
    print(f"     Quelle: {f['quelle']}")
    print(zeile("  davon Dienstreisen (Auswaertstaetigkeit)", f"{zahl(f['dienstreise_km'])} km"))
    print(zeile("  davon Wohnung <-> Betriebsstaette", f"{zahl(f['betriebsstaette_km'])} km"))
    print(zeile("  davon privat", f"{zahl(f['privat_km'])} km"))
    print(zeile("  betrieblicher Nutzungsanteil", prozent(f['betriebsanteil'])))

    print("\n3. KILOMETERSATZ")
    print("-" * BREITE)
    print(zeile("  Individueller Satz (Gesamtkosten / Gesamt-km)",
                f"{eur(s['individuell'], 4)} EUR/km"))
    print(zeile("  Pauschale Dienstreise", f"{eur(s['pauschale_dienstreise'], 2)} EUR/km"))
    print(zeile("  guenstiger", s["guenstigere_methode"].upper()))

    print("\n4. BETRIEBSAUSGABENABZUG")
    print("-" * BREITE)
    print(zeile(f"  Dienstreisen individuell ({zahl(f['dienstreise_km'])} km x "
                f"{eur(s['individuell'], 4)})", f"{eur(a['dienstreise_individuell'])} EUR"))
    print(zeile(f"  Dienstreisen pauschal ({zahl(f['dienstreise_km'])} km x "
                f"{eur(s['pauschale_dienstreise'], 2)})", f"{eur(a['dienstreise_pauschal'])} EUR"))
    print(zeile("  -> angesetzt", f"{eur(a['dienstreise_angesetzt'])} EUR"))
    if f["betriebsstaette_km"]:
        print()
        print(zeile("  Betriebsstaette: Entfernungspauschale",
                    f"{eur(a['betriebsstaette_entfernungspauschale'])} EUR"))
        print(f"     Basis: {a['betriebsstaette_basis']}")
        print(zeile("     (tatsaechliche Kosten dieser Fahrten)",
                    f"{eur(a['betriebsstaette_tatsaechliche_kosten'])} EUR"))
        print("     Nur die Entfernungspauschale ist abziehbar (§ 4 Abs. 5 Nr. 6 EStG).")
    print("-" * BREITE)
    print(zeile("  ABZIEHBAR GESAMT", f"{eur(a['gesamt'])} EUR"))
    print(zeile("  entspricht monatlich", f"{eur(e['monatlich']['abzug_je_monat'])} EUR"))

    if "monatsabrechnung" in e:
        m = e["monatsabrechnung"]
        print(f"\n5. MONATSABRECHNUNG {m['monat']}")
        print("-" * BREITE)
        print(zeile("  Fahrten im Monat", f"{m['fahrten']}"))
        print(zeile("  Dienstreise-Kilometer", f"{zahl(m['dienstreise_km'])} km"))
        print(zeile(f"  Satz ({m['methode']})", f"{eur(m['angewandter_satz'], 4)} EUR/km"))
        print(zeile("  BETRAG EIGENBELEG", f"{eur(m['betrag_dienstreisen'])} EUR"))
        print(f"  {m['hinweis']}")

    if maengel:
        print(f"\nFAHRTENBUCH-PRUEFUNG: {len(maengel)} Beanstandung(en)")
        print("-" * BREITE)
        for m in maengel[:20]:
            print(f"  - {m}")
        if len(maengel) > 20:
            print(f"  ... und {len(maengel) - 20} weitere")

    if e["warnungen"]:
        print("\nHINWEISE")
        print("-" * BREITE)
        for w in e["warnungen"]:
            print(f"  - {w}")

    print("\n" + "=" * BREITE)
    print("Planungswerkzeug, keine Steuerberatung. Werte vor Abgabe der")
    print("Steuererklaerung mit dem Steuerberater abstimmen.")
    print("=" * BREITE)


def ausgabe_eigenbeleg(e, profil):
    fz = profil.get("fahrzeug", {})
    unt = profil.get("unternehmen", {})
    m = e.get("monatsabrechnung")
    if m:
        zeitraum, betrag, km = m["monat"], m["betrag_dienstreisen"], m["dienstreise_km"]
        satz = m["angewandter_satz"]
        methode = m["methode"]
    else:
        zeitraum = str(e["jahr"])
        betrag = e["abzug"]["dienstreise_angesetzt"]
        km = e["fahrleistung"]["dienstreise_km"]
        satz = (e["kilometersatz"]["individuell"]
                if e["kilometersatz"]["guenstigere_methode"] == "individuell"
                else e["kilometersatz"]["pauschale_dienstreise"])
        methode = e["kilometersatz"]["guenstigere_methode"]

    heute = date.today().strftime("%d.%m.%Y")
    print("EIGENBELEG - NUTZUNGSEINLAGE FAHRZEUGKOSTEN")
    print("=" * BREITE)
    print(f"Betrieb:            {unt.get('name', '(Einzelunternehmen)')}")
    print(f"Inhaber:            {unt.get('inhaber', '(Name)')}")
    print(f"Abrechnungszeitraum: {zeitraum}")
    print(f"Belegdatum:         {heute}")
    print()
    print(f"Fahrzeug:           {fz.get('bezeichnung', '(Fahrzeug)')}")
    print(f"Kennzeichen:        {fz.get('kennzeichen', '(Kennzeichen)')}")
    print(f"Halter / Leasingnehmer: {unt.get('inhaber', '(Name)')} (privat)")
    print()
    print(f"Betrieblich gefahrene Kilometer:  {zahl(km)} km")
    print(f"Angesetzter Kilometersatz:        {eur(satz, 4)} EUR/km ({methode})")
    print(f"BETRAG:                           {eur(betrag)} EUR")
    print()
    print("Rechtsgrundlage: Nutzungseinlage der auf betriebliche Fahrten")
    print("entfallenden Aufwendungen eines privat geleasten Fahrzeugs")
    print("(§ 4 Abs. 4 EStG). Kein Leistungsaustausch, daher keine")
    print("Umsatzsteuer und kein gesonderter Vorsteuerausweis.")
    print()
    print("Anlagen: Fahrtenbuch des Zeitraums, Kostenaufstellung mit Belegen.")
    print()
    print("_" * 40)
    print("Ort, Datum, Unterschrift")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Kilometerkosten privat geleaster Fahrzeuge fuer die "
                    "Weiterbelastung an das Einzelunternehmen berechnen.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Beispiele:
  %(prog)s --profil fahrzeug.json --fahrtenbuch fahrten.csv
  %(prog)s --profil fahrzeug.json --fahrtenbuch fahrten.csv --monat 2026-03
  %(prog)s --profil fahrzeug.json --fahrtenbuch fahrten.csv --eigenbeleg
  %(prog)s --profil fahrzeug.json --fahrtenbuch fahrten.csv --format json
""",
    )
    parser.add_argument("--profil", required=True, help="Fahrzeugprofil (JSON)")
    parser.add_argument("--fahrtenbuch", required=True, help="Fahrtenbuch (CSV)")
    parser.add_argument("--jahr", type=int, help="Abrechnungsjahr (Standard: aus Profil)")
    parser.add_argument("--monat", help="Zusaetzliche Monatsabrechnung, Format JJJJ-MM")
    parser.add_argument("--eigenbeleg", action="store_true",
                        help="Eigenbeleg-Text statt Rechenbericht ausgeben")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strikt", action="store_true",
                        help="Exit-Code 2, wenn das Fahrtenbuch Beanstandungen hat")
    args = parser.parse_args()

    profil = lade_profil(args.profil)
    jahr = args.jahr or int(profil.get("steuer", {}).get("jahr", STANDARD_JAHR))
    if jahr not in PARAMETER:
        print(f"WARNUNG: Fuer {jahr} sind keine Parameter hinterlegt, "
              f"es gelten die Werte {STANDARD_JAHR}.", file=sys.stderr)

    fahrten = lade_fahrtenbuch(args.fahrtenbuch, jahr)
    maengel = pruefe_fahrtenbuch(fahrten)
    ergebnis = berechne(profil, fahrten, jahr, args.monat)
    ergebnis["fahrtenbuch_beanstandungen"] = maengel

    if args.format == "json":
        print(json.dumps(ergebnis, indent=2, ensure_ascii=False))
    elif args.eigenbeleg:
        ausgabe_eigenbeleg(ergebnis, profil)
    else:
        ausgabe_text(ergebnis, profil, maengel)

    if args.strikt and maengel:
        sys.exit(2)


if __name__ == "__main__":
    main()
