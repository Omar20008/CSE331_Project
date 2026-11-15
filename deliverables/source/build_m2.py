# -*- coding: utf-8 -*-
import os
from docxcommon import (new_doc, heading, bipara, bibullet, table, figure,
                        callout, title_page, enpara, arpara, running_chrome, BLUE, TEAL, GREEN, RED, MUTED, INK)

HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs")
OUT = r"C:\Users\omar\CSE331_Project\deliverables\CSE331_TeamXX_M2_Design_Prototype.docx"

TITLE_EN = "Beyond the Black Box: Bilingual, Multi-Surface Document Redaction with Measured Re-identification Risk"
TITLE_AR = "ما وراء الصندوق الأسود: تنقيح المستندات ثنائي اللغة ومتعدّد الأسطح مع قياس مخاطر إعادة التعرّف"
DESC_EN = ("A local, offline Python tool that detects and removes personal data from Word (DOCX) and PDF "
           "documents on every surface \u2014 body, tables, headers/footers, hidden text, comments and comment "
           "authors, PDF annotations, and file metadata. Built on Microsoft Presidio and spaCy with custom "
           "bilingual recognizers for Arabic-script names/addresses and Jordanian/international phone numbers, "
           "it measures detection precision/recall, counts residual disclosures, and runs a re-identification "
           "(anonymity-set) attack on its own output \u2014 reporting residual risk rather than claiming anonymity. "
           "Evaluated on 40 synthetic documents.")
DESC_AR = ("أداة محلّية تعمل دون اتصال، مكتوبة بلغة Python، تكشف البيانات الشخصية وتزيلها من مستندات Word (DOCX) "
           "وPDF على كل سطح: المتن والجداول والرؤوس والتذييلات والنص المخفي والتعليقات وأسماء كاتبيها وتعليقات "
           "PDF التوضيحية والبيانات الوصفية للملف. وهي مبنية على Microsoft Presidio و spaCy مع مُميِّزات ثنائية "
           "اللغة مخصّصة للأسماء والعناوين بالخط العربي وأرقام الهواتف الأردنية والدولية، ثم تقيس دقّة الكشف "
           "واستدعاءه، وتَعُدّ التسرّبات المتبقّية، وتشنّ هجوم إعادة تعرّف (حجم مجموعة إخفاء الهوية) على مخرجاتها "
           "— وتُفصح عن المخاطر المتبقّية بدل ادّعاء إخفاء الهوية. جرى تقييمها على 40 مستندًا اصطناعيًا.")

doc = new_doc()
title_page(
    doc,
    course="CSE331 — Confidentiality and Information Privacy",
    project="Project 09 — Document Redaction & Metadata Privacy",
    milestone_en="MILESTONE 2 · DESIGN & PROTOTYPE",
    milestone_ar="المحطّة 2 · التصميم والنموذج الأوّلي",
    title_en=TITLE_EN, title_ar=TITLE_AR,
    sub_en="Architecture & data flows, privacy model, design alternatives, a working prototype, the requirement\u2192test map, and the response to M1 feedback",
    sub_ar="البنية وتدفّق البيانات ونموذج الخصوصية وبدائل التصميم والنموذج الأوّلي العامل وخريطة الاختبارات والاستجابة لملاحظات M1",
    desc_en=DESC_EN, desc_ar=DESC_AR,
    meta_rows=[
        (("Milestone", "المحطّة"), "M2 — Design & Prototype (Week 7 · 7 marks)"),
        (("Builds on", "يبني على"), "M1 — Proposal & Requirements (CSE331_TeamXX_M1)"),
        (("Team", "الفريق"), "Team XX — [names, roles & student IDs to be completed]"),
        (("Instructor", "المُدرّس"), "[to be completed]"),
        (("Semester", "الفصل"), "First semester, 2026\u20132027"),
        (("Date / Version", "التاريخ / الإصدار"), "10 November 2026 · v1.0"),
    ],
    filename="CSE331_TeamXX_M2.docx",
)
running_chrome(doc, "CSE331 · Project 09 — M2 Design & Prototype", "التصميم والنموذج الأوّلي · المشروع 09")

# ---------------------------------------------------------------- 1 intro
heading(doc, "Introduction \u2014 what this milestone delivers", "مقدّمة \u2014 ما تُقدّمه هذه المحطّة", 1, number="1")
bipara(doc,
    "M1 defined the problem, scope, requirements, data inventory, and risks for a local, bilingual tool that "
    "minimizes personal-data disclosure across every surface of an Office/PDF document. This milestone turns "
    "that proposal into a justified design and a running prototype: it presents the architecture and data "
    "flows, states the privacy model and its assumptions, compares the design alternatives we evaluated, "
    "describes the working build, maps each requirement to the test that exercises it, and records our "
    "response to M1 feedback.",
    "عرّفت المحطّة M1 المشكلة والنطاق والمتطلّبات وجرد البيانات والمخاطر لأداة محلّية ثنائية اللغة تُقلّل إفشاء "
    "البيانات الشخصية عبر كل سطح من أسطح مستند Office/PDF. وتحوّل هذه المحطّة ذلك المقترح إلى تصميم مُبرَّر "
    "ونموذج أوّلي عامل: فتعرض البنية وتدفّق البيانات، وتذكر نموذج الخصوصية وافتراضاته، وتقارن بدائل التصميم "
    "التي قيّمناها، وتصف البناء العامل، وتربط كل متطلّب بالاختبار الذي يفحصه، وتسجّل استجابتنا لملاحظات M1.")
