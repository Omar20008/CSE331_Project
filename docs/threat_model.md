# Threat Model

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** Scope: releasing a synthetic HR
*"employee personal file"* (DOCX/PDF) outside the organization while preserving its useful,
non‑identifying content. This model names the assets, the attacker types and what each knows/can
do, the assumptions, what is out of scope, and — using the **executed** re‑identification results —
exactly **what an attacker still learns after each approach**.

> **No anonymity guarantee.** This tool **reduces and measures** content and document‑metadata
> disclosure. It does **not** guarantee complete anonymity: even the recommended v4 output leaves
> residual quasi‑identifiers that re‑identify **16/40** real documents by linkage (§5). Redaction
> here is a strong, measured control — not a proof of anonymization.

---

## 1. Assets to protect

| Asset | Why it matters |
|---|---|
| **Direct identifiers** — name, phone, email, national ID (SSN) | Name the individual outright. |
| **Quasi‑identifiers** — street address, ZIP/postcode, district, employer context | Re‑identify by **linkage** with external data even after direct identifiers are gone. |
| **Sensitive context** — document subject ("Employee personal file"), the fact a file concerns a person | Discloses the relationship/category even without a name. |
| **Hidden‑surface copies** — the same PII in headers/footers, hidden `w:vanish` / white text, comments (+ author), annotations, metadata | Each is an independent disclosure channel that a visible‑page redaction misses. |
| **Utility of the document** | Over‑redaction destroys the document's legitimate value (a competing goal). |

Out of band (protected by *other* controls, not this tool): the original file, the ground truth,
the internal network, and the transport channel.

## 2. Attacker types — knowledge & capability

| # | Attacker | Knows / holds | Can do | Modelled by |
|---|---|---|---|---|
| **A1** | **Reader of the redacted file** | the released DOCX/PDF + standard tooling | open it, read the visible page | baseline of `evaluate_real_docs.py` |
| **A2** | **Text extractor / copy‑paster** | A1 + `pypdf` / `python‑docx` / "save as text" | select‑all+copy, extract the **text layer** incl. hidden `w:vanish` and invisible **white** PDF text | `evaluate_real_docs.py` (reads extracted text, never the rendered page) |
| **A3** | **Metadata / hidden‑content inspector** | A1 + a metadata viewer / zip tool | read core/app/custom `docProps`, PDF Info dict, XMP, **comment‑author** attributes, headers/footers, annotations | `evaluate_real_docs.py` + `check_metadata.py` (all metadata parts) |
| **A4** | **Linkage adversary with partial knowledge** | A1–A3 + an **auxiliary directory** of candidate individuals (an "HR directory") | link surviving fragments (name tokens, phone/SSN digit runs, ZIP/postcode) to a directory row → put a **name** to the file | `attack_real_docs.py` (anonymity‑set size *k*; closed‑population linkage) |

The verifier/attacker is given **no privileged access**: it reads exactly the surfaces A2/A3 can,
and A4's auxiliary knowledge is an explicit, stated 20‑person directory.

## 3. Assumptions

- The adversary has the **complete released file** and standard open‑source tooling.
- The adversary can read **every non‑visible channel** (hidden text, white text, comments,
  annotations, all metadata) — a visual overlay does not stop them.
- The linkage adversary (A4) holds a candidate directory and matches on surviving **quasi‑identifiers**.
  Fragment recovery is **conservative** (digit runs ≥ 4 taken separately, alpha tokens ≥ 4, generic
  address words dropped), so a stronger attacker could only do better — the reported *k* is an
  **upper bound on anonymity** (the harness never understates risk).
- Synthetic data is fixed/deterministic; results are reproducible under the pinned environment.

## 4. Out of scope

- **Transport & endpoint security.** TLS, sender/recipient anonymity, network metadata (who sent
  what, when), and the endpoint devices. Redaction protects *content*, not *transmission*
  (see [`LEGAL_ETHICS.md`](LEGAL_ETHICS.md) / `LIMITATIONS_AND_MANUAL_REVIEW.md`).
- **Access to the original, the ground truth, or the internal network.**
- **Side channels** (file size, timing) and **cryptographic attacks**.
- **Scanned / image‑only documents** (no text layer) — would need OCR.
- **Formal anonymization guarantees** (k‑anonymity / l‑diversity *proofs*); the attack metric
  *approximates* anonymity‑set size but does not certify it.

