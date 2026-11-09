# `results/` — committed evidence snapshot

This folder is the **stable, reviewed evidence** the milestone is graded on. The scripts still
write **fresh copies to the repository root** every time you re-run them
(`python run_all_real.py` / `python run_all_fresh.py`); those root copies are **git-ignored**
(see `../.gitignore`), so the versioned record lives here and never gets clobbered by a re-run.

Each file name encodes the **dataset** and the **approach**.

**Dataset:** `real` = the 20-person set the detectors were tuned on · `fresh` = the 20-person
**unseen hold-out** set (generalisation test; see [`../docs/FRESH_HOLDOUT_RESULTS.md`](../docs/FRESH_HOLDOUT_RESULTS.md)).

**Approach:**

| Tag | Meaning |
|-----|---------|
| `original` | raw synthetic document, no redaction (baseline) |
| `meta` | metadata-only strip (`strip_metadata.py`), no body redaction — **real set only** |
| `v1` | Presidio defaults |
| `v2` | + spaCy `en_core_web_lg` NER |
| `v3` | + US phone/address regex + allow-list |
| `v4` | + Jordan/intl phone + Arabic PII + document-consistent redaction (**recommended**) |

## `real/` — residual-disclosure evidence (real set)
- `evaluation_real_<approach>.txt` — did any planted value survive in the released file? (the privacy **outcome**)
- `failed_cases_real_<approach>.csv` — every surviving / over-redacted value, with the auto note and the `manual_review_note` column

## `fresh/` — generalisation evidence (unseen hold-out set)
- `evaluation_fresh_<approach>.txt`, `failed_cases_fresh_<approach>.csv` — the same residual-disclosure metrics on 20 people the detectors never saw
- `detection_quality_fresh.txt` — detector precision / recall on the fresh set

## `attack/` — re-identification (red-team) evidence (both sets)
- `attack_report_<approach>.txt` / `attack_report_fresh_<approach>.txt` — anonymity-set size *k* + re-identification rate per approach
- `attack_findings_<approach>.csv` / `attack_findings_fresh_<approach>.csv` — per-document *k*, attacker guess, leaking surfaces, surviving fragments

## `detection/` — detector quality (real set)
- `detection_quality.txt` — detector precision / recall per version

See the top-level [`../README.md`](../README.md) for the full results tables and
[`../docs/evidence_map.md`](../docs/evidence_map.md) for the requirement → control → evidence chain.
