#!/usr/bin/env python3
"""Create the A/A Executive Search vault skeleton for Obsidian.

Builds two separate vaults, per the data model in
documentation/implementation/obsidian-vault-datenmodell.md:

  AA-Search/       connected via MCP, model-visible
  AA-Vertraulich/  never connected, holds confidentially disclosed data

Never overwrites an existing file. Re-running it is safe and only fills gaps.

Usage:
    python3 setup-obsidian-vault.py ~/Obsidian
    python3 setup-obsidian-vault.py ~/Obsidian --dry-run
    python3 setup-obsidian-vault.py ~/Obsidian --mit-pitch-geruest
"""

import argparse
import os
import sys

OPEN_VAULT = "AA-Search"
CONF_VAULT = "AA-Vertraulich"

FOLDERS = ["00-Steuerung", "10-Kontakte", "20-Arbeitgeber", "30-Mandate",
           "40-Ereignisse", "50-Markt", "80-Vorlagen", "90-Playbooks"]

T_KONTAKT = """---
typ: kontakt
geschaeft: aa
rolle_fuer_aa: [kandidat]
status: aktiv
temperatur: kalt
welle: kern
pipeline_rang:
unternehmen:
position:
region:
erstkontakt_am:
letzte_interaktion_am:
naechste_aktion:
naechste_aktion_am:
mandat:
assessment_score:
assessment_stand: nicht_bewertet
knockout: false
knockout_grund:
sig_ertragsmechanik:
sig_herstellerspannung:
sig_fachkraefte:
sig_entscheidung:
sig_inhaberfamilie:
sig_flaeche:
sig_transformation:
quelle:
vertraulich_ref:
---

## Profil

## Fit-Einschaetzung

## Journal

## Offene Punkte
"""

T_ARBEITGEBER = """---
typ: arbeitgeber
geschaeft: aa
status: ziel
gruppe:
marken: []
standorte:
region:
entscheider: []
bedarf_hypothese:
letzte_interaktion_am:
naechste_aktion:
naechste_aktion_am:
mandate: []
quelle:
---

## Lage

## Schmerzpunkt-Hypothesen

## Journal

## Offene Punkte
"""

T_MANDAT = """---
typ: mandat
geschaeft: aa
aktenzeichen:
mandant:
position:
fee_modell: model_a_hybrid
honorar_mindest: 15000
honorar_vereinbart:
phase: kickoff
start_am:
ziel_platzierung_am:
kandidaten: []
zahlung_status: offen
gewichtung_abweichend:
---

## Anforderungsprofil

## Suchstrategie

## Meilensteine

## Journal

## Risiken
"""

T_EREIGNIS = """---
typ: ereignis
geschaeft: aa
datum:
kanal: telefon
kontakt:
unternehmen:
mandat:
anlass:
ergebnis: neutral
temperatur_nachher:
folgeaktion:
folgeaktion_am:
---

## Notizen

## Zusagen
"""

T_MARKT = """---
typ: marktbeobachtung
geschaeft: aa
erfasst_am:
person:
unternehmen_neu:
unternehmen_alt:
rolle_neu:
anlass: wechsel
quelle:
quelle_url:
belegbar: false
relevanz: beobachten
kontakt_angelegt: false
---

## Belegte Fakten

## Fit-Einschaetzung

## Unsicherheiten
"""

PIPELINE = """---
typ: steuerung
geschaeft: aa
---

# Pipeline A/A Executive Search

Diese Seite rechnet, Claude bewertet. Voraussetzung: Community-Plugin Dataview.

## 1 Sofort dran (ueberfaellig)

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion AS "Naechste Aktion",
      (date(today) - naechste_aktion_am).days AS "Tage ueberfaellig"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND geschaeft = "aa"
  AND status != "abgesagt" AND naechste_aktion_am < date(today)
SORT naechste_aktion_am ASC
```

## 2 Diese Woche

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion AS "Naechste Aktion",
      naechste_aktion_am AS "Zieldatum"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND geschaeft = "aa"
  AND naechste_aktion_am >= date(today)
  AND naechste_aktion_am <= date(today) + dur(7 days)
SORT naechste_aktion_am ASC
```

## 3 Bestaetigte Pitch-Termine

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion_am AS "Termin",
      temperatur AS "Temperatur"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "pitch_terminiert"
SORT naechste_aktion_am ASC
```

## 4 Ruhend

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion_am AS "Naechste Beruehrung"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "ruhend"
SORT naechste_aktion_am ASC
```

## 5 Kernpipeline in gesetzter Reihenfolge

```dataview
TABLE pipeline_rang AS "Rang", temperatur AS "Temp",
      letzte_interaktion_am AS "Letzter Kontakt"
FROM "10-Kontakte"
WHERE welle = "kern" AND pipeline_rang
SORT pipeline_rang ASC
```

## Mandate nach Phase

```dataview
TABLE mandant, phase, fee_modell, ziel_platzierung_am
FROM "30-Mandate"
WHERE typ = "mandat" AND phase != "abgeschlossen"
SORT ziel_platzierung_am ASC
```

## Marktbeobachtungen, Entscheidung offen

```dataview
TABLE person, unternehmen_neu, relevanz, quelle
FROM "50-Markt"
WHERE typ = "marktbeobachtung" AND relevanz = "pipeline"
  AND kontakt_angelegt = false
SORT erfasst_am DESC
```

## Leck-Erkennung: aktiv, aber 30 Tage kein Kontakt

```dataview
TABLE unternehmen, letzte_interaktion_am, temperatur
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "aktiv"
  AND letzte_interaktion_am < date(today) - dur(30 days)
SORT letzte_interaktion_am ASC
```
"""

