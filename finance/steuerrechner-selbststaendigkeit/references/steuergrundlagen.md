# Steuergrundlagen für gewerbliche Einzelunternehmer (EÜR)

Wissensbasis für den Steuerrechner. Stand: 2026 — Tarifwerte jährlich gegen
den offiziellen BMF-Rechner prüfen (https://www.bmf-steuerrechner.de).

> **Disclaimer:** Planungswissen für die Rücklagenbildung, keine Steuerberatung.
> Verbindlich sind ausschließlich Steuerbescheide und die Auskunft eines
> Steuerberaters.

## Das wichtigste Prinzip zuerst

**Steuern entstehen auf den Gewinn, nicht auf den Umsatz** (einzige Ausnahme:
Umsatzsteuer). Wer Rücklagen nur prozentual vom Umsatz bildet, ohne die
Kostenquote zu berücksichtigen, spart entweder zu viel (Liquidität liegt brach)
oder zu wenig (böses Erwachen bei der Erklärung). Der Rechner nimmt deshalb
immer Umsatz **und** Betriebsausgaben als Eingabe.

Zweites Prinzip: **Die Umsatzsteuer gehört zu keinem Zeitpunkt dir.** Sie ist
ein Durchlaufposten, den du treuhänderisch für das Finanzamt einnimmst. Sie
gehört sofort vom Geschäftskonto herunter auf ein eigenes Unterkonto.

## 1. Umsatzsteuer (USt)

| Parameter | Wert |
|---|---|
| Regelsteuersatz | 19 % |
| Ermäßigter Satz | 7 % (für Beratung/Dienstleistung i. d. R. irrelevant) |
| Zahllast | vereinnahmte USt − gezahlte Vorsteuer |
| Voranmeldung | bis zum 10. des Folgemonats (elektronisch, ELSTER) |
| Rhythmus | Zahllast Vorjahr > 9.000 € → monatlich; 2.000–9.000 € → quartalsweise; ≤ 2.000 € → nur Jahreserklärung (Werte ab 2025) |
| Dauerfristverlängerung | +1 Monat Abgabefrist, bei Monatszahlern gegen 1/11-Sondervorauszahlung |

**Kleinunternehmerregelung (§ 19 UStG, ab 2025):** Vorjahresumsatz ≤ 25.000 €
und laufendes Jahr ≤ 100.000 €. Keine USt auf Rechnungen, aber auch kein
Vorsteuerabzug. Für B2B-Geschäft (z. B. Executive Search) fast immer
unattraktiv, weil Geschäftskunden die USt ohnehin als Vorsteuer ziehen und der
eigene Vorsteuerabzug verloren geht.

**Vorsteuer-Schätzung im Rechner:** Standardannahme ist, dass alle
Betriebsausgaben 19 % Vorsteuer enthalten. Realistisch ist das zu hoch, sobald
Versicherungen, Beiträge, Bewirtung (nur 70 % abziehbar, Vorsteuer aber voll)
oder Auslandsleistungen dabei sind — dann die tatsächliche Vorsteuer aus der
Buchhaltung per `--vorsteuer` übergeben.

## 2. Gewerbesteuer (GewSt)

Rechenweg für Einzelunternehmer:

```
Gewinn aus Gewerbebetrieb
→ Gewerbeertrag (± Hinzurechnungen/Kürzungen, im Normalfall ≈ Gewinn)
→ Abrunden auf volle 100 €
→ − Freibetrag 24.500 €
→ × Steuermesszahl 3,5 %  = Steuermessbetrag
→ × Hebesatz der Gemeinde = Gewerbesteuer
```

**Wiggensbach (Landkreis Oberallgäu): Hebesatz 320 %** → effektiv
3,5 % × 320 % = **11,2 % auf den Gewinnanteil über 24.500 €**.

### § 35 EStG — die entscheidende Entlastung

Die Gewerbesteuer wird mit dem **4,0-fachen des Steuermessbetrags** auf die
Einkommensteuer angerechnet (gedeckelt auf die tatsächlich gezahlte GewSt und
die anteilige tarifliche ESt). Break-even liegt bei Hebesatz 400 %:

- **Hebesatz 320 % < 400 % → die GewSt wird faktisch vollständig auf die ESt
  angerechnet.** Wirtschaftlich kostet die Gewerbesteuer in Wiggensbach also
  fast nichts — sie ist im Wesentlichen ein **Liquiditäts- und Timing-Thema**
  (die Gemeinde will vierteljährlich Geld, die Erstattung kommt über die
  niedrigere ESt zurück).
- Deshalb trotzdem ein eigenes Rücklagen-Unterkonto: Die GewSt-Vorauszahlungen
  (15.02. / 15.05. / 15.08. / 15.11.) sind real fällig, bevor die
  ESt-Entlastung wirkt.

Hinzurechnungen (§ 8 GewStG, z. B. 25 % der Zinsen, Anteile von Mieten/Leasing)
greifen erst oberhalb eines Freibetrags von 200.000 € Hinzurechnungssumme —
für ein Dienstleistungs-Einzelunternehmen praktisch nie relevant.

## 3. Einkommensteuer (ESt)

Bemessungsgrundlage: **zu versteuerndes Einkommen (zvE)** =
Gewinn − Vorsorgeaufwendungen − Sonderausgaben (− ggf. weitere Abzüge).

Tarif § 32a EStG (Grundtarif, Einzelveranlagung):

| Jahr | Grundfreibetrag | Ende Zone 1 | 42 % ab | 45 % ab | Soli-Freigrenze |
|---|---|---|---|---|---|
| 2025 | 12.096 € | 17.443 € | 68.481 € | 277.826 € | 19.950 € |
| 2026 | 12.348 € | 17.799 € | 69.879 € | 277.826 € | 20.350 € |

Grenzsteuersatz startet bei 14 %, steigt progressiv auf 42 % (Spitzensteuersatz),
45 % „Reichensteuer" ab ~277.826 €. Die Zahlen für 2026 stammen aus dem
Steuerfortentwicklungsgesetz — **vor der ersten Nutzung im neuen Jahr gegen den
BMF-Rechner prüfen** und ggf. in `scripts/steuerrechner.py`
(`TARIF_ECKWERTE`, `SOLI_FREIGRENZE`) aktualisieren.

**Wichtigste Abzugsposten für Selbstständige (im Rechner: `--kv-monat`,
`--sonstige-vorsorge`):**

- Kranken- und Pflegeversicherung (Basisabsicherung): **voll abziehbar** —
  bei freiwilliger GKV oder PKV schnell 800–1.100 €/Monat, senkt das zvE massiv.
- Altersvorsorge (Rürup/Basisrente, freiwillige GRV): abziehbar bis
  Höchstbetrag (2025: 29.344 € Alleinstehende, 100 % wirksam) — das ist
  gleichzeitig der stärkste legale Gestaltungshebel zum Jahresende.
- Sonderausgaben-Pauschbetrag: 36 € (der Rechner zieht ihn automatisch ab).

## 4. Solidaritätszuschlag (Soli)

5,5 % der festzusetzenden ESt, aber nur oberhalb der Freigrenze
(2026: 20.350 € ESt bei Einzelveranlagung), mit Milderungszone
(max. 11,9 % des übersteigenden Betrags). Bei mittleren Gewinnen fällt der
Soli daher oft gar nicht oder nur gering an.

## 5. Kirchensteuer (KiSt)

8 % der festzusetzenden ESt in **Bayern** (und BW), 9 % in den übrigen
Ländern. Nur bei Kirchenmitgliedschaft. Die KiSt ist selbst als Sonderausgabe
abziehbar — der Rechner ignoriert diesen Rückkopplungseffekt bewusst und
reserviert damit leicht konservativ (Puffer zu deinen Gunsten).

## 6. Vorauszahlungen — so funktioniert der Zyklus

Das Finanzamt setzt nach der ersten Erklärung (oder nach dem Fragebogen zur
steuerlichen Erfassung) Vorauszahlungen fest, basierend auf dem erwarteten bzw.
letzten Gewinn:

| Steuer | Fälligkeiten | Empfänger |
|---|---|---|
| ESt + Soli (+ KiSt) | 10.03. / 10.06. / 10.09. / 10.12. | Finanzamt |
| Gewerbesteuer | 15.02. / 15.05. / 15.08. / 15.11. | Gemeinde Wiggensbach |
| USt-Voranmeldung | 10. des Folgemonats/-quartals | Finanzamt |

**Die Falle im Gründungs-/Wachstumsjahr:** Vorauszahlungen basieren auf der
Vergangenheit. Läuft das Jahr besser als das Vorjahr, entsteht bei der
Erklärung eine **Nachzahlung für das abgelaufene Jahr PLUS sofort erhöhte
Vorauszahlungen für das laufende** — der berüchtigte Doppeleffekt, der
Selbstständige im Jahr 2–3 regelmäßig in Liquiditätsnot bringt. Genau dafür
ist die monatliche Rücklage nach diesem Rechner da: Sie deckt die *echte*
Steuerlast des laufenden Jahres, unabhängig davon, was das Finanzamt bereits
als Vorauszahlung einzieht.

**Gestaltungshinweis:** Vorauszahlungen können auf Antrag (formlos ans
Finanzamt, mit Gewinnprognose) **herauf- oder herabgesetzt** werden. Bei
absehbar besserem Jahr lohnt die freiwillige Heraufsetzung selten — besser
selbst zurücklegen (Rücklage bleibt liquide). Bei schlechterem Jahr sofort
Herabsetzung beantragen.

## 7. Nicht Steuer, aber gleiche Disziplin: Sozialabgaben

Der Vollständigkeit halber (gehören in die private Finanzplanung, nicht in die
gewerbliche Steuerrücklage):

- **Krankenversicherung:** freiwillig GKV (einkommensabhängig, Beitrag wird
  nachträglich anhand des ESt-Bescheids spitz abgerechnet — auch hier drohen
  Nachzahlungen!) oder PKV.
- **Rentenversicherung:** für die meisten Gewerbetreibenden freiwillig.

Diese Beiträge unbedingt als `--kv-monat` / `--sonstige-vorsorge` in den
Rechner geben — sie senken das zvE erheblich.
