#!/usr/bin/env python3
"""Pseudonymisierung fuer den A/A Steckbrief-Arbeitsplatz.

Ersetzt personenbeziehbare Klartextangaben (Kandidatenname, Arbeitgeber,
Orte, Kontaktdaten) durch stabile Platzhalter, bevor Text den Rechner
verlaesst, und setzt sie danach lokal wieder ein.

Die Zuordnungstabelle bleibt ausschliesslich im Arbeitsspeicher des
lokalen Prozesses und in der lokalen Falldatei. Sie wird nie versendet.

Nur Standardbibliothek, Python 3.8+.
"""

import re

# Kontaktdaten werden immer erkannt, unabhaengig von der Entitaetenliste.
MUSTER = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("TELEFON", re.compile(r"(?:\+\d{1,3}[\s./-]?)?(?:\(?\d{2,5}\)?[\s./-]?)\d{3,}[\s./-]?\d{2,}")),
    ("URL", re.compile(r"https?://\S+|www\.\S+")),
]


class Mapping:
    """Bidirektionale Zuordnung zwischen Klartext und Platzhalter."""

    def __init__(self):
        self.zu_platzhalter = {}   # klartext -> platzhalter
        self.zu_klartext = {}      # platzhalter -> klartext
        self._zaehler = {}

    def platzhalter(self, klartext, typ):
        klartext = klartext.strip()
        if not klartext:
            return klartext
        if klartext in self.zu_platzhalter:
            return self.zu_platzhalter[klartext]
        self._zaehler[typ] = self._zaehler.get(typ, 0) + 1
        marke = "[%s_%d]" % (typ, self._zaehler[typ])
        self.zu_platzhalter[klartext] = marke
        self.zu_klartext[marke] = klartext
        return marke

    def as_dict(self):
        return dict(self.zu_klartext)

    @classmethod
    def from_dict(cls, daten):
        m = cls()
        for marke, klartext in (daten or {}).items():
            m.zu_klartext[marke] = klartext
            m.zu_platzhalter[klartext] = marke
        return m


def namensvarianten(vollname):
    """Liefert Varianten eines Personennamens, laengste zuerst."""
    vollname = (vollname or "").strip()
    if not vollname:
        return []
    teile = [t.strip(",.") for t in vollname.split() if t.strip(",.")]
    varianten = {vollname}
    if len(teile) >= 2:
        varianten.add("%s %s" % (teile[0], teile[-1]))
        varianten.add("%s, %s" % (teile[-1], teile[0]))
        varianten.add(teile[-1])
        varianten.add(teile[0])
    varianten.update(t for t in teile if len(t) > 2)
    return sorted(varianten, key=len, reverse=True)


def pseudonymisieren(text, kandidat_name="", arbeitgeber=None, orte=None, mapping=None):
    """Ersetzt Klartext durch Platzhalter. Gibt (text, mapping) zurueck.

    Reihenfolge ist wichtig: erst lange Zeichenketten, dann kurze, sonst
    zerschneidet ein kurzer Treffer einen laengeren.
    """
    mapping = mapping or Mapping()
    ergebnis = text or ""

    for typ, muster in MUSTER:
        for treffer in sorted(set(muster.findall(ergebnis)), key=len, reverse=True):
            if len(treffer.strip()) < 5:
                continue
            ergebnis = ergebnis.replace(treffer, mapping.platzhalter(treffer, typ))

    for wert in sorted([a for a in (arbeitgeber or []) if a and a.strip()],
                       key=len, reverse=True):
        ergebnis = _ersetze(ergebnis, wert, mapping.platzhalter(wert, "ARBEITGEBER"))

    for wert in sorted([o for o in (orte or []) if o and o.strip()],
                       key=len, reverse=True):
        ergebnis = _ersetze(ergebnis, wert, mapping.platzhalter(wert, "ORT"))

    if kandidat_name:
        marke = mapping.platzhalter(kandidat_name.strip(), "KANDIDAT")
        for variante in namensvarianten(kandidat_name):
            ergebnis = _ersetze(ergebnis, variante, marke)

    return ergebnis, mapping


def _ersetze(text, wort, marke):
    if not wort or wort in ("", " "):
        return text
    return re.sub(re.escape(wort), marke.replace("\\", "\\\\"), text, flags=re.IGNORECASE)


def repersonalisieren(text, mapping):
    """Setzt Klartext wieder ein. Laengste Platzhalter zuerst."""
    ergebnis = text or ""
    tabelle = mapping.as_dict() if isinstance(mapping, Mapping) else dict(mapping or {})
    for marke in sorted(tabelle, key=len, reverse=True):
        ergebnis = ergebnis.replace(marke, tabelle[marke])
    return ergebnis


def restbestand(text, kandidat_name="", arbeitgeber=None, orte=None, ausnahmen=None):
    """Prueft, ob nach der Pseudonymisierung noch Klartext im Text steht.

    Rueckgabe: Liste der gefundenen Klartextfragmente. Leere Liste heisst
    sauber. Wird vor jedem Versand an eine externe Schnittstelle geprueft.

    ausnahmen: Zeichenketten, die im Text stehen duerfen, weil sie nicht zum
    Kandidaten gehoeren. Typisch der Name der Beraterin oder des Beraters und
    der Name des Auftraggebers, die im Mandatskopf stehen. Sie werden vor der
    Pruefung aus der Textkopie entfernt, damit ein gemeinsamer Nachname von
    Kandidat und Berater keinen Fehlalarm ausloest.
    """
    text = text or ""
    for ausnahme in sorted([a for a in (ausnahmen or []) if a and a.strip()],
                           key=len, reverse=True):
        text = re.sub(re.escape(ausnahme), " ", text, flags=re.IGNORECASE)
    funde = []
    kandidaten = list(arbeitgeber or []) + list(orte or [])
    if kandidat_name:
        kandidaten += namensvarianten(kandidat_name)
    for wert in kandidaten:
        if wert and len(wert) > 2 and re.search(re.escape(wert), text, re.IGNORECASE):
            funde.append(wert)
    for typ, muster in MUSTER:
        for treffer in muster.findall(text):
            if len(treffer.strip()) >= 5:
                funde.append("%s: %s" % (typ, treffer))
    return sorted(set(funde))
