# A/A Steckbrief-Arbeitsplatz, lokale Anwendung

Erstellt Kandidaten-Steckbriefe auf dem eigenen Rechner. Lebenslauf, Zuordnungstabelle und fertiges Profil bleiben lokal. Verlässt Text den Rechner, dann nur pseudonymisiert und nur nach bestandener Rückstandsprüfung.

## Voraussetzungen

Windows 10 oder 11 und Python 3.8 oder neuer. Beim Installieren von Python die Option "Add python.exe to PATH" anhaken. Sonst nichts. Die Anwendung nutzt ausschließlich die Python-Standardbibliothek, es wird kein Paket nachinstalliert.

## Starten

Doppelklick auf `Steckbrief-starten.bat`. Es öffnet sich ein Konsolenfenster und der Standardbrowser mit der Oberfläche. Das Konsolenfenster muss offen bleiben, solange gearbeitet wird. Beenden mit Strg+C oder Schließen des Fensters.

Alternativ in der Eingabeaufforderung: `py -3 steckbrief_app.py`. Optionen: `--port 8731` und `--kein-browser`.

## Ablauf in der Oberfläche

Schritt 1, Mandat: Position, Auftraggeber, Profil-ID, Datum, Berater und Modus eintragen. Der Modus entscheidet über Vollprofil mit Klarnamen oder anonymisiertes Blindprofil.

Schritt 2, Lebenslauf laden: .docx oder .txt auswählen, oder Text einfügen. PDF wird bewusst nicht gelesen, weil eine zuverlässige PDF-Extraktion ohne Fremdbibliothek nicht möglich ist. Bei PDF den Text im Reader kopieren und einfügen. Interviewnotizen sind optional, verbessern das Ergebnis aber deutlich.

Schritt 3, Pseudonymisieren: Kandidatenname eintragen. Die Anwendung schlägt erkannte Arbeitgeber vor, Vorschläge lassen sich per Klick abwählen. Weitere Begriffe wie Orte oder Standorte kommagetrennt ergänzen. Dann Prompt erzeugen. Die Anwendung meldet, ob die Rückstandsprüfung sauber ist.

Schritt 4, Antwort zurückspielen: den Prompt in die Zwischenablage kopieren, in Claude einfügen und die JSON-Antwort zurück in das Feld kopieren. Alternativ, wenn ein API-Schlüssel hinterlegt ist, direkt über die Schaltfläche senden. Die Anwendung setzt die Klardaten lokal wieder ein, prüft auf AGG- und DSGVO-Verstöße und zeigt eine Vorschau.

Schritt 5, Arbeitsstand ausgeben: Word-Datei mit grünen Feldern erzeugen. Das ist der Arbeitsstand für das Interview, nicht das Dokument für den Auftraggeber.

Schritt 6, Finalisieren und freigeben: Hier steht, ob das Profil freigabefaehig ist. Das PDF ist das Dokument, das beim Auftraggeber landet, deshalb ist das Gate hart. Es entsteht nur, wenn kein grünes Feld mehr offen ist, kein Compliance-Fehler vorliegt, die Einwilligung des Kandidaten dokumentiert ist, ein Votum in Block 10 steht und der Freigabehaken gesetzt ist. Fehlt etwas, nennt die Anwendung die offenen Punkte statt eine Datei zu erzeugen. Für die Abstimmung mit dem Kandidaten gibt es daneben das Entwurfs-PDF, erkennbar am Vermerk in der Fußzeile jeder Seite und am Kürzel ENTWURF im Dateinamen.

Schritt 7, Versenden: Mailentwurf öffnen. Liegt Outlook vor, wird ein Entwurf mit Anhang erstellt. Sonst öffnet sich der Ordner mit der Datei und ein Mailentwurf ohne Anhang, die Datei ist dann manuell anzufügen. Es werden keine Zugangsdaten gespeichert und keine Mail automatisch versendet.

## Wo liegen die Dateien

`%USERPROFILE%\Documents\AA-Steckbriefe\<Profil-ID>\` mit `profil.json`, `zuordnung.json`, `Steckbrief_<ID>.docx`, `Steckbrief_<ID>.txt` und nach der Freigabe `Steckbrief_<ID>.pdf`, im Entwurfsfall `Steckbrief_<ID>_ENTWURF.pdf`.

Die Datei `zuordnung.json` enthält die Zuordnung von Platzhaltern zu Klarnamen. Sie ist der sensibelste Teil des Falls. Sie gehört nicht in eine Cloud, nicht in einen geteilten Ordner und wird nach Abschluss des Mandats zusammen mit den übrigen Kandidatendaten gelöscht.

## Optionaler API-Modus

Ohne API-Schlüssel arbeitet die Anwendung im Zwischenablage-Modus und braucht keine Internetverbindung außer der, die der Browser für Claude ohnehin nutzt.

Für den direkten Aufruf entweder die Umgebungsvariable `ANTHROPIC_API_KEY` setzen oder die Datei `%USERPROFILE%\.aa-steckbrief\config.json` anlegen:

    {"api_key": "sk-ant-..."}

Der Schlüssel wird nie in die Oberfläche geschrieben und nie protokolliert. Vor jedem Aufruf prüft die Anwendung erneut auf Klartext und bricht ab, statt zu warnen, wenn sie etwas findet.

## Was diese Anwendung nicht leistet

Sie macht die Verarbeitung nicht automatisch DSGVO-konform. Lokal zu rechnen beseitigt die Frage nach dem Auftragsverarbeiter, nicht die Fragen nach Rechtsgrundlage, Einwilligung, Zweckbindung, Löschfristen und technischen Schutzmaßnahmen. Diese Punkte bleiben in der Verantwortung von A/A Executive Search und gehören einmal fachlich geprüft.

Sie ersetzt auch nicht das Urteil des Beraters. Die maschinelle Prüfung erkennt unzulässige Felder, fehlende Einwilligungen und Klartextreste. Ob ein Blindprofil trotz Anonymisierung identifizierbar ist und ob eine Aussage belastbar ist, entscheidet weiterhin der Mensch.

## Sicherheitsmerkmale

Der Server bindet ausschließlich an 127.0.0.1 und weist Anfragen mit fremdem Host-Header ab. Jeder Start erzeugt ein neues Zugriffstoken, das in der Adresse steht und bei jeder Anfrage geprüft wird. Damit kann keine im Browser geöffnete fremde Seite die lokale Schnittstelle ansprechen. Die Oberfläche lädt keine externen Ressourcen, es gibt keine Telemetrie und keine Protokollierung von Inhalten.
