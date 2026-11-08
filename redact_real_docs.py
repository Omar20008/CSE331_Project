"""
redact_real_docs.py
CSE331 - Project 09

يأخذ ملفات DOCX و PDF من documents_real/
يستخرج النص → يطبق الـ detector من pipelines.py (v1/v2/v3)
يعيد كتابة الملف بعد التعتيم + ينظف الـ metadata

الاستخدام:
    python redact_real_docs.py          # يشغل v3 (الأفضل)
    python redact_real_docs.py v2       # أو أي نسخة ثانية
"""

import os
import re
import sys

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from presidio_anonymizer import AnonymizerEngine

# استيراد الـ detector من ملفك
from pipelines import make_detector, ALLOW_LIST

# ------------------------------------------------------------ إعدادات
# ---------------------------------------------------------------- CLI: version + dataset
# Accept the detector version and an OPTIONAL dataset keyword ("real" | "fresh") in any
# order. The detector/pipeline is IDENTICAL for both datasets (pipelines.py is untouched);
# only the input/output folders change, so the fresh hold-out is redacted by the exact same
# v1..v4 code the real set uses.  `python redact_real_docs.py v4`         -> redacted_real_v4/
#                                `python redact_real_docs.py v4 fresh`    -> redacted_fresh_v4/
_args = sys.argv[1:]
DATASET = "real"
_positional = []
for _a in _args:
    if _a in ("real", "fresh"):
        DATASET = _a
    else:
        _positional.append(_a)
VERSION = _positional[0] if _positional else "v3"

SRC_DOCX = os.path.join(f"documents_{DATASET}", "docx")
SRC_PDF = os.path.join(f"documents_{DATASET}", "pdf")
TRUTH_FILE = os.path.join(f"documents_{DATASET}", f"ground_truth_{DATASET}.json")

OUT_DIR = f"redacted_{DATASET}_{VERSION}"

# Document-consistent redaction (v4): detect PII once over the WHOLE document, then scrub
# every occurrence. This catches a name in a header/comment that paragraph-by-paragraph
# NER misses in isolation, because spaCy's PERSON detection depends on surrounding context.
CONSISTENT = VERSION == "v4"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "docx"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "pdf"), exist_ok=True)

anonymizer = AnonymizerEngine()
detect = make_detector(VERSION)


def redact_text(text: str) -> str:
    """يشغل الـ detector ثم يستبدل المعرفات بـ <ENTITY>"""
    if not text or not text.strip():
        return text
    results = detect(text)
    if not results:
        return text
    redacted = anonymizer.anonymize(text=text, analyzer_results=results)
    return redacted.text


# ------------------------------------------------------------ DOCX
def redact_paragraph(para, global_map=None):
    original = para.text
    if not original.strip():
        return
    new_text = redact_text(original)
    # document-consistent scrub: remove any value detected elsewhere in this document
    if global_map:
        for value, ent in global_map.items():
            if value in new_text:
                new_text = new_text.replace(value, f"<{ent}>")
    if new_text != original:
        for run in para.runs:
            run.text = ""
        if para.runs:
            para.runs[0].text = new_text
        else:
            para.add_run(new_text)


def iter_container_paragraphs(container):
    """paragraphs + paragraphs inside tables (recursive)"""
    for p in container.paragraphs:
        yield p
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from iter_container_paragraphs(cell)


def iter_all_docx_paragraphs(doc):
    """every editable paragraph in the document: body, headers/footers, comments."""
    yield from iter_container_paragraphs(doc)
    for section in doc.sections:
        for part in (section.header, section.footer,
                     section.first_page_header, section.first_page_footer,
                     section.even_page_header, section.even_page_footer):
            yield from iter_container_paragraphs(part)
    if hasattr(doc, "comments"):
        for comment in doc.comments:
            yield from iter_container_paragraphs(comment)


