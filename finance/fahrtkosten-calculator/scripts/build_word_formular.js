const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, HeadingLevel,
  PageOrientation, VerticalAlign, TableLayoutType
} = require('docx');
const fs = require('fs');

// ---- Design-Token (A/A: weiss, schwarz/grau, ruhig) ----
const INK   = "1D1D1F";
const INK2  = "6E6E73";
const INK3  = "8E8E93";
const LINE  = "D2D2D7";
const SOFT  = "E8E8ED";
const SHADE = "F5F5F7";
const FONT  = "Calibri";

const W_PORTRAIT  = 9638;   // A4 hoch, 2 cm Raender
const W_LANDSCAPE = 14570;  // A4 quer, 2 cm Raender

const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NONE, bottom: NONE, left: NONE, right: NONE };
const ruleBottom = (color = LINE) => ({
  top: NONE, left: NONE, right: NONE,
  bottom: { style: BorderStyle.SINGLE, size: 6, color }
});

// ---- Textbausteine ----
const t = (text, o = {}) => new TextRun({
  text, font: FONT,
  size: o.size || 20,
  bold: !!o.bold,
  color: o.color || INK,
  characterSpacing: o.spacing,
  allCaps: !!o.caps
});

const p = (text, o = {}) => new Paragraph({
  children: Array.isArray(text) ? text : [t(text, o)],
  alignment: o.align,
  spacing: { before: o.before || 0, after: o.after === undefined ? 80 : o.after, line: o.line || 260 },
  border: o.border,
  keepNext: o.keepNext
});

const spacer = (h = 120) => new Paragraph({ children: [], spacing: { after: h } });

// Platzhalter fuer echte Word-Formularfelder. Werden nach dem Packen durch
// FORMTEXT- bzw. FORMCHECKBOX-Felder ersetzt (siehe formularfelder.py).
const FELD = (name, o = {}) => new TextRun({
  text: "@@T|" + name + "@@", font: FONT,
  size: o.size || 20, bold: !!o.bold, color: o.color || INK
});
const FELDU = (name, o = {}) => new TextRun({
  text: "@@U|" + name + "@@", font: FONT, size: o.size || 20, color: o.color || INK
});
const BOX = (name) => new TextRun({ text: "@@C|" + name + "@@", font: FONT, size: 20 });

const feldAbsatz = (name, o = {}) => new Paragraph({
  children: [FELD(name, o)],
  spacing: { after: o.after === undefined ? 40 : o.after, line: 260 },
  alignment: o.align
});

const h1 = (text) => new Paragraph({
  children: [t(text, { size: 34, bold: true })],
  spacing: { after: 60 }
});

const h2 = (text) => new Paragraph({
  children: [t(text, { size: 17, bold: true, color: INK3, caps: true, spacing: 20 })],
  spacing: { before: 280, after: 120 },
  keepNext: true
});

const hint = (text) => new Paragraph({
  children: [t(text, { size: 17, color: INK2 })],
  spacing: { after: 140, line: 240 }
});

// ---- Tabellenbausteine ----
const cell = (children, o = {}) => new TableCell({
  children: Array.isArray(children) ? children : [children],
  width: { size: o.width, type: WidthType.DXA },
  borders: o.borders || noBorders,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
  margins: { top: o.mt === undefined ? 60 : o.mt, bottom: o.mb === undefined ? 60 : o.mb, left: 80, right: 80 },
  verticalAlign: VerticalAlign.BOTTOM,
  columnSpan: o.span
});

const table = (rows, widths) => new Table({
  rows,
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  layout: TableLayoutType.FIXED,
  borders: {
    top: NONE, bottom: NONE, left: NONE, right: NONE,
    insideHorizontal: NONE, insideVertical: NONE
  }
});

