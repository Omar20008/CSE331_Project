# CSE331 — Project 09: Document Redaction & Metadata Privacy

A local, **bilingual (Arabic + English), Jordan‑aware** tool that detects and removes personal data
from Office/PDF documents — in the body **and** everywhere PII hides (headers, footers, hidden text,
comments, PDF annotations, file metadata) — then measures the protection and utility it delivers, and
finally **attacks its own output** to test whether a person can still be re‑identified.

> **Privacy lab rule.** All **40 documents** are **100 % synthetic** (invented names, reserved
> `example.*` e‑mail domains, fictional `555‑01xx` phones, made‑up IDs). No real personal data is used
> anywhere. A classroom prototype does not establish legal compliance.

## What makes it distinct

1. **Bilingual & Jordan‑locale detection** — Arabic‑script names/addresses and `+962` / `07x` / intl
   phones the English spaCy model cannot see.
2. **Every surface, not just the visible page** — body, tables, headers/footers, hidden `w:vanish`
   text, invisible white PDF text, comments **and comment‑author attributes**, PDF annotations, and
   all metadata (core/app/custom `docProps`, PDF info dict, XMP).
3. **Two honest metrics** — detector precision/recall (`detection_quality.py`) reported separately
   from the privacy outcome: did a value actually survive the released file (`evaluate_real_docs.py`).
4. **A measured v1 → v4 evolution** — each stage fixes a *named* weakness (v4 adds document‑consistent
   redaction).
5. **We red‑team our own release** — `attack_real_docs.py` links surviving fragments against a
   candidate directory and reports the **anonymity‑set size *k*** and re‑identification rate. v4 shows
   only **3 full leaks** yet linkage still re‑identifies **16/40** via surviving ZIP/postcode
   quasi‑identifiers (metadata alone re‑identifies **38/40** of the *raw* files).

## Repository structure

```
CSE331_Project/
├─ pipelines.py              ← the detectors: make_detector("v1".."v4") + allow-list
├─ generate_real_docs.py     ← 20 synthetic people → 40 DOCX/PDF + ground_truth_real.json
├─ generate_fresh_docs.py    ← the 20-person UNSEEN hold-out set + ground_truth_fresh.json
├─ redact_real_docs.py       ← detect → anonymize → scrub metadata (per version, real|fresh)
├─ strip_metadata.py         ← metadata-only baseline (comparison point)
├─ evaluate_real_docs.py     ← residual-disclosure evaluation (the privacy OUTCOME)
├─ detection_quality.py      ← detector precision/recall (the DETECTION quality)
├─ attack_real_docs.py       ← RED TEAM: re-identification / anonymity-set attack
├─ run_all_real.py / run_all_fresh.py   ← orchestrators (reproduce everything)
├─ documents_real/ documents_fresh/     ← INPUT: ground_truth_*.json (+ docx/,pdf/ regenerated, git-ignored)
├─ results/{real,fresh,attack,detection}/   ← committed evidence snapshot (see results/README.md)
├─ tests/                    ← pytest suite (test_redaction.py + conftest.py)
├─ docs/                     ← privacy-by-design & compliance docs (see table below)
├─ deliverables/             ← packaged M1/M2 documents + bilingual slide decks
└─ archive_removed/          ← retired helper scripts (kept for history, not used by the pipeline)
```

> Re‑running regenerates `documents_*/docx|pdf/`, `redacted_*/`, and the root‑level evidence files —
> all **git‑ignored** and deterministic. The committed, reviewed evidence lives in
> [`results/`](results/).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

> **Arabic in PDFs (optional).** Uses `arabic-reshaper` + `python-bidi` (in `requirements.txt`) plus a
> Unicode TTF; `generate_real_docs.py` auto‑detects a system font (Arial/Segoe UI) and falls back to
> an ASCII approximation with a one‑time warning if none is found.

## Reproduce everything

```bash
python generate_real_docs.py    # (re)create the 40 synthetic documents + ground truth
python run_all_real.py          # real set: redact v1..v4 + meta baseline + evaluate + detection + attack
python run_all_fresh.py         # hold-out: generate fresh docs, then redact + evaluate + detection + attack
```

