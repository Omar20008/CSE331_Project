# Data Dictionary — Fields, Entities & Hidden Locations

**CSE331 Project 09 — Document Redaction & Metadata Privacy.**
Context: a synthetic university HR *"employee personal file"* (DOCX + PDF) released outside the
HR trust boundary. This dictionary lists **every field/entity the tool plants, detects, or
inspects**, with its identification role, sensitivity, the detector/control that handles it, and
its known limitation.

- **All examples are synthetic** (invented names, reserved `example.*` domains, fictional
  `555‑01xx` numbers, made‑up IDs). Source of truth for every planted value:
  [`documents_real/ground_truth_real.json`](../documents_real/ground_truth_real.json) (and
  `ground_truth_fresh.json`), produced by `generate_real_docs.py` / `generate_fresh_docs.py`.
- **Identification role** follows the course model and allows **overlapping labels**: a *direct
  identifier* names the person on its own; a *quasi‑identifier* re‑identifies by **linkage** with
  other data; a *sensitive attribute* is protected context. Sensitivity is Low / Medium / High.
- The "Detector / control" column names the exact mechanism in
  [`pipelines.py`](../pipelines.py) / [`redact_real_docs.py`](../redact_real_docs.py) (v4 unless
  stated). "Known limitation" is drawn from the measured residuals (see
  [`privacy_utility_residual_risk.md`](privacy_utility_residual_risk.md) and
  [`test_results.md`](test_results.md)).

---

## 1. Content entities (planted in the document text)

| Field / entity | Example (synthetic) | Where it appears | Identification role | Sensitivity | Detector / control (v4) | Known limitation |
|---|---|---|---|---|---|---|
| **PERSON** (full name) | `Omar Al‑Khatib`; `محمد الخطيب` | body, tables, header, footer, comments, hidden runs, metadata | Direct identifier | High | spaCy `en_core_web_lg` NER + document‑consistent scrub; Arabic via `ArabicPiiRecognizer` | Statistical NER is context‑sensitive: a borderline Latin name can be missed (`Aisha Khan` real; `Minjun Park` fresh). Arabic recognizer is a catch‑all for *any* Arabic‑script run (no name/word precision). |
| **PHONE_NUMBER** | `+962 79 555 1234`, `0795551234`, `+44 20 7946 0958` | body, hidden text, header/footer | Direct identifier (quasi in aggregate) | High | `UsPhoneRecognizer`, `IntlPhoneRecognizer`, `JoPhoneRecognizer` (regex) | A bare **7‑digit local number with no area code** (`555‑0123`) is intentionally not matched (precision protection), so it survives. |
| **EMAIL_ADDRESS** | `omar.khatib@example.jo` | body, metadata (keywords) | Direct identifier | High | Presidio `EMAIL_ADDRESS` recognizer | None material (100 % recall in both datasets); an obfuscated email (`name [at] domain`) would not match. |
| **LOCATION — street address** | `Building 15, Wasfi Al‑Tal Street, Amman 11181, Jordan` | body, hidden text | Direct if full; **quasi‑identifier** at city granularity | High | `AddressRecognizer` (US + Jordan/UK/Spain regex) + overlap resolution + spaCy GPE/LOC | Full‑address regex covers **only US + JO/UK/ES**. Other locales fall back to spaCy, which removes the city but leaves street/unit lines (partial leak). |
| **LOCATION — postal / ZIP code** | `11181`, `62704`, `200021`, `560001` | inside the address line | **Quasi‑identifier** | Medium | Removed only when the **whole** address regex matches | A **bare ZIP/postcode** survives whenever the full‑address pattern does not fire (US 4‑part, `P.O. Box`, non‑US codes). 16 such partials on real, 32 on fresh. |
| **US_SSN** (national ID) | `623‑19‑4580` | body, hidden text | Direct identifier | High (critical) | Presidio `US_SSN` recognizer | Matches the US `NNN‑NN‑NNNN` shape only; a non‑US national‑ID format would need its own recognizer. |
| **Decoy (non‑personal)** | `hr@company.com` | body | **Non‑personal** (shared org mailbox) | None | **Allow‑list** `ALLOW_LIST` (v3+) — must *survive* | Allow‑list is an exact‑string match; a different org mailbox not on the list could be over‑redacted. |
| Free‑text notes | "joined the engineering team this quarter" | body | Non‑identifying utility text | Low | — (preserved; measured as utility) | Aggressive redaction can clip adjacent words (utility ≈ 97 %). |

**Quasi‑identifier note.** Removing direct identifiers does **not** anonymize the person: the
re‑identification harness (`attack_real_docs.py`) shows that surviving ZIP/postcode + district
fragments still re‑identify **16/40** real documents by linkage. The named next control is
postcode generalization/suppression (e.g. ZIP→region), not more per‑country regexes.

---

## 2. Metadata fields (in the file, invisible on the page)

