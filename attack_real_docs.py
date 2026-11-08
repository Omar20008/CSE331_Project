"""
attack_real_docs.py
CSE331 - Project 09   --   ADVERSARIAL RE-IDENTIFICATION HARNESS (red team)

Most "PII redaction" projects stop at a detector question: *did a planted string survive?*
This script asks the question an attacker actually asks: *given only the RELEASED file, can I
put a NAME to it?*  It turns docs/THREAT_MODEL.md from prose into runnable, measured evidence.

For every released document it:
  1. reads EVERY surface the way an adversary would -- not just the visible page, but hidden
     <w:vanish> runs, comments + comment-author attributes, footnotes/endnotes, headers/
     footers, PDF annotations, and ALL metadata (docProps core/app/custom, PDF info dict, XMP);
  2. recovers "linkable" fragments that still leak -- surviving name tokens (Arabic too),
     phone / SSN digit runs, ZIP / postcode, e-mail tokens -- ignoring generic address words;
  3. links them against a known population (the "HR directory" the attacker is assumed to
     hold = the distinct identities in ground_truth_real.json) and computes the ANONYMITY SET:
     how many people in that population are STILL consistent with everything that leaked.
         anonymity-set size  k == 1   =>   the person is UNIQUELY RE-IDENTIFIED.

Why this matters (and what the leak-count table cannot show):
  * A document can score "0 full leaks" and still be re-identified, because surviving
    QUASI-identifiers (a 7-digit local number, a ZIP, a postcode) link to exactly one row.
    k-anonymity is a stronger, more honest privacy outcome than "no exact string remained."
  * It attributes the win to a CHANNEL.  On the raw files, metadata or hidden surfaces
    re-identify the person on their own -- proving "a black box over the page is not redaction."

Threat model (stated so the numbers are honest):
  * Closed-population linkage: the attacker holds the directory of candidate individuals and
    only needs to match a released file to a row.
  * Conservative fragment recovery (separate digit runs >= 4, alpha tokens >= 4, generic
    address words dropped).  A stronger attacker could only do better, so a reported k is an
    UPPER BOUND on anonymity -- this harness never understates the risk.

Usage (from the project folder):
    python attack_real_docs.py v4         # attack redacted_real_v4/      (default)
    python attack_real_docs.py original   # attack the raw documents  (attacker should win 20/20)
    python attack_real_docs.py meta       # attack the metadata-only baseline
    python attack_real_docs.py v1         # ...any detector version

Writes attack_report_<version>.txt and attack_findings_<version>.csv
"""

import csv
import json
import os
import re
import sys

# Reuse the EXACT same all-surface extractor the evaluator uses, so the attacker is proven to
# read nothing the evaluator didn't also measure (no "privileged" attacker).
from evaluate_real_docs import extract, GENERIC, PLACEHOLDER, TOKEN

# ---------------------------------------------------------------- CLI: version + dataset
# Accept the detector version and an OPTIONAL dataset keyword ("real" | "fresh") in any
# order:  `python attack_real_docs.py v4`  attacks the real set (default), while
# `python attack_real_docs.py v4 fresh`  attacks the unseen documents_fresh/ hold-out and
# writes attack_report_fresh_*.txt, leaving the real-set reports intact. The population the
# attacker links against is always the one in the matching ground_truth_<dataset>.json.
_args = sys.argv[1:]
DATASET = "real"
_positional = []
for _a in _args:
    if _a in ("real", "fresh"):
        DATASET = _a
    else:
        _positional.append(_a)
VERSION = _positional[0] if _positional else "v4"

ORIG_ROOT = f"documents_{DATASET}"                       # documents_real | documents_fresh
TRUTH_FILE = os.path.join(ORIG_ROOT, f"ground_truth_{DATASET}.json")

if VERSION == "original":
    ROOT = ORIG_ROOT
elif VERSION == "meta":
    ROOT = f"redacted_{DATASET}"
else:
    ROOT = f"redacted_{DATASET}_{VERSION}"

