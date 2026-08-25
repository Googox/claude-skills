#!/usr/bin/env python3
"""
formularfelder.py — wandelt die Platzhalter aus build_word_formular.js in echte
Word-Formularfelder um und aktiviert den Formularschutz.

  @@T|name@@  ->  FORMTEXT      (Texteingabefeld in einer Tabellenzelle)
  @@U|name@@  ->  FORMTEXT      (Inline-Feld im Fliesstext, unterstrichen)
  @@C|name@@  ->  FORMCHECKBOX  (anklickbares Kontrollkaestchen)

Zusaetzlich wird word/settings.xml mit
<w:documentProtection w:edit="forms" w:enforcement="1"/> angelegt: Word laesst
dann nur noch die Formularfelder bearbeiten, Layout und Text sind gesperrt.

Aufruf:  python3 formularfelder.py <eingabe.docx> [ausgabe.docx]
"""

import re
import shutil
import sys
import zipfile

MARKER = re.compile(r'@@([TCU])\|([A-Za-z0-9]+)@@')

SETTINGS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:documentProtection w:edit="forms" w:enforcement="1" w:formatting="0"/>'
    '<w:defaultTabStop w:val="708"/>'
    '<w:characterSpacingControl w:val="doNotCompress"/>'
    '</w:settings>'
)
SETTINGS_CT = ('<Override PartName="/word/settings.xml" ContentType="application/'
               'vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>')
SETTINGS_REL = ('<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/settings" Target="settings.xml"/>')


def ffdata(name, inhalt):
    return (f'<w:ffData><w:name w:val="{name}"/><w:enabled/>'
            f'<w:calcOnExit w:val="0"/>{inhalt}</w:ffData>')


def mit_unterstrich(rpr):
    """Haengt <w:u> an die Zeichenformatierung an. Schema-Reihenfolge: u kommt
    nach sz/szCs, also ans Ende von rPr."""
    if not rpr:
        return '<w:rPr><w:u w:val="single"/></w:rPr>'
    return rpr.replace('</w:rPr>', '<w:u w:val="single"/></w:rPr>')


def formtext(name, rpr, unterstrichen=False):
    # Das Ergebnisfeld traegt den Unterstrich, damit ein Inline-Feld im
    # Fliesstext als Ausfuellstelle sichtbar ist.
    rpr_anzeige = mit_unterstrich(rpr) if unterstrichen else rpr
    platzhalter = ' ' * (16 if unterstrichen else 5)
    return (
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin">'
        f'{ffdata(name, "<w:textInput/>")}</w:fldChar></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> FORMTEXT </w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{rpr_anzeige}<w:t xml:space="preserve">{platzhalter}</w:t></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def formcheckbox(name, rpr):
    box = '<w:checkBox><w:sizeAuto/><w:default w:val="0"/></w:checkBox>'
    return (
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin">'
        f'{ffdata(name, box)}</w:fldChar></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> FORMCHECKBOX </w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def ersetze_marker(xml):
    """Ersetzt jeden Marker samt umschliessendem <w:r> durch das Feld-XML."""
    anzahl = {"T": 0, "U": 0, "C": 0}
    namen = []
    while True:
        m = MARKER.search(xml)
        if not m:
            break
        art, name = m.group(1), m.group(2)

        start = xml.rfind('<w:r>', 0, m.start())
        ende = xml.find('</w:r>', m.end())
        if start == -1 or ende == -1:
            raise SystemExit(f"Marker {name} liegt nicht in einem <w:r>-Element")
        ende += len('</w:r>')
        original = xml[start:ende]

        rpr_m = re.search(r'<w:rPr>.*?</w:rPr>', original, re.S)
        rpr = rpr_m.group(0) if rpr_m else ''

        if art == 'C':
            feld = formcheckbox(name, rpr)
        else:
            feld = formtext(name, rpr, unterstrichen=(art == 'U'))
        xml = xml[:start] + feld + xml[ende:]
        anzahl[art] += 1
        namen.append(name)

    if len(namen) != len(set(namen)):
        doppelt = sorted({n for n in namen if namen.count(n) > 1})
        raise SystemExit(f"Doppelte Feldnamen: {', '.join(doppelt)}")
    return xml, anzahl


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    quelle = sys.argv[1]
    ziel = sys.argv[2] if len(sys.argv) > 2 else quelle

    with zipfile.ZipFile(quelle) as zin:
        teile = {n: zin.read(n) for n in zin.namelist()}

    doc = teile['word/document.xml'].decode('utf-8')
    doc, anzahl = ersetze_marker(doc)
    teile['word/document.xml'] = doc.encode('utf-8')

    # settings.xml anlegen und verknuepfen
    teile['word/settings.xml'] = SETTINGS.encode('utf-8')

    ct = teile['[Content_Types].xml'].decode('utf-8')
    if 'word/settings.xml' not in ct:
        ct = ct.replace('</Types>', SETTINGS_CT + '</Types>')
    teile['[Content_Types].xml'] = ct.encode('utf-8')

    rels = teile['word/_rels/document.xml.rels'].decode('utf-8')
    if 'settings.xml' not in rels:
        rels = rels.replace('</Relationships>', SETTINGS_REL + '</Relationships>')
    teile['word/_rels/document.xml.rels'] = rels.encode('utf-8')

    if ziel == quelle:
        shutil.copyfile(quelle, quelle + '.bak')
    with zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, daten in teile.items():
            zout.writestr(name, daten)

    print(f"{anzahl['T'] + anzahl['U']} Textfelder "
          f"(davon {anzahl['U']} inline unterstrichen), "
          f"{anzahl['C']} Kontrollkaestchen, Formularschutz aktiv -> {ziel}")


if __name__ == '__main__':
    main()
