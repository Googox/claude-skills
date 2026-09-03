#!/usr/bin/env python3
"""Minimaler PDF-Schreiber ohne externe Abhaengigkeiten.

Erzeugt ein A4-Dokument mit den drei Standardschriften Helvetica,
Helvetica-Bold und Helvetica-Oblique, mit Wortumbruch, Seitenumbruch und
einer Fusszeile auf jeder Seite.

Bewusst schmal: Text, Ueberschriften, Fusszeile. Ein Steckbrief braucht
nichts weiter. Kein Bild, keine Tabelle, keine eingebettete Schrift.
Damit laeuft der Export auf jedem Rechner ohne Installation und ohne
Word, und das Ergebnis ist auf jedem Rechner identisch.

Nur Standardbibliothek, Python 3.8+.
"""

import re
import zlib

A4 = (595.28, 841.89)
RAND = 56.0

# Zeichenbreiten der Standardschrift Helvetica in 1/1000 em, Bereich 32 bis 126.
_H = (
    "278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556 "
    "1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556 "
    "333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 "
    "556 556 333 500 278 556 500 722 500 500 500 334 260 334 584")
_HB = (
    "278 333 474 556 556 889 722 238 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 333 333 584 584 584 611 "
    "975 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 333 278 333 584 556 "
    "333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611 "
    "611 611 389 556 333 611 556 778 556 556 500 389 280 389 584")

BREITEN = {
    "F1": [int(x) for x in _H.split()],
    "F3": [int(x) for x in _H.split()],
    "F2": [int(x) for x in _HB.split()],
}

# Akzentbuchstaben haben in den Standardschriften dieselbe Laufweite wie
# ihr Grundbuchstabe. Die Zuordnung reicht damit fuer exakte Breiten.
FALTUNG = {
    "ä": "a", "ö": "o", "ü": "u", "Ä": "A", "Ö": "O", "Ü": "U", "ß": "s",
    "á": "a", "à": "a", "â": "a", "é": "e", "è": "e", "ê": "e", "í": "i",
    "ì": "i", "î": "i", "ó": "o", "ò": "o", "ô": "o", "ú": "u", "ù": "u",
    "û": "u", "ç": "c", "ñ": "n", "É": "E", "È": "E", "Á": "A", "Ó": "O",
    "€": "C", "„": '"', "“": '"', "”": '"', "‚": "'", "‘": "'", "’": "'",
    "–": "-", "—": "-", "…": ".",
}

LUECKE = re.compile(r"\[\[(.+?)\]\]", re.DOTALL)

STILE = {
    "titel": ("F2", 16.0, 0.0),
    "block": ("F2", 11.5, 14.0),
    "text": ("F1", 9.8, 3.0),
    "klein": ("F1", 8.2, 3.0),
}


def _breite(text, font, groesse):
    tabelle = BREITEN[font]
    summe = 0
    for zeichen in text:
        zeichen = FALTUNG.get(zeichen, zeichen)
        index = ord(zeichen) - 32
        summe += tabelle[index] if 0 <= index < len(tabelle) else 556
    return summe * groesse / 1000.0


def _kodiere(text):
    """WinAnsi-tauglich machen und PDF-Sonderzeichen maskieren."""
    sauber = "".join(FALTUNG.get(c, c) if ord(c) > 255 else c for c in text)
    roh = sauber.encode("cp1252", errors="replace").decode("cp1252")
    return roh.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _umbrechen(text, font, groesse, breite):
    zeilen = []
    for absatz in text.split("\n"):
        worte = absatz.split()
        if not worte:
            zeilen.append("")
            continue
        aktuell = worte[0]
        for wort in worte[1:]:
            if _breite(aktuell + " " + wort, font, groesse) <= breite:
                aktuell += " " + wort
            else:
                zeilen.append(aktuell)
                aktuell = wort
        zeilen.append(aktuell)
    return zeilen


def _segmente(text):
    """Trennt offene Felder [[...]] vom Fliesstext, damit sie kursiv erscheinen."""
    teile, pos = [], 0
    for treffer in LUECKE.finditer(text):
        if treffer.start() > pos:
            teile.append((text[pos:treffer.start()], False))
        teile.append((treffer.group(1), True))
        pos = treffer.end()
    if pos < len(text):
        teile.append((text[pos:], False))
    return teile or [(text, False)]


