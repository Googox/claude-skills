#!/usr/bin/env python3
"""
ARENA Executive Search — Businessplan 2026–2029
Professionelle PowerPoint-Präsentation (Apple-Style, schwarz/grau/weiß)
Aaron Arena | Start: 01.10.2026
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import os, sys

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN-SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

SW = Inches(13.33)   # 16:9 Breite
SH = Inches(7.5)     # 16:9 Höhe

# Farbpalette — Apple / Classic Professional
NAVY      = RGBColor(0x0F, 0x1B, 0x35)   # Tiefdunkel-Navy (Titelfolien)
NAVY_MID  = RGBColor(0x1E, 0x35, 0x5E)   # Mittel-Navy
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
APPLE_BK  = RGBColor(0x1D, 0x1D, 0x1F)   # Apple-Schwarz
DK_GREY   = RGBColor(0x3A, 0x3A, 0x3C)   # Dunkelgrau
MD_GREY   = RGBColor(0x6E, 0x6E, 0x73)   # Mittelgrau
LT_GREY   = RGBColor(0xF5, 0xF5, 0xF7)   # Hellgrau (Apple-Hintergrund)
VLT_GREY  = RGBColor(0xFA, 0xFA, 0xFC)   # Sehr hellgrau
DIVIDER   = RGBColor(0xD2, 0xD2, 0xD7)   # Trennlinie
GOLD      = RGBColor(0xAA, 0x8F, 0x5C)   # Warm-Gold (Premium-Akzent)
GOLD_BG   = RGBColor(0xF8, 0xF3, 0xE8)   # Gold-Hintergrund
CARD_BG   = RGBColor(0xF2, 0xF2, 0xF7)   # Kartenhintergrund

F  = 'Calibri'
FL = 'Calibri Light'

_sid = [0]
def _nid():
    _sid[0] += 1
    return _sid[0]

def _rst():
    _sid[0] = 0

# ─────────────────────────────────────────────────────────────────────────────
# PRIMITIVE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def new_slide(prs, bg=WHITE):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    f = s.background.fill; f.solid(); f.fore_color.rgb = bg
    return s

def rect(s, x, y, w, h, fill=None, lc=None, lw=0.5):
    sh = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    else:     sh.fill.background()
    if lc:    sh.line.color.rgb = lc; sh.line.width = Pt(lw)
    else:     sh.line.fill.background()
    return sh

def txt(s, text, x, y, w, h, sz=16, clr=None, bold=False, italic=False,
        align=PP_ALIGN.LEFT, fn=F, wrap=True):
    if clr is None: clr = APPLE_BK
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text; r.font.name = fn; r.font.size = Pt(sz)
    r.font.color.rgb = clr; r.font.bold = bold; r.font.italic = italic
    return tb

def txb(s, rows, x, y, w, h, wrap=True):
    """rows = list of (text, size, color, bold, align, italic, space_before)"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    for i, row in enumerate(rows):
        text, sz, clr, bold, align, italic = row[:6]
        sp = row[6] if len(row) > 6 else 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if sp: p.space_before = Pt(sp)
        r = p.add_run()
        r.text = text; r.font.name = F; r.font.size = Pt(sz)
        r.font.color.rgb = clr or APPLE_BK
        r.font.bold = bold; r.font.italic = italic
    return tb

def top_bar(s, color=NAVY, h=0.07):
    return rect(s, 0, 0, 13.33, h, fill=color)

def footer(s, slide_num, total=16):
    rect(s, 0, 7.25, 13.33, 0.25, fill=LT_GREY)
    txt(s, "ARENA Executive Search  |  Businessplan 2026–2029", 0.4, 7.27, 9, 0.2,
        sz=8, clr=MD_GREY)
    txt(s, f"{slide_num} / {total}", 12.5, 7.27, 0.8, 0.2,
        sz=8, clr=MD_GREY, align=PP_ALIGN.RIGHT)

def slide_title(s, title, subtitle=None, y=0.25):
    txt(s, title, 0.5, y, 12.3, 0.55, sz=26, clr=APPLE_BK, fn=FL)
    if subtitle:
        rect(s, 0.5, y + 0.55, 1.2, 0.04, fill=GOLD)
        txt(s, subtitle, 0.5, y + 0.65, 9, 0.3, sz=13, clr=MD_GREY)

def kpi_card(s, value, label, x, y, w=2.8, h=1.5, val_sz=40, label_sz=11):
    rect(s, x, y, w, h, fill=CARD_BG)
    txt(s, value, x+0.15, y+0.1, w-0.3, 0.7, sz=val_sz, clr=NAVY, bold=True,
        fn=FL, align=PP_ALIGN.CENTER)
    txt(s, label, x+0.15, y+0.78, w-0.3, 0.65, sz=label_sz, clr=MD_GREY,
        align=PP_ALIGN.CENTER, wrap=True)
    return s

def fade_transition(slide):
    ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    ex = slide.element.find(f'{{{ns}}}transition')
    if ex is not None: slide.element.remove(ex)
    xml = f'<p:transition xmlns:p="{ns}" spd="fast"><p:fade/></p:transition>'
    slide.element.append(etree.fromstring(xml))

# ─────────────────────────────────────────────────────────────────────────────
# ANIMATIONS
# ─────────────────────────────────────────────────────────────────────────────

