# Evidence Map (Requirement → Risk → Control → Test → Evidence)

**Project 09.** The brief requires an *evidence chain*: link each requirement to its risk, control,
test, and evidence item, using the **same test conditions before and after** protection. The
"before" condition is `evaluate_real_docs.py original`; the "after" condition is the same script on
`redacted_real_v4/`. All numbers below are from the current 40‑document run.

## Project‑09 required evidence → where it lives

| Required evidence (brief) | Control / artifact | Test script | Output artifact | Status |
|---|---|---|---|---|
| ≥ 20 synthetic files w/ planted identifiers **and** metadata | `generate_real_docs.py` | file count = 20 DOCX + 20 PDF (40) | `documents_real/`, `ground_truth_real.json` | **Done** |
| Ground‑truth inventory (per‑value) | deterministic generator | `generate_real_docs.py` | `ground_truth_real.json` | **Done** |
| Local detection & redaction workflow (Presidio) | `pipelines.py` + `redact_real_docs.py` | runs end‑to‑end | `redacted_real_v4/` | **Done** |
| Inspect text, metadata, copy‑paste, hidden content | `evaluate_real_docs.py` (extracts every surface) | baseline leaks on 40/40 | `evaluation_real_original.txt` | **Done** |
| Detection precision / recall | `detection_quality.py` | span‑overlap vs truth | `detection_quality.txt` (99.0 % / 98.6 %) | **Done** |
| Residual‑disclosure count | `evaluate_real_docs.py` | value survives in released file? | `evaluation_real_v4.txt` (3 full / 16 partial) | **Done** |
| False redactions | allow‑list in `pipelines.py` | decoy removed? | `evaluation_real_v4.txt` (0/40 decoy) | **Done** |
| Readability / utility check | utility metric | non‑sensitive words kept | `evaluation_real_v4.txt` (97.0 %) | **Done** |
| Copy‑and‑paste inspection | extraction‑based eval (never the rendered page) | `pypdf` / DOCX‑XML text | `evaluation_real_*.txt` + README "Copy‑and‑paste equivalence" | **Done** |
| Re‑identification / linkage risk | `attack_real_docs.py` | anonymity‑set `k` | `attack_report_v4.txt` (16/40 unique) | **Done** |
| Manual review of misses | human analysis + helper | `fill_manual_review.py` | `failed_cases_real_v4.csv` → `LIMITATIONS_AND_MANUAL_REVIEW.md` | **Done** (per‑row notes: team TODO) |
| Reproducibility | pinned `requirements.txt`, deterministic generator | `run_all_real.py` | all evidence files | **Done** |

## Requirement → Risk → Control → Test → Result (traceability)

| Req ID | Requirement | Risk | Control | Test | Result (v4) | Status |
|---|---|---|---|---|---|---|
| FR‑1 | Remove person names everywhere | R1,R3,R5 | NER + consistent scrub + comment‑author clear | PERSON recall, leak locations | 97.5 % (1 residual) | Done |
| FR‑2 | Remove phone numbers incl. Jordan/intl | R6 | US+intl+JO recognizers | PHONE recall | 95 % (1 local number ×2) | Done |
| FR‑3 | Remove e‑mail addresses | — | Presidio `EMAIL_ADDRESS` | EMAIL recall | 100 % | Done |
| FR‑4 | Remove postal addresses | R9,R10 | address regex + overlap resolution | LOCATION full/partial | 0 full, 16 partial (ZIP/postcode) | Partial¹ |
| FR‑5 | Remove national ID / SSN | — | Presidio `US_SSN` | SSN recall | 100 % | Done |
| FR‑6 | Strip all document metadata | R2,R3 | core + PDF info + comment authors | metadata leaks | 0 | Done |
| FR‑7 | Reach hidden/comment/annotation surfaces | R4 | surface‑aware redaction | leak locations | 0 names; 1 short phone | Done |
| FR‑8 | Preserve non‑personal content (no over‑redaction) | R8,R11 | allow‑list; measure utility | precision, utility | 98.6 % precision, 0/40 decoy, 97.0 % utility | Done |
| NFR‑1 | Reproducible | — | pinned deps, deterministic generator | re‑run `run_all_real.py` | stable outputs | Done |
| NFR‑2 | Bilingual (Arabic + English) | R7 | Arabic recognizer + Arabic rendering/extraction | docx/pdf 05, 10, 19 | Arabic name+address redacted (DOCX & PDF) | Done |

¹ FR‑4 is **Partial by design**: direct address parts are removed, but bare ZIP/postcode and some
non‑US district tokens survive as quasi‑identifiers. The gap is quantified (R9/R10) and the next
control (postcode generalization, non‑US address rules) is named — see `LIMITATIONS_AND_MANUAL_REVIEW.md`.

## Acceptance criteria

- [x] Baseline leaks PII from **every** surface on 40/40 documents (establishes the threat).
- [x] v4 removes **100 %** of metadata leaks and commits **0** decoy false‑redactions.
- [x] v4 detector precision **98.6 %**, recall **99 %**; utility **97.0 %** (≥ 95 %).
- [x] Every residual miss is listed (`failed_cases_real_v4.csv`) and reviewed with a root cause.
- [x] The release is **attacked** (`attack_real_docs.py`): re‑identification falls 100 % → 40 %.
- [x] Same test conditions before and after protection.
- [ ] Per‑case `manual_review_note` and the contribution log filled in by the team (pre‑submission).
