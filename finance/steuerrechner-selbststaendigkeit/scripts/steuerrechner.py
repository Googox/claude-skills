#!/usr/bin/env python3
"""
Steuerrechner fuer Selbststaendige (Einzelunternehmer, gewerblich, EUeR).

Rechnet aus monatlichem (oder jaehrlichem) Umsatz und Betriebsausgaben alle
relevanten gewerblichen Steuern hoch und leitet daraus monatliche
Ruecklagen-Ueberweisungen fuer die Qonto-Unterkonten ab:

  1. Umsatzsteuer-Zahllast  (USt 19 % abzueglich Vorsteuer)
  2. Gewerbesteuer          (Freibetrag 24.500 EUR, Messzahl 3,5 %, Hebesatz
                             konfigurierbar — Standard: 320 % / Wiggensbach)
  3. Einkommensteuer        (Grundtarif §32a EStG, Jahr waehlbar)
     + Solidaritaetszuschlag (5,5 % oberhalb der Freigrenze, mit Milderungszone)
     + Kirchensteuer         (optional, Bayern/BW 8 %, sonst 9 %)
  4. §35 EStG               (Anrechnung der Gewerbesteuer auf die ESt —
                             bei Hebesatz <= 400 % wird die GewSt faktisch
                             vollstaendig angerechnet)

WICHTIG: Dies ist ein Planungswerkzeug fuer Steuerruecklagen, KEINE
Steuerberatung und KEIN Ersatz fuer den Steuerbescheid. Tarifwerte muessen
jaehrlich gegen die offiziellen BMF-Werte geprueft werden
(https://www.bmf-steuerrechner.de).

Verwendung:
  python3 steuerrechner.py --umsatz 12500 --ausgaben 2800 --jahr 2026
  python3 steuerrechner.py --umsatz 12500 --ausgaben 2800 --kirche --kv-monat 850
  python3 steuerrechner.py --umsatz 150000 --ausgaben 33600 --jahreswerte
  python3 steuerrechner.py --profil steuerprofil.json --umsatz 12500
  python3 steuerrechner.py --tabelle 6000:16000:2000 --kostenquote 0.25
  python3 steuerrechner.py --umsatz 12500 --ausgaben 2800 --format json

Nur Python-Standardbibliothek, Python 3.8+.
"""

import argparse
import json
import math
import sys

# ---------------------------------------------------------------------------
# Tarif-Parameter (jaehrlich pruefen und pflegen!)
# ---------------------------------------------------------------------------

# Eckwerte des Einkommensteuertarifs (§32a EStG), zu versteuerndes Einkommen:
# [Grundfreibetrag, Ende Progressionszone 1, Ende Progressionszone 2,
#  Beginn Reichensteuer]. Die Polynom-Koeffizienten werden aus den Eckwerten
# und den gesetzlichen Grenzsteuersaetzen (14 % / 23,97 % / 42 % / 45 %)
# abgeleitet — fuer 2025 ergibt das exakt die im Gesetz stehenden Werte
# (932,30 / 176,64 / 1.015,13 / 10.911,92 / 19.246,67).
TARIF_ECKWERTE = {
    2025: [12096, 17443, 68480, 277825],
    2026: [12348, 17799, 69878, 277825],
}

# Solidaritaetszuschlag: Freigrenze der festzusetzenden ESt (Einzelveranlagung)
SOLI_FREIGRENZE = {2025: 19950, 2026: 20350}
SOLI_SATZ = 0.055
SOLI_MILDERUNG = 0.119  # Milderungszone: max. 11,9 % des uebersteigenden Betrags

# Gewerbesteuer
GEWST_FREIBETRAG = 24500      # Einzelunternehmer / Personengesellschaft
GEWST_MESSZAHL = 0.035
GEWST_ANRECHNUNG_FAKTOR = 4.0  # §35 EStG: 4,0-faches des Messbetrags

# Umsatzsteuer
UST_REGELSATZ = 0.19

# Sonderausgaben-Pauschbetrag (ohne Nachweis)
SONDERAUSGABEN_PAUSCHBETRAG = 36

DEFAULT_HEBESATZ = 320.0  # Wiggensbach (Landkreis Oberallgaeu)