| Field | Example (synthetic) | Where it appears (DOCX / PDF) | Identification role | Sensitivity | Control (v4) | Known limitation |
|---|---|---|---|---|---|---|
| **Author / creator name** | `Omar Al‑Khatib` | DOCX `docProps/core.xml` `dc:creator` · PDF `/Author` | Direct identifier | High | `core.author=""` · PDF `add_metadata({"/Author":""})` | — (0 leaks measured) |
| **Title** | `Confidential – Omar Al‑Khatib` | core `dc:title` · PDF `/Title` | Direct identifier + sensitive context | High | `core.title=""` · `/Title":""` | — |
| **Subject** | `Employee personal file` | core `dc:subject` · PDF `/Subject` | Sensitive attribute | Medium | `core.subject=""` · `/Subject":""` | — |
| **Keywords** | `Omar Al‑Khatib, omar.khatib@example.jo` | core `cp:keywords` · PDF `/Keywords` | Direct identifier (name + email) | High | `core.keywords=""` · `/Keywords":""` | — |
| **Comments / description** | `Created for Omar Al‑Khatib` | core `dc:description` · PDF `/Subject` (n/a) | Direct identifier | High | `core.comments=""` | — |
| **Last modified by** | `Omar Al‑Khatib` | core `cp:lastModifiedBy` | Direct identifier | High | `core.last_modified_by=""` | — |
| **Creator application** | `HR System – Omar Al‑Khatib` | — · PDF `/Creator` | Direct identifier (name embedded) | High | PDF `/Creator":""` | — |
| **Producer** | `ReportLab PDF Library …` | — · PDF `/Producer` | Software fingerprint | Low | PDF `/Producer":""` | Fingerprint only; not personally identifying. |
| **Comment author / initials** | `w:author="Sara Haddad"` | DOCX `word/comments.xml` | Direct identifier | High | `comment.author=""`, `comment.initials=""` | Requires `python‑docx ≥ 1.2` comment API; the field a *metadata‑only* strip forgets (baseline leaks 20/40). |
| Custom / app `docProps` | — (AppVersion, dates) | DOCX `docProps/app.xml`, `custom.xml` | — | Low | Not individually cleared; inspected by evaluator | Boilerplate only in this dataset (0 PII leaks); a real template could place PII in a custom property that is **not** explicitly cleared. |

> **Why the metadata rows matter.** A visual overlay leaves **every** row of this table intact.
> The *metadata channel alone* re‑identifies **38/40** raw documents without reading the visible
> page — which is why metadata stripping (and comment‑author clearing) is a first‑class control.

---

## 3. Hidden / non‑visible surfaces (inspected and redacted)

| Surface | Example content (synthetic) | Where it appears (DOCX / PDF) | Role | Sensitivity | Control (v4) | Known limitation |
|---|---|---|---|---|---|---|
| **Body text & table cells** | `Phone: +962 79 555 1234` | `word/document.xml` `w:t` · PDF page text | carries any entity | High | per‑paragraph redaction + document‑consistent scrub | — |
| **Header** (all variants) | `Confidential — Omar Al‑Khatib` | `word/header*.xml` · (PDF n/a) | carries any entity | High | all header variants redacted | Text inside **text boxes / shapes** is not traversed (only paragraphs/tables). |
| **Footer** (all variants) | `Prepared by Omar Al‑Khatib` | `word/footer*.xml` · (PDF n/a) | carries any entity | High | all footer variants redacted | Same as header (shapes/text boxes). |
| **Hidden text** (`w:vanish`) | `Omar Al‑Khatib 623‑19‑4580` | `w:vanish` run · invisible **white** PDF text | carries any entity | High | hidden runs redacted; PDF fully re‑extracted & rebuilt from text | — (extraction returns it, so it is redacted on purpose). |
| **Comments (text)** | `note about Priya Raman` | `word/comments.xml` paragraphs · (PDF n/a) | carries any entity | High | comment paragraphs redacted | — |
| **PDF annotations** | `/Contents`, `/T`, `/Subj`, `/URI` | — · PDF `/Annots` | carries any entity | High | PDF is **rebuilt from extracted text**, so annotations are dropped wholesale | Rebuild discards *all* annotations (and original layout); a redaction that must preserve annotations would need a different approach. |
| **Invisible white PDF text** | `secret Michael Chen` in white | — · PDF text layer | carries any entity | High | text extracted (copy‑paste equivalent) then redacted in the rebuilt PDF | Scanned/image text (no text layer) is **not** handled — would need OCR. |

**Copy‑and‑paste equivalence.** The evaluator and attacker read the document's **extracted text**
(`pypdf` / DOCX XML) and metadata — exactly what select‑all+copy, "save as text", or a metadata
viewer returns — never the rendered page. "No residual leak" therefore means *the value is absent
from what extraction returns*, not merely hidden behind a box.