def build_timing(specs):
    """
    specs: list of (shape_id, 'fade'|'fly_up', click_grp 1..n, delay_ms, dur_ms)
    Returns lxml Element for p:timing
    """
    _rst()
    ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'

    def E(tag, **a):
        e = etree.Element(f'{{{ns}}}{tag}')
        for k, v in a.items(): e.set(k, str(v))
        return e

    from collections import defaultdict
    grps = defaultdict(list)
    for sp_id, anim, grp, delay, dur in specs:
        grps[grp].append((sp_id, anim, delay, dur))

    timing = E('timing')
    tnLst  = E('tnLst'); timing.append(tnLst)
    par0   = E('par');   tnLst.append(par0)
    cTn0   = E('cTn', id=_nid(), dur='indefin', restart='whenNotActive', nodeType='tmRoot')
    par0.append(cTn0)
    ch0    = E('childTnLst'); cTn0.append(ch0)
    seq    = E('seq', concurrent='1', nextAc='seek'); ch0.append(seq)
    cTnS   = E('cTn', id=_nid(), dur='indefin', nodeType='mainSeq'); seq.append(cTnS)
    chS    = E('childTnLst'); cTnS.append(chS)

    for grp_idx in sorted(grps.keys()):
        items = grps[grp_idx]
        par_cg = E('par'); chS.append(par_cg)
        cTn_cg = E('cTn', id=_nid(), fill='hold'); par_cg.append(cTn_cg)
        sc1 = E('stCondLst'); cTn_cg.append(sc1); sc1.append(E('cond', delay='indefin'))
        ch_cg = E('childTnLst'); cTn_cg.append(ch_cg)
        par_in = E('par'); ch_cg.append(par_in)
        cTn_in = E('cTn', id=_nid(), fill='hold'); par_in.append(cTn_in)
        sc2 = E('stCondLst'); cTn_in.append(sc2); sc2.append(E('cond', delay='0'))
        ch_in = E('childTnLst'); cTn_in.append(ch_in)

        for i, (sp_id, anim, delay, dur) in enumerate(items):
            nt = 'clickEffect' if i == 0 else 'withEffect'
            par_a = E('par'); ch_in.append(par_a)
            preset = '10' if anim == 'fade' else '2'
            sub    = '0'  if anim == 'fade' else '8'
            cTn_a  = E('cTn', id=_nid(), presetID=preset, presetClass='entr',
                        presetSubtype=sub, fill='hold', grpId=str(grp_idx-1), nodeType=nt)
            par_a.append(cTn_a)
            sc3 = E('stCondLst'); cTn_a.append(sc3); sc3.append(E('cond', delay=str(delay)))
            ch_a = E('childTnLst'); cTn_a.append(ch_a)

            # visibility set
            set_el = E('set'); ch_a.append(set_el)
            cbS = E('cBhvr'); set_el.append(cbS)
            cbS.append(E('cTn', id=_nid(), dur='1'))
            tS = E('tgtEl'); cbS.append(tS); tS.append(E('spTgt', spid=str(sp_id)))
            anl = E('attrNameLst'); cbS.append(anl)
            an  = E('attrName'); an.text = 'style.visibility'; anl.append(an)
            to_el = E('to'); set_el.append(to_el)
            sv = E('strVal', val='visible'); to_el.append(sv)

            # animEffect / fade
            if anim == 'fade':
                ae = E('animEffect', transition='in', filter='fade'); ch_a.append(ae)
            else:
                ae = E('animEffect', transition='in', filter='wipe(up)'); ch_a.append(ae)
            cbE = E('cBhvr'); ae.append(cbE)
            cbE.append(E('cTn', id=_nid(), dur=str(dur)))
            tE = E('tgtEl'); cbE.append(tE); tE.append(E('spTgt', spid=str(sp_id)))

    prev = E('prevCondLst'); seq.append(prev)
    cond_p = E('cond', evt='onPrevClick', delay='0'); prev.append(cond_p)
    cond_p.append(E('tn'))
    timing.append(E('bldLst'))
    return timing

def apply_animations(slide, specs):
    if not specs: return
    ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    ex = slide.element.find(f'{{{ns}}}timing')
    if ex is not None: slide.element.remove(ex)
    slide.element.append(build_timing(specs))

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — COVER
# ─────────────────────────────────────────────────────────────────────────────

def slide_cover(prs):
    s = new_slide(prs, bg=NAVY)
    # Dezente graue Linie links
    rect(s, 0, 0, 0.06, 7.5, fill=GOLD)

    # Haupttitel
    t1 = txt(s, "ARENA", 1.2, 1.8, 11, 1.4, sz=88, clr=WHITE, bold=False, fn=FL,
             align=PP_ALIGN.LEFT)
    # Untertitel Executive Search
    t2 = txt(s, "Executive Search", 1.2, 3.1, 11, 0.7, sz=36, clr=GOLD, fn=FL,
             align=PP_ALIGN.LEFT)
    # Goldene Trennlinie
    ln = rect(s, 1.2, 3.85, 5.5, 0.05, fill=GOLD)
    # Tagline
    t3 = txt(s, "Die richtigen Führungspersönlichkeiten.", 1.2, 4.05, 10, 0.5,
             sz=18, clr=WHITE, fn=FL, align=PP_ALIGN.LEFT)
    t4 = txt(s, "Zur richtigen Zeit. Mit dem richtigen Partner.", 1.2, 4.5, 10, 0.45,
             sz=14, clr=RGBColor(0xB0, 0xB8, 0xC8), fn=FL, align=PP_ALIGN.LEFT)
    # Datum / Person
    t5 = txt(s, "Aaron Arena  |  Businessplan 2026 – 2029  |  Oktober 2026",
             1.2, 6.6, 11, 0.4, sz=11, clr=RGBColor(0x88, 0x96, 0xB0), align=PP_ALIGN.LEFT)
    # Vertikaler Text rechts
    t6 = txt(s, "CONFIDENTIAL", 12.3, 3.5, 1.2, 0.35, sz=8,
             clr=RGBColor(0x55, 0x60, 0x78), align=PP_ALIGN.RIGHT, italic=True)

    fade_transition(s)
    apply_animations(s, [
        (t1.shape_id, 'fade', 1, 0,   700),
        (t2.shape_id, 'fade', 1, 500, 600),
        (ln.shape_id, 'fade', 1, 900, 400),
        (t3.shape_id, 'fade', 1,1100, 600),
        (t4.shape_id, 'fade', 1,1600, 600),
        (t5.shape_id, 'fade', 1,2200, 500),
    ])
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — INHALTSVERZEICHNIS
# ─────────────────────────────────────────────────────────────────────────────

def slide_agenda(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 2)

    slide_title(s, "Inhaltsverzeichnis")

    items = [
        ("01", "Die Marktchance"),
        ("02", "Der Gründer – Aaron Arena"),
        ("03", "Marktanalyse DACH"),
        ("04", "Geschäftsmodell & Einnahmen"),
        ("05", "Leistungsportfolio"),
        ("06", "Wettbewerbsvorteile (USP)"),
        ("07", "Partnerschaftsmodell – Nachfolgelösung"),
        ("08", "Wachstumsstrategie"),
        ("09", "Finanzplanung 2026 – 2029"),
        ("10", "Investitionsbedarf & Mittelverwendung"),
        ("11", "Meilensteine & Roadmap"),
        ("12", "Fazit & Nächste Schritte"),
    ]

    col_w = 5.8
    for idx, (num, label) in enumerate(items):
        col = idx // 6
        row = idx % 6
        x = 0.5 + col * 6.5
        y = 1.4 + row * 0.88

        # Nummernbox
        nb = rect(s, x, y + 0.03, 0.42, 0.42, fill=NAVY)
        txt(s, num, x, y + 0.03, 0.42, 0.42, sz=11, clr=WHITE, bold=True,
            align=PP_ALIGN.CENTER)
        txt(s, label, x + 0.55, y + 0.05, col_w - 0.55, 0.38, sz=14,
            clr=APPLE_BK, fn=F)
        rect(s, x + 0.55, y + 0.46, col_w - 0.6, 0.015, fill=DIVIDER)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — DIE MARKTCHANCE
