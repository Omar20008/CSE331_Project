# Changelog

All notable changes to this project. Dates are ISO‑8601. "Original version" = the first working
prototype (10 synthetic individuals, English‑plus‑one‑Arabic, detectors v1–v4, residual‑disclosure
evaluation). This changelog summarizes what was added on top of it.

## [2.2] — 2026‑11‑09 — Technical deliverables (docs, tests, manual review)

### Added
- **Automated test suite** `tests/test_redaction.py` (+ `tests/conftest.py`): 10 named tests
  (18 cases) that build their own synthetic DOCX/PDF fixtures and drive the **real v4 pipeline**
  (`redact_real_docs` + `evaluate_real_docs` + `pipelines`). Covers text removal, allow‑list,
  DOCX/PDF metadata + comment‑author clearing, hidden/white‑text surfaces, copy‑paste/extraction
  equivalence, boundary phone/address formats, no‑false‑redaction, empty‑input robustness, an
  Arabic/English‑NER limitation (`xfail`, strict), and a before/after evaluator check. **Result:
  17 passed, 1 xfailed** (`docs/test_results.md`).
- **New deliverable docs:** `docs/privacy_utility_residual_risk.md` (real + fresh comparison tables,
  privacy–utility discussion, v3→v4 cycle, residual risk), `docs/test_plan.md`, `docs/test_results.md`,
  `docs/technical_guide.md`, `docs/environment.md`.
- **Batch manual‑review helper** `fill_manual_review_auto.py`: non‑interactive complement to
  `fill_manual_review.py`; writes an evidence‑based factual `manual_review_note` for every empty row
  in all `failed_cases_*.csv`. Run: **1599 rows filled**, 19 already human‑reviewed (real v4, kept),
  **0 flagged** `NEEDS HUMAN REVIEW`.

### Changed
- **Privacy‑by‑design docs rewritten to the technical‑deliverable spec and renamed to the requested
  lowercase names** (history preserved via `git mv`): `DATA_DICTIONARY.md → data_dictionary.md`,
  `ARCHITECTURE.md → architecture_dataflow.md`, `THREAT_MODEL.md → threat_model.md`,
  `EVIDENCE_MAP.md → evidence_map.md`. In‑scope cross‑references updated (README, `results/README.md`,
  `RED_TEAM_REIDENTIFICATION.md`). *(Two backtick‑prose mentions remain in the team‑owned, out‑of‑scope
  `LEGAL_ETHICS.md`; flagged for the team — they are not links.)*
- **`requirements.txt`** pins `pytest==9.2.0` and documents that Faker is intentionally **not** a
  dependency (data is fixed/deterministic; no `import faker` anywhere).
- **README** gains a "Technical deliverables" section (each deliverable → file, how to run tests,
  where evidence lives) and an updated documentation index.

### Notes
- No production pipeline code changed. Every number in the new docs traces to a committed
  `results/` file or to the `pytest`/command output from this run. No milestone **M1** document is
  present, so the requirement/risk IDs in `evidence_map.md` are derived from README/`RISK_REGISTER.md`
  and flagged for M1 alignment; the legal‑reference column is `TBD (team: Jordan PDPL mapping)`.
  `mmdc` (Mermaid CLI) is not installed, so no PNG export of the data‑flow is committed (GitHub
  renders the Mermaid inline).

## [2.1] — 2026‑11‑09 — Repository cleanup & `results/` layout

### Changed
- **Evidence reorganized into `results/`** with four subfolders — `real/`, `fresh/`, `attack/`,
  `detection/` — plus a `results/README.md` mapping each subfolder and approach tag (`original`,
  `meta`, `v1`–`v4`) to its files. The 46 evaluation / failed‑cases / detection‑quality / attack
  files moved out of the repo root with `git mv` (version history preserved). **No script paths
  changed:** the scripts still write fresh copies to the root on re‑run; `results/` is the committed
  snapshot.
- **`.gitignore`** now ignores the regenerated root‑level outputs (`/evaluation_*.txt`,
  `/failed_cases_*.csv`, `/attack_report_*.txt`, `/attack_findings_*.csv`, `/detection_quality*.txt` —
  anchored with a leading `/` so the `results/` snapshot stays tracked) and broadens the redacted‑output
  rule to `redacted_*/` + `holdout_redacted_*/`.
