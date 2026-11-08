"""
generate_real_docs.py
CSE331 - Project 09: Document Redaction & Metadata Privacy

Population: 20 distinct, fully synthetic individuals. Each person generates ONE DOCX and
ONE PDF, so the generator produces 20 + 20 = 40 documents (comfortably above the brief's
"at least 20 synthetic files"), plus documents_real/ground_truth_real.json.

يولّد 20 فردًا اصطناعيًا (20 DOCX + 20 PDF = 40 ملفًا)
مع معرفات مزروعة داخل النص + metadata مزروعة (Author, Title, Creator, Keywords)

Arabic names/addresses are shaped (arabic-reshaper + python-bidi) and drawn with a Unicode
font so they render and can be extracted from PDFs instead of being dropped by a Latin font.
"""

import json
import os
from docx import Document
from docx.shared import RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

OUT_DIR = "documents_real"
DOCX_DIR = os.path.join(OUT_DIR, "docx")
PDF_DIR = os.path.join(OUT_DIR, "pdf")
os.makedirs(DOCX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

DECOY_EMAIL = "hr@company.com"

# ----------------------------------------------------------------------------
# Arabic rendering support for PDFs.
# reportlab with a Latin-only font (Helvetica) cannot draw Arabic, so Arabic text used to
# be dropped. We register a Unicode TTF that has Arabic glyphs, then reshape (join letters
# into their contextual forms) and apply the bidi algorithm before drawing. Everything
# degrades gracefully: if no font or the shaping libraries are missing, we warn ONCE and
# fall back to the previous ASCII-replace behaviour.
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


# بيانات اصطناعية ثابتة (بدون Faker) – قابلة للتكرار
PEOPLE = [
    {
        "PERSON": "Omar Al-Khatib",
        "PHONE_NUMBER": "+962 79 555 1234",
        "EMAIL_ADDRESS": "omar.khatib@example.jo",
        "LOCATION": "Building 15, Wasfi Al-Tal Street, Amman 11181, Jordan",
        "US_SSN": "623-19-4580",
    },
    {
        "PERSON": "Siobhan O'Brien-Walsh",
        "PHONE_NUMBER": "+44 20 7946 0958",
        "EMAIL_ADDRESS": "siobhan.obrien-walsh@example.co.uk",
        "LOCATION": "14 Mill Lane, Cardiff CF10 3AT, UK",
        "US_SSN": "412-55-7731",
    },
    {
        "PERSON": "Aisha Khan",
        "PHONE_NUMBER": "+1 (415) 555-0132",
        "EMAIL_ADDRESS": "aisha.khan+hr@example.org",
        "LOCATION": "42 Elm Street, Apt 5B, Springfield, IL 62704",
        "US_SSN": "538-62-4417",
    },
    {
        "PERSON": "Michael Chen",
        "PHONE_NUMBER": "555 867 5309",
        "EMAIL_ADDRESS": "michael_chen@mail.example.com",
        "LOCATION": "700 Harbor Blvd, Unit 12, San Diego, CA 92101",
        "US_SSN": "528-91-4406",
    },
    {
        "PERSON": "Maria Garcia",
        "PHONE_NUMBER": "(212) 555-0147",
        "EMAIL_ADDRESS": "maria.garcia@example.com",
        "LOCATION": "88 Broadway, New York, NY 10006",
        "US_SSN": "301-44-9012",
    },
    {
        "PERSON": "محمد الخطيب",
        "PHONE_NUMBER": "0795551234",
        "EMAIL_ADDRESS": "mohammad.khateeb@example.com",
        "LOCATION": "شارع الجامعة، عمان",
        "US_SSN": "317-80-2256",
    },
    {
        "PERSON": "Priya Raman",
        "PHONE_NUMBER": "555.201.8890",
        "EMAIL_ADDRESS": "priya.raman@example.net",
        "LOCATION": "1200 Market St, Philadelphia, PA 19107",
        "US_SSN": "287-31-5540",
    },
    {
        "PERSON": "Liam Nguyen",
        "PHONE_NUMBER": "1-800-555-0199",
        "EMAIL_ADDRESS": "liam@sub.domain.example.com",
        "LOCATION": "P.O. Box 4471, Austin, TX 78765",
        "US_SSN": "140-22-6073",
    },
    {
        "PERSON": "José Ángel Martínez",
        "PHONE_NUMBER": "555-0123",
        "EMAIL_ADDRESS": "jose.martinez@example.es",
        "LOCATION": "Calle Mayor 7, Madrid 28013, Spain",
        "US_SSN": "562-19-3345",
    },
    {
        "PERSON": "Wei Zhang",
        "PHONE_NUMBER": "+1.555.123.4567",
        "EMAIL_ADDRESS": "wei.zhang@example.com",
        "LOCATION": "300 Oak Ave Apt 4, Seattle, WA 98101",
        "US_SSN": "077-14-2938",
    },
    # ----- additional synthetic individuals (population expanded to 20) -----
    {
        "PERSON": "فاطمة الزعبي",                       # Arabic-script name + Arabic address
        "PHONE_NUMBER": "+962 78 555 0146",
        "EMAIL_ADDRESS": "fatima.zoubi@example.jo",
        "LOCATION": "شارع الملكة رانيا، إربد",
        "US_SSN": "609-23-7788",
    },
    {
        "PERSON": "Mateo Hernández",
        "PHONE_NUMBER": "+34 612 55 01 88",
        "EMAIL_ADDRESS": "mateo.hernandez@example.es",
        "LOCATION": "Calle del Sol 23, Sevilla 41004, Spain",
        "US_SSN": "254-73-9910",
    },
    {
        "PERSON": "Mei Lin",
        "PHONE_NUMBER": "+86 10 5555 0123",
        "EMAIL_ADDRESS": "mei.lin@example.com",
        "LOCATION": "88 Nanjing Road, Huangpu, Shanghai 200021, China",
        "US_SSN": "231-55-7420",
    },
    {
        "PERSON": "Arjun Patel",
        "PHONE_NUMBER": "+91 22 5555 0112",
        "EMAIL_ADDRESS": "arjun.patel@example.in",
        "LOCATION": "12 MG Road, Bengaluru 560001, India",
        "US_SSN": "276-14-8835",
    },
    {
        "PERSON": "Hannah Schmidt",
        "PHONE_NUMBER": "+49 30 5550 0199",
        "EMAIL_ADDRESS": "hannah.schmidt@example.de",
        "LOCATION": "Unter den Linden 5, 10117 Berlin, Germany",
        "US_SSN": "205-66-3471",
    },
    {
        "PERSON": "Khaled Mansour",                       # Arabic-origin name, Latin script, Jordan
        "PHONE_NUMBER": "+962 79 555 0164",
        "EMAIL_ADDRESS": "khaled.mansour@example.jo",
        "LOCATION": "Mecca Street 90, Amman 11953, Jordan",
        "US_SSN": "312-48-9025",
    },
    {
        "PERSON": "Emily Watson",
        "PHONE_NUMBER": "+44 161 496 0198",
        "EMAIL_ADDRESS": "emily.watson@example.co.uk",
        "LOCATION": "22 King Street, Manchester M2 4LQ, UK",
        "US_SSN": "188-29-5540",
    },
    {
        "PERSON": "Carlos Rivera",
        "PHONE_NUMBER": "+1 (305) 555-0176",
        "EMAIL_ADDRESS": "carlos.rivera@example.com",
        "LOCATION": "500 Ocean Drive, Miami, FL 33139",
        "US_SSN": "263-51-7788",
    },
    {
        "PERSON": "Sara Haddad",                          # Arabic-origin name, Latin script, Jordan local phone
        "PHONE_NUMBER": "0796667788",
        "EMAIL_ADDRESS": "sara.haddad@example.jo",
        "LOCATION": "Rainbow Street 15, Amman 11181, Jordan",
        "US_SSN": "299-37-6610",
    },
    {
        "PERSON": "نورا المصري",                          # Arabic-script name + Arabic address
        "PHONE_NUMBER": "0781234567",
        "EMAIL_ADDRESS": "noura.masri@example.jo",
        "LOCATION": "شارع مكة، عمّان",
        "US_SSN": "341-52-8890",
    },
]


def create_docx(doc_id: str, planted: dict, author_name: str) -> str:
    doc = Document()
    doc.add_heading(f"Employee Report – {doc_id}", level=1)

    doc.add_paragraph(f"Full Name: {planted['PERSON']}")
    doc.add_paragraph(f"Phone: {planted['PHONE_NUMBER']}")
    doc.add_paragraph(f"Email: {planted['EMAIL_ADDRESS']}")
    doc.add_paragraph(f"Address: {planted['LOCATION']}")
    doc.add_paragraph(f"National ID / SSN: {planted['US_SSN']}")
    doc.add_paragraph("")
    doc.add_paragraph("Notes: This employee joined the company recently.")
    doc.add_paragraph("Performance review is scheduled for next month.")
    doc.add_paragraph(f"For HR inquiries contact {DECOY_EMAIL}")

    # ---- Hidden / secondary content (must also be redacted) ----
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

    # Metadata (Core Properties)
    core = doc.core_properties
    core.author = author_name
    core.title = f"Confidential – {planted['PERSON']}"
    core.subject = "Employee personal file"
    core.keywords = f"{planted['PERSON']}, {planted['EMAIL_ADDRESS']}"
    core.comments = f"Created for {planted['PERSON']}"

    path = os.path.join(DOCX_DIR, f"{doc_id}.docx")
    doc.save(path)
    return path


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

    # إضافة Metadata حقيقية
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


def main():
    truth = {}

    for i, planted in enumerate(PEOPLE):
        author = planted["PERSON"]  # نزرع الاسم عمداً داخل الـ metadata

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

    truth_path = os.path.join(OUT_DIR, "ground_truth_real.json")
    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(truth, f, indent=2, ensure_ascii=False)

    n = len(PEOPLE)
    print("=" * 50)
    print("Done! Generated real documents with planted PII + metadata")
    print(f"  Population  : {n} distinct synthetic individuals")
    print(f"  DOCX files : {DOCX_DIR}/  ({n} files, with header/footer/hidden text/comment)")
    print(f"  PDF  files : {PDF_DIR}/   ({n} files)")
    print(f"  Total       : {2 * n} documents")
    print(f"  Ground truth: {truth_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()