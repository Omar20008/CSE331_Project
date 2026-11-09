# Red‑Team Re‑Identification — the threat model, executed

**Project 09 — Document Redaction & Metadata Privacy.** This document describes
`attack_real_docs.py`, an adversary that takes *only the released files* and tries to put a **name**
to each one. It is the executable counterpart to `threat_model.md` §3 ("re‑identification by linkage
on surviving quasi‑identifiers") and reports a privacy outcome the leak‑count table cannot express.

## 1. Why a second, harder question

`evaluate_real_docs.py` answers a *detector* question — **did a planted value survive?** An attacker
does not care whether an exact string survived; they care whether they can **identify the person**. A
file can show **zero full leaks** and still be re‑identified, because surviving **quasi‑identifiers**
(a ZIP, a postcode, a 7‑digit local number) each point at exactly one individual. The right privacy
measure is therefore the **anonymity set**:

> **k = how many people in the attacker's candidate population are still consistent with everything
> that leaked from the released file.**  `k = 1` ⇒ **uniquely re‑identified.**

## 2. Attacker model (stated so the numbers are honest)

| Assumption | Choice in `attack_real_docs.py` |
|---|---|
| Candidate population (auxiliary knowledge) | The **distinct identities** in `ground_truth_real.json` (an "HR directory" the attacker holds). Closed‑world: the file belongs to one row. |
| Surfaces read | **Exactly** the surfaces `evaluate_real_docs.py` measures — body, headers/footers, hidden `<w:vanish>` text, comments + comment‑author attributes, footnotes/endnotes, PDF annotations, and all metadata (core/app/custom `docProps`, PDF info dict, XMP). The attacker is given **no** privileged access. |
| Fragments recovered | Alpha tokens ≥ 4 chars (Arabic included), digit runs ≥ 4, generic address words dropped. Only fragments that match **some** population row are kept (boilerplate matching nobody is discarded). |
| Linkage | A row is *consistent* if every recovered fragment appears in that row's fields. `k` = number of consistent rows. |

**Conservative by design.** Digit runs are taken separately (not re‑joined across separators), so a
stronger attacker could only recover *more*. A reported `k` is therefore an **upper bound on
anonymity** — this harness never understates the risk. Because every recovered fragment comes from the
true person's own data, a unique hit (`k = 1`) is **never a false accusation** (verified: 0 across all
runs).

**Honest caveat on external validity.** Re‑identification rate is **relative to the assumed
directory**. Here synthetic identities mostly live in different cities, so a bare postcode is unique
*in this population of 20*; against a real national population a postcode is shared by thousands. The
value of the metric is therefore **comparative** (does the control shrink the attacker's success and
grow `k`?) and **demonstrative** (quasi‑identifiers link even when direct identifiers are gone) — not
an absolute real‑world re‑identification probability. (A couple of identities *do* share a postcode —
two residents of Amman `11181` — which correctly yields an anonymity set of `k = 2` for them.)

## 3. Results — `attack_report_<version>.txt`

| Approach | Uniquely re‑identified (k=1) | Mean anonymity k | Fully anonymous (k=N) | Metadata alone | Hidden/aux alone |
|---|---:|---:|---:|---:|---:|
| original (raw) | **40 / 40 (100 %)** | 1.0 | 0 / 40 | **38 / 40** | 20 / 40 |
| metadata‑only strip | 40 / 40 (100 %) | 1.0 | 0 / 40 | 19 / 40 | 20 / 40 |
| v1 Presidio | 35 / 40 (87.5 %) | 3.4 | 5 / 40 | 0 / 40 | 6 / 40 |
| v2 + spaCy | 37 / 40 (92.5 %) | 2.4 | 3 / 40 | 0 / 40 | 6 / 40 |
| v3 + US regex | 31 / 40 (77.5 %) | 5.3 | 9 / 40 | 0 / 40 | 10 / 40 |
| **v4 (recommended)** | **16 / 40 (40 %)** | **11.5** | **22 / 40** | **0 / 40** | **1 / 40** |

*(N = 20 distinct individuals.)*

**Reading the results**

- **"A black box over the page is not redaction," proven.** On the raw files the **metadata channel
  alone re‑identifies 38/40** and the **hidden/aux channel alone 20/40** — *without ever reading the
  visible page*. The full pipeline closes the metadata channel completely (0/40) from v1 on; the
  metadata‑only strip does **not** (19/40 remain, because the author also hides in the
  **comment‑author attribute**, consistent with the main evaluation).
- **Removing names is not anonymizing people.** v4 reports only **3 full text leaks**, yet linkage
  still re‑identifies **16/40** (8 identities × 2 formats) — every one via a surviving
  **quasi‑identifier**: ZIP `62704` (Aisha Khan), `92101` (Michael Chen), `78765` (Liam Nguyen),
  postcode `200021` (Mei Lin), `560001` (Arjun Patel), or a district + code such as `Mecca …11953`
  (Khaled Mansour), `Rainbow …11181` (Sara Haddad), and `Unter den Linden` (Hannah Schmidt). These are
  precisely the residual partial leaks `LIMITATIONS_AND_MANUAL_REVIEW.md` documents — the attack shows
  they are **re‑identifying**, not merely "present."
- **The v1→v4 evolution holds under attack.** Re‑identification falls 100 % → 40 % and mean anonymity
  rises 1.0 → 11.5 as each stage closes a named channel (metadata, then hidden/aux via comment‑author
  scrubbing and document‑consistent redaction, then the regex/Arabic coverage of v4). v3 dips in
  re‑identification versus v2 because its US‑only phone regex leaves phones (weakly identifying) while
  removing more of the strongly‑identifying names/addresses; v4 then fixes phones *and* drives
  re‑identification to its lowest.

## 4. What this adds to the project

1. **Executed threat model.** `threat_model.md` §3's linkage adversary is now *code with evidence*,
   not a paragraph.
2. **A privacy metric, not a detector metric.** Anonymity‑set size / re‑identification rate measures
   the **outcome** (can the person be named?) rather than string survival.
3. **Channel attribution.** It proves *which* surface defeats the control, turning "we redact every
   surface" into a measured claim.
4. **A sharper residual‑risk story.** It converts "16 partial location leaks" into the concrete,
   defensible statement: *eight identities remain uniquely re‑identifiable by ZIP/postcode linkage;
   this is why postcode generalization (e.g. ZIP3), non‑US address coverage, and manual review are
   listed as the next controls.*

## 5. Reproduce

```bash
python attack_real_docs.py original   # attacker wins 40/40 (before protection)
python attack_real_docs.py v4         # recommended pipeline (after protection)
# or everything, every approach:
python run_all_real.py                # also writes attack_report_*.txt + attack_findings_*.csv
```

Per‑document evidence (true identity, `k`, attacker's guess, leaking surfaces, the exact recovered
fragments, and which channel was sufficient alone) is in `attack_findings_<version>.csv`.
