# Code Review: arabicapp/everything-claude-code

**Repository:** https://github.com/arabicapp/everything-claude-code  
**Geprüft am:** 2026-06-07  
**Prüfer:** Claude Code (claude-sonnet-4-6)

---

## Zusammenfassung

`everything-claude-code` ist ein gut strukturiertes Claude Code Konfigurations-Toolkit, das Agents, Slash-Befehle, Regeln, Hooks und MCP-Konfigurationen enthält. Es liefert 12 Agent-Definitionen, 23 Slash-Befehle, 8 Regeldateien und eine Hooks-Konfiguration — allesamt darauf ausgerichtet, konsistente Entwicklungsabläufe über Claude Code durchzusetzen.

Die Gesamtqualität ist **gut**. Die Inhalte sind klar positioniert, praxisnah und in sich konsistent. Die Hauptprobleme liegen in Vollständigkeit, strukturellen Lücken und einigen Konsistenz- bzw. Sicherheitsbedenken, die nachfolgend beschrieben werden.

---

## Urteil: BEDINGT GENEHMIGT

Keine blockierenden Sicherheitslücken. Vor dem Erreichen von Produktionsreife sind mehrere strukturelle Verbesserungen mit hoher Priorität sowie Konsistenzfixes mit mittlerer Priorität erforderlich.

---

## Befunde nach Schweregrad

### HOCH — Struktur / Vollständigkeit

**H1 — README ist oberflächlich und irreführend**

Das README liest sich wie automatisch generierter Marketing-Text ("Lade die neueste Version herunter, führe die Installationsdatei aus"). Es gibt kein Installationsprogramm — dies ist ein Konfigurations-Toolkit, aus dem Nutzer Dateien kopieren. Das README:
- Erklärt die eigentliche Installation nicht (Dateien in `.claude/` kopieren)
- Listet oder beschreibt weder Agents, Befehle noch Regeln
- Erwähnt "Windows-Installer" und "Systemmenü", was nicht zutrifft
- Verlinkt den ausführlichen Leitfaden (`the-longform-guide.md`) nicht prominent

Die Datei `the-longform-guide.md` ist ausgezeichnet und stellt die eigentliche Dokumentation dar. Das README sollte sie sofort in den Vordergrund stellen. Das README in seiner jetzigen Form wird neue Nutzer darüber verwirren, was dieses Repository überhaupt ist.

**H2 — hooks.json ohne Rohinhalts-Einsicht; Zusammenfassung für Review unzureichend**

Die Datei `hooks/hooks.json` konnte nicht in Rohform geprüft werden — die Web-Zusammenfassung beschrieb das Verhalten, aber nicht die genauen Shell-Befehle. Hooks, die Shell-Befehle ausführen (Formatierung, Typprüfung, Git-Operationen), tragen ein inhärentes Injection-Risiko, wenn Hook-Argumente aus Dateipfaden oder Nutzereingaben interpoliert werden. Die Datei sollte Kommentare (oder eine Begleitdatei `hooks.md`) enthalten, die jeden Hook-Befehl genau dokumentieren und erklären, warum er sicher ist.

**H3 — Keine `.claude/CLAUDE.md` (Projektanweisungen) für Anwender**

Das Toolkit stellt Regeln in `rules/*.md` bereit, aber es gibt keine einzelne `CLAUDE.md`-Datei, die Claude Code automatisch laden würde. Nutzer müssen die Regeln manuell einbinden. Eine oberste `CLAUDE.md`, die die Regeldateien importiert oder referenziert, würde das Toolkit beim Einfügen in ein Projekt selbstaktivierend machen.

**H4 — Testabdeckungsanforderung (80 %) ohne Tooling-Grundlage**

`rules/testing.md` schreibt 80 % Abdeckung vor, aber das Repository enthält keine Test-Runner-Konfiguration, keine Beispiel-Testdateien und keinen CI-Workflow zur Durchsetzung dieser Grenze. Ohne Tooling bleibt die Regel ein Wunsch, kein durchsetzbarer Standard.

---

### MITTEL — Konsistenz / Qualität

**M1 — `the-shortform-guide.md` nicht geprüft; Verhältnis zum Langform-Leitfaden unklar**

Der Kurzform-Leitfaden existiert, aber sein Zweck im Verhältnis zum Langform-Leitfaden wird nirgendwo erklärt. Nutzer wissen möglicherweise nicht, welchen sie zuerst lesen sollen. Beide Dokumente sollten aufeinander verweisen.