def build_global_map(doc):
    """Detect PII once over the whole document; return {detected_value: entity_type}."""
    joined = "\n".join(p.text for p in iter_all_docx_paragraphs(doc) if p.text.strip())
    global_map = {}
    for r in detect(joined):
        value = joined[r.start:r.end]
        if value and value not in ALLOW_LIST:
            global_map.setdefault(value, r.entity_type)
    return global_map


def process_docx(src_path: str, out_path: str):
    doc = Document(src_path)

    global_map = build_global_map(doc) if CONSISTENT else None

    # body (paragraphs + tables; hidden runs live inside these paragraphs)
    for para in iter_container_paragraphs(doc):
        redact_paragraph(para, global_map)

    # headers / footers (all variants)
    for section in doc.sections:
        for part in (section.header, section.footer,
                     section.first_page_header, section.first_page_footer,
                     section.even_page_header, section.even_page_footer):
            for para in iter_container_paragraphs(part):
                redact_paragraph(para, global_map)

    # comments (python-docx >= 1.2): text + author name
    if hasattr(doc, "comments"):
        for comment in doc.comments:
            for para in iter_container_paragraphs(comment):
                redact_paragraph(para, global_map)
            try:
                comment.author = ""
                comment.initials = ""
            except Exception:
                pass

    # core properties
    core = doc.core_properties
    core.author = ""
    core.title = ""
    core.subject = ""
    core.keywords = ""
    core.comments = ""
    core.last_modified_by = ""
    try:
        core.category = ""
    except Exception:
        pass

    doc.save(out_path)
    print(f"  [DOCX] {os.path.basename(src_path)} -> redacted (body/tables/headers/footers/comments) + metadata cleaned")


# ------------------------------------------------------------ PDF
def extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n".join(parts)


def process_pdf(src_path: str, out_path: str):
    # 1) استخراج النص
    original_text = extract_pdf_text(src_path)

    # 2) تعتيم
    redacted_text = redact_text(original_text)

    # 3) كتابة PDF جديد بالنص المعتّم (تخطيط مبسط)
    c = canvas.Canvas(out_path, pagesize=A4)
    _, height = A4
    y = height - 50
    c.setFont("Helvetica", 10)

    for line in redacted_text.splitlines():
        # تجنب مشاكل الترميز
        try:
            safe = line.encode("cp1252", "replace").decode("cp1252")
        except Exception:
            safe = re.sub(r"[^\x00-\x7F]", "?", line)

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50

        c.drawString(40, y, safe[:110])  # قص السطر الطويل
        y -= 14

    c.save()

    # 4) تنظيف metadata بشكل صريح
    reader = PdfReader(out_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata({
        "/Author": "",
        "/Title": "",
        "/Subject": "",
        "/Creator": "",
        "/Producer": "",
        "/Keywords": "",
    })
    with open(out_path, "wb") as f:
        writer.write(f)

    print(f"  [PDF ] {os.path.basename(src_path)} -> redacted + metadata cleaned")


# ------------------------------------------------------------ main
def main():
    print(f"Redacting real documents using detector: {VERSION}")
    print(f"Output folder: {OUT_DIR}/")
    print("-" * 50)

    # DOCX
    if os.path.isdir(SRC_DOCX):
        for name in sorted(os.listdir(SRC_DOCX)):
            if name.endswith(".docx"):
                process_docx(
                    os.path.join(SRC_DOCX, name),
                    os.path.join(OUT_DIR, "docx", name),
                )

    # PDF
    if os.path.isdir(SRC_PDF):
        for name in sorted(os.listdir(SRC_PDF)):
            if name.endswith(".pdf"):
                process_pdf(
                    os.path.join(SRC_PDF, name),
                    os.path.join(OUT_DIR, "pdf", name),
                )

    print("-" * 50)
    print("Done.")
    print(f"Redacted files are in: {OUT_DIR}/")
    print("Next step: run evaluation on these files.")


if __name__ == "__main__":
    main()