# ---------------------------------------------------------------------------
# Steuerfunktionen
# ---------------------------------------------------------------------------

def einkommensteuer(zve, jahr):
    """Tarifliche Einkommensteuer nach §32a EStG (Grundtarif, Einzelveranlagung)."""
    if jahr not in TARIF_ECKWERTE:
        raise ValueError(
            "Kein Tarif fuer %s hinterlegt. Verfuegbar: %s"
            % (jahr, sorted(TARIF_ECKWERTE))
        )
    e0, e1, e2, e3 = TARIF_ECKWERTE[jahr]
    zve = math.floor(max(0, zve))  # auf vollen Euro abrunden

    if zve <= e0:
        return 0.0

    if zve <= e1:
        y = (zve - e0) / 10000.0
        y_end = (e1 - e0) / 10000.0
        a = 997.0 / (2 * y_end)  # Anstieg 14 % -> 23,97 %
        tax = (a * y + 1400) * y
    elif zve <= e2:
        z = (zve - e1) / 10000.0
        z_end = (e2 - e1) / 10000.0
        b = 1803.0 / (2 * z_end)  # Anstieg 23,97 % -> 42 %
        c1 = 1898.5 * ((e1 - e0) / 10000.0)  # Steuer am Ende von Zone 1
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

    return float(math.floor(tax))  # auf vollen Euro abrunden


def gewerbesteuer(gewinn, hebesatz):
    """Gewerbesteuer eines Einzelunternehmers (ohne Hinzurechnungen/Kuerzungen).

    Rueckgabe: (gewerbesteuer, steuermessbetrag)
    """
    gewerbeertrag = math.floor(max(0, gewinn) / 100) * 100  # auf volle 100 abrunden
    bemessung = max(0, gewerbeertrag - GEWST_FREIBETRAG)
    messbetrag = bemessung * GEWST_MESSZAHL
    return round(messbetrag * hebesatz / 100.0, 2), round(messbetrag, 2)


def solidaritaetszuschlag(est, jahr):
    """Soli auf die festzusetzende ESt, mit Freigrenze und Milderungszone."""
    freigrenze = SOLI_FREIGRENZE.get(jahr)
    if freigrenze is None:
        raise ValueError("Keine Soli-Freigrenze fuer %s hinterlegt." % jahr)
    if est <= freigrenze:
        return 0.0
    return round(min(SOLI_SATZ * est, SOLI_MILDERUNG * (est - freigrenze)), 2)


