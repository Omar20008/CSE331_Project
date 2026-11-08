# Threat Model, Trust Boundaries & Data Flow

**Project 09 — Document Redaction & Metadata Privacy.** Scope: releasing a synthetic HR "employee
personal file" (DOCX/PDF) outside the organization while preserving the document's useful,
non‑identifying content.

## 1. Actors

| Actor | Trust | Goal |
|---|---|---|
| HR author | Trusted (inside boundary) | Produces the original document (full PII) |
| Redaction tool (`redact_real_docs.py` + `pipelines.py`) | Trusted | Detect + remove PII and metadata before release |
| Recipient / observer | **Untrusted** | Receives only the redacted file |
| Adversary | **Untrusted / hostile** | Recovers PII from the released file using any surface + external auxiliary data (linkage) |

## 2. Trust boundary and data flow

```
            ┌──────────────── TRUSTED (inside HR) ─────────────────┐
            │                                                      │
  original DOCX/PDF        ground_truth_real.json  (internal only, │
  documents_real/   ─┐        never released)                      │
                     │                                             │
                     ▼                                             │
        ┌───────────────────────────┐                             │
        │  DETECT   pipelines.py     │  spaCy NER + regex          │
        │  make_detector("v4")       │  (phone/address/Arabic)     │
        └─────────────┬─────────────┘                             │
                      ▼                                            │
        ┌───────────────────────────┐                             │
        │  REDACT   redact_real_docs │  Presidio anonymize text    │
        │  • body/tables/headers/    │  + document-consistent      │
        │    footers/hidden/comments │    scrub                    │
        │  • scrub ALL metadata +    │                             │
        │    comment authors         │                             │
        └─────────────┬─────────────┘                             │
            │         │                                            │
            └─────────┼──────────── TRUST BOUNDARY (release) ──────┘
                      ▼
          redacted_real_v4/*.docx / *.pdf   ──────────►   Recipient / Adversary
                      ▲                                   (sees ONLY this file)
                      │
        ┌─────────────┴─────────────┐
        │  VERIFY + ATTACK          │  evaluate_real_docs.py reads EVERY surface of the
        │  (adversary's view)       │  released file the way an attacker would (extraction,
        │  evaluate / detection /   │  copy-paste, metadata, hidden text, annotations);
        │  attack_real_docs.py      │  attack_real_docs.py then re-identifies by linkage
        └───────────────────────────┘
```

Key property: the **verifier plays the adversary**. `evaluate_real_docs.py` extracts body, headers,
footers, hidden/`vanish` text, comments, PDF annotations, and metadata from the *released* file and
checks each planted value against it — it never trusts the rendered page. `attack_real_docs.py` goes
one step further and is the **executable form of §3's linkage adversary**: it links surviving
quasi‑identifiers against a candidate directory and reports the anonymity‑set size (see
`RED_TEAM_REIDENTIFICATION.md`).

## 3. Adversary knowledge & capabilities (assumptions)

- Has the complete **released (redacted) file** and standard tooling (`pypdf`, `python-docx`, any
  text/metadata extractor, copy‑paste).
- Can read **non‑visible** channels: hidden text, white text, comments, annotations, and all
  metadata parts (core/app/custom `docProps`, PDF info dict, XMP).
- May hold **auxiliary data** and attempt **re‑identification by linkage** on surviving
  quasi‑identifiers (e.g., a bare ZIP + employer context). This capability is **executed**, not just
  assumed, by `attack_real_docs.py`, which models the auxiliary data as a 20‑person candidate directory.
- **Out of scope:** access to the original file, the ground truth, the internal network, or the
  rendering pipeline; side channels (file size, timing); and cryptographic attacks on transport.

## 4. Attack surfaces → tested

Every surface in the data flow is exercised by the baseline (`evaluate_real_docs.py original`), which
shows PII leaking from body, header, footer, comments, hidden text, and metadata on **40/40**
documents (20 synthetic individuals × 2 formats) — establishing the "before protection" condition
under the **same test** used "after". The attacker (`attack_real_docs.py original`) correspondingly
re‑identifies **40/40**.

## 5. Transport / endpoint note (TLS, metadata, communication anonymity)

Redaction protects the **content** of a released file; it does **not** provide transport
confidentiality or sender anonymity. If these documents were transmitted, TLS would protect them in
transit but would still expose **metadata** (who sent what, when, to whom) to a network observer, and
the **endpoints** (sender/recipient devices) remain outside this tool's control. Communication
anonymity (e.g., Tor/Whonix) is a *different* control addressing a *different* threat and is not
claimed here. See `LIMITATIONS_AND_MANUAL_REVIEW.md`.
