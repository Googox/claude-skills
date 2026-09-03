# Executive Search Skills

Domänenleitfaden für Claude Code beim Arbeiten im Ordner `executive-search/`.

## Zweck

Skills für die Arbeit eines selbstständigen Executive Searchers im DACH-Raum, Schwerpunkt Premium-Automobilhandel. Die Skills bilden den Kernprozess ab: Kandidatenprofile für den beauftragenden Arbeitgeber aufbereiten, bewerten und rechtssicher übermitteln.

## Skills in dieser Domäne

| Skill | Zweck |
|-------|-------|
| aa-candidate-profile | Lebenslauf zu präsentationsfähigem Kandidaten-Steckbrief, Vollprofil oder Blindprofil, mit AGG- und DSGVO-Prüfung |

## Verhältnis zu den aa-* Skills auf Nutzerebene

Die Skills `aa-pipeline-review`, `aa-pitch-prep`, `aa-follow-up`, `aa-mandate-kickoff`, `aa-market-intelligence` und `aa-weekly-review` liegen als persönliche Skills auf Nutzerebene, nicht in diesem Repository. `aa-candidate-profile` folgt bewusst deren Konventionen, damit die Familie konsistent bleibt:

Firmenname immer "A/A Executive Search" mit Schrägstrich. Ausgabe kopierfreundlich in nummerierten Blöcken, normale Absätze, keine Trennlinien. Ehrlichkeitsregel: nichts erfinden, Unsicheres als unsicher ausweisen, ein dünneres ehrliches Ergebnis schlägt ein dickes erfundenes. Trennung: Ergebnisse dienen ausschließlich A/A Executive Search, keine Vermischung mit Alexandras separaten Geschäftsideen.

## Die Assessment-Methodik ist extern

Aarons proprietäre C-Level-Assessment-Methodik (Knock-out-Kriterien, sieben Fitness-Signale, gewichtetes Scoring null bis hundert) liegt in einem separaten A/A-Assessment-SKILL.md, das nicht Teil dieses Repositories ist. Skills in dieser Domäne dürfen diese Kriterien **niemals erfinden**. Sie laden das externe SKILL.md oder lassen den Bewertungsblock aus und weisen darauf hin.

## Konventionen beim Erweitern

Skills folgen der Repository-Struktur: `SKILL.md`, `scripts/`, `references/`, `assets/`. Python-Skripte nutzen ausschließlich die Standardbibliothek, keine LLM-Aufrufe, Python 3.8+ kompatibel, CLI-first mit `--json`-Ausgabe für Automatisierung.

Rechtliche Inhalte werden als Arbeitshilfe nach gängiger Praxis gekennzeichnet, nie als Rechtsberatung. Normen werden nur genannt, wenn sie belegbar einschlägig sind.

Personenbezogene Daten: Beispieldaten in `assets/` sind immer fiktiv und als fiktiv gekennzeichnet. Keine realen Kandidatendaten in das Repository.

## Commit-Scope

`feat(executive-search): ...`