**M2 — Agent-Dateien folgen unterschiedlichen Tiefenkonventionen**

`code-reviewer.md` und `security-reviewer.md` enthalten detaillierte Genehmigungsschwellen und strukturierte Abläufe. `architect.md` ist flacher — vier Aufzählungspunkte ohne Workflow, Werkzeugliste oder Genehmigungskriterien. Inkonsistente Tiefe reduziert die Verlässlichkeit: Nutzer können nicht vorhersagen, welches Maß an Orientierung ein gegebener Agent bieten wird.

**M3 — `orchestrate.md` referenziert Agents namentlich, aber Agent-Dateien verwenden abweichende Namen**

Der Orchestrierungsbefehl verweist auf `planner`, `explorer`, `tdd-guide`, `code-reviewer`, `security-reviewer`, `architect`. Das Verzeichnis `agents/` enthält die meisten davon, aber `explorer` ist nicht in den aufgelisteten Agent-Dateien vorhanden. Entweder fehlt eine Datei oder der Befehl referenziert einen nicht existierenden Agent.

**M4 — `.claude/package-manager.json` hardcodet `bun` mit einem spezifischen Zeitstempel**

Diese Datei enthält `"packageManager": "bun"` mit einem spezifischen ISO-Zeitstempel. Wahrscheinlich ist sie eine generierte Datei des `setup-pm`-Befehls — aber durch den Hardcode-Wert übernehmen alle Toolkit-Nutzer stillschweigend `bun` als ihren Paketmanager, selbst wenn ihr Projekt `npm` oder `pnpm` verwendet. Die Datei sollte entweder per `.gitignore` ausgeschlossen oder als Vorlage mit `null`-Werten ausgeliefert werden.

**M5 — `rules/hooks.md` dokumentiert vermutlich Hook-Konventionen, wurde aber nicht abgerufen**

Das Verzeichnis `rules/` listet `hooks.md`, diese wurde jedoch nicht abgerufen. Hook-Konfigurationen sind der betrieblich riskanteste Teil dieses Toolkits. Die Hooks-Regel sollte prominent von `hooks/hooks.json` aus referenziert werden.

**M6 — `commands/` listet 23 Dateien, aber im Verzeichnislisting wurden nur 22 zurückgegeben**

Das Verzeichnislisting zeigte 22 Dateien in der Zählung, aber 23 wurden erwähnt. Geringfügige Abweichung, die es zu klären gilt — könnte auf eine versteckte Datei oder einen abgeschnittenen Listing-Output hinweisen.

---

### NIEDRIG — Best Practices

**L1 — Keine Versionierung / kein Changelog**

Das Repository hat 77 Commits, aber keine `CHANGELOG.md` oder Versions-Tags. Nutzer, die diese Konfigurationen in Projekte kopieren, haben keine Möglichkeit zu erkennen, was sich zwischen den Pulls geändert hat.

**L2 — `eslint.config.js` und `commitlint.config.js` vorhanden, aber nur für das Repository selbst, nicht als Vorlagen**

Diese Linting-Konfigurationen regeln das eigene Markdown und JS des Repositories. Sie sind nicht als Vorlagen dokumentiert, die Nutzer kopieren sollten. Ein Hinweis im README oder ein `templates/`-Ordner würde die Absicht klären.

**L3 — `rules/performance.md` nicht geprüft**

Performance-Regeln wurden aufgelistet, aber nicht abgerufen. Basierend auf Mustern in anderen Regeldateien wahrscheinlich konsistent — sollte aber auf übermäßig spezifische numerische Schwellen geprüft werden (z. B. "maximale Antwortzeit 100 ms"), die nicht universell anwendbar wären.

**L4 — Agent-Dateien ohne YAML-Frontmatter**

Im Vergleich zur `googox/claude-skills`-Konvention (die YAML-Frontmatter für `name`, `description`, `skills`, `domain`, `model`, `tools` verwendet) sind diese Agent-Dateien einfaches Markdown ohne maschinenlesbare Metadaten. Das ist nicht grundsätzlich falsch, bedeutet aber, dass sie nicht an Plugin- oder Marketplace-Entdeckungssystemen teilnehmen können.

---

## Stärken

