# AI Use Declaration

Course rule (CSE331 PBL guide, §09): *"Use AI only where permitted and declare the tool, purpose, and
prompt summary. Cite reused material and be ready to explain your work."*

> **Action required by the team:** confirm AI assistance is permitted for this milestone under your
> instructor's policy, then keep/trim this declaration accordingly. Every team member must be able to
> explain any AI‑assisted code or text during the individual oral defense.

## Declaration

| Item | Detail |
|---|---|
| **Tool** | Claude (Anthropic) via the Claude Code CLI |
| **Where used** | Code refactor/cleanup; the `v4` locale‑aware detector; the precision/recall script; the **re‑identification attack harness** (`attack_real_docs.py`); the **20‑individual population expansion + Arabic PDF rendering**; the metadata‑baseline path refactor and manual‑review helper; and the documentation in `docs/` and `README.md` |
| **Not AI‑generated** | The original project concept, the synthetic dataset design, and the v1–v3 pipeline approach were the team's own work |

## Purpose & prompt summary

- **Review & cleanup:** check the project against the Project‑09 brief; remove an abandoned
  plain‑text prototype and duplicate scripts; fix a Windows console encoding crash.
- **Detector improvement:** add Jordanian/international phone recognizers, an Arabic‑script PII
  recognizer, and **document‑consistent** DOCX redaction (`v4`), keeping v1–v3 for comparison.
- **Measurement:** add `detection_quality.py` (precision/recall) separate from the residual‑disclosure
  evaluation; add `attack_real_docs.py` (adversarial re‑identification / anonymity‑set `k`); regenerate
  all evidence files for the 40‑document set.
- **Dataset:** expand to 20 distinct synthetic individuals (40 documents); add Arabic PDF rendering
  (reshaper + bidi + Unicode font) with a logical hidden text layer so Arabic is testable; keep all
  data synthetic.
- **Documentation:** architecture (Mermaid), data dictionary, threat model, risk register, evidence
  map, legal/ethics notes, the re‑identification write‑up, this manual‑review/limitations analysis,
  and the changelog.

## Reused material / libraries (cite in the report)

- Microsoft **Presidio** (analyzer/anonymizer) and **spaCy** `en_core_web_lg` for detection.
- `python-docx`, `pypdf`, `reportlab` for document I/O.
- Jordan **Personal Data Protection Law No. 24 of 2023** and the MoDEE repository for legal mapping
  (verify exact clauses against the official text — see `LEGAL_ETHICS.md`).
