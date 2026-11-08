"""
fill_manual_review.py
CSE331 - Project 09

Interactive helper to complete the MANUAL REVIEW of residual misses required by the brief.
It reads failed_cases_real_<version>.csv (default v4), shows each failed case together with
its automatic note, prompts you for a `manual_review_note` (root cause + decision), and
writes the updated CSV back in place.

Usage:
    python fill_manual_review.py            # reviews failed_cases_real_v4.csv
    python fill_manual_review.py v3         # another detector version

Controls:
  * Enter  -> keep the current note (shown in [brackets])
  * '-'    -> clear the note
  * 'q'    -> save and quit early
It runs only in an interactive terminal and never overwrites the file on EOF/non-TTY input.
"""

import csv
import os
import sys

VERSION = sys.argv[1] if len(sys.argv) > 1 else "v4"
CSV_PATH = f"failed_cases_real_{VERSION}.csv"
FIELDS = ["doc", "kind", "location", "entity_or_field", "value",
          "auto_note", "manual_review_note"]


def main():
    if not os.path.exists(CSV_PATH):
        print(f"Not found: {CSV_PATH}  (run `python evaluate_real_docs.py {VERSION}` first)")
        sys.exit(1)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print(f"{CSV_PATH} has no failed cases — nothing to review.")
        return

    if not sys.stdin or not sys.stdin.isatty():
        print("This helper is interactive; please run it in a terminal "
              "(stdin is not a TTY). No changes written.")
        sys.exit(2)

    print(f"Manual review of {len(rows)} residual case(s) in {CSV_PATH}")
    print("Enter = keep current | '-' = clear | 'q' = save & quit\n")

    for i, row in enumerate(rows, 1):
        for k in FIELDS:                      # tolerate older/short rows
            row.setdefault(k, "")
        print("-" * 68)
        print(f"[{i}/{len(rows)}] {row['doc']}  {row['kind']}  {row['entity_or_field']}")
        print(f"      value   : {row['value']}")
        print(f"      location: {row['location']}")
        print(f"      auto    : {row['auto_note'] or '(none)'}")
        current = row.get("manual_review_note", "")
        prompt = f"      manual note [{current}]: " if current else "      manual note: "
        try:
            ans = input(prompt).strip()
        except EOFError:
            print("\nEOF received — saving progress so far.")
            break
        if ans == "q":
            break
        if ans == "-":
            row["manual_review_note"] = ""
        elif ans:
            row["manual_review_note"] = ans
        # empty input keeps the current note

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})
    print(f"\nSaved manual review notes to {CSV_PATH}.")


if __name__ == "__main__":
    main()
