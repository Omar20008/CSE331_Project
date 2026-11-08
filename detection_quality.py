"""
detection_quality.py
CSE331 - Project 09: Document Redaction & Metadata Privacy

Measures DETECTOR quality (precision / recall per entity) on the ORIGINAL documents.
This is deliberately separate from evaluate_real_docs.py:

  * evaluate_real_docs.py  answers "did any sensitive VALUE survive in the redacted file?"
                           (the privacy OUTCOME / residual disclosure)
  * detection_quality.py   answers "how good is the DETECTOR itself at spotting PII?"
                           (precision / recall, the metric the Project-09 brief asks for)

Definitions (span overlap against the ground-truth values):
  recall(entity)   = planted values of that entity the detector flags / planted values present
  precision(micro) = detector spans that hit a planted sensitive value / all detector spans
                     A span over the decoy (hr@company.com) is a FALSE POSITIVE, because the
                     decoy must stay in the document.

Usage:
    python detection_quality.py            # all versions: v1 v2 v3 v4
    python detection_quality.py v4         # a single version
"""

import json
import os
import re
import sys
import zipfile

from pypdf import PdfReader

from pipelines import ENTITIES, make_detector

# ---------------------------------------------------------------- CLI: version + dataset
# Optional single version and an OPTIONAL dataset keyword ("real" | "fresh"), in any order:
#   python detection_quality.py            -> v1..v4 on the real set (historical default)
#   python detection_quality.py v4         -> v4 only, real set
#   python detection_quality.py fresh      -> v1..v4 on the unseen fresh hold-out set
#   python detection_quality.py v4 fresh   -> v4 only, fresh set
# "fresh" reads documents_fresh/ and writes detection_quality_fresh.txt (real output kept).
_args = sys.argv[1:]
DATASET = "real"
_positional = []
for _a in _args:
    if _a in ("real", "fresh"):
        DATASET = _a
    else:
        _positional.append(_a)
VERSIONS = [_positional[0]] if _positional else ["v1", "v2", "v3", "v4"]

ORIG_ROOT = f"documents_{DATASET}"                       # documents_real | documents_fresh
TRUTH_FILE = os.path.join(ORIG_ROOT, f"ground_truth_{DATASET}.json")

_WT = re.compile(r"<w:(?:t|delText)[^>]*>([^<]*)</w:(?:t|delText)>")


def docx_text(path):
    """All text runs (body, headers, footers, comments, hidden runs) as one string."""
    out = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                out += _WT.findall(z.read(name).decode("utf-8", "ignore"))
    return "\n".join(out)


def pdf_text(path):
    reader = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract(doc_id, dtype):
    path = os.path.join(ORIG_ROOT, dtype, f"{doc_id}.{dtype}")
    return docx_text(path) if dtype == "docx" else pdf_text(path)


def spans_of(value, text):
    """All (start, end) occurrences of an exact value in text."""
    out, i = [], text.find(value)
    while i != -1:
        out.append((i, i + len(value)))
        i = text.find(value, i + 1)
    return out


def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]


def run_version(version, truth):
    detect = make_detector(version)
    present = {e: 0 for e in ENTITIES}
    tp_recall = {e: 0 for e in ENTITIES}
    det_total = det_tp = fp_decoy = fp_other = 0
    not_extractable = 0

    for doc_id, info in sorted(truth.items()):
        text = extract(doc_id, info["type"])
        results = detect(text)
        det_spans = [(r.start, r.end) for r in results]

        planted_spans = []
        for value in info["planted_text"].values():
            planted_spans += spans_of(value, text)
        decoy_spans = []
        for d in info.get("decoys", []):
            decoy_spans += spans_of(d, text)

        # recall, per entity
        for ent, value in info["planted_text"].items():
            vspans = spans_of(value, text)
            if not vspans:
                not_extractable += 1          # e.g. Arabic drawn in a PDF with Helvetica
                continue
            present[ent] += 1
            if any(overlaps(v, d) for v in vspans for d in det_spans):
                tp_recall[ent] += 1

        # precision, micro over all detector spans
        for d in det_spans:
            det_total += 1
            if any(overlaps(d, p) for p in planted_spans):
                det_tp += 1
            elif any(overlaps(d, dc) for dc in decoy_spans):
                fp_decoy += 1
            else:
                fp_other += 1

    lines = [
        "=" * 70,
        f"DETECTION QUALITY   detector: {version}",
        "=" * 70,
        f"{'Entity':<15}{'Present':>9}{'Found':>8}{'Missed':>8}{'Recall':>9}",
    ]
    tot_present = tot_found = 0
    for e in ENTITIES:
        p, f = present[e], tp_recall[e]
        tot_present += p
        tot_found += f
        rec = f / p * 100 if p else float("nan")
        lines.append(f"{e:<15}{p:>9}{f:>8}{p - f:>8}{rec:>8.1f}%")
    lines.append("-" * 70)
    micro_rec = tot_found / tot_present * 100 if tot_present else float("nan")
    precision = det_tp / det_total * 100 if det_total else float("nan")
    lines.append(f"Recall  (all entities, micro)       : {micro_rec:.1f}%  ({tot_found}/{tot_present})")
    lines.append(f"Precision (detector spans on PII)   : {precision:.1f}%  ({det_tp}/{det_total})")
    lines.append(f"False positives - decoy redacted    : {fp_decoy}")
    lines.append(f"False positives - other             : {fp_other}")
    lines.append(f"Planted values not extractable      : {not_extractable}  (excluded from recall)")
    return "\n".join(lines)


def main():
    with open(TRUTH_FILE, encoding="utf-8") as f:
        truth = json.load(f)

    blocks = [run_version(v, truth) for v in VERSIONS]
    report = "\n\n".join(blocks)
    print(report)

    # real -> detection_quality.txt (unchanged); fresh -> detection_quality_fresh.txt
    out_name = "detection_quality.txt" if DATASET == "real" else f"detection_quality_{DATASET}.txt"
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\nSaved: {out_name}")


if __name__ == "__main__":
    main()
