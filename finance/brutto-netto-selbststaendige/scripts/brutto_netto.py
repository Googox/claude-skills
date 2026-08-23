#!/usr/bin/env python3
"""
Brutto-Netto-Rechner fuer Selbststaendige (Deutschland).

Rechnet vom Umsatz bis zum tatsaechlich verfuegbaren Netto und beruecksichtigt
dabei vollstaendig:

  A) ALLE DIREKTEN STEUERN
     - Einkommensteuer (Grundtarif §32a EStG)
     - Solidaritaetszuschlag (Freigrenze + Milderungszone)
     - Kirchensteuer (8 % / 9 %, optional)
     - Gewerbesteuer (Freibetrag 24.500 EUR, Messzahl 3,5 %, Hebesatz frei)
       inkl. Anrechnung nach §35 EStG
     (Umsatzsteuer ist eine indirekte Steuer und wird als Durchlaufposten
      separat ausgewiesen — sie mindert das Netto nicht.)

  B) ALLE PFLICHTBEITRAEGE ZUR SOZIALVERSICHERUNG
     - Krankenversicherung (GKV freiwillig mit/ohne Krankengeld, oder PKV)
     - Pflegeversicherung (inkl. Kinderlosenzuschlag und Kinderabschlaegen)
     - Rentenversicherung (Pflicht §2 SGB VI: Regelbeitrag / halber
       Regelbeitrag / einkommensgerecht; freiwillig; Versorgungswerk; Ruerup)

  C) FREIWILLIGE ARBEITSLOSENVERSICHERUNG (§28a SGB III)
     - Beitrag = 2,6 % der Bezugsgroesse, Gruenderermaessigung 50 %
     - Schaetzung des ALG-I-Anspruchs (fiktive Bemessung §152 SGB III)

Die steuerliche Wechselwirkung ist abgebildet: Altersvorsorge- und
Basiskranken-/Pflegebeitraege mindern als Sonderausgaben das zu versteuernde
Einkommen (§10 EStG, inkl. 4-%-Kuerzung bei Krankengeldanspruch und
Guenstigerpruefung fuer sonstige Vorsorgeaufwendungen).

WICHTIG: Planungswerkzeug, KEINE Steuer- oder Rechtsberatung. Rechengroessen
jaehrlich pruefen (BMF-Steuerrechner, Sozialversicherungs-Rechengroessen-
verordnung, Agentur fuer Arbeit).

Verwendung:
  python3 brutto_netto.py --umsatz 12500 --ausgaben 2800
  python3 brutto_netto.py --umsatz 150000 --ausgaben 33600 --jahreswerte --alv
  python3 brutto_netto.py --umsatz 12500 --kv privat --pkv-monat 780 --kinder 2
  python3 brutto_netto.py --umsatz 9000 --freiberuflich --rv regelbeitrag
  python3 brutto_netto.py --tabelle 6000:16000:2000 --kostenquote 0.25
  python3 brutto_netto.py --umsatz 12500 --ausgaben 2800 --format json

Nur Python-Standardbibliothek, Python 3.8+.
"""

import argparse
import json
import math
import sys

# ---------------------------------------------------------------------------
# Rechengroessen (jaehrlich pruefen und pflegen!)
#
# Quellen:
#   - Sozialversicherungsrechengroessen-Verordnung 2026 (BGBl. 26.11.2025)
#   - Beitragssatzverordnung / GKV-Spitzenverband (Zusatzbeitrag)
#   - Steuerfortentwicklungsgesetz (Tarifeckwerte 2026)
# ---------------------------------------------------------------------------

RECHENGROESSEN = {
    2025: {
        "bezugsgroesse_monat": 3745.00,       # bundeseinheitlich seit 2025
        "bbg_kv_monat": 5512.50,              # 66.150 EUR/Jahr
        "bbg_rv_monat": 8050.00,              # 96.600 EUR/Jahr (auch ALV)
        "jaeg_jahr": 73800.00,                # Versicherungspflichtgrenze GKV
        "kv_mindestbemessung_monat": 1248.33,  # 1/3 der Bezugsgroesse
        "rv_mindestbemessung_monat": 556.00,   # Geringfuegigkeitsgrenze
        "kv_satz_allgemein": 0.146,           # mit Krankengeldanspruch
        "kv_satz_ermaessigt": 0.140,          # ohne Krankengeld
        "zusatzbeitrag_durchschnitt": 0.025,
        "pv_satz_basis": 0.036,               # ab 1 Kind
        "pv_zuschlag_kinderlos": 0.006,       # ab 23 Jahre, kinderlos
        "pv_abschlag_je_kind": 0.0025,        # 2. bis 5. Kind (unter 25 J.)
        "rv_satz": 0.186,
        "alv_satz": 0.026,
        "altersvorsorge_hoechstbetrag": 29344.00,   # 118.800 x 24,7 %
        "sonstige_vorsorge_hoechstbetrag": 2800.00,  # Selbststaendige
        "tarif_eckwerte": [12096, 17443, 68480, 277825],
        "soli_freigrenze": 19950.00,
    },
    2026: {
        "bezugsgroesse_monat": 3955.00,       # 47.460 EUR/Jahr
        "bbg_kv_monat": 5812.50,              # 69.750 EUR/Jahr
        "bbg_rv_monat": 8450.00,              # 101.400 EUR/Jahr (auch ALV)
        "jaeg_jahr": 77400.00,
        "kv_mindestbemessung_monat": 1318.33,  # 1/3 der Bezugsgroesse
        "rv_mindestbemessung_monat": 603.00,
        "kv_satz_allgemein": 0.146,
        "kv_satz_ermaessigt": 0.140,
        "zusatzbeitrag_durchschnitt": 0.029,
        "pv_satz_basis": 0.036,
        "pv_zuschlag_kinderlos": 0.006,
        "pv_abschlag_je_kind": 0.0025,
        "rv_satz": 0.186,
        "alv_satz": 0.026,
        "altersvorsorge_hoechstbetrag": 30826.00,   # 124.800 x 24,7 %
        "sonstige_vorsorge_hoechstbetrag": 2800.00,
        "tarif_eckwerte": [12348, 17799, 69878, 277825],
        "soli_freigrenze": 20350.00,
    },
}

