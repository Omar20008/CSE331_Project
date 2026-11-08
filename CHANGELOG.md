# Changelog

All notable changes to this project. Dates are ISO‑8601. "Original version" = the first working
prototype (10 synthetic individuals, English‑plus‑one‑Arabic, detectors v1–v4, residual‑disclosure
evaluation). This changelog summarizes what was added on top of it.

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
