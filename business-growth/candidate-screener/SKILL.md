---
name: candidate-screener
description: Erzeugt Suchstrings (Google X-Ray, LinkedIn, Xing) fuer Verkaufsleiter, Geschaeftsfuehrer und Vorstaende bei Audi, BMW und Mercedes Autohaeusern und fuehrt ein DSGVO-bewusstes Kandidaten-Tracking als CSV
---

# Candidate Screener

Recherche-Beschleuniger fuer die Direktansprache im Premium-Automobilhandel DACH. Kein Scraping, keine Netzwerkzugriffe, nur Python-Standardbibliothek.

## Workflow
1. **Suchstrings erzeugen:** `python scripts/candidate_screener.py queries --plz 80331 --radius 50 --orte "Muenchen,Augsburg" --marken audi,bmw,mercedes --rollen verkaufsleiter,geschaeftsfuehrer`
2. **Manuell ausfuehren** (Google, LinkedIn Recruiter/Sales Navigator, Xing). Umkreis ueber das Plattform-Filterfeld (PLZ + km) oder `--orte`.
3. **Kandidaten erfassen:** `add --name ... --quelle "LinkedIn-Profil" --punkte 2,2,1,1`
4. **Nachfassen:** `update 1 --status kontaktiert --followup 2026-12-08`, taeglich `due`.

## Regions-Vorlagen
`--region hamburg` oder `--region lueneburg` setzt PLZ, Radius und Orte (ueberschreibbar). Weitere Regionen im Dict `REGIONEN` im Skript ergaenzen.

## Fit-Score
Vier Kriterien je 0 bis 2 Punkte: Markenerfahrung (Premium), Verantwortungsumfang, Wechselsignal (Uebernahme, Umstrukturierung, Neubesetzung), Erreichbarkeit. Summe 6+ = A, 4-5 = B, sonst C.

## Status
neu, kontaktiert, gespraech, vorgestellt, absage, platziert

## Referenzen
- `references/compliance.md`
- `assets/outreach_templates.md`

Tracking-Datei: `kandidaten_tracking.csv` im aktuellen Verzeichnis (`--file` aendert den Pfad). Enthaelt personenbezogene Daten: nicht ins Repo committen.
