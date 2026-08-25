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
const feldZeile = (label, wLabel, wFeld, note) => new TableRow({
  children: [
    cell(p(label, { size: 20, after: 20 }), { width: wLabel, borders: noBorders }),
    cell(
      note ? [p("", { after: 0 }), new Paragraph({ children: [t(note, { size: 15, color: INK3 })], spacing: { after: 20 } })]
           : p("", { after: 40 }),
      { width: wFeld, borders: ruleBottom() }
    )
  ]
});

// Rechenzeile: Label, Formelhinweis, Betragsfeld
const rechenZeile = (label, formel, wL, wF, wB, o = {}) => new TableRow({
  children: [
    cell(p(label, { size: 20, bold: !!o.bold, after: 20 }), { width: wL, borders: o.top ? { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } } : noBorders, mt: o.top ? 100 : 60 }),
    cell(p(formel, { size: 16, color: INK3, after: 20 }), { width: wF, borders: o.top ? { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } } : noBorders, mt: o.top ? 100 : 60 }),
    cell(p("", { after: 40 }), { width: wB, borders: ruleBottom(o.bold ? INK : LINE), mt: o.top ? 100 : 60 })
  ]
});

// Leere Erfassungszeile fuer Tabellen mit Rahmen
const leerZeile = (widths, hoehe = 120) => new TableRow({
  children: widths.map(w => cell(p("", { after: 0 }), {
    width: w,
    borders: { top: NONE, left: NONE, right: NONE, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } },
    mt: hoehe / 2, mb: hoehe / 2
  }))
});

