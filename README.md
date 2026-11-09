# CSE331 — Project 09: Document Redaction & Metadata Privacy

A local, **bilingual (Arabic + English), Jordan‑aware** tool that detects and removes personal
data from Office/PDF documents — in the body **and** in every place PII hides (headers, footers,
hidden text, comments, PDF annotations, and file metadata) — then measures how much protection and
utility it actually delivers, and finally **attacks its own output** to see whether a person can
still be re‑identified.

> **Privacy lab rule compliance.** All **40 documents** are **100 % synthetic**: invented names,
> reserved `example.*` e‑mail domains, fictional `555‑01xx` phone numbers, and made‑up ID numbers.
> No real person's data is used anywhere. A classroom prototype does not establish legal compliance.

---

## What makes this project distinct

Most "PII redaction with Presidio" projects stop at English body text on a few `.txt` files. This
one is deliberately different on five axes:

1. **Bilingual & Jordan‑locale detection.** Custom recognizers for Jordanian/international phone
   numbers (`+962`, `07x`, `+44`, …) and **Arabic‑script names/addresses** that the English spaCy
   model cannot see. Without these, every Arabic identifier and non‑US phone leaks.
2. **Every document surface, not just the visible page.** We redact and then *re‑inspect* body,
   tables, headers/footers, **hidden `<w:vanish>` text**, **invisible white PDF text**, **comments
   and comment‑author attributes**, **PDF annotations**, and **document metadata** (core/app/custom
   `docProps`, PDF info dict, XMP). *A black box over the page is not redaction.*
3. **Two separate, honest metrics.** Detector **precision/recall** (`detection_quality.py`) is
   reported separately from the privacy **outcome** — did any value actually survive in the released
   file (`evaluate_real_docs.py`). We state residual risk instead of claiming complete anonymity.
4. **A measured four‑stage evolution** (v1 → v4) where each stage fixes a *named* weakness of the
   previous one, including a subtle finding: paragraph‑by‑paragraph NER misses names that
   whole‑document detection catches (fixed by **document‑consistent redaction** in v4).
5. **We red‑team our own release.** `attack_real_docs.py` is an *adversary*, not a checker: it takes
   only the released file and tries to put a **name** to it by linking surviving fragments against a
   candidate directory, reporting the **anonymity‑set size k** and the **re‑identification rate**.
   It surfaces what leak counts hide — v4 shows only **3 full leaks** yet **linkage still
   re‑identifies 16/40** via surviving ZIP/postcode quasi‑identifiers — and proves *which channel*
   (metadata alone re‑identifies **38/40** of the raw files) defeats the control. This turns
   `threat_model.md` into executed evidence.

---

## Repository structure

```
CSE331_Project/
├─ README.md                     ← this file
├─ CHANGELOG.md                  ← what changed vs. the original prototype
├─ requirements.txt              ← pinned dependencies + spaCy model + Arabic shaping libs
├─ .gitignore                    ← ignores regenerated outputs (see "Reproduce everything")
│
│   ── source: detectors + pipeline ─────────────────────────────────
├─ pipelines.py                  ← the detectors: make_detector("v1".."v4") + allow-list
├─ generate_real_docs.py         ← builds 20 synthetic people → 40 DOCX/PDF + ground_truth_real.json
├─ generate_fresh_docs.py        ← builds the 20-person UNSEEN hold-out set + ground_truth_fresh.json
├─ redact_real_docs.py           ← detect → anonymize → scrub metadata  (per version, real|fresh)
├─ strip_metadata.py             ← metadata-only baseline → redacted_real/meta/{docx,pdf}/
├─ check_metadata.py             ← quick residual-metadata spot check
├─ evaluate_real_docs.py         ← residual-disclosure evaluation (the privacy OUTCOME)
├─ detection_quality.py          ← detector precision/recall (the DETECTION quality)
├─ attack_real_docs.py           ← RED TEAM: re-identification / anonymity-set attack on the release
├─ fill_manual_review.py         ← interactive helper to complete the manual review of misses
├─ run_all_real.py               ← one command: redact + baseline + evaluate + detection + attack (real)
├─ run_all_fresh.py              ← same pipeline on the unseen hold-out set (generalisation test)
│
│   ── synthetic inputs (only ground_truth_*.json is versioned) ──────
├─ documents_real/               ← INPUT: ground_truth_real.json  (+ docx/, pdf/ regenerated, git-ignored)
├─ documents_fresh/              ← INPUT: ground_truth_fresh.json (+ docx/, pdf/ regenerated, git-ignored)
│
│   ── committed evidence snapshot (see results/README.md) ───────────
├─ results/
│  ├─ real/                      ← evaluation_real_*.txt, failed_cases_real_*.csv
│  ├─ fresh/                     ← evaluation_fresh_*.txt, failed_cases_fresh_*.csv, detection_quality_fresh.txt
│  ├─ attack/                    ← attack_report_*.txt, attack_findings_*.csv  (real + fresh)
│  ├─ detection/                 ← detection_quality.txt
│  └─ README.md                  ← what each subfolder and approach tag means
│
├─ fill_manual_review_auto.py    ← batch-fill manual_review_note from row evidence (non-interactive)
├─ tests/                        ← pytest suite (test_redaction.py + conftest.py)
└─ docs/                         ← privacy-by-design & compliance documentation
   ├─ data_dictionary.md             ├─ technical_guide.md
   ├─ architecture_dataflow.md       ├─ environment.md
   ├─ threat_model.md                ├─ test_plan.md
   ├─ evidence_map.md                ├─ test_results.md
   ├─ privacy_utility_residual_risk.md
   ├─ RISK_REGISTER.md               ├─ LIMITATIONS_AND_MANUAL_REVIEW.md
   ├─ RED_TEAM_REIDENTIFICATION.md   ├─ FRESH_HOLDOUT_RESULTS.md
   ├─ LEGAL_ETHICS.md                └─ AI_USE_DECLARATION.md
```