// Ausfuellzeile: Label links, Linie rechts
const feldZeile = (label, wLabel, wFeld, note, name) => new TableRow({
  children: [
    cell(p(label, { size: 20, after: 20 }), { width: wLabel, borders: noBorders }),
    cell(
      note ? [feldAbsatz(name, { after: 0 }), new Paragraph({ children: [t(note, { size: 15, color: INK3 })], spacing: { after: 20 } })]
           : feldAbsatz(name),
      { width: wFeld, borders: ruleBottom() }
    )
  ]
});

// Rechenzeile: Label, Formelhinweis, Betragsfeld
const rechenZeile = (label, formel, wL, wF, wB, o = {}) => new TableRow({
  children: [
    cell(p(label, { size: 20, bold: !!o.bold, after: 20 }), { width: wL, borders: o.top ? { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } } : noBorders, mt: o.top ? 100 : 60 }),
    cell(p(formel, { size: 16, color: INK3, after: 20 }), { width: wF, borders: o.top ? { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } } : noBorders, mt: o.top ? 100 : 60 }),
    cell(feldAbsatz(o.name, { bold: !!o.bold, align: AlignmentType.RIGHT }), { width: wB, borders: ruleBottom(o.bold ? INK : LINE), mt: o.top ? 100 : 60 })
  ]
});

// Leere Erfassungszeile fuer Tabellen mit Rahmen
const VLINE = { style: BorderStyle.SINGLE, size: 2, color: SOFT };

const leerZeile = (widths, hoehe = 120, namen = [], vlines = false) => new TableRow({
  children: widths.map((w, i) => cell(feldAbsatz(namen[i], { after: 0, size: 18 }), {
    width: w,
    borders: {
      top: NONE, left: NONE,
      right: vlines && i < widths.length - 1 ? VLINE : NONE,
      bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT }
    },
    mt: hoehe / 2, mb: hoehe / 2
  }))
});

const kopfZeile = (labels, widths, alignRight = [], vlines = false) => new TableRow({
  tableHeader: true,
  children: labels.map((l, i) => cell(
    p(l, { size: 15, bold: true, color: INK3, caps: true, spacing: 16, after: 0,
           align: alignRight.includes(i) ? AlignmentType.RIGHT : undefined }),
    { width: widths[i], shade: SHADE,
      borders: { top: NONE, left: NONE,
                 right: vlines && i < labels.length - 1 ? VLINE : NONE,
                 bottom: { style: BorderStyle.SINGLE, size: 6, color: LINE } },
      mt: 90, mb: 90 }
  ))
});

// ===========================================================
// SEITE 1 — EIGENBELEG
// ===========================================================
const W_L = 3400, W_F = W_PORTRAIT - W_L;