## 5. What the attacker still learns after each approach (executed)

From `attack_report_*.txt` (real set, population **N = 20** distinct individuals, 40 documents). *k=1*
⇒ uniquely re‑identified; "channel alone" = that surface re‑identifies **without** the visible page.

| Approach | Re‑identified (k=1) | Mean k | Fully anonymous (k=N) | Metadata **alone** | Hidden/aux **alone** | What the attacker still learns |
|---|---:|---:|---:|---:|---:|---|
| original (raw) | 40/40 (100 %) | 1.0 | 0/40 | **38/40** | 20/40 | Everything — name, contacts, ID, address — on every surface. |
| metadata‑only strip | 40/40 (100 %) | 1.0 | 0/40 | 19/40 | 20/40 | Body is untouched; and the **comment‑author** name still re‑identifies 19/40 via metadata alone. |
| v1 Presidio | 35/40 (87.5 %) | 3.4 | 5/40 | 0/40 | 6/40 | Metadata channel closed, but missed names/addresses in the body still identify most people. |
| v2 + spaCy | 37/40 (92.5 %) | 2.4 | 3/40 | 0/40 | 6/40 | Same class as v1 (the hard names persist). |
| v3 + US regex | 31/40 (77.5 %) | 5.3 | 9/40 | 0/40 | 10/40 | Removes more names/addresses, but its **US‑only phone** regex leaves international numbers. |
| **v4 (recommended)** | **16/40 (40 %)** | **11.5** | **22/40** | **0/40** | **1/40** | Only **surviving quasi‑identifiers**: a bare ZIP/postcode (`62704`, `92101`, `78765`, `200021`, `560001`) or a district+code (`Mecca …11953`, `Rainbow …11181`), each linking to one directory row. |

**Key readings.**
- **"A box over the page is not redaction," proven.** On raw files the **metadata channel alone**
  re‑identifies 38/40 and **hidden/aux alone** 20/40 — without reading the visible page. The full
  pipeline closes the metadata channel completely (0/40) from v1 on; the metadata‑*only* strip does
  not (19/40), because the author also hides in the comment‑author attribute.
- **Removing names ≠ anonymizing people.** v4 leaves only **3 full text leaks** yet linkage still
  re‑identifies **16/40**, every one via a surviving **quasi‑identifier**. This is the boundary
  between *redaction* (this project) and formal *anonymization* (ZIP generalization, group‑size
  thresholds — future work).
- **Generalisation caveat.** On the unseen **fresh** hold‑out, v4 re‑identification rises to
  **80 %** (`attack_report_fresh_v4.txt`) because the country‑list address regexes do not cover the
  new locales — see `FRESH_HOLDOUT_RESULTS.md`. The honest comparison is the fresh set.

## 6. Limitations (stated honestly)

1. **English NER cannot see Arabic.** v1/v2/v3 miss Arabic‑script names; v4 adds a catch‑all Arabic
   recognizer, which in turn cannot tell an Arabic name from an ordinary Arabic word (precision cost).
2. **Rules are tied to the document template / locale.** Full‑address detection is
   **country‑list‑based** (US + Jordan/UK/Spain); unseen locales fall back to spaCy, which leaves
   street/unit/postcode fragments (32 partial leaks on the fresh set).
3. **Postal/ZIP codes survive as fragments.** A bare ZIP/postcode is not removed unless the whole
   address matches — a weak quasi‑identifier individually, but **re‑identifying by linkage**.
4. **Statistical NER is not a guarantee.** A borderline name can be missed in short, structured
   records (`Aisha Khan` real; `Minjun Park` fresh) — the reason **manual review is a required step**.
5. **Formats not seen in tests** (obfuscated emails, non‑US national‑ID shapes, 7‑digit local phones
   with no area code, scanned images) are out of current coverage and documented as gaps, not hidden.
6. **Re‑identification rate is relative to the assumed 20‑person directory** — comparative and
   demonstrative, not an absolute real‑world probability (see `RED_TEAM_REIDENTIFICATION.md`).

## 7. Relationship to the executed harness

`attack_real_docs.py` is the **executable form of attacker A4**: same surfaces as the evaluator, an
explicit candidate directory as auxiliary knowledge, conservative fragment recovery, and a reported
anonymity‑set size *k*. It turns this threat model from prose into measured evidence
(`attack_report_*.txt`, `attack_findings_*.csv`).
