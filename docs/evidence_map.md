# Evidence Map — Requirement → Risk → Control → Test → Evidence

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** This is the *evidence chain*: each
requirement is linked to the disclosure risk it addresses, the control that implements it, the test
that exercises it, and the evidence file that records the result — under the **same test conditions
before and after** protection ("before" = `evaluate_real_docs.py original`; "after" = the same
script on `redacted_real_v4/`).

> **Requirement / risk IDs.** No milestone **M1** document is present in `docs/`, so the `FR‑*`,
> `NFR‑*`, and `R*` IDs below are **derived from `README.md` and `RISK_REGISTER.md`**. ⚠️ **These IDs
> must be aligned with the official M1 document before submission** (team action): if M1 numbers the
> requirements/risks differently, update this table to match M1's scheme.
>
> **Legal reference.** The `Legal reference` column is intentionally left as
> `TBD (team: Jordan PDPL mapping)`. Legal mapping (Jordan PDPL No. 24 of 2023) is owned by the team
> and documented separately in [`LEGAL_ETHICS.md`](LEGAL_ETHICS.md); no legal claim is asserted here.

All numbers are from the committed `results/real/` run (v4) — see
[`privacy_utility_residual_risk.md`](privacy_utility_residual_risk.md) for the full tables.

## 1. Requirement → Risk → Control → Test → Evidence

| Req ID | Requirement | Risk | Control (where) | Test | Evidence file | Result (v4) | Legal reference |
|---|---|---|---|---|---|---|---|
| FR‑1 | Remove person names on every surface | R1, R3, R5 | spaCy NER + document‑consistent scrub + comment‑author clear (`redact_real_docs.py`, `pipelines.py`) | PERSON recall; leak locations; `test_t1`, `test_t4` | `results/real/evaluation_real_v4.txt`; `results/detection/detection_quality.txt` | 97.5 % recall (1 residual name) | TBD (team: Jordan PDPL mapping) |
| FR‑2 | Remove phone numbers incl. Jordan/intl | R6 | `UsPhoneRecognizer` + `IntlPhoneRecognizer` + `JoPhoneRecognizer` (`pipelines.py`) | PHONE recall; `test_t6_boundary_phone_formats` | `results/real/evaluation_real_v4.txt` | 95 % (1 local 7‑digit ×2) | TBD (team: Jordan PDPL mapping) |
| FR‑3 | Remove e‑mail addresses | R1 | Presidio `EMAIL_ADDRESS` | EMAIL recall; `test_t1` | `results/real/evaluation_real_v4.txt` | 100 % | TBD (team: Jordan PDPL mapping) |
| FR‑4 | Remove postal addresses | R9, R10 | US + locale address regex + overlap resolution (`pipelines.py`) | LOCATION full/partial; `test_t6_boundary_address_formats` | `results/real/evaluation_real_v4.txt` | 0 full, 16 partial (ZIP/postcode) — **Partial by design**¹ | TBD (team: Jordan PDPL mapping) |
| FR‑5 | Remove national ID / SSN | R1 | Presidio `US_SSN` | SSN recall; `test_t1`, `test_t8` | `results/real/evaluation_real_v4.txt` | 100 % | TBD (team: Jordan PDPL mapping) |
| FR‑6 | Strip all document metadata | R2, R3 | clear DOCX core + PDF Info + comment authors (`redact_real_docs.py`, `strip_metadata.py`) | metadata leaks; `test_t3` | `results/real/evaluation_real_v4.txt` | 0 metadata leaks | TBD (team: Jordan PDPL mapping) |
| FR‑7 | Reach hidden/comment/annotation surfaces | R4 | surface‑aware redaction; PDF re‑extracted & rebuilt (`redact_real_docs.py`) | leak locations; `test_t4`, `test_t5` | `results/real/evaluation_real_v4.txt` | 0 names; 1 short phone | TBD (team: Jordan PDPL mapping) |
| FR‑8 | Preserve non‑personal content (no over‑redaction) | R8, R11 | allow‑list; measure utility (`pipelines.py`, `evaluate_real_docs.py`) | precision, decoy, utility; `test_t2`, `test_t7a` | `results/detection/detection_quality.txt`; `results/real/evaluation_real_v4.txt` | 98.6 % precision, 0/40 decoy, 97.0 % utility | TBD (team: Jordan PDPL mapping) |
| NFR‑1 | Reproducible pipeline | — | fixed/deterministic data, pinned deps (`requirements.txt`, `run_all_*.py`) | re‑run orchestrators | all `results/` files | stable outputs | TBD (team: Jordan PDPL mapping) |
| NFR‑2 | Bilingual (Arabic + English) | R7 | `ArabicPiiRecognizer` + Arabic rendering/extraction (`pipelines.py`, `generate_real_docs.py`) | Arabic detect; `test_t7c` (xfail limit + v4 fix) | `results/real/evaluation_real_v4.txt` (docx/pdf 05,10,19) | Arabic name+address redacted (DOCX & PDF) | TBD (team: Jordan PDPL mapping) |
| NFR‑3 | Measure re‑identification (not just string survival) | R10 | `attack_real_docs.py` (anonymity‑set k, linkage) | re‑identification rate | `results/attack/attack_report_v4.txt` | 100 % → 40 % re‑id; mean k 1.0 → 11.5 | TBD (team: Jordan PDPL mapping) |