# Which surfaces belong to which disclosure CHANNEL (the project's "every surface" thesis).
CHANNELS = {
    "metadata": {"metadata"},
    "hidden/aux surfaces": {"hidden_text", "comments", "footnotes", "endnotes",
                            "header", "footer", "annotations"},
    "visible body": {"body"},
}
DIGITS = re.compile(r"\d{4,}")        # a recovered numeric fragment (phone/SSN/ZIP piece)


def released_path(doc_id, doc_type):
    if VERSION == "original":
        return os.path.join(ORIG_ROOT, doc_type, f"{doc_id}.{doc_type}")
    if VERSION == "meta":
        return os.path.join(ROOT, "meta", doc_type, f"{doc_id}.{doc_type}")
    return os.path.join(ROOT, doc_type, f"{doc_id}.{doc_type}")


# ------------------------------------------------------------------ the population (aux knowledge)
def build_population(truth):
    """Distinct candidate individuals the attacker is assumed to know (deduped by name).
    Each record keeps a lowercase text blob (for alpha fragments) and the full digit string of
    every field separately (so a numeric fragment is tested as a substring of ONE real field,
    never across a boundary)."""
    pop = {}
    for info in truth.values():
        name = info["planted_text"].get("PERSON", "").strip()
        if not name:
            continue
        rec = pop.setdefault(name, {"name": name, "text": "", "digits": []})
        for value in info["planted_text"].values():
            rec["text"] += " " + value.lower()
            d = re.sub(r"\D", "", value)
            if d:
                rec["digits"].append(d)
    return list(pop.values())


# ------------------------------------------------------------------ fragment recovery + linkage
def fragments(text, pop):
    """From one surface's text, recover (alpha_tokens, digit_runs) that are LINKABLE -- i.e.
    actually match some population record (boilerplate that matches nobody is discarded, exactly
    as a real attacker would discard non-discriminating noise)."""
    clean = PLACEHOLDER.sub(" ", text)
    alphas = {t.lower() for t in TOKEN.findall(clean)
              if len(t) >= 4 and not t.isdigit() and t.lower() not in GENERIC}
    digruns = set(DIGITS.findall(clean))
    al = {a for a in alphas if any(a in r["text"] for r in pop)}
    dl = {d for d in digruns if any(d in fld for r in pop for fld in r["digits"])}
    return al, dl


def anonymity_set(alpha, digit, pop):
    """Population records still consistent with every recovered fragment.
    Nothing linkable recovered  =>  the whole population is consistent (fully anonymous)."""
    if not alpha and not digit:
        return list(pop)
    out = []
    for r in pop:
        if all(a in r["text"] for a in alpha) and \
           all(any(d in fld for fld in r["digits"]) for d in digit):
            out.append(r)
    return out


