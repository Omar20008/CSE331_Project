"""
check_metadata.py
يفحص إذا بقي metadata حساس في الملفات (قبل أو بعد التنظيف)
"""

import os
import json
from docx import Document
from pypdf import PdfReader

TRUTH_FILE = "documents_real/ground_truth_real.json"


def check_docx(path):
    doc = Document(path)
    core = doc.core_properties
    return {
        "author": core.author or "",
        "title": core.title or "",
        "keywords": core.keywords or "",
        "comments": core.comments or "",
    }


def check_pdf(path):
    reader = PdfReader(path)
    md = reader.metadata
    if not md:
        return {"author": "", "title": "", "creator": "", "keywords": ""}
    return {
        "author": md.author or "",
        "title": md.title or "",
        "creator": md.creator or "",
        "keywords": getattr(md, "keywords", "") or "",
    }


def main():
    with open(TRUTH_FILE, encoding="utf-8") as f:
        truth = json.load(f)

    print("=" * 60)
    print("METADATA CHECK (residual sensitive values)")
    print("=" * 60)

    folders = [
        ("ORIGINAL DOCX", "documents_real/docx"),
        ("ORIGINAL PDF", "documents_real/pdf"),
        ("CLEANED meta DOCX", "redacted_real/meta/docx"),
        ("CLEANED meta PDF", "redacted_real/meta/pdf"),
    ]

    for label, folder in folders:
        if not os.path.isdir(folder):
            print(f"\n[{label}] folder not found -> skipped")
            continue

        print(f"\n--- {label} ---")
        residual_count = 0

        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            doc_id = os.path.splitext(name)[0]

            if doc_id not in truth:
                continue

            planted_md = truth[doc_id]["planted_metadata"]
            sensitive_values = set(v for v in planted_md.values() if v)

            if name.endswith(".docx"):
                found = check_docx(path)
            elif name.endswith(".pdf"):
                found = check_pdf(path)
            else:
                continue

            remaining = []
            for field, value in found.items():
                if value and any(s in value for s in sensitive_values):
                    remaining.append(f"{field}={value}")

            if remaining:
                residual_count += 1
                print(f"  {name}: STILL HAS -> {remaining}")
            else:
                print(f"  {name}: clean")

        print(f"  -> Documents with residual metadata: {residual_count}")


if __name__ == "__main__":
    main()
