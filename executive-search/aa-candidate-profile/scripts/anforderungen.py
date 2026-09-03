#!/usr/bin/env python3
"""Extraktion von Anforderungen aus einem schriftlichen Anforderungsprofil.

Zerlegt eine Stellenbeschreibung oder ein Anforderungsprofil des
Auftraggebers in einzelne, pruefbare Anforderungen und trennt Muss- von
Kann-Kriterien. Rein deterministisch, kein Modellaufruf.

Die Trennung in Muss und Kann ist im Executive Search der eigentliche
Hebel: ein Kandidat, der ein Kann-Kriterium reisst, ist im Rennen, einer,
der ein Muss-Kriterium reisst, nicht. Auftraggeber vermischen beides in
der Regel im selben Absatz. Wer die Liste sauber trennt, fuehrt das
Briefinggespraech.

Nur Standardbibliothek, Python 3.8+.
"""

import re

# Ueberschriften, ab denen Anforderungen stehen.
START = re.compile(
    r"(anforderung|ihr profil|ihre qualifikation|sie bringen|was sie mitbringen|"
    r"voraussetzung|wir erwarten|qualifikation|ihr hintergrund|profil des kandidaten|"
    r"das bringen sie mit|fachliche anforderung|persoenliche anforderung|"
    r"persönliche anforderung)", re.IGNORECASE)

# Ueberschriften, ab denen keine Anforderungen mehr stehen.
ENDE = re.compile(
    r"(wir bieten|ihre aufgaben|unser angebot|benefits|das bieten wir|kontakt|"
    r"ueber uns|über uns|bewerbung|ihre chance|unser kunde|das unternehmen|"
    r"ihre perspektive|vergütung|verguetung)", re.IGNORECASE)

AUFZAEHLUNG = re.compile(r"^\s*(?:[-–—•*▪·o]|\d{1,2}[.)])\s+")

# Formulierungen, die eine Anforderung auch ohne Aufzaehlungszeichen kennzeichnen.
SIGNAL = re.compile(
    r"(mindestens|mehrjährig|mehrjaehrig|langjährig|langjaehrig|erfahrung|"
    r"sie verfügen|sie verfuegen|erforderlich|voraussetzung|abgeschlossene|"
    r"nachgewiesene|fundierte|sicherer umgang|kenntnisse|bereitschaft|"
    r"führungserfahrung|fuehrungserfahrung)", re.IGNORECASE)

# Abschwaechungen kennzeichnen ein Kann-Kriterium.
KANN = re.compile(
    r"(wünschenswert|wuenschenswert|von vorteil|idealerweise|vorteilhaft|"
    r"gerne|optional|plus\b|nice to have|bevorzugt|gern gesehen)", re.IGNORECASE)

RAUSCHEN = re.compile(
    r"^(m/w/d|w/m/d|d/m/w|seite \d|www\.|https?://|tel\.|e-?mail)", re.IGNORECASE)


def _saeubern(zeile):
    text = AUFZAEHLUNG.sub("", zeile).strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ;,.-–—•*")


def extrahiere(text):
    """Liefert eine Liste von {"anforderung", "gewichtung"} in Reihenfolge.

    gewichtung ist "muss" oder "kann". Die Zuordnung ist eine Heuristik
    ueber Signalwoerter und deshalb zu pruefen, nicht zu glauben.
    """
    zeilen = [z.rstrip() for z in (text or "").split("\n")]

    # Vorlauf: gibt es ueberhaupt eine Anforderungs-Ueberschrift? Wenn ja,
    # zaehlen nur Zeilen aus diesem Abschnitt. Sonst wuerden die Bullets aus
    # "Ihre Aufgaben" oder "Wir bieten" als Anforderungen mitgelesen.
    abschnitt_gefunden = any(
        len(z.strip()) < 70 and not z.strip().endswith((".", ";")) and START.search(z)
        for z in zeilen if z.strip())

    im_abschnitt = False
    treffer = []

    for zeile in zeilen:
        blank = zeile.strip()
        if not blank:
            continue
        if RAUSCHEN.match(blank):
            continue
        # Kurze Zeile ohne Satzzeichen ist vermutlich eine Ueberschrift.
        ist_ueberschrift = len(blank) < 70 and not blank.endswith((".", ";"))
        if ist_ueberschrift and START.search(blank):
            im_abschnitt = True
            continue
        if ist_ueberschrift and ENDE.search(blank):
            im_abschnitt = False
            continue
        if im_abschnitt or (not abschnitt_gefunden and AUFZAEHLUNG.match(zeile)):
            sauber = _saeubern(zeile)
            if len(sauber) >= 12:
                treffer.append(sauber)

    if not treffer:
        # Kein Abschnitt, keine Aufzaehlung: auf Signalsaetze zurueckfallen.
        for zeile in zeilen:
            for satz in re.split(r"(?<=[.;])\s+", zeile):
                sauber = _saeubern(satz)
                if len(sauber) >= 20 and SIGNAL.search(sauber):
                    treffer.append(sauber)

    gesehen, ergebnis = set(), []
    for eintrag in treffer:
        schluessel = eintrag.lower()
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        ergebnis.append({
            "anforderung": eintrag[:300],
            "gewichtung": "kann" if KANN.search(eintrag) else "muss",
        })
    return ergebnis, abschnitt_gefunden


def als_passung(anforderungen):
    """Baut das Passungsgeruest fuer den Steckbrief, Status noch offen."""
    return [{"anforderung": a["anforderung"], "gewichtung": a["gewichtung"],
             "status": "", "beleg": ""} for a in anforderungen]
