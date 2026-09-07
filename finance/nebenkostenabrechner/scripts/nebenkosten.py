#!/usr/bin/env python3
"""Betriebskostenabrechnung nach BetrKV und HeizkostenV.

Liest eine Jahresakte im JSON-Format und gibt die Abrechnung je Mieteinheit
aus. Reine Standardbibliothek, keine Netzwerk- oder Modellaufrufe.

    python3 nebenkosten.py akte.json                 # Textabrechnung
    python3 nebenkosten.py akte.json --format json   # maschinenlesbar
    python3 nebenkosten.py akte.json --format csv    # fuer Tabellenkalkulation
    python3 nebenkosten.py akte.json --pruefen       # nur Plausibilitaetspruefung

Der Rechner prueft nicht, ob eine Position im Mietvertrag vereinbart ist.
Das bleibt Aufgabe des Vermieters.
"""

import argparse
import csv
import datetime as dt
import io
import json
import sys

SCHLUESSEL = {
    "flaeche": "Wohnflaeche (m2)",
    "einheiten": "Wohneinheiten (je 1/n)",
    "personen": "Personen",
    "direkt": "direkt / verbrauchsgenau",
    "heizung": "Heizkostenmodul",
    "nicht": "nicht umlagefaehig",
}

# 10-Stufen-Modell CO2KostAufG fuer Wohngebaeude: (Kennwert-Obergrenze kg/m2/a,
# Vermieteranteil in Prozent). Vor dem Versand gegen die amtliche Fassung pruefen.
CO2_STUFEN = [(12, 0), (17, 10), (22, 20), (27, 30), (32, 40),
              (37, 50), (42, 60), (47, 70), (52, 80), (float("inf"), 95)]


def co2_vermieteranteil(kennwert):
    for grenze, prozent in CO2_STUFEN:
        if kennwert < grenze:
            return prozent
    return 95


def d(s):
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def tage(von, bis):
    a, b = d(von), d(bis)
    if not a or not b or b < a:
        return 0
    return (b - a).days + 1


def euro(x):
    return "{:,.2f}".format(x).replace(",", "\x00").replace(".", ",").replace("\x00", ".")


