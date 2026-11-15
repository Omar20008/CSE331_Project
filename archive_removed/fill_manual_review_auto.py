"""
fill_manual_review_auto.py
CSE331 - Project 09: Document Redaction & Metadata Privacy

Non-interactive, batch complement to fill_manual_review.py (which is interactive and targets the
real v4 CSV only). This fills an **evidence-based factual** `manual_review_note` for every row in
every failed_cases_*.csv whose note is still empty, deriving the note ONLY from that row's own
evidence columns (kind, location, entity_or_field, value, auto_note) and the approach tag in the
file name. Rows that already have a note (e.g. the human-reviewed real v4 file) are left untouched.

It never fabricates a root cause: a note states WHAT leaked, WHERE, the identifier class, and a
severity. A row whose evidence is insufficient to classify is flagged `NEEDS HUMAN REVIEW`.

Usage:
    python fill_manual_review_auto.py                 # fill results/real/ + results/fresh/ CSVs
    python fill_manual_review_auto.py path1.csv ...   # fill specific CSV files
    python fill_manual_review_auto.py --dry-run       # report counts without writing

Prints per-file and total counts of rows filled automatically vs. already filled vs. flagged.
"""

import csv
import glob
import os
import sys

FIELDS = ["doc", "kind", "location", "entity_or_field", "value", "auto_note", "manual_review_note"]

# Full-leak severity by identifier type (direct identifiers are High; a full address is High too).
FULL_SEVERITY = {
    "US_SSN": "High", "PERSON": "High", "EMAIL_ADDRESS": "High",
    "PHONE_NUMBER": "High", "LOCATION": "High",
}


def approach_of(path):
    """failed_cases_<set>_<approach>.csv -> '<approach>' (original|meta|v1..v4)."""
    base = os.path.basename(path)
    stem = base[:-4] if base.endswith(".csv") else base
    return stem.split("_")[-1]


def tokens_from_auto(auto_note):
    note = (auto_note or "").strip()
    if note.lower().startswith("remaining tokens:"):
        return note.split(":", 1)[1].strip()
    return ""


def make_note(approach, row):
    """A short factual note derived only from this row's evidence. Returns '' if unclassifiable."""
    kind = (row.get("kind") or "").strip().upper()
    ent = (row.get("entity_or_field") or "").strip() or "value"
    loc = (row.get("location") or "").strip() or "(unspecified)"
    toks = tokens_from_auto(row.get("auto_note"))
    is_baseline = approach in ("original", "meta")

    if kind == "FALSE-REDACTION":
        return ("False redaction: non-personal decoy was removed (over-redaction). "
                "Severity: Medium (utility/precision loss). Fix: allow-list the non-personal value.")

    if kind.startswith("META"):
        full = kind.endswith("FULL")
        base = ("Metadata-only baseline leaves this field populated. " if approach == "meta" else "")
        return (f"Metadata {'full' if full else 'partial'} leak: {ent} present in field(s) {loc}. "
                f"{base}Direct identifier in document metadata. Severity: High. "
                "Fix: clear this metadata field (core props / PDF Info / comment author).")

    if kind == "TEXT-FULL":
        sev = FULL_SEVERITY.get(ent, "High")
        if approach == "original":
            return (f"Baseline (no redaction): {ent} present as planted in {loc}. "
                    "Expected leak — establishes the before-protection condition.")
        if approach == "meta":
            return (f"Metadata-only baseline (no body redaction): {ent} text value present in {loc}. "
                    "Expected text leak; this approach strips metadata only.")
        return (f"Residual FULL text leak: {ent} value survived in {loc}. "
                f"Direct identifier not removed by {approach}. Severity: {sev}. "
                "Action: extend detector coverage / remove in manual review before release.")

    if kind == "TEXT-PARTIAL":
        frag = f" Surviving fragment(s): {toks}." if toks else ""
        if is_baseline:
            return (f"Baseline: partial {ent} fragment in {loc}.{frag} Expected "
                    "(approach performs no / metadata-only redaction).")
        return (f"Residual PARTIAL leak: {ent} quasi-identifier fragment in {loc}.{frag} "
                "Low identifiability alone but linkable (re-identification). Severity: Low. "
                "Fix: generalize/suppress postcode; add locale address rule.")

    return ""  # unclassifiable -> caller flags NEEDS HUMAN REVIEW


def fill_file(path, dry_run=False):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    approach = approach_of(path)
    already = filled = flagged = 0
    for row in rows:
        for k in FIELDS:
            row.setdefault(k, "")
        if (row.get("manual_review_note") or "").strip():
            already += 1
            continue
        note = make_note(approach, row)
        if not note:
            row["manual_review_note"] = "NEEDS HUMAN REVIEW"
            flagged += 1
        else:
            row["manual_review_note"] = note
            filled += 1
    if not dry_run and (filled or flagged):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, "") for k in FIELDS})
    return len(rows), already, filled, flagged


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if args:
        paths = args
    else:
        paths = sorted(glob.glob(os.path.join("results", "real", "failed_cases_*.csv")) +
                       glob.glob(os.path.join("results", "fresh", "failed_cases_*.csv")))
    if not paths:
        print("No failed_cases_*.csv files found.")
        return

    tot_rows = tot_already = tot_filled = tot_flagged = 0
    print(f"{'file':44} {'rows':>5} {'already':>8} {'filled':>7} {'flagged':>8}")
    print("-" * 76)
    for p in paths:
        n, already, filled, flagged = fill_file(p, dry_run=dry)
        tot_rows += n; tot_already += already; tot_filled += filled; tot_flagged += flagged
        print(f"{os.path.relpath(p):44} {n:>5} {already:>8} {filled:>7} {flagged:>8}")
    print("-" * 76)
    print(f"{'TOTAL':44} {tot_rows:>5} {tot_already:>8} {tot_filled:>7} {tot_flagged:>8}")
    print(f"\nFilled automatically: {tot_filled}   Already filled (kept): {tot_already}   "
          f"Flagged NEEDS HUMAN REVIEW: {tot_flagged}" + ("   [DRY RUN]" if dry else ""))


if __name__ == "__main__":
    main()