const seite1 = [
  new Paragraph({
    children: [t("Einzelunternehmen · Nutzungseinlage", { size: 15, color: INK3, caps: true, spacing: 24 })],
    spacing: { after: 100 }
  }),
  h1("Eigenbeleg Fahrzeugkosten"),
  new Paragraph({
    children: [t("Betrieblich veranlasster Anteil der Aufwendungen eines privat geleasten Fahrzeugs", { size: 20, color: INK2 })],
    spacing: { after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }
  }),
  spacer(160),

  h2("Beleg"),
  table([
    feldZeile("Betrieb", W_L, W_F, null, "betrieb"),
    feldZeile("Inhaber", W_L, W_F, null, "inhaber"),
    feldZeile("Steuernummer", W_L, W_F, null, "steuernr"),
    feldZeile("Abrechnungszeitraum", W_L, W_F, "Monat / Jahr oder Kalenderjahr", "zeitraum"),
    feldZeile("Belegdatum", W_L, W_F, null, "belegdatum"),
    feldZeile("Beleg-Nr.", W_L, W_F, null, "belegnr")
  ], [W_L, W_F]),

  h2("Fahrzeug"),
  table([
    feldZeile("Bezeichnung", W_L, W_F, null, "fzbez"),
    feldZeile("Kennzeichen", W_L, W_F, null, "kennz"),
    feldZeile("Halter / Leasingnehmer", W_L, W_F, "Inhaber persönlich, privat geleast", "halter"),
    feldZeile("Leasingvertrag Nr.", W_L, W_F, null, "leasingnr"),
    feldZeile("Vertragslaufzeit", W_L, W_F, "in Monaten — Pflichtangabe bei Sonderzahlung", "laufzeit")
  ], [W_L, W_F]),

  h2("A · Gesamtkosten und Fahrleistung"),
  hint("Beträge aus der beiliegenden Kostenaufstellung übernehmen. Die Leasingsonderzahlung geht nur anteilig ein, verteilt über die Vertragslaufzeit."),
  table([
    rechenZeile("Fahrzeug-Gesamtkosten des Jahres", "Summe der Anlage Kostenaufstellung", 4400, 2900, 2338, { name: "aKosten" }),
    rechenZeile("Kilometerstand am 31. Dezember", "", 4400, 2900, 2338, { name: "aKmEnde" }),
    rechenZeile("Kilometerstand am 1. Januar", "abziehen", 4400, 2900, 2338, { name: "aKmStart" }),
    rechenZeile("Gesamtfahrleistung des Jahres", "Differenz der Kilometerstände", 4400, 2900, 2338, { bold: true, name: "aGesamtKm" })
  ], [4400, 2900, 2338]),

  h2("B · Kilometersatz"),
  table([
    rechenZeile("Individueller Kilometersatz", "Gesamtkosten ÷ Gesamtfahrleistung", 4400, 2900, 2338, { bold: true, name: "bSatzInd" }),
    rechenZeile("Pauschale je gefahrenem Kilometer", "gesetzlich 0,30 EUR", 4400, 2900, 2338, { name: "bSatzPau" }),
    rechenZeile("Angewandter Satz", "der höhere der beiden Werte", 4400, 2900, 2338, { bold: true, name: "bSatzAng" })
  ], [4400, 2900, 2338]),
  new Paragraph({
    children: [
      t("Angewandte Methode:    ", { size: 20 }),
      BOX("mIndiv"), t("  individueller Satz          ", { size: 20 }),
      BOX("mPausch"), t("  Pauschale 0,30 EUR", { size: 20 })
    ],
    spacing: { before: 120, after: 60 }
  }),
  new Paragraph({
    children: [
      t("Stand des Satzes:        ", { size: 20 }),
      BOX("mVorl"), t("  vorläufig, Korrektur zum Jahresende          ", { size: 20 }),
      BOX("mEndg"), t("  endgültig", { size: 20 })
    ],
    spacing: { after: 80 }
  }),

  h2("C · Betrieblich gefahrene Kilometer"),
  hint("Dienstreisen zählen mit jedem gefahrenen Kilometer, Hin- und Rückweg. Fahrten zwischen Wohnung und Betriebsstätte sind dagegen auf die Entfernungspauschale begrenzt und werden nur mit der einfachen Entfernung angesetzt."),
  table([
    rechenZeile("Dienstreisen im Zeitraum", "Kilometer laut Fahrtenbuch", 4400, 2900, 2338, { name: "cDienstKm" }),
    rechenZeile("Abzug Dienstreisen", "Kilometer × angewandter Satz", 4400, 2900, 2338, { bold: true, name: "cAbzugD" }),
    rechenZeile("Fahrten Wohnung ↔ Betriebsstätte", "Tage × einfache Entfernung", 4400, 2900, 2338, { name: "cBsKm" }),
    rechenZeile("Abzug Entfernungspauschale", "Entfernungskilometer × 0,38 EUR", 4400, 2900, 2338, { bold: true, name: "cAbzugBs" })
  ], [4400, 2900, 2338]),

  h2("D · Betrag der Nutzungseinlage"),
  table([
    rechenZeile("Betrag gesamt", "Summe der beiden Abzüge aus C", 4400, 2900, 2338, { bold: true, top: true, name: "dBetrag" })
  ], [4400, 2900, 2338]),
  spacer(80),
  new Paragraph({
    children: [
      t("Betrieblicher Nutzungsanteil: ", { size: 17, color: INK2 }),
      FELDU("dAnteil", { size: 17 }),
      t(" Prozent.  Über 50 Prozent gilt dieses Modell nicht mehr — dann greift der volle Kostenabzug mit Versteuerung der Privatnutzung. Vor der Abrechnung mit dem Steuerberater klären.", { size: 17, color: INK2 })
    ],
    spacing: { after: 100, line: 240 }
  }),

  h2("Rechtsgrundlage und Buchung"),
  new Paragraph({
    children: [t("Nutzungseinlage der auf betriebliche Fahrten entfallenden Aufwendungen eines privat geleasten Fahrzeugs, § 4 Abs. 4 EStG. Zwischen Inhaber und Einzelunternehmen besteht kein Leistungsaustausch, daher keine Umsatzsteuer und kein gesonderter Vorsteuerausweis.", { size: 18, color: INK2 })],
    spacing: { after: 120, line: 250 }
  }),
  table([
    new TableRow({ children: [
      cell(p("SKR03", { size: 18, bold: true, after: 0 }), { width: 1200 }),
      cell(p("4670 Reisekosten Unternehmer Fahrtkosten   an   1890 Privateinlagen", { size: 18, after: 0 }), { width: W_PORTRAIT - 1200 })
    ]}),
    new TableRow({ children: [
      cell(p("SKR04", { size: 18, bold: true, after: 0 }), { width: 1200 }),
      cell(p("6670 Reisekosten Unternehmer Fahrtkosten   an   2180 Privateinlagen", { size: 18, after: 0 }), { width: W_PORTRAIT - 1200 })
    ]})
  ], [1200, W_PORTRAIT - 1200]),

  h2("Anlagen"),
  new Paragraph({ children: [BOX("anl1"), t("   Fahrtenbuch des Abrechnungszeitraums", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [BOX("anl2"), t("   Kostenaufstellung mit Einzelbelegen", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [BOX("anl3"), t("   Kilometerstandsnachweis Jahresanfang und Jahresende", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [BOX("anl4"), t("   Leasingvertrag mit Sonderzahlung und Laufzeit", { size: 19 })], spacing: { after: 260 } }),

  table([
    new TableRow({ children: [
      cell(feldAbsatz("ortDatum"), { width: 4600, borders: ruleBottom(INK) }),
      cell(p("", { after: 0 }), { width: 438 }),
      cell(p("", { after: 40 }), { width: 4600, borders: ruleBottom(INK) })
    ]}),
    new TableRow({ children: [
      cell(p("Ort, Datum", { size: 16, color: INK3, after: 0 }), { width: 4600, mt: 40 }),
      cell(p("", { after: 0 }), { width: 438 }),
      cell(p("Unterschrift des Inhabers", { size: 16, color: INK3, after: 0 }), { width: 4600, mt: 40 })
    ]})
  ], [4600, 438, 4600])
];

// ===========================================================
// SEITE 2 — KOSTENAUFSTELLUNG
// ===========================================================
const KW = [4838, 2000, 2800];

const kostenZeile = (pos, note, name) => {
  // Aufrufe ohne Beschreibungstext liefern den Namen im note-Parameter
  if (name === undefined) { name = note; note = undefined; }
  return new TableRow({
  children: [
    cell(note
      ? [p(pos, { size: 19, after: 10 }), new Paragraph({ children: [t(note, { size: 15, color: INK3 })], spacing: { after: 10 } })]
      : p(pos, { size: 19, after: 30 }),
      { width: KW[0], borders: { top: NONE, left: NONE, right: VLINE, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 }),
    cell(feldAbsatz(name + "B", { after: 30, align: AlignmentType.RIGHT }), { width: KW[1], borders: { top: NONE, left: NONE, right: VLINE, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 }),
    cell(feldAbsatz(name + "N", { after: 30, size: 18 }), { width: KW[2], borders: { ...noBorders, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 })
  ]
  });
};

const seite2 = [
  h1("Kostenaufstellung"),
  new Paragraph({
    children: [t("Anlage zum Eigenbeleg · Kalenderjahr ", { size: 20, color: INK2 }), FELDU("kJahr", { size: 20, color: INK2 })],
    spacing: { after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }
  }),
  spacer(160),
  hint("Alle Beträge des Kalenderjahres, einheitlich brutto oder einheitlich netto. Jede Zeile braucht einen Beleg dahinter. Parkgebühren, Maut und Fährkosten gehören nicht hierher — sie sind Reisenebenkosten und zusätzlich in voller Höhe abziehbar."),

  table([
    kopfZeile(["Position", "Betrag EUR", "Belege / Bemerkung"], KW, [1], true),
    kostenZeile("Leasingraten", "Anzahl der Raten im Jahr × Monatsrate", "kLeas"),
    kostenZeile("Leasingsonderzahlung, Jahresanteil", "Sonderzahlung ÷ Laufzeit in Monaten × Monate im Jahr", "kSond"),
    kostenZeile("Kfz-Versicherung", "Haftpflicht und Kasko", "kVers"),
    kostenZeile("Kfz-Steuer", "kSteu"),
    kostenZeile("Stellplatz oder Garage", "nur bei separater Anmietung", "kStell"),
    kostenZeile("Schutzbrief, GAP-Versicherung", "kSchutz"),
    kostenZeile("Hauptuntersuchung, Abgasuntersuchung", "kHu"),
    kostenZeile("Kraftstoff oder Ladestrom", "Ladestrom zuhause nur bei messbarer Erfassung", "kSprit"),
    kostenZeile("Wartung, Inspektion, Ölwechsel", "kWart"),
    kostenZeile("Reifen, Wechsel, Einlagerung", "kReif"),
    kostenZeile("Reparaturen", "kRep"),
    kostenZeile("Wagenwäsche, Pflege", "kPfleg"),
    kostenZeile("Mehrkilometer-Nachzahlung", "anteilig, falls Inklusivkilometer überschritten", "kMehr"),
    kostenZeile("Sonstiges", "kSonst"),
    new TableRow({ children: [
      cell(p("Gesamtkosten des Jahres", { size: 20, bold: true, after: 30 }),
        { width: KW[0], borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: NONE, right: VLINE, bottom: NONE }, mt: 110, mb: 60 }),
      cell(feldAbsatz("kSumme", { after: 30, bold: true, align: AlignmentType.RIGHT }),
        { width: KW[1], borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: NONE, right: NONE, bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }, mt: 110, mb: 60 }),
      cell(p("", { after: 30 }),
        { width: KW[2], borders: { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } }, mt: 110, mb: 60 })
    ]})
  ], KW),

  h2("Fahrleistung"),
  table([
    rechenZeile("Kilometerstand am 31. Dezember", "Tacho-Foto als Nachweis", 4400, 2900, 2338, { name: "kKmEnde" }),
    rechenZeile("Kilometerstand am 1. Januar", "", 4400, 2900, 2338, { name: "kKmStart" }),
    rechenZeile("Gesamtfahrleistung", "Differenz", 4400, 2900, 2338, { bold: true, name: "kGesamtKm" }),
    rechenZeile("Individueller Kilometersatz", "Gesamtkosten ÷ Gesamtfahrleistung", 4400, 2900, 2338, { bold: true, top: true, name: "kSatz" })
  ], [4400, 2900, 2338]),

  h2("Nicht in diese Aufstellung"),
  new Paragraph({
    children: [t("Parkgebühren, Maut und Fährkosten (Reisenebenkosten, separat voll abziehbar) · Bußgelder und Verwarnungsgelder (nicht abziehbar) · Unfallkosten einer Privatfahrt · Automobilclub-Beitrag · Insassenunfallversicherung.", { size: 18, color: INK2 })],
    spacing: { after: 100, line: 250 }
  })
];

// ===========================================================
// SEITE 3 — FAHRTENBUCH (quer)
// ===========================================================
const FW = [1250, 1150, 1150, 850, 1400, 3200, 2870, 2700];

const seite3 = [
  h1("Fahrtenbuch"),
  new Paragraph({
    children: [
      t("Erfassungsbogen · Monat ", { size: 20, color: INK2 }), FELDU("fbMonat", { size: 20, color: INK2 }),
      t("  Jahr ", { size: 20, color: INK2 }), FELDU("fbJahr", { size: 20, color: INK2 }),
      t("  ·  Kennzeichen ", { size: 20, color: INK2 }), FELDU("fbKennz", { size: 20, color: INK2 })
    ],
    spacing: { after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }
  }),
  spacer(140),
  new Paragraph({
    children: [t("Zeitnah führen, am besten direkt nach der Fahrt. Der Endstand einer Fahrt ist der Startstand der nächsten — jede Lücke ist eine nicht erfasste Fahrt und macht den Einzelnachweis angreifbar. Privatfahrten brauchen nur die Kilometerangabe, müssen aber erfasst sein, sonst fehlt die Gesamtfahrleistung. Kategorie eintragen: D für Dienstreise, B für Betriebsstätte, P für privat. Bei Dienstreisen sind Reiseziel mit Adresse, Reisezweck und aufgesuchter Geschäftspartner Pflicht — fehlt eine Angabe, kippt die Fahrt in die Privatnutzung. Bei Umwegen den Grund vermerken.", { size: 17, color: INK2 })],
    spacing: { after: 150, line: 250 }
  }),
  new Paragraph({
    children: [t("Dieser Bogen ist ein Erfassungshilfsmittel. Als steuerlich anerkanntes Fahrtenbuch gilt nur eine geschlossene, nachträglich nicht änderbare Form — gebundenes Papierbuch oder ein elektronisches Fahrtenbuch mit revisionssicherem Protokoll. Eine Tabellenkalkulation wird nicht anerkannt.", { size: 17, color: INK2 })],
    spacing: { after: 200, line: 250 }
  }),

  table([
    kopfZeile(["Datum", "km Start", "km Ende", "km", "Kategorie", "Reiseziel mit Adresse", "Reisezweck", "Partner"], FW, [1, 2, 3], true),
    ...Array.from({ length: 12 }, (_, i) => {
      const n = String(i + 1).padStart(2, "0");
      return leerZeile(FW, 200, ["d", "s", "e", "k", "c", "z", "w", "p"].map(sp => "fb" + n + sp), true);
    })
  ], FW),

  spacer(120)
];

// ===========================================================
// Dokument
// ===========================================================
const fuss = (text) => ({
  default: new (require('docx').Footer)({
    children: [new Paragraph({
      children: [t(text, { size: 14, color: INK3 })],
      alignment: AlignmentType.LEFT,
      spacing: { before: 120 },
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }
    })]
  })
});

const FUSSTEXT = "Rechenstand 2026: Entfernungspauschale 0,38 EUR ab dem ersten Kilometer, Dienstreisepauschale 0,30 EUR je gefahrenem Kilometer. Keine Steuerberatung — Werte vor Abgabe der Steuererklärung mit dem Steuerberater abstimmen.";

const doc = new Document({
  creator: "Fahrtkosten-Calculator",
  title: "Eigenbeleg Fahrzeugkosten",
  description: "Ausfüllbares Formular zur Nutzungseinlage eines privat geleasten Fahrzeugs",
  styles: { default: { document: { run: { font: FONT, size: 20, color: INK } } } },
  sections: [
    {
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
      footers: fuss(FUSSTEXT),
      children: seite1
    },
    {
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
      footers: fuss(FUSSTEXT),
      children: seite2
    },
    {
      properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
      footers: fuss(FUSSTEXT),
      children: seite3
    }
  ]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("Eigenbeleg-Fahrzeugkosten.docx", buf);
  console.log("geschrieben:", buf.length, "Bytes");
});