ZIELE = """---
typ: steuerung
geschaeft: aa
---

# Ziele A/A Executive Search

## Kernziel

Mindestens ein unterschriebener Retainer. Referenzgroesse fuer jedes
Wochenreview. Gemessen wird daran, nicht an Betriebsamkeit.

## Fee-Modelle

Model A hybrid: 5.000 Euro Start, 5.000 Euro bei Meilenstein, 25 Prozent
Erfolgshonorar, Mindesthonorar 15.000 Euro.

Model B retained.

Abweichende vertragliche Vereinbarungen schlagen diese Standardzahlen. Im
Mandat ist `honorar_vereinbart` die Wahrheit, nicht `honorar_mindest`.

## Offen

Assessment-Methodik ist noch nicht dokumentiert. Solange sie fehlt, bleiben
`assessment_score` und `knockout` in allen Kontakten leer.
"""

WOCHENREVIEW = """---
typ: steuerung
geschaeft: aa
---

# Wochenreview

Topf A ist direkte Kundenansprache und akquisewirksame Aktivitaet. Topf B ist
Infrastruktur, Tools, Konzepte, interne Bauarbeit. Dominiert Topf B, wird das
benannt.

## Journal
"""

CONF_README = """# AA-Vertraulich

Dieser Vault wird NIEMALS per MCP verbunden. Kein Claude-Client, kein
Local-REST-API-Plugin, keine Ausnahme.

Hier liegen ausschliesslich vertraulich mitgeteilte Daten: Gehaltsvorstellungen,
Wechselmotive, familiaere Lage, Einschaetzungen ueber Dritte. Alles, was aus
einem Vertrauensverhaeltnis stammt und nicht oeffentlich recherchierbar ist.

Verknuepfung zum offenen Vault nur ueber die Pseudonym-Kennung im Dateinamen
(K-0001, K-0002, ...). Der offene Vault fuehrt diese Kennung im Feld
`vertraulich_ref`. Dort steht nie ein Inhalt, immer nur die Kennung.

Pruefung vor jeder MCP-Konfiguration: Zeigt der konfigurierte Vault-Pfad auf
AA-Search? Wenn nicht, sofort korrigieren.
"""

CONF_TEMPLATE = """# K-XXXX

Zugehoeriger offener Datensatz: Feld `vertraulich_ref` dort auf diese Kennung
setzen. Keinen Klarnamen in diese Datei schreiben, wenn es vermeidbar ist.

## Verguetung

## Wechselmotiv

## Persoenliche Lage

## Einschaetzungen Dritter
"""

FILES_OPEN = {
    "00-Steuerung/Pipeline.md": PIPELINE,
    "00-Steuerung/Ziele.md": ZIELE,
    "00-Steuerung/Wochenreview.md": WOCHENREVIEW,
    "80-Vorlagen/Vorlage Kontakt.md": T_KONTAKT,
    "80-Vorlagen/Vorlage Arbeitgeber.md": T_ARBEITGEBER,
    "80-Vorlagen/Vorlage Mandat.md": T_MANDAT,
    "80-Vorlagen/Vorlage Ereignis.md": T_EREIGNIS,
    "80-Vorlagen/Vorlage Marktbeobachtung.md": T_MARKT,
}

FILES_CONF = {
    "README.md": CONF_README,
    "Personen/Vorlage Vertraulich.md": CONF_TEMPLATE,
}

