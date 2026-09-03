#!/usr/bin/env python3
"""Lokale Textextraktion aus Lebenslaufdateien.

Unterstuetzt DOCX und Klartext ohne externe Abhaengigkeiten. Die Datei
wird ausschliesslich lokal gelesen, nichts wird hochgeladen.

PDF wird bewusst nicht unterstuetzt: eine zuverlaessige PDF-Extraktion
ohne Fremdbibliothek gibt es nicht, und ein halb gelesener Lebenslauf
ist schlimmer als gar keiner. Bei PDF den Text im Reader markieren,
kopieren und in das Textfeld einfuegen.

Nur Standardbibliothek, Python 3.8+.
"""

import html
import io
import re
import zipfile


class NichtUnterstuetzt(Exception):
    pass


def aus_docx(rohdaten):
    with zipfile.ZipFile(io.BytesIO(rohdaten)) as z:
        if "word/document.xml" not in z.namelist():
            raise NichtUnterstuetzt("Datei ist kein lesbares Word-Dokument.")
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    xml = xml.replace("</w:p>", "\n</w:p>")
    xml = xml.replace("<w:tab/>", "\t").replace("<w:br/>", "\n")
    text = html.unescape(re.sub(r"<[^>]+>", "", xml))
    zeilen = [z.strip() for z in text.split("\n")]
    return "\n".join(z for z in zeilen if z)


def aus_datei(dateiname, rohdaten):
    name = (dateiname or "").lower()
    if name.endswith(".docx") or rohdaten[:2] == b"PK":
        return aus_docx(rohdaten)
    if name.endswith(".pdf") or rohdaten[:5] == b"%PDF-":
        raise NichtUnterstuetzt(
            "PDF wird nicht gelesen. Text im PDF-Reader markieren, kopieren "
            "und unten in das Textfeld einfuegen.")
    if name.endswith((".txt", ".md", ".text")):
        return rohdaten.decode("utf-8", errors="replace")
    if name.endswith(".doc"):
        raise NichtUnterstuetzt(
            "Altes .doc-Format wird nicht gelesen. In Word als .docx speichern "
            "oder den Text einfuegen.")
    raise NichtUnterstuetzt(
        "Format nicht erkannt. Unterstuetzt werden .docx und .txt, sonst Text einfuegen.")


def entitaeten_vorschlag(text):
    """Schlaegt Arbeitgeber- und Ortsnamen zur Pseudonymisierung vor.

    Bewusst grob und auf Recall statt Praezision getrimmt: lieber ein
    Vorschlag zu viel, den Aaron abwaehlt, als ein Klarname zu wenig, der
    den Rechner verlaesst. Die Auswahl trifft immer der Mensch.
    """
    kandidaten = set()
    rechtsformen = r"(?:GmbH(?:\s*&\s*Co\.?\s*KG)?|AG|KG|OHG|SE|e\.K\.|UG|GbR|Gruppe)"
    wort = r"[A-ZÄÖÜ][\wÄÖÜäöüß.\-]*"
    schluessel = ("Autohaus", "Porsche Zentrum", "Audi Zentrum", "Autohausgruppe",
                  "Zentrum", "Handelsgruppe", "Automobile")
    # Zeilenweise, damit kein Treffer ueber einen Zeilenumbruch hinweg entsteht.
    for zeile in (text or "").split("\n"):
        for treffer in re.findall(r"(%s(?:\s+%s){0,4}\s+%s)" % (wort, wort, rechtsformen), zeile):
            kandidaten.add(treffer.strip(" ,.|"))
        for marke in schluessel:
            for treffer in re.findall(
                    r"((?:%s\s+)?%s(?:\s+%s){0,2})" % (wort, re.escape(marke), wort), zeile):
                treffer = treffer.strip(" ,.|")
                if len(treffer) > len(marke):
                    kandidaten.add(treffer)

    # Teilstrings entfernen, die vollstaendig in einem laengeren Treffer stecken.
    sortiert = sorted(kandidaten, key=len, reverse=True)
    ergebnis = []
    for eintrag in sortiert:
        if not any(eintrag != anderer and eintrag in anderer for anderer in ergebnis):
            ergebnis.append(eintrag)
    return ergebnis[:40]
