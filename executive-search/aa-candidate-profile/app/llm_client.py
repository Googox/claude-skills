#!/usr/bin/env python3
"""Optionaler API-Aufruf fuer die Textstufe, mit harter Klartextsperre.

Der Aufruf ist optional. Ohne API-Schluessel arbeitet die App im
Zwischenablage-Modus: sie erzeugt den pseudonymisierten Prompt, Aaron
fuegt ihn in seine Claude-Oberflaeche ein und die Antwort zurueck.

Sicherheitsregel dieses Moduls: es verlaesst kein Text den Rechner, in
dem die Rueckstandspruefung noch Klartext findet. Der Aufruf bricht in
dem Fall ab, statt zu warnen.

Nur Standardbibliothek, Python 3.8+.
"""

import json
import os
import urllib.error
import urllib.request

from pseudonymize import restbestand

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
STANDARD_MODELL = "claude-opus-5"


class KlartextGefunden(Exception):
    """Abbruch: der Text enthaelt noch personenbeziehbaren Klartext."""


def schluessel_lesen(konfig_pfad):
    """Liest den API-Schluessel aus Umgebungsvariable oder lokaler Datei."""
    aus_umgebung = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if aus_umgebung:
        return aus_umgebung
    try:
        with open(konfig_pfad, "r", encoding="utf-8") as handle:
            return json.load(handle).get("api_key", "").strip()
    except (OSError, ValueError):
        return ""


def frage(prompt, api_key, modell=STANDARD_MODELL, max_tokens=8000,
          kandidat_name="", arbeitgeber=None, orte=None, ausnahmen=None, timeout=180):
    """Schickt den pseudonymisierten Prompt an die API und liefert den Text."""
    funde = restbestand(prompt, kandidat_name, arbeitgeber, orte, ausnahmen)
    if funde:
        raise KlartextGefunden(
            "Abbruch vor dem Versand. Im Prompt steht noch Klartext: %s"
            % ", ".join(funde[:10]))
    if not api_key:
        raise ValueError("Kein API-Schluessel hinterlegt.")

    rumpf = json.dumps({
        "model": modell,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    anfrage = urllib.request.Request(
        API_URL, data=rumpf, method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
        })
    try:
        with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
            daten = json.loads(antwort.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError("API-Fehler %s: %s" % (err.code, detail))
    except urllib.error.URLError as err:
        raise RuntimeError("Keine Verbindung zur API: %s" % err.reason)

    teile = [b.get("text", "") for b in daten.get("content", []) if b.get("type") == "text"]
    return "".join(teile)
