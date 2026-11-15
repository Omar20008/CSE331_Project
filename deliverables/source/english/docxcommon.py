# -*- coding: utf-8 -*-
"""Shared python-docx helpers for the CSE331 milestone documents (ENGLISH-ONLY).

This is the English-only counterpart of ../docxcommon.py. It keeps exactly the
same public API (every helper still accepts the Arabic argument) so the build
scripts are unchanged, but it emits only the English text — no Arabic twin,
no RTL paragraphs, no complex-script runs.
"""
from docx import Document
from docx.shared import Pt, Mm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK   = RGBColor(0x1F, 0x29, 0x37)
BLUE  = RGBColor(0x1D, 0x4E, 0xD8)
TEAL  = RGBColor(0x0F, 0x76, 0x6E)
GREEN = RGBColor(0x15, 0x80, 0x3D)
RED   = RGBColor(0xB9, 0x1C, 0x1C)
MUTED = RGBColor(0x55, 0x65, 0x70)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

HDR_FILL = "1E293B"
ALT_FILL = "F1F5F9"
BOX_FILL = "EFF6FF"

_FIGN = {"n": 0}   # auto figure counter, reset per document in new_doc()

# ------------------------------------------------------------------ low level
def _rPr(run):
    return run._element.get_or_add_rPr()

def _par_border(p, edge, color="CBD5E1", sz="6", space="4"):
    pPr = p._p.get_or_add_pPr()
    pbdr = pPr.find(qn('w:pBdr'))
    if pbdr is None:
        pbdr = OxmlElement('w:pBdr'); pPr.append(pbdr)
    e = OxmlElement(f'w:{edge}')
    for k, v in (('w:val', 'single'), ('w:sz', sz), ('w:space', space), ('w:color', color)):
        e.set(qn(k), v)
    pbdr.append(e)

def _field(p, instr, size=8.5, color=MUTED, bold=False):
    r = p.add_run(); r.font.size = Pt(size); r.font.color.rgb = color; r.bold = bold
    b = OxmlElement('w:fldChar'); b.set(qn('w:fldCharType'), 'begin')
    i = OxmlElement('w:instrText'); i.set(qn('xml:space'), 'preserve'); i.text = instr
    e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), 'end')
    r._r.append(b); r._r.append(i); r._r.append(e)

def run(p, text, bold=False, italic=False, size=10.5, color=INK, cs=False, rtl=False, font=None):
    # cs/rtl accepted for API compatibility but ignored in the English build.
    r = p.add_run(text)
    r.bold = bold; r.italic = italic
    r.font.size = Pt(size); r.font.color.rgb = color
    if font: r.font.name = font
    return r

def _emit(p, seg, default=None):
    if isinstance(seg, str):
        run(p, seg, **(default or {}))
    else:
        kw = dict(default or {}); kw.update(seg[1]); run(p, seg[0], **kw)

# ------------------------------------------------------------------ document
def new_doc():
    _FIGN["n"] = 0
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.left_margin = s.right_margin = Mm(20)
    s.top_margin, s.bottom_margin = Mm(18), Mm(18)
    s.header_distance, s.footer_distance = Mm(10), Mm(10)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(10.5); st.font.color.rgb = INK
    st.paragraph_format.space_after = Pt(5); st.paragraph_format.line_spacing = 1.1
    return doc

def running_chrome(doc, head_en, head_ar=None):
    """A muted running header (kept off the title page) and a page-number footer."""
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    cw = (sec.page_width - sec.left_margin - sec.right_margin) / 914400.0  # EMU -> inches
    hp = sec.header.paragraphs[0]; hp.text = ""
    hp.paragraph_format.tab_stops.add_tab_stop(Inches(cw), WD_TAB_ALIGNMENT.RIGHT)
    run(hp, head_en, size=8, color=MUTED)
    _par_border(hp, "bottom", "E2E8F0", sz="4", space="3")
    fp = sec.footer.paragraphs[0]; fp.text = ""; fp.alignment = AL.CENTER
    _par_border(fp, "top", "E2E8F0", sz="4", space="3")
    run(fp, "Page ", size=8.5, color=MUTED)
    _field(fp, "PAGE"); run(fp, " / ", size=8.5, color=MUTED); _field(fp, "NUMPAGES")

# ------------------------------------------------------------------ paragraphs
def enpara(doc, *segs, align=None, space_after=3, space_before=0, size=10.5):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    for seg in segs:
        _emit(p, seg, {"size": size})
    return p

def arpara(doc, *segs, space_after=9, size=10.5):
    # English build: Arabic paragraphs are intentionally omitted.
    return None

def bipara(doc, en, ar=None):
    """English paragraph (the Arabic twin is omitted in the English build)."""
    return enpara(doc, en, space_after=7)

