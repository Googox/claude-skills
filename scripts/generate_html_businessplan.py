#!/usr/bin/env python3
"""
ARENA Executive Search — Businessplan 2026–2029
HTML-Präsentation: Standalone, kein Speichern nötig
Koordinatensystem: 1334 × 750 px (1" = 100 px), skaliert auf Viewport
"""
import html as _html, os

# ── HTML-Farben (identisch mit PPTX Design-System) ────────────────────────────
W   = '#FFFFFF'
BK  = '#1D1D1F'   # Apple-Schwarz
DK  = '#3A3A3C'   # Dunkelgrau
MD  = '#6E6E73'   # Mittelgrau
LT  = '#F5F5F7'   # Hellgrau
VLT = '#FAFAFC'
DV  = '#D2D2D7'   # Divider

# ── Primitive ──────────────────────────────────────────────────────────────────

def e(s):
    return _html.escape(str(s)).replace('\n', '<br>')

def p(v):  # Inches → px
    return f"{v * 100:.0f}"

def r(x, y, w, h, fill=W, lc=None, lw=0.5, extra=''):
    st = (f"left:{p(x)}px;top:{p(y)}px;width:{p(w)}px;height:{p(h)}px;"
          f"background:{fill};")
    if lc: st += f"border:{lw}pt solid {lc};"
    return f'<div style="position:absolute;{st}{extra}"></div>'

def t(text, x, y, w, h, sz=16, clr=BK, bold=False, italic=False,
      al='left', fl=False, wrap=True):
    fa = ("'Calibri Light',Calibri,-apple-system,sans-serif" if fl
          else "Calibri,-apple-system,sans-serif")
    fw = '700' if bold else '400'
    fs = 'italic' if italic else 'normal'
    ow = "overflow-wrap:break-word;" if wrap else "white-space:nowrap;overflow:hidden;"
    st = (f"left:{p(x)}px;top:{p(y)}px;width:{p(w)}px;height:{p(h)}px;"
          f"font-family:{fa};font-size:{sz}pt;color:{clr};"
          f"font-weight:{fw};font-style:{fs};text-align:{al};"
          f"line-height:1.28;{ow}")
    return f'<div style="position:absolute;{st}">{e(text)}</div>'

def hdr(title, sub=None):
    out = t(title, 0.55, 0.32, 12.3, 0.58, sz=28, clr=BK, fl=True)
    out += r(0.55, 0.94, 12.23, 0.022, fill=DV)
    if sub: out += t(sub, 0.55, 1.0, 12.0, 0.3, sz=12, clr=MD, italic=True)
    return out

def ftr(n, total=16):
    return (r(0, 7.28, 13.33, 0.22, fill=LT)
            + t("ARENA Executive Search  —  Businessplan 2026–2029", 0.45, 7.3, 9, 0.18, sz=8, clr=MD)
            + t(f"{n} / {total}", 12.55, 7.3, 0.7, 0.18, sz=8, clr=MD, al='right'))

def wrap_slide(content, idx):
    active = ' class="slide active"' if idx == 1 else ' class="slide"'
    return f'<div{active} id="s{idx}">\n{content}\n</div>'

# ── Slides ─────────────────────────────────────────────────────────────────────

def s01_cover():
    out  = r(0.55, 1.6, 0.04, 4.3, fill=BK)
    out += t("ARENA",                        0.9, 1.55, 11, 1.6,  sz=90, fl=True)
    out += t("Executive Search",             0.9, 3.1,  11, 0.7,  sz=34, clr=MD, fl=True)
    out += r(0.9, 3.9, 7.0, 0.025, fill=DV)
    out += t("Die richtigen Führungspersönlichkeiten.\nZur richtigen Zeit.",
             0.9, 4.05, 9, 0.7, sz=17, clr=DK, fl=True)
    out += t("Businessplan  2026 – 2029  |  Aaron Arena  |  Oktober 2026",
             0.9, 6.75, 10, 0.3, sz=10, clr=MD)
    return wrap_slide(out, 1)

def s02_agenda():
    out  = ftr(2)
    out += hdr("Inhaltsverzeichnis")
    items = [
        "Die Marktchance", "Der Gründer — Aaron Arena",
        "Marktanalyse DACH", "Geschäftsmodell & Einnahmen",
        "Leistungsportfolio", "Wettbewerbsvorteile (USP)",
        "Partnerschaftsmodell — Nachfolgelösung", "Wachstumsstrategie",
        "Finanzplanung 2026 – 2029", "Investitionsbedarf & Mittelverwendung",
        "Meilensteine & Roadmap", "Fazit & Nächste Schritte",
    ]
    for i, label in enumerate(items):
        col = i // 6; row = i % 6
        x = 0.55 + col * 6.5; y = 1.45 + row * 0.88
        num = f"{i+1:02d}"
        out += r(x, y+0.04, 0.4, 0.38, fill=BK)
        out += t(num, x, y+0.04, 0.4, 0.38, sz=11, clr=W, bold=True, al='center')
        out += t(label, x+0.52, y+0.07, 5.7, 0.35, sz=13, clr=BK)
        out += r(x+0.52, y+0.48, 5.7, 0.012, fill=DV)
    return wrap_slide(out, 2)

