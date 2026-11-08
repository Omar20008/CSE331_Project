"""
evaluate_real_docs.py
CSE331 - Project 09

Evaluates redaction of the real DOCX + PDF files against ground_truth_real.json.

What it checks (same conditions for every approach):
  - Text leaks per entity: FULL (exact value still present) and PARTIAL (a token of it remains)
  - WHERE the leak is: body / header / footer / comments / hidden text / PDF annotation
  - Metadata leaks (all fields, including comment authors, subject, creator, producer)
  - False redactions (decoy hr@company.com removed)
  - Utility / readability (share of non-sensitive words that survived + placeholder count)
  - NOT-TESTABLE values (planted value not extractable from the ORIGINAL file, e.g. Arabic in
    a PDF drawn with Helvetica) are reported separately and never counted as "no leak".

Usage:
    python evaluate_real_docs.py            # redacted_real_v3/
    python evaluate_real_docs.py v2         # redacted_real_v2/
    python evaluate_real_docs.py meta       # redacted_real/  (metadata-only baseline from strip_metadata.py)
    python evaluate_real_docs.py original   # documents_real/ (baseline: should show leaks everywhere)
"""

import csv
import json
import os
import re
import sys
import zipfile

from docx import Document
from pypdf import PdfReader

# ---------------------------------------------------------------- CLI: version + dataset
# Accept the detector version and an OPTIONAL dataset keyword ("real" | "fresh") in any
# order, so both the historical  `python evaluate_real_docs.py v4`  (real set) and the new
# `python evaluate_real_docs.py v4 fresh`  work. "fresh" points every path at the unseen
# documents_fresh/ hold-out set and writes separate evidence files (evaluation_fresh_*.txt),
# so the existing real-set outputs are never overwritten. Default stays "real".
_args = sys.argv[1:]
DATASET = "real"
_positional = []
for _a in _args:
    if _a in ("real", "fresh"):
        DATASET = _a
    else:
        _positional.append(_a)
VERSION = _positional[0] if _positional else "v3"

ORIG_ROOT = f"documents_{DATASET}"                       # documents_real | documents_fresh
TRUTH_FILE = os.path.join(ORIG_ROOT, f"ground_truth_{DATASET}.json")

if VERSION == "original":
    ROOT = ORIG_ROOT
elif VERSION == "meta":
    ROOT = f"redacted_{DATASET}"
else:
    ROOT = f"redacted_{DATASET}_{VERSION}"

ENTITIES = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "US_SSN"]
GENERIC = {  # address/format words that are not identifying on their own
    "street", "road", "lane", "avenue", "blvd", "unit", "apt", "calle", "mayor", "market",
    "jordan", "spain", "broadway", "harbor", "confidential", "employee", "personal", "file",
    "created", "system", "example", "mail", "sub", "domain",
}
PLACEHOLDER = re.compile(r"<[A-Z_]+>")
TOKEN = re.compile(r"\w+", re.UNICODE)


# ------------------------------------------------------------------ extraction
def _wt(xml: str) -> str:
    """all text runs (incl. hidden <w:vanish> runs and deleted text) from a WordprocessingML part"""
    return "\n".join(re.findall(r"<w:(?:t|delText)[^>]*>([^<]*)</w:(?:t|delText)>", xml))


