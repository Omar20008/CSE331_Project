# Fresh Hold-out Results — generalisation of the v1→v4 detectors

**What this is.** A second, independent test set the detectors have **never seen**. The
v1→v4 pipeline was *built and tuned* against the 20 people in `documents_real/`. Reporting
only on that set measures how well we fit our own data. This document measures the **same,
unchanged** detectors (`pipelines.py` is byte-for-byte untouched) on **20 brand-new
synthetic people** with **new names, new phone formats, and five+ new address/postcode
locales** (Egypt, Turkey, Brazil, Japan, Canada, Mexico, Italy, Nigeria, South Korea,
Netherlands, Sweden, Argentina, UAE, Jordan). That is the honest *generalisation* number.

**How to reproduce (nothing is overwritten on the real set):**

```
python generate_fresh_docs.py          # 20 people -> documents_fresh/ + ground_truth_fresh.json
python run_all_fresh.py                # redact v1..v4, then evaluate / detection_quality / attack
```

Every measurement script now takes an optional `real | fresh` keyword (default `real`), so
`python evaluate_real_docs.py v4 fresh`, `python detection_quality.py fresh`,
`python attack_real_docs.py v4 fresh`, etc. The detector code is identical for both sets.

Evidence files: `evaluation_fresh_*.txt`, `failed_cases_fresh_*.csv`,
`detection_quality_fresh.txt`, `attack_report_fresh_*.txt`, `attack_findings_fresh_*.csv`.

---

## 1. Side-by-side: old (real) set vs fresh set, v1–v4

**Detector quality** (`detection_quality*.txt`, micro over all entities):

| metric | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Recall — real | 93.5% | 93.5% | 86.5% | **99.0%** |
| Recall — fresh | 97.5% | 96.5% | 86.5% | **99.0%** |
| Precision — real | 89.3% | 89.0% | 99.4% | 98.6% |
| Precision — fresh | 90.8% | 90.5% | 98.2% | 98.4% |
| Decoy wrongly redacted — real | 40/40 | 40/40 | 0 | 0 |
| Decoy wrongly redacted — fresh | 40/40 | 40/40 | 0 | 0 |

**Residual disclosure** (`evaluation_*.txt`, after redaction) and **utility**:

| metric | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Residual **full** leaks — real | 11 | 11 | 25 | **3** |
| Residual **full** leaks — fresh | 11 | 12 | 34 | **2** |
| Residual **partial** leaks — real | 34 | 36 | 28 | 16 |
| Residual **partial** leaks — fresh | 35 | 38 | 38 | **33** |
| Utility (non-sensitive words kept) — real | 94.8% | 94.8% | 97.0% | 97.0% |
| Utility — fresh | 93.7% | 93.7% | 96.4% | 96.4% |
| Metadata leaks — real & fresh | 0 | 0 | 0 | 0 |

**Re-identification** (`attack_report_*.txt`, closed-population linkage, N = 20 people):

| metric | original | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|
| Re-identified k=1 — real | 100% | 87.5% | 92.5% | 77.5% | **40.0%** |
| Re-identified k=1 — fresh | 100% | 85.0% | 90.0% | 92.5% | **80.0%** |
| Mean anonymity set k — real | 1.0 | 3.4 | 2.4 | 5.3 | **11.5** |
| Mean anonymity set k — fresh | 1.0 | 3.9 | 2.9 | 2.4 | **4.8** |

**Per-entity detector recall, v4 (the recommended detector):**

| entity | PERSON | PHONE | EMAIL | LOCATION | US_SSN |
|---|---|---|---|---|---|
| real v4 | 100% | 95.0% | 100% | 100% | 100% |
| fresh v4 | 95.0% | 100% | 100% | 100% | 100% |

---

## 2. What generalised, and what did not

**Held up on unseen data (good):**

- **Phones.** v4 caught **100%** of the new international formats (`+20 +90 +55 +81 +52 +39
  +234 +82 +31 +46 +54 +971`, a local `078…`, and both extension styles `… ext. 118` and
  `… x4021`). 0 full and 0 partial phone leaks. The international / Jordan regexes are
  format-based, not country-list-based, so they travel.
- **Email, SSN:** 100% recall, 0 leaks (standard formats).
- **Metadata:** 0 metadata leaks on every redacted version — core-property / PDF-info
  stripping is generic. The attack confirms **0/40** re-identifications via the metadata
  channel after redaction (vs **40/40** on the raw files).
- **Arabic:** all 4 new Arabic individuals (`docx_00/10/11/19`, `pdf_00/10/11/19`) are
  **fully redacted** — name *and* address — and come out **anonymous (k=20)**. The Arabic
  recognizer matches *any* Arabic-script run, so it is locale-robust by construction.
- **Decoy handling:** v3/v4 still keep `hr@company.com` (0 false redactions); v1/v2 still
  wrongly remove it 40/40 — same as the real set.

**Broke on unseen data (the real finding):**

