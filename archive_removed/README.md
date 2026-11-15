# `archive_removed/` — retired helper scripts

These scripts were part of earlier iterations but are **not needed to reproduce the
results**. They are **not imported or invoked** by `run_all_real.py`, `run_all_fresh.py`,
or the test suite. They are kept here (with full git history) rather than deleted so nothing
is lost; the project was slimmed down on 2026-11-15 to keep only what the pipeline needs.

| Script | What it did | Why retired |
|---|---|---|
| `check_metadata.py` | Quick residual-metadata spot check on `documents_real/` vs `redacted_real/meta/`. | Fully subsumed by `evaluate_real_docs.py`, which inspects every metadata part (core/app/custom docProps, PDF Info, XMP, comment-author). |
| `fill_manual_review.py` | Interactive helper to type a `manual_review_note` into `failed_cases_real_<v>.csv` by hand. | Duplicated by the non-interactive `fill_manual_review_auto.py`; the reviewed notes are already committed in `results/`. |
| `fill_manual_review_auto.py` | Batch-filled an evidence-based `manual_review_note` for every empty row in `results/*/failed_cases_*.csv`. | One-off authoring tool; it is not part of producing the headline metrics (evaluation / detection / attack). The notes it wrote are committed in `results/`. |

## Restore a script
```bash
git mv archive_removed/<name>.py <name>.py
```
The scripts still run from the repo root if copied back (they use project-root-relative paths).