class Abrechnung:
    def __init__(self, akte):
        self.a = akte
        self.o = akte["objekt"]
        self.units = akte["einheiten"]
        self.kosten = akte["kosten"]
        self.h = akte.get("heizung", {})
        self.hinweise = []

    # ---------- Zeit- und Flaechenanteile ----------
    def gesamttage(self):
        return tage(self.o["von"], self.o["bis"]) or 365

    def unit_tage(self, u):
        ov, ob = d(self.o["von"]), d(self.o["bis"])
        uv = d(u.get("von")) or ov
        ub = d(u.get("bis")) or ob
        if not (ov and ob and uv and ub):
            return self.gesamttage()
        s, e = max(uv, ov), min(ub, ob)
        return (e - s).days + 1 if e >= s else 0

    def unit_monate(self, u):
        return self.unit_tage(u) / self.gesamttage() * 12

    def flaeche_gesamt(self):
        return sum(float(u.get("flaeche", 0)) for u in self.units)

    def anteile(self, schluessel):
        basis = {"flaeche": lambda u: float(u.get("flaeche", 0)),
                 "einheiten": lambda u: 1.0,
                 "personen": lambda u: float(u.get("personen", 0))}.get(schluessel)
        if not basis:
            return {u["id"]: 0.0 for u in self.units}
        gew = {u["id"]: basis(u) * self.unit_tage(u) for u in self.units}
        s = sum(gew.values())
        return {k: (v / s if s > 0 else 0.0) for k, v in gew.items()}

    # ---------- Oelbestand ----------
    def oel(self):
        o = self.a.get("oel") or {}
        lief = sorted(o.get("lieferungen") or [], key=lambda x: x.get("datum") or "")
        zu_l = sum(float(l.get("liter", 0)) for l in lief)
        zu_e = sum(float(l.get("eur", 0)) for l in lief)
        anf_l, anf_e = float(o.get("anfangL", 0)), float(o.get("anfangEur", 0))
        end_l = float(o.get("endeL", 0))
        vorrat = anf_l + zu_l
        verbrauch = vorrat - end_l
        gedeckelt = False
        if verbrauch < 0 or verbrauch > vorrat:
            verbrauch = min(max(verbrauch, 0.0), vorrat)
            gedeckelt = True
        wert = anf_e + zu_e
        kosten = 0.0
        if vorrat > 0 and verbrauch > 0:
            if o.get("methode") == "fifo":
                lagen = [(anf_l, anf_e / anf_l if anf_l > 0 else 0.0)]
                for l in lief:
                    li = float(l.get("liter", 0))
                    lagen.append((li, float(l.get("eur", 0)) / li if li > 0 else 0.0))
                rest = verbrauch
                for menge, preis in lagen:
                    if rest <= 0:
                        break
                    nimm = min(rest, menge)
                    kosten += nimm * preis
                    rest -= nimm
            else:
                kosten = verbrauch * (wert / vorrat)
        return {"aktiv": bool(o.get("aktiv")), "zu_liter": zu_l, "zu_eur": zu_e,
                "vorrat": vorrat, "verbrauch": verbrauch, "kosten": kosten,
                "preis": wert / vorrat if vorrat > 0 else 0.0,
                "endwert": max(0.0, wert - kosten), "gedeckelt": gedeckelt,
                "co2_menge": verbrauch * float(o.get("faktor", 0))}

    # ---------- Heizung ----------
    def heizung(self):
        h = self.h
        oel = self.oel()
        if oel["aktiv"]:
            h["brenn"] = oel["kosten"]
        brutto = sum(float(h.get(f, 0)) for f in
                     ("brenn", "strom", "wartung", "mess", "schorn", "tank"))
        co2_v = float(h.get("co2Kosten", 0)) * float(h.get("co2Proz", 0)) / 100.0
        umlage = max(0.0, brutto - co2_v)
        ww_q = min(100.0, max(0.0, float(h.get("ww", 0)))) / 100.0
        pot_ww, pot_hz = umlage * ww_q, umlage * (1 - ww_q)
        grund_q = min(100.0, max(0.0, float(h.get("grund", 30)))) / 100.0
        fl = self.anteile("flaeche")

        def split(pot, feld):
            s = sum(float(u.get(feld, 0)) for u in self.units)
            grund, verbr = pot * grund_q, pot * (1 - grund_q)
            out = {}
            for u in self.units:
                vq = (float(u.get(feld, 0)) / s) if s > 0 else 1.0 / max(1, len(self.units))
                out[u["id"]] = grund * fl[u["id"]] + verbr * vq
            return out

        a_hz, a_ww = split(pot_hz, "vHeiz"), split(pot_ww, "vWW")
        fg = self.flaeche_gesamt()
        kennwert = float(h.get("co2Menge", 0)) / fg if fg > 0 else 0.0
        return {"brutto": brutto, "co2_vermieter": co2_v, "umlage": umlage,
                "pot_hz": pot_hz, "pot_ww": pot_ww, "a_hz": a_hz, "a_ww": a_ww,
                "ges": {u["id"]: a_hz[u["id"]] + a_ww[u["id"]] for u in self.units},
                "kennwert": kennwert, "grund_q": grund_q, "oel": oel}

    # ---------- Gesamtrechnung ----------
    def rechne(self):
        heiz = self.heizung()
        zeilen, pro_unit = [], {u["id"]: 0.0 for u in self.units}
        summe_kalt = summe_nicht = 0.0
        for k in self.kosten:
            schl = k.get("schluessel", "flaeche")
            if schl == "direkt":
                betrag = sum(float(v) for v in (k.get("direkt") or {}).values())
            else:
                betrag = float(k.get("betrag", 0))
            if schl == "nicht":
                summe_nicht += betrag
                continue
            if schl == "heizung":
                continue
            if schl == "direkt":
                a = {u["id"]: float((k.get("direkt") or {}).get(u["id"], 0)) for u in self.units}
            else:
                q = self.anteile(schl)
                a = {u["id"]: betrag * q[u["id"]] for u in self.units}
            for u in self.units:
                pro_unit[u["id"]] += a[u["id"]]
            summe_kalt += betrag
            zeilen.append({"nr": k.get("nr", ""), "pos": k.get("pos", ""),
                           "schluessel": schl, "beleg": k.get("beleg", ""),
                           "betrag": betrag, "anteile": a})

        ergebnis = []
        for u in self.units:
            kalt = pro_unit[u["id"]]
            warm = heiz["ges"][u["id"]]
            mon = self.unit_monate(u)
            vz = (float(u.get("vzNK", 0)) + float(u.get("vzHeiz", 0))) * mon
            ges = kalt + warm
            fl = float(u.get("flaeche", 0))
            ergebnis.append({
                "id": u["id"], "name": u.get("name", u["id"]), "mieter": u.get("mieter", ""),
                "flaeche": fl, "tage": self.unit_tage(u), "monate": round(mon, 2),
                "kalt": kalt, "warm": warm, "gesamt": ges, "vorauszahlung": vz,
                "saldo": ges - vz,
                "pro_qm_monat": (ges / fl / mon) if fl > 0 and mon > 0 else 0.0,
            })
        return {"zeilen": zeilen, "heizung": heiz, "einheiten": ergebnis,
                "summe_kalt": summe_kalt, "summe_warm": sum(heiz["ges"].values()),
                "summe_nicht": summe_nicht,
                "summe_gesamt": sum(e["gesamt"] for e in ergebnis),
                "summe_vz": sum(e["vorauszahlung"] for e in ergebnis),
                "summe_saldo": sum(e["saldo"] for e in ergebnis)}

    # ---------- Pruefungen ----------
    def pruefe(self, r):
        p = []
        grund = float(self.h.get("grund", 30))
        selbst = bool(self.o.get("selbst"))
        if r["heizung"]["umlage"] > 0 and not (30 <= grund <= 50) and not selbst:
            p.append(("FEHLER", "Grundkostenanteil {:.0f} % liegt ausserhalb 30 bis 50 %. "
                                "Paragraf 7 HeizkostenV verlangt 50 bis 70 % verbrauchsabhaengig."
                      .format(grund)))
        if selbst and len(self.units) <= 2:
            p.append(("HINWEIS", "Zweifamilienhaus mit Selbstnutzung: Ausnahme nach "
                                 "Paragraf 2 HeizkostenV, verbrauchsabhaengige Abrechnung nicht zwingend."))
        bis = d(self.o["bis"])
        if bis:
            frist = bis.replace(year=bis.year + 1)
            rest = (frist - dt.date.today()).days
            if rest < 0:
                p.append(("FEHLER", "Abrechnungsfrist am {} abgelaufen (Paragraf 556 Abs. 3 BGB). "
                                    "Nachforderungen in der Regel ausgeschlossen."
                          .format(frist.isoformat())))
            elif rest < 60:
                p.append(("WARNUNG", "Nur noch {} Tage bis zum Fristende am {}. "
                                     "Massgeblich ist der Zugang beim Mieter."
                          .format(rest, frist.isoformat())))
        kw = r["heizung"]["kennwert"]
        if kw > 0:
            soll = co2_vermieteranteil(kw)
            ist = float(self.h.get("co2Proz", 0))
            if abs(soll - ist) > 0.01:
                p.append(("WARNUNG", "CO2-Kennwert {:.1f} kg/m2a entspricht Stufe mit {} % "
                                     "Vermieteranteil, angesetzt sind {:.0f} %."
                          .format(kw, soll, ist)))
        for k in self.kosten:
            if k.get("schluessel") not in ("nicht", "heizung") and float(k.get("betrag", 0)) > 0 \
                    and not k.get("beleg"):
                p.append(("HINWEIS", "Position '{}' ohne Beleg-Nummer.".format(k.get("pos"))))
        oel = r["heizung"]["oel"]
        if oel["aktiv"]:
            if oel["gedeckelt"]:
                p.append(("FEHLER", "Oelbestand unplausibel: Endbestand groesser als Anfangsbestand "
                                    "plus Zukaeufe, oder negativer Verbrauch. Peilung pruefen."))
            else:
                p.append(("HINWEIS", "Oelverbrauch {:.0f} Liter, bewertet mit {} EUR. Endbestand "
                                     "{} EUR wird ins Folgejahr vorgetragen."
                          .format(oel["verbrauch"], euro(oel["kosten"]), euro(oel["endwert"]))))
        for u in self.units:
            if not u.get("angehoerig"):
                continue
            e = [x for x in r["einheiten"] if x["id"] == u["id"]][0]
            bk_m = e["gesamt"] / e["monate"] if e["monate"] else 0.0
            orts_kalt = float(u.get("ortsQm", 0)) * float(u.get("flaeche", 0))
            if orts_kalt <= 0:
                p.append(("WARNUNG", "{}: an Angehoerige vermietet, aber keine ortsuebliche "
                                     "Vergleichsmiete hinterlegt. Die 66-Prozent-Grenze des "
                                     "Paragrafen 21 Abs. 2 EStG ist nicht pruefbar."
                          .format(u.get("name"))))
                continue
            orts_warm = orts_kalt + bk_m
            quote = (float(u.get("kaltmiete", 0)) + bk_m) / orts_warm * 100
            ohne = float(u.get("kaltmiete", 0)) / orts_warm * 100
            mindest = 0.66 * orts_warm - bk_m
            if quote < 50:
                p.append(("FEHLER", "{}: {:.1f} % der ortsueblichen Warmmiete. Unter 50 Prozent, "
                                    "Werbungskosten nur anteilig abziehbar. Voller Abzug ab {} Kaltmiete."
                          .format(u.get("name"), quote, euro(mindest))))
            elif quote < 66:
                p.append(("WARNUNG", "{}: {:.1f} % der ortsueblichen Warmmiete. Totalueberschussprognose "
                                     "erforderlich. Ohne Prognose waeren {} Kaltmiete noetig."
                          .format(u.get("name"), quote, euro(mindest))))
            else:
                p.append(("HINWEIS", "{}: {:.1f} % der ortsueblichen Warmmiete, voller Werbungskosten"
                                     "abzug. Ohne Nebenkostenumlage laege die Quote bei {:.1f} %."
                          .format(u.get("name"), quote, ohne)))
        for e in r["einheiten"]:
            if e["vorauszahlung"] > 0 and e["saldo"] / e["vorauszahlung"] > 0.25:
                p.append(("HINWEIS", "{}: Nachzahlung uebersteigt 25 % der Vorauszahlung. "
                                     "Anpassung nach Paragraf 560 Abs. 4 BGB auf {} EUR pro Monat moeglich."
                          .format(e["name"], euro(e["gesamt"] / (e["monate"] or 12)))))
        return p