def extract_docx(path):
    """returns (parts: {location: text}, meta: {field: value})"""
    parts, meta = {}, {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.startswith("word/") or not name.endswith(".xml"):
                continue
            base = os.path.basename(name)
            xml = z.read(name).decode("utf-8", "ignore")
            if base == "document.xml":
                parts["body"] = _wt(xml)
                hidden = re.findall(r"<w:r>(?:(?!</w:r>).)*?<w:vanish/>(?:(?!</w:r>).)*?</w:r>", xml, re.S)
                parts["hidden_text"] = "\n".join(_wt(h) for h in hidden)
            elif re.match(r"header\d*\.xml", base):
                parts["header:" + base] = _wt(xml)
            elif re.match(r"footer\d*\.xml", base):
                parts["footer:" + base] = _wt(xml)
            elif base in ("comments.xml", "footnotes.xml", "endnotes.xml"):
                parts[base.replace(".xml", "")] = _wt(xml)
                if base == "comments.xml":
                    meta["comment_authors"] = " ".join(
                        re.findall(r'w:(?:author|initials)="([^"]*)"', xml))
        # every docProps part (core, app, custom) as raw text
        for name in z.namelist():
            if name.startswith("docProps/") and name.endswith(".xml"):
                meta[os.path.basename(name)] = " ".join(re.findall(r">([^<]+)<", z.read(name).decode("utf-8", "ignore")))
    core = Document(path).core_properties
    for f in ("author", "title", "subject", "keywords", "comments", "last_modified_by", "category"):
        meta["core." + f] = getattr(core, f, "") or ""
    return parts, meta


def extract_pdf(path):
    reader = PdfReader(path)
    parts = {"body": "\n".join((p.extract_text() or "") for p in reader.pages)}
    annots = []
    for p in reader.pages:
        for a in (p.get("/Annots") or []):
            a = a.get_object()
            for key in ("/Contents", "/T", "/Subj"):
                if a.get(key):
                    annots.append(str(a.get(key)))
            act = a.get("/A")
            if act and act.get_object().get("/URI"):
                annots.append(str(act.get_object().get("/URI")))
    parts["annotations"] = "\n".join(annots)
    md = reader.metadata or {}
    meta = {str(k).lstrip("/"): str(v) for k, v in md.items()}
    try:
        xmp = reader.xmp_metadata
        if xmp is not None:
            meta["xmp"] = str(xmp.rdf_root.toxml()) if hasattr(xmp, "rdf_root") else ""
    except Exception:
        pass
    return parts, meta


def extract(path, doc_type):
    return extract_docx(path) if doc_type == "docx" else extract_pdf(path)


def redacted_path(doc_id, doc_type):
    if VERSION in ("original",):
        return os.path.join(ORIG_ROOT, doc_type, f"{doc_id}.{doc_type}")
    if VERSION == "meta":
        return os.path.join(ROOT, "meta", doc_type, f"{doc_id}.{doc_type}")
    return os.path.join(ROOT, doc_type, f"{doc_id}.{doc_type}")


# ------------------------------------------------------------------ helpers
def tokens(value):
    out = set()
    for t in TOKEN.findall(value):
        tl = t.lower()
        if tl in GENERIC:
            continue
        if len(t) >= 4:
            out.add(tl)
    return out


def classify(value, text, exclude=frozenset()):
    """returns ('full'|'partial'|None, sorted list of tokens that remain).
    `exclude` = tokens already explained by another leaked entity (e.g. the person's name
    appearing inside that person's e-mail address) so one leak is not counted twice."""
    if value and value in text:
        return "full", []
    toks = tokens(value) - set(exclude)
    words = set(w.lower() for w in TOKEN.findall(text.lower()))
    hit = sorted(toks & words)
    return ("partial", hit) if hit else (None, [])


def words_of(text):
    return [w.lower() for w in TOKEN.findall(PLACEHOLDER.sub(" ", text))]


# ------------------------------------------------------------------ main
def main():
    with open(TRUTH_FILE, encoding="utf-8") as f:
        truth = json.load(f)

    stats = {e: {"present": 0, "full": 0, "partial": 0} for e in ENTITIES}
    not_testable = []
    meta_present = meta_full = meta_partial = 0
    where = {}
    decoys_total = false_red = 0
    util_num = util_den = 0
    placeholders = 0
    docs = docs_with_full_leak = docs_with_meta_leak = 0
    failed = []

    print("=" * 70)
    print(f"EVALUATION - {DATASET} documents   approach: {VERSION}   folder: {ROOT}/")
    print("=" * 70)

    for doc_id, info in sorted(truth.items()):
        dtype = info["type"]
        orig_path = os.path.join(ORIG_ROOT, dtype, f"{doc_id}.{dtype}")
        red_path = redacted_path(doc_id, dtype)
        if not os.path.exists(red_path):
            print(f"  MISSING: {red_path}")
            continue
        docs += 1

        o_parts, o_meta = extract(orig_path, dtype)
        r_parts, r_meta = extract(red_path, dtype)
        o_all = "\n".join(o_parts.values())
        r_all = "\n".join(r_parts.values())
        o_meta_all = "\n".join(o_meta.values())
        r_meta_all = "\n".join(r_meta.values())

        doc_full = doc_meta = False

        # ---- text leaks (only values that were actually extractable from the original) ----
        for ent, value in info["planted_text"].items():
            if value not in o_all:
                not_testable.append(f"{doc_id} | {ent} | {value!r} not present in original extracted text")
                continue
            stats[ent]["present"] += 1
            excl = tokens(info["planted_text"]["PERSON"]) if ent != "PERSON" else frozenset()
            kind, rem = classify(value, r_all, excl)
            if kind:
                stats[ent][kind] += 1
                doc_full |= kind == "full"
                locs = [loc for loc, t in r_parts.items() if classify(value, t, excl)[0]]
                for loc in locs:
                    where[loc.split(":")[0]] = where.get(loc.split(":")[0], 0) + 1
                note = ("remaining tokens: " + ", ".join(rem)) if rem else ""
                failed.append((doc_id, f"TEXT-{kind.upper()}", ",".join(locs), ent, value, note))

        # ---- metadata leaks ----
        for field, value in info["planted_metadata"].items():
            if not value:
                continue
            meta_present += 1
            kind, rem = classify(value, r_meta_all)
            if kind:
                if kind == "full":
                    meta_full += 1
                else:
                    meta_partial += 1
                doc_meta = True
                fields = [k for k, v in r_meta.items() if classify(value, v)[0]]
                failed.append((doc_id, f"META-{kind.upper()}", ",".join(fields), field, value,
                               ("remaining tokens: " + ", ".join(rem)) if rem else ""))
        # also catch sensitive values that moved into other metadata fields
        for ent in ("PERSON", "EMAIL_ADDRESS"):
            v = info["planted_text"][ent]
            if classify(v, r_meta_all)[0] and not any(
                    f[0] == doc_id and f[1].startswith("META") and f[4] == v for f in failed):
                meta_full += 1
                doc_meta = True
                failed.append((doc_id, "META-FULL", "(other field)", ent, v, ""))

        # ---- decoys ----
        for d in info.get("decoys", []):
            if d in o_all:
                decoys_total += 1
                if d not in r_all:
                    false_red += 1
                    failed.append((doc_id, "FALSE-REDACTION", "body", "decoy", d, ""))

        # ---- utility ----
        sens = set()
        for v in list(info["planted_text"].values()) + list(info["planted_metadata"].values()):
            sens |= set(words_of(v))   # every word of a planted value (incl. 'example', '555', 'jo') is sensitive
        base_words = [w for w in set(words_of(o_all)) if w not in sens and len(w) > 1]
        kept = set(words_of(r_all))
        util_den += len(base_words)
        util_num += sum(1 for w in base_words if w in kept)
        placeholders += len(PLACEHOLDER.findall(r_all))

        docs_with_full_leak += doc_full
        docs_with_meta_leak += doc_meta
        flag = []
        if doc_full:
            flag.append("TEXT-LEAK")
        if doc_meta:
            flag.append("META-LEAK")
        print(f"  {doc_id:10} {' | '.join(flag) if flag else 'OK'}")

    # ------------------------------------------------------------------ report
    lines = []
    lines.append("-" * 70)
    lines.append(f"{'Entity':<15}{'Testable':>9}{'Full leak':>11}{'Partial':>9}{'Recall':>9}")
    for e in ENTITIES:
        s = stats[e]
        rec = (1 - s["full"] / s["present"]) * 100 if s["present"] else float("nan")
        lines.append(f"{e:<15}{s['present']:>9}{s['full']:>11}{s['partial']:>9}{rec:>8.1f}%")
    tot_full = sum(s["full"] for s in stats.values())
    tot_part = sum(s["partial"] for s in stats.values())
    lines.append("-" * 70)
    lines.append(f"Documents evaluated                 : {docs}")
    lines.append(f"Text: residual full leaks           : {tot_full}  (docs affected: {docs_with_full_leak}/{docs})")
    lines.append(f"Text: residual partial leaks        : {tot_part}")
    lines.append(f"Leak locations (full+partial)       : {where if where else 'none'}")
    lines.append(f"Metadata values planted             : {meta_present}")
    lines.append(f"Metadata: full / partial leaks      : {meta_full} / {meta_partial}  (docs affected: {docs_with_meta_leak}/{docs})")
    lines.append(f"False redactions (decoys removed)   : {false_red}/{decoys_total}")
    util = util_num / util_den * 100 if util_den else float("nan")
    lines.append(f"Utility (non-sensitive words kept)  : {util:.1f}%")
    lines.append(f"Placeholders inserted               : {placeholders}")
    lines.append(f"NOT TESTABLE planted values         : {len(not_testable)}  (excluded from recall)")
    report = "\n".join(lines)
    print(report)

    if not_testable:
        print("\nNot testable (value never extractable from the original file):")
        for n in not_testable[:10]:
            print("  ", n)
        if len(not_testable) > 10:
            print(f"   ... and {len(not_testable) - 10} more")

    # Filenames embed the dataset, so real -> evaluation_real_*.txt (unchanged) and
    # fresh -> evaluation_fresh_*.txt; the two sets' evidence never collide.
    out_txt = f"evaluation_{DATASET}_{VERSION}.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"Approach: {VERSION}\n{report}\n\nNot testable:\n" + "\n".join(not_testable) + "\n")
    out_csv = f"failed_cases_{DATASET}_{VERSION}.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["doc", "kind", "location", "entity_or_field", "value", "auto_note", "manual_review_note"])
        for row in failed:
            w.writerow(list(row) + [""])  # fill manual_review_note by hand (manual review of misses)
    print(f"\nSaved: {out_txt}, {out_csv}  (fill manual_review_note for each failed case)")


if __name__ == "__main__":
    main()