def berechne_jahr(
    umsatz_jahr,
    ausgaben_jahr,
    jahr,
    hebesatz=DEFAULT_HEBESATZ,
    kirchensteuer_satz=0.0,
    vorsorge_jahr=0.0,
    vorsteuer_jahr=None,
    kleinunternehmer=False,
):
    """Vollstaendige Jahresrechnung. Alle Betraege netto (ohne USt), in EUR."""
    gewinn = umsatz_jahr - ausgaben_jahr

    # --- Umsatzsteuer (Durchlaufposten, aber liquiditaetswirksam) ---
    if kleinunternehmer:
        ust, vorsteuer, ust_zahllast = 0.0, 0.0, 0.0
    else:
        ust = round(umsatz_jahr * UST_REGELSATZ, 2)
        if vorsteuer_jahr is None:
            # Naeherung: alle Betriebsausgaben enthalten 19 % Vorsteuer.
            # Bei vielen vorsteuerfreien Kosten (Versicherungen, Bewirtung
            # anteilig, Auslandsleistungen) explizit --vorsteuer angeben.
            vorsteuer = round(ausgaben_jahr * UST_REGELSATZ, 2)
        else:
            vorsteuer = round(vorsteuer_jahr, 2)
        ust_zahllast = round(ust - vorsteuer, 2)

    # --- Gewerbesteuer ---
    gewst, messbetrag = gewerbesteuer(gewinn, hebesatz)

    # --- Einkommensteuer ---
    zve = max(0.0, gewinn - vorsorge_jahr - SONDERAUSGABEN_PAUSCHBETRAG)
    est_tariflich = einkommensteuer(zve, jahr)

    # §35 EStG: Anrechnung der GewSt (4,0-facher Messbetrag, gedeckelt auf die
    # tatsaechlich gezahlte GewSt und auf die tarifliche ESt)
    anrechnung = round(
        min(GEWST_ANRECHNUNG_FAKTOR * messbetrag, gewst, est_tariflich), 2
    )
    est = round(est_tariflich - anrechnung, 2)

    soli = solidaritaetszuschlag(est, jahr)
    # Hinweis: Kirchensteuer ist selbst als Sonderausgabe abziehbar; das wird
    # hier bewusst NICHT gegengerechnet -> die Ruecklage ist leicht konservativ.
    kirchensteuer = round(est * kirchensteuer_satz, 2)

    steuern_auf_gewinn = round(gewst + est + soli + kirchensteuer, 2)
    gesamt_inkl_ust = round(steuern_auf_gewinn + max(0.0, ust_zahllast), 2)

    return {
        "jahr": jahr,
        "eingaben": {
            "umsatz_jahr_netto": round(umsatz_jahr, 2),
            "betriebsausgaben_jahr_netto": round(ausgaben_jahr, 2),
            "vorsorgeaufwand_jahr": round(vorsorge_jahr, 2),
            "hebesatz_prozent": hebesatz,
            "kirchensteuer_satz": kirchensteuer_satz,
            "kleinunternehmer": kleinunternehmer,
        },
        "gewinn_jahr": round(gewinn, 2),
        "umsatzsteuer": {
            "umsatzsteuer": ust,
            "vorsteuer": vorsteuer,
            "zahllast_jahr": ust_zahllast,
            "zahllast_monat": round(ust_zahllast / 12.0, 2),
        },
        "gewerbesteuer": {
            "steuermessbetrag": messbetrag,
            "gewerbesteuer_jahr": gewst,
            "effektiver_satz_auf_gewinn": (
                round(gewst / gewinn, 4) if gewinn > 0 else 0.0
            ),
        },
        "einkommensteuer": {
            "zu_versteuerndes_einkommen": round(zve, 2),
            "est_tariflich": est_tariflich,
            "anrechnung_gewst_p35": anrechnung,
            "est_festzusetzen": est,
            "solidaritaetszuschlag": soli,
            "kirchensteuer": kirchensteuer,
        },
        "summen": {
            "steuern_auf_gewinn_jahr": steuern_auf_gewinn,
            "steuern_auf_gewinn_monat": round(steuern_auf_gewinn / 12.0, 2),
            "gesamt_inkl_ust_zahllast_jahr": gesamt_inkl_ust,
            "effektive_belastung_gewinn": (
                round(steuern_auf_gewinn / gewinn, 4) if gewinn > 0 else 0.0
            ),
        },
        "qonto_ruecklagen_monatlich": {
            "unterkonto_umsatzsteuer": round(max(0.0, ust_zahllast) / 12.0, 2),
            "unterkonto_gewerbesteuer": round(gewst / 12.0, 2),
            "unterkonto_est_soli_kist": round(
                (est + soli + kirchensteuer) / 12.0, 2
            ),
            "summe_monatlich": round(
                (max(0.0, ust_zahllast) + steuern_auf_gewinn) / 12.0, 2
            ),
        },
    }


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def _eur(x):
    """Formatierung im deutschen Zahlenformat: 12.345,67 EUR"""
    s = "{:,.2f}".format(x).replace(",", "X").replace(".", ",").replace("X", ".")
    return s + " EUR"


