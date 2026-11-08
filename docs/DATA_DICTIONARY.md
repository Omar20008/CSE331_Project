# Data Dictionary & Identification / Sensitivity Labels

**Project 09 — Document Redaction & Metadata Privacy.** Context: a synthetic university "employee
personal file" released outside the HR trust boundary. Labels follow the course objective:
*classify direct identifiers, quasi‑identifiers, and sensitive attributes in a stated context;
overlapping labels are allowed.*

All values below are **synthetic** (see README lab‑rule box) and cover **20 distinct individuals →
40 DOCX/PDF documents**, diverse across Arabic/English/Spanish/Chinese/South‑Asian/European names and
Jordan/UK/US/Spain/EU/Asia addresses. Source of truth for every planted value:
[`documents_real/ground_truth_real.json`](../documents_real/ground_truth_real.json), produced by
[`generate_real_docs.py`](../generate_real_docs.py).

## 1. Content fields (planted in the document text)

| Field | Example (synthetic) | Identification role | Sensitivity | Presidio entity | Redact? |
|---|---|---|---|---|---|
| Full name | `Omar Al‑Khatib`, `محمد الخطيب` | Direct identifier | High | `PERSON` | Yes |
| Phone | `+962 79 555 1234`, `0795551234`, `+44 20 7946 0958` | Direct identifier (quasi in aggregate) | High | `PHONE_NUMBER` | Yes |
| E‑mail | `omar.khatib@example.jo` | Direct identifier | High | `EMAIL_ADDRESS` | Yes |
| Address | `Building 15, Wasfi Al‑Tal Street, Amman 11181, Jordan` | Direct if full; **quasi‑identifier** at city/ZIP granularity | High | `LOCATION` | Yes |
| National ID / SSN | `623‑19‑4580` | Direct identifier | **Critical** | `US_SSN` | Yes |
| HR contact (decoy) | `hr@company.com` | **Non‑personal** (organizational mailbox) | None | — (allow‑listed) | **No — must survive** |
| Free‑text notes | "joined the company recently…" | Non‑identifying utility text | Low | — | No |

**Quasi‑identifier note.** City + ZIP + employer context can re‑identify by *linkage* even after
direct identifiers are removed. v4 redacts full addresses, but bare ZIP/postcode fragments and some
non‑US district names can remain (see residual risk); `attack_real_docs.py` shows these re‑identify
**8 / 20 identities** by linkage — the reason postcode generalization is the named next control. The
decoy exists specifically to measure **false redactions** (over‑redaction).

## 2. Metadata fields (planted in the file, invisible on the page)

| Field | DOCX location | PDF location | Carries | Sensitivity |
|---|---|---|---|---|
| Author | `docProps/core.xml` `dc:creator` | `/Author` | Person name | High |
| Title | core `dc:title` ("Confidential – &lt;name&gt;") | `/Title` | Person name | High |
| Subject | core `dc:subject` ("Employee personal file") | `/Subject` | Sensitive context | Medium |
| Keywords | core `cp:keywords` (name, e‑mail) | `/Keywords` | Name + e‑mail | High |
| Comments/Description | core `dc:description` ("Created for &lt;name&gt;") | — | Person name | High |
| Creator app | — | `/Creator` ("HR System – &lt;name&gt;") | Person name | High |
| Producer | — | `/Producer` | Software fingerprint | Low |
| Last modified by | core `cp:lastModifiedBy` | — | Person name | High |
| **Comment author / initials** | `word/comments.xml` `w:author`, `w:initials` | — | Person name | High |

> The comment‑author attribute is the field a *metadata‑only* strip forgets — which is why the
> baseline in the results table still leaks, and the full pipeline does not.

## 3. Surfaces where PII hides (all inspected by the evaluator)

| Surface | DOCX | PDF | Extracted by |
|---|---|---|---|
| Body text & table cells | `word/document.xml` `w:t` | page text | `python-docx` / `pypdf` |
| Header / footer (all variants) | `word/header*.xml`, `footer*.xml` | — | zip XML scan |
| Hidden text | `w:vanish` runs | invisible **white** text | hidden‑run regex / text extraction |
| Comments | `word/comments.xml` (text + author) | — | zip XML scan |
| Annotations | — | `/Annots` `/Contents`,`/T`,`/Subj`,`/URI` | `pypdf` |
| File metadata | core/app/custom `docProps` | info dict + XMP | `python-docx` / `pypdf` |

A visual overlay would leave every row of this table intact — which is why the brief says a visual
overlay alone is insufficient, and why the evaluator reads **copy‑paste / extraction output**, not
the rendered page. Arabic PDF values are embedded both as shaped (visible) text **and** as a
logical‑order hidden text layer, so copy‑paste/extraction returns the real Unicode and the
Arabic‑script person is testable (not silently dropped).