> Re-running the pipeline recreates `documents_*/docx|pdf/`, `redacted_*/`, and the root-level
> evidence files; all of those are **git-ignored** and regenerate deterministically. The committed,
> reviewed evidence lives in [`results/`](results/).

> Naming note: `documents_real` / `redacted_real` mean *realistic office documents* (DOCX/PDF),
> as opposed to an earlier plain‑text prototype. The data itself is synthetic (see the lab‑rule box).

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

> **Arabic in PDFs (optional font).** Arabic rendering uses `arabic-reshaper` + `python-bidi` (both
> in `requirements.txt`) plus a Unicode TTF. `generate_real_docs.py` auto‑detects a system font
> (e.g. Windows `Arial`/`Segoe UI`); for the best shaping, drop `Amiri-Regular.ttf` or
> `NotoNaskhArabic-Regular.ttf` into a `fonts/` folder. If none is found it falls back to an ASCII
> approximation and prints a one‑time warning (the DOCX and PDF **metadata** paths are unaffected).

## Reproduce everything

Two orchestrators reproduce the whole project — run them in order:

```bash
python generate_real_docs.py           # (re)create the 40 synthetic documents + ground truth
python run_all_real.py                  # real set: redact v1..v4 + metadata baseline + evaluate + detection + attack
python run_all_fresh.py                 # hold-out: generate fresh docs, then redact + evaluate + detection + attack
```

Both write their **fresh outputs to the repository root**
(`evaluation_<ds>_<version>.txt`, `failed_cases_<ds>_<version>.csv`, `detection_quality*.txt`,
`attack_report_*.txt`, `attack_findings_*.csv`) plus the redacted corpora in `redacted_<ds>_*/`.
All of these are **git-ignored** and regenerate deterministically; the committed, reviewed copies
live in [`results/`](results/) (see [`results/README.md`](results/README.md)).

To run one piece (add a `fresh` argument to target the hold-out set, e.g.
`python evaluate_real_docs.py v4 fresh`):

```bash
python redact_real_docs.py v4          # produce redacted_real_v4/
python evaluate_real_docs.py v4        # residual-disclosure report for v4   (-> root; snapshot in results/real/)
python evaluate_real_docs.py original  # baseline: shows PII leaking from every surface
python detection_quality.py v4         # precision/recall for the v4 detector (-> root; snapshot in results/detection/)
python attack_real_docs.py v4          # RED TEAM: re-identification / anonymity-set attack on v4
python attack_real_docs.py original    # baseline: attacker re-identifies 40/40 from the raw files
python fill_manual_review.py           # interactively complete manual_review_note in the v4 CSV
```

---

## Results

*(20 distinct individuals × 2 formats = 40 documents; 200 planted text identifiers, 160 planted
metadata values.)* The committed evidence behind every table below is in
[`results/`](results/) — `real/`, `fresh/`, `attack/`, `detection/`.

### A. Detector quality — precision / recall on the original documents (`detection_quality.txt`)