def drucke_bericht(r):
    e = r["eingaben"]
    u = r["umsatzsteuer"]
    g = r["gewerbesteuer"]
    est = r["einkommensteuer"]
    s = r["summen"]
    q = r["qonto_ruecklagen_monatlich"]

    print("=" * 62)
    print("STEUERRECHNER SELBSTSTAENDIGKEIT — Planungsjahr %s" % r["jahr"])
    print("=" * 62)
    print("Umsatz (netto, Jahr):        %s" % _eur(e["umsatz_jahr_netto"]))
    print("Betriebsausgaben (netto):    %s" % _eur(e["betriebsausgaben_jahr_netto"]))
    print("Gewinn (EUeR):               %s" % _eur(r["gewinn_jahr"]))
    print("Hebesatz Gewerbesteuer:      %.0f %%" % e["hebesatz_prozent"])
    print("-" * 62)
    print("1) UMSATZSTEUER (Durchlaufposten — gehoert nie dir!)")
    if e["kleinunternehmer"]:
        print("   Kleinunternehmer (§19 UStG): keine USt, keine Vorsteuer")
    else:
        print("   Umsatzsteuer 19 %%:         %s" % _eur(u["umsatzsteuer"]))
        print("   ./. Vorsteuer:             %s" % _eur(u["vorsteuer"]))
        print("   = Zahllast Jahr:           %s" % _eur(u["zahllast_jahr"]))
        print("     Zahllast je Monat:       %s" % _eur(u["zahllast_monat"]))
    print("-" * 62)
    print("2) GEWERBESTEUER (Freibetrag 24.500, Messzahl 3,5 %)")
    print("   Steuermessbetrag:          %s" % _eur(g["steuermessbetrag"]))
    print("   Gewerbesteuer Jahr:        %s" % _eur(g["gewerbesteuer_jahr"]))
    print("-" * 62)
    print("3) EINKOMMENSTEUER + ANNEXSTEUERN")
    print("   zu verst. Einkommen:       %s" % _eur(est["zu_versteuerndes_einkommen"]))
    print("   ESt tariflich:             %s" % _eur(est["est_tariflich"]))
    print("   ./. GewSt-Anrechnung §35:  %s" % _eur(est["anrechnung_gewst_p35"]))
    print("   = ESt festzusetzen:        %s" % _eur(est["est_festzusetzen"]))
    print("   + Solidaritaetszuschlag:   %s" % _eur(est["solidaritaetszuschlag"]))
    print("   + Kirchensteuer:           %s" % _eur(est["kirchensteuer"]))
    print("=" * 62)
    print("STEUERN AUF GEWINN (Jahr):    %s" % _eur(s["steuern_auf_gewinn_jahr"]))
    print("Effektive Belastung Gewinn:   %.1f %%"
          % (100 * s["effektive_belastung_gewinn"]))
    print("=" * 62)
    print("MONATLICHE QONTO-UEBERWEISUNGEN (Ruecklagen-Unterkonten)")
    print("   -> Unterkonto 'Umsatzsteuer':   %s"
          % _eur(q["unterkonto_umsatzsteuer"]))
    print("   -> Unterkonto 'Gewerbesteuer':  %s"
          % _eur(q["unterkonto_gewerbesteuer"]))
    print("   -> Unterkonto 'ESt+Soli+KiSt':  %s"
          % _eur(q["unterkonto_est_soli_kist"]))
    print("   SUMME RUECKLAGE JE MONAT:       %s" % _eur(q["summe_monatlich"]))
    print("=" * 62)
    print("Hinweis: Planungswerkzeug, keine Steuerberatung. Werte jaehrlich")
    print("gegen den offiziellen BMF-Rechner pruefen: bmf-steuerrechner.de")