def als_text(ab, r):
    o = ab.o
    out = io.StringIO()
    w = out.write
    w("=" * 78 + "\n")
    w("BETRIEBSKOSTENABRECHNUNG {}\n".format(ab.a.get("jahr", "")))
    w("{}{}\n".format(o.get("name", ""), (", " + o["strasse"]) if o.get("strasse") else ""))
    w("Zeitraum {} bis {}   Gesamtflaeche {} m2\n".format(
        o["von"], o["bis"], euro(ab.flaeche_gesamt())))
    w("=" * 78 + "\n\n")
    for e in r["einheiten"]:
        w("-" * 78 + "\n")
        w("{}   {}\n".format(e["name"], e["mieter"] or "Mieter/in"))
        w("{} m2   {} Tage Nutzung\n\n".format(euro(e["flaeche"]), e["tage"]))
        w("{:<40}{:>12}{:>9}{:>14}\n".format("Kostenart", "Gesamt EUR", "Anteil", "Ihr Anteil"))
        w("-" * 78 + "\n")
        for z in r["zeilen"]:
            if z["betrag"] <= 0:
                continue
            q = z["anteile"][e["id"]] / z["betrag"] * 100 if z["betrag"] else 0
            w("{:<40}{:>12}{:>8.2f}%{:>14}\n".format(
                (z["nr"] + " " + z["pos"])[:39], euro(z["betrag"]), q, euro(z["anteile"][e["id"]])))
        h = r["heizung"]
        if h["umlage"] > 0:
            w("{:<40}{:>12}{:>9}{:>14}\n".format(
                "Heizkosten (HeizkostenV)", euro(h["pot_hz"]), "",
                euro(h["a_hz"][e["id"]])))
            if h["pot_ww"] > 0:
                w("{:<40}{:>12}{:>9}{:>14}\n".format(
                    "Warmwasserkosten", euro(h["pot_ww"]), "", euro(h["a_ww"][e["id"]])))
            if h["co2_vermieter"] > 0:
                w("{:<40}{:>12}{:>9}{:>14}\n".format(
                    "abzgl. CO2-Anteil Vermieter", "-" + euro(h["co2_vermieter"]), "", "beruecks."))
        w("-" * 78 + "\n")
        w("{:<62}{:>16}\n".format("Summe umlagefaehig", euro(e["gesamt"])))
        w("{:<62}{:>16}\n".format(
            "abzgl. Vorauszahlungen ({:.2f} Monate)".format(e["monate"]), "-" + euro(e["vorauszahlung"])))
        label = "NACHZAHLUNG DURCH MIETER" if e["saldo"] >= 0 else "GUTHABEN FUER MIETER"
        w("{:<62}{:>16}\n".format(label, euro(abs(e["saldo"]))))
        w("je m2 und Monat: {} EUR\n\n".format(euro(e["pro_qm_monat"])))
    w("=" * 78 + "\n")
    w("{:<62}{:>16}\n".format("Umlagefaehig gesamt", euro(r["summe_gesamt"])))
    w("{:<62}{:>16}\n".format("Vorauszahlungen gesamt", euro(r["summe_vz"])))
    w("{:<62}{:>16}\n".format("Saldo gesamt", euro(r["summe_saldo"])))
    w("{:<62}{:>16}\n".format("Nicht umlagefaehig (Vermieter)", euro(r["summe_nicht"])))
    p = ab.pruefe(r)
    if p:
        w("\nPRUEFUNG\n" + "-" * 78 + "\n")
        for stufe, txt in p:
            w("[{}] {}\n".format(stufe, txt))
    w("\nOhne Gewaehr. Ersetzt keine Rechtsberatung.\n")
    return out.getvalue()