- **Addresses are the weak point.** v4 reports LOCATION "recall 100%", but that metric only
  asks *did the exact full address string survive?* — and it never does, because spaCy still
  removes the **city/country**. The honest signal is the **33 partial leaks** and the
  **80% re-identification rate (double the real set's 40%)**: street number, street name,
  unit line and postcode survive on every non-Arabic locale.
- **Re-identification nearly doubled (40% → 80%)** and mean k collapsed (11.5 → 4.8). It is
  driven **entirely by the visible-body address fragments** (visible body 32/40; metadata
  0/40; hidden/aux just 2/40). Document-consistent redaction still scrubs headers, footers,
  comments and hidden runs — that part generalised.
- **v3 got *worse* than the real set** (re-id 77.5% → 92.5%, phone recall 55% → 45-50%),
  because v3's phone detector is **US-only** and the fresh set is almost entirely
  international. This is the clearest demonstration of why v4's locale-aware phones exist.

---

## 3. Every v4 miss, with its likely cause

v4 is the recommended detector; here is every residual leak it left on the fresh set
(source: `failed_cases_fresh_v4.csv`, `attack_findings_fresh_v4.csv`).

**A. PERSON — full leak — `docx_15`, `pdf_15` — "Minjun Park"  →  cause: NER limit.**
spaCy `en_core_web_lg` does not tag this Korean romaji name as PERSON. v4's extra
recognizers are phone / address / Arabic only — there is no Latin-name fallback — so the
name passes through on *every* surface (body, header, comment) and the person is
re-identified. This is the mirror image of the real set, where v4's 2 misses were the two
hardest US *phone* formats; here the 2 misses are a *name*.

**B. PERSON — partial leak — `docx_05` — "Lima" (Beatriz Santos Lima)  →  cause: NER limit
(ambiguous token).** NER tagged "Beatriz Santos" but dropped the trailing "Lima" in the
DOCX body (it is also a city name). The PDF copy (`pdf_05`) was caught in full, so the
failure is an inconsistent name-boundary call, not a systematic one.

**C. LOCATION — 32 partial leaks (all non-Arabic locales)  →  cause: regex coverage +
locale.** v4's full-address regexes cover **only US + Jordan / UK / Spain**
(`INTL_ADDRESS_REGEXES` in `pipelines.py`). None of the fresh locales match, so redaction
falls back to spaCy GPE/LOC NER, which removes the city/country (hence "0 full leaks") but
leaves the rest. Surviving fragments by locale:

| locale | example surviving tokens |
|---|---|
| Egypt | `11765`, `apartment`, `nasr` |
| Turkey | `34433`, `34710`, `istiklal`, `caddesi`, `istanbul` |
| Brazil | `1500`, `apto`, `1702`, `22021`, `avenida`, `atlantica` |
| Japan | `0023`, `0041`, `1203`, `nishi`, `shinjuku`, `chuo` |
| Canada | `2210`, `station`, `king`, `west` |
| Mexico | `06600`, `avenida`, `ciudad`, `piso`, `reforma` |
| Italy | `corso`, `interno` |
| Nigeria | `101233`, `awolowo` |
| South Korea | `06236`, `teheran` |
| Netherlands | `1015`, `keizersgracht` |
| Sweden | `1102`, `drottninggatan` |
| Argentina | `1450`, `c1043aaz`, `avenida`, `corrientes`, `piso`, `depto` |

Each row above is a surviving **quasi-identifier**: in a 20-person directory, a postcode plus
a street name links to exactly one person, which is why re-identification is 80% even with
only 2 full leaks.

**Clean entities on fresh v4:** PHONE, EMAIL, US_SSN — 100% recall, 0 leaks.

---

## 4. The one-line takeaway

> The **format-based** recognizers (phones, email, SSN, Arabic-script, metadata stripping,
> document-consistent scrubbing) **generalise** to unseen people and locales. The
> **country-list-based** address regexes **do not** — on 12 new locales the full address is
> never matched, so street + postcode survive and re-identification doubles (40% → 80%).
> The fix is a *generic* structured-address recognizer (street-number + line + postcode
> pattern, locale-independent) and/or a multilingual NER model — **not** more per-country
> regexes. (Proposed, not implemented here: this run only *measures* the existing detectors.)

---

## 5. Measurement honesty / caveats (so the numbers are defensible)

1. **Nothing in `pipelines.py` or any regex was changed.** Only the data generator and the
   measurement scripts' input/output paths were added (via the `fresh` argument). The real
   outputs are byte-identical and were not overwritten.
2. **US_SSN is a deliberate control.** The national-ID *values* are new but kept in standard
   `NNN-NN-NNNN` shape, so any recall change comes from the genuinely new dimensions
   (names / phones / addresses), not from also swapping the ID format.
3. **`GENERIC` (the metric's address-word allow-list) was left unchanged.** It lists
   `jordan`/`spain` but not `egypt`/`turkey`/… , so a bare *country* token counts as a
   surviving quasi-identifier on the fresh set where it would not on the real set. We did
   **not** tune the metric to flatter the fresh numbers; this makes the fresh partial-leak
   and re-identification counts a *conservative (worst-case) upper bound* on risk.
4. **Metadata-only baseline (`strip_metadata.py`) was not re-run for fresh** — the brief
   asks for the v1–v4 comparison, and that script targets the real set only.
5. **k=0 guard.** The attack links recovered digit runs against the population; python-docx
   stamps boilerplate digit runs (`core.xml` dates `2001/2006/2013`, `app.xml 0000`) into
   every DOCX. `generate_fresh_docs.py` has a `self_check()` that rejects any synthetic
   number whose *separator-stripped* digits contain such a run (one real collision —
   João's `302 … 01305` → `…2013…` — was caught and fixed). Verified: the attack on the raw
   fresh files re-identifies 40/40 with **min k = 1, zero k = 0, zero false accusations**.
