# Privacy, Utility & Residual Risk

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** Every number below is copied from a
committed evidence file in [`results/`](../results/) (`evaluation_*.txt`, `detection_quality*.txt`,
`attack_report_*.txt`, `failed_cases_*.csv`). *Population per set: 20 distinct individuals × 2
formats = 40 documents; 200 planted text identifiers; 160 planted metadata values.*

- **real** = the 20‑person set the detectors were **built and tuned on**.
- **fresh** = a 20‑person **unseen hold‑out** (new names, phone formats, and 12+ new address
  locales). Because v4's rules were tuned on `real`, **`fresh` is the fair generalisation number.**
  (The metadata‑only baseline is `real`‑only; `strip_metadata.py` targets the real set.)

---

## 1. Residual disclosure & utility — real dataset
*Source: `results/real/evaluation_real_<approach>.txt`.*

| Approach | Full text leaks | Partial text leaks | Metadata leaks (full / partial) | False redactions (decoy removed) | Utility (non‑sensitive words kept) | Placeholders |
|---|---:|---:|---:|---:|---:|---:|
| original (baseline) | 200 | 0 | 200 / 0 | 0 / 40 | 100.0 % | 0 |
| metadata‑only strip | 200 | 0 | 34 / 57 | 0 / 40 | 100.0 % | 0 |
| v1 Presidio | 11 | 34 | 0 / 0 | **40 / 40** | 94.8 % | 171 |
| v2 + spaCy | 11 | 36 | 0 / 0 | **40 / 40** | 94.8 % | 167 |
| v3 + US regex + allow‑list | 25 | 28 | 0 / 0 | 0 / 40 | 97.0 % | 133 |
| **v4 (recommended)** | **3** | **16** | **0 / 0** | **0 / 40** | **97.0 %** | 147 |

## 2. Residual disclosure & utility — fresh hold‑out dataset
*Source: `results/fresh/evaluation_fresh_<approach>.txt`.*

| Approach | Full text leaks | Partial text leaks | Metadata leaks (full / partial) | False redactions (decoy removed) | Utility | Placeholders |
|---|---:|---:|---:|---:|---:|---:|
| original (baseline) | 200 | 0 | 200 / 0 | 0 / 40 | 100.0 % | 0 |
| v1 Presidio | 11 | 35 | 0 / 0 | **40 / 40** | 93.7 % | 193 |
| v2 + spaCy | 12 | 38 | 0 / 0 | **40 / 40** | 93.7 % | 188 |
| v3 + US regex + allow‑list | 34 | 38 | 0 / 0 | 0 / 40 | 96.4 % | 147 |
| **v4 (recommended)** | **2** | **33** | **0 / 0** | **0 / 40** | **96.4 %** | 167 |

## 3. Per‑entity residual recall (did the value survive?)
*`recall = 1 − full_leaks / testable`, from the same `evaluation_*.txt` files. 100 % = no full leak.*

**Real:**

| Entity | v1 | v2 | v3 | v4 |
|---|---:|---:|---:|---:|
| PERSON | 85.0 % | 85.0 % | 85.0 % | **97.5 %** |
| PHONE_NUMBER | 90.0 % | 90.0 % | 55.0 % | **95.0 %** |
| EMAIL_ADDRESS | 100 % | 100 % | 100 % | 100 % |
| LOCATION | 97.5 % | 97.5 % | 97.5 % | **100 %** |
| US_SSN | 100 % | 100 % | 100 % | 100 % |

**Fresh:**

| Entity | v1 | v2 | v3 | v4 |
|---|---:|---:|---:|---:|
| PERSON | 72.5 % | 70.0 % | 70.0 % | **95.0 %** |
| PHONE_NUMBER | 100 % | 100 % | 45.0 % | **100 %** |
| EMAIL_ADDRESS | 100 % | 100 % | 100 % | 100 % |
| LOCATION | 100 % | 100 % | 100 % | 100 % |
| US_SSN | 100 % | 100 % | 100 % | 100 % |

