"""
generate_fresh_docs.py
CSE331 - Project 09: Document Redaction & Metadata Privacy

FRESH HOLD-OUT TEST SET  (the v4 detector has NEVER seen these people).

Why a separate "fresh" set exists
---------------------------------
`generate_real_docs.py` built the 20 synthetic individuals we tuned the v1->v4 detectors
against. Reporting only on that set risks measuring how well we *fit our own data*. This
script builds a completely NEW population of 20 synthetic individuals -- new names, new
phone formats, and NEW address/postcode styles from countries the real set never used
(Egypt, Turkey, Brazil, Japan, Canada, and more) -- so we can measure the SAME, UNCHANGED
detectors on data they were never tuned on. That is the honest, generalisation number.

It mirrors `generate_real_docs.py` EXACTLY in structure:
  * Each person -> ONE DOCX + ONE PDF  => 20 + 20 = 40 files in documents_fresh/.
  * Same planting SURFACES:
        DOCX : body paragraph, a table, header, footer, hidden (vanish) run,
               comment + comment author, and core properties (metadata).
        PDF  : visible text, white (hidden) text, and document metadata.
  * Same ground-truth SCHEMA (documents_fresh/ground_truth_fresh.json), so the existing
    evaluate / detection_quality / attack scripts read it with a single `fresh` argument.

Everything is SYNTHETIC: example.* e-mail domains, 555-01xx style phone tails, and
made-up national-ID / SSN numbers. No real person or real contact detail is used.

Arabic rendering uses the same reshaper + bidi + Unicode-font trick as the real generator
so Arabic names/addresses render in the PDF AND stay extractable (a hidden logical-order
copy is embedded), which keeps the Arabic individuals testable.
"""

import json
import os
import re
import sys

from docx import Document
from docx.shared import RGBColor  # noqa: F401  (imported to mirror the real generator)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

OUT_DIR = "documents_fresh"
DOCX_DIR = os.path.join(OUT_DIR, "docx")
PDF_DIR = os.path.join(OUT_DIR, "pdf")
os.makedirs(DOCX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# Same non-personal decoy as the real set: it must SURVIVE redaction (false-positive probe).
DECOY_EMAIL = "hr@company.com"

# ----------------------------------------------------------------------------
# Arabic rendering support for PDFs (mirrors generate_real_docs.py).
# reportlab + a Latin-only font cannot draw Arabic, so we register a Unicode TTF, reshape
# (contextual letter forms) and apply the bidi algorithm before drawing. If no font / libs
# are available we warn ONCE and fall back to an ASCII approximation.
# ----------------------------------------------------------------------------
_ARABIC_FONT_NAME = "ArabicFont"
_ARABIC_FONT_CANDIDATES = [
    os.path.join("fonts", "Amiri-Regular.ttf"),
    os.path.join("fonts", "NotoNaskhArabic-Regular.ttf"),
    os.path.join("fonts", "Arial.ttf"),
    r"C:\Windows\Fonts\arial.ttf",          # Arial embeds Arabic glyphs on Windows
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
]
_arabic_font_ready = None       # None = not tried yet; True/False after the first attempt
_arabic_warned = False


def _ensure_arabic_font() -> bool:
    """Register an Arabic-capable TTF with reportlab once; return True if available."""
    global _arabic_font_ready
    if _arabic_font_ready is not None:
        return _arabic_font_ready
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for path in _ARABIC_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(_ARABIC_FONT_NAME, path))
                _arabic_font_ready = True
                return True
            except Exception:
                continue
    _arabic_font_ready = False
    return False


def _has_arabic(text: str) -> bool:
    return any(
        "\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F"
        or "\u08A0" <= ch <= "\u08FF" or "\uFB50" <= ch <= "\uFDFF"
        or "\uFE70" <= ch <= "\uFEFF"
        for ch in text
    )