| Detector | What it adds | Recall (micro) | Precision | Decoy wrongly flagged |
|---|---|---:|---:|---:|
| v1 | Presidio defaults | 93.5 % | 89.3 % | 40 / 40 |
| v2 | + spaCy `en_core_web_lg` | 93.5 % | 89.0 % | 40 / 40 |
| v3 | + US phone/address regex + allow‑list | 86.5 % | 99.4 % | 0 / 40 |
| **v4** | **+ Jordan/intl phone + Arabic PII + consistent redaction** | **99.0 %** | **98.6 %** | **0 / 40** |

> v3's US‑only phone regex drops **phone recall to 55 %** (it loses the international numbers
> Presidio's built‑in recognizer caught); v4 restores it to 95 % and lifts PERSON/LOCATION to 100 %.
> v3/v4 precision is below 100 % only because of a handful of non‑decoy over‑redactions — the
> **decoy** itself is never over‑redacted from v3 on (allow‑list).

### B. Privacy outcome — did any value survive the redacted file? (`evaluation_real_*.txt`)

| Approach | Full text leaks | Partial text leaks | Metadata leaks | Decoy removed | Utility kept |
|---|---:|---:|---:|---:|---:|
| original (baseline) | 200 (40/40 docs) | 0 | 200 (40/40) | 0/40 | 100 % |
| metadata‑only strip | 200 (40/40) | 0 | 34 full + 57 partial (20/40) | 0/40 | 100 % |
| v1 Presidio | 11 | 34 | 0 | **40/40** | 94.8 % |
| v2 + spaCy | 11 | 36 | 0 | **40/40** | 94.8 % |
| v3 + US regex | 25 | 28 | 0 | 0/40 | 97.0 % |
| **v4 (recommended)** | **3** | **16** | **0** | **0/40** | **97.0 %** |

**Reading the results**

- **Removing names alone is not enough, and neither is stripping core metadata.** The
  *metadata‑only* baseline still leaks on 20/40 documents because the author's name also lives in the
  **comment‑author attribute** (all DOCX) — only the full pipeline (which clears comment authors)
  reaches 0 metadata leaks.
- **v1→v2** barely moves (spaCy and the default NER miss the same hard names), but v2 is the base NER
  for the later stages.
- **v3** eliminates decoy over‑redaction (allow‑list) but *regresses* phone recall, because replacing
  Presidio's built‑in phone recognizer with a **US‑only** regex drops the many international numbers —
  so its full‑leak count actually *rises* to 25.
- **v4** restores and extends phone coverage (`+962`, `+44`, `+34`, `+49`, `+91`, `+86`, …), adds
  Arabic detection, and redacts **document‑consistently**, reaching 99 % recall with 97.0 % utility
  and just 3 residual full leaks.

### C. Re‑identification outcome — can an attacker *name* the released file? (`attack_report_*.txt`)

`attack_real_docs.py` executes the `threat_model.md` adversary: it reads only the released file,
links surviving fragments against a **20‑person** candidate directory, and reports the
**anonymity‑set size k** (`k = 1` ⇒ uniquely re‑identified). This is a privacy *outcome*, distinct
from both the detector metric (A) and the string‑survival metric (B).

| Approach | Re‑identified (k=1) | Mean anonymity k | Fully anonymous (k=N) | Metadata channel alone | Hidden/aux alone |
|---|---:|---:|---:|---:|---:|
| original (baseline) | 40/40 (100 %) | 1.0 | 0/40 | **38/40** | 20/40 |
| metadata‑only strip | 40/40 (100 %) | 1.0 | 0/40 | 19/40 | 20/40 |
| v1 | 35/40 (87.5 %) | 3.4 | 5/40 | 0/40 | 6/40 |
| v2 | 37/40 (92.5 %) | 2.4 | 3/40 | 0/40 | 6/40 |
| v3 | 31/40 (77.5 %) | 5.3 | 9/40 | 0/40 | 10/40 |
| **v4 (recommended)** | **16/40 (40 %)** | **11.5** | **22/40** | **0/40** | **1/40** |

*(N = 20 distinct individuals.)*

- **A box over the page is not redaction — measured.** On the raw files the **metadata channel alone
  re‑identifies 38/40** and hidden/aux surfaces alone 20/40, *without reading the visible page*. The
  full pipeline closes the metadata channel completely (0/40) from v1 on.
- **Leak counts understate risk.** v4 has only **3 full text leaks** but is re‑identified **16/40** —
  each via a surviving **quasi‑identifier** (ZIP/postcode `62704` / `92101` / `78765` / `200021` /
  `560001`, or a district + code like `Mecca …11953`, `Rainbow …11181`). Anonymizing a person needs
  *quasi*‑identifier control (ZIP generalization), not just name removal.