SOLI_SATZ = 0.055
SOLI_MILDERUNG = 0.119          # max. 11,9 % des die Freigrenze uebersteigenden Betrags
GEWST_FREIBETRAG = 24500.0      # Einzelunternehmer / Personengesellschaft
GEWST_MESSZAHL = 0.035
GEWST_ANRECHNUNG_FAKTOR = 4.0   # §35 EStG
UST_REGELSATZ = 0.19
SONDERAUSGABEN_PAUSCHBETRAG = 36.0
KV_KUERZUNG_KRANKENGELD = 0.04  # §10 Abs. 1 Nr. 3a EStG: 4 % Abschlag
DEFAULT_HEBESATZ = 320.0        # Wiggensbach (Landkreis Oberallgaeu)

# Fiktive Bemessung §152 Abs. 2 SGB III: Bruchteil der JAHRES-Bezugsgroesse
# je Kalendertag, nach Qualifikationsgruppe.
QUALIFIKATIONSGRUPPEN = {
    1: (300, "Hochschul-/Fachhochschulabschluss"),
    2: (360, "Meister, Techniker, Fachschulabschluss"),
    3: (450, "abgeschlossene Berufsausbildung"),
    4: (600, "ohne Berufsausbildung"),
}
ALG_SATZ_OHNE_KIND = 0.60
ALG_SATZ_MIT_KIND = 0.67
ALG_SV_PAUSCHALE = 0.20         # §153 Abs. 1 SGB III
ARBEITNEHMER_PAUSCHBETRAG = 1230.0


# ---------------------------------------------------------------------------
# Steuerfunktionen
# ---------------------------------------------------------------------------

def einkommensteuer(zve, jahr):
    """Tarifliche Einkommensteuer nach §32a EStG (Grundtarif, Einzelveranlagung).

    Die Polynom-Koeffizienten werden aus den Eckwerten und den gesetzlichen
    Grenzsteuersaetzen (14 % / 23,97 % / 42 % / 45 %) abgeleitet.
    """
    werte = _rechengroessen(jahr)
    e0, e1, e2, e3 = werte["tarif_eckwerte"]
    zve = math.floor(max(0.0, zve))  # auf vollen Euro abrunden

    if zve <= e0:
        return 0.0

    if zve <= e1:
        y = (zve - e0) / 10000.0
        y_end = (e1 - e0) / 10000.0
        a = 997.0 / (2 * y_end)
        tax = (a * y + 1400) * y
    elif zve <= e2:
        z = (zve - e1) / 10000.0
        z_end = (e2 - e1) / 10000.0
        b = 1803.0 / (2 * z_end)
        c1 = 1898.5 * ((e1 - e0) / 10000.0)
        tax = (b * z + 2397) * z + c1
    else:
        z_end = (e2 - e1) / 10000.0
        c1 = 1898.5 * ((e1 - e0) / 10000.0)
        tax_e2 = (1803.0 / (2 * z_end) * z_end + 2397) * z_end + c1
        d42 = 0.42 * e2 - tax_e2
        if zve <= e3:
            tax = 0.42 * zve - d42
        else:
            tax_e3 = 0.42 * e3 - d42
            d45 = 0.45 * e3 - tax_e3
            tax = 0.45 * zve - d45

    return float(math.floor(tax))


def gewerbesteuer(gewinn, hebesatz):
    """Gewerbesteuer eines Einzelunternehmers (ohne Hinzurechnungen/Kuerzungen).

    Rueckgabe: (gewerbesteuer, steuermessbetrag)
    """
    gewerbeertrag = math.floor(max(0.0, gewinn) / 100) * 100  # auf volle 100 ab
    bemessung = max(0.0, gewerbeertrag - GEWST_FREIBETRAG)
    messbetrag = bemessung * GEWST_MESSZAHL
    return round(messbetrag * hebesatz / 100.0, 2), round(messbetrag, 2)


def solidaritaetszuschlag(est, jahr):
    """Soli auf die festzusetzende ESt, mit Freigrenze und Milderungszone."""
    freigrenze = _rechengroessen(jahr)["soli_freigrenze"]
    if est <= freigrenze:
        return 0.0
    return round(min(SOLI_SATZ * est, SOLI_MILDERUNG * (est - freigrenze)), 2)


def _rechengroessen(jahr):
    if jahr not in RECHENGROESSEN:
        raise ValueError(
            "Keine Rechengroessen fuer %s hinterlegt. Verfuegbar: %s"
            % (jahr, sorted(RECHENGROESSEN))
        )
    return RECHENGROESSEN[jahr]


# ---------------------------------------------------------------------------
# Sozialversicherung
# ---------------------------------------------------------------------------

def pflegeversicherung_satz(jahr, kinder, kinderlos_ab_23=True):
    """Beitragssatz Pflegeversicherung fuer Selbststaendige (voller Satz).

    Selbststaendige tragen den Beitrag allein; der saechsische Sonderweg
    (hoeherer Arbeitnehmeranteil) wirkt sich deshalb nicht aus.
    """
    w = _rechengroessen(jahr)
    if kinder <= 0:
        # Kinderlosenzuschlag entfaellt vor dem 23. Geburtstag.
        return w["pv_satz_basis"] + (
            w["pv_zuschlag_kinderlos"] if kinderlos_ab_23 else 0.0
        )
    # Abschlag fuer das 2. bis 5. Kind, solange die Kinder unter 25 sind.
    abschlagskinder = min(max(kinder - 1, 0), 4)
    return w["pv_satz_basis"] - abschlagskinder * w["pv_abschlag_je_kind"]