def _shape_arabic(text: str) -> str:
    """Reshape + bidi so Arabic draws correctly (contextual forms, right-to-left)."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _warn_no_arabic_once():
    global _arabic_warned
    if not _arabic_warned:
        print("  [warn] No Arabic-capable TTF font (or shaping libs) found; Arabic in PDFs "
              "will be ASCII-approximated. Install arabic-reshaper + python-bidi and provide "
              "fonts/Amiri-Regular.ttf (or rely on a system Arial) for full support.")
        _arabic_warned = True


# ----------------------------------------------------------------------------
# The FRESH population: 20 distinct synthetic individuals.
#
# Design goals (all required by the brief, and none overlapping the real set):
#   * brand-new names, phone formats and address/postcode styles;
#   * at least Egypt, Turkey, Brazil, Japan and Canada postcode styles, plus more;
#   * mixed Arabic-script names (and Arabic addresses);
#   * hyphenated and multi-word names;
#   * a P.O. Box, apartment / unit lines;
#   * a phone WITH an extension (two styles: "ext. NNN" and "xNNNN");
#   * phones in several international formats (+20, +90, +55, +81, +1, +52, +39, ...).
#
# NOTE on the US_SSN field: we keep the national-ID VALUES in standard US SSN shape
# (NNN-NN-NNNN, made-up, valid area 001-665). This is deliberate -- it keeps US_SSN a clean
# CONTROL so any recall change on the fresh set comes from the genuinely new dimensions
# (names / phones / addresses), not from also swapping the ID format.
#
# NOTE on digits (the k=0 gotcha, see docs + memory): the adversarial attack links recovered
# digit runs against the population, and python-docx stamps boilerplate digit runs into every
# DOCX (app.xml "16.0000"/AppVersion, core.xml dates like 2001/2006/2013, thumbnail bytes
# 456789/56789/000000). If any person's numeric field CONTAINED one of those runs, that run
# would become "linkable" and collapse most documents to an empty anonymity set (k=0). So no
# numeric field below contains 0000, a 20xx year, or an ascending 4567/5678/6789 run. The
# self-check in main() enforces this so a future edit cannot silently reintroduce the bug.
# ----------------------------------------------------------------------------
FRESH_PEOPLE = [
    {   # 1 - Egypt, Arabic-script name + Arabic address, international mobile
        "PERSON": "ياسمين عبد الرحمن",
        "PHONE_NUMBER": "+20 100 555 0188",
        "EMAIL_ADDRESS": "yasmin.abdelrahman@example.eg",
        "LOCATION": "شارع التحرير، القاهرة",
        "US_SSN": "431-72-8859",
    },
    {   # 2 - Egypt, Latin script, hyphenated name, apartment line, 5-digit postcode
        "PERSON": "Tarek El-Masry",
        "PHONE_NUMBER": "+20 2 2574 0133",
        "EMAIL_ADDRESS": "tarek.elmasry@example.eg",
        "LOCATION": "12 Nasr Road, Apartment 7, Cairo 11765, Egypt",
        "US_SSN": "502-18-3367",
    },
    {   # 3 - Turkey, hyphenated name, "Caddesi" street, 5-digit postcode
        "PERSON": "Elif Yilmaz-Demir",
        "PHONE_NUMBER": "+90 212 555 0142",
        "EMAIL_ADDRESS": "elif.yilmaz@example.com.tr",
        "LOCATION": "Istiklal Caddesi 45, Beyoglu, Istanbul 34433, Turkey",
        "US_SSN": "276-33-5519",
    },
    {   # 4 - Turkey, phone WITH extension ("ext. 118"), mobile international format
        "PERSON": "Mehmet Kaya",
        "PHONE_NUMBER": "+90 532 555 0176 ext. 118",
        "EMAIL_ADDRESS": "mehmet.kaya@example.com.tr",
        "LOCATION": "Bagdat Caddesi 210, Kadikoy, Istanbul 34710, Turkey",
        "US_SSN": "419-52-7731",
    },
    {   # 5 - Brazil, hyphenated+accented name, "Apto" apartment, CEP postcode (00000-000)
        "PERSON": "João Carvalho-Souza",
        "PHONE_NUMBER": "+55 11 95555-0143",
        "EMAIL_ADDRESS": "joao.carvalho@example.com.br",
        "LOCATION": "Rua Augusta 1500, Apto 410, São Paulo 01305-001, Brazil",
        "US_SSN": "314-66-2285",
    },
    {   # 6 - Brazil, three-word name, CEP postcode
        "PERSON": "Beatriz Santos Lima",
        "PHONE_NUMBER": "+55 21 3555-0198",
        "EMAIL_ADDRESS": "beatriz.lima@example.com.br",
        "LOCATION": "Avenida Atlantica 1702, Copacabana, Rio de Janeiro 22021-030, Brazil",
        "US_SSN": "188-47-9920",
    },
    {   # 7 - Japan, romaji name, Unit line, 7-digit (NNN-NNNN) postcode, block address
        "PERSON": "Haruto Sato",
        "PHONE_NUMBER": "+81 3-3412-6690",
        "EMAIL_ADDRESS": "haruto.sato@example.jp",
        "LOCATION": "2-3-5 Nishi-Shinjuku, Unit 1203, Shinjuku, Tokyo 160-0023, Japan",
        "US_SSN": "233-58-4471",
    },
    {   # 8 - Japan, mobile (+81 90), 7-digit postcode
        "PERSON": "Yuki Tanaka",
        "PHONE_NUMBER": "+81 90-5555-0171",
        "EMAIL_ADDRESS": "yuki.tanaka@example.jp",
        "LOCATION": "1-8-14 Chuo, Osaka 541-0041, Japan",
        "US_SSN": "305-19-7744",
    },
    {   # 9 - Canada, P.O. Box + Station, alphanumeric postal code (A1A 1A1)
        "PERSON": "Olivia Tremblay",
        "PHONE_NUMBER": "+1-604-555-0162",
        "EMAIL_ADDRESS": "olivia.tremblay@example.ca",
        "LOCATION": "P.O. Box 2210, Station A, Toronto, ON M5W 1E6, Canada",
        "US_SSN": "262-41-8830",
    },
    {   # 10 - Canada, hyphenated name, Unit line, phone WITH "x" extension
        "PERSON": "Nathan Gagne-Roy",
        "PHONE_NUMBER": "(416) 555-0145 x4021",
        "EMAIL_ADDRESS": "nathan.gagne@example.ca",
        "LOCATION": "55 King Street West, Unit 808, Toronto, ON M5X 1A9, Canada",
        "US_SSN": "199-26-5538",
    },
    {   # 11 - Jordan, Arabic-script multi-word name + Arabic address, LOCAL 078 mobile
        "PERSON": "عبد الله الشريف",
        "PHONE_NUMBER": "0789990137",
        "EMAIL_ADDRESS": "abdullah.sharif@example.jo",
        "LOCATION": "شارع الاستقلال، الزرقاء",
        "US_SSN": "348-61-2274",
    },
    {   # 12 - Egypt, Arabic-script name + Arabic address, international mobile
        "PERSON": "منى فؤاد",
        "PHONE_NUMBER": "+20 109 555 0130",
        "EMAIL_ADDRESS": "mona.fouad@example.eg",
        "LOCATION": "ميدان رمسيس، القاهرة",
        "US_SSN": "417-29-6683",
    },
    {   # 13 - Mexico, accented name, "Piso" floor line, 5-digit postcode
        "PERSON": "Sofía Ramírez",
        "PHONE_NUMBER": "+52 55 8712 0164",
        "EMAIL_ADDRESS": "sofia.ramirez@example.mx",
        "LOCATION": "Avenida Reforma 222, Piso 4, Ciudad de México 06600, Mexico",
        "US_SSN": "214-37-9951",
    },
    {   # 14 - Italy, "Interno" apartment line, 5-digit CAP postcode
        "PERSON": "Giulia Esposito",
        "PHONE_NUMBER": "+39 06 7455 0184",
        "EMAIL_ADDRESS": "giulia.esposito@example.it",
        "LOCATION": "Via del Corso 101, Interno 3, Roma 00184, Italy",
        "US_SSN": "253-74-6612",
    },
    {   # 15 - Nigeria, hyphenated name, 6-digit postcode
        "PERSON": "Chidi Okeke-Nwosu",
        "PHONE_NUMBER": "+234 802 555 0147",
        "EMAIL_ADDRESS": "chidi.okeke@example.ng",
        "LOCATION": "15 Awolowo Road, Ikoyi, Lagos 101233, Nigeria",
        "US_SSN": "291-58-3340",
    },
    {   # 16 - South Korea, romaji name, 5-digit postcode
        "PERSON": "Minjun Park",
        "PHONE_NUMBER": "+82 2-555-0169",
        "EMAIL_ADDRESS": "minjun.park@example.kr",
        "LOCATION": "14 Teheran-ro, Gangnam-gu, Seoul 06236, South Korea",
        "US_SSN": "307-42-8816",
    },
    {   # 17 - Netherlands, "van der" multi-word name, Dutch postcode (NNNN AA)
        "PERSON": "Daan van der Berg",
        "PHONE_NUMBER": "+31 20 555 0152",
        "EMAIL_ADDRESS": "daan.vanderberg@example.nl",
        "LOCATION": "Keizersgracht 123, 1015 CJ Amsterdam, Netherlands",
        "US_SSN": "268-53-9024",
    },
    {   # 18 - Sweden, "Lagenhet" apartment line, Swedish postcode (NNN NN)
        "PERSON": "Astrid Johansson",
        "PHONE_NUMBER": "+46 8 555 0138",
        "EMAIL_ADDRESS": "astrid.johansson@example.se",
        "LOCATION": "Drottninggatan 50, Lagenhet 1102, 111 21 Stockholm, Sweden",
        "US_SSN": "231-49-7705",
    },
    {   # 19 - Argentina, three-word name, "Piso/Depto" lines, alphanumeric postcode
        "PERSON": "Lucia Fernandez Rossi",
        "PHONE_NUMBER": "+54 11 4555-0126",
        "EMAIL_ADDRESS": "lucia.fernandez@example.ar",
        "LOCATION": "Avenida Corrientes 1450, Piso 8 Depto B, Buenos Aires C1043AAZ, Argentina",
        "US_SSN": "205-61-8847",
    },
    {   # 20 - UAE, Arabic-script name + Arabic address, international mobile
        "PERSON": "ريم السالم",
        "PHONE_NUMBER": "+971 50 555 0119",
        "EMAIL_ADDRESS": "reem.salem@example.ae",
        "LOCATION": "شارع الكورنيش، أبوظبي",
        "US_SSN": "329-64-7752",
    },
]


# ----------------------------------------------------------------------------
# DOCX writer: plants every surface (body, TABLE, header, footer, hidden run,
# comment + author, core properties). Mirrors generate_real_docs.create_docx but adds an
# explicit table so the "table" planting surface named in the brief is present.
# ----------------------------------------------------------------------------
def create_docx(doc_id: str, planted: dict, author_name: str) -> str:
    doc = Document()
    doc.add_heading(f"Employee Report – {doc_id}", level=1)

    # ---- body paragraphs ----
    doc.add_paragraph(f"Full Name: {planted['PERSON']}")
    doc.add_paragraph(f"Phone: {planted['PHONE_NUMBER']}")
    doc.add_paragraph(f"Email: {planted['EMAIL_ADDRESS']}")
    doc.add_paragraph(f"Address: {planted['LOCATION']}")
    doc.add_paragraph(f"National ID / SSN: {planted['US_SSN']}")
    doc.add_paragraph("")
    doc.add_paragraph("Notes: This employee joined the company recently.")
    doc.add_paragraph("Performance review is scheduled for next month.")
    doc.add_paragraph(f"For HR inquiries contact {DECOY_EMAIL}")

    # ---- TABLE surface (a 2-column "field / value" grid; same PII planted again) ----
    table = doc.add_table(rows=0, cols=2)
    try:
        table.style = "Table Grid"
    except Exception:
        pass  # style name not available in some python-docx builds; grid lines are cosmetic
    for label, value in (("Employee", planted["PERSON"]),
                         ("Contact", planted["PHONE_NUMBER"]),
                         ("Residence", planted["LOCATION"])):
        row = table.add_row().cells
        row[0].text = label
        row[1].text = value

    # ---- hidden / secondary content (must also be redacted) ----
    sec = doc.sections[0]
    sec.header.paragraphs[0].text = f"Confidential - {planted['PERSON']}"          # header
    sec.footer.paragraphs[0].text = f"Contact: {planted['EMAIL_ADDRESS']}"          # footer
    hp = doc.add_paragraph()
    hr = hp.add_run(f"Backup phone: {planted['PHONE_NUMBER']}")                    # hidden text
    hr.font.hidden = True
    if hasattr(doc, "add_comment"):                                                 # python-docx >= 1.2
        cp = doc.add_paragraph("Reviewed by HR.")
        doc.add_comment(cp.runs, text=f"Check SSN {planted['US_SSN']} for {planted['PERSON']}",
                        author=author_name, initials="HR")

    # ---- metadata (core properties) ----
    core = doc.core_properties
    core.author = author_name
    core.title = f"Confidential – {planted['PERSON']}"
    core.subject = "Employee personal file"
    core.keywords = f"{planted['PERSON']}, {planted['EMAIL_ADDRESS']}"
    core.comments = f"Created for {planted['PERSON']}"

    path = os.path.join(DOCX_DIR, f"{doc_id}.docx")
    doc.save(path)
    return path


# ----------------------------------------------------------------------------
# PDF writer: visible text + white (hidden) text + metadata. Mirrors
# generate_real_docs.create_pdf, including the Arabic hidden-logical-order trick.
# ----------------------------------------------------------------------------
def create_pdf(doc_id: str, planted: dict, author_name: str) -> str:
    path = os.path.join(PDF_DIR, f"{doc_id}.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Employee Report – {doc_id}")
    y -= 40

    c.setFont("Helvetica", 11)
    lines = [
        f"Full Name: {planted['PERSON']}",
        f"Phone: {planted['PHONE_NUMBER']}",
        f"Email: {planted['EMAIL_ADDRESS']}",
        f"Address: {planted['LOCATION']}",
        f"National ID / SSN: {planted['US_SSN']}",
        "",
        "Notes: This employee joined the company recently.",
        "Performance review is scheduled for next month.",
        f"For HR inquiries contact {DECOY_EMAIL}",
    ]
    arabic_ok = _ensure_arabic_font()

    # invisible (white) text = hidden content that copy-paste / extraction still returns
    c.setFillColorRGB(1, 1, 1)
    c.drawString(50, 40, f"Backup phone: {planted['PHONE_NUMBER']}  SSN: {planted['US_SSN']}")
    # Arabic PII is ALSO embedded as hidden text in LOGICAL order so extraction/copy-paste
    # returns it. The VISIBLE Arabic line is shaped into presentation forms (correct RTL
    # rendering) and does NOT round-trip to the original Unicode; this hidden logical copy
    # models the text layer a real Office-generated Arabic PDF carries, and is what keeps the
    # Arabic person TESTABLE. Drawn reversed because reportlab lays glyphs left-to-right, so
    # pypdf (which reads left-to-right) reverses it back to logical order. No-op for Latin.
    if arabic_ok:
        c.setFont(_ARABIC_FONT_NAME, 10)
        yy = 30
        for v in (planted["PERSON"], planted["LOCATION"]):
            if _has_arabic(v):
                c.drawString(50, yy, v[::-1])
                yy -= 12
        c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)

    # Arabic needs a Unicode font + reshaping/bidi; visible Latin lines keep Helvetica.
    for line in lines:
        if line and _has_arabic(line):
            if arabic_ok:
                c.setFont(_ARABIC_FONT_NAME, 12)
                c.drawString(50, y, _shape_arabic(line))
                c.setFont("Helvetica", 11)
            else:
                _warn_no_arabic_once()
                c.drawString(50, y, line.encode("ascii", "replace").decode("ascii"))
        else:
            try:
                c.drawString(50, y, line)
            except Exception:
                c.drawString(50, y, line.encode("ascii", "replace").decode("ascii"))
        y -= 22

    c.save()

    # add real metadata (planted author / title / creator / keywords)
    reader = PdfReader(path)
    writer = PdfWriter()
    writer.append(reader)

    writer.add_metadata({
        "/Author": author_name,
        "/Title": f"Confidential – {planted['PERSON']}",
        "/Subject": "Employee personal file",
        "/Creator": f"HR System – {planted['PERSON']}",
        "/Producer": "Internal Generator v1.0",
        "/Keywords": f"{planted['PERSON']}, {planted['EMAIL_ADDRESS']}",
    })

    with open(path, "wb") as f:
        writer.write(f)

    return path


# ----------------------------------------------------------------------------
# Safety self-check: catches the two mistakes that silently break the attack metric
# (see docs/RED_TEAM_REIDENTIFICATION.md and the project memory):
#   1. a numeric field containing a DOCX boilerplate digit run (would force k=0), and
#   2. a duplicate PERSON name (the population is deduped by name, so a dup hides a person).
# It also checks the SSN shape so US_SSN stays a clean control. It PRINTS problems and
# raises, so a bad edit fails loudly at generation time rather than corrupting the evidence.
# ----------------------------------------------------------------------------
# Digit runs python-docx stamps into every DOCX (app.xml AppVersion "16.0000", core.xml
# created/modified years, thumbnail JPEG bytes). If a person's number contains one of these,
# the run becomes "linkable" against that person and collapses other docs to an empty set.
_BOILERPLATE_DIGIT_RUNS = ("0000", "2001", "2006", "2007", "2013", "56789", "456789")
_SSN_SHAPE = re.compile(r"^\d{3}-\d{2}-\d{4}$")


def _field_digits(value: str) -> str:
    """ALL digits of a value, separators removed -- EXACTLY how attack_real_docs.py builds a
    population record's per-field digit string (`re.sub(r"\\D","",value)`). It must match the
    attack, because a boilerplate run can hide ACROSS a separator: "Apto 302 ... 01305" has no
    4-digit run containing 2013, yet "30201305" (concatenated) does -> that is what collapses
    the anonymity set to k=0, so we check the concatenated form, not the raw runs."""
    return re.sub(r"\D", "", value)


def self_check(people) -> None:
    problems = []

    names = [p["PERSON"] for p in people]
    for name in names:
        if names.count(name) > 1:
            problems.append(f"duplicate PERSON name: {name!r}")

    for i, p in enumerate(people):
        # SSN control: standard US shape so detection stays comparable to the real set.
        if not _SSN_SHAPE.match(p["US_SSN"]):
            problems.append(f"person {i}: US_SSN {p['US_SSN']!r} is not NNN-NN-NNNN")
        # k=0 guard: no field's concatenated digits may contain a boilerplate run that
        # python-docx stamps into every DOCX (core.xml dates 2001/2006/2013, app.xml 0000,
        # thumbnail bytes). If one did, that run would become linkable to this person and
        # collapse every OTHER document to an empty anonymity set (k=0).
        for field, value in p.items():
            digits = _field_digits(value)
            for bad in _BOILERPLATE_DIGIT_RUNS:
                if bad in digits:
                    problems.append(
                        f"person {i} ({p['PERSON']}): {field}={value!r} concatenated digits "
                        f"{digits!r} contain DOCX-boilerplate run {bad!r} -> would cause k=0")

    if problems:
        print("SELF-CHECK FAILED:")
        for pr in problems:
            print("  -", pr)
        raise SystemExit("Fix the synthetic data above before generating (see comments).")
    print(f"Self-check OK: {len(people)} distinct people, no boilerplate digit collisions.")


def main():
    # Fail fast on bad data BEFORE writing 40 files + ground truth.
    self_check(FRESH_PEOPLE)

    truth = {}

    for i, planted in enumerate(FRESH_PEOPLE):
        author = planted["PERSON"]  # the name is planted into the metadata on purpose

        # ----- DOCX -----
        doc_id = f"docx_{i:02d}"
        create_docx(doc_id, planted, author)
        truth[doc_id] = {
            "type": "docx",
            "planted_text": planted,
            "planted_metadata": {
                "author": author,
                "title": f"Confidential – {planted['PERSON']}",
                "keywords": f"{planted['PERSON']}, {planted['EMAIL_ADDRESS']}",
                "comments": f"Created for {planted['PERSON']}",
            },
            "decoys": [DECOY_EMAIL],
        }

        # ----- PDF -----
        doc_id = f"pdf_{i:02d}"
        create_pdf(doc_id, planted, author)
        truth[doc_id] = {
            "type": "pdf",
            "planted_text": planted,
            "planted_metadata": {
                "author": author,
                "title": f"Confidential – {planted['PERSON']}",
                "creator": f"HR System – {planted['PERSON']}",
                "keywords": f"{planted['PERSON']}, {planted['EMAIL_ADDRESS']}",
            },
            "decoys": [DECOY_EMAIL],
        }

    truth_path = os.path.join(OUT_DIR, "ground_truth_fresh.json")
    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(truth, f, indent=2, ensure_ascii=False)

    n = len(FRESH_PEOPLE)
    print("=" * 50)
    print("Done! Generated FRESH hold-out documents with planted PII + metadata")
    print(f"  Population  : {n} NEW distinct synthetic individuals (unseen by v1-v4)")
    print(f"  DOCX files : {DOCX_DIR}/  ({n} files, body/table/header/footer/hidden/comment)")
    print(f"  PDF  files : {PDF_DIR}/   ({n} files, visible/hidden/metadata)")
    print(f"  Total       : {2 * n} documents")
    print(f"  Ground truth: {truth_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