¹ **FR‑4 is Partial by design:** direct address parts are removed, but a bare ZIP/postcode and some
non‑US district tokens survive as quasi‑identifiers (R9) and re‑identify by linkage (R10). The gap is
quantified and the next control (postcode generalization, non‑US address rules) is named — see
`privacy_utility_residual_risk.md` and `LIMITATIONS_AND_MANUAL_REVIEW.md`.

## 2. Risk index (derived from `RISK_REGISTER.md`)

| ID | Disclosure risk | Residual after v4 |
|---|---|---|
| R1 | Person name/email/SSN survives in body | 1 borderline name (`Aisha Khan`) |
| R2 | PII in document metadata (author/title/keywords/creator…) | 0 |
| R3 | Person name in comment‑author attribute | 0 (baseline leaks 20/40) |
| R4 | PII in hidden `w:vanish` / invisible white PDF text | 0 names; 1 short phone |
| R5 | PII in header / footer | 0 |
| R6 | International / Jordanian phone not matched | 1 local 7‑digit (×2 docs) |
| R7 | Arabic name/address undetected by English NER | 0 (v4 Arabic recognizer) |
| R8 | Over‑redaction of the non‑personal decoy | 0/40 (allow‑list) |
| R9 | Quasi‑identifier fragment (ZIP/postcode/district) survives | 16 partial |
| R10 | Re‑identification by linkage of residual quasi‑identifiers | 16/40 (8 identities) still unique |
| R11 | Utility destroyed by aggressive redaction | 97.0 % retained (acceptable) |

## 3. Required‑evidence checklist (Project‑09 brief → artifact)

| Required evidence | Test script | Output artifact | Status |
|---|---|---|---|
| ≥ 20 synthetic files w/ planted identifiers **and** metadata | `generate_real_docs.py` | `documents_real/` (40), `ground_truth_real.json` | Done |
| Local detection & redaction workflow (Presidio) | `pipelines.py` + `redact_real_docs.py` | `redacted_real_v4/` | Done |
| Inspect text, metadata, copy‑paste, hidden content | `evaluate_real_docs.py` | `results/real/evaluation_real_original.txt` (baseline leaks 40/40) | Done |
| Detection precision / recall | `detection_quality.py` | `results/detection/detection_quality.txt` (99.0 % / 98.6 %) | Done |
| Residual‑disclosure count | `evaluate_real_docs.py` | `results/real/evaluation_real_v4.txt` (3 full / 16 partial) | Done |
| False redactions / utility | allow‑list + utility metric | `results/real/evaluation_real_v4.txt` (0/40 decoy, 97.0 %) | Done |
| Re‑identification / linkage risk | `attack_real_docs.py` | `results/attack/attack_report_v4.txt` (16/40 unique) | Done |
| Manual review of misses | human analysis + CSV notes | `results/real/failed_cases_real_v4.csv` → `LIMITATIONS_AND_MANUAL_REVIEW.md` | Done |
| Automated test suite | `tests/test_redaction.py` | `test_results.md` (17 passed, 1 xfail) | Done |
| Reproducibility | `run_all_real.py` / `run_all_fresh.py` | all `results/` files | Done |
| Generalisation (unseen hold‑out) | `run_all_fresh.py` | `results/fresh/*`, `results/attack/attack_report_fresh_*` | Done |

## 4. Acceptance criteria

- [x] Baseline leaks PII from **every** surface on 40/40 documents (establishes the threat).
- [x] v4 removes **100 %** of metadata leaks and commits **0** decoy false‑redactions.
- [x] v4 detector precision **98.6 %**, recall **99.0 %**; utility **97.0 %** (≥ 95 %).
- [x] Every residual miss is listed (`failed_cases_real_v4.csv`) and reviewed with a root cause.
- [x] The release is **attacked** (`attack_real_docs.py`): re‑identification falls 100 % → 40 %.
- [x] Automated tests pass (`tests/test_redaction.py`: 17 passed, 1 documented xfail).
- [x] Same test conditions before and after protection.
- [ ] **Req/risk IDs reconciled with the official M1 document** (team, pre‑submission).
- [ ] Legal mapping completed in `LEGAL_ETHICS.md` (team: Jordan PDPL).