Both write fresh outputs to the repo **root** (git‑ignored, deterministic); the committed copies live
in [`results/`](results/). Run one piece by passing a version (and optional `fresh`), e.g.
`python evaluate_real_docs.py v4`, `python attack_real_docs.py v4 fresh`,
`python attack_real_docs.py original` (baseline — the attacker re‑identifies 40/40).

> On Windows, set `PYTHONIOENCODING=utf-8` if you redirect output to a file, or the attack step's
> Arabic `print()` can raise a cp1252 `UnicodeEncodeError` (file outputs are UTF‑8 regardless).

## Results

*(20 individuals × 2 formats = 40 documents; 200 planted text identifiers, 160 planted metadata
values.)* Evidence behind every table is in [`results/`](results/).

### A. Detector quality — precision / recall on the originals (`detection_quality.txt`)

| Detector | What it adds | Recall | Precision | Decoy wrongly flagged |
|---|---|---:|---:|---:|
| v1 | Presidio defaults | 93.5 % | 89.3 % | 40 / 40 |
| v2 | + spaCy `en_core_web_lg` | 93.5 % | 89.0 % | 40 / 40 |
| v3 | + US phone/address regex + allow‑list | 86.5 % | 99.4 % | 0 / 40 |
| **v4** | **+ Jordan/intl phone + Arabic PII + consistent redaction** | **99.0 %** | **98.6 %** | **0 / 40** |

> v3's US‑only phone regex drops phone recall to 55 %; v4 restores it and lifts PERSON/LOCATION to
> 100 %. The decoy is never over‑redacted from v3 on (allow‑list).

### B. Privacy outcome — did any value survive the redacted file? (`evaluation_real_*.txt`)

| Approach | Full leaks | Partial leaks | Metadata leaks | Decoy removed | Utility |
|---|---:|---:|---:|---:|---:|
| original (baseline) | 200 (40/40) | 0 | 200 (40/40) | 0/40 | 100 % |
| metadata‑only strip | 200 (40/40) | 0 | 34 full + 57 partial (20/40) | 0/40 | 100 % |
| v1 Presidio | 11 | 34 | 0 | **40/40** | 94.8 % |
| v2 + spaCy | 11 | 36 | 0 | **40/40** | 94.8 % |
| v3 + US regex | 25 | 28 | 0 | 0/40 | 97.0 % |
| **v4 (recommended)** | **3** | **16** | **0** | **0/40** | **97.0 %** |

> Stripping core metadata is not enough: the metadata‑only baseline still leaks on 20/40 docs via the
> **comment‑author attribute** — only the full pipeline reaches 0 metadata leaks. v4 reaches 99 %
> recall with 97 % utility and just 3 residual full leaks.

### C. Re‑identification — can an attacker *name* the released file? (`attack_report_*.txt`)

`attack_real_docs.py` reads only the released file, links surviving fragments against a **20‑person**
directory, and reports the anonymity‑set size *k* (`k = 1` ⇒ uniquely re‑identified).

| Approach | Re‑identified (k=1) | Mean k | Fully anonymous | Metadata alone | Hidden/aux alone |
|---|---:|---:|---:|---:|---:|
| original (baseline) | 40/40 (100 %) | 1.0 | 0/40 | **38/40** | 20/40 |
| v1 | 35/40 (87.5 %) | 3.4 | 5/40 | 0/40 | 6/40 |
| v2 | 37/40 (92.5 %) | 2.4 | 3/40 | 0/40 | 6/40 |
| v3 | 31/40 (77.5 %) | 5.3 | 9/40 | 0/40 | 10/40 |
| **v4 (recommended)** | **16/40 (40 %)** | **11.5** | **22/40** | **0/40** | **1/40** |

> **A box over the page is not redaction — measured.** On raw files the metadata channel alone
> re‑identifies 38/40, *without the visible page*. Leak counts understate risk: v4 has 3 full leaks but
> is re‑identified 16/40 via surviving quasi‑identifiers (ZIP/postcode), so anonymizing needs
> quasi‑identifier control (ZIP generalization), not just name removal. The re‑id rate is relative to
> the assumed directory — comparative and demonstrative. On the unseen fresh hold‑out, detection still
> hits 99 % and 0 metadata leaks, but re‑identification doubles to 80 % because the country‑specific
> address regexes do not generalize (see `docs/FRESH_HOLDOUT_RESULTS.md`).