def heading(doc, en, ar=None, level=1, number=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6 if level == 1 else 4)
    p.paragraph_format.keep_with_next = True
    sz = {1: 15, 2: 12.5, 3: 11}[level]
    col = BLUE if level == 1 else (TEAL if level == 2 else INK)
    run(p, (f"{number}  " if number else "") + en, bold=True, size=sz, color=col)
    if level == 1:
        pbdr = OxmlElement('w:pBdr'); bo = OxmlElement('w:bottom')
        for k, v in (('w:val', 'single'), ('w:sz', '6'), ('w:space', '4'), ('w:color', 'CBD5E1')):
            bo.set(qn(k), v)
        pbdr.append(bo); p._p.get_or_add_pPr().append(pbdr)
    return p

def bibullet(doc, en, ar=None, level=0):
    # en may be a str or a list of segments
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.28 + 0.25*level)
    p.paragraph_format.space_after = Pt(4)
    for seg in (en if isinstance(en, list) else [en]):
        _emit(p, seg, {"size": 10})
    return p

# ------------------------------------------------------------------ tables
def _shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)

def _cell(cell, value, bold=False, size=8.6, header=False):
    """value: str (EN only) OR (en, ar) tuple -> only the EN line is emitted."""
    cell.text = ""
    en = value[0] if isinstance(value, tuple) else value
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(1)
    col = WHITE if header else INK
    for i, part in enumerate(str(en).split("\n")):
        if i:
            p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(part); r.bold = bold or header
        r.font.size = Pt(size); r.font.color.rgb = col

def table(doc, headers, rows, widths, zebra=True, font=8.6):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False; t.allow_autofit = False
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{edge}')
        for k, v in (('w:val', 'single'), ('w:sz', '4'), ('w:space', '0'), ('w:color', 'CBD5E1')):
            e.set(qn(k), v)
        borders.append(e)
    t._tbl.tblPr.append(borders)
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]
        _cell(c, h, header=True, size=font+0.2)
        _shade(c, HDR_FILL); c.width = Inches(widths[j])
    for i, rowdata in enumerate(rows):
        cells = t.add_row().cells
        for j, val in enumerate(rowdata):
            _cell(cells[j], val, bold=(j == 0), size=font)
            cells[j].width = Inches(widths[j])
            if zebra and i % 2 == 1:
                _shade(cells[j], ALT_FILL)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ------------------------------------------------------------------ figure / callout
def figure(doc, path, cap_en, cap_ar=None, width=6.3):
    _FIGN["n"] += 1; n = _FIGN["n"]
    p = doc.add_paragraph(); p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    p.add_run().add_picture(path, width=Inches(width))
    c = doc.add_paragraph(); c.alignment = AL.CENTER
    c.paragraph_format.space_after = Pt(11); c.paragraph_format.keep_with_next = False
    run(c, f"Figure {n}. ", bold=True, size=9, color=MUTED)
    run(c, cap_en, size=9, color=MUTED, italic=True)

def callout(doc, label_en, label_ar, body_en, body_ar=None, fill=BOX_FILL, bar="2563EB"):
    t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]; cell.width = Inches(6.6)
    _shade(cell, fill)
    tcPr = cell._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    for k, v in (('w:val', 'single'), ('w:sz', '24'), ('w:space', '0'), ('w:color', bar)):
        left.set(qn(k), v)
    b.append(left); tcPr.append(b)
    cell.text = ""
    p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(1)
    run(p, label_en + "  ", bold=True, size=10, color=INK)
    run(p, body_en, size=10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ------------------------------------------------------------------ title page
def title_page(doc, course, project, milestone_en, milestone_ar, title_en, title_ar,
               sub_en, sub_ar, desc_en, desc_ar, meta_rows, filename):
    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    p = doc.add_paragraph(); p.alignment = AL.CENTER
    run(p, course, bold=True, size=12, color=MUTED)
    p = doc.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_after = Pt(2)
    run(p, project, bold=True, size=13, color=TEAL)
    p = doc.add_paragraph(); p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(14)
    run(p, milestone_en, bold=True, size=10.5, color=RED)
    p = doc.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_after = Pt(10)
    run(p, title_en, bold=True, size=19, color=INK)
    p = doc.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_after = Pt(14)
    run(p, sub_en, italic=True, size=10.5, color=MUTED)
    # description box
    callout(doc, "About the project.", None,
            desc_en, None, fill="F8FAFC", bar="0F766E")
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    t = doc.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in meta_rows:
        cells = t.add_row().cells
        _cell(cells[0], k, bold=True, size=10); cells[0].width = Inches(2.1)
        _cell(cells[1], v, size=10); cells[1].width = Inches(4.2)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    p = doc.add_paragraph(); p.alignment = AL.CENTER
    run(p, "Submission file: ", bold=True, size=9.5, color=MUTED)
    run(p, filename, size=9.5, color=INK)
    p = doc.add_paragraph(); p.alignment = AL.CENTER
    run(p, "All data is 100% synthetic. A classroom prototype does not establish legal compliance.",
        italic=True, size=9, color=MUTED)
    doc.add_page_break()