def drucke_tabelle(spanne, kostenquote, args):
    """Szenario-Tabelle: monatliche Ruecklage je Umsatzstufe."""
    lo, hi, step = spanne
    print("Szenario-Tabelle %s | Kostenquote %.0f %% | Hebesatz %.0f %%"
          % (args.jahr, kostenquote * 100, args.hebesatz))
    print("%-18s %-16s %-16s %-16s" % (
        "Umsatz/Monat", "Ruecklage/Monat", "davon USt", "eff. Steuer/Gewinn"))
    print("-" * 68)
    m = lo
    while m <= hi:
        r = berechne_jahr(
            m * 12, m * 12 * kostenquote, args.jahr,
            hebesatz=args.hebesatz,
            kirchensteuer_satz=args.kirchensteuer_satz,
            vorsorge_jahr=args.kv_monat * 12 + args.sonstige_vorsorge * 12,
            kleinunternehmer=args.kleinunternehmer,
        )
        q = r["qonto_ruecklagen_monatlich"]
        print("%-18s %-16s %-16s %15.1f %%" % (
            _eur(m), _eur(q["summe_monatlich"]),
            _eur(q["unterkonto_umsatzsteuer"]),
            100 * r["summen"]["effektive_belastung_gewinn"]))
        m += step


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Steuerrechner fuer Selbststaendige (Einzelunternehmer, "
                    "gewerblich) — errechnet USt, GewSt, ESt, Soli, KiSt und "
                    "die monatlichen Qonto-Ruecklagen.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--umsatz", type=float, help="Umsatz netto (Monat; mit --jahreswerte: Jahr)")
    p.add_argument("--ausgaben", type=float, default=0.0, help="Betriebsausgaben netto (Monat bzw. Jahr)")
    p.add_argument("--jahr", type=int, default=2026, help="Steuerjahr (Tarif)")
    p.add_argument("--hebesatz", type=float, default=DEFAULT_HEBESATZ, help="GewSt-Hebesatz in %% (Wiggensbach: 320)")
    p.add_argument("--kirche", action="store_true", help="Kirchensteuerpflichtig (Bayern: 8 %%)")
    p.add_argument("--kirchensteuer-satz", type=float, default=None, help="Abweichender KiSt-Satz, z.B. 0.09")
    p.add_argument("--kv-monat", type=float, default=0.0, help="Kranken-/Pflegeversicherung pro Monat (Sonderausgabe)")
    p.add_argument("--sonstige-vorsorge", type=float, default=0.0, help="Weitere Vorsorge pro Monat (Rentenvers., Ruerup)")
    p.add_argument("--vorsteuer", type=float, default=None, help="Vorsteuer (Monat bzw. Jahr); Standard: 19 %% der Ausgaben")
    p.add_argument("--kleinunternehmer", action="store_true", help="Kleinunternehmerregelung §19 UStG aktiv")
    p.add_argument("--jahreswerte", action="store_true", help="Eingaben sind Jahres- statt Monatswerte")
    p.add_argument("--profil", type=str, default=None, help="JSON-Profil mit Standardwerten (CLI uebersteuert)")
    p.add_argument("--tabelle", type=str, default=None, metavar="MIN:MAX:SCHRITT", help="Szenario-Tabelle ueber Monatsumsaetze, z.B. 6000:16000:2000")
    p.add_argument("--kostenquote", type=float, default=0.25, help="Kostenquote fuer --tabelle (Anteil vom Umsatz)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Ausgabeformat")
    args = p.parse_args()

    # Profil laden (Datei liefert Defaults, explizite CLI-Werte gewinnen)
    if args.profil:
        try:
            with open(args.profil, "r", encoding="utf-8") as f:
                profil = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            sys.exit("Profil konnte nicht gelesen werden: %s" % exc)
        for key in ("umsatz", "ausgaben", "jahr", "hebesatz", "kv_monat",
                    "sonstige_vorsorge", "vorsteuer", "kirchensteuer_satz"):
            if key in profil and p.get_default(key) == getattr(args, key):
                setattr(args, key, profil[key])
        if profil.get("kleinunternehmer"):
            args.kleinunternehmer = True
        if profil.get("kirche"):
            args.kirche = True

    if args.kirchensteuer_satz is None:
        args.kirchensteuer_satz = 0.08 if args.kirche else 0.0

    if args.tabelle:
        try:
            lo, hi, step = (float(x) for x in args.tabelle.split(":"))
        except ValueError:
            sys.exit("Ungueltiges Format fuer --tabelle, erwartet MIN:MAX:SCHRITT")
        drucke_tabelle((lo, hi, step), args.kostenquote, args)
        return

    if args.umsatz is None:
        p.error("--umsatz ist erforderlich (oder --tabelle verwenden)")

    faktor = 1.0 if args.jahreswerte else 12.0
    ergebnis = berechne_jahr(
        umsatz_jahr=args.umsatz * faktor,
        ausgaben_jahr=args.ausgaben * faktor,
        jahr=args.jahr,
        hebesatz=args.hebesatz,
        kirchensteuer_satz=args.kirchensteuer_satz,
        vorsorge_jahr=(args.kv_monat + args.sonstige_vorsorge) * faktor
        if args.jahreswerte
        else (args.kv_monat + args.sonstige_vorsorge) * 12.0,
        vorsteuer_jahr=None if args.vorsteuer is None else args.vorsteuer * faktor,
        kleinunternehmer=args.kleinunternehmer,
    )

    if args.format == "json":
        print(json.dumps(ergebnis, indent=2, ensure_ascii=False))
    else:
        drucke_bericht(ergebnis)


if __name__ == "__main__":
    main()
