# Legal & Ethical Reasoning

**Project 09 — Document Redaction & Metadata Privacy.** This project operationalizes **data
minimization**: before a document leaves the HR trust boundary, identifiers not needed for the
released purpose are removed from both content and metadata.

> **Verification caveat.** Article numbers below follow the brief's starting points for Jordan's
> **Personal Data Protection Law No. 24 of 2023** (begin with Articles 2, 4–8, 13–15, 20) and the
> MoDEE legal/guidance repository. **The exact clauses, definitions, exceptions, and any issued
> implementing instructions must be verified against the official text before relying on them.** A
> successful classroom prototype does **not** establish institutional legal compliance.

## 1. Principle → control mapping

| Data‑protection principle (as embodied by PDPL 24/2023) | How this project applies it | Control / evidence |
|---|---|---|
| **Data minimization** — process only what the purpose needs | Strip direct identifiers (name, phone, e‑mail, address, ID) from released documents | `redact_real_docs.py`; `evaluation_real_v4.txt` |
| **Purpose limitation** — use data only for the stated purpose | Released document supports non‑identifying review, not identification | Data dictionary "released purpose" |
| **Storage limitation / retention** — keep identifiable data no longer than needed | Original (identifiable) file stays inside the boundary; only the redacted copy is released; ground truth is never released | `THREAT_MODEL.md` data‑flow |
| **Integrity & confidentiality (security)** — protect against unauthorized disclosure | Reach hidden/comment/annotation/metadata channels, not just the visible page | `DATA_DICTIONARY.md` §3; leak‑location evidence |
| **Accuracy / avoid collateral harm** — do not corrupt legitimate content | Allow‑list + utility measurement prevent over‑redaction | precision 98.6 %, 0/40 decoy over‑redaction, utility 97.0 % |
| **Data‑subject rights** (access, correction, erasure) | Out of scope for this artifact, but redaction is the enabling control for lawful **disclosure/transfer**; noted as future work | `LIMITATIONS_AND_MANUAL_REVIEW.md` |

## 2. Lawful handling in this project

- **Synthetic data only.** No real data subject exists, so no lawful basis/consent is required to
  process the sample set. This is the course's *Privacy Lab Rule* and the correct posture for a
  classroom prototype.
- **Re‑identification experiments are fictional.** Residual‑risk analysis uses only the planted
  synthetic ground truth; no attempt is made to re‑identify real people.
- **No secrets or real records** are committed to the repository.

## 3. Ethical considerations

- **Honesty over hype.** We report residual leaks and a precise protection level rather than claiming
  "complete anonymity." Overstating protection is itself a privacy harm because it invites unsafe
  release decisions.
- **Dual‑use awareness.** The same detectors that redact PII could be used to *locate* PII. The tool
  is scoped to team‑owned synthetic documents and defensive use.
- **Bias / coverage.** English NER underperforms on non‑Latin scripts; we added Arabic detection
  explicitly so the tool does not silently fail on Arabic‑speaking users' data — a fairness concern,
  not only an accuracy one.

## 4. Applicability & exceptions (to verify)

Typical data‑protection regimes include exceptions (e.g., journalistic, statistical/research, or
national‑security processing) and conditions for **cross‑border transfer**. For a real deployment of
this tool, confirm against the official PDPL text and MoDEE instruments: (a) whether the released,
de‑identified document still constitutes "personal data" under the law's definition (Art. 2), (b) the
lawful basis for the original processing (Arts. 4–8), and (c) transfer conditions (Arts. 13–15, 20).
These determine whether redaction alone is sufficient or must be paired with contractual/organizational
controls.