- **Honest scope:** re‑identification rate is relative to the assumed directory (synthetic identities
  mostly live in different cities, so a postcode is locally unique); the metric is comparative +
  demonstrative. Full attacker model and caveats in
  [`docs/RED_TEAM_REIDENTIFICATION.md`](docs/RED_TEAM_REIDENTIFICATION.md).

**Residual risk in v4 (fully characterized in `docs/LIMITATIONS_AND_MANUAL_REVIEW.md`):**
one borderline English name spaCy misses (`Aisha Khan`), two occurrences of a 7‑digit local number
with no area code (`555‑0123`), and 16 partial LOCATION fragments — 5‑digit ZIPs plus non‑US
postcodes/district names the US‑centric address regex does not fully cover (e.g. `Nanjing`,
`Bengaluru`, `Unter den Linden`). These are low‑identifiability on their own and are the reason
**manual review is part of the workflow** — statistical NER cannot guarantee 100 %.

---

## Copy‑and‑paste equivalence

The evaluator and the attacker never read the *rendered page* — they read the document's **extracted
text** (`pypdf` / the DOCX XML) and its metadata, which is exactly what an adversary obtains with
select‑all + copy, "Save as text", or a metadata viewer. So "no residual leak" means *the value is
absent from what copy‑paste / extraction returns*, not merely hidden behind a visual box. Invisible
white PDF text and hidden `w:vanish` runs are inspected **on purpose** because copy‑paste still
returns them. (For Arabic, the synthetic PDFs also embed a logical‑order hidden text layer so
extraction returns the real Unicode — see `generate_real_docs.py`.)

## Manual review workflow

Statistical NER cannot guarantee 100 %, so manual review is a step, not an afterthought:

1. `python evaluate_real_docs.py v4` writes every residual case to `failed_cases_real_v4.csv`
   (doc, kind, location, entity, value, an automatic note, and an empty `manual_review_note`).
2. `python fill_manual_review.py` walks each case interactively and records a human root‑cause /
   decision in `manual_review_note`; `python fill_manual_review_auto.py` is a non‑interactive batch
   complement that fills an evidence‑based factual note for every empty row and reports the counts
   (filled vs. already reviewed vs. flagged).
3. The analysis is written up in
   [`docs/LIMITATIONS_AND_MANUAL_REVIEW.md`](docs/LIMITATIONS_AND_MANUAL_REVIEW.md), which reviews all
   **3 full + 16 partial** v4 residuals and recommends the next control (ZIP/postcode generalization,
   a `P.O. Box` rule, non‑US address coverage, a name gazetteer).

---

## Technical deliverables

The technical deliverables for this milestone and where they live:

| # | Deliverable | File(s) |
|---|---|---|
| 1 | Data dictionary (entities, metadata, hidden surfaces) | [`docs/data_dictionary.md`](docs/data_dictionary.md) |
| 2 | Architecture & data‑flow (Mermaid + trust boundaries + alternatives) | [`docs/architecture_dataflow.md`](docs/architecture_dataflow.md) |
| 3 | Threat model (assets, attackers, no‑anonymity statement) | [`docs/threat_model.md`](docs/threat_model.md) |
| 4 | Test suite + plan + results | [`tests/test_redaction.py`](tests/test_redaction.py), [`docs/test_plan.md`](docs/test_plan.md), [`docs/test_results.md`](docs/test_results.md) |
| 5 | Evidence map (Requirement → Risk → Control → Test → Evidence) | [`docs/evidence_map.md`](docs/evidence_map.md) |
| 6 | Privacy / utility / residual risk (real + fresh) | [`docs/privacy_utility_residual_risk.md`](docs/privacy_utility_residual_risk.md) |
| 7 | Manual review of misses (per‑row notes) | [`fill_manual_review_auto.py`](fill_manual_review_auto.py), [`results/*/failed_cases_*.csv`](results/) |
| 8 | Technical guide + environment + pinned deps | [`docs/technical_guide.md`](docs/technical_guide.md), [`docs/environment.md`](docs/environment.md), [`requirements.txt`](requirements.txt) |

**Run the tests:**

```bash
pip install -r requirements.txt            # includes pytest
python -m spacy download en_core_web_lg
python -m pytest tests/ -v                  # expect: 17 passed, 1 xfailed  (~10 s)
```

The suite builds its own synthetic DOCX/PDF fixtures and drives the **real v4 pipeline** (see
[`docs/test_plan.md`](docs/test_plan.md)); the verbatim run is in
[`docs/test_results.md`](docs/test_results.md).