> **LOCATION "100 %" is a full‑string metric.** It only asks whether the *entire* address string
> survived — it never does, because spaCy always strips the city. The honest address signal is the
> **partial** leak count (§1–2) and re‑identification (§5): the street/unit/**postcode** survive.

## 4. Detector quality (precision / recall of the detector itself)
*Source: `results/detection/detection_quality.txt` and `results/fresh/detection_quality_fresh.txt`.
This is the detector metric (span overlap vs. ground truth), separate from residual survival above.*

| Metric | v1 | v2 | v3 | v4 |
|---|---:|---:|---:|---:|
| Recall (micro) — real | 93.5 % | 93.5 % | 86.5 % | **99.0 %** |
| Recall (micro) — fresh | 97.5 % | 96.5 % | 86.5 % | **99.0 %** |
| Precision — real | 89.3 % | 89.0 % | 99.4 % | 98.6 % |
| Precision — fresh | 90.8 % | 90.5 % | 98.2 % | 98.4 % |
| Decoy wrongly flagged — real / fresh | 40/40 | 40/40 | 0 | 0 |

## 5. Re‑identification (closed‑population linkage, N = 20)
*Source: `results/attack/attack_report_[fresh_]<approach>.txt`. k=1 ⇒ uniquely re‑identified.*

| Approach | Re‑id k=1 — real | Mean k — real | Anonymous (k=20) — real | Re‑id k=1 — fresh | Mean k — fresh | Anonymous — fresh |
|---|---:|---:|---:|---:|---:|---:|
| original | 100 % | 1.0 | 0/40 | 100 % | 1.0 | 0/40 |
| meta‑only | 100 % | 1.0 | 0/40 | — | — | — |
| v1 | 87.5 % | 3.4 | 5/40 | 85.0 % | 3.9 | 6/40 |
| v2 | 92.5 % | 2.4 | 3/40 | 90.0 % | 2.9 | 4/40 |
| v3 | 77.5 % | 5.3 | 9/40 | 92.5 % | 2.4 | 3/40 |
| **v4** | **40.0 %** | **11.5** | **22/40** | **80.0 %** | **4.8** | **8/40** |

---

## 6. Privacy–utility discussion (what each approach protects and destroys)

- **original / metadata‑only — maximum utility, no privacy.** Utility 100 %, but every value leaks.
  The metadata‑only strip proves metadata is a channel, yet still re‑identifies **40/40** because it
  forgets the **comment‑author** attribute (34 full + 57 partial metadata leaks remain).
- **v1 / v2 — automated detection, but blunt.** They cut full leaks to 11 and close the metadata
  channel, but **over‑redact the decoy 40/40** and cost ~5 points of utility (94.8 %). The extra
  placeholders (171/167) are partly *wrong* redactions.
- **v3 — precision at the cost of recall.** The allow‑list ends decoy over‑redaction (0/40) and
  lifts precision to 99.4 %, raising utility to 97.0 %. But swapping Presidio's phone recognizer for
  a **US‑only** regex drops phone recall to 55 % (real) / 45 % (fresh), so **full leaks rise to 25
  (real) / 34 (fresh)** — a clear precision‑vs‑recall regression.
- **v4 — best balance.** Locale/bilingual recognizers + document‑consistent scrubbing reach
  **3 full leaks (real)** at **97.0 % utility**, **0 metadata leaks**, **0 decoy over‑redactions**,
  and drive re‑identification from 100 % → **40 %**. Utility is preserved because redaction is
  **targeted** (147 placeholders, nearly all correct) rather than aggressive.

**The trade‑off, stated plainly:** more aggressive redaction (v1/v2) destroys utility *and* still
leaks; better *targeting* (v4) improves privacy *and* utility together — up to the point where the
remaining risk is **quasi‑identifier linkage**, which no amount of name/phone redaction removes.

## 7. Improvement cycle v3 → v4 (found → changed → retested)

**Failures found in v3** (`results/real/failed_cases_real_v3.csv`, 53 rows): the dominant class was
**PHONE full leaks — 18 of 40, recall 55 %** — every international number the US‑only regex cannot
see, e.g. `docx_00 +962 79 555 1234`, `docx_01 +44 20 7946 0958`, plus `+34/+49/+91/+86` numbers;
and **Arabic names** (`docx_05 محمد الخطيب`, `docx_10 فاطمة الزعبي`) that the English pipeline misses
entirely. Partial LOCATION leaks (bare ZIP/postcode) also persisted.

**What changed in v4** (`pipelines.py`, unchanged since): added `IntlPhoneRecognizer` +
`JoPhoneRecognizer` (international/Jordan phones), `ArabicPiiRecognizer` (Arabic‑script names/
addresses), `INTL_ADDRESS_REGEXES` (Jordan/UK/Spain), and **document‑consistent redaction**
(`CONSISTENT = True`: detect once over the whole document, then scrub every occurrence, catching a
name that paragraph‑by‑paragraph NER misses in a header/comment). Result on real: full leaks
**25 → 3**, phone recall **55 % → 95 %**, PERSON recall **85 % → 97.5 %**, re‑id **77.5 % → 40 %**.

**Retest on the untouched fresh hold‑out** (`results/fresh/`, `results/attack/attack_report_fresh_v4.txt`):

| | real v4 | fresh v4 |
|---|---:|---:|
| Full leaks | 3 | 2 |
| Partial leaks | 16 | **33** |
| Phone recall | 95.0 % | **100 %** |
| Re‑identification (k=1) | 40.0 % | **80.0 %** |
| Mean anonymity k | 11.5 | **4.8** |

> **v4 was tuned on the real set, so the fresh numbers are the fair comparison.** What **generalised**
> is **format‑based**: phones (100 % on all‑new international formats), email, SSN, Arabic, metadata
> stripping, and document‑consistent scrubbing (metadata channel re‑identifies **0/40** on fresh;
> hidden/aux just 2/40). What **did not** is the **country‑list‑based address regex**: on 12 unseen
> locales the full address never matches, so street + postcode survive (32 partial LOCATION leaks)
> and re‑identification **doubles (40 % → 80 %)**. The fix is a *generic* structured‑address
> recognizer (street‑number + line + postcode, locale‑independent) and/or a multilingual NER model —
> **not** more per‑country regexes. (Proposed, not implemented: this run only *measures*.)

## 8. Residual risk

**What still leaks after v4 (real):** 3 full + 16 partial text leaks, 0 metadata leaks
(`results/real/evaluation_real_v4.txt`, reviewed per‑row in `failed_cases_real_v4.csv` and
`LIMITATIONS_AND_MANUAL_REVIEW.md`):

| Residual | Count | Severity | Why it survives |
|---|---|---|---|
| Borderline English name (`Aisha Khan`) | 1 full | **Medium** (a full name) | spaCy NER is context‑sensitive; missed in this document's paragraph/comment layout |
| 7‑digit local phone `555‑0123` (docx_08/pdf_08) | 1 value ×2 docs | **Low** (not dialable alone) | intentionally not matched to avoid redacting unrelated 7‑digit runs (precision protection) |
| Bare ZIP / postcode / district (`62704`, `92101`, `78765`, `200021`, `560001`, `Mecca…11953`, `Rainbow…11181`, `Unter den Linden`) | 16 partial | **Low individually, but re‑identifying by linkage** | the full‑address regex does not fire on US 4‑part / `P.O. Box` / non‑US formats; spaCy removes the city but leaves the fragment |

**How bad is it?** The 16 partial location fragments are low‑identifiability on their own, but the
re‑identification harness shows they still **uniquely re‑identify 16/40 real documents (8 identities)
by linkage** — the concrete reason postcode generalization is the named next control. On the fresh
set the same class re‑identifies **32/40 (80 %)**.

**What we did NOT test / out of scope:**
- No **formal anonymization guarantee** (k‑anonymity / l‑diversity proofs); the attack *approximates*
  anonymity‑set size against an assumed 20‑person directory — comparative, not an absolute real‑world
  probability.
- **Transport / endpoint / communication‑metadata** security (TLS, sender anonymity, network
  metadata) — see `threat_model.md` §4 and `LIMITATIONS_AND_MANUAL_REVIEW.md` §4.
- **Scanned / image‑only** documents (no text layer) — would need OCR.
- **Obfuscated formats** not in the fixtures (e.g. `name [at] domain`, non‑US national‑ID shapes).
- **Faithful layout / annotation preservation** — the PDF is rebuilt from extracted text (favours
  certainty of redaction over layout fidelity; annotations are dropped wholesale).

**Named next controls:** ZIP/postcode generalization (e.g. ZIP3) or suppression, a generic
structured‑address recognizer, a `P.O. Box` rule, an organization name gazetteer, and a
**mandatory human review** step for release (statistical NER cannot guarantee 100 %).