# ─────────────────────────────────────────────────────────────────────────────

def slide_chance(prs):
    s = new_slide(prs, bg=NAVY)
    rect(s, 0, 0, 0.06, 7.5, fill=GOLD)
    footer(s, 3)

    t0 = txt(s, "Der Moment ist jetzt.", 1.2, 0.8, 11, 1.0, sz=44, clr=WHITE, fn=FL)
    t_sub = txt(s, "Executive Search in Deutschland erlebt eine strukturelle Transformation.",
                1.2, 1.75, 11, 0.4, sz=14, clr=RGBColor(0xB0,0xB8,0xC8), fn=FL)

    rect(s, 1.2, 2.3, 11, 0.04, fill=RGBColor(0x3A,0x4A,0x6A))

    # KPI-Karten
    kpis = [
        ("€ 2,8 Mrd.", "Executive-Search-\nMarktvolumen\nDeutschland 2026"),
        ("+11 %",      "Jährliches\nMarktwachstum\n(CAGR 2023–2028)"),
        ("67 %",       "C-Level-Positionen\nwerden diskret\nbesetzt"),
        ("4,2 Jahre",  "Ø Amtszeit\nC-Level-Manager\nbevor Wechsel"),
    ]
    for i, (val, lbl) in enumerate(kpis):
        cx = 1.2 + i * 2.85
        bg = rect(s, cx, 2.6, 2.65, 1.85, fill=RGBColor(0x1A,0x2B,0x4D))
        vt = txt(s, val, cx+0.15, 2.7, 2.35, 0.75, sz=30, clr=GOLD, bold=True,
                 fn=FL, align=PP_ALIGN.CENTER)
        lt = txt(s, lbl, cx+0.1, 3.42, 2.45, 0.95, sz=11, clr=RGBColor(0xB0,0xB8,0xC8),
                 align=PP_ALIGN.CENTER, wrap=True)

    tq = txt(s, "Quellen: BDU Executive Search Report 2026 | Statista | Kienbaum Executive Panel 2026",
             1.2, 6.8, 11, 0.3, sz=8, clr=RGBColor(0x55,0x60,0x78), italic=True)

    fade_transition(s)
    apply_animations(s, [
        (t0.shape_id,   'fade', 1,   0, 700),
        (t_sub.shape_id,'fade', 1, 600, 500),
    ])
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — DER GRÜNDER
# ─────────────────────────────────────────────────────────────────────────────

def slide_founder(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 4)

    slide_title(s, "Der Gründer — Aaron Arena")

    # Linke Spalte — persönliche Highlights
    rect(s, 0.5, 1.35, 3.8, 5.6, fill=CARD_BG)
    txt(s, "30+", 0.65, 1.55, 3.5, 0.9, sz=62, clr=NAVY, bold=False, fn=FL,
        align=PP_ALIGN.CENTER)
    txt(s, "Jahre Erfahrung in\nFührungsrekrutierung", 0.65, 2.4, 3.5, 0.55,
        sz=12, clr=MD_GREY, align=PP_ALIGN.CENTER, wrap=True)
    rect(s, 1.2, 3.05, 2.5, 0.04, fill=DIVIDER)

    highlights = [
        ("►  Seniorberater bei Top-3-Personalberatung"),
        ("►  200+ erfolgreiche C-Level-Placements"),
        ("►  Netzwerk: 1.500+ Entscheider DACH"),
        ("►  Sektorfokus: Finance, Tech, Industrie"),
        ("►  Ausbildung: BWL, Personalmanagement"),
        ("►  Mehrsprachig: DE / EN / IT"),
    ]
    for i, h in enumerate(highlights):
        txt(s, h, 0.65, 3.2 + i * 0.47, 3.5, 0.4, sz=11, clr=DK_GREY)

    # Rechte Spalte — Karriere-Timeline
    rect(s, 4.7, 1.35, 8.2, 5.6, fill=WHITE)

    timeline = [
        ("2026 →", "GRÜNDUNG", "ARENA Executive Search", NAVY),
        ("2019–2026", "SENIOR PARTNER", "Boutique Executive Search, München", DK_GREY),
        ("2012–2019", "DIRECTOR SEARCH", "Internationale Personalberatung, Frankfurt", DK_GREY),
        ("2005–2012", "SENIOR CONSULTANT", "DACH-Region, Finanz- & Technologiesektor", DK_GREY),
        ("1995–2005", "CAREER START", "Unternehmensberatung & Personalwesen", MD_GREY),
    ]

    for i, (year, role, desc, clr) in enumerate(timeline):
        yp = 1.45 + i * 1.0
        # Linie
        rect(s, 4.85, yp, 0.04, 0.85, fill=GOLD if i == 0 else DIVIDER)
        # Dot
        rect(s, 4.72, yp + 0.07, 0.18, 0.18, fill=GOLD if i == 0 else DIVIDER)
        txt(s, year, 5.1, yp, 1.6, 0.3, sz=10, clr=GOLD if i==0 else MD_GREY,
            bold=(i==0))
        txt(s, role, 5.1, yp + 0.28, 7.5, 0.3, sz=12, clr=clr, bold=True)
        txt(s, desc, 5.1, yp + 0.56, 7.5, 0.35, sz=11, clr=MD_GREY)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — MARKTANALYSE DACH
# ─────────────────────────────────────────────────────────────────────────────