- **README** structure tree and "Reproduce everything" section updated for the `results/` layout and the
  hold‑out commands (`run_all_fresh.py`, `generate_fresh_docs.py`), including where regenerated vs.
  committed outputs live.

### Notes
- Nothing was removed from version control. Generated working‑directory folders (`__pycache__/`,
  `redacted_*/`) are untracked and regenerate with `run_all_*.py`. No duplicate or junk files were
  found. `requirements.txt` verified complete (no `faker` — it appears only in a source comment).

## [2.0] — 2026‑11‑08 — Population, bilingual PDFs, red‑team, and docs

### Added
- **Population doubled to 20 distinct synthetic individuals → 40 documents** (20 DOCX + 20 PDF),
  comfortably above the brief's "≥ 20 synthetic files". New identities span Arabic, English,
  Spanish, Chinese, South‑Asian, and European names with Jordanian/UK/US/Spain/EU/Asia addresses
  and varied phone formats (`+962`, `07x`, `+44`, `+34`, `+49`, `+91`, `+86`, `+1`). Three
  individuals use **Arabic script with Arabic addresses**. (`generate_real_docs.py`)
- **Arabic rendering in PDFs.** PDFs now register a Unicode TTF (auto‑detects
  `fonts/Amiri-Regular.ttf`, `fonts/NotoNaskhArabic-Regular.ttf`, or a system Arial/Segoe UI),
  reshape with `arabic-reshaper`, and apply the bidi algorithm, with a graceful ASCII fallback +
  one‑time warning if no font/libs are present. A hidden logical‑order Arabic text layer keeps the
  Arabic value **extractable and testable** (the visible shaped line is presentation‑form only).
  Result: Arabic persons are no longer "not testable" — `NOT TESTABLE` planted values dropped to **0**.
- **Adversarial re‑identification harness** `attack_real_docs.py` (added previously, now reported on
  all approaches by `run_all_real.py`): computes the **anonymity‑set size k** and
  **re‑identification rate** per document and attributes the win to a channel. New doc
  `docs/RED_TEAM_REIDENTIFICATION.md`.
- **Manual‑review helper** `fill_manual_review.py`: interactively fills `manual_review_note` for each
  residual case in `failed_cases_real_<version>.csv`.
- **New documentation:** this `CHANGELOG.md` and `docs/ARCHITECTURE.md` (Mermaid data‑flow + trust
  boundaries). README expanded with contribution log, AI‑use, copy‑and‑paste equivalence, and a
  manual‑review workflow section.
- **Pinned dependencies** `arabic-reshaper==3.1.0`, `python-bidi==0.6.12` in `requirements.txt`.

### Changed
- **Metadata‑only baseline layout** now mirrors the versioned outputs:
  `redacted_real/meta/{docx,pdf}/` (was flat `redacted_real/`). Readers updated to match
  (`evaluate_real_docs.py`, `attack_real_docs.py`, `check_metadata.py` — one‑line path each).
- All evidence files and every number in the README/`docs/` were **regenerated** for the 40‑document
  set so the project stays internally consistent.

### Fixed
- **Re‑identification `k = 0` artifact.** Expanding the population surfaced two synthetic‑data
  cross‑linkages that made a document's own owner inconsistent with its leaked fragments: a city/name
  clash ("San **Diego**" vs a person "Diego") and a postcode (`200001`) whose `0000` matched the
  `14.0000` AppVersion boilerplate in every DOCX's `app.xml`. Resolved in the **data** (person renamed
  to "Mateo Hernández"; postcode changed to `200021`), leaving the attack logic untouched. Anonymity
  sets are now always ≥ 1.

### Headline results (40 documents, detector v4 vs. baseline)
- Detection: recall **99.0 %**, precision **98.6 %**, 0 decoy false‑redactions.
- Disclosure: **3** residual full text leaks, **0** metadata leaks (from 200 on the raw files), 97.0 % utility.
- Re‑identification: **40 %** (down from 100 % on raw files); mean anonymity **k = 11.5**; 22/40 fully anonymous.
