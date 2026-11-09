"""
test_redaction.py — CSE331 Project 09: Document Redaction & Metadata Privacy

Pytest suite that builds its OWN tiny synthetic fixtures (DOCX/PDF) in a temp dir, runs the
REAL project pipeline (redact_real_docs configured for v4 + evaluate_real_docs + pipelines),
and asserts privacy / utility outcomes. All data here is synthetic (invented names,
reserved example.* domains, fictional 555-01xx numbers, made-up IDs) — no real personal data.

Test map (see docs/test_plan.md for the full table):
  T1  allowed/privacy  : all planted text identifiers removed (body)
  T2  allowed/allowlist: non-personal decoy hr@company.com is preserved
  T3  metadata         : DOCX core props + comment authors AND PDF Info fields are cleared
  T4  privacy/hidden   : header, footer, comment, hidden w:vanish run, white PDF text redacted
  T5  privacy/extract  : copy-paste/extraction text of the redacted file has no planted value
  T6  boundary         : intl/Jordan/local phone + Apt/Unit/P.O.Box/non-US address formats
  T7a failure          : a document with no PII is left unchanged (no false redaction)
  T7b failure          : empty inputs do not crash the pipeline
  T7c limitation(xfail): English-only NER (v1) does not redact an Arabic name (known limit)
  T8  privacy/utility  : the evaluator reports a full leak BEFORE and none AFTER (same test)

The pipeline loads spaCy + Presidio once (session-scoped fixtures), so the first test is slow.
"""

import os

import pytest
from docx import Document
from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# --------------------------------------------------------------------------- fixture builders
def build_docx(path, body_lines=None, header=None, footer=None, hidden=None,
               comment_text=None, comment_author=None, core=None):
    """Create a tiny synthetic .docx with PII on whichever surfaces are given."""
    doc = Document()
    for line in (body_lines or []):
        doc.add_paragraph(line)
    if hidden is not None:
        run = doc.add_paragraph().add_run(hidden)
        run.font.hidden = True                      # produces a <w:vanish/> run
    if header is not None:
        doc.sections[0].header.paragraphs[0].text = header
    if footer is not None:
        doc.sections[0].footer.paragraphs[0].text = footer
    if comment_text is not None:
        anchor = doc.add_paragraph("review anchor").add_run("anchor")
        doc.add_comment(anchor, text=comment_text,
                        author=comment_author or "", initials="RV")
    if core:
        cp = doc.core_properties
        for field, value in core.items():
            setattr(cp, field, value)
    doc.save(path)
    return path


def build_pdf(path, visible_lines=None, white_lines=None, info=None):
    """Create a tiny synthetic .pdf; white_lines are invisible but still extractable."""
    c = canvas.Canvas(str(path), pagesize=A4)
    if info:
        if "author" in info:
            c.setAuthor(info["author"])
        if "title" in info:
            c.setTitle(info["title"])
        if "subject" in info:
            c.setSubject(info["subject"])
        if "creator" in info:
            c.setCreator(info["creator"])
        if "keywords" in info:
            c.setKeywords(info["keywords"])
    _, h = A4
    y = h - 60
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    for line in (visible_lines or []):
        c.drawString(40, y, line)
        y -= 18
    c.setFillColor(white)                           # invisible white text
    for line in (white_lines or []):
        c.drawString(40, y, line)
        y -= 18
    c.showPage()
    c.save()
    return path


def all_text(evaluator, path, doc_type):
    parts, _meta = evaluator.extract(path, doc_type)
    return "\n".join(parts.values())


def all_meta(evaluator, path, doc_type):
    _parts, meta = evaluator.extract(path, doc_type)
    return "\n".join(str(v) for v in meta.values())


# Synthetic identifiers that v4 fully removes (used where "must be gone" is asserted).
NAME = "Omar Al-Khatib"
PHONE = "+962 79 555 1234"
PHONE_UK = "+44 20 7946 0958"
EMAIL = "omar.khatib@example.jo"
EMAIL2 = "project.lead@example.jo"
SSN = "623-19-4580"
ADDRESS = "Building 15, Wasfi Al-Tal Street, Amman 11181, Jordan"  # v4 matches the full span
DECOY = "hr@company.com"