def slide_markt(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 5)

    slide_title(s, "Marktanalyse — Executive Search DACH",
                "Strukturelles Wachstum in einem hochmargigen Nischenmarkt")

    # Linke Spalte: Marktgrösse
    rect(s, 0.5, 1.5, 6.0, 5.1, fill=LT_GREY)
    txt(s, "Marktvolumen Executive Search DACH", 0.65, 1.6, 5.7, 0.35,
        sz=12, clr=DK_GREY, bold=True)

    bars = [
        ("2022", 1.8, "€ 2,0 Mrd."),
        ("2023", 2.1, "€ 2,2 Mrd."),
        ("2024", 2.4, "€ 2,5 Mrd."),
        ("2025e", 2.65, "€ 2,65 Mrd."),
        ("2026e", 3.0, "€ 2,8 Mrd."),
        ("2027p", 3.4, "€ 3,1 Mrd."),
    ]
    max_h = 2.5
    bar_w = 0.65
    for i, (yr, val, lbl) in enumerate(bars):
        bh = (val / 3.4) * max_h
        bx = 0.7 + i * 0.88
        by = 5.6 - bh
        highlight = (i >= 3)
        fill_c = NAVY if highlight else RGBColor(0xB0,0xB8,0xC8)
        rect(s, bx, by, bar_w, bh, fill=fill_c)
        txt(s, lbl, bx - 0.05, by - 0.35, 0.75, 0.3, sz=8,
            clr=NAVY if highlight else MD_GREY, align=PP_ALIGN.CENTER)
        txt(s, yr, bx - 0.01, 5.65, 0.72, 0.25, sz=9,
            clr=DK_GREY, align=PP_ALIGN.CENTER)

    txt(s, "* e = geschätzt  |  p = Prognose  |  Quelle: BDU, Statista 2026",
        0.65, 6.45, 5.7, 0.2, sz=8, clr=MD_GREY, italic=True)

    # Rechte Spalte: Treiber
    txt(s, "Wachstumstreiber", 7.0, 1.5, 6.2, 0.35, sz=13, clr=APPLE_BK, bold=True)
    rect(s, 7.0, 1.88, 2.5, 0.03, fill=GOLD)

    drivers = [
        ("🏢", "Digitale Transformation",
         "70 % der Unternehmen suchen CDO/CTO-Profile – Nachfrage +34 %"),
        ("♻", "Nachfolgeplanung",
         "Baby-Boomer-Welle: 580.000 KMU-Übergaben bis 2030"),
        ("🌍", "Internationalisierung",
         "Grenzübergreifende Searches +28 % in D/A/CH"),
        ("⚖️", "ESG & Compliance",
         "Regulierung treibt Nachfrage nach Risiko- & Nachhaltigkeitsexperten"),
    ]
    for i, (icon, title, desc) in enumerate(drivers):
        yp = 2.1 + i * 1.2
        rect(s, 7.0, yp, 6.2, 1.1, fill=CARD_BG)
        txt(s, title, 7.15, yp + 0.07, 5.9, 0.32, sz=13, clr=NAVY, bold=True)
        txt(s, desc, 7.15, yp + 0.42, 5.9, 0.55, sz=11, clr=DK_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — GESCHÄFTSMODELL
# ─────────────────────────────────────────────────────────────────────────────

def slide_modell(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 6)

    slide_title(s, "Geschäftsmodell & Einnahmen",
                "Drei Säulen — Retained Search als Kern")

    modelle = [
        ("RETAINED\nSEARCH", "Kernleistung",
         ["Exklusives Mandat", "Retainer 1/3 upfront", "Milestone + Success Fee",
          "Ø Projektlaufzeit 10–14 Wochen", "Gebühr: 28–33 % des\nJahresgehalts"],
         NAVY, WHITE, "60 %"),
        ("EXECUTIVE\nINTERIM", "Ergänzend",
         ["Sofortbesetzung Führungslücke", "3–12 Monate Laufzeit",
          "Tagesatz €1.200–2.200", "Keine Exklusivität nötig",
          "Schneller ROI für Kunden"],
         DK_GREY, WHITE, "25 %"),
        ("ADVISORY &\nASSESSMENT", "Ergänzend",
         ["C-Suite-Potenzialanalysen", "Nachfolgeplanung intern",
          "Karriere-Coaching Executives", "Workshop-Formate",
          "Festpreis €8.000–18.000"],
         CARD_BG, APPLE_BK, "15 %"),
    ]

    for i, (title, badge, bullets, bg, tc, share) in enumerate(modelle):
        cx = 0.5 + i * 4.25
        rect(s, cx, 1.5, 4.0, 5.2, fill=bg)
        txt(s, title, cx+0.15, 1.65, 3.7, 0.9, sz=20, clr=tc, bold=True,
            fn=FL, align=PP_ALIGN.CENTER, wrap=True)
        # Badge
        rect(s, cx + 1.2, 2.55, 1.6, 0.32, fill=GOLD if i==0 else DIVIDER)
        txt(s, badge, cx+1.2, 2.55, 1.6, 0.32, sz=9, clr=NAVY if i>0 else WHITE,
            bold=True, align=PP_ALIGN.CENTER)
        # Bullets
        for j, b in enumerate(bullets):
            txt(s, f"• {b}", cx+0.2, 3.05 + j*0.55, 3.6, 0.5, sz=11,
                clr=tc if i < 2 else DK_GREY, wrap=True)
        # Share
        rect(s, cx, 6.4, 4.0, 0.3, fill=GOLD if i==0 else RGBColor(0x88,0x88,0x90))
        txt(s, f"Umsatzanteil: {share}", cx+0.1, 6.41, 3.8, 0.26, sz=10,
            clr=WHITE, bold=True, align=PP_ALIGN.CENTER)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — LEISTUNGSPORTFOLIO
# ─────────────────────────────────────────────────────────────────────────────

def slide_leistungen(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 7)

    slide_title(s, "Leistungsportfolio", "Was wir für unsere Mandanten leisten")

    services = [
        ("C-SUITE SEARCH", "Vorstand, Geschäftsführung, C-Level",
         "Diskreter, vollumfänglicher Suchprozess für höchste Führungsebenen. "
         "Longlist → Assessment → Onboarding-Begleitung. "
         "Erfolgsquote > 95 %. Garantiezeitraum 12 Monate."),
        ("BOARD ADVISORY", "Aufsichtsrat, Beirat, Advisory Board",
         "Rekrutierung und Beratung für Kontrollgremien. "
         "Governance, Diversität und Kompetenzprofil-Analyse. "
         "Wachsend regulatorische Anforderungen als Treiber."),
        ("EXECUTIVE INTERIM", "Überbrückung & Transformation",
         "Kurzfristige Top-Führungskräfte für Restrukturierungen, "
         "M&A-Projekte und Vakanzüberbrückungen. "
         "Netzwerk von 120+ geprüften Interim-Executives."),
        ("SUCCESSION PLANNING", "Nachfolge & Talentpipeline",
         "Systematische Nachfolgeplanung für Inhaber, "
         "Familienunternehmen und PE-Portfolios. "
         "Begleitung über 12–36 Monate Transitionszeitraum."),
    ]

    for i, (title, sub, desc) in enumerate(services):
        col = i % 2
        row = i // 2
        cx = 0.5 + col * 6.4
        cy = 1.5 + row * 2.65

        rect(s, cx, cy, 6.1, 2.45, fill=CARD_BG)
        rect(s, cx, cy, 0.07, 2.45, fill=NAVY if i < 2 else GOLD)
        txt(s, title, cx+0.25, cy+0.12, 5.6, 0.38, sz=14, clr=NAVY, bold=True)
        txt(s, sub,   cx+0.25, cy+0.52, 5.6, 0.28, sz=11, clr=GOLD, italic=True)
        rect(s, cx+0.25, cy+0.82, 5.5, 0.025, fill=DIVIDER)
        txt(s, desc,  cx+0.25, cy+0.92, 5.7, 1.3,  sz=11, clr=DK_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — WETTBEWERBSVORTEILE (USP)
# ─────────────────────────────────────────────────────────────────────────────

def slide_usp(prs):
    s = new_slide(prs, bg=NAVY)
    rect(s, 0, 0, 0.06, 7.5, fill=GOLD)
    footer(s, 8)

    t_h = txt(s, "Warum ARENA?", 1.2, 0.35, 11, 0.7, sz=36, clr=WHITE, fn=FL)
    t_s = txt(s, "Vier strategische Differenzierungsmerkmale gegenüber Wettbewerbern",
              1.2, 0.95, 10, 0.35, sz=13, clr=RGBColor(0xB0,0xB8,0xC8), fn=FL)

    usps = [
        ("01", "Tiefes Branchennetzwerk",
         "30+ Jahre aufgebautes, persönliches Netzwerk von 1.500+ C-Level-Kontakten "
         "in Finance, Technology und Industrie im DACH-Raum. "
         "Direktansprache — kein Datenbanksurf."),
        ("02", "Boutique-Qualität\nbei jeder Suche",
         "Kein Volumenziel. Kein Staffing. Jede Suche wird vom Gründer persönlich geführt. "
         "Mandantenzahl bewusst limitiert für maximale Qualität."),
        ("03", "Nachfolge-Expertise\nals Alleinstellungsmerkmal",
         "Spezialkompetenz in Unternehmensnachfolge und Senioren-Transition. "
         "Wachsendes Marktsegment: 580.000 KMU-Nachfolgen bis 2030."),
        ("04", "Diskrete, vertrauensbasierte\nArbeitsweise",
         "Vertraulichkeit als Kernprinzip. "
         "Keine Stellenanzeigen, keine Transparenz nach außen. "
         "Preferred Partner vieler Familienunternehmen und PE-Häuser."),
    ]

    for i, (num, title, desc) in enumerate(usps):
        cx = 1.2 + (i % 2) * 5.9
        cy = 1.55 + (i // 2) * 2.6
        rect(s, cx, cy, 5.6, 2.35, fill=RGBColor(0x1A,0x2B,0x4D))
        rect(s, cx, cy, 0.07, 2.35, fill=GOLD)
        txt(s, num, cx+0.2, cy+0.1, 0.6, 0.45, sz=22, clr=GOLD, bold=True, fn=FL)
        txt(s, title, cx+0.95, cy+0.08, 4.5, 0.55, sz=14, clr=WHITE, bold=True,
            fn=FL, wrap=True)
        txt(s, desc, cx+0.2, cy+0.72, 5.2, 1.45, sz=11,
            clr=RGBColor(0xB0,0xB8,0xC8), wrap=True)

    fade_transition(s)
    apply_animations(s, [
        (t_h.shape_id, 'fade', 1, 0, 600),
        (t_s.shape_id, 'fade', 1, 500, 500),
    ])
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — PARTNERSCHAFTSMODELL
# ─────────────────────────────────────────────────────────────────────────────

def slide_partner(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 9)

    slide_title(s, "Partnerschaftsmodell — Nachfolgelösung",
                "Strukturierte Übernahme einer etablierten Praxis über 4 Jahre")

    # Linke Erklärung
    rect(s, 0.5, 1.5, 5.5, 5.2, fill=LT_GREY)
    txt(s, "Das Modell", 0.65, 1.6, 5.2, 0.35, sz=14, clr=NAVY, bold=True)
    desc = (
        "Ein erfahrener Headhunter (Gründer, 60+) sucht einen qualifizierten "
        "Nachfolger, der sein Lebenswerk weiterführt und über 4 Jahre die "
        "Mandanten, das Know-how und den Markennamen übernimmt.\n\n"
        "Aaron Arena bringt als designierter Nachfolger:\n"
        "• Operatives Executive-Search-Know-how\n"
        "• Ein eigenständiges Netzwerk im DACH-Raum\n"
        "• Kapital & Finanzierungszusage\n"
        "• Klares Wachstumskonzept für die Praxis\n\n"
        "Der Senior-Partner erhält:\n"
        "• Strukturierten Ausstieg über 48 Monate\n"
        "• Faire Beteiligungsvergütung\n"
        "• Sicherung seines Lebenswerks"
    )
    txt(s, desc, 0.65, 2.05, 5.2, 4.5, sz=11, clr=DK_GREY, wrap=True)

    # Rechte Phasen-Darstellung
    phases = [
        ("Phase 1\n2026–2027", "Einstieg & Lernen",
         "Shadowing, gemeinsame Mandate, Brand Building dual",
         NAVY),
        ("Phase 2\n2027–2028", "Operative Übernahme",
         "Aaron Arena führt 60 % der Mandate eigenständig",
         NAVY_MID),
        ("Phase 3\n2028–2029", "Mehrheitskontrolle",
         "Übernahme der Mandantschaft, schrittweise Beteiligungsübertragung",
         DK_GREY),
        ("Phase 4\n2030", "Vollübernahme",
         "Komplette Übernahme — Senior-Partner in Advisory-Rolle",
         GOLD),
    ]
    for i, (ph, title, desc2, clr) in enumerate(phases):
        cy = 1.5 + i * 1.22
        rect(s, 6.35, cy, 6.5, 1.1, fill=CARD_BG)
        rect(s, 6.35, cy, 0.07, 1.1, fill=clr)
        txt(s, ph,    6.5, cy+0.07, 1.5, 0.5, sz=10, clr=clr, bold=True, wrap=True)
        txt(s, title, 8.15, cy+0.07, 4.5, 0.32, sz=13, clr=APPLE_BK, bold=True)
        txt(s, desc2, 8.15, cy+0.43, 4.5, 0.55, sz=11, clr=MD_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — WACHSTUMSSTRATEGIE
# ─────────────────────────────────────────────────────────────────────────────

def slide_wachstum(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 10)

    slide_title(s, "Wachstumsstrategie",
                "Fokussiertes Wachstum in drei Horizonten")

    horizons = [
        ("H1: Aufbau\nOkt 2026 – Sep 2027",
         ["Erste 5–8 Retained Searches abschließen",
          "3 Anker-Mandanten akquirieren",
          "Website, Brand, Reputation aufbauen",
          "Partnerschaft formalisieren",
          "Referenznetzwerk aktivieren"],
         NAVY, "€ 240K\nZiel-Umsatz"),
        ("H2: Wachstum\n2028",
         ["12–15 Mandate p.a.",
          "Spezialisierung Sektor Finance/Tech vertieft",
          "2. Consultant hinzunehmen",
          "Nachfolge-Boutique-Marke etablieren",
          "Erste Interim-Mandate"],
         DK_GREY, "€ 540K\nZiel-Umsatz"),
        ("H3: Skalierung\n2029",
         ["18–22 Mandate p.a.",
          "Vollübernahme Partnerpraxis",
          "Board-Advisory-Segment ausgebaut",
          "DACH-weite Mandantenbasis",
          "Team: 3–4 Berater"],
         GOLD, "€ 840K\nZiel-Umsatz"),
    ]

    for i, (title, bullets, clr, kpi) in enumerate(horizons):
        cx = 0.5 + i * 4.25
        rect(s, cx, 1.5, 3.95, 4.7, fill=CARD_BG)
        rect(s, cx, 1.5, 3.95, 0.55, fill=clr)
        txt(s, title, cx+0.15, 1.52, 3.65, 0.5, sz=13, clr=WHITE, bold=True,
            fn=FL, wrap=True)
        for j, b in enumerate(bullets):
            txt(s, f"• {b}", cx+0.18, 2.2 + j*0.6, 3.65, 0.55,
                sz=11, clr=DK_GREY, wrap=True)
        rect(s, cx, 5.8, 3.95, 0.4, fill=clr)
        txt(s, kpi, cx+0.1, 5.82, 3.75, 0.36, sz=11, clr=WHITE, bold=True,
            align=PP_ALIGN.CENTER, wrap=True)

    # Pfeil
    for i in range(2):
        rect(s, 4.45 + i*4.25, 3.7, 0.3, 0.08, fill=GOLD)

    rect(s, 0.5, 6.38, 12.5, 0.5, fill=LT_GREY)
    txt(s, "Akquise-Strategie: Bestandsnetzwerk → Empfehlungen → Ausgewählte Verbandspräsenz → "
           "LinkedIn-Thought-Leadership → Persönliche Ansprache",
        0.65, 6.42, 12.2, 0.4, sz=10, clr=MD_GREY)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — FINANZPLANUNG
# ─────────────────────────────────────────────────────────────────────────────

def slide_finanzen(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 11)

    slide_title(s, "Finanzplanung 2026 – 2029",
                "Konservative Prognose | Alle Werte in EUR | Steuern nicht eingerechnet")

    # Tabellenkopf
    years = ["", "Q4 2026", "GJ 2027", "GJ 2028", "GJ 2029"]
    col_w = [3.2, 2.1, 2.1, 2.1, 2.1]
    col_x = [0.5, 3.8, 5.95, 8.1, 10.25]

    for i, (label, cx, cw) in enumerate(zip(years, col_x, col_w)):
        rect(s, cx, 1.5, cw, 0.38, fill=NAVY if i > 0 else LT_GREY)
        clr = WHITE if i > 0 else MD_GREY
        txt(s, label, cx+0.05, 1.5, cw-0.05, 0.38, sz=12, clr=clr, bold=True,
            align=PP_ALIGN.CENTER if i > 0 else PP_ALIGN.LEFT)

    rows = [
        ("Placements (Anzahl)", ["3",    "8",   "15",   "22"],    False, False),
        ("Ø Honorar (€)",       ["50.000","55.000","58.000","60.000"], False, False),
        ("Umsatz",              ["150.000","440.000","870.000","1.320.000"], True, False),
        ("+ Interim / Advisory",["90.000","80.000","110.000","160.000"],   False, False),
        ("= Gesamtumsatz",      ["240.000","520.000","980.000","1.480.000"],True, True),
        ("Betriebskosten",      ["(130.000)","(170.000)","(220.000)","(310.000)"],False,False),
        ("EBIT",                ["110.000","350.000","760.000","1.170.000"], True, True),
        ("EBIT-Marge",          ["46 %",  "67 %", "78 %",  "79 %"],         False, False),
    ]

    for ri, (label, vals, bold_row, highlight) in enumerate(rows):
        ry = 1.95 + ri * 0.56
        sep = ri in (4, 6)
        bg_r = GOLD_BG if highlight else (LT_GREY if ri % 2 == 0 else WHITE)
        rect(s, 0.5, ry, 12.33, 0.52, fill=bg_r)
        txt(s, label, 0.6, ry+0.07, 3.1, 0.38, sz=11, clr=APPLE_BK if bold_row else DK_GREY,
            bold=bold_row)
        for ci, val in enumerate(vals):
            cx2 = col_x[ci+1] + 0.05
            txt(s, val, cx2, ry+0.07, col_w[ci+1]-0.1, 0.38, sz=11,
                clr=NAVY if bold_row else DK_GREY, bold=bold_row,
                align=PP_ALIGN.RIGHT)
        if sep:
            rect(s, 0.5, ry, 12.33, 0.04, fill=NAVY)

    txt(s, "* Placements × Ø-Honorar = Retained-Search-Umsatz | Interim & Advisory separat ausgewiesen",
        0.5, 6.55, 12.3, 0.3, sz=8, clr=MD_GREY, italic=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — INVESTITIONSBEDARF
# ─────────────────────────────────────────────────────────────────────────────

def slide_invest(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 12)

    slide_title(s, "Investitionsbedarf & Mittelverwendung",
                "Finanzierungsanfrage an die Bank | Gesamtbedarf: € 150.000")

    # Linke Seite: Aufstellung
    rect(s, 0.5, 1.5, 6.2, 5.2, fill=LT_GREY)
    txt(s, "Mittelverwendung", 0.65, 1.6, 5.9, 0.35, sz=14, clr=NAVY, bold=True)
    rect(s, 0.65, 2.0, 5.9, 0.04, fill=GOLD)

    items = [
        ("Büro & Coworking (12 Monate)", "18.000 €"),
        ("IT, CRM & Research-Tools", "12.000 €"),
        ("Marke, Website, Marketing", "15.000 €"),
        ("Verbandsmitgliedschaften & Events", "8.000 €"),
        ("Versicherungen & Recht", "7.000 €"),
        ("Betriebskapital (laufende Kosten)", "60.000 €"),
        ("Gründungsreserve (3 Monate)", "30.000 €"),
    ]
    for i, (label, val) in enumerate(items):
        ry = 2.15 + i * 0.62
        bg = CARD_BG if i % 2 == 0 else LT_GREY
        rect(s, 0.65, ry, 5.9, 0.58, fill=bg)
        txt(s, label, 0.8, ry+0.1, 4.1, 0.38, sz=12, clr=DK_GREY)
        txt(s, val, 4.8, ry+0.1, 1.65, 0.38, sz=12, clr=NAVY, bold=True,
            align=PP_ALIGN.RIGHT)

    rect(s, 0.65, 6.45, 5.9, 0.1, fill=NAVY)
    txt(s, "GESAMT  150.000 €", 0.8, 6.18, 5.6, 0.32, sz=13, clr=NAVY, bold=True)

    # Rechte Seite: Konditionen-Vorschlag
    rect(s, 7.0, 1.5, 6.0, 5.2, fill=CARD_BG)
    txt(s, "Konditionen-Vorschlag", 7.15, 1.6, 5.7, 0.35, sz=14, clr=NAVY, bold=True)
    rect(s, 7.15, 2.0, 5.7, 0.04, fill=GOLD)

    conds = [
        ("Kreditbetrag", "€ 150.000"),
        ("Laufzeit", "60 Monate (5 Jahre)"),
        ("Tilgungsfrei", "12 Monate"),
        ("Rückzahlung ab", "Oktober 2027"),
        ("Monatliche Rate (ab M13)", "ca. € 2.900"),
        ("Sicherheit", "Abtretung Honorarforderungen +\nPersonalbürgschaft"),
        ("Break-Even", "Monat 8 (Juni 2027)"),
    ]
    for i, (label, val) in enumerate(conds):
        ry = 2.15 + i * 0.6
        rect(s, 7.15, ry, 5.7, 0.56, fill=WHITE if i%2==0 else CARD_BG)
        txt(s, label, 7.3, ry+0.1, 2.5, 0.36, sz=11, clr=MD_GREY)
        txt(s, val, 9.85, ry+0.08, 2.85, 0.4, sz=11, clr=NAVY, bold=True, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13 — RISIKEN & MITIGATION
# ─────────────────────────────────────────────────────────────────────────────

def slide_risiken(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 13)

    slide_title(s, "Risiken & Mitigationsmaßnahmen",
                "Transparente Risikobetrachtung — strukturierte Gegenmaßnahmen")

    risks = [
        ("Lange Akquise-\nAnlaufphase",
         "Hoch", "Mittel",
         "Aktivierung des Bestandsnetzwerks ab Tag 1; "
         "Pipeline aus 10+ qualifizierten Interessenten bereits vorhanden"),
        ("Konjunktureller\nAbschwung",
         "Mittel", "Hoch",
         "Executive Search bleibt auch in Krisen kritisch; "
         "Krisenzeiten erhöhen Nachfolgebedarf; "
         "Diversifizierung über Sectoren"),
        ("Ausfall Partner-\nkooperation",
         "Niedrig", "Hoch",
         "Notarielle Regelung im Partnerschaftsvertrag; "
         "ARENA funktioniert auch als Solo-Praxis von Tag 1"),
        ("Wettbewerb\ngroße Kanzleien",
         "Mittel", "Niedrig",
         "Differenzierung über Persönlichkeit, Netzwerk & "
         "Boutique-Service — nicht über Preis; "
         "Kunden wechseln zu Boutiques aus Qualitätsgründen"),
    ]

    for i, (risk, warsch, impact, mitigation) in enumerate(risks):
        col = i % 2; row = i // 2
        cx = 0.5 + col * 6.4; cy = 1.5 + row * 2.65
        rect(s, cx, cy, 6.1, 2.45, fill=CARD_BG)
        txt(s, risk, cx+0.2, cy+0.12, 4.0, 0.55, sz=14, clr=APPLE_BK, bold=True, wrap=True)
        # Badges
        clr_w = GOLD if warsch == "Hoch" else (DK_GREY if warsch == "Mittel" else DIVIDER)
        clr_i = RGBColor(0xCC,0x44,0x44) if impact == "Hoch" else (GOLD if impact == "Mittel" else DIVIDER)
        rect(s, cx+0.2, cy+0.7, 1.3, 0.26, fill=clr_w)
        txt(s, f"W: {warsch}", cx+0.2, cy+0.7, 1.3, 0.26, sz=9, clr=WHITE, bold=True,
            align=PP_ALIGN.CENTER)
        rect(s, cx+1.6, cy+0.7, 1.3, 0.26, fill=clr_i)
        txt(s, f"I: {impact}", cx+1.6, cy+0.7, 1.3, 0.26, sz=9, clr=WHITE, bold=True,
            align=PP_ALIGN.CENTER)
        txt(s, mitigation, cx+0.2, cy+1.08, 5.7, 1.2, sz=11, clr=DK_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 14 — MEILENSTEINE & ROADMAP
# ─────────────────────────────────────────────────────────────────────────────

def slide_roadmap(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 14)

    slide_title(s, "Meilensteine & Roadmap",
                "Klare operative Etappenziele — Quartal für Quartal")

    milestones = [
        ("Q4 2026",  "Start",   NAVY,  ["Gründung & Anmeldung", "Website live", "Erste 2 Mandate"]),
        ("Q1 2027",  "Aufbau",  NAVY,  ["3 Retainer-Mandate laufend", "Partnervertrag unterzeichnet", "Break-Even in Sicht"]),
        ("Q2 2027",  "Wachsen", DK_GREY,["5. Placement", "Erstes Interim-Mandat", "Verbandsmitgliedschaft aktiv"]),
        ("Q3 2027",  "Profil",  DK_GREY,["8. Placement", "10 aktive Mandanten", "Break-Even erreicht"]),
        ("GJ 2028",  "Skalieren",GOLD,  ["15 Placements", "2. Berater", "Nachfolgemandate aktiv"]),
        ("GJ 2029",  "Führen",  GOLD,  ["22 Placements", "Vollübernahme Partnerpraxis", "EBIT > €1,1 Mio."]),
    ]

    # Zeitlinie
    rect(s, 0.5, 3.8, 12.33, 0.06, fill=DIVIDER)

    for i, (period, stage, clr, bullets) in enumerate(milestones):
        cx = 0.5 + i * 2.1
        # Kreis auf Zeitlinie
        rect(s, cx + 0.8, 3.65, 0.28, 0.28, fill=clr)
        # Obere oder untere Karte
        if i % 2 == 0:
            cy = 1.55
            rect(s, cx, cy, 2.0, 2.1, fill=CARD_BG)
            rect(s, cx, cy, 2.0, 0.38, fill=clr)
            txt(s, period, cx+0.08, cy+0.04, 1.84, 0.28, sz=11, clr=WHITE, bold=True)
            txt(s, stage,  cx+0.08, cy+0.42, 1.84, 0.28, sz=10, clr=clr, bold=True)
            for j, b in enumerate(bullets):
                txt(s, f"• {b}", cx+0.08, cy+0.76 + j*0.42, 1.86, 0.38,
                    sz=9, clr=DK_GREY, wrap=True)
            # Verbindungslinie nach unten
            rect(s, cx + 0.94, cy + 2.1, 0.04, 0.06, fill=clr)
        else:
            cy = 4.15
            rect(s, cx, cy, 2.0, 2.1, fill=CARD_BG)
            rect(s, cx, cy, 2.0, 0.38, fill=clr)
            txt(s, period, cx+0.08, cy+0.04, 1.84, 0.28, sz=11, clr=WHITE, bold=True)
            txt(s, stage,  cx+0.08, cy+0.42, 1.84, 0.28, sz=10, clr=clr, bold=True)
            for j, b in enumerate(bullets):
                txt(s, f"• {b}", cx+0.08, cy+0.76 + j*0.42, 1.86, 0.38,
                    sz=9, clr=DK_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 15 — ZIELBRANCHEN
# ─────────────────────────────────────────────────────────────────────────────

def slide_branchen(prs):
    s = new_slide(prs, bg=WHITE)
    top_bar(s)
    footer(s, 15)

    slide_title(s, "Zielbranchen & Zielgruppen",
                "Fokussierter Sektormix — Tiefe vor Breite")

    sectors = [
        ("Financial\nServices",   "CFO, CRO, CEO\nPrivate Banking, PE, Versicherung",         NAVY),
        ("Technology &\nDigital",  "CTO, CDO, CISO\nSoftware, FinTech, AI/ML-Unternehmen",     NAVY_MID),
        ("Industrie &\nMittelstand","CEO, COO, CSO\nFamilienunternehmen, Hidden Champions",     DK_GREY),
        ("Nachfolge /\nM&A",        "Übergangsmandate\nNachfolgeplanung, Post-Merger-Führung",  GOLD),
    ]

    for i, (sector, profile, clr) in enumerate(sectors):
        cx = 0.5 + (i % 2) * 6.4
        cy = 1.5 + (i // 2) * 2.75
        rect(s, cx, cy, 6.1, 2.55, fill=CARD_BG)
        rect(s, cx, cy, 6.1, 0.5,  fill=clr)
        txt(s, sector, cx+0.2, cy+0.07, 5.7, 0.42, sz=16, clr=WHITE, bold=True,
            fn=FL, wrap=True)
        txt(s, "Zielpositionen & Schwerpunkte", cx+0.2, cy+0.65, 5.7, 0.28,
            sz=10, clr=GOLD, italic=True)
        txt(s, profile, cx+0.2, cy+0.98, 5.7, 1.35, sz=12, clr=DK_GREY, wrap=True)

    fade_transition(s)
    return s

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 16 — FAZIT & CTA
# ─────────────────────────────────────────────────────────────────────────────

def slide_fazit(prs):
    s = new_slide(prs, bg=NAVY)
    rect(s, 0, 0, 0.06, 7.5, fill=GOLD)

    t1 = txt(s, "Starten wir gemeinsam.", 1.2, 1.2, 11, 0.9, sz=44, clr=WHITE, fn=FL)
    t2 = txt(s, "ARENA Executive Search ist bereit.", 1.2, 2.0, 11, 0.55, sz=28,
             clr=GOLD, fn=FL)

    rect(s, 1.2, 2.7, 9.5, 0.05, fill=RGBColor(0x3A,0x4A,0x6A))

    bullets = [
        "✓  Erfahrener Gründer — 30+ Jahre operative Erfahrung, etabliertes Netzwerk",
        "✓  Klares Geschäftsmodell — Retained Search mit sofort aktivierbarem Deal-Flow",
        "✓  Realistische Zahlen — Break-Even Monat 8, EBIT > 1 Mio. € ab Jahr 3",
        "✓  Doppelte Sicherheit — Solo-fähig + Partnerschaftsoption als Upside",
        "✓  Finanzierungsbedarf überschaubar — € 150.000 mit klar geplanter Tilgung",
    ]
    for i, b in enumerate(bullets):
        txt(s, b, 1.2, 2.95 + i * 0.52, 11, 0.45, sz=13,
            clr=RGBColor(0xD0,0xD8,0xE8), wrap=True)

    rect(s, 1.2, 5.75, 11, 0.06, fill=RGBColor(0x3A,0x4A,0x6A))

    txt(s, "Kontakt:", 1.2, 5.98, 4, 0.28, sz=11, clr=GOLD, bold=True)
    txt(s, "Aaron Arena  |  aaron.arena@arena-executive-search.de  |  +49 (0) 170 — — — — — —",
        1.2, 6.28, 11, 0.28, sz=12, clr=WHITE)
    txt(s, "www.arena-executive-search.de  |  LinkedIn: /in/aaronarena",
        1.2, 6.6,  11, 0.28, sz=11, clr=RGBColor(0xB0,0xB8,0xC8))

    fade_transition(s)
    apply_animations(s, [
        (t1.shape_id, 'fade', 1,  0, 700),
        (t2.shape_id, 'fade', 1,600, 600),
    ])
    return s

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    print("Erstelle Präsentation …")
    slide_cover(prs)     # 1
    slide_agenda(prs)    # 2
    slide_chance(prs)    # 3
    slide_founder(prs)   # 4
    slide_markt(prs)     # 5
    slide_modell(prs)    # 6
    slide_leistungen(prs)# 7
    slide_usp(prs)       # 8
    slide_partner(prs)   # 9
    slide_wachstum(prs)  # 10
    slide_finanzen(prs)  # 11
    slide_invest(prs)    # 12
    slide_risiken(prs)   # 13
    slide_roadmap(prs)   # 14
    slide_branchen(prs)  # 15
    slide_fazit(prs)     # 16

    out = "/home/user/ARENA_Executive_Search_Businessplan_2026.pptx"
    prs.save(out)
    print(f"✓  Gespeichert: {out}")
    print(f"   Folien: {len(prs.slides)}")
    return out

if __name__ == "__main__":
    main()
