"""
strip_metadata.py
CSE331 - Project 09

ينظف الـ metadata من ملفات DOCX و PDF بعد التعتيم.
يشيل: Author, Title, Subject, Creator, Keywords, Comments...

Output layout now MATCHES redacted_real_<version>/{docx,pdf}/ :
    redacted_real/meta/docx/   and   redacted_real/meta/pdf/
This "meta" baseline is a metadata-only strip (no body redaction), used for comparison.
"""

import os
from docx import Document
from pypdf import PdfReader, PdfWriter

SRC_DOCX = "documents_real/docx"
SRC_PDF = "documents_real/pdf"
OUT_DIR = "redacted_real"
META_DIR = os.path.join(OUT_DIR, "meta")          # redacted_real/meta
DOCX_OUT = os.path.join(META_DIR, "docx")         # redacted_real/meta/docx
PDF_OUT = os.path.join(META_DIR, "pdf")           # redacted_real/meta/pdf

os.makedirs(DOCX_OUT, exist_ok=True)
os.makedirs(PDF_OUT, exist_ok=True)


def clean_docx(src_path: str, out_path: str):
    doc = Document(src_path)
    core = doc.core_properties
    core.author = ""
    core.title = ""
    core.subject = ""
    core.keywords = ""
    core.comments = ""
    core.last_modified_by = ""
    # بعض الإصدارات تدعم هذه الحقول
    try:
        core.category = ""
    except Exception:
        pass
    doc.save(out_path)
    print(f"[DOCX] {os.path.basename(src_path)} -> cleaned")


def clean_pdf(src_path: str, out_path: str):
    reader = PdfReader(src_path)
    writer = PdfWriter()
    writer.append(reader)

    # مسح الـ metadata
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
    print(f"[PDF ] {os.path.basename(src_path)} -> cleaned")


def main():
    print("Cleaning metadata from real documents (metadata-only baseline)...")
    print("-" * 40)

    for name in sorted(os.listdir(SRC_DOCX)):
        if name.endswith(".docx"):
            clean_docx(
                os.path.join(SRC_DOCX, name),
                os.path.join(DOCX_OUT, name),
            )

    for name in sorted(os.listdir(SRC_PDF)):
        if name.endswith(".pdf"):
            clean_pdf(
                os.path.join(SRC_PDF, name),
                os.path.join(PDF_OUT, name),
            )

    print("-" * 40)
    print(f"Done. Cleaned files are in: {META_DIR}/ (docx/ + pdf/)")


if __name__ == "__main__":
    main()
