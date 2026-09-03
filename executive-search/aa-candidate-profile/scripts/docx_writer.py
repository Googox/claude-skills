#!/usr/bin/env python3
"""Minimaler DOCX-Schreiber ohne externe Abhaengigkeiten.

Erzeugt eine Word-Datei aus einer Liste von Absaetzen. Bewusst schmal
gehalten: Ueberschriften, Fliesstext, Fusszeilentext. Kein Bild, keine
Tabelle, kein Kopfbild. Ein Steckbrief braucht nichts davon.

Nur Standardbibliothek, Python 3.8+.
"""

import re
import zipfile
from xml.sax.saxutils import escape

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Absatzarten: (Schriftgroesse in halben Punkt, fett, Abstand davor in Twips)
STILE = {
    "titel": (32, True, 0),
    "untertitel": (22, False, 60),
    "block": (24, True, 320),
    "text": (20, False, 60),
    "klein": (16, False, 60),
}


# Offene Felder werden im Text als [[...]] geschrieben und im Word-Dokument
# gruen hinterlegt. So sieht man auf einen Blick, was noch zu ergaenzen ist,
# und kann direkt hineinschreiben.
LUECKE_FILL = "C6EFCE"
LUECKE = re.compile(r"\[\[(.+?)\]\]", re.DOTALL)


def _run(text, groesse, fett, luecke=False):
    if not text:
        return ""
    schatten = ('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % LUECKE_FILL) if luecke else ""
    return ('<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
            '<w:sz w:val="%d"/>%s%s%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
            % (groesse, "<w:b/>" if fett else "", "<w:i/>" if luecke else "",
               schatten, escape(text)))


def _absatz(text, art="text"):
    groesse, fett, davor = STILE.get(art, STILE["text"])
    runs = []
    for zeilennr, teil in enumerate(str(text).split("\n")):
        if zeilennr:
            runs.append("<w:r><w:br/></w:r>")
        pos = 0
        for treffer in LUECKE.finditer(teil):
            runs.append(_run(teil[pos:treffer.start()], groesse, fett))
            runs.append(_run(treffer.group(1), groesse, fett, luecke=True))
            pos = treffer.end()
        runs.append(_run(teil[pos:], groesse, fett))
    return ('<w:p><w:pPr><w:spacing w:before="%d" w:after="60" w:line="264" '
            'w:lineRule="auto"/></w:pPr>%s</w:p>' % (davor, "".join(runs)))


def schreibe_docx(pfad, absaetze):
    """absaetze: Liste von (text, art) oder reine Strings (art 'text')."""
    koerper = []
    for eintrag in absaetze:
        if isinstance(eintrag, (tuple, list)):
            koerper.append(_absatz(eintrag[0], eintrag[1] if len(eintrag) > 1 else "text"))
        else:
            koerper.append(_absatz(eintrag, "text"))

    dokument = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="%s"><w:body>%s'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>'
        '</w:sectPr></w:body></w:document>' % (W, "".join(koerper)))

    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", dokument)
    return pfad


def steckbrief_zu_absaetzen(text):
    """Wandelt den Blocktext aus steckbrief_build.render in DOCX-Absaetze."""
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