table(doc,
      [("M2 required element (rubric)", "العنصر المطلوب في M2"), ("Where it is in this document", "موضعه في هذا المستند")],
      [[("Architecture and data flows", "البنية وتدفّق البيانات"), ("\u00a72 \u2014 diagram, trust boundaries, component table", "\u00a72 \u2014 المخطّط وحدود الثقة وجدول المكوّنات")],
       [("Privacy model / policy and assumptions", "نموذج/سياسة الخصوصية والافتراضات"), ("\u00a73 \u2014 assets, attacker model A1\u2013A4, assumptions", "\u00a73 \u2014 الأصول ونموذج المُهاجِم A1\u2013A4 والافتراضات")],
       [("Alternatives", "البدائل"), ("\u00a74 \u2014 the v1\u2192v4 ladder and the rejected overlay", "\u00a74 \u2014 سُلّم v1\u2192v4 والتراكب المرفوض")],
       [("Working partial build", "بناء جزئي عامل"), ("\u00a75 \u2014 what runs today and how to run it", "\u00a75 \u2014 ما يعمل اليوم وكيفية تشغيله")],
       [("Requirement-to-test map", "خريطة المتطلّب إلى الاختبار"), ("\u00a76 \u2014 traceability table", "\u00a76 \u2014 جدول التتبّع")],
       [("M1 feedback response", "الاستجابة لملاحظات M1"), ("\u00a78 \u2014 feedback-tracking table", "\u00a78 \u2014 جدول متابعة الملاحظات")]],
      widths=[3.1, 3.5], font=8.4)

# ---------------------------------------------------------------- 2 architecture
heading(doc, "Architecture and data flow", "البنية وتدفّق البيانات", 1, number="2")
bipara(doc,
    "The pipeline runs entirely on the local machine inside the HR trust boundary. Only the redacted file "
    "crosses the boundary to the recipient; the measurement components deliberately play the adversary and "
    "read only that released file.",
    "يعمل خط المعالجة بالكامل على الجهاز المحلّي داخل حدود ثقة الموارد البشرية. ولا يعبر الحدَّ إلى المستلِم "
    "إلا الملف المُنقَّح؛ أمّا مكوّنات القياس فتلعب عمدًا دور الخصم ولا تقرأ سوى ذلك الملف المُطلَق.")
figure(doc, os.path.join(FIG, "m2_arch.png"),
       "End-to-end architecture and data flow, with trust boundaries made explicit",
       "البنية وتدفّق البيانات من البداية إلى النهاية مع إظهار حدود الثقة")