# The three confirmed pitch appointments, as recorded in aa-pipeline-review.
# Surnames only: no first names are documented, so none are invented here.
PITCH = [
    ("Senger", "Scheele", "Pitch-Termin bestaetigt"),
    ("Hahn", "Reichl", "Pitch-Termin bestaetigt"),
    ("Scherer", "Scherer", "Pitch-Termin bestaetigt, vermutlich Familienunternehmen"),
]


def pitch_files():
    """Scaffolds for the three confirmed appointments, documented fields only."""
    out = {}
    for firma, person, anlass in PITCH:
        out[f"20-Arbeitgeber/{firma}.md"] = T_ARBEITGEBER.replace(
            "entscheider: []", f'entscheider: ["[[{person}]]"]'
        ).replace("status: ziel", "status: im_gespraech").replace(
            "## Offene Punkte\n",
            "## Offene Punkte\n\n- Firmierung vervollstaendigen (Rechtsform, Gruppe)\n"
            "- Marken, Standorte, Region ergaenzen\n- Quelle nachtragen\n",
        )
        out[f"10-Kontakte/{person}.md"] = T_KONTAKT.replace(
            "status: aktiv", "status: pitch_terminiert"
        ).replace("temperatur: kalt", "temperatur: warm").replace(
            "rolle_fuer_aa: [kandidat]", "rolle_fuer_aa: [entscheider]"
        ).replace("unternehmen:", f'unternehmen: "[[{firma}]]"').replace(
            "naechste_aktion:\n", f"naechste_aktion: {anlass}\n"
        ).replace(
            "## Offene Punkte\n",
            "## Offene Punkte\n\n- Vorname ergaenzen, Datei danach umbenennen "
            "nach Konvention \"Nachname, Vorname\"\n- Position ergaenzen\n"
            "- Termindatum in naechste_aktion_am setzen\n- pipeline_rang setzen\n",
        )
    return out


def write(path, content, dry):
    if os.path.exists(path):
        return "exists"
    if dry:
        return "would-create"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return "created"


def main():
    ap = argparse.ArgumentParser(description="Create the A/A Obsidian vault skeleton.")
    ap.add_argument("ziel", help="Parent directory for both vaults, e.g. ~/Obsidian")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen")
    ap.add_argument("--mit-pitch-geruest", action="store_true",
                    help="Also scaffold the three confirmed pitch appointments")
    args = ap.parse_args()

    base = os.path.abspath(os.path.expanduser(args.ziel))
    dry = args.dry_run
    if not os.path.isdir(base):
        if dry:
            print(f"[would-create] {base}")
        else:
            os.makedirs(base, exist_ok=True)
            print(f"[created] {base}")

    counts = {"created": 0, "exists": 0, "would-create": 0}

    print(f"\n{OPEN_VAULT} (MCP-verbunden)")
    for folder in FOLDERS:
        path = os.path.join(base, OPEN_VAULT, folder)
        if not os.path.isdir(path) and not dry:
            os.makedirs(path, exist_ok=True)
        print(f"  dir   {folder}")

    files = dict(FILES_OPEN)
    if args.mit_pitch_geruest:
        files.update(pitch_files())
    for rel, content in sorted(files.items()):
        state = write(os.path.join(base, OPEN_VAULT, rel), content, dry)
        counts[state] += 1
        print(f"  {state:13} {rel}")

    print(f"\n{CONF_VAULT} (NIE verbinden)")
    for rel, content in sorted(FILES_CONF.items()):
        state = write(os.path.join(base, CONF_VAULT, rel), content, dry)
        counts[state] += 1
        print(f"  {state:13} {rel}")

    print(f"\nangelegt: {counts['created']}   vorhanden: {counts['exists']}"
          f"   geplant: {counts['would-create']}")

    if dry:
        print("\nProbelauf. Nichts geschrieben. Ohne --dry-run erneut ausfuehren.")
        return 0

    print(f"""
Naechste Schritte in Obsidian, manuell:

  1. Vault oeffnen: {os.path.join(base, OPEN_VAULT)}
  2. Community-Plugin "Dataview" installieren und aktivieren.
     Ohne Dataview bleibt 00-Steuerung/Pipeline.md leer.
  3. Community-Plugin "Local REST API" (coddingtonbear) installieren,
     aktivieren, HTTP-Server unter Einstellungen aktivieren, API-Key kopieren.
  4. Zweiten Vault separat oeffnen: {os.path.join(base, CONF_VAULT)}
     Diesen Vault NICHT mit MCP verbinden.
  5. Verbindung pruefen: python3 diagnose-obsidian-mcp.py

Pruefpunkt vor jeder MCP-Konfiguration: der Vault-Pfad muss auf
{OPEN_VAULT} zeigen, nie auf {CONF_VAULT}.
""")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(130)
