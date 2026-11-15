# Milestone deliverables — CSE331 Project 09

Packaged milestone documents for **Project 09 — Document Redaction & Metadata Privacy**,
formatted per the PBL Student Guide (milestone DOCX with diagrams, sanitized synthetic evidence).

**Project title:** *Beyond the Black Box: Bilingual, Multi-Surface Document Redaction with Measured
Re-identification Risk* — *ما وراء الصندوق الأسود: تنقيح المستندات ثنائي اللغة ومتعدّد الأسطح مع قياس مخاطر إعادة التعرّف*

Both documents are **fully bilingual (English + Arabic)** — every heading, paragraph, bullet, table,
and callout appears in both languages (Arabic right-to-left), so you can adjust either language freely.
The title page carries a short, code-grounded project **description** in both languages.

| File | Milestone | Covers (per the guide) |
|---|---|---|
| `CSE331_TeamXX_M1_Proposal_Requirements.docx` | **M1 — Proposal & Requirements** (Week 4) | Proposal/context/scope, stakeholders, objectives, 11 requirements, data inventory, risks, resources & feasibility, team charter & schedule |
| `CSE331_TeamXX_M2_Design_Prototype.docx` | **M2 — Design & Prototype** (Week 7) | Architecture & data flows, privacy model & assumptions, design alternatives, working prototype, requirement→test map, M1-feedback response |

Each document also contains illustrative **bilingual (English + Arabic)** diagrams — **11 in M1**
(the black-box fallacy, redaction scope, file-format anatomy, system context, stakeholder map, data
classification, re-identification by linkage, evidence chain, risk heat map, methodology, schedule)
and **10 in M2** (architecture, per-surface flow, the metadata channel, attacker model, anonymity-set
*k*, the v1→v4 ladder, the v4 detector internals, results bars, privacy–utility trade-off, and the M3
generalization plan).

Arabic in the diagrams is rendered with the **Amiri** font. `diagrams.py` probes, at import, whether
the installed matplotlib shapes Arabic natively (modern matplotlib does, via HarfBuzz) and
**automatically** falls back to `arabic-reshaper` + `python-bidi` when it does not — so the script is
always correctly connected, on any machine, with no manual switch. The documents' body text is shaped
by Word/LibreOffice (complex-script font Arial, right-to-left runs).

## ⚠️ Placeholders the team must complete before submission

Both documents are ready except for the team-owned fields, which are intentionally left as
`[to be completed]` / `Team XX`:

1. **Team members** — names, roles, and student IDs (title page + charter / roles table).
2. **Instructor** name.
3. **File name** — rename `CSE331_TeamXX_…` to your real team number (e.g. `CSE331_Team07_M1`).
4. **M2 §8 — M1 feedback response** — fill once the instructor returns M1 feedback.
5. Confirm the **target weeks** in the schedule match the dates announced on the course platform.

## Exporting to PDF

The guide accepts **PDF or DOCX**. To hand in a PDF, open the `.docx` in Word and choose
**File → Save As → PDF** (or **File → Export → Create PDF/XPS**). The diagrams are embedded PNGs,
so they export unchanged.

## Regenerating the documents

The documents are fully reproducible from `source/` (Windows Python with
`python-docx`, `matplotlib`, `arabic-reshaper`, `python-bidi`):

```bash
cd source
python diagrams.py     # (re)render the 21 bilingual figures into source/figs/
python build_m1.py     # writes CSE331_TeamXX_M1_Proposal_Requirements.docx
python build_m2.py     # writes CSE331_TeamXX_M2_Design_Prototype.docx
```

All numbers in the documents come from the committed evidence in [`../results/`](../results/).