def krankenversicherung(gewinn_jahr, jahr, modus="gesetzlich",
                        zusatzbeitrag=None, krankengeld=True,
                        pkv_monat=0.0, pkv_basis_anteil=0.80,
                        kinder=0, kinderlos_ab_23=True):
    """Kranken- und Pflegeversicherung fuer Selbststaendige (Jahresbetraege).

    GKV (freiwillig versichert): Bemessungsgrundlage ist das Arbeitseinkommen
    (= steuerlicher Gewinn), begrenzt durch Beitragsbemessungsgrenze und
    Mindestbemessungsgrundlage.

    PKV: Beitrag ist gesetzt; `pkv_basis_anteil` beziffert den steuerlich
    abziehbaren Basisanteil (Standard 80 %, exakter Wert steht auf der
    Beitragsbescheinigung des Versicherers).
    """
    w = _rechengroessen(jahr)
    pv_satz = pflegeversicherung_satz(jahr, kinder, kinderlos_ab_23)

    if modus == "privat":
        kv_jahr = round(pkv_monat * 12.0, 2)
        # Bei PKV ist die Pflegepflichtversicherung im genannten Beitrag
        # enthalten; sie wird nicht zusaetzlich berechnet.
        return {
            "modus": "privat",
            "bemessungsgrundlage_monat": None,
            "kv_satz_gesamt": None,
            "pv_satz": None,
            "kv_jahr": kv_jahr,
            "pv_jahr": 0.0,
            "kv_pv_jahr": kv_jahr,
            "kv_pv_monat": round(kv_jahr / 12.0, 2),
            "abziehbar_basis_jahr": round(kv_jahr * pkv_basis_anteil, 2),
        }

    if zusatzbeitrag is None:
        zusatzbeitrag = w["zusatzbeitrag_durchschnitt"]
    kv_satz = w["kv_satz_allgemein"] if krankengeld else w["kv_satz_ermaessigt"]
    kv_satz_gesamt = kv_satz + zusatzbeitrag

    basis_monat = min(
        max(gewinn_jahr / 12.0, w["kv_mindestbemessung_monat"]),
        w["bbg_kv_monat"],
    )
    kv_jahr = round(basis_monat * 12.0 * kv_satz_gesamt, 2)
    pv_jahr = round(basis_monat * 12.0 * pv_satz, 2)

    # §10 Abs. 1 Nr. 3 EStG: Basisabsicherung. Der KV-Beitrag wird um 4 %
    # gekuerzt, wenn Anspruch auf Krankengeld besteht; die PV ist voll
    # abziehbar. Der Zusatzbeitrag gehoert zur Basisabsicherung.
    kuerzung = KV_KUERZUNG_KRANKENGELD if krankengeld else 0.0
    abziehbar = round(kv_jahr * (1 - kuerzung) + pv_jahr, 2)

    return {
        "modus": "gesetzlich",
        "bemessungsgrundlage_monat": round(basis_monat, 2),
        "kv_satz_gesamt": round(kv_satz_gesamt, 5),
        "pv_satz": round(pv_satz, 5),
        "kv_jahr": kv_jahr,
        "pv_jahr": pv_jahr,
        "kv_pv_jahr": round(kv_jahr + pv_jahr, 2),
        "kv_pv_monat": round((kv_jahr + pv_jahr) / 12.0, 2),
        "abziehbar_basis_jahr": abziehbar,
    }


def rentenversicherung(gewinn_jahr, jahr, modus="keine", betrag_monat=0.0):
    """Altersvorsorge-Pflichtbeitraege bzw. freiwillige Beitraege (Jahreswerte).

    Modi:
      keine            - keine gesetzliche Altersvorsorge (nur bei echter
                         Versicherungsfreiheit zulaessig!)
      regelbeitrag     - Pflichtversicherung §2 SGB VI, Regelbeitrag
                         (Bezugsgroesse x Beitragssatz)
      halber-regelbeitrag - Existenzgruender in den ersten 3 Kalenderjahren
      einkommensgerecht   - Pflichtbeitrag auf das nachgewiesene
                         Arbeitseinkommen (Mindest-/Hoechstgrenze)
      freiwillig       - freiwillige Beitraege in frei gewaehlter Hoehe
      versorgungswerk  - berufsstaendisches Versorgungswerk (Betrag gesetzt)
      ruerup           - Basisrente (Betrag gesetzt)
    """
    w = _rechengroessen(jahr)
    satz = w["rv_satz"]
    regelbeitrag_monat = round(w["bezugsgroesse_monat"] * satz, 2)
    min_monat = round(w["rv_mindestbemessung_monat"] * satz, 2)
    max_monat = round(w["bbg_rv_monat"] * satz, 2)

    if modus == "keine":
        beitrag_monat = 0.0
    elif modus == "regelbeitrag":
        beitrag_monat = regelbeitrag_monat
    elif modus == "halber-regelbeitrag":
        beitrag_monat = round(regelbeitrag_monat / 2.0, 2)
    elif modus == "einkommensgerecht":
        basis = min(
            max(gewinn_jahr / 12.0, w["rv_mindestbemessung_monat"]),
            w["bbg_rv_monat"],
        )
        beitrag_monat = round(basis * satz, 2)
    elif modus in ("freiwillig", "versorgungswerk", "ruerup"):
        beitrag_monat = round(betrag_monat, 2)
        if modus == "freiwillig":
            # Gesetzliche RV: Beitrag nur zwischen Mindest- und Hoechstbeitrag.
            beitrag_monat = min(max(beitrag_monat, min_monat), max_monat) \
                if beitrag_monat > 0 else 0.0
    else:
        raise ValueError("Unbekannter RV-Modus: %s" % modus)

    return {
        "modus": modus,
        "beitrag_monat": round(beitrag_monat, 2),
        "beitrag_jahr": round(beitrag_monat * 12.0, 2),
        "regelbeitrag_monat": regelbeitrag_monat,
        "mindestbeitrag_monat": min_monat,
        "hoechstbeitrag_monat": max_monat,
    }


def arbeitslosenversicherung(jahr, aktiv=False, gruenderermaessigung=False):
    """Freiwillige Weiterversicherung §28a SGB III (Antragspflichtversicherung).

    Beitrag = Beitragssatz zur Arbeitslosenversicherung x Bezugsgroesse.
    In dem Kalenderjahr der Existenzgruendung und im folgenden Kalenderjahr
    wird nur der halbe Beitrag erhoben (§345b i. V. m. §434w SGB III).
    """
    w = _rechengroessen(jahr)
    voll = round(w["bezugsgroesse_monat"] * w["alv_satz"], 2)
    if not aktiv:
        beitrag = 0.0
    else:
        beitrag = round(voll / 2.0, 2) if gruenderermaessigung else voll
    return {
        "aktiv": aktiv,
        "gruenderermaessigung": gruenderermaessigung,
        "beitrag_monat": beitrag,
        "beitrag_jahr": round(beitrag * 12.0, 2),
        "voller_beitrag_monat": voll,
        "bemessung_monat": w["bezugsgroesse_monat"],
        "satz": w["alv_satz"],
    }