def s03_chance():
    out  = ftr(3)
    out += hdr("Die Marktchance",
               "Executive Search in Deutschland — strukturelles Wachstum in einem hochmargigen Markt")
    kpis = [
        ("€ 2,8 Mrd.", "Executive-Search-Markt\nDeutschland 2026"),
        ("+ 11 %",     "Jährliches Wachstum\n(CAGR 2023–2028)"),
        ("67 %",       "C-Level-Positionen\nwerden diskret besetzt"),
    ]
    for i, (val, lbl) in enumerate(kpis):
        cx = 0.55 + i * 4.25
        out += r(cx, 1.55, 4.0, 2.2, fill=LT)
        out += t(val, cx+0.2, 1.65, 3.6, 1.05, sz=48, clr=BK, fl=True, al='center')
        out += r(cx+0.3, 2.68, 3.4, 0.018, fill=DV)
        out += t(lbl, cx+0.2, 2.73, 3.6, 0.75, sz=12, clr=MD, al='center')
    drivers = [
        ("Digitale Transformation",   "70 % der Unternehmen suchen CDO/CTO — Nachfrage +34 % YoY"),
        ("Nachfolgeplanung",           "580.000 KMU-Übergaben bis 2030 — struktureller Dauertreiber"),
        ("Regulierung & ESG",          "Compliance-Druck erhöht Nachfrage nach Risk-Executives"),
        ("Internationalisierung",      "Cross-border Searches DACH +28 %"),
    ]
    for i, (ti, desc) in enumerate(drivers):
        cx = 0.55 + i * 3.2
        out += r(cx, 4.05, 3.05, 1.55, fill=W, lc=DV)
        out += r(cx, 4.05, 3.05, 0.04, fill=BK)
        out += t(ti,   cx+0.12, 4.15, 2.8, 0.38, sz=11, clr=BK, bold=True)
        out += t(desc, cx+0.12, 4.58, 2.8, 0.9,  sz=10, clr=MD)
    out += t("Quellen: BDU Executive Search Report 2026  |  Statista 2026  |  Kienbaum Executive Panel",
             0.55, 6.82, 12, 0.25, sz=8, clr=DV, italic=True)
    return wrap_slide(out, 3)

def s04_founder():
    out  = ftr(4)
    out += hdr("Der Gründer — Aaron Arena",
               "30+ Jahre Erfahrung in Executive Recruitment | Gründung 01.10.2026")
    out += r(0.55, 1.38, 4.0, 5.65, fill=LT)
    out += t("30+", 0.7, 1.5, 3.7, 1.1, sz=72, clr=BK, fl=True, al='center')
    out += t("Jahre im Executive Search", 0.7, 2.55, 3.7, 0.35, sz=12, clr=MD, al='center')
    out += r(1.1, 3.0, 2.9, 0.02, fill=DV)
    hl = ["200+  erfolgreiche C-Level-Placements",
          "1.500+  Entscheider-Kontakte DACH",
          "Sektorfokus: Finance · Tech · Industrie",
          "Ausbildung: BWL, Executive Development",
          "Sprachen: Deutsch · Englisch · Italienisch"]
    for i, h in enumerate(hl):
        out += t(h, 0.7, 3.15 + i * 0.5, 3.65, 0.42, sz=11, clr=DK)
    tl = [
        ("2026 →",    "Gründer",           "ARENA Executive Search — München",           True),
        ("2019–2026", "Senior Partner",    "Boutique Executive Search — DACH",           False),
        ("2012–2019", "Director Search",   "Internationale Personalberatung — Frankfurt", False),
        ("2005–2012", "Senior Consultant", "Finanz- & Technologiesektor — DACH",         False),
        ("1995–2005", "Karrierebeginn",    "Unternehmensberatung & Personalwesen",        False),
    ]
    for i, (year, role, desc, cur) in enumerate(tl):
        yp = 1.42 + i * 1.02
        lc = BK if cur else DV
        out += r(4.9, yp+0.04, 0.04, 0.85, fill=lc)
        out += r(4.77, yp+0.1, 0.2, 0.2, fill=BK if cur else DV)
        out += t(year, 5.15, yp,        3.5, 0.3,  sz=9,  clr=BK if cur else MD, bold=cur)
        out += t(role, 5.15, yp+0.28,   7.6, 0.32, sz=13, clr=BK, bold=True)
        out += t(desc, 5.15, yp+0.58,   7.6, 0.34, sz=11, clr=MD)
    return wrap_slide(out, 4)

def s05_markt():
    out  = ftr(5)
    out += hdr("Marktanalyse — Executive Search DACH",
               "Kontinuierliches Wachstum in einem strukturell robusten Markt")
    out += r(0.55, 1.38, 6.15, 5.35, fill=LT)
    out += t("Marktvolumen Executive Search DACH (Mrd. €)", 0.7, 1.5, 5.8, 0.32, sz=11, clr=DK, bold=True)
    bars = [("2022",2.0),("2023",2.2),("2024",2.5),("2025e",2.65),("2026e",2.8),("2027p",3.1)]
    max_v=3.4; max_h=2.8; bw=0.62
    for i, (yr, val) in enumerate(bars):
        bh = (val/max_v)*max_h; bx=0.75+i*0.88; by=5.6-bh
        fc = BK if i >= 3 else DK
        out += r(bx, by, bw, bh, fill=fc)
        out += t(f"{val:.1f}", bx-0.02, by-0.3, 0.7, 0.25, sz=8, clr=BK if i>=3 else MD, bold=(i>=3), al='center')
        out += t(yr, bx-0.01, 5.65, 0.68, 0.22, sz=9, clr=DK, al='center')
    out += t("e = geschätzt  |  p = Prognose  |  Quelle: BDU, Statista 2026",
             0.7, 6.6, 5.8, 0.2, sz=8, clr=MD, italic=True)
    out += t("Marktsegmente nach Funktion", 7.0, 1.38, 5.9, 0.32, sz=11, clr=DK, bold=True)
    out += r(7.0, 1.73, 5.9, 0.022, fill=DV)
    segs = [("CEO / Geschäftsführung","38 %"),("CFO / Finance Leadership","22 %"),
            ("CTO / Digital / CDO","18 %"),("COO / Operations","12 %"),("Sonstige C-Suite","10 %")]
    fc_seq = [BK,BK,DK,DK,MD]
    for i, (lbl, pct) in enumerate(segs):
        ry = 1.88 + i*0.72
        bw2 = float(pct.rstrip(" %"))/100 * 4.8
        out += r(7.0, ry, bw2, 0.32, fill=fc_seq[i])
        out += t(lbl, 7.08, ry+0.06, 3.5, 0.24, sz=10, clr=W)
        out += t(pct, 11.7, ry+0.06, 0.5, 0.24, sz=10, clr=DK, bold=True)
    ins = ["Nachfolgemandate: +31 % gegenüber Vorjahr",
           "Frauenanteil C-Level: Regulierung als Treiber",
           "Ø Suchdauer Top-Mandat: 12–16 Wochen",
           "Boutiques gewinnen Marktanteile von Big 4"]
    for i, s in enumerate(ins):
        out += r(7.0, 5.5+i*0.4, 5.9, 0.36, fill=LT if i%2==0 else W)
        out += t(f"→  {s}", 7.1, 5.54+i*0.4, 5.7, 0.28, sz=10, clr=DK)
    return wrap_slide(out, 5)