# --------------------------------------------------------------------------- T1
def test_t1_all_planted_text_identifiers_removed(redactor, evaluator, tmp_path):
    """T1 (allowed/privacy): a normal document — every planted direct identifier is gone."""
    src = build_docx(tmp_path / "t1.docx", body_lines=[
        f"Employee: {NAME}",
        f"Phone: {PHONE}   Email: {EMAIL}",
        f"National ID: {SSN}",
        f"Address: {ADDRESS}",
        "Notes: joined the engineering team this quarter.",
    ])
    out = str(tmp_path / "t1_red.docx")
    redactor.process_docx(str(src), out)

    text = all_text(evaluator, out, "docx")
    for value in (NAME, PHONE, EMAIL, SSN, ADDRESS):
        assert value not in text, f"{value!r} survived redaction in: {text!r}"
    # Non-sensitive utility text is kept.
    assert "engineering" in text.lower()


# --------------------------------------------------------------------------- T2
def test_t2_non_personal_decoy_preserved(redactor, evaluator, tmp_path):
    """T2 (allowed/allow-list): the organizational decoy survives; real PII does not."""
    src = build_docx(tmp_path / "t2.docx", body_lines=[
        f"For HR forms contact {DECOY}.",
        f"Employee {NAME} personal email {EMAIL}.",
    ])
    out = str(tmp_path / "t2_red.docx")
    redactor.process_docx(str(src), out)

    text = all_text(evaluator, out, "docx")
    assert DECOY in text, "allow-listed decoy was wrongly over-redacted"
    assert NAME not in text
    assert EMAIL not in text


# --------------------------------------------------------------------------- T3
def test_t3_metadata_cleared_docx_and_pdf(redactor, evaluator, tmp_path):
    """T3 (metadata): DOCX core props + comment-author attribute AND PDF Info fields cleared."""
    # DOCX: core properties + a comment whose AUTHOR is a person name.
    src_docx = build_docx(
        tmp_path / "t3.docx",
        body_lines=["Quarterly staffing note."],
        comment_text="follow up with the team", comment_author=NAME,
        core={"author": NAME, "title": f"Confidential - {NAME}",
              "subject": "Employee personal file", "keywords": f"{NAME}, {EMAIL}",
              "comments": f"Created for {NAME}", "last_modified_by": NAME},
    )
    out_docx = str(tmp_path / "t3_red.docx")
    redactor.process_docx(str(src_docx), out_docx)
    docx_meta = all_meta(evaluator, out_docx, "docx")
    for value in (NAME, EMAIL):
        assert value not in docx_meta, f"{value!r} survived in DOCX metadata: {docx_meta!r}"
    # comment-author attribute specifically must be emptied
    _parts, meta = evaluator.extract(out_docx, "docx")
    assert NAME not in meta.get("comment_authors", ""), "comment author not cleared"

    # PDF: Info dictionary fields.
    src_pdf = build_pdf(
        tmp_path / "t3.pdf", visible_lines=["Quarterly staffing note."],
        info={"author": NAME, "title": f"Confidential - {NAME}",
              "subject": "Employee personal file", "creator": f"HR System - {NAME}",
              "keywords": f"{NAME}, {EMAIL}"},
    )
    out_pdf = str(tmp_path / "t3_red.pdf")
    redactor.process_pdf(str(src_pdf), out_pdf)
    pdf_meta = all_meta(evaluator, out_pdf, "pdf")
    for value in (NAME, EMAIL, "HR System"):
        assert value not in pdf_meta, f"{value!r} survived in PDF Info: {pdf_meta!r}"