def alg_anspruch_schaetzung(jahr, qualifikationsgruppe=1, mit_kind=False,
                            kirchensteuer_satz=0.0):
    """Schaetzung des ALG-I-Anspruchs nach fiktiver Bemessung (§152 SGB III).

    Rechenweg: fiktives Bemessungsentgelt je Kalendertag -> Leistungsentgelt
    (abzueglich 20 % Sozialversicherungspauschale und pauschaler Lohnsteuer,
    Steuerklasse I) -> 60 % (ohne Kind) bzw. 67 % (mit Kind).

    Die Lohnsteuer wird ueber den Einkommensteuertarif inkl. Vorsorgepauschale
    angenaehert; die Agentur fuer Arbeit rechnet mit der amtlichen
    Lohnsteuertabelle. Abweichung typischerweise unter 5 %.
    """
    w = _rechengroessen(jahr)
    if qualifikationsgruppe not in QUALIFIKATIONSGRUPPEN:
        raise ValueError("Qualifikationsgruppe muss 1-4 sein.")
    nenner, bezeichnung = QUALIFIKATIONSGRUPPEN[qualifikationsgruppe]

    bezugsgroesse_jahr = w["bezugsgroesse_monat"] * 12.0
    entgelt_tag = round(bezugsgroesse_jahr / nenner, 2)
    entgelt_jahr = entgelt_tag * 365.0

    # Vorsorgepauschale (Steuerklasse I, vereinfacht): Arbeitnehmeranteil RV
    # plus Arbeitnehmeranteil KV/PV, jeweils bis zur Beitragsbemessungsgrenze.
    rv_anteil = min(entgelt_jahr, w["bbg_rv_monat"] * 12.0) * (w["rv_satz"] / 2.0)
    kv_pv_basis = min(entgelt_jahr, w["bbg_kv_monat"] * 12.0)
    kv_anteil = kv_pv_basis * (
        (w["kv_satz_ermaessigt"] + w["zusatzbeitrag_durchschnitt"]) / 2.0
    )
    pv_anteil = kv_pv_basis * (w["pv_satz_basis"] / 2.0)
    vorsorgepauschale = rv_anteil + kv_anteil + pv_anteil

    zve = max(
        0.0,
        entgelt_jahr
        - ARBEITNEHMER_PAUSCHBETRAG
        - SONDERAUSGABEN_PAUSCHBETRAG
        - vorsorgepauschale,
    )
    lohnsteuer_jahr = einkommensteuer(zve, jahr)
    soli_jahr = solidaritaetszuschlag(lohnsteuer_jahr, jahr)
    kist_jahr = lohnsteuer_jahr * kirchensteuer_satz
    steuer_tag = (lohnsteuer_jahr + soli_jahr + kist_jahr) / 365.0

    leistungsentgelt_tag = max(
        0.0, entgelt_tag * (1 - ALG_SV_PAUSCHALE) - steuer_tag
    )
    satz = ALG_SATZ_MIT_KIND if mit_kind else ALG_SATZ_OHNE_KIND
    alg_tag = leistungsentgelt_tag * satz

    return {
        "qualifikationsgruppe": qualifikationsgruppe,
        "bezeichnung": bezeichnung,
        "bemessungsentgelt_tag": entgelt_tag,
        "bemessungsentgelt_monat": round(entgelt_tag * 30.0, 2),
        "leistungsentgelt_tag": round(leistungsentgelt_tag, 2),
        "leistungssatz": satz,
        "alg_tag": round(alg_tag, 2),
        "alg_monat": round(alg_tag * 30.0, 2),
    }


# ---------------------------------------------------------------------------
# Vorsorgeaufwendungen (§10 EStG)
# ---------------------------------------------------------------------------

def vorsorgeabzug(jahr, altersvorsorge_jahr, basis_kv_pv_jahr,
                  sonstige_vorsorge_jahr):
    """Abziehbare Vorsorgeaufwendungen als Sonderausgaben.

    - Altersvorsorge (§10 Abs. 1 Nr. 2 EStG): seit 2023 zu 100 % abziehbar,
      gedeckelt auf den Hoechstbetrag (Hoechstbeitrag knappschaftliche RV).
    - Basiskranken- und Pflegeversicherung (Nr. 3): unbegrenzt abziehbar.
    - Sonstige Vorsorgeaufwendungen (Nr. 3a) — darunter die freiwillige
      Arbeitslosenversicherung, Berufsunfaehigkeits-, Unfall- und
      Haftpflichtversicherung: nur im Rahmen des Hoechstbetrags von 2.800 EUR
      und nur, soweit dieser nicht bereits durch die Basisabsicherung
      ausgeschoepft ist (Guenstigerpruefung §10 Abs. 4 Satz 4 EStG).
    """
    w = _rechengroessen(jahr)
    alter_abziehbar = min(altersvorsorge_jahr, w["altersvorsorge_hoechstbetrag"])

    hoechst_sonstige = w["sonstige_vorsorge_hoechstbetrag"]
    # Mindestens die Basisabsicherung ist immer abziehbar.
    sonstige_abziehbar = max(
        basis_kv_pv_jahr,
        min(hoechst_sonstige, basis_kv_pv_jahr + sonstige_vorsorge_jahr),
    )
    # Steuerlich wirksamer Anteil der "sonstigen" Beitraege (i. d. R. 0 EUR,
    # sobald die Basisabsicherung ueber 2.800 EUR liegt).
    davon_sonstige_wirksam = round(
        max(0.0, sonstige_abziehbar - basis_kv_pv_jahr), 2
    )

    return {
        "altersvorsorge_gezahlt": round(altersvorsorge_jahr, 2),
        "altersvorsorge_abziehbar": round(alter_abziehbar, 2),
        "altersvorsorge_hoechstbetrag": w["altersvorsorge_hoechstbetrag"],
        "basis_kv_pv_abziehbar": round(basis_kv_pv_jahr, 2),
        "sonstige_gezahlt": round(sonstige_vorsorge_jahr, 2),
        "sonstige_steuerlich_wirksam": davon_sonstige_wirksam,
        "summe_abziehbar": round(alter_abziehbar + sonstige_abziehbar, 2),
    }


# ---------------------------------------------------------------------------
# Gesamtrechnung
# ---------------------------------------------------------------------------

