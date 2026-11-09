# Environment

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** The exact environment in which this
run's evidence (`results/`) and test output (`test_results.md`) were produced. Pinned versions are in
[`../requirements.txt`](../requirements.txt); the NLP model is installed separately with
`python -m spacy download en_core_web_lg`.

## Operating system & interpreter

| Item | Value |
|---|---|
| Operating system | Windows 10 Home — `Windows-10-10.0.19045-SP0` |
| Architecture | AMD64 (x86‑64) |
| Shell used | PowerShell (Git Bash also available) |
| Python | CPython **3.14.4** |

> Developed and tested on CPython 3.14; the code targets Python 3.10+.

## Python libraries actually imported by the project

*(from `pip freeze` in this run; these are the libraries the source files import.)*

| Library | Version | Used by |
|---|---|---|
| presidio-analyzer | **2.2.366** | `pipelines.py` (detectors) |
| presidio-anonymizer | **2.2.366** | `redact_real_docs.py` (`<ENTITY>` replacement) |
| spacy | **3.8.18** | NER engine behind Presidio (v2–v4) |
| en_core_web_lg (model) | **3.8.0** | spaCy English NER model |
| python-docx | **1.2.0** | DOCX read/write, comments, core properties |
| pypdf | **6.21.2** | PDF text extraction + Info‑dict metadata |
| reportlab | **5.1.0** | PDF (re)generation |
| arabic-reshaper | **3.1.0** | Arabic shaping for PDF generation |
| python-bidi | **0.6.12** | bidi reordering for Arabic PDF text |
| pytest | **9.2.0** | `tests/test_redaction.py` |

**Supporting packages** (transitive / test): `pluggy 1.7.0`, `iniconfig 2.3.1` (pytest);
`spacy-legacy 3.0.12`, `spacy-loggers 1.0.5` (spaCy).

**Installed but NOT used by the project:** `Faker 40.44.0` is present in the environment but is
**not imported anywhere** — the synthetic data is fixed/deterministic (see
`requirements.txt`). It is intentionally excluded from `requirements.txt`.

## Reproducing this environment

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows   (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python -m pytest tests/ -v             # expect: 17 passed, 1 xfailed
```

> **Determinism / caveats.** The synthetic generators and all measurement scripts are
> deterministic. The one environment‑sensitive assertion is the Arabic `xfail`
> (`test_t7c_english_ner_misses_arabic_name_xfail`), which relies on the pinned
> `en_core_web_lg==3.8.0` not tagging a bare Arabic name — a different spaCy model version could
> change that single result. All other tests and all `results/` numbers are model/locale‑independent
> given the pinned versions above.