const kopfZeile = (labels, widths, alignRight = []) => new TableRow({
  tableHeader: true,
  children: labels.map((l, i) => cell(
    p(l, { size: 15, bold: true, color: INK3, caps: true, spacing: 16, after: 0,
           align: alignRight.includes(i) ? AlignmentType.RIGHT : undefined }),
    { width: widths[i], shade: SHADE,
      borders: { ...noBorders, bottom: { style: BorderStyle.SINGLE, size: 6, color: LINE } },
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
    feldZeile("Betrieb", W_L, W_F),
    feldZeile("Inhaber", W_L, W_F),
    feldZeile("Steuernummer", W_L, W_F),
    feldZeile("Abrechnungszeitraum", W_L, W_F, "Monat / Jahr oder Kalenderjahr"),
    feldZeile("Belegdatum", W_L, W_F),
    feldZeile("Beleg-Nr.", W_L, W_F)
  ], [W_L, W_F]),

  h2("Fahrzeug"),
  table([
    feldZeile("Bezeichnung", W_L, W_F),
    feldZeile("Kennzeichen", W_L, W_F),
    feldZeile("Halter / Leasingnehmer", W_L, W_F, "Inhaber persönlich, privat geleast"),
    feldZeile("Leasingvertrag Nr.", W_L, W_F),
    feldZeile("Vertragslaufzeit", W_L, W_F, "in Monaten — Pflichtangabe bei Sonderzahlung")
  ], [W_L, W_F]),

  h2("A · Gesamtkosten und Fahrleistung"),
  hint("Beträge aus der Kostenaufstellung auf Seite 2 übernehmen. Die Leasingsonderzahlung geht nur anteilig ein, verteilt über die Vertragslaufzeit."),
  table([
    rechenZeile("Fahrzeug-Gesamtkosten des Jahres", "Summe Seite 2", 4400, 2900, 2338),
    rechenZeile("Kilometerstand am 31. Dezember", "", 4400, 2900, 2338),
    rechenZeile("Kilometerstand am 1. Januar", "abziehen", 4400, 2900, 2338),
    rechenZeile("Gesamtfahrleistung des Jahres", "Differenz der Kilometerstände", 4400, 2900, 2338, { bold: true })
  ], [4400, 2900, 2338]),

  h2("B · Kilometersatz"),
  table([
    rechenZeile("Individueller Kilometersatz", "Gesamtkosten ÷ Gesamtfahrleistung", 4400, 2900, 2338, { bold: true }),
    rechenZeile("Pauschale je gefahrenem Kilometer", "gesetzlich 0,30 EUR", 4400, 2900, 2338),
    rechenZeile("Angewandter Satz", "der höhere der beiden Werte", 4400, 2900, 2338, { bold: true })
  ], [4400, 2900, 2338]),
  new Paragraph({
    children: [
      t("Angewandte Methode:   ", { size: 20 }),
      t("☐ individueller Satz        ☐ Pauschale 0,30 EUR", { size: 20 }),
      t("        ☐ vorläufiger Satz   ☐ endgültiger Satz", { size: 18, color: INK2 })
    ],
    spacing: { before: 120, after: 80 }
  }),

  h2("C · Betrieblich gefahrene Kilometer"),
  hint("Dienstreisen zählen mit jedem gefahrenen Kilometer, Hin- und Rückweg. Fahrten zwischen Wohnung und Betriebsstätte sind dagegen auf die Entfernungspauschale begrenzt und werden nur mit der einfachen Entfernung angesetzt."),
  table([
    rechenZeile("Dienstreisen im Zeitraum", "Kilometer laut Fahrtenbuch", 4400, 2900, 2338),
    rechenZeile("Abzug Dienstreisen", "Kilometer × angewandter Satz", 4400, 2900, 2338, { bold: true }),
    rechenZeile("Fahrten Wohnung ↔ Betriebsstätte", "Tage × einfache Entfernung", 4400, 2900, 2338),
    rechenZeile("Abzug Entfernungspauschale", "Entfernungskilometer × 0,38 EUR", 4400, 2900, 2338, { bold: true })
  ], [4400, 2900, 2338]),

  h2("D · Betrag der Nutzungseinlage"),
  table([
    rechenZeile("Betrag gesamt", "Summe der beiden Abzüge aus C", 4400, 2900, 2338, { bold: true, top: true })
  ], [4400, 2900, 2338]),
  spacer(80),
  new Paragraph({
    children: [t("Betrieblicher Nutzungsanteil: ______ Prozent.  Über 50 Prozent gilt dieses Modell nicht mehr — dann greift der volle Kostenabzug mit Versteuerung der Privatnutzung. Vor der Abrechnung mit dem Steuerberater klären.", { size: 17, color: INK2 })],
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
  new Paragraph({ children: [t("☐   Fahrtenbuch des Abrechnungszeitraums", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [t("☐   Kostenaufstellung mit Einzelbelegen (Seite 2)", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [t("☐   Kilometerstandsnachweis Jahresanfang und Jahresende", { size: 19 })], spacing: { after: 70 } }),
  new Paragraph({ children: [t("☐   Leasingvertrag mit Sonderzahlung und Laufzeit", { size: 19 })], spacing: { after: 260 } }),

  table([
    new TableRow({ children: [
      cell(p("", { after: 40 }), { width: 4600, borders: ruleBottom(INK) }),
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

const kostenZeile = (pos, note) => new TableRow({
  children: [
    cell(note
      ? [p(pos, { size: 19, after: 10 }), new Paragraph({ children: [t(note, { size: 15, color: INK3 })], spacing: { after: 10 } })]
      : p(pos, { size: 19, after: 30 }),
      { width: KW[0], borders: { ...noBorders, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 }),
    cell(p("", { after: 30 }), { width: KW[1], borders: { ...noBorders, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 }),
    cell(p("", { after: 30 }), { width: KW[2], borders: { ...noBorders, bottom: { style: BorderStyle.SINGLE, size: 4, color: SOFT } }, mt: 80, mb: 80 })
  ]
});

const seite2 = [
  h1("Kostenaufstellung"),
  new Paragraph({
    children: [t("Anlage zum Eigenbeleg · Kalenderjahr ____________", { size: 20, color: INK2 })],
    spacing: { after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }
  }),
  spacer(160),
  hint("Alle Beträge des Kalenderjahres, einheitlich brutto oder einheitlich netto. Jede Zeile braucht einen Beleg dahinter. Parkgebühren, Maut und Fährkosten gehören nicht hierher — sie sind Reisenebenkosten und zusätzlich in voller Höhe abziehbar."),

  table([
    kopfZeile(["Position", "Betrag EUR", "Belege / Bemerkung"], KW, [1]),
    kostenZeile("Leasingraten", "Anzahl der Raten im Jahr × Monatsrate"),
    kostenZeile("Leasingsonderzahlung, Jahresanteil", "Sonderzahlung ÷ Laufzeit in Monaten × Monate im Jahr"),
    kostenZeile("Kfz-Versicherung", "Haftpflicht und Kasko"),
    kostenZeile("Kfz-Steuer"),
    kostenZeile("Stellplatz oder Garage", "nur bei separater Anmietung"),
    kostenZeile("Schutzbrief, GAP-Versicherung"),
    kostenZeile("Hauptuntersuchung, Abgasuntersuchung"),
    kostenZeile("Kraftstoff oder Ladestrom", "Ladestrom zuhause nur bei messbarer Erfassung"),
    kostenZeile("Wartung, Inspektion, Ölwechsel"),
    kostenZeile("Reifen, Wechsel, Einlagerung"),
    kostenZeile("Reparaturen"),
    kostenZeile("Wagenwäsche, Pflege"),
    kostenZeile("Mehrkilometer-Nachzahlung", "anteilig, falls Inklusivkilometer überschritten"),
    kostenZeile("Sonstiges"),
    new TableRow({ children: [
      cell(p("Gesamtkosten des Jahres", { size: 20, bold: true, after: 30 }),
        { width: KW[0], borders: { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } }, mt: 110, mb: 60 }),
      cell(p("", { after: 30 }),
        { width: KW[1], borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: NONE, right: NONE, bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }, mt: 110, mb: 60 }),
      cell(p("", { after: 30 }),
        { width: KW[2], borders: { ...noBorders, top: { style: BorderStyle.SINGLE, size: 8, color: INK } }, mt: 110, mb: 60 })
    ]})
  ], KW),

  h2("Fahrleistung"),
  table([
    rechenZeile("Kilometerstand am 31. Dezember", "Tacho-Foto als Nachweis", 4400, 2900, 2338),
    rechenZeile("Kilometerstand am 1. Januar", "", 4400, 2900, 2338),
    rechenZeile("Gesamtfahrleistung", "Differenz", 4400, 2900, 2338, { bold: true }),
    rechenZeile("Individueller Kilometersatz", "Gesamtkosten ÷ Gesamtfahrleistung", 4400, 2900, 2338, { bold: true, top: true })
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
const FW = [1300, 1200, 1200, 900, 1600, 3400, 2870, 2100];

const seite3 = [
  h1("Fahrtenbuch"),
  new Paragraph({
    children: [t("Erfassungsbogen · Monat ________  Jahr ________  ·  Kennzeichen ________________", { size: 20, color: INK2 })],
    spacing: { after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } }
  }),
  spacer(140),
  new Paragraph({
    children: [t("Zeitnah führen, am besten direkt nach der Fahrt. Der Endstand einer Fahrt ist der Startstand der nächsten — jede Lücke ist eine nicht erfasste Fahrt und macht den Einzelnachweis angreifbar. Privatfahrten brauchen nur die Kilometerangabe, müssen aber erfasst sein, sonst fehlt die Gesamtfahrleistung. Kategorie eintragen: D für Dienstreise, B für Betriebsstätte, P für privat.", { size: 17, color: INK2 })],
    spacing: { after: 200, line: 250 }
  }),

  table([
    kopfZeile(["Datum", "km Start", "km Ende", "km", "Kategorie", "Reiseziel mit Adresse", "Reisezweck", "Geschäftspartner"], FW, [1, 2, 3]),
    ...Array.from({ length: 22 }, () => leerZeile(FW, 190))
  ], FW),

  spacer(200),
  new Paragraph({
    children: [t("Pflichtangaben bei Dienstreisen: Datum, Kilometerstände, Reiseziel mit Adresse, Reisezweck und aufgesuchter Geschäftspartner. Fehlt eine davon, kippt die Fahrt in die Privatnutzung. Bei Umwegen den Grund vermerken.", { size: 17, color: INK2 })],
    spacing: { after: 80, line: 250 }
  }),
  new Paragraph({
    children: [t("Dieser Bogen ist ein Erfassungshilfsmittel. Als steuerlich anerkanntes Fahrtenbuch gilt nur eine geschlossene, nachträglich nicht änderbare Form — gebundenes Papierbuch oder ein elektronisches Fahrtenbuch mit revisionssicherem Protokoll. Eine Tabellenkalkulation wird nicht anerkannt.", { size: 17, color: INK2 })],
    spacing: { after: 80, line: 250 }
  })
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