def berechne(umsatz_jahr, ausgaben_jahr, jahr=2026, gewerblich=True,
             hebesatz=DEFAULT_HEBESATZ, kirchensteuer_satz=0.0,
             vorsteuer_jahr=None, kleinunternehmer=False,
             kv_modus="gesetzlich", zusatzbeitrag=None, krankengeld=True,
             pkv_monat=0.0, pkv_basis_anteil=0.80,
             kinder=0, kinderlos_ab_23=True,
             rv_modus="keine", rv_betrag_monat=0.0,
             alv=False, alv_gruender=False,
             weitere_vorsorge_monat=0.0,
             qualifikationsgruppe=1, alg_mit_kind=False,
             mit_grenzbelastung=True):
    """Vollstaendige Jahresrechnung vom Umsatz bis zum Netto."""
    gewinn = umsatz_jahr - ausgaben_jahr

    # --- Umsatzsteuer: Durchlaufposten, mindert das Netto NICHT ---
    if kleinunternehmer:
        ust, vorsteuer, ust_zahllast = 0.0, 0.0, 0.0
    else:
        ust = round(umsatz_jahr * UST_REGELSATZ, 2)
        if vorsteuer_jahr is None:
            vorsteuer = round(ausgaben_jahr * UST_REGELSATZ, 2)
        else:
            vorsteuer = round(vorsteuer_jahr, 2)
        ust_zahllast = round(ust - vorsteuer, 2)

    # --- Sozialversicherung ---
    kv = krankenversicherung(
        gewinn, jahr, modus=kv_modus, zusatzbeitrag=zusatzbeitrag,
        krankengeld=krankengeld, pkv_monat=pkv_monat,
        pkv_basis_anteil=pkv_basis_anteil, kinder=kinder,
        kinderlos_ab_23=kinderlos_ab_23,
    )
    rv = rentenversicherung(gewinn, jahr, modus=rv_modus,
                            betrag_monat=rv_betrag_monat)
    av = arbeitslosenversicherung(jahr, aktiv=alv,
                                  gruenderermaessigung=alv_gruender)

    weitere_vorsorge_jahr = round(weitere_vorsorge_monat * 12.0, 2)
    sozialabgaben_jahr = round(
        kv["kv_pv_jahr"] + rv["beitrag_jahr"] + av["beitrag_jahr"], 2
    )

    # --- Vorsorgeaufwendungen (Sonderausgaben) ---
    vs = vorsorgeabzug(
        jahr,
        altersvorsorge_jahr=rv["beitrag_jahr"],
        basis_kv_pv_jahr=kv["abziehbar_basis_jahr"],
        sonstige_vorsorge_jahr=av["beitrag_jahr"] + weitere_vorsorge_jahr,
    )

    # --- Gewerbesteuer ---
    if gewerblich:
        gewst, messbetrag = gewerbesteuer(gewinn, hebesatz)
    else:
        gewst, messbetrag = 0.0, 0.0

    # --- Einkommensteuer + Annexsteuern ---
    zve = max(0.0, gewinn - vs["summe_abziehbar"] - SONDERAUSGABEN_PAUSCHBETRAG)
    est_tariflich = einkommensteuer(zve, jahr)
    anrechnung = round(
        min(GEWST_ANRECHNUNG_FAKTOR * messbetrag, gewst, est_tariflich), 2
    )
    est = round(est_tariflich - anrechnung, 2)
    soli = solidaritaetszuschlag(est, jahr)
    # Die Kirchensteuer ist selbst Sonderausgabe; das wird bewusst nicht
    # gegengerechnet -> das Ergebnis ist leicht konservativ.
    kist = round(est * kirchensteuer_satz, 2)

    steuern_jahr = round(gewst + est + soli + kist, 2)
    netto_jahr = round(gewinn - steuern_jahr - sozialabgaben_jahr, 2)

    # --- Grenzbelastung: was bleibt vom naechsten Euro Gewinn? ---
    grenz = _grenzbelastung(
        umsatz_jahr, ausgaben_jahr, jahr, gewerblich, hebesatz,
        kirchensteuer_satz, kv_modus, zusatzbeitrag, krankengeld, pkv_monat,
        pkv_basis_anteil, kinder, kinderlos_ab_23, rv_modus, rv_betrag_monat,
        alv, alv_gruender, weitere_vorsorge_monat, netto_jahr,
    ) if mit_grenzbelastung else None

    ergebnis = {
        "jahr": jahr,
        "eingaben": {
            "umsatz_jahr_netto": round(umsatz_jahr, 2),
            "betriebsausgaben_jahr_netto": round(ausgaben_jahr, 2),
            "gewerblich": gewerblich,
            "hebesatz_prozent": hebesatz if gewerblich else 0.0,
            "kirchensteuer_satz": kirchensteuer_satz,
            "kleinunternehmer": kleinunternehmer,
            "kinder": kinder,
        },
        "gewinn_jahr": round(gewinn, 2),
        "umsatzsteuer": {
            "umsatzsteuer": ust,
            "vorsteuer": vorsteuer,
            "zahllast_jahr": ust_zahllast,
            "zahllast_monat": round(ust_zahllast / 12.0, 2),
            "hinweis": "Durchlaufposten — mindert das Netto nicht.",
        },
        "sozialversicherung": {
            "krankenversicherung": kv,
            "rentenversicherung": rv,
            "arbeitslosenversicherung": av,
            "weitere_vorsorge_jahr": weitere_vorsorge_jahr,
            "summe_jahr": sozialabgaben_jahr,
            "summe_monat": round(sozialabgaben_jahr / 12.0, 2),
            "quote_vom_gewinn": (
                round(sozialabgaben_jahr / gewinn, 4) if gewinn > 0 else 0.0
            ),
        },
        "vorsorgeabzug": vs,
        "steuern": {
            "gewerbesteuer": {
                "steuermessbetrag": messbetrag,
                "gewerbesteuer_jahr": gewst,
                "anrechnung_p35": anrechnung,
                "definitivbelastung": round(gewst - anrechnung, 2),
            },
            "zu_versteuerndes_einkommen": round(zve, 2),
            "est_tariflich": est_tariflich,
            "est_festzusetzen": est,
            "solidaritaetszuschlag": soli,
            "kirchensteuer": kist,
            "summe_jahr": steuern_jahr,
            "summe_monat": round(steuern_jahr / 12.0, 2),
            "quote_vom_gewinn": (
                round(steuern_jahr / gewinn, 4) if gewinn > 0 else 0.0
            ),
        },
        "netto": {
            "netto_jahr": netto_jahr,
            "netto_monat": round(netto_jahr / 12.0, 2),
            "abgaben_jahr": round(steuern_jahr + sozialabgaben_jahr, 2),
            "abgabenquote_gewinn": (
                round((steuern_jahr + sozialabgaben_jahr) / gewinn, 4)
                if gewinn > 0 else 0.0
            ),
            "nettoquote_umsatz": (
                round(netto_jahr / umsatz_jahr, 4) if umsatz_jahr > 0 else 0.0
            ),
            "grenzbelastung": grenz,
        },
        "ruecklage_monatlich": {
            "umsatzsteuer": round(max(0.0, ust_zahllast) / 12.0, 2),
            "gewerbesteuer": round(gewst / 12.0, 2),
            "est_soli_kist": round((est + soli + kist) / 12.0, 2),
            "sozialversicherung": round(sozialabgaben_jahr / 12.0, 2),
            "summe": round(
                (max(0.0, ust_zahllast) + steuern_jahr + sozialabgaben_jahr)
                / 12.0, 2
            ),
        },
    }

    if alv:
        ergebnis["arbeitslosengeld_schaetzung"] = alg_anspruch_schaetzung(
            jahr, qualifikationsgruppe=qualifikationsgruppe,
            mit_kind=alg_mit_kind, kirchensteuer_satz=kirchensteuer_satz,
        )
        jahresbeitrag = av["beitrag_jahr"]
        alg_monat = ergebnis["arbeitslosengeld_schaetzung"]["alg_monat"]
        ergebnis["arbeitslosengeld_schaetzung"]["beitrag_jahr"] = jahresbeitrag
        ergebnis["arbeitslosengeld_schaetzung"]["break_even_monate"] = (
            round(jahresbeitrag / alg_monat, 2) if alg_monat > 0 else None
        )

    return ergebnis