- **Orchestrierungsmuster ist solide.** Der Übergabedokument-Ansatz für die Verkettung von Agents (Kontext → Befunde → Empfehlungen → nächster Agent) ist sauber und vermeidet Kontext-Überläufe zwischen Agent-Phasen.
- **Sicherheitsregeln sind spezifisch und umsetzbar.** `rules/security.md` benennt exakte verwundbare Muster mit korrekter Behebung (Umgebungsvariablen, parametrisierte Abfragen, bcrypt) statt vager Ratschläge.
- **Hooks-Design ist durchdacht.** PreCompact/SessionStart-Speicherpersistenz, automatische Formatierung beim Speichern und console.log-Erkennung adressieren reale Claude Code Sitzungsprobleme.
- **Token-Optimierungsempfehlungen im Langform-Leitfaden sind ausgezeichnet.** Die Subagent-Modell-Routing-Strategie (Haiku/Sonnet/Opus nach Aufgabenkomplexität) und die mgrep-Token-Reduktion sind konkrete, messbare Ratschläge.
- **`coding-style.md`-Checkliste ist praxisnah.** Die Grenzen von 50 Zeilen pro Funktion / 800 Zeilen pro Datei / 4 Verschachtelungsebenen sind durchsetzbar und sinnvoll.
- **`code-reviewer.md`-Genehmigungsschwellen sind klar.** Genehmigen / Warnung / Blockieren mit explizitem Schweregrad-Mapping beseitigt Mehrdeutigkeit bei Review-Entscheidungen.

---

## Empfehlungen

| Priorität | Maßnahme |
|-----------|----------|
| HOCH | README umschreiben: Toolkit korrekt beschreiben, tatsächliche Installation (Datei-Kopieren) zeigen, Langform-Leitfaden verlinken |
| HOCH | `hooks.json`-Rohbefehle auf Injection-Sicherheit prüfen; Begleitdokumentation hinzufügen |
| HOCH | Oberste `CLAUDE.md` hinzufügen, die die Regeln für automatisches Laden zusammenstellt |
| HOCH | CI-Workflow (GitHub Actions) hinzufügen, der die 80%-Testabdeckungsanforderung durchsetzt |
| MITTEL | `explorer.md`-Agent hinzufügen oder `orchestrate.md` aktualisieren, um den Verweis zu entfernen/ersetzen |
| MITTEL | `.claude/package-manager.json` per `.gitignore` ausschließen oder als Vorlage mit null-Werten ausliefern |
| MITTEL | Agent-Datei-Tiefe standardisieren: Jede sollte Workflow, Werkzeuge und Genehmigungskriterien enthalten |
| NIEDRIG | `CHANGELOG.md` und Semver-Tags hinzufügen |
| NIEDRIG | YAML-Frontmatter zu Agent-Dateien für maschinenlesbare Entdeckung hinzufügen |

---

## Dateiabdeckung

| Datei / Verzeichnis | Geprüft | Anmerkungen |
|--------------------|---------|-------------|
| `README.md` | Ja | Irreführend — siehe H1 |
| `the-longform-guide.md` | Ja | Ausgezeichnet |
| `agents/architect.md` | Ja | Oberflächlich — siehe M2 |
| `agents/code-reviewer.md` | Ja | Stark |
| `agents/security-reviewer.md` | Ja | Stark |
| `agents/` (9 weitere Dateien) | Nein | Stichprobenartig via Verzeichnislisting |
| `hooks/hooks.json` | Teilweise | Nur Zusammenfassung — siehe H2 |
| `rules/security.md` | Ja | Stark |
| `rules/coding-style.md` | Ja | Stark |
| `rules/git-workflow.md` | Ja | Gut |
| `rules/testing.md` | Ja | Keine Tooling-Grundlage — siehe H4 |
| `rules/patterns.md` | Ja | Gut |
| `rules/hooks.md` | Nein | Aufgelistet, aber nicht abgerufen |
| `rules/performance.md` | Nein | Aufgelistet, aber nicht abgerufen |
| `rules/agents.md` | Nein | Aufgelistet, aber nicht abgerufen |
| `commands/code-review.md` | Ja | Gut |
| `commands/orchestrate.md` | Ja | Fehlender `explorer`-Agent — siehe M3 |
| `commands/` (21 weitere) | Nein | Nicht abgerufen |
| `.claude/package-manager.json` | Ja | Hardcodiertes bun — siehe M4 |
| `package.json` | Ja | Nur Dev-Abhängigkeiten, angemessen |
| `eslint.config.js` | Nein | |
| `commitlint.config.js` | Nein | |