heading(doc, "Trust boundaries", "حدود الثقة", 2, number="2.1")
bibullet(doc, [("Untrusted input container. ", {"bold": True}), "Each document is treated as an untrusted container: PII may hide on any surface, so the pipeline must reach every one."],
         [("حاوية إدخال غير موثوقة. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "يُعامَل كل مستند كحاوية غير موثوقة: فقد تختبئ البيانات على أي سطح، ويجب أن يبلغ الخط كلًّا منها."])
bibullet(doc, [("Local processing (trusted). ", {"bold": True}), "Generation, extraction, detection and redaction run locally; the ground-truth file scores protection and is never released."],
         [("معالجة محلّية (موثوقة). ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "يجري التوليد والاستخراج والكشف والتنقيح محلّيًا؛ وملف المرجع يُسجّل الحماية ولا يُنشر أبدًا."])
bibullet(doc, [("Release boundary. ", {"bold": True}), "Only the redacted output crosses to the recipient; everything the adversary can do is modelled by reading that file alone."],
         [("حدّ الإطلاق. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "لا يعبر إلى المستلِم إلا المخرَج المُنقَّح؛ وكل ما يستطيعه الخصم يُنمذَج بقراءة ذلك الملف وحده."])
bibullet(doc, [("Measurement plays the adversary. ", {"bold": True}), "The evaluator and attacker read exactly the surfaces an adversary can (extracted text + metadata), never the rendered page."],
         [("القياس يلعب دور الخصم. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "يقرأ المُقيّم والمُهاجِم الأسطح نفسها التي يصل إليها الخصم (النص المُستخرَج + البيانات الوصفية)، لا الصفحة المعروضة."])
heading(doc, "Components", "المكوّنات", 2, number="2.2")
table(doc,
      [("Component", "المكوّن"), ("Role", "الدور")],
      [[("Synthetic generator", "المولّد الاصطناعي"), ("Builds 20+ individuals \u2192 40 DOCX/PDF with PII on every surface + metadata, and emits per-value ground truth (deterministic).", "يبني أكثر من 20 فردًا \u2190 40 مستند DOCX/PDF ببيانات على كل سطح + بيانات وصفية، ويُخرج مرجعًا لكل قيمة (حتمي).")],
       [("Extraction", "الاستخراج"), ("Pulls text + metadata from every surface (python-docx, pypdf, raw XML scan) \u2014 hidden runs, comment authors, headers/footers.", "يسحب النص والبيانات الوصفية من كل سطح \u2014 المقاطع المخفية وأسماء الكُتّاب والرؤوس/التذييلات.")],
       [("Detectors (v1\u2013v4)", "الكواشف (v1\u2013v4)"), ("Map text \u2192 PII spans: Presidio + spaCy NER + phone/address/Arabic recognizers + an allow-list for the decoy.", "تُحوّل النص \u2190 نطاقات بيانات شخصية: Presidio + spaCy + مُميّزات هاتف/عنوان/عربية + قائمة سماح للطُّعم.")],
       [("Redaction / rewrite", "التنقيح / إعادة الكتابة"), ("Replace each detected span and rewrite the file; v4 scrubs document-consistently (detect once, remove every occurrence).", "تستبدل كل نطاق مكتشَف وتعيد كتابة الملف؛ وتُنقّي v4 باتّساق المستند (كشف مرّة، إزالة كل الورود).")],
       [("Metadata stripping", "إزالة البيانات الوصفية"), ("Clear DOCX core properties + comment authors and the PDF Info dict; a metadata-only variant is kept as a baseline.", "تمسح خصائص DOCX وأسماء الكُتّاب و Info في PDF؛ ويُبقى متغيّر البيانات الوصفية فقط كأساس.")],
       [("Measurement", "القياس"), ("Detection precision/recall, residual disclosure, and a re-identification attack \u2014 three separate, honest metrics.", "دقّة/استدعاء الكشف والتسرّب المتبقّي وهجوم إعادة التعرّف \u2014 ثلاثة مقاييس صادقة منفصلة.")]],
      widths=[1.7, 4.9], font=8.2)

# ---------------------------------------------------------------- 3 privacy model
figure(doc, os.path.join(FIG, "m2_metadata.png"),
       "Closing the metadata and comment-author channel — every field cleared",
       "إغلاق قناة البيانات الوصفية واسم كاتب التعليق — مسح كل حقل")
figure(doc, os.path.join(FIG, "m2_surface_flow.png"),
       "Per-surface redaction — the pipeline reaches every channel, then re-inspects",
       "التنقيح لكل سطح — يبلغ الخط كل قناة ثم يُعيد الفحص")
heading(doc, "Privacy model, policy and assumptions", "نموذج الخصوصية والسياسة والافتراضات", 1, number="3")
heading(doc, "Assets and policy", "الأصول والسياسة", 2, number="3.1")
bipara(doc,
    "The protected assets are the direct identifiers (name, phone, email, national ID), the quasi-identifiers "
    "(address, ZIP/postcode, district, employer context) that re-identify by linkage, the sensitive context "
    "(that the file concerns a specific person), and every hidden-surface copy of them. The release policy: a "
    "document may leave the HR boundary only once every direct identifier is removed on every surface, metadata "
    "and comment authors are cleared, and residual quasi-identifier risk has been measured and reviewed.",
    "الأصول المحميّة هي المعرّفات المباشرة (الاسم والهاتف والبريد والرقم الوطني)، والمعرّفات شبه المباشرة "
    "(العنوان والرمز البريدي والحي وسياق جهة العمل) التي تُعيد التعرّف بالربط، والسياق الحسّاس (أنّ الملف يخصّ "
    "شخصًا بعينه)، وكل نسخة مخفية منها. وسياسة الإطلاق: لا يغادر المستند حدود الموارد البشرية إلا بعد إزالة كل "
    "معرّف مباشر على كل سطح، ومسح البيانات الوصفية وأسماء الكُتّاب، وقياس خطر المعرّفات شبه المباشرة المتبقّي "
    "ومراجعته.")
heading(doc, "Attacker model", "نموذج المُهاجِم", 2, number="3.2")
table(doc,
      [("#", "#"), ("Attacker", "المُهاجِم"), ("Knows / can do", "ما يعرفه / يقدر عليه"), ("Modelled by", "يُنمذَج بـ")],
      [["A1", ("Reader of the released file", "قارئ الملف المُطلَق"), ("Opens it and reads the visible page", "يفتحه ويقرأ الصفحة المرئية"), ("Evaluator baseline", "أساس المُقيّم")],
       ["A2", ("Text extractor / copy-paster", "مُستخرِج النص / الناسخ"), ("Extracts the text layer incl. hidden & white text", "يستخرج طبقة النص شاملةً المخفي والأبيض"), ("Residual-disclosure evaluator", "مُقيّم التسرّب")],
       ["A3", ("Metadata / hidden-content inspector", "فاحص البيانات الوصفية/المخفية"), ("Reads all metadata, comment authors, annotations", "يقرأ كل البيانات الوصفية وأسماء الكُتّاب والتعليقات"), ("Evaluator + metadata check", "المُقيّم + فحص البيانات")],
       ["A4", ("Linkage adversary", "خصم الربط"), ("A1\u2013A3 + an auxiliary directory \u2192 puts a name to the file", "A1\u2013A3 + دليل مساعد \u2190 يُسمّي الملف"), ("Re-identification attack (k)", "هجوم إعادة التعرّف (k)")]],
      widths=[0.4, 1.9, 2.9, 1.4], font=8.1)
figure(doc, os.path.join(FIG, "m2_attackers.png"),
       "Attacker model A1→A4 — escalating knowledge and capability",
       "نموذج المُهاجِم A1→A4 — معرفة وقدرة متصاعدتان")
heading(doc, "Assumptions", "الافتراضات", 2, number="3.3")
bibullet(doc, "The adversary holds the complete released file and standard open-source tooling, and can read every non-visible channel.",
         "يملك الخصم الملف المُطلَق كاملًا وأدوات مفتوحة المصدر معتادة، ويستطيع قراءة كل قناة غير مرئية.")
bibullet(doc, "Fragment recovery is conservative, so the reported anonymity-set k is an upper bound on anonymity \u2014 the harness never understates risk.",
         "استعادة الأجزاء مُتحفِّظة، فقيمة k المُبلَّغة حدٌّ أعلى لإخفاء الهوية \u2014 والأداة لا تُقلّل من الخطر أبدًا.")
bibullet(doc, "Synthetic data is fixed/deterministic; results are reproducible under the pinned environment.",
         "البيانات الاصطناعية ثابتة/حتمية؛ والنتائج قابلة للتكرار في البيئة المثبّتة.")
callout(doc, "No-anonymity statement.", "بيان عدم إخفاء الهوية.",
        "This tool reduces and measures disclosure; it does not guarantee complete anonymity. Even the "
        "recommended build leaves residual quasi-identifiers that re-identify some documents by linkage. "
        "Redaction here is a strong, measured control \u2014 not a proof of anonymization.",
        "تُقلّل هذه الأداة الإفشاء وتقيسه؛ لكنها لا تضمن إخفاء الهوية الكامل. فحتى البناء المُوصى به يُبقي "
        "معرّفات شبه مباشرة تُعيد التعرّف على بعض المستندات بالربط. والتنقيح هنا ضابط قوي ومقيس \u2014 لا برهان على "
        "إخفاء الهوية.", fill="FEE2E2", bar="DC2626")

# ---------------------------------------------------------------- 4 alternatives
heading(doc, "Design alternatives compared", "مقارنة بدائل التصميم", 1, number="4")
bipara(doc,
    "We deliberately compared a ladder of approaches so each design choice is justified by a measured number "
    "rather than asserted. Each stage fixes a named weakness of the previous one.",
    "قارنّا عمدًا سُلّمًا من الأساليب كي يُبرَّر كل قرار تصميمي برقم مقيس لا بالادّعاء. وتعالج كل مرحلة ضعفًا "
    "محدّدًا في سابقتها.")
figure(doc, os.path.join(FIG, "m2_ladder.png"),
       "The v1\u2192v4 design ladder \u2014 each stage closes a named weakness",
       "سُلّم التصميم v1\u2192v4 \u2014 كل مرحلة تُغلق ضعفًا محدّدًا")
table(doc,
      [("Approach", "الأسلوب"), ("What it adds", "ما يضيفه"), ("Key result", "النتيجة"), ("Why not enough alone", "لماذا لا يكفي وحده")],
      [[("Metadata-only strip", "إزالة البيانات الوصفية فقط"), ("Clears metadata, no body redaction", "يمسح البيانات الوصفية بلا تنقيح للمتن"), ("Body leaks; re-id 100%", "المتن يتسرّب؛ 100%"), ("Forgets the comment-author attribute", "يغفل خاصية كاتب التعليق")],
       [("v1 \u2014 Presidio defaults", "v1 \u2014 افتراضات Presidio"), ("Built-in recognizers", "مُميّزات مدمجة"), ("Recall 93.5%; re-id 87.5%", "استدعاء 93.5%"), ("Over-redacts the decoy; misses hard names", "يُفرِط في تنقيح الطُّعم ويفوته أسماء")],
       [("v2 \u2014 + spaCy lg", "v2 \u2014 + spaCy lg"), ("Stronger PERSON/LOCATION NER", "تمييز أقوى للأشخاص/المواقع"), ("Recall 93.5%; re-id 92.5%", "استدعاء 93.5%"), ("Barely moves vs v1 (same hard names)", "تحسّن ضئيل عن v1")],
       [("v3 \u2014 + US regex + allow-list", "v3 \u2014 + تعابير + قائمة سماح"), ("Decoy allow-list; US phone/address regex", "قائمة سماح؛ تعابير هاتف/عنوان أمريكية"), ("Precision 99.4%; re-id 77.5%", "دقّة 99.4%"), ("US-only phone regex drops recall to 55%", "تعابير أمريكية فقط تُسقِط الاستدعاء إلى 55%")],
       [("v4 \u2014 locale/bilingual (chosen)", "v4 \u2014 مراعٍ للمنطقة/ثنائي (المختار)"), ("Jordan/intl phones, Arabic, consistent scrub", "هواتف أردنية/دولية وعربية وتنقية متّسقة"), ("Recall 99.0%; re-id 40%", "استدعاء 99.0%"), ("Country-list addresses don\u2019t generalise", "عناوين قائمة الدول لا تُعمَّم")],
       [("Visual overlay (rejected)", "تراكب مرئي (مرفوض)"), ("Draws a black box over the page", "يرسم صندوقًا أسود فوق الصفحة"), ("Would register as 100% leak", "يُسجَّل تسرّبًا 100%"), ("Value stays in text/metadata; copy-paste recovers it", "القيمة تبقى في النص/البيانات؛ النسخ يستعيدها")]],
      widths=[1.65, 1.9, 1.35, 1.7], font=8.0)
callout(doc, "Why a visual overlay is insufficient \u2014 measured, not asserted.", "لماذا لا يكفي التراكب المرئي \u2014 قياسًا لا ادّعاءً.",
        "The evaluator and attacker read extracted text and metadata, so a box over the page would register "
        "as an unchanged leak. Redaction here means the value is absent from what extraction returns on every "
        "surface \u2014 the only claim an adversary with pypdf/python-docx cannot defeat.",
        "يقرأ المُقيّم والمُهاجِم النص والبيانات الوصفية المُستخرَجة، فالصندوق فوق الصفحة يُسجَّل تسرّبًا دون "
        "تغيير. والتنقيح هنا يعني غياب القيمة عمّا يُعيده الاستخراج على كل سطح \u2014 وهو الادّعاء الوحيد الذي لا "
        "يستطيع خصمٌ بأدوات pypdf/python-docx دحضه.", fill="EFF6FF", bar="2563EB")

# ---------------------------------------------------------------- 5 prototype
figure(doc, os.path.join(FIG, "m2_recognizers.png"),
       "Inside the v4 detector (pipelines.py): five recognizers feed one result set",
       "داخل كاشف v4: خمسة مُميّزات تُغذّي مجموعة نتائج واحدة")
heading(doc, "Working prototype", "النموذج الأوّلي العامل", 1, number="5")
bipara(doc,
    "A functional end-to-end prototype runs today. It generates the synthetic corpus, detects and redacts "
    "across all surfaces (v1\u2013v4), strips metadata, and produces all three metrics \u2014 reproducibly from a "
    "single command.",
    "يعمل اليوم نموذج أوّلي متكامل. فهو يولّد المجموعة الاصطناعية، ويكشف ويُنقّح عبر كل الأسطح (v1\u2013v4)، "
    "ويُزيل البيانات الوصفية، ويُنتج المقاييس الثلاثة \u2014 بشكل قابل للتكرار من أمر واحد.")
heading(doc, "What runs today", "ما الذي يعمل اليوم", 2, number="5.1")
bibullet(doc, [("Data generation: ", {"bold": True}), "20 individuals \u2192 40 DOCX/PDF with PII on every surface + a per-value ground-truth file."],
         [("توليد البيانات: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "20 فردًا \u2190 40 مستند DOCX/PDF ببيانات على كل سطح + ملف مرجع لكل قيمة."])
bibullet(doc, [("Detection & redaction: ", {"bold": True}), "four detector stages (v1\u2013v4) + a metadata-only baseline, writing redacted corpora per version."],
         [("الكشف والتنقيح: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "أربع مراحل كشف (v1\u2013v4) + أساس البيانات الوصفية فقط، مع كتابة مجموعات مُنقّحة لكل إصدار."])
bibullet(doc, [("Measurement: ", {"bold": True}), "detector precision/recall, residual-disclosure evaluation, and the re-identification attack, each with an evidence file."],
         [("القياس: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "دقّة/استدعاء الكاشف وتقييم التسرّب وهجوم إعادة التعرّف، ولكلٍّ ملف دليل."])
bibullet(doc, [("Generalisation check: ", {"bold": True}), "a second, unseen hold-out set the detectors were never tuned on, for honest generalisation numbers."],
         [("فحص التعميم: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "مجموعة اختبار ثانية غير مرئية لم تُضبَط عليها الكواشف، لأرقام تعميم صادقة."])
bibullet(doc, [("Automated tests: ", {"bold": True}), "a pytest suite (17 passed, 1 documented xfail) builds its own fixtures and drives the chosen v4 pipeline."],
         [("اختبارات آلية: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "مجموعة pytest (17 ناجحة، 1 xfail موثّق) تبني تجهيزاتها وتُشغّل خط v4 المختار."])
heading(doc, "How to run it", "كيفية تشغيله", 2, number="5.2")
for cmd, en, ar in [
    ("python generate_real_docs.py", "create the 40 synthetic documents + ground truth", "إنشاء 40 مستندًا اصطناعيًا + المرجع"),
    ("python run_all_real.py", "redact v1\u2013v4 + baseline, then evaluate, score detection, and attack", "تنقيح v1\u2013v4 + الأساس، ثم التقييم والكشف والهجوم"),
    ("python run_all_fresh.py", "repeat the whole chain on the unseen hold-out set", "تكرار السلسلة على مجموعة الاختبار غير المرئية"),
]:
    enpara(doc, (cmd + "  ", {"size": 9.5, "color": TEAL, "bold": True}), ("\u2014 " + en, {"size": 9.5}), space_after=1)
    arpara(doc, "\u2014 " + ar, space_after=5, size=9.5)
heading(doc, "Current status (partial build)", "الحالة الراهنة (بناء جزئي)", 2, number="5.3")
bibullet(doc, [("Complete: ", {"bold": True, "color": GREEN}), "detection, multi-surface redaction, metadata/comment-author clearing, all three metrics, tests, reproducibility."],
         [("مُكتمل: ", {"bold": True, "cs": True, "rtl": True, "color": GREEN}), "الكشف والتنقيح متعدّد الأسطح ومسح البيانات الوصفية/أسماء الكُتّاب والمقاييس الثلاثة والاختبارات وقابلية التكرار."])
bibullet(doc, [("Planned for M3: ", {"bold": True, "color": RED}), "quasi-identifier generalization (ZIP\u2192region), a P.O.-Box rule, broader non-US address coverage, and the Jordan PDPL control mapping."],
         [("مخطّط لـ M3: ", {"bold": True, "cs": True, "rtl": True, "color": RED}), "تعميم المعرّفات شبه المباشرة (الرمز \u2190 المنطقة) وقاعدة صندوق البريد وتوسيع تغطية العناوين وربط قانون حماية البيانات الأردني."])

# ---------------------------------------------------------------- 6 req->test
heading(doc, "Requirement-to-test map", "خريطة المتطلّب إلى الاختبار", 1, number="6")
bipara(doc,
    "Every requirement from M1 is traced to the control that implements it, the test that exercises it, and "
    "the measured result for the chosen v4 build.",
    "يُربط كل متطلّب من M1 بالضابط الذي يُنفّذه، والاختبار الذي يفحصه، والنتيجة المقيسة لبناء v4 المختار.")
table(doc,
      [("Req", "المتطلّب"), ("Control", "الضابط"), ("Test / evidence", "الاختبار / الدليل"), ("Result (v4)", "النتيجة (v4)")],
      [["FR-1", ("NER + consistent scrub + comment-author clear", "تمييز + تنقية متّسقة + مسح الكاتب"), ("PERSON recall; leak locations", "استدعاء؛ مواضع التسرّب"), ("97.5% recall (1 residual name)", "97.5% (اسم متبقٍّ واحد)")],
       ["FR-2", ("US + intl + Jordan phone recognizers", "مُميّزات هاتف أمريكية ودولية وأردنية"), ("PHONE recall; boundary formats", "استدعاء؛ صيغ حدّية"), ("95% (1 local 7-digit \u00d72)", "95% (رقم محلّي \u00d72)")],
       ["FR-3", ("Presidio EMAIL recognizer", "مُميّز بريد Presidio"), ("EMAIL recall", "استدعاء البريد"), ("100%", "100%")],
       ["FR-4", ("Address regex + overlap resolution", "تعابير العنوان + حلّ التداخل"), ("LOCATION full/partial", "موقع كامل/جزئي"), ("0 full, 16 partial (postcodes)", "0 كامل، 16 جزئي")],
       ["FR-5", ("Presidio national-ID recognizer", "مُميّز الرقم الوطني"), ("ID recall", "استدعاء الهوية"), ("100%", "100%")],
       ["FR-6", ("Clear DOCX core + PDF Info + comment authors", "مسح DOCX و Info وأسماء الكُتّاب"), ("Metadata leaks", "تسرّب البيانات الوصفية"), ("0 metadata leaks", "صفر")],
       ["FR-7", ("Surface-aware redaction; PDF rebuilt from text", "تنقيح واعٍ بالأسطح؛ إعادة بناء PDF"), ("Hidden/comment/annotation leaks", "تسرّب المخفي/التعليقات"), ("0 names; 1 short phone", "0 أسماء؛ هاتف قصير")],
       ["FR-8", ("Allow-list; utility metric", "قائمة سماح؛ مقياس المنفعة"), ("Precision, decoy, utility", "الدقّة والطُّعم والمنفعة"), ("98.6% prec., 0/40 decoy, 97% util.", "98.6% دقّة، 97% منفعة")],
       ["NFR-1", ("Deterministic data + pinned deps", "بيانات حتمية + اعتماديات مثبّتة"), ("Re-run orchestrators", "إعادة تشغيل المنسّقات"), ("Stable, reproducible outputs", "مخرجات ثابتة")],
       ["NFR-2", ("Arabic recognizer + Arabic extraction", "مُميّز عربي + استخراج عربي"), ("Arabic detect (DOCX & PDF)", "كشف العربية (DOCX و PDF)"), ("Arabic name+address redacted", "تنقيح الاسم+العنوان العربي")],
       ["NFR-3", ("Re-identification attack (anonymity-set k)", "هجوم إعادة التعرّف (k)"), ("Re-id rate & mean k", "النسبة ومتوسط k"), ("100%\u219240% re-id; k 1.0\u219211.5", "100%\u219240%؛ k 1.0\u219211.5")]],
      widths=[0.6, 2.75, 1.95, 1.3], font=7.9)

# ---------------------------------------------------------------- 7 results
heading(doc, "Early results and the privacy\u2013utility trade-off", "النتائج الأولية ومفاضلة الخصوصية والمنفعة", 1, number="7")
bipara(doc,
    "Three separate metrics are reported on the 40-document set (20 individuals \u00d7 2 formats). The chosen v4 "
    "build sits at the favourable corner of the trade-off: high utility with the lowest re-identification.",
    "تُذكر ثلاثة مقاييس منفصلة على مجموعة الـ40 مستندًا (20 فردًا \u00d7 صيغتان). ويقع بناء v4 المختار في الركن "
    "المُواتي من المفاضلة: منفعة عالية مع أدنى إعادة تعرّف.")
figure(doc, os.path.join(FIG, "m2_results_bars.png"),
       "Re-identification falls and mean anonymity k rises across the v1→v4 ladder",
       "تنخفض إعادة التعرّف ويرتفع متوسط k عبر السُّلّم v1→v4")
figure(doc, os.path.join(FIG, "m2_tradeoff.png"),
       "Privacy\u2013utility trade-off across approaches (v4 is the recommended release)",
       "مفاضلة الخصوصية مقابل المنفعة بين الأساليب (v4 هو الإصدار المُوصى به)")
heading(doc, "A. Detector quality (precision / recall)", "أ. جودة الكاشف (الدقّة / الاستدعاء)", 2, number="7.1")
table(doc,
      [("Detector", "الكاشف"), ("Recall", "الاستدعاء"), ("Precision", "الدقّة"), ("Decoy wrongly flagged", "طُعم مُنقَّح خطأً")],
      [[("v1 \u2014 Presidio defaults", "v1 \u2014 افتراضات Presidio"), "93.5%", "89.3%", "40 / 40"],
       [("v2 \u2014 + spaCy lg", "v2 \u2014 + spaCy lg"), "93.5%", "89.0%", "40 / 40"],
       [("v3 \u2014 + US regex + allow-list", "v3 \u2014 + تعابير + سماح"), "86.5%", "99.4%", "0 / 40"],
       [("v4 \u2014 + locale / bilingual", "v4 \u2014 + منطقة / ثنائي"), "99.0%", "98.6%", "0 / 40"]],
      widths=[2.6, 1.3, 1.3, 1.4], font=8.4)
heading(doc, "B. Residual disclosure (did a value survive?)", "ب. التسرّب المتبقّي (هل بقيت قيمة؟)", 2, number="7.2")
table(doc,
      [("Approach", "الأسلوب"), ("Full leaks", "تسرّب كامل"), ("Partial", "جزئي"), ("Metadata", "وصفية"), ("Utility", "منفعة")],
      [[("original (baseline)", "الأصل (أساس)"), "200", "0", "200", "100%"],
       ["v1", "11", "34", "0", "94.8%"],
       ["v2", "11", "36", "0", "94.8%"],
       ["v3", "25", "28", "0", "97.0%"],
       [("v4 (recommended)", "v4 (موصى به)"), "3", "16", "0", "97.0%"]],
      widths=[2.2, 1.1, 1.0, 1.1, 1.2], font=8.4)
heading(doc, "C. Re-identification (can an attacker name the file?)", "ج. إعادة التعرّف (هل يُسمّي المُهاجِم الملف؟)", 2, number="7.3")
table(doc,
      [("Approach", "الأسلوب"), ("Re-identified (k=1)", "مُعاد التعرّف (k=1)"), ("Mean k", "متوسط k"), ("Metadata channel alone", "قناة البيانات وحدها")],
      [[("original (baseline)", "الأصل (أساس)"), "40/40 (100%)", "1.0", "38/40"],
       ["v1", "35/40 (87.5%)", "3.4", "0/40"],
       ["v2", "37/40 (92.5%)", "2.4", "0/40"],
       ["v3", "31/40 (77.5%)", "5.3", "0/40"],
       [("v4 (recommended)", "v4 (موصى به)"), "16/40 (40%)", "11.5", "0/40"]],
      widths=[2.0, 1.8, 0.9, 1.9], font=8.4)
figure(doc, os.path.join(FIG, "m2_kset.png"),
       "The anonymity set k — v4 moves each released record from unique to hidden in a crowd",
       "مجموعة إخفاء الهوية k — تنقل v4 كل سجلّ من التفرّد إلى الاختباء في حشد")
callout(doc, "Reading the results.", "قراءة النتائج.",
        "Leak counts understate risk: v4 has only 3 full text leaks yet linkage still re-identifies 16/40 via "
        "surviving quasi-identifiers. On the unseen hold-out set, v4 re-identification rises to 80% because the "
        "country-list address rules do not cover the new locales \u2014 the honest generalisation number, and the "
        "motivation for quasi-identifier generalization in M3.",
        "تُقلّل أعداد التسرّب من حجم الخطر: فلدى v4 ثلاث تسرّبات نصّية كاملة فقط، ومع ذلك يُعيد الربط التعرّف "
        "على 16 من 40 عبر معرّفات شبه مباشرة باقية. وعلى مجموعة الاختبار غير المرئية ترتفع إعادة تعرّف v4 إلى "
        "80% لأن قواعد عناوين قائمة الدول لا تُغطّي المناطق الجديدة \u2014 وهو رقم التعميم الصادق ودافع تعميم "
        "المعرّفات شبه المباشرة في M3.", fill="FEF9C3", bar="CA8A04")

# ---------------------------------------------------------------- 8 feedback
heading(doc, "Response to M1 feedback", "الاستجابة لملاحظات M1", 1, number="8")
bipara(doc,
    "This table will record each item of instructor feedback on M1 and our response. It is prepared now and "
    "completed when feedback is received, so the evidence chain shows M1\u2192M2 traceability.",
    "سيُسجّل هذا الجدول كل ملاحظة من المُدرّس على M1 واستجابتنا لها. وهو مُجهَّز الآن ويُكمَل عند استلام "
    "الملاحظات، كي تُظهر سلسلة الأدلّة التتبّع من M1 إلى M2.")
table(doc,
      [("#", "#"), ("M1 feedback item", "ملاحظة M1"), ("Our response / change", "استجابتنا / التغيير"), ("Status", "الحالة")],
      [["1", ("[to be completed on receipt of M1 feedback]", "[يُكمَل عند استلام الملاحظات]"), ("[response]", "[الاستجابة]"), ("[open]", "[مفتوح]")],
       ["2", ("[\u2026]", "[\u2026]"), ("[\u2026]", "[\u2026]"), ("[\u2026]", "[\u2026]")],
       ["3", ("[\u2026]", "[\u2026]"), ("[\u2026]", "[\u2026]"), ("[\u2026]", "[\u2026]")]],
      widths=[0.4, 2.9, 2.5, 0.8], font=8.4)
bipara(doc,
    "Self-identified item carried into M2: the requirement/risk IDs were reconciled into a single scheme "
    "(FR/NFR, R*) shared by M1 and this document, and the quasi-identifier generalization gap is scheduled for M3.",
    "بند حدّدناه ذاتيًا ونقلناه إلى M2: جرى توحيد معرّفات المتطلّبات/المخاطر في مخطّط واحد (FR/NFR، R*) مشترك "
    "بين M1 وهذا المستند، وجُدوِل سدّ فجوة تعميم المعرّفات شبه المباشرة في M3.")

# ---------------------------------------------------------------- 9 residual
heading(doc, "Residual risk and path to M3", "المخاطر المتبقّية والطريق إلى M3", 1, number="9")
bibullet(doc, [("Residual in v4: ", {"bold": True}), "3 full leaks (1 borderline name, 1 area-code-less local number \u00d72) and 16 partial postcode/district fragments; 0 metadata leaks; 97% utility."],
         [("المتبقّي في v4: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "3 تسرّبات كاملة (اسم حدّي، ورقم محلّي بلا رمز منطقة \u00d72) و16 جزءًا من رمز/حي؛ صفر بيانات وصفية؛ 97% منفعة."])
bibullet(doc, [("Next controls (M3): ", {"bold": True}), "postcode generalization (ZIP\u2192region), a P.O.-Box rule, non-US address coverage, an org-name gazetteer, and the PDPL control-to-evidence mapping."],
         [("الضوابط التالية (M3): ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "تعميم الرمز البريدي (الرمز \u2190 المنطقة) وقاعدة صندوق البريد وتغطية العناوين ومُعجم أسماء الجهات وربط القانون بالأدلّة."])
bibullet(doc, [("Why manual review stays: ", {"bold": True}), "statistical NER cannot guarantee 100%, so human review of every residual miss is a required step, not an afterthought."],
         [("لماذا تبقى المراجعة اليدوية: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "لا يضمن التمييز الإحصائي 100%، فمراجعة كل تسرّب متبقٍّ يدويًا خطوة مطلوبة لا أمر ثانوي."])

# ---------------------------------------------------------------- 10 refs
figure(doc, os.path.join(FIG, "m2_generalization.png"),
       "Planned for M3 — generalizing quasi-identifiers raises the anonymity set",
       "مخطّط لـ M3 — تعميم المعرّفات شبه المباشرة يرفع مجموعة إخفاء الهوية")
heading(doc, "References", "المراجع", 1, number="10")
for en, ar in [
    ("CSE331 Confidentiality and Information Privacy \u2014 syllabus and instructor Project Pack.", "CSE331 \u2014 خطة المقرّر وحزمة المشروع."),
    ("NIST SP 800-188, De-Identifying Government Datasets.", "NIST SP 800-188، إزالة تعريف مجموعات البيانات."),
    ("Microsoft Presidio \u2014 PII detection and anonymization framework.", "Microsoft Presidio \u2014 إطار كشف البيانات الشخصية وإخفائها."),
    ("spaCy \u2014 en_core_web_lg named-entity model.", "spaCy \u2014 نموذج الكيانات en_core_web_lg."),
    ("Jordan, Personal Data Protection Law No. 24 of 2023 (MoDEE repository).", "الأردن، قانون حماية البيانات الشخصية رقم 24 لسنة 2023."),
    ("Project repository \u2014 architecture, data dictionary, threat model, evidence map, committed results.", "مستودع المشروع \u2014 البنية وقاموس البيانات ونموذج التهديد وخريطة الأدلّة والنتائج."),
]:
    bibullet(doc, en, ar)

doc.save(OUT)
print("SAVED", OUT)