**Where evidence lives:** the committed, reviewed snapshot is [`results/`](results/) —
`real/` (residual disclosure), `fresh/` (generalisation hold‑out), `attack/` (re‑identification),
`detection/` (detector precision/recall). Re‑runs write git‑ignored copies to the repo root. The
full comparison tables are in [`docs/privacy_utility_residual_risk.md`](docs/privacy_utility_residual_risk.md).

## Documentation

| Document | Covers |
|---|---|
| [`docs/data_dictionary.md`](docs/data_dictionary.md) | Every entity/metadata/hidden surface: identification role, sensitivity, detector/control, known limitation |
| [`docs/architecture_dataflow.md`](docs/architecture_dataflow.md) | Mermaid data‑flow + trust boundaries, component table, alternatives compared (v1–v4 + overlay) |
| [`docs/threat_model.md`](docs/threat_model.md) | Assets, attacker types A1–A4, assumptions, out‑of‑scope, no‑anonymity statement, what each approach still leaks |
| [`docs/evidence_map.md`](docs/evidence_map.md) | Requirement → Risk → Control → Test → Evidence (+ legal‑reference TBD, M1‑alignment flag) |
| [`docs/privacy_utility_residual_risk.md`](docs/privacy_utility_residual_risk.md) | Real + fresh comparison tables, privacy–utility discussion, v3→v4 cycle, residual risk |
| [`docs/test_plan.md`](docs/test_plan.md) · [`docs/test_results.md`](docs/test_results.md) | Test‑case table; verbatim `pytest -v` output (17 passed, 1 xfail) + fix history |
| [`docs/technical_guide.md`](docs/technical_guide.md) · [`docs/environment.md`](docs/environment.md) | Setup/run/extend/troubleshoot; OS + pinned library versions |
| [`docs/RISK_REGISTER.md`](docs/RISK_REGISTER.md) | Ranked disclosure risks → control → test → residual |
| [`docs/LIMITATIONS_AND_MANUAL_REVIEW.md`](docs/LIMITATIONS_AND_MANUAL_REVIEW.md) | Manual review of every v4 residual miss, TLS/metadata discussion |
| [`docs/RED_TEAM_REIDENTIFICATION.md`](docs/RED_TEAM_REIDENTIFICATION.md) | The re‑identification adversary: attacker model, anonymity‑set metric, channel attribution |
| [`docs/FRESH_HOLDOUT_RESULTS.md`](docs/FRESH_HOLDOUT_RESULTS.md) | Generalisation of the v1→v4 detectors on the unseen hold‑out set |
| [`docs/LEGAL_ETHICS.md`](docs/LEGAL_ETHICS.md) | Jordan PDPL No. 24 of 2023 principles, ethics, synthetic‑data statement (team) |
| [`docs/AI_USE_DECLARATION.md`](docs/AI_USE_DECLARATION.md) | Declared AI assistance (course rule; team) |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed vs. the original prototype |

---

## AI‑use declaration (course rule)

AI assistance (Claude, via the Claude Code CLI) was used for code cleanup, the locale‑aware `v4`
detector, the precision/recall and re‑identification harnesses, and documentation; the project
concept, the synthetic‑dataset design, and the v1–v3 approach are the team's own work. Full
declaration and prompt summary in [`docs/AI_USE_DECLARATION.md`](docs/AI_USE_DECLARATION.md).
**TODO:** confirm AI use is permitted for this milestone under the instructor's policy, and that each
member can explain any AI‑assisted code or text during the oral defense.

## Contribution log

**TODO — fill in before submission.**

| Member | Role | Student ID | Main contributions |
|---|---|---|---|
| _&lt;name&gt;_ | _&lt;role&gt;_ | _&lt;id&gt;_ | _&lt;e.g. detectors / evaluation / attack / docs&gt;_ |
| _&lt;name&gt;_ | _&lt;role&gt;_ | _&lt;id&gt;_ | _&lt;…&gt;_ |
| _&lt;name&gt;_ | _&lt;role&gt;_ | _&lt;id&gt;_ | _&lt;…&gt;_ |

## Team & submission

- **Team:** _&lt;add names, roles, student IDs&gt;_
- **Instructor:** _&lt;add&gt;_
- **Course:** CSE331 Confidentiality and Information Privacy — First semester 2026–2027
- **File naming for milestone packages:** `CSE331_TeamXX_M1` … `CSE331_TeamXX_M4`