def _seiten_aufbauen(absaetze, breite, hoehe_nutzbar):
    """Verteilt die Absaetze auf Seiten. Liefert Listen von Zeichenbefehlen."""
    seiten, aktuell, y = [], [], 0.0
    for eintrag in absaetze:
        text, art = (eintrag if isinstance(eintrag, (tuple, list)) else (eintrag, "text"))
        font, groesse, davor = STILE.get(art, STILE["text"])
        zeilenhoehe = groesse * 1.35
        roh = "".join(t for t, _ in _segmente(str(text)))
        kursiv = any(k for _, k in _segmente(str(text)))
        zeilen = _umbrechen(roh, font, groesse, breite)

        if y + davor + zeilenhoehe * len(zeilen) > hoehe_nutzbar and aktuell:
            if y + davor + zeilenhoehe * 2 > hoehe_nutzbar:
                seiten.append(aktuell)
                aktuell, y = [], 0.0
        y += davor
        for zeile in zeilen:
            if y + zeilenhoehe > hoehe_nutzbar:
                seiten.append(aktuell)
                aktuell, y = [], 0.0
            aktuell.append((zeile, "F3" if kursiv and font == "F1" else font, groesse, y))
            y += zeilenhoehe
    if aktuell:
        seiten.append(aktuell)
    return seiten


def schreibe_pdf(pfad, absaetze, fusszeile="", entwurf=False):
    breite_seite, hoehe_seite = A4
    breite = breite_seite - 2 * RAND
    hoehe_nutzbar = hoehe_seite - 2 * RAND - 24.0
    seiten = _seiten_aufbauen(absaetze, breite, hoehe_nutzbar) or [[]]

    streams = []
    for nummer, seite in enumerate(seiten, start=1):
        befehle = ["BT"]
        for zeile, font, groesse, y in seite:
            befehle.append("/%s %.2f Tf" % (font, groesse))
            befehle.append("1 0 0 1 %.2f %.2f Tm" % (RAND, hoehe_seite - RAND - y - groesse))
            befehle.append("(%s) Tj" % _kodiere(zeile))
        befehle.append("ET")

        text_fuss = "%s%s     Seite %d von %d" % (
            "ENTWURF, nicht freigegeben.     " if entwurf else "", fusszeile, nummer, len(seiten))
        befehle += [
            "0.35 0.35 0.35 rg", "BT", "/F1 7.5 Tf",
            "1 0 0 1 %.2f %.2f Tm" % (RAND, RAND - 14.0),
            "(%s) Tj" % _kodiere(text_fuss), "ET", "0 0 0 rg",
            "0.8 0.8 0.8 RG 0.5 w",
            "%.2f %.2f m %.2f %.2f l S" % (RAND, RAND - 4.0, breite_seite - RAND, RAND - 4.0),
        ]
        streams.append(zlib.compress("\n".join(befehle).encode("cp1252", errors="replace")))

    objekte = []

    def obj(inhalt):
        objekte.append(inhalt)
        return len(objekte)

    schrift_ids = {}
    for kuerzel, basis in (("F1", "Helvetica"), ("F2", "Helvetica-Bold"),
                           ("F3", "Helvetica-Oblique")):
        schrift_ids[kuerzel] = obj(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>"
            % basis.encode())

    inhalt_ids = [obj(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(s)
                      + s + b"\nendstream") for s in streams]

    seiten_id = len(objekte) + len(streams) + 1
    seiten_ids = []
    ressourcen = b"/Font << " + b" ".join(
        b"/%s %d 0 R" % (k.encode(), v) for k, v in schrift_ids.items()) + b" >>"
    for inhalt_id in inhalt_ids:
        seiten_ids.append(obj(
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] /Resources << %s >> "
            b"/Contents %d 0 R >>" % (seiten_id, breite_seite, hoehe_seite,
                                      ressourcen, inhalt_id)))
    baum_id = obj(b"<< /Type /Pages /Kids [%s] /Count %d >>" % (
        b" ".join(b"%d 0 R" % i for i in seiten_ids), len(seiten_ids)))
    katalog_id = obj(b"<< /Type /Catalog /Pages %d 0 R >>" % baum_id)

    ausgabe = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    versatz = []
    for nummer, inhalt in enumerate(objekte, start=1):
        versatz.append(len(ausgabe))
        ausgabe += b"%d 0 obj\n" % nummer + inhalt + b"\nendobj\n"
    start_xref = len(ausgabe)
    ausgabe += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objekte) + 1)
    for stelle in versatz:
        ausgabe += b"%010d 00000 n \n" % stelle
    ausgabe += (b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objekte) + 1, katalog_id, start_xref))

    with open(pfad, "wb") as handle:
        handle.write(bytes(ausgabe))
    return pfad


def steckbrief_zu_absaetzen(text):
    """Wandelt den Blocktext aus steckbrief_build.render in PDF-Absaetze."""
    absaetze = []
    for zeile in (text or "").split("\n"):
        roh = zeile.rstrip()
        if not roh:
            continue
        if roh == "Kandidaten-Steckbrief":
            absaetze.append((roh, "titel"))
        elif roh.startswith("Block ") and "," in roh[:12]:
            absaetze.append((roh.split(", ", 1)[1], "block"))
        elif roh.startswith("Vertraulich."):
            absaetze.append((roh, "klein"))
        else:
            absaetze.append((roh, "text"))
    return absaetze