def _grenzbelastung(umsatz_jahr, ausgaben_jahr, jahr, gewerblich, hebesatz,
                    kirchensteuer_satz, kv_modus, zusatzbeitrag, krankengeld,
                    pkv_monat, pkv_basis_anteil, kinder, kinderlos_ab_23,
                    rv_modus, rv_betrag_monat, alv, alv_gruender,
                    weitere_vorsorge_monat, netto_basis, delta=1000.0):
    """Numerische Grenzbelastung: Abgabenanteil an 1.000 EUR Mehrgewinn."""
    vergleich = berechne(
        umsatz_jahr + delta, ausgaben_jahr, jahr=jahr, gewerblich=gewerblich,
        hebesatz=hebesatz, kirchensteuer_satz=kirchensteuer_satz,
        kleinunternehmer=True,  # USt ist Durchlaufposten, hier irrelevant
        kv_modus=kv_modus, zusatzbeitrag=zusatzbeitrag, krankengeld=krankengeld,
        pkv_monat=pkv_monat, pkv_basis_anteil=pkv_basis_anteil, kinder=kinder,
        kinderlos_ab_23=kinderlos_ab_23, rv_modus=rv_modus,
        rv_betrag_monat=rv_betrag_monat, alv=alv, alv_gruender=alv_gruender,
        weitere_vorsorge_monat=weitere_vorsorge_monat,
        mit_grenzbelastung=False,
    )
    netto_plus = vergleich["netto"]["netto_jahr"]
    behalten = (netto_plus - netto_basis) / delta
    return {
        "mehrgewinn": delta,
        "davon_netto": round(netto_plus - netto_basis, 2),
        "netto_anteil": round(behalten, 4),
        "abgaben_anteil": round(1 - behalten, 4),
    }


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def _eur(x):
    """Deutsches Zahlenformat: 12.345,67 EUR"""
    s = "{:,.2f}".format(x).replace(",", "X").replace(".", ",").replace("X", ".")
    return s + " EUR"


def _pct(x):
    return ("%.1f %%" % (100 * x)).replace(".", ",")


def _zeile(label, betrag, breite=34):
    print("%-*s %18s" % (breite, label, _eur(betrag)))


