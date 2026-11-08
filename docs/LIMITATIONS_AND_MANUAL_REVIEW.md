# Limitations & Manual Review of Misses

**Project 09.** The brief requires a **manual review of misses** and an honest statement of limits.
This document reviews every residual case from the recommended detector **v4**
(`evaluation_real_v4.txt`, `failed_cases_real_v4.csv`) on the 40‑document set and records the
remaining limitations. Use `fill_manual_review.py` to record a per‑row `manual_review_note`.

## 1. Manual review of every v4 residual case

*3 full + 16 partial residuals. Partials are grouped by unique value (each appears in both the DOCX
and the PDF of that person).*

| # | Doc(s) | Type | Value | Root cause (manual analysis) | Risk | Recommendation |
|---|--------|------|-------|------------------------------|------|----------------|
| 1 | docx_02 | PERSON (full) | `Aisha Khan` | spaCy NER is context‑sensitive; it tags this borderline name in some layouts but misses it in this document's paragraph/comment context, so the document‑consistent scrub never learns the value. | **Med** — a full name | Human review step; or an organization‑specific name gazetteer. Do **not** silently trust NER for release. |
| 2 | docx_08, pdf_08 | PHONE (full) | `555-0123` | 7‑digit local number with **no area code**; intentionally not matched to avoid redacting unrelated 7‑digit sequences (precision protection). | **Low** — not dialable/identifying on its own | Accept as residual, or add a context‑anchored short‑number rule if 7‑digit numbers are in scope. |
| 3 | docx_02, pdf_02 | LOCATION (partial) | ZIP `62704` | 4‑part US address (`street, apt, city, ST ZIP`) is not matched by the strict address regex; spaCy removes the named parts but leaves the bare ZIP. | **Low** — a ZIP alone is a weak quasi‑identifier | Generalize/suppress ZIP for real release (see §3, linkage). |
| 4 | docx_03, pdf_03 | LOCATION (partial) | ZIP `92101` | Same as #3 (San Diego). | Low | Same. |
| 5 | docx_07, pdf_07 | LOCATION (partial) | ZIP `78765` | Address begins with `P.O. Box` (no leading street number), so the street‑address regex does not fire; spaCy leaves the ZIP. | Low | Add a `P.O. Box` address rule, or suppress ZIP. |
| 6 | docx_12, pdf_12 | LOCATION (partial) | `200021`, `Nanjing` | **Non‑US** 6‑digit postcode + a Chinese district name the US‑centric address regex does not cover; spaCy removes "Shanghai"/"China" but leaves these. | Low | Add non‑US address/postcode coverage. |
| 7 | docx_13, pdf_13 | LOCATION (partial) | `560001`, `Bengaluru` | Same class as #6 (India PIN code + city not matched). | Low | Same (locale address rules). |
| 8 | docx_14, pdf_14 | LOCATION (partial) | `Unter`, `Linden` | German street name `Unter den Linden`; the 5‑digit postcode `10117` was removed, but the street‑name tokens survive. | Low | Locale street‑name coverage / gazetteer. |
| 9 | docx_15, pdf_15 | LOCATION (partial) | `11953`, `Mecca` | Jordanian address `Mecca Street …, Amman 11953`: the postcode and street name survive the US‑centric regex. | Low | Jordan address rule + postcode suppression. |
| 10 | docx_18, pdf_18 | LOCATION (partial) | `11181`, `Rainbow` | Jordanian address `Rainbow Street …, Amman 11181`: same class as #9. | Low | Same. |

**Not‑testable values: 0.** Earlier the Arabic PDFs were excluded because a Latin‑only font dropped the
glyphs. The generator now renders Arabic (reshaped + bidi) **and** embeds a logical‑order hidden text
layer, so `pypdf` extracts the real Unicode: the Arabic name/address in `pdf_05/10/19` is now
**testable** and is redacted by the v4 Arabic recognizer (and cleared from PDF metadata), exactly like
the DOCX counterparts. No planted value is excluded from recall in the current run.

## 2. Known limitations

1. **Statistical NER is not a guarantee.** Person detection depends on context; a small fraction of
   names can be missed in short structured records (case #1). Redaction‑for‑release must include human
   review.
2. **Quasi‑identifiers can survive as fragments.** Bare ZIPs/postcodes and some locale street/district
   names remain (cases #3–10). Removing direct identifiers does not defeat **linkage** re‑identification
   (see §3), which `attack_real_docs.py` demonstrates.
3. **US‑centric address coverage.** The address regex is tuned for US‑style `street, city, ST ZIP`.
   Non‑US postcodes (China/India 6‑digit, Jordan/German codes) and non‑US street names are only
   partially covered — a named gap, not a silent one.
4. **PDF rebuild simplifies layout.** `redact_real_docs.py` re‑draws the PDF from extracted text in a
   single column and truncates very long lines; this favors certainty of redaction over faithful
   layout, and is a utility limitation, not a leak. (It also means visible Arabic is not re‑rendered in
   the redacted PDF — the value is removed, which is the goal.)
5. **Single evaluation set.** v4's rules were developed and reported on the same 40 documents, so
   numbers may be optimistic; a held‑out set would tighten the claim (future work).

## 3. Residual re‑identification (linkage) note

Even at only 3 direct‑identifier leaks, the linkage attack (`attack_real_docs.py`,
`docs/RED_TEAM_REIDENTIFICATION.md`) shows **8 of 20 identities (16/40 documents)** remain **uniquely
re‑identifiable** by **linking** surviving quasi‑identifiers (ZIP/postcode, district) to a candidate
directory. This project removes direct identifiers and most quasi‑identifiers; for a real release we
recommend **generalization/suppression** of residual quasi‑identifiers (e.g., ZIP → region), non‑US
address rules, and a minimum group‑size threshold. This is the boundary between *redaction* (this
project) and formal *anonymization* models (k‑anonymity / l‑diversity), which the attack metric
approximates (anonymity‑set size `k`) but which are out of scope to fully guarantee here.

## 4. TLS, metadata, and communication anonymity (final discussion)

- **Redaction ≠ transport security.** This tool protects document *content*; it does not encrypt
  transmission. TLS would protect a transfer in transit but still exposes **communication metadata**
  (sender, recipient, time, size) to a network observer.
- **Metadata beyond the file.** We remove *document* metadata; *transport/endpoint* metadata is
  outside the tool's control.
- **Communication anonymity is a different control.** Sender/recipient unlinkability (e.g.,
  Tor/Whonix) addresses a different threat and is **not** claimed by this project. The accurate claim
  here is: *"content and document‑metadata disclosure is strongly reduced and measured; transport and
  communication‑metadata anonymity are out of scope."*
