# Test Plan

**CSE331 Project 09 — Document Redaction & Metadata Privacy.** Automated tests in
[`tests/test_redaction.py`](../tests/test_redaction.py), run with `pytest -v`. Each test builds its
**own tiny synthetic fixtures** (DOCX/PDF) in a pytest temp dir and drives the **real project code**
— `redact_real_docs` configured for the recommended **v4** detector, plus `evaluate_real_docs` and
`pipelines` — then asserts the outcome. No real personal data is used (invented names, reserved
`example.*` domains, fictional `555‑01xx` numbers, made‑up IDs).

See [`test_results.md`](test_results.md) for the actual `pytest -v` output and the fix history.

## Test types

`privacy` (a value must be gone) · `allowed` (a non‑personal value must stay) · `boundary` (edge
formats) · `failure` (robustness / no false redaction) · `limitation` (a known gap, recorded as
`xfail`) · `utility` (legitimate content preserved).

## Test cases

| ID | Test function | Type | Input (synthetic fixture) | Expected result |
|---|---|---|---|---|
| **T1** | `test_t1_all_planted_text_identifiers_removed` | privacy | DOCX body with PERSON, PHONE (+962), EMAIL, US_SSN, full Jordan address + a non‑PII notes line | All five direct identifiers absent from extracted text; the non‑sensitive word ("engineering") kept |
| **T2** | `test_t2_non_personal_decoy_preserved` | allowed | DOCX body with the decoy `hr@company.com` + a real name and email | `hr@company.com` **still present** (allow‑list); the real name and email removed |
| **T3** | `test_t3_metadata_cleared_docx_and_pdf` | privacy / metadata | DOCX core props (author/title/subject/keywords/comments/last_modified_by) + a comment whose **author** is a name; PDF Info (author/title/subject/creator/keywords) | No planted metadata value survives in DOCX core or PDF Info; the **comment‑author attribute** is emptied |
| **T4** | `test_t4_hidden_and_auxiliary_surfaces_redacted` | privacy / hidden | DOCX with identifiers in **header, footer, comment text, hidden `w:vanish` run**, and a name as **comment author**; PDF with identifiers in **invisible white text** | Every identifier absent from the extracted text of each surface; comment author cleared; white PDF text redacted |
| **T5** | `test_t5_copy_paste_extraction_has_no_planted_value` | privacy / extraction | DOCX with PII **only** in a hidden `w:vanish` run; PDF with PII **only** in invisible white text | The **extracted** text (what copy‑paste / "save as text" returns) contains no planted value — overlay‑only would fail this |
| **T6a** | `test_t6_boundary_phone_formats` (4 cases) | boundary | `+962 79 555 1234`, `+44 20 7946 0958`, `0795551234`, `555‑0123` | First three detected as PHONE_NUMBER; bare **7‑digit local** `555‑0123` **not** detected (documented precision‑protection limit) |
| **T6b** | `test_t6_boundary_address_formats` (4 cases) | boundary | full Jordan address; US `…, Apt 5B, …, IL 62704`; `…, Unit 12, …, CA 92101`; `P.O. Box …, TX 78765` | Jordan address matched **whole**; US/Apt/Unit/P.O.Box matched only **partly** (city removed, bare ZIP survives) |
| **T7a** | `test_t7a_document_with_no_pii_is_unchanged` | failure / utility | DOCX with only non‑personal text + the decoy | No `<PLACEHOLDER>` inserted (no false redaction); decoy and content words preserved |
| **T7b** | `test_t7b_empty_inputs_do_not_crash` | failure | empty string, whitespace string, empty DOCX (no paragraphs), blank PDF | No exception; output files written |
| **T7c** | `test_t7c_english_ner_misses_arabic_name_xfail` | limitation (`xfail`, strict) | a bare Arabic name `محمد الخطيب` fed to the **English‑only v1** detector | Expected **to fail** to flag it — documents that English NER cannot see Arabic (the reason v4 adds the Arabic recognizer). `strict=True` fails the suite if it unexpectedly passes |
| **T7c′** | `test_t7c_v4_detects_arabic_name` | privacy | same Arabic name fed to **v4** | v4 **does** flag it as PERSON (the bilingual fix) |
| **T8** | `test_t8_evaluator_reports_leak_before_and_none_after` | privacy / utility | DOCX with PERSON, PHONE, US_SSN | The **same evaluator** (`classify`) reports a **full leak before** redaction and **no leak after** — same test conditions before/after |

## How to run

```bash
pip install -r requirements.txt            # includes pytest; see requirements.txt
python -m spacy download en_core_web_lg     # NER model (pinned en_core_web_lg==3.8.0)
python -m pytest tests/ -v                   # from the project root
```

The first test is slow (~6 s) because spaCy + Presidio load once in a session‑scoped fixture; the
whole suite runs in ~10 s.