def als_csv(ab, r):
    buf = io.StringIO()
    wr = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    namen = [e["name"] for e in r["einheiten"]]
    wr.writerow(["Nr", "Position", "Umlageschluessel", "Beleg", "Gesamtkosten"] + namen)
    for z in r["zeilen"]:
        wr.writerow([z["nr"], z["pos"], SCHLUESSEL.get(z["schluessel"], z["schluessel"]),
                     z["beleg"], euro(z["betrag"])] +
                    [euro(z["anteile"][e["id"]]) for e in r["einheiten"]])
    h = r["heizung"]
    wr.writerow(["", "Heizung und Warmwasser", "HeizkostenV", "", euro(h["umlage"])] +
                [euro(h["ges"][e["id"]]) for e in r["einheiten"]])
    wr.writerow([])
    wr.writerow(["", "Summe umlagefaehig", "", "", euro(r["summe_gesamt"])] +
                [euro(e["gesamt"]) for e in r["einheiten"]])
    wr.writerow(["", "Vorauszahlungen", "", "", euro(r["summe_vz"])] +
                [euro(e["vorauszahlung"]) for e in r["einheiten"]])
    wr.writerow(["", "Saldo", "", "", euro(r["summe_saldo"])] +
                [euro(e["saldo"]) for e in r["einheiten"]])
    wr.writerow(["", "Nicht umlagefaehig", "", "", euro(r["summe_nicht"])])
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description="Betriebskostenabrechnung nach BetrKV und HeizkostenV")
    ap.add_argument("akte", help="Pfad zur JSON-Jahresakte")
    ap.add_argument("--format", choices=["text", "json", "csv"], default="text")
    ap.add_argument("--pruefen", action="store_true", help="nur Plausibilitaetspruefung ausgeben")
    args = ap.parse_args()

    with open(args.akte, encoding="utf-8") as f:
        akte = json.load(f)
    ab = Abrechnung(akte)
    r = ab.rechne()

    if args.pruefen:
        p = ab.pruefe(r)
        if not p:
            print("Keine Beanstandungen.")
        for stufe, txt in p:
            print("[{}] {}".format(stufe, txt))
        return 1 if any(s == "FEHLER" for s, _ in p) else 0

    if args.format == "json":
        r["pruefung"] = [{"stufe": s, "text": t} for s, t in ab.pruefe(r)]
        print(json.dumps(r, indent=2, ensure_ascii=False))
    elif args.format == "csv":
        sys.stdout.write(als_csv(ab, r))
    else:
        sys.stdout.write(als_text(ab, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