def drucke_bericht(r):
    e = r["eingaben"]
    u = r["umsatzsteuer"]
    sv = r["sozialversicherung"]
    kv = sv["krankenversicherung"]
    rv = sv["rentenversicherung"]
    av = sv["arbeitslosenversicherung"]
    vs = r["vorsorgeabzug"]
    st = r["steuern"]
    n = r["netto"]
    rl = r["ruecklage_monatlich"]

    breite = 54
    print("=" * breite)
    print("BRUTTO-NETTO-RECHNER SELBSTSTAENDIGKEIT — Jahr %s" % r["jahr"])
    print("=" * breite)
    print("Rechtliche Einordnung:  %s"
          % ("Gewerbebetrieb (mit GewSt)" if e["gewerblich"]
             else "Freiberuflich (keine GewSt)"))
    _zeile("Umsatz netto (Jahr)", e["umsatz_jahr_netto"])
    _zeile("./. Betriebsausgaben", e["betriebsausgaben_jahr_netto"])
    _zeile("= GEWINN (EUeR) — dein Brutto", r["gewinn_jahr"])
    print()

    print("-" * breite)
    print("0) UMSATZSTEUER — Durchlaufposten, gehoert nie dir")
    print("-" * breite)
    if e["kleinunternehmer"]:
        print("   Kleinunternehmer §19 UStG: keine USt, keine Vorsteuer")
    else:
        _zeile("   Umsatzsteuer 19 %", u["umsatzsteuer"])
        _zeile("   ./. Vorsteuer", u["vorsteuer"])
        _zeile("   = Zahllast Jahr", u["zahllast_jahr"])
        _zeile("     davon je Monat", u["zahllast_monat"])
    print()

    print("-" * breite)
    print("1) PFLICHTBEITRAEGE SOZIALVERSICHERUNG")
    print("-" * breite)
    if kv["modus"] == "gesetzlich":
        print("   GKV freiwillig | Bemessung %s/Monat"
              % _eur(kv["bemessungsgrundlage_monat"]))
        _zeile("   Krankenversicherung (%s)" % _pct(kv["kv_satz_gesamt"]),
               kv["kv_jahr"])
        _zeile("   Pflegeversicherung (%s)" % _pct(kv["pv_satz"]), kv["pv_jahr"])
    else:
        print("   Private Krankenversicherung (Beitrag gesetzt)")
        _zeile("   KV + PV gesamt", kv["kv_pv_jahr"])
    if rv["beitrag_jahr"] > 0:
        _zeile("   Altersvorsorge (%s)" % rv["modus"], rv["beitrag_jahr"])
    else:
        print("   Altersvorsorge: keine Beitraege erfasst  <- pruefen!")
    if av["aktiv"]:
        _zeile("   Arbeitslosenvers. %s"
               % ("(halb, Gruender)" if av["gruenderermaessigung"]
                  else "(freiwillig)"),
               av["beitrag_jahr"])
    else:
        print("   Arbeitslosenversicherung: nicht abgeschlossen")
    if sv["weitere_vorsorge_jahr"]:
        _zeile("   Weitere Vorsorge (BU etc.)", sv["weitere_vorsorge_jahr"])
    _zeile("   SUMME SOZIALABGABEN (Jahr)", sv["summe_jahr"])
    _zeile("   je Monat", sv["summe_monat"])
    print("   Anteil am Gewinn: %s" % _pct(sv["quote_vom_gewinn"]))
    print()

    print("-" * breite)
    print("2) SONDERAUSGABENABZUG VORSORGE (§10 EStG)")
    print("-" * breite)
    _zeile("   Altersvorsorge abziehbar", vs["altersvorsorge_abziehbar"])
    _zeile("   Basis KV/PV abziehbar", vs["basis_kv_pv_abziehbar"])
    _zeile("   Sonstige (ALV, BU) wirksam", vs["sonstige_steuerlich_wirksam"])
    if vs["sonstige_gezahlt"] > 0 and vs["sonstige_steuerlich_wirksam"] == 0:
        print("   Hinweis: Hoechstbetrag 2.800 EUR bereits durch KV/PV")
        print("   ausgeschoepft — ALV/BU wirken steuerlich nicht mehr.")
    _zeile("   = Summe abziehbar", vs["summe_abziehbar"])
    print()

    print("-" * breite)
    print("3) DIREKTE STEUERN")
    print("-" * breite)
    if e["gewerblich"]:
        g = st["gewerbesteuer"]
        print("   Gewerbesteuer (Hebesatz %.0f %%, FB 24.500 EUR)"
              % e["hebesatz_prozent"])
        _zeile("   Gewerbesteuer", g["gewerbesteuer_jahr"])
        _zeile("   ./. Anrechnung §35 EStG", g["anrechnung_p35"])
        _zeile("   = Definitivbelastung GewSt", g["definitivbelastung"])
    _zeile("   zu versteuerndes Einkommen", st["zu_versteuerndes_einkommen"])
    _zeile("   Einkommensteuer (festzus.)", st["est_festzusetzen"])
    _zeile("   Solidaritaetszuschlag", st["solidaritaetszuschlag"])
    _zeile("   Kirchensteuer", st["kirchensteuer"])
    _zeile("   SUMME STEUERN (Jahr)", st["summe_jahr"])
    print("   Anteil am Gewinn: %s" % _pct(st["quote_vom_gewinn"]))
    print()

    print("=" * breite)
    print("4) BRUTTO -> NETTO")
    print("=" * breite)
    _zeile("Gewinn (brutto)", r["gewinn_jahr"])
    _zeile("./. Sozialabgaben", sv["summe_jahr"])
    _zeile("./. Steuern", st["summe_jahr"])
    _zeile("= NETTO IM JAHR", n["netto_jahr"])
    _zeile("= NETTO IM MONAT", n["netto_monat"])
    print("-" * breite)
    print("Abgabenquote auf den Gewinn:   %s" % _pct(n["abgabenquote_gewinn"]))
    print("Netto je Euro Umsatz:          %s" % _pct(n["nettoquote_umsatz"]))
    gb = n["grenzbelastung"]
    if gb:
        print("Von 1.000 EUR Mehrgewinn bleiben: %s (%s Abgaben)"
              % (_eur(gb["davon_netto"]), _pct(gb["abgaben_anteil"])))
    print()

    if "arbeitslosengeld_schaetzung" in r:
        a = r["arbeitslosengeld_schaetzung"]
        print("-" * breite)
        print("5) ARBEITSLOSENVERSICHERUNG — was der Beitrag kauft")
        print("-" * breite)
        print("   Qualifikationsgruppe %d (%s)"
              % (a["qualifikationsgruppe"], a["bezeichnung"]))
        _zeile("   fiktives Bemessungsentgelt/Mon", a["bemessungsentgelt_monat"])
        print("   Leistungssatz: %s" % _pct(a["leistungssatz"]))
        _zeile("   geschaetztes ALG I je Monat", a["alg_monat"])
        _zeile("   Beitrag je Jahr", a["beitrag_jahr"])
        if a["break_even_monate"]:
            print("   Ein Jahresbeitrag ist nach %s Tagen ALG I wieder drin."
                  % ("%.0f" % (a["break_even_monate"] * 30)))
        print("   Schaetzung — verbindlich nur die Auskunft der Agentur")
        print("   fuer Arbeit. Antragsfrist: 3 Monate ab Aufnahme der")
        print("   selbststaendigen Taetigkeit (§28a Abs. 3 SGB III).")
        print()

    print("-" * breite)
    print("6) MONATLICHE RUECKLAGE / DAUERAUFTRAEGE")
    print("-" * breite)
    _zeile("   -> Umsatzsteuer", rl["umsatzsteuer"])
    _zeile("   -> Gewerbesteuer", rl["gewerbesteuer"])
    _zeile("   -> ESt + Soli + KiSt", rl["est_soli_kist"])
    _zeile("   -> Sozialversicherung", rl["sozialversicherung"])
    _zeile("   SUMME JE MONAT", rl["summe"])
    print("=" * breite)
    print("Planungswerkzeug, keine Steuer- oder Rechtsberatung.")
    print("Werte jaehrlich pruefen: bmf-steuerrechner.de,")
    print("Sozialversicherungs-Rechengroessenverordnung, arbeitsagentur.de")


