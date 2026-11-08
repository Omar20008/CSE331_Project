# Risk Register

**Project 09 — Document Redaction & Metadata Privacy.** Disclosure risks for releasing a redacted
document, each linked to a control, the test that exercises it, and the **measured residual** from
the v4 run on the 40‑document set. Likelihood/Impact are pre‑control (Low/Med/High).

| ID | Threat (disclosure path) | Surface | L | I | Control (where) | Test / evidence | Residual after v4 |
|----|--------------------------|---------|---|---|-----------------|-----------------|-------------------|
| R1 | Person name survives in body | body | H | H | spaCy NER + document‑consistent scrub (`redact_real_docs.py`) | `evaluate_real_docs.py` PERSON recall | **1** borderline name (`Aisha Khan`, docx_02) |
| R2 | PII in document metadata (author/title/keywords/creator…) | metadata | H | H | Clear core + PDF info dict (`redact_real_docs.py`, `strip_metadata.py`) | metadata leaks = 0 (v1–v4) | **0** |
| R3 | Person name in **comment‑author attribute** | comments.xml | H | H | Clear `comment.author`/`initials` | meta‑only baseline leaks on 20/40 docs; v4 = 0 | **0** |
| R4 | PII in hidden text (`w:vanish`) / invisible white PDF text | hidden | M | H | Hidden runs redacted; full PDF text re‑extracted & rebuilt | hidden‑text leak locations | **0** names; 1 short phone |
| R5 | PII in header / footer | header/footer | M | H | Redact all header/footer variants | leak locations show 0 header/footer names | **0** |
| R6 | International / Jordanian phone not matched | body/hidden | H | H | `IntlPhoneRecognizer`, `JoPhoneRecognizer` (v4) | PHONE recall 55 %→95 % v3→v4 | **1** 7‑digit local number (×2 docs, docx_08/pdf_08) |
| R7 | Arabic‑script name/address undetected by English NER | body/metadata | H | H | `ArabicPiiRecognizer` (v4) + Arabic rendering so the value is extractable | PERSON/LOCATION incl. Arabic redacted (docx/pdf 05,10,19) | **0** (DOCX **and** PDF)¹ |
| R8 | Over‑redaction of the non‑personal decoy | body | M | M | Allow‑list `hr@company.com` (v3+) | decoy false‑redactions 40→0 | **0** decoy (precision 98.6 %)² |
| R9 | Quasi‑identifier fragment (ZIP/postcode/district) survives | body | M | M | US/locale address regex + overlap resolution | 16 partial LOCATION leaks | **16** partial (ZIP/postcode + non‑US district tokens) |
| R10 | Re‑identification by **linkage** of residual quasi‑identifiers + aux data | released file | M | H | Executed by `attack_real_docs.py`; recommend postcode suppression/generalization for real release | re‑identification rate, anonymity set | **8 identities** still unique (16/40 docs); documented |
| R11 | Utility destroyed by aggressive redaction | released file | M | M | Measure non‑sensitive words kept | utility 97.0 % (v4) | Acceptable |

¹ Arabic now renders (reshaped + bidi) **and** is embedded as a logical‑order hidden text layer, so
`pypdf` extracts the real Unicode and the Arabic value is **testable** (no longer excluded from
recall). The v4 Arabic recognizer redacts it in both DOCX and PDF, and the Arabic name is also cleared
from PDF metadata. `NOT TESTABLE` planted values = **0** in the current run.

² v3/v4 precision is 99.4 %/98.6 % (a few non‑decoy over‑redactions remain); the **decoy specifically**
is never over‑redacted from v3 on, thanks to the allow‑list (decoy false‑redactions = 0/40).

## Residual‑risk summary (v4)

- **3 full** text disclosures: 1 borderline English name (NER limit, R1) + a 7‑digit area‑code‑less
  number appearing in 2 documents (R6).
- **16 partial** disclosures: 5‑digit ZIPs and non‑US postcodes/district names (R9) — low
  identifiability individually, but the linkage attack (R10) shows **8 identities** remain uniquely
  re‑identifiable by them.
- **0** metadata disclosures, **0** decoy false‑redactions, **97.0 %** utility retained.

The non‑zero residual is deliberate evidence of the **privacy–utility trade‑off** and the reason
**manual review** (R1, R9, R10) is a required step rather than an optional one. The named next
controls are postcode generalization (e.g. ZIP3), a `P.O. Box` address rule, broader non‑US address
coverage, and an organization name gazetteer.
