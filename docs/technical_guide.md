# Technical Guide

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** How to set up, run, extend, and
troubleshoot the pipeline. Exact versions are in [`environment.md`](environment.md).

## 1. Setup

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows   (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt        # presidio, spaCy, python-docx, pypdf, reportlab, pytest, …
python -m spacy download en_core_web_lg # the NER model used by v2/v3/v4 (not on PyPI)
```

- **Python 3.10+** (developed/tested on CPython 3.14).
- **Arabic in PDFs (optional):** `arabic-reshaper` + `python-bidi` are installed by the step above;
  for best shaping, drop `Amiri-Regular.ttf` or `NotoNaskhArabic-Regular.ttf` into a `fonts/` folder.
  Without a font the generator falls back to an ASCII approximation and prints a one‑time warning
  (metadata paths are unaffected).

## 2. ⚠️ Run scripts from a terminal, with arguments

Every script takes its **detector version** and an **optional dataset** (`real` | `fresh`) from the
command line (`sys.argv`). **Do not use an IDE "Run ▶" button** that launches the file with no
arguments — you would silently get the defaults (`v3`, `real`) instead of the version you intend.
Always run from a terminal, e.g. `python redact_real_docs.py v4` or `python evaluate_real_docs.py v4 fresh`.

## 3. Folder layout

```
CSE331_Project/
├─ pipelines.py                 # the detectors: make_detector("v1".."v4") + allow-list
├─ generate_real_docs.py        # 20 synthetic people -> 40 DOCX/PDF + ground_truth_real.json
├─ generate_fresh_docs.py       # the 20-person UNSEEN hold-out set + ground_truth_fresh.json
├─ redact_real_docs.py          # detect -> anonymize -> scrub metadata (per version, real|fresh)
├─ strip_metadata.py            # metadata-only baseline -> redacted_real/meta/{docx,pdf}/
├─ check_metadata.py            # quick residual-metadata spot check
├─ evaluate_real_docs.py        # residual-disclosure evaluation (the privacy OUTCOME)
├─ detection_quality.py         # detector precision/recall (the DETECTION quality)
├─ attack_real_docs.py          # RED TEAM: re-identification / anonymity-set attack
├─ fill_manual_review.py        # interactive helper: fill manual_review_note (real v4 by default)
├─ fill_manual_review_auto.py   # non-interactive batch: fill notes from row evidence + report counts
├─ run_all_real.py / run_all_fresh.py   # orchestrators (whole chain)
├─ documents_real/ documents_fresh/     # INPUT: ground_truth_*.json (+ docx/, pdf/ regenerated)
├─ results/                     # committed evidence snapshot (real/ fresh/ attack/ detection/)
├─ tests/                       # pytest suite (test_redaction.py + conftest.py)
└─ docs/                        # this guide + the privacy-by-design docs
```

> Re‑running regenerates `documents_*/docx|pdf/`, `redacted_*/`, and the **root‑level** evidence
> files (`evaluation_*.txt`, `failed_cases_*.csv`, `detection_quality*.txt`, `attack_*.{txt,csv}`);
> all of those are **git‑ignored**. The committed, reviewed snapshot is in `results/`.

## 4. Running each piece

```bash
# 1) (re)generate the synthetic corpora + ground truth
python generate_real_docs.py
python generate_fresh_docs.py

# 2) redact (produces redacted_<set>_<version>/)
python redact_real_docs.py v4            # real set, v4 (recommended)
python redact_real_docs.py v4 fresh      # hold-out set, v4
python strip_metadata.py                 # metadata-only baseline (real set only)

# 3) evaluate residual disclosure (-> evaluation_<set>_<version>.txt + failed_cases_*.csv)
python evaluate_real_docs.py original     # baseline: PII leaks from every surface
python evaluate_real_docs.py v4           # recommended pipeline
python evaluate_real_docs.py v4 fresh     # on the unseen hold-out
python evaluate_real_docs.py meta         # metadata-only baseline

# 4) detector precision / recall (-> detection_quality[_fresh].txt)
python detection_quality.py               # all versions, real
python detection_quality.py v4 fresh      # one version, hold-out

# 5) RED TEAM re-identification (-> attack_report_*.txt + attack_findings_*.csv)
python attack_real_docs.py original       # attacker wins 40/40 on raw files
python attack_real_docs.py v4             # recommended pipeline
python attack_real_docs.py v4 fresh       # on the unseen hold-out

# 6) manual review of residual misses
python fill_manual_review.py              # interactive, real v4 CSV
python fill_manual_review_auto.py         # batch-fill empty notes in every results CSV (+counts)
python fill_manual_review_auto.py --dry-run

# 7) tests
python -m pytest tests/ -v                # 17 passed, 1 xfailed
```

**Orchestrators** (reproduce everything in order):

```bash
python run_all_real.py     # redact v1..v4 + meta baseline + evaluate + detection + attack (real)
python run_all_fresh.py    # generate fresh, then redact + evaluate + detection + attack (hold-out)
```

## 5. How detectors are selected

All detectors live in [`pipelines.py`](../pipelines.py) as `make_detector("v1".."v4")`, each a
function `text -> list[RecognizerResult]`:

| Version | Composition |
|---|---|
| v1 | Presidio `AnalyzerEngine()` defaults |
| v2 | Presidio + spaCy `en_core_web_lg` |
| v3 | v2 + US phone/address regex + overlap resolution + allow‑list (`hr@company.com`) |
| v4 | v3 + Jordan/international phones + Arabic‑script recognizer + Jordan/UK/Spain addresses (**recommended**) |

`redact_real_docs.py`, `evaluate_real_docs.py`, `detection_quality.py`, and `attack_real_docs.py`
each parse `sys.argv` for the version (`v1`..`v4`, or `original`/`meta` for the evaluators/attacker)
and an optional `real`/`fresh` dataset keyword, then call `make_detector(version)`. Only `v4` enables
**document‑consistent** scrubbing (`CONSISTENT = VERSION == "v4"` in `redact_real_docs.py`).

## 6. Adding a new entity or regex

1. **New regex recognizer (same entity type)** — in `pipelines.py`, add the pattern constant and
   register it inside `_add_custom_recognizers(...)` with `PatternRecognizer(supported_entity=…,
   name=…, patterns=[Pattern(name, REGEX, score)])`. Put locale‑specific rules behind the
   `locale_aware` flag so they belong to **v4** only (keeps v3 as the US‑only comparison point).
   For phones, add the recognizer name to `PHONE_KEEP` so `detect()` trusts it (the built‑in phone
   recognizer is otherwise filtered out).
2. **A brand‑new entity type** — add it to `ENTITIES` in `pipelines.py`; make the generator plant it
   (and record it in `ground_truth_*.json`); add any always‑generic words to `GENERIC` in
   `evaluate_real_docs.py` so they are not counted as quasi‑identifiers; confirm the anonymizer
   replaces it (Presidio maps the entity to `<ENTITY>` automatically).
3. **Allow‑listing a non‑personal value** — add the exact string to `ALLOW_LIST` in `pipelines.py`
   (and as a `decoy` in the ground truth so false‑redaction is measured).
4. Re‑run `detection_quality.py` and `evaluate_real_docs.py` to see the effect, and add/extend a
   `tests/test_redaction.py` case.

## 7. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `OSError: [E050] Can't find model 'en_core_web_lg'` | Run `python -m spacy download en_core_web_lg`. |
| `ValueError: unknown version '-v'` on import | A script was launched with no/odd args (e.g. an IDE run button passed a flag). Run from a terminal with a valid version, e.g. `python redact_real_docs.py v4`. |
| `TypeError: Cannot use WindowsPath(...) as a filename` (reportlab) | Pass a **string** path to `canvas.Canvas(...)`, not a `pathlib.Path` (already handled in the pipeline/tests). |
| Arabic shows as `?` / "no Arabic font" warning | Drop `Amiri-Regular.ttf` or `NotoNaskhArabic-Regular.ttf` into `fonts/`; the DOCX/metadata paths still work without it. |
| Arabic prints crash in a console (`cp1252 codec`) | A Windows console encoding issue only; set `PYTHONIOENCODING=utf-8`. File I/O uses UTF‑8 and is unaffected. |
| `ModuleNotFoundError: No module named 'pytest'` | `pip install -r requirements.txt` (pytest is pinned there). |
| `fill_manual_review.py` prints "interactive … stdin is not a TTY" | It is interactive by design; use `fill_manual_review_auto.py` for non‑interactive batch filling. |
| Root‑level outputs reappear after a run | Expected — they are git‑ignored; the committed snapshot is `results/`. |
