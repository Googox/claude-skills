#!/usr/bin/env python3
"""Baut aus dem Artifact-Fragment eine vollstaendige, offline lauffaehige HTML-Datei.

Das Dashboard unter assets/nebenkosten-dashboard.html ist als Artifact-Seite
geschrieben und enthaelt daher kein <!doctype>, <html>, <head> oder <body>.
Der Artifact-Viewer ergaenzt diese Huelle beim Veroeffentlichen. Fuer den
Betrieb per Doppelklick auf dem eigenen Rechner muss sie mitgeliefert werden.

    python3 scripts/build-standalone.py
    python3 scripts/build-standalone.py --out ~/Dokumente/nebenkostenabrechner.html

Keine externen Abhaengigkeiten. Die erzeugte Datei laeuft ohne Internet; nur
die Schriftart wird dann nicht geladen und faellt auf die Systemschrift zurueck.
"""

import argparse
import os
import sys

HUELLE_KOPF = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{color-scheme:light dark}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif;background:#fff}
img{max-width:100%}
[hidden]{display:none!important}
</style>
</head>
<body>
"""

HUELLE_FUSS = """
</body>
</html>
"""


def main():
    hier = os.path.dirname(os.path.abspath(__file__))
    quelle_std = os.path.join(hier, "..", "assets", "nebenkosten-dashboard.html")
    ziel_std = os.path.join(hier, "..", "assets", "nebenkostenabrechner.html")

    ap = argparse.ArgumentParser(description="Standalone-HTML fuer den Offline-Betrieb bauen")
    ap.add_argument("--quelle", default=quelle_std, help="Artifact-Fragment")
    ap.add_argument("--out", default=ziel_std, help="Zieldatei")
    args = ap.parse_args()

    with open(args.quelle, encoding="utf-8") as f:
        inhalt = f.read()

    if "<!doctype" in inhalt[:200].lower():
        print("Die Quelle ist bereits eine vollstaendige HTML-Datei.", file=sys.stderr)
        return 1

    ziel = os.path.abspath(args.out)
    with open(ziel, "w", encoding="utf-8") as f:
        f.write(HUELLE_KOPF + inhalt + HUELLE_FUSS)

    groesse = os.path.getsize(ziel) / 1024
    print("Geschrieben: {} ({:.0f} KB)".format(ziel, groesse))
    print("Per Doppelklick im Browser oeffnen. Kein Server, keine Installation noetig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