def s06_modell():
    out  = ftr(6)
    out += hdr("Geschäftsmodell & Einnahmen", "Drei Säulen — Retained Search als Kern")
    cols = [
        ("Retained\nSearch","Kernleistung",
         ["Exklusives Mandat","Retainer 1/3 upfront + Milestone + Success",
          "Gebühr: 28–33 % Jahresgehalt","Garantiezeitraum: 12 Monate","Ø Laufzeit: 10–14 Wochen"],
         "60 %", BK),
        ("Executive\nInterim","Ergänzend",
         ["Sofortbesetzung bei Führungslücken","3–12 Monate Laufzeit",
          "Tagesatz: €1.200 – 2.200","Kein Exklusiv-Mandat nötig","Schneller ROI für Mandanten"],
         "25 %", DK),
        ("Advisory &\nAssessment","Ergänzend",
         ["C-Suite Potenzialanalysen","Nachfolgeplanung intern",
          "Executive Coaching","Workshop-Formate","Festpreis: €8.000 – 18.000"],
         "15 %", MD),
    ]
    for i, (ti, badge, bullets, share, hc) in enumerate(cols):
        cx = 0.55 + i*4.25
        out += r(cx, 1.38, 4.0, 5.35, fill=LT if i%2==0 else W, lc=DV)
        out += r(cx, 1.38, 4.0, 0.5,  fill=hc)
        out += t(ti,    cx+0.15, 1.4,  3.7, 0.48, sz=18, clr=W, bold=True, fl=True, al='center')
        out += r(cx+0.8,1.93, 2.4, 0.3, fill=DV)
        out += t(badge, cx+0.8,1.93, 2.4, 0.3, sz=9, clr=DK, bold=True, al='center')
        for j, b in enumerate(bullets):
            out += t(f"· {b}", cx+0.18, 2.36+j*0.54, 3.65, 0.48, sz=11, clr=DK)
        out += r(cx, 6.43, 4.0, 0.3, fill=hc)
        out += t(f"Umsatzanteil: {share}", cx+0.1, 6.45, 3.8, 0.26, sz=10, clr=W, bold=True, al='center')
    return wrap_slide(out, 6)

def s07_leistungen():
    out  = ftr(7)
    out += hdr("Leistungsportfolio", "Was wir für unsere Mandanten leisten")
    svcs = [
        ("C-Suite Search", "Vorstand · Geschäftsführung · C-Level",
         "Vollumfänglicher diskreter Suchprozess. Longlist → Assessment → Onboarding. Erfolgsquote > 95 %. 12 Monate Garantie."),
        ("Board Advisory", "Aufsichtsrat · Beirat · Advisory Board",
         "Rekrutierung und Beratung für Kontrollgremien. Governance, Diversität, Kompetenzprofil-Analyse."),
        ("Executive Interim", "Überbrückung & Transformation",
         "Top-Führungskräfte für Restrukturierungen, M&A-Projekte. Netzwerk von 120+ geprüften Interim-Executives."),
        ("Succession Planning", "Nachfolge & Talentpipeline",
         "Systematische Nachfolgeplanung für Inhaber, Familienunternehmen und PE-Portfolios. 12–36 Monate Begleitung."),
    ]
    for i, (ti, sub, desc) in enumerate(svcs):
        col=i%2; row=i//2
        cx=0.55+col*6.4; cy=1.38+row*2.72
        out += r(cx, cy, 6.1, 2.55, fill=LT if i%2==0 else W, lc=DV)
        out += r(cx, cy, 0.05, 2.55, fill=BK)
        out += t(ti,   cx+0.2, cy+0.1,  5.7, 0.38, sz=15, clr=BK, bold=True)
        out += t(sub,  cx+0.2, cy+0.5,  5.7, 0.28, sz=10, clr=MD, italic=True)
        out += r(cx+0.2, cy+0.82, 5.6, 0.018, fill=DV)
        out += t(desc, cx+0.2, cy+0.9,  5.75, 1.4, sz=11, clr=DK)
    return wrap_slide(out, 7)