# --------------------------------------------------------------------------- T4
def test_t4_hidden_and_auxiliary_surfaces_redacted(redactor, evaluator, tmp_path):
    """T4 (privacy/hidden): header, footer, comment text, hidden w:vanish run, white PDF text.

    Each surface carries a *deterministically-detected* identifier (phone/email/SSN via regex /
    Presidio pattern, independent of NER context) so a surviving value means the surface was not
    reached, not that NER was flaky. The comment AUTHOR is a name, cleared structurally.
    """
    src_docx = build_docx(
        tmp_path / "t4.docx",
        body_lines=["Body summary line."],
        header=f"Header hotline {PHONE_UK}",
        footer=f"Footer contact {EMAIL2}",
        hidden=f"Hidden {SSN} and {PHONE}",
        comment_text=f"review ref {EMAIL}",
        comment_author=NAME,
    )
    out_docx = str(tmp_path / "t4_red.docx")
    redactor.process_docx(str(src_docx), out_docx)
    text = all_text(evaluator, out_docx, "docx")
    meta = all_meta(evaluator, out_docx, "docx")
    surface_values = {
        "header": PHONE_UK, "footer": EMAIL2,
        "hidden+ssn": SSN, "hidden+phone": PHONE, "comment": EMAIL,
    }
    for where, value in surface_values.items():
        assert value not in text, f"{value!r} survived on the {where} surface"
    assert NAME not in (text + meta), "comment author (a name) was not cleared"

    # PDF invisible white text carries identifiers too
    src_pdf = build_pdf(
        tmp_path / "t4.pdf",
        visible_lines=["Visible: quarterly note."],
        white_lines=[f"Invisible white text {SSN} {PHONE} {EMAIL2}"],
    )
    out_pdf = str(tmp_path / "t4_red.pdf")
    redactor.process_pdf(str(src_pdf), out_pdf)
    ptext = all_text(evaluator, out_pdf, "pdf")
    for value in (SSN, PHONE, EMAIL2):
        assert value not in ptext, f"{value!r} in invisible white PDF text was not redacted"


# --------------------------------------------------------------------------- T5
def test_t5_copy_paste_extraction_has_no_planted_value(redactor, evaluator, tmp_path):
    """T5 (privacy/extract): extraction output (what copy-paste returns) has no planted value.

    The value is planted ONLY in the invisible layer, so a visual overlay alone would leave it
    recoverable; the test reads EXTRACTED text, not the rendered page, and requires it gone.
    """
    # DOCX: value only in a hidden vanish run
    src_docx = build_docx(tmp_path / "t5.docx",
                          body_lines=["Visible non-sensitive summary line."],
                          hidden=f"{NAME} {PHONE}")
    out_docx = str(tmp_path / "t5_red.docx")
    redactor.process_docx(str(src_docx), out_docx)
    dtext = all_text(evaluator, out_docx, "docx")
    assert NAME not in dtext and PHONE not in dtext

    # PDF: value only in invisible white text
    src_pdf = build_pdf(tmp_path / "t5.pdf",
                        visible_lines=["Visible non-sensitive summary line."],
                        white_lines=[f"{NAME} {EMAIL}"])
    out_pdf = str(tmp_path / "t5_red.pdf")
    redactor.process_pdf(str(src_pdf), out_pdf)
    ptext = all_text(evaluator, out_pdf, "pdf")
    assert NAME not in ptext and EMAIL not in ptext


# --------------------------------------------------------------------------- T6
@pytest.mark.parametrize("number, should_detect", [
    ("+962 79 555 1234", True),    # Jordanian international
    ("+44 20 7946 0958", True),    # UK international
    ("0795551234", True),          # Jordanian local mobile
    ("555-0123", False),           # 7-digit local, no area code -> documented limitation
])
def test_t6_boundary_phone_formats(detector_v4, number, should_detect):
    """T6 (boundary): international/Jordanian phones detected; bare 7-digit local is a known gap."""
    text = f"Please call {number} during office hours."
    phones = [r for r in detector_v4(text) if r.entity_type == "PHONE_NUMBER"]
    assert bool(phones) is should_detect, (
        f"{number!r}: expected detect={should_detect}, got {[text[r.start:r.end] for r in phones]}"
    )


@pytest.mark.parametrize("address, expect_full_span", [
    ("Building 15, Wasfi Al-Tal Street, Amman 11181, Jordan", True),   # Jordan rule -> full match
    ("42 Elm Street, Apt 5B, Springfield, IL 62704", False),           # US 4-part -> partial only
    ("700 Harbor Blvd, Unit 12, San Diego, CA 92101", False),          # Unit line -> partial only
    ("P.O. Box 4471, Austin, TX 78765", False),                        # P.O. Box -> partial only
])
def test_t6_boundary_address_formats(detector_v4, address, expect_full_span):
    """T6 (boundary): a locale-covered address is matched whole; US/PObox variants only partly.

    For the partial cases the detector must still remove *something* (the city), but the bare
    ZIP survives — the documented quasi-identifier limitation (see docs/privacy_utility_residual_risk.md).
    """
    text = f"Residence: {address}."
    locs = [text[r.start:r.end] for r in detector_v4(text) if r.entity_type == "LOCATION"]
    assert locs, f"no LOCATION detected in {address!r}"
    if expect_full_span:
        assert address in locs, f"expected full-address match, got {locs}"
    else:
        # at least the city is removed, but not the whole string (ZIP remains) -> partial leak
        assert all(address != m for m in locs), f"unexpected full match for {address!r}: {locs}"