**What copy‑paste equivalence means.** The evaluator/attacker read the document's *extracted* text
(`pypdf` / DOCX XML) and metadata — exactly what select‑all+copy, "save as text", or a metadata viewer
returns — not the rendered page. Invisible white PDF text and hidden `w:vanish` runs are inspected on
purpose because copy‑paste still returns them. **Manual review** of every residual miss (3 full + 16
partial on v4) is written up in
[`docs/LIMITATIONS_AND_MANUAL_REVIEW.md`](docs/LIMITATIONS_AND_MANUAL_REVIEW.md), with the per‑row notes
committed in [`results/`](results/).

## Deliverables & documentation

| Deliverable / doc | File(s) | Covers |
|---|---|---|
| Data dictionary | [`docs/data_dictionary.md`](docs/data_dictionary.md) | Every entity/metadata/hidden surface: role, sensitivity, control, limitation |
| Architecture & data‑flow | [`docs/architecture_dataflow.md`](docs/architecture_dataflow.md) | Mermaid flow + trust boundaries, components, alternatives (v1–v4) |
| Threat model | [`docs/threat_model.md`](docs/threat_model.md) | Assets, attackers A1–A4, assumptions, out‑of‑scope, no‑anonymity statement |
| Evidence map | [`docs/evidence_map.md`](docs/evidence_map.md) | Requirement → Risk → Control → Test → Evidence |
| Risk register | [`docs/RISK_REGISTER.md`](docs/RISK_REGISTER.md) | Ranked disclosure risks → control → test → residual |
| Privacy/utility/residual risk | [`docs/privacy_utility_residual_risk.md`](docs/privacy_utility_residual_risk.md) | Real + fresh comparison tables, privacy–utility discussion |
| Limitations & manual review | [`docs/LIMITATIONS_AND_MANUAL_REVIEW.md`](docs/LIMITATIONS_AND_MANUAL_REVIEW.md) | Every v4 residual miss, root‑caused |
| Re‑identification write‑up | [`docs/RED_TEAM_REIDENTIFICATION.md`](docs/RED_TEAM_REIDENTIFICATION.md) | Attacker model, anonymity‑set metric, channel attribution |
| Fresh hold‑out results | [`docs/FRESH_HOLDOUT_RESULTS.md`](docs/FRESH_HOLDOUT_RESULTS.md) | Generalisation of v1→v4 on unseen people/locales |
| Tests (suite + plan + results) | [`tests/`](tests/), [`docs/test_plan.md`](docs/test_plan.md), [`docs/test_results.md`](docs/test_results.md) | Test‑case table + verbatim `pytest -v` (17 passed, 1 xfail) |
| Technical guide + environment | [`docs/technical_guide.md`](docs/technical_guide.md), [`docs/environment.md`](docs/environment.md) | Setup/run/extend/troubleshoot; OS + pinned versions |
| Legal / ethics (team) | [`docs/LEGAL_ETHICS.md`](docs/LEGAL_ETHICS.md) | Jordan PDPL No. 24 of 2023 principles, synthetic‑data statement |
| AI‑use declaration (team) | [`docs/AI_USE_DECLARATION.md`](docs/AI_USE_DECLARATION.md) | Declared AI assistance (tool, purpose, prompt summary) |
| Milestone packages | [`deliverables/`](deliverables/) | Bilingual M1/M2 documents + slide decks |

**Run the tests:** `python -m pytest tests/ -v` → **17 passed, 1 xfailed** (~10 s). The suite builds
its own synthetic fixtures and drives the real v4 pipeline.

## AI‑use, team & submission

AI assistance (Claude, via the Claude Code CLI) was used for code cleanup, the locale‑aware `v4`
detector, the precision/recall + re‑identification harnesses, and documentation; the project concept,
synthetic‑dataset design, and the v1–v3 approach are the team's own work (full declaration:
[`docs/AI_USE_DECLARATION.md`](docs/AI_USE_DECLARATION.md)). **TODO:** confirm AI use is permitted and
that each member can explain any AI‑assisted work in the oral defense.

**TODO before submission — team‑owned fields:** member names, roles, student IDs, instructor, and the
contribution log; rename `CSE331_TeamXX_*` to your real team number.

- **Course:** CSE331 Confidentiality and Information Privacy — First semester 2026–2027
- **Milestone packages:** `CSE331_TeamXX_M1` … `CSE331_TeamXX_M4`