def s08_usp():
    out  = ftr(8)
    out += hdr("Warum ARENA?",
               "Vier strategische Differenzierungsmerkmale gegenüber dem Wettbewerb")
    usps = [
        ("01","Tiefes persönliches\nBranchennetzwerk",
         "30+ Jahre aufgebautes Netzwerk von 1.500+ C-Level-Kontakten in Finance, Technology und Industrie. Direktansprache — kein anonymes Datenbanksurf."),
        ("02","Boutique-Qualität\nbei jeder Suche",
         "Kein Volumenziel. Jede Suche wird vom Gründer persönlich geführt. Mandantenzahl bewusst limitiert für maximale Qualität."),
        ("03","Nachfolge-Expertise\nals Alleinstellungsmerkmal",
         "Spezialkompetenz in Unternehmensnachfolge und Senior-Transition. 580.000 KMU-Nachfolgen bis 2030 in Deutschland."),
        ("04","Diskrete, vertrauens-\nbasierte Arbeitsweise",
         "Vertraulichkeit als Kernprinzip. Keine Stellenanzeigen. Preferred Partner zahlreicher Familienunternehmen und PE-Häuser."),
    ]
    for i, (num, ti, desc) in enumerate(usps):
        cx=0.55+(i%2)*6.4; cy=1.38+(i//2)*2.75
        out += r(cx, cy, 6.1, 2.55, fill=LT if i%2==0 else W, lc=DV)
        out += r(cx+0.15, cy+0.12, 0.55, 0.55, fill=BK)
        out += t(num, cx+0.15, cy+0.12, 0.55, 0.55, sz=14, clr=W, bold=True, al='center')
        out += t(ti,  cx+0.85, cy+0.1,  5.1, 0.7,  sz=14, clr=BK, bold=True, fl=True)
        out += r(cx+0.85, cy+0.88, 4.9, 0.018, fill=DV)
        out += t(desc, cx+0.2, cy+0.98, 5.7, 1.35, sz=11, clr=DK)
    return wrap_slide(out, 8)

def s09_partner():
    out  = ftr(9)
    out += hdr("Partnerschaftsmodell — Nachfolgelösung",
               "Strukturierte Praxisübernahme über 4 Jahre — Win-Win für beide Seiten")
    out += r(0.55, 1.38, 5.7, 5.35, fill=LT)
    out += t("Das Modell", 0.7, 1.48, 5.4, 0.32, sz=13, clr=BK, bold=True)
    out += r(0.7, 1.82, 5.3, 0.02, fill=DV)
    desc = ("Ein erfahrener Headhunter (Gründer, 60+) sucht einen qualifizierten "
            "Nachfolger, der sein Lebenswerk weiterführt.\n\n"
            "Aaron Arena bringt mit:\n"
            "· Operatives Executive-Search-Know-how (30+ Jahre)\n"
            "· Eigenständiges DACH-Netzwerk (1.500+ Kontakte)\n"
            "· Finanzielle Kapazität & Bankfinanzierung\n"
            "· Klares Wachstumskonzept für die Praxis\n\n"
            "Der Senior-Partner erhält:\n"
            "· Strukturierten Ausstieg über 48 Monate\n"
            "· Faire Beteiligungsvergütung\n"
            "· Sicherung seines Lebenswerks")
    out += t(desc, 0.7, 1.95, 5.3, 4.6, sz=11, clr=DK)
    phases = [
        ("Phase 1  |  2026–2027", "Einstieg & Lernen",         "Shadowing, gemeinsame Mandate, Dual-Brand",       BK),
        ("Phase 2  |  2027–2028", "Operative Übernahme",        "Aaron Arena führt 60 % der Mandate eigenständig", DK),
        ("Phase 3  |  2028–2029", "Mehrheitskontrolle",          "Übernahme Mandantschaft & Beteiligung",           MD),
        ("Phase 4  |  2030",      "Vollübernahme",               "100 % ARENA — Senior-Partner in Advisory-Rolle",  BK),
    ]
    for i, (ph, ti, d2, hc) in enumerate(phases):
        cy = 1.38 + i*1.22
        out += r(6.55, cy, 6.5, 1.12, fill=LT if i%2==0 else W, lc=DV)
        out += r(6.55, cy, 6.5, 0.36, fill=hc)
        out += t(ph,   6.68, cy+0.06, 6.2, 0.26, sz=10, clr=W, bold=True)
        out += t(ti,   6.68, cy+0.44, 6.1, 0.3,  sz=13, clr=BK, bold=True)
        out += t(d2,   6.68, cy+0.76, 6.1, 0.28, sz=11, clr=MD)
    return wrap_slide(out, 9)

def s10_wachstum():
    out  = ftr(10)
    out += hdr("Wachstumsstrategie", "Fokussiertes Wachstum in drei Horizonten")
    hs = [
        ("H1  —  Aufbau",    "Okt 2026 – Sep 2027",
         ["5–8 Retained Searches abschließen","3 Anker-Mandanten gewinnen",
          "Website, Brand, Reputation aufbauen","Partnerschaft formalisieren",
          "Bestandsnetzwerk vollständig aktivieren"],
         "€ 240K", BK),
        ("H2  —  Wachstum",  "2028",
         ["12–15 Mandate p.a.","Spezialisierung Finance/Tech vertieft",
          "2. Consultant hinzunehmen","Nachfolge-Boutique-Marke etabliert",
          "Erste Interim-Mandate produktiv"],
         "€ 520K", DK),
        ("H3  —  Skalierung","2029",
         ["18–22 Mandate p.a.","Vollübernahme Partnerpraxis",
          "Board-Advisory-Segment ausgebaut","DACH-weite Mandantenbasis",
          "Team: 3–4 Berater"],
         "€ 980K", MD),
    ]
    for i, (ti, per, bul, kpi, hc) in enumerate(hs):
        cx = 0.55 + i*4.25
        out += r(cx, 1.38, 4.0, 5.35, fill=LT if i%2==0 else W, lc=DV)
        out += r(cx, 1.38, 4.0, 0.55, fill=hc)
        out += t(ti,  cx+0.15, 1.4,  3.7, 0.3,  sz=14, clr=W, bold=True)
        out += t(per, cx+0.15, 1.72, 3.7, 0.22, sz=10, clr='#C8C8CC')
        for j, b in enumerate(bul):
            out += t(f"· {b}", cx+0.18, 2.1+j*0.6, 3.65, 0.52, sz=11, clr=DK)
        out += r(cx, 6.45, 4.0, 0.28, fill=hc)
        out += t(f"Ziel-Umsatz:  {kpi}", cx+0.15, 6.47, 3.7, 0.24, sz=11, clr=W, bold=True, al='center')
    return wrap_slide(out, 10)

def s11_finanzen():
    out  = ftr(11)
    out += hdr("Finanzplanung 2026 – 2029",
               "Konservative Prognose  |  Alle Werte in EUR  |  vor Steuern")
    years  = ["", "Q4 2026", "GJ 2027", "GJ 2028", "GJ 2029"]
    col_xs = [0.55, 4.3,  6.42, 8.54, 10.66]
    col_ws = [3.7,  2.08, 2.08, 2.08, 2.58]
    for i, (lbl, cx, cw) in enumerate(zip(years, col_xs, col_ws)):
        out += r(cx, 1.38, cw, 0.42, fill=BK if i > 0 else LT)
        out += t(lbl, cx+0.05, 1.38, cw-0.05, 0.42, sz=12,
                 clr=W if i > 0 else MD, bold=True, al='center' if i > 0 else 'left')
    rows = [
        ("Placements (Anzahl)",      ["3","8","15","22"],                   False, False),
        ("Ø Honorar (€)",            ["50.000","55.000","58.000","60.000"],  False, False),
        ("Retained-Search-Umsatz",   ["150.000","440.000","870.000","1.320.000"], True,  False),
        ("+ Interim / Advisory",     ["90.000","80.000","110.000","160.000"],False, False),
        ("= Gesamtumsatz",           ["240.000","520.000","980.000","1.480.000"],True, True),
        ("Betriebskosten",           ["130.000","170.000","220.000","310.000"],False,False),
        ("EBIT",                     ["110.000","350.000","760.000","1.170.000"],True, True),
        ("EBIT-Marge",               ["46 %","67 %","78 %","79 %"],         False, False),
    ]
    for ri, (lbl, vals, bold_row, hl) in enumerate(rows):
        ry = 1.85 + ri*0.56
        bg = LT if hl else (VLT if ri%2==0 else W)
        out += r(0.55, ry, 12.69, 0.52, fill=bg)
        if ri in (4, 6): out += r(0.55, ry, 12.69, 0.025, fill=BK)
        out += t(lbl, 0.65, ry+0.08, 3.55, 0.38, sz=11, clr=BK if bold_row else DK, bold=bold_row)
        for ci, val in enumerate(vals):
            cx2=col_xs[ci+1]+0.05; cw2=col_ws[ci+1]-0.1
            out += t(val, cx2, ry+0.08, cw2, 0.38, sz=11, clr=BK if bold_row else DK, bold=bold_row, al='right')
    return wrap_slide(out, 11)

def s12_invest():
    out  = ftr(12)
    out += hdr("Investitionsbedarf & Mittelverwendung",
               "Finanzierungsanfrage an die Bank  |  Gesamtbedarf: € 150.000")
    out += r(0.55, 1.38, 6.2, 5.35, fill=LT)
    out += t("Mittelverwendung", 0.7, 1.48, 5.9, 0.32, sz=13, clr=BK, bold=True)
    out += r(0.7, 1.83, 5.9, 0.02, fill=DV)
    items = [("Büro & Coworking  (12 Monate)","18.000 €"),
             ("IT, CRM & Research-Tools","12.000 €"),
             ("Marke, Website, Marketing","15.000 €"),
             ("Verbände & Netzwerk-Events","8.000 €"),
             ("Versicherungen & Recht","7.000 €"),
             ("Betriebskapital (lfd. Kosten)","60.000 €"),
             ("Gründungsreserve (3 Monate)","30.000 €")]
    for i, (lbl, val) in enumerate(items):
        ry = 1.98 + i*0.58
        out += r(0.7, ry, 5.9, 0.54, fill=W if i%2==0 else LT)
        out += t(lbl, 0.82, ry+0.1, 4.1, 0.34, sz=11, clr=DK)
        out += t(val, 4.8, ry+0.1, 1.65, 0.34, sz=11, clr=BK, bold=True, al='right')
    out += r(0.7, 6.04, 5.9, 0.04, fill=BK)
    out += t("GESAMT", 0.82, 6.13, 2.0, 0.3, sz=12, clr=BK, bold=True)
    out += t("150.000 €", 4.8, 6.13, 1.65, 0.3, sz=12, clr=BK, bold=True, al='right')
    out += r(7.05, 1.38, 6.0, 5.35, fill=W, lc=DV)
    out += t("Vorgeschlagene Konditionen", 7.2, 1.48, 5.7, 0.32, sz=13, clr=BK, bold=True)
    out += r(7.2, 1.83, 5.7, 0.02, fill=DV)
    conds = [("Kreditbetrag","€ 150.000"),("Laufzeit","60 Monate (5 Jahre)"),
             ("Tilgungsfrei","12 Monate"),("Rückzahlung ab","Oktober 2027"),
             ("Monatliche Rate","ca. € 2.900 ab M13"),
             ("Sicherheit","Abtretung Forderungen + Bürgschaft"),
             ("Break-Even","Monat 8  (Juni 2027)")]
    for i, (lbl, val) in enumerate(conds):
        ry = 1.98 + i*0.58
        out += r(7.2, ry, 5.7, 0.54, fill=LT if i%2==0 else W)
        out += t(lbl, 7.32, ry+0.1, 2.4, 0.34, sz=10, clr=MD)
        out += t(val, 9.75, ry+0.08, 3.0, 0.4, sz=11, clr=BK, bold=True)
    return wrap_slide(out, 12)

def s13_risiken():
    out  = ftr(13)
    out += hdr("Risiken & Mitigationsmaßnahmen",
               "Transparente Betrachtung — strukturierte Gegenmaßnahmen")
    risks = [
        ("Lange Anlaufphase",        "Hoch","Mittel",
         "Bestandsnetzwerk ab Tag 1 aktiv; Pipeline aus 10+ Interessenten vor Start vorhanden."),
        ("Konjunktureller Abschwung","Mittel","Hoch",
         "Executive Search bleibt in Krisen kritisch; Krisen erhöhen Nachfolgebedarf. Diversifizierung federt ab."),
        ("Ausfall Partnerkooperation","Niedrig","Hoch",
         "Notarielle Regelung im Partnerschaftsvertrag; ARENA funktioniert vollständig als Solo-Praxis."),
        ("Intensiver Wettbewerb",    "Mittel","Niedrig",
         "Differenzierung über Persönlichkeit, Netzwerk & Boutique-Service — nicht über Preis."),
    ]
    lbls = {"Hoch": BK, "Mittel": DK, "Niedrig": MD}
    for i, (risk, w, imp, mitg) in enumerate(risks):
        col=i%2; row=i//2; cx=0.55+col*6.4; cy=1.38+row*2.78
        out += r(cx, cy, 6.1, 2.6, fill=LT if i%2==0 else W, lc=DV)
        out += t(risk, cx+0.2, cy+0.1, 5.7, 0.38, sz=15, clr=BK, bold=True)
        for j, (key, val) in enumerate([("Wahrsch.", w), ("Impact", imp)]):
            bx = cx + 0.2 + j * 2.0
            out += r(bx, cy+0.58, 1.8, 0.28, fill=lbls[val])
            out += t(f"{key}: {val}", bx+0.05, cy+0.58, 1.7, 0.28, sz=9, clr=W, bold=True, al='center')
        out += r(cx+0.2, cy+0.96, 5.7, 0.018, fill=DV)
        out += t(mitg, cx+0.2, cy+1.04, 5.7, 1.38, sz=11, clr=DK)
    return wrap_slide(out, 13)

def s14_roadmap():
    out  = ftr(14)
    out += hdr("Meilensteine & Roadmap", "Klare Etappenziele — Quartal für Quartal")
    ms = [
        ("Q4\n2026","Start",   ["Gründung & Anmeldung","Website live","Erste 2 Mandate aktiv"]),
        ("Q1\n2027","Aufbau",  ["3 Retainer-Mandate laufend","Partnervertrag unterzeichnet","Break-Even in Sicht"]),
        ("Q2\n2027","Wachsen", ["5. Placement","Erstes Interim-Mandat","Verbandsmitgliedschaft aktiv"]),
        ("Q3\n2027","Profil",  ["8. Placement","10 aktive Mandanten","Break-Even erreicht"]),
        ("GJ\n2028","Skalieren",["15 Placements","2. Consultant","Nachfolgemandate aktiv"]),
        ("GJ\n2029","Führen",  ["22 Placements","Vollübernahme Praxis","EBIT > €1,1 Mio."]),
    ]
    fs = [BK,BK,DK,DK,MD,MD]
    out += r(0.55, 3.9, 12.33, 0.04, fill=DV)
    for i, (per, stg, bul) in enumerate(ms):
        cx = 0.55 + i*2.1; dox = cx + 0.83
        out += r(dox, 3.77, 0.26, 0.26, fill=fs[i])
        cy = 1.38 if i%2==0 else 4.25
        out += r(cx, cy, 2.0, 2.35, fill=LT, lc=DV)
        out += r(cx, cy, 2.0, 0.42, fill=fs[i])
        out += t(per, cx+0.08, cy+0.05, 0.85, 0.38, sz=11, clr=W, bold=True)
        out += t(stg, cx+1.0,  cy+0.1,  0.85, 0.3,  sz=10, clr=W, bold=True)
        for j, b in enumerate(bul):
            out += t(f"· {b}", cx+0.1, cy+0.52+j*0.56, 1.82, 0.48, sz=9, clr=DK)
    return wrap_slide(out, 14)

def s15_branchen():
    out  = ftr(15)
    out += hdr("Zielbranchen & Zielgruppen", "Fokussierter Sektormix — Tiefe vor Breite")
    secs = [
        ("Financial\nServices",     "CFO · CRO · CEO",
         "Private Banking · PE · Versicherung · Asset Management"),
        ("Technology &\nDigital",   "CTO · CDO · CISO",
         "Software · FinTech · AI/ML · SaaS · Deep Tech"),
        ("Industrie &\nMittelstand","CEO · COO · CSO",
         "Familienunternehmen · Hidden Champions · Automotive"),
        ("Nachfolge & M&A",         "Übergabe · Integration",
         "Nachfolgeplanung · Post-Merger-Führung · PE-Portfolio"),
    ]
    fs2 = [BK,DK,MD,BK]
    for i, (sec, roles, desc) in enumerate(secs):
        cx=0.55+(i%2)*6.4; cy=1.38+(i//2)*2.85
        out += r(cx, cy, 6.1, 2.65, fill=LT if i%2==0 else W, lc=DV)
        out += r(cx, cy, 6.1, 0.52, fill=fs2[i])
        out += t(sec,   cx+0.2, cy+0.07, 5.7, 0.44, sz=17, clr=W, bold=True, fl=True)
        out += t("Zielpositionen", cx+0.2, cy+0.65, 2.0, 0.28, sz=9, clr=MD, italic=True)
        out += t(roles, cx+0.2, cy+0.93, 5.7, 0.32, sz=12, clr=BK, bold=True)
        out += r(cx+0.2, cy+1.27, 5.7, 0.018, fill=DV)
        out += t(desc,  cx+0.2, cy+1.37, 5.7, 0.55, sz=11, clr=MD)
    return wrap_slide(out, 15)

def s16_fazit():
    out  = ftr(16)
    out += r(0.55, 0.45, 0.04, 6.35, fill=BK)
    out += t("Starten wir\ngemeinsam.",          0.9, 0.5, 11, 2.0, sz=54, clr=BK, fl=True)
    out += t("ARENA Executive Search ist bereit.", 0.9, 2.5, 10, 0.55, sz=22, clr=MD, fl=True)
    out += r(0.9, 3.15, 8.0, 0.025, fill=DV)
    buls = [
        "Erfahrener Gründer — 30+ Jahre · 1.500+ Kontakte · 200+ Placements",
        "Klares Geschäftsmodell — Retained Search mit sofort aktivierbarem Deal-Flow",
        "Realistische Zahlen — Break-Even Monat 8, EBIT > €1 Mio. ab Jahr 3",
        "Doppelte Sicherheit — Solo-fähig + Partnerschaft als strategischer Upside",
        "Überschaubarer Kapitalbedarf — € 150.000 mit klar geplanter Tilgung",
    ]
    for i, b in enumerate(buls):
        out += t(b, 0.9, 3.35+i*0.5, 11.8, 0.42, sz=13, clr=DK)
    out += r(0.9, 5.82, 12.0, 0.022, fill=DV)
    out += t("Kontakt", 0.9, 5.97, 2.0, 0.28, sz=10, clr=MD, bold=True)
    out += t("Aaron Arena   ·   aaron.arena@arena-executive-search.de   ·   +49 (0) 170 — — — — — —",
             0.9, 6.28, 12.0, 0.3, sz=12, clr=BK)
    out += t("www.arena-executive-search.de   ·   LinkedIn: /in/aaronarena",
             0.9, 6.62, 10.0, 0.28, sz=11, clr=MD)
    return wrap_slide(out, 16)

# ── Haupt-Generator ────────────────────────────────────────────────────────────

SLIDE_TITLES = [
    "Cover", "Inhaltsverzeichnis", "Die Marktchance", "Der Gründer",
    "Marktanalyse DACH", "Geschäftsmodell", "Leistungsportfolio", "Warum ARENA?",
    "Partnerschaftsmodell", "Wachstumsstrategie", "Finanzplanung",
    "Investitionsbedarf", "Risiken", "Roadmap", "Zielbranchen", "Fazit",
]

def generate_html(output_path):
    all_slides = (
        s01_cover() + s02_agenda()   + s03_chance()  + s04_founder() +
        s05_markt() + s06_modell()   + s07_leistungen() + s08_usp()  +
        s09_partner() + s10_wachstum() + s11_finanzen()  + s12_invest() +
        s13_risiken() + s14_roadmap() + s15_branchen()  + s16_fazit()
    )

    dots = ''.join(
        f'<button class="dot{"  active" if i==0 else ""}" '
        f'onclick="go({i})" title="{SLIDE_TITLES[i]}"></button>'
        for i in range(16)
    )

    nav_items = ''.join(
        f'<li class="nav-item" onclick="go({i})">'
        f'<span class="nav-num">{i+1:02d}</span>'
        f'<span class="nav-title">{SLIDE_TITLES[i]}</span></li>'
        for i in range(16)
    )

    css = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    html,body{width:100%;height:100%;overflow:hidden;background:#111;
      font-family:Calibri,-apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif}

    #canvas-wrap{
      position:fixed;inset:0;display:flex;justify-content:center;align-items:center}

    #canvas{
      position:relative;width:1334px;height:750px;
      transform-origin:top left;overflow:hidden;background:#fff;
      box-shadow:0 20px 80px rgba(0,0,0,.6)}

    .slide{
      position:absolute;inset:0;display:none;background:#fff;
      opacity:0;transition:opacity .35s ease}
    .slide.active{display:block;opacity:1}

    /* ── Nav bar ── */
    #nav{position:fixed;bottom:0;left:0;right:0;height:40px;
      display:flex;align-items:center;justify-content:space-between;
      padding:0 24px;background:rgba(0,0,0,.75);backdrop-filter:blur(6px);
      z-index:100}
    #nav button{
      background:none;border:none;color:#fff;font-size:18px;
      cursor:pointer;padding:4px 12px;opacity:.8;transition:opacity .2s}
    #nav button:hover{opacity:1}
    #counter{color:rgba(255,255,255,.7);font-size:12px;min-width:56px;text-align:center}
    #slide-label{color:rgba(255,255,255,.6);font-size:11px;max-width:320px;
      text-align:center;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
    .dots{display:flex;gap:5px;align-items:center}
    .dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.35);
      border:none;cursor:pointer;padding:0;transition:all .2s}
    .dot.active{background:#fff;transform:scale(1.3)}
    .dot:hover{background:rgba(255,255,255,.75)}

    /* ── Slide menu (links) ── */
    #menu-toggle{position:fixed;top:12px;left:12px;z-index:200;
      background:rgba(0,0,0,.5);border:none;color:#fff;width:32px;height:32px;
      border-radius:6px;cursor:pointer;font-size:16px;backdrop-filter:blur(4px)}
    #menu{position:fixed;top:0;left:-260px;width:260px;height:100vh;
      background:rgba(20,20,20,.95);backdrop-filter:blur(10px);z-index:150;
      transition:left .3s ease;overflow-y:auto;padding-top:52px}
    #menu.open{left:0}
    .nav-item{display:flex;align-items:center;gap:10px;padding:10px 16px;
      cursor:pointer;color:rgba(255,255,255,.7);font-size:12px;
      transition:background .15s;border-bottom:1px solid rgba(255,255,255,.06)}
    .nav-item:hover{background:rgba(255,255,255,.08);color:#fff}
    .nav-item.active{background:rgba(255,255,255,.14);color:#fff}
    .nav-num{color:rgba(255,255,255,.4);font-size:10px;min-width:20px}
    .nav-title{font-size:12px}

    /* ── Progress bar ── */
    #progress{position:fixed;top:0;left:0;height:2px;
      background:#fff;transition:width .3s ease;z-index:200}

    /* ── Keyboard hint ── */
    #hint{position:fixed;top:12px;right:12px;color:rgba(255,255,255,.4);
      font-size:10px;text-align:right;z-index:200;pointer-events:none}

    /* ── Fullscreen button ── */
    #fs{position:fixed;top:12px;right:12px;z-index:200;
      background:rgba(0,0,0,.5);border:none;color:rgba(255,255,255,.6);
      width:28px;height:28px;border-radius:5px;cursor:pointer;font-size:13px}
    #fs:hover{color:#fff}
    """

    js = """
    let cur = 0;
    const N = 16;
    const slides = document.querySelectorAll('.slide');
    const dots   = document.querySelectorAll('.dot');
    const navItems = document.querySelectorAll('.nav-item');
    const titles = """ + str(SLIDE_TITLES).replace("'", '"') + """;

    function go(n) {
      slides[cur].classList.remove('active');
      dots[cur].classList.remove('active');
      navItems[cur].classList.remove('active');
      cur = ((n % N) + N) % N;
      slides[cur].classList.add('active');
      dots[cur].classList.add('active');
      navItems[cur].classList.add('active');
      document.getElementById('counter').textContent = (cur+1) + ' / ' + N;
      document.getElementById('slide-label').textContent = titles[cur];
      document.getElementById('progress').style.width = ((cur+1)/N*100) + '%';
    }

    document.addEventListener('keydown', ev => {
      if (ev.key==='ArrowRight'||ev.key==='ArrowDown'||ev.key===' ') {ev.preventDefault();go(cur+1);}
      if (ev.key==='ArrowLeft' ||ev.key==='ArrowUp')  {ev.preventDefault();go(cur-1);}
      if (ev.key==='Escape') document.getElementById('menu').classList.remove('open');
      if (ev.key==='f'||ev.key==='F') toggleFS();
    });

    // Click left/right half of slide to navigate
    document.getElementById('canvas').addEventListener('click', ev => {
      const half = ev.currentTarget.getBoundingClientRect().width / 2;
      if (ev.clientX - ev.currentTarget.getBoundingClientRect().left > half) go(cur+1);
      else go(cur-1);
    });

    // Touch swipe
    let tx0 = 0;
    document.addEventListener('touchstart', ev => { tx0 = ev.touches[0].clientX; });
    document.addEventListener('touchend',   ev => {
      const dx = ev.changedTouches[0].clientX - tx0;
      if (Math.abs(dx) > 50) go(dx < 0 ? cur+1 : cur-1);
    });

    function scaleCanvas() {
      const wrap = document.getElementById('canvas-wrap');
      const cnv  = document.getElementById('canvas');
      const sx = wrap.clientWidth  / 1334;
      const sy = wrap.clientHeight / 750;
      const s  = Math.min(sx, sy) * 0.97;
      const tx = (wrap.clientWidth  - 1334 * s) / 2;
      const ty = (wrap.clientHeight - 750  * s) / 2;
      cnv.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`;
    }

    window.addEventListener('resize', scaleCanvas);
    scaleCanvas();

    document.getElementById('menu-toggle').addEventListener('click', ev => {
      ev.stopPropagation();
      document.getElementById('menu').classList.toggle('open');
    });
    document.addEventListener('click', () => {
      document.getElementById('menu').classList.remove('open');
    });
    document.getElementById('menu').addEventListener('click', ev => ev.stopPropagation());

    function toggleFS() {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    }
    document.getElementById('fs').addEventListener('click', toggleFS);

    // Init
    go(0);
    """

    html_out = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ARENA Executive Search — Businessplan 2026</title>
<style>{css}</style>
</head>
<body>

<div id="progress"></div>
<button id="menu-toggle" title="Folienliste">☰</button>
<button id="fs" title="Vollbild (F)">⛶</button>

<nav id="menu">
  <ul style="list-style:none">{nav_items}</ul>
</nav>

<div id="canvas-wrap">
  <div id="canvas">
    {all_slides}
  </div>
</div>

<div id="nav">
  <button onclick="go(cur-1)" title="Zurück (←)">&#8592;</button>
  <div style="display:flex;align-items:center;gap:12px">
    <span id="counter">1 / 16</span>
    <div class="dots">{dots}</div>
    <span id="slide-label">Cover</span>
  </div>
  <button onclick="go(cur+1)" title="Weiter (→)">&#8594;</button>
</div>

<script>{js}</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f"✓  HTML gespeichert: {output_path}")
    print(f"   Größe: {os.path.getsize(output_path)/1024:.0f} KB")
    return output_path


if __name__ == "__main__":
    out = "/home/user/ARENA_Executive_Search_Businessplan_2026.html"
    generate_html(out)
    print(f"\n→  Jetzt im Browser öffnen: file://{out}")