# ------------------------------------------------------------------ main
def main():
    with open(TRUTH_FILE, encoding="utf-8") as f:
        truth = json.load(f)
    pop = build_population(truth)
    N = len(pop)

    print("=" * 70)
    print(f"RE-IDENTIFICATION ATTACK   target: {VERSION}   folder: {ROOT}/")
    print(f"Population (attacker's directory): {N} distinct individuals")
    print("=" * 70)

    reident = pseudo = anon = 0
    false_accusation = 0
    kset = []
    chan_hits = {c: 0 for c in CHANNELS}
    rows = []

    for doc_id, info in sorted(truth.items()):
        dtype = info["type"]
        path = released_path(doc_id, dtype)
        if not os.path.exists(path):
            print(f"  MISSING: {path}")
            continue

        parts, meta = extract(path, dtype)
        surfaces = {}
        for loc, txt in parts.items():
            s = loc.split(":")[0]
            surfaces[s] = surfaces.get(s, "") + "\n" + (txt or "")
        surfaces["metadata"] = "\n".join(str(v) for v in meta.values())

        # fragments per surface, then the union across all surfaces
        surf_frag = {s: fragments(t, pop) for s, t in surfaces.items()}
        AL = set().union(*(f[0] for f in surf_frag.values())) if surf_frag else set()
        DL = set().union(*(f[1] for f in surf_frag.values())) if surf_frag else set()

        aset = anonymity_set(AL, DL, pop)
        k = len(aset)
        kset.append(k)
        truth_name = info["planted_text"].get("PERSON", "").strip()

        if k == 1:
            reident += 1
            guess = aset[0]["name"]
            if guess != truth_name:       # cannot happen in a closed population, but verified
                false_accusation += 1
            verdict = f"RE-IDENTIFIED  k=1  -> {guess}"
        elif k < N:
            pseudo += 1
            verdict = f"narrowed        k={k}/{N}"
        else:
            anon += 1
            verdict = f"anonymous       k={k}/{N}"

        # which CHANNEL could do it alone?
        leaking_surfaces = []
        chans_alone = set()
        for s, (sa, sd) in surf_frag.items():
            if not sa and not sd:
                continue
            leaking_surfaces.append(s)
            if len(anonymity_set(sa, sd, pop)) == 1:
                for c, members in CHANNELS.items():
                    if s in members:
                        chans_alone.add(c)
        for c in chans_alone:
            chan_hits[c] += 1

        print(f"  {doc_id:10} {verdict:38} via: {', '.join(sorted(leaking_surfaces)) or 'nothing'}")

        rows.append([
            doc_id, dtype, truth_name,
            "YES" if k == 1 else "no", k, N,
            aset[0]["name"] if k == 1 else "",
            ";".join(sorted(leaking_surfaces)),
            ";".join(sorted(chans_alone)),
            ";".join(sorted(AL | DL)),
        ])

    # ------------------------------------------------------------------ report
    docs = len(kset)
    mean_k = sum(kset) / docs if docs else float("nan")
    lines = []
    lines.append("-" * 70)
    lines.append(f"Documents attacked                      : {docs}")
    lines.append(f"UNIQUELY RE-IDENTIFIED (k=1)            : {reident}/{docs}"
                 f"   ({reident / docs * 100:.1f}% re-identification rate)" if docs else "")
    lines.append(f"Narrowed but not unique (2<=k<{N})       : {pseudo}/{docs}")
    lines.append(f"Fully anonymous (k={N}, nothing linkable) : {anon}/{docs}")
    lines.append(f"Anonymity-set size k  (higher = safer)  : min={min(kset)}  mean={mean_k:.1f}  max={max(kset)}"
                 if kset else "")
    lines.append(f"False accusations (unique guess wrong)  : {false_accusation}  "
                 f"(0 expected: a unique hit is always correct in a closed population)")
    lines.append("-" * 70)
    lines.append("Re-identification achievable by ONE channel alone:")
    for c in CHANNELS:
        lines.append(f"  {c:22}: {chan_hits[c]}/{docs}")
    lines.append("-" * 70)
    lines.append("Reading: on the raw files the metadata and hidden/aux channels re-identify the")
    lines.append("person WITHOUT the visible page -- a box over the text is not redaction. A low")
    lines.append("re-identification rate on a redacted set is the real privacy win; any residual")
    lines.append("k=1 is a surviving quasi-identifier that linkage recovers even with 0 full leaks.")
    report = "\n".join(l for l in lines if l != "")
    print(report)

    # real -> attack_report_<version>.* (unchanged); fresh -> attack_report_fresh_<version>.*
    _tag = "" if DATASET == "real" else f"{DATASET}_"
    out_txt = f"attack_report_{_tag}{VERSION}.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"Adversarial re-identification attack   target: {VERSION}\n")
        f.write(f"Population: {N} distinct individuals (attacker's assumed directory)\n")
        f.write(report + "\n")
    out_csv = f"attack_findings_{_tag}{VERSION}.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["doc", "type", "true_identity", "reidentified", "anonymity_set_k",
                    "population_N", "attacker_guess", "leaking_surfaces",
                    "channels_sufficient_alone", "recovered_fragments"])
        w.writerows(rows)
    print(f"\nSaved: {out_txt}, {out_csv}")


if __name__ == "__main__":
    main()