# --------------------------------------------------------------------------- T7a
def test_t7a_document_with_no_pii_is_unchanged(redactor, evaluator, tmp_path):
    """T7 (failure): a PII-free document is passed through without any false redaction."""
    clean_lines = [
        "The quarterly engineering report is due next Monday.",
        "All teams should submit their updated roadmaps.",
        f"For logistics questions, email {DECOY}.",
    ]
    src = build_docx(tmp_path / "t7a.docx", body_lines=clean_lines)
    out = str(tmp_path / "t7a_red.docx")
    redactor.process_docx(str(src), out)
    text = all_text(evaluator, out, "docx")
    assert "<" not in text, f"false redaction placeholder inserted into PII-free doc: {text!r}"
    assert DECOY in text
    for word in ("quarterly", "roadmaps", "logistics"):
        assert word in text.lower()


# --------------------------------------------------------------------------- T7b
def test_t7b_empty_inputs_do_not_crash(redactor, evaluator, tmp_path):
    """T7 (failure): empty DOCX, empty PDF, and empty string do not raise."""
    # empty string through the text redactor
    assert redactor.redact_text("") == ""
    assert redactor.redact_text("   ") == "   "

    # empty DOCX (no paragraphs)
    src_docx = build_docx(tmp_path / "empty.docx", body_lines=[])
    out_docx = str(tmp_path / "empty_red.docx")
    redactor.process_docx(str(src_docx), out_docx)      # must not raise
    assert os.path.exists(out_docx)

    # blank PDF (one empty page)
    src_pdf = build_pdf(tmp_path / "empty.pdf", visible_lines=[])
    out_pdf = str(tmp_path / "empty_red.pdf")
    redactor.process_pdf(str(src_pdf), out_pdf)         # must not raise
    assert os.path.exists(out_pdf)


# --------------------------------------------------------------------------- T7c
# A bare Arabic name: the English spaCy model (v1/v2/v3) has no Arabic NER and deterministically
# returns nothing for it on the pinned en_core_web_lg==3.8.0; v4's ArabicPiiRecognizer catches it.
ARABIC_NAME = "محمد الخطيب"


@pytest.mark.xfail(strict=True, reason=(
    "Known limitation: the Presidio-default / English spaCy detector (v1/v2/v3) has no Arabic "
    "NER, so it does not flag an Arabic-script name. This is exactly why v4 adds "
    "ArabicPiiRecognizer; v4 DOES redact it (see test_t7c_v4_detects_arabic_name). strict=True "
    "makes an unexpected pass fail the suite rather than silently hiding the limitation."))
def test_t7c_english_ner_misses_arabic_name_xfail(detector_v1):
    """T7 (limitation): English-only NER is expected to FAIL to flag an Arabic name."""
    persons = [r for r in detector_v1(ARABIC_NAME) if r.entity_type == "PERSON"]
    assert persons, "English NER flagged an Arabic name (limitation would be resolved)"


def test_t7c_v4_detects_arabic_name(detector_v4):
    """Companion to T7c: v4's bilingual recognizer DOES flag the Arabic name (the fix)."""
    results = detector_v4(ARABIC_NAME)
    assert results, "v4 failed to detect any Arabic-script PII"
    assert any(r.entity_type == "PERSON" for r in results)


# --------------------------------------------------------------------------- T8
def test_t8_evaluator_reports_leak_before_and_none_after(redactor, evaluator, tmp_path):
    """T8 (privacy/utility): same evaluator logic — full leak BEFORE, no leak AFTER."""
    src = build_docx(tmp_path / "t8.docx", body_lines=[
        f"Employee {NAME}", f"Phone {PHONE}", f"ID {SSN}",
    ])
    out = str(tmp_path / "t8_red.docx")

    before = all_text(evaluator, str(src), "docx")
    for value in (NAME, PHONE, SSN):
        kind, _rem = evaluator.classify(value, before)
        assert kind == "full", f"evaluator did not see {value!r} as a full leak before redaction"

    redactor.process_docx(str(src), out)
    after = all_text(evaluator, out, "docx")
    for value in (NAME, PHONE, SSN):
        kind, _rem = evaluator.classify(value, after)
        assert kind is None, f"evaluator still reports {value!r} as leaking after redaction ({kind})"