def drucke_tabelle(spanne, kostenquote, args, kwargs):
    """Szenario-Tabelle: Netto je Umsatzstufe."""
    lo, hi, step = spanne
    print("Szenario-Tabelle %s | Kostenquote %s | %s"
          % (args.jahr, _pct(kostenquote),
             "gewerblich, Hebesatz %.0f %%" % args.hebesatz
             if not args.freiberuflich else "freiberuflich"))
    print("%-14s %-14s %-14s %-14s %8s"
          % ("Umsatz/Mon", "Sozialabg./M", "Steuern/M", "NETTO/Mon", "Quote"))
    print("-" * 70)
    m = lo
    while m <= hi:
        r = berechne(m * 12, m * 12 * kostenquote, **kwargs)
        print("%-14s %-14s %-14s %-14s %8s" % (
            _eur(m),
            _eur(r["sozialversicherung"]["summe_monat"]),
            _eur(r["steuern"]["summe_monat"]),
            _eur(r["netto"]["netto_monat"]),
            _pct(r["netto"]["abgabenquote_gewinn"]),
        ))
        m += step


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Brutto-Netto-Rechner fuer Selbststaendige: alle direkten "
                    "Steuern, alle Pflichtbeitraege zur Sozialversicherung "
                    "und die freiwillige Arbeitslosenversicherung.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Betrieb
    p.add_argument("--umsatz", type=float,
                   help="Umsatz netto (Monat; mit --jahreswerte: Jahr)")
    p.add_argument("--ausgaben", type=float, default=0.0,
                   help="Betriebsausgaben netto (Monat bzw. Jahr)")
    p.add_argument("--jahreswerte", action="store_true",
                   help="Eingaben sind Jahres- statt Monatswerte")
    p.add_argument("--jahr", type=int, default=2026, help="Rechenjahr")
    p.add_argument("--freiberuflich", action="store_true",
                   help="Freier Beruf §18 EStG — keine Gewerbesteuer")
    p.add_argument("--hebesatz", type=float, default=DEFAULT_HEBESATZ,
                   help="GewSt-Hebesatz in %% (Wiggensbach: 320)")
    p.add_argument("--vorsteuer", type=float, default=None,
                   help="Vorsteuer (Monat bzw. Jahr); Standard: 19 %% der Ausgaben")
    p.add_argument("--kleinunternehmer", action="store_true",
                   help="Kleinunternehmerregelung §19 UStG")
    # Steuern
    p.add_argument("--kirche", action="store_true",
                   help="Kirchensteuerpflichtig (Bayern/BW: 8 %%)")
    p.add_argument("--kirchensteuer-satz", type=float, default=None,
                   help="Abweichender KiSt-Satz, z. B. 0.09")
    # Krankenversicherung
    p.add_argument("--kv", choices=["gesetzlich", "privat"], default="gesetzlich",
                   help="Krankenversicherung")
    p.add_argument("--zusatzbeitrag", type=float, default=None,
                   help="Kassenindividueller Zusatzbeitrag als Dezimalzahl, z. B. 0.029")
    p.add_argument("--ohne-krankengeld", action="store_true",
                   help="Ermaessigter Beitragssatz 14,0 %% (kein Krankengeld)")
    p.add_argument("--pkv-monat", type=float, default=0.0,
                   help="PKV-Beitrag pro Monat inkl. Pflegepflichtversicherung")
    p.add_argument("--pkv-basis-anteil", type=float, default=0.80,
                   help="Steuerlich abziehbarer Basisanteil des PKV-Beitrags")
    p.add_argument("--kinder", type=int, default=0,
                   help="Zahl der Kinder unter 25 (Pflegeversicherung)")
    p.add_argument("--unter-23", action="store_true",
                   help="Juenger als 23 — kein Kinderlosenzuschlag")
    # Altersvorsorge
    p.add_argument("--rv", default="keine",
                   choices=["keine", "regelbeitrag", "halber-regelbeitrag",
                            "einkommensgerecht", "freiwillig",
                            "versorgungswerk", "ruerup"],
                   help="Altersvorsorge-Modus")
    p.add_argument("--rv-betrag", type=float, default=0.0,
                   help="Monatsbeitrag fuer freiwillig/versorgungswerk/ruerup")
    # Arbeitslosenversicherung
    p.add_argument("--alv", action="store_true",
                   help="Freiwillige Arbeitslosenversicherung §28a SGB III")
    p.add_argument("--alv-gruender", action="store_true",
                   help="Halber Beitrag (Gruendungsjahr + Folgejahr)")
    p.add_argument("--qualifikationsgruppe", type=int, default=1,
                   choices=[1, 2, 3, 4],
                   help="Fuer die ALG-I-Schaetzung (1 = Hochschulabschluss)")
    p.add_argument("--alg-mit-kind", action="store_true",
                   help="Leistungssatz 67 %% statt 60 %%")
    # Sonstiges
    p.add_argument("--weitere-vorsorge", type=float, default=0.0,
                   help="Weitere Vorsorge pro Monat (BU, Unfall, Haftpflicht)")
    p.add_argument("--profil", type=str, default=None,
                   help="JSON-Profil mit Standardwerten (CLI uebersteuert)")
    p.add_argument("--tabelle", type=str, default=None, metavar="MIN:MAX:SCHRITT",
                   help="Szenario-Tabelle ueber Monatsumsaetze, z. B. 6000:16000:2000")
    p.add_argument("--kostenquote", type=float, default=0.25,
                   help="Kostenquote fuer --tabelle (Anteil vom Umsatz)")
    p.add_argument("--format", choices=["text", "json"], default="text",
                   help="Ausgabeformat")
    args = p.parse_args()

    if args.profil:
        try:
            with open(args.profil, "r", encoding="utf-8") as f:
                profil = json.load(f)
        except (OSError, ValueError) as exc:
            sys.exit("Profil konnte nicht gelesen werden: %s" % exc)
        for key, wert in profil.items():
            attr = key.replace("-", "_")
            if not hasattr(args, attr):
                continue
            # Nur setzen, wenn der CLI-Wert noch der Default ist.
            if getattr(args, attr) == p.get_default(attr):
                setattr(args, attr, wert)

    if args.kirchensteuer_satz is None:
        args.kirchensteuer_satz = 0.08 if args.kirche else 0.0

    if args.kv == "privat" and args.pkv_monat <= 0:
        p.error("--kv privat erfordert --pkv-monat")
    if args.rv in ("freiwillig", "versorgungswerk", "ruerup") \
            and args.rv_betrag <= 0:
        p.error("--rv %s erfordert --rv-betrag" % args.rv)

    kwargs = dict(
        jahr=args.jahr,
        gewerblich=not args.freiberuflich,
        hebesatz=args.hebesatz,
        kirchensteuer_satz=args.kirchensteuer_satz,
        kleinunternehmer=args.kleinunternehmer,
        kv_modus=args.kv,
        zusatzbeitrag=args.zusatzbeitrag,
        krankengeld=not args.ohne_krankengeld,
        pkv_monat=args.pkv_monat,
        pkv_basis_anteil=args.pkv_basis_anteil,
        kinder=args.kinder,
        kinderlos_ab_23=not args.unter_23,
        rv_modus=args.rv,
        rv_betrag_monat=args.rv_betrag,
        alv=args.alv,
        alv_gruender=args.alv_gruender,
        weitere_vorsorge_monat=args.weitere_vorsorge,
        qualifikationsgruppe=args.qualifikationsgruppe,
        alg_mit_kind=args.alg_mit_kind,
    )

    if args.tabelle:
        try:
            lo, hi, step = (float(x) for x in args.tabelle.split(":"))
        except ValueError:
            sys.exit("Ungueltiges Format fuer --tabelle, erwartet MIN:MAX:SCHRITT")
        drucke_tabelle((lo, hi, step), args.kostenquote, args, kwargs)
        return

    if args.umsatz is None:
        p.error("--umsatz ist erforderlich (oder --tabelle verwenden)")

    faktor = 1.0 if args.jahreswerte else 12.0
    ergebnis = berechne(
        umsatz_jahr=args.umsatz * faktor,
        ausgaben_jahr=args.ausgaben * faktor,
        vorsteuer_jahr=None if args.vorsteuer is None else args.vorsteuer * faktor,
        **kwargs
    )

    if args.format == "json":
        print(json.dumps(ergebnis, indent=2, ensure_ascii=False))
    else:
        drucke_bericht(ergebnis)


if __name__ == "__main__":
    main()
