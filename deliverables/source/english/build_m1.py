# -*- coding: utf-8 -*-
import os
from docxcommon import (new_doc, heading, bipara, bibullet, table, figure,
                        callout, title_page, enpara, arpara, running_chrome, BLUE, TEAL, GREEN, RED, MUTED, INK)

HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs")
OUT = r"C:\Users\omar\CSE331_Project\deliverables\CSE331_TeamXX_M1_Proposal_Requirements_EN.docx"

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
    milestone_en="MILESTONE 1 · PROPOSAL & REQUIREMENTS",
    milestone_ar="المحطّة 1 · المقترح والمتطلّبات",
    title_en=TITLE_EN, title_ar=TITLE_AR,
    sub_en="Proposal, scope, stakeholders, objectives, requirements, data inventory, risks, resources, and team charter",
    sub_ar="المقترح والنطاق وأصحاب المصلحة والأهداف والمتطلّبات وجرد البيانات والمخاطر والموارد وميثاق الفريق",
    desc_en=DESC_EN, desc_ar=DESC_AR,
    meta_rows=[
        (("Milestone", "المحطّة"), "M1 — Proposal & Requirements (Week 4 · 5 marks)"),
        (("Team", "الفريق"), "Team XX — [names, roles & student IDs to be completed]"),
        (("Instructor", "المُدرّس"), "[to be completed]"),
        (("Semester", "الفصل"), "First semester, 2026\u20132027"),
        (("Date / Version", "التاريخ / الإصدار"), "10 November 2026 · v1.0"),
    ],
    filename="CSE331_TeamXX_M1.docx",
)
running_chrome(doc, "CSE331 · Project 09 — M1 Proposal & Requirements", "المقترح والمتطلّبات · المشروع 09")

# ---------------------------------------------------------------- summary
heading(doc, "Executive summary", "الملخّص التنفيذي", 1)
bipara(doc,
    "This proposal defines a local, bilingual (Arabic + English), Jordan-aware tool that detects and "
    "removes personal data from Office (DOCX) and PDF documents \u2014 not only in the visible body, but on "
    "every surface where personal data hides: headers and footers, hidden text, comments and the "
    "comment-author attribute, PDF annotations, and file metadata. The tool then measures how much "
    "protection and utility it delivers, and finally attacks its own output to test whether an individual "
    "can still be re-identified.",
    "يُعرّف هذا المقترح أداة محلّية ثنائية اللغة (عربية + إنجليزية) ومراعية للسياق الأردني، تكشف البيانات "
    "الشخصية وتزيلها من مستندات Office (DOCX) و PDF \u2014 ليس في المتن المرئي فحسب، بل على كل سطح تختبئ فيه "
    "البيانات الشخصية: الرؤوس والتذييلات والنص المخفي والتعليقات وخاصية اسم كاتب التعليق وتعليقات PDF "
    "التوضيحية والبيانات الوصفية للملف. ثم تقيس الأداة مقدار الحماية والمنفعة اللتين تحقّقهما، وتهاجم أخيرًا "
    "مخرجاتها لاختبار ما إذا كان لا يزال بالإمكان إعادة التعرّف على الفرد.")
bipara(doc,
    "All data is 100% synthetic (invented names, reserved example.* e-mail domains, fictional 555-01xx "
    "phone numbers and made-up identifiers); no real personal record is used. Consistent with the course "
    "brief, we state the threat model and the remaining limitations rather than claiming complete anonymity.",
    "جميع البيانات اصطناعية بالكامل (أسماء مُختلقة، ونطاقات بريد محجوزة example.*، وأرقام هواتف وهمية "
    "555-01xx، ومُعرّفات مُفترَضة)؛ ولا يُستخدم أي سجلّ شخصي حقيقي. واتّساقًا مع توصيف المقرّر، نذكر نموذج "
    "التهديد والقيود المتبقّية بدل ادّعاء إخفاء الهوية الكامل.")

# ---------------------------------------------------------------- 1 scope
heading(doc, "Proposal, context and scope", "المقترح والسياق والنطاق", 1, number="1")
heading(doc, "Problem statement", "بيان المشكلة", 2, number="1.1")
bipara(doc,
    "Organizations routinely share documents that look clean on screen yet still carry personal data in "
    "channels a reader never sees. A black box drawn over a name changes pixels, not bytes: the value "
    "remains in the extracted text layer, in hidden runs, in comments, in annotations, and in document "
    "metadata, where copy-paste, \u201csave as text\u201d, or a metadata viewer recovers it. The problem this "
    "project addresses is minimizing personal-data disclosure across every document surface while preserving "
    "the document\u2019s legitimate, non-identifying content.",
    "تُشارِك المؤسسات بصورة معتادة مستندات تبدو نظيفة على الشاشة، لكنها لا تزال تحمل بيانات شخصية في قنوات "
    "لا يراها القارئ. والصندوق الأسود المرسوم فوق اسمٍ يُغيّر البكسلات لا البايتات: فتبقى القيمة في طبقة النص "
    "المُستخرَج، وفي المقاطع المخفية، وفي التعليقات، وفي التعليقات التوضيحية، وفي البيانات الوصفية للمستند، "
    "حيث يستعيدها النسخ واللصق أو \u201cالحفظ كنص\u201d أو عارض البيانات الوصفية. والمشكلة التي يعالجها هذا المشروع "
    "هي تقليل إفشاء البيانات الشخصية عبر كل سطح من أسطح المستند مع الحفاظ على محتواه المشروع غير المُعرِّف.")
figure(doc, os.path.join(FIG, "m1_blackbox.png"),
       "A visual black box is not redaction — the value survives in text, metadata and comments",
       "الصندوق الأسود المرئي ليس تنقيحًا — القيمة تبقى في النص والبيانات الوصفية والتعليقات")
heading(doc, "Context and the service", "السياق والخدمة", 2, number="1.2")
bipara(doc,
    "The scoped service is a synthetic university HR \u201cemployee personal file\u201d (DOCX + PDF) that must be "
    "released outside the HR trust boundary \u2014 for example, shared with an external auditor or another "
    "department. The processing purpose is data minimization before release: detect and remove direct and "
    "quasi-identifiers so the recipient receives only what they need.",
    "الخدمة المقصودة هي \u201cملف موظف\u201d جامعي اصطناعي في الموارد البشرية (DOCX + PDF) يجب إطلاقه خارج حدود ثقة "
    "الموارد البشرية \u2014 كأن يُشارَك مع مُدقّق خارجي أو قسم آخر. والغرض من المعالجة هو تقليل البيانات قبل "
    "الإطلاق: كشف المعرّفات المباشرة وشبه المباشرة وإزالتها كي لا يتلقّى المستلِم إلا ما يحتاجه.")
figure(doc, os.path.join(FIG, "m1_surfaces.png"),
       "Redaction scope \u2014 every surface where personal data can hide",
       "نطاق التنقيح \u2014 كل سطح يمكن أن تختبئ فيه البيانات الشخصية")
figure(doc, os.path.join(FIG, "m1_context.png"),
       "System context: only the redacted file crosses the trust boundary",
       "سياق النظام: لا يعبر حدَّ الثقة إلا الملف المُنقَّح")
heading(doc, "Scope \u2014 in and out", "النطاق — داخله وخارجه", 2, number="1.3")
table(doc,
      [("In scope", "داخل النطاق"), ("Out of scope (protected by other controls)", "خارج النطاق (بضوابط أخرى)")],
      [[("Detecting & removing PII in DOCX/PDF body, tables, headers/footers",
         "كشف وإزالة البيانات الشخصية في المتن والجداول والرؤوس/التذييلات"),
        ("Transport & endpoint security (TLS, who sent what, when)",
         "أمن النقل والأطراف (TLS، ومن أرسل ماذا ومتى)")],
       [("Hidden text, comments + comment-author",
         "النص المخفي والتعليقات واسم كاتب التعليق"),
        ("Access to the original file, ground truth, or internal network",
         "الوصول إلى الملف الأصلي أو المرجع أو الشبكة الداخلية")],
       [("PDF annotations and all metadata (core/app/custom/XMP; PDF Info)",
         "تعليقات PDF التوضيحية وكل البيانات الوصفية"),
        ("Scanned / image-only documents with no text layer (need OCR)",
         "المستندات الممسوحة ضوئيًا بلا طبقة نص (تحتاج OCR)")],
       [("Two honest metrics (residual disclosure + re-identification) + manual review",
         "مقياسان صادقان (التسرّب المتبقّي + إعادة التعرّف) + مراجعة يدوية"),
        ("Formal anonymization proofs (k-anonymity / l-diversity)",
         "براهين إخفاء الهوية الشكلية (k-anonymity / l-diversity)")],
       [("Bilingual (Arabic + English) and Jordan/international locales",
         "ثنائية اللغة (عربية + إنجليزية) ولغات/مناطق أردنية ودولية"),
        ("Real personal data of any kind (synthetic data only)",
         "أي بيانات شخصية حقيقية (بيانات اصطناعية فقط)")]],
      widths=[3.3, 3.3], font=8.4)
heading(doc, "Measurable success criteria", "معايير النجاح القابلة للقياس", 2, number="1.4")
bibullet(doc, [("Detection recall \u2265 95%", {"bold": True}), " across all planted entities; metadata/comment-author leaks = 0."],
         [("استدعاء الكشف \u2265 95%", {"bold": True, "cs": True, "rtl": True, "color": INK}), " لكل الكيانات المزروعة؛ وتسرّبات البيانات الوصفية/اسم الكاتب = صفر."])
bibullet(doc, [("Utility \u2265 95%", {"bold": True}), " of non-identifying words preserved (no wholesale over-redaction)."],
         [("منفعة \u2265 95%", {"bold": True, "cs": True, "rtl": True, "color": INK}), " من الكلمات غير المُعرِّفة محفوظة (دون تنقيح مفرط)."])
bibullet(doc, [("A measured drop in re-identification", {"bold": True}), " versus the baseline, reported honestly against a stated attacker directory."],
         [("انخفاض مقيس في إعادة التعرّف", {"bold": True, "cs": True, "rtl": True, "color": INK}), " مقارنةً بالأساس، مع إفصاح صادق إزاء دليل مُهاجِم مُعلَن."])
bibullet(doc, "Every residual miss listed, root-caused, and manually reviewed \u2014 no hidden failures.",
         "كل تسرّب متبقٍّ مُدرَج ومُحلَّل السبب ومُراجَع يدويًا \u2014 دون إخفاقات خفيّة.")

# ---------------------------------------------------------------- 2 stakeholders
heading(doc, "Stakeholders", "أصحاب المصلحة", 1, number="2")
bipara(doc, "The parties with an interest in the released document and their primary privacy concern:",
       "الأطراف المعنيّة بالمستند المُطلَق وأبرز شواغلها المتعلّقة بالخصوصية:")
table(doc,
      [("Stakeholder", "صاحب المصلحة"), ("Interest / need", "المصلحة / الحاجة"), ("Primary privacy concern", "أبرز شاغل خصوصية")],
      [[("Data subject (the employee)", "صاحب البيانات (الموظف)"),
        ("Their file is handled and shared responsibly", "التعامل مع ملفه ومشاركته بمسؤولية"),
        ("No name, contact, ID, address or sensitive context leaks", "عدم تسرّب الاسم أو الاتصال أو الهوية أو العنوان")],
       [("Document owner / HR (releasing org)", "مالك المستند / الموارد البشرية"),
        ("Share useful content lawfully and efficiently", "مشاركة محتوى مفيد بشكل قانوني وفعّال"),
        ("Accountability for disclosure; minimization duties", "المساءلة عن الإفشاء وواجب تقليل البيانات")],
       [("Recipient (external auditor / dept.)", "المستلِم (مُدقّق خارجي / قسم)"),
        ("Receive the useful, non-identifying content", "تلقّي المحتوى المفيد غير المُعرِّف"),
        ("Should not receive personal data they do not need", "ألّا يتلقّى بيانات شخصية لا يحتاجها")],
       [("Course instructor / evaluator", "مُدرّس المقرّر / المُقيّم"),
        ("Assess a reproducible, evidence-based solution", "تقييم حلّ قابل للتكرار ومبني على أدلّة"),
        ("Evidence is sanitized, synthetic, and honest", "أن تكون الأدلّة مُعقّمة واصطناعية وصادقة")],
       [("Development team (us)", "فريق التطوير (نحن)"),
        ("Build, test, document and defend the tool", "بناء الأداة واختبارها وتوثيقها والدفاع عنها"),
        ("Attributable work; no real data; declared AI use", "عمل قابل للعزو؛ بلا بيانات حقيقية؛ إفصاح عن الذكاء الاصطناعي")],
       [("Linkage adversary (threat actor)", "خصم الربط (جهة التهديد)"),
        ("Re-identify the person from the released file", "إعادة التعرّف على الشخص من الملف المُطلَق"),
        ("Modelled explicitly \u2014 the attacker we design against", "مُنمذَج صراحةً \u2014 المُهاجِم الذي نصمّم ضدّه")],
       [("Regulator (Jordan PDPL / MoDEE)", "الجهة المنظِّمة (قانون حماية البيانات الأردني)"),
        ("Lawful processing of personal data", "المعالجة القانونية للبيانات الشخصية"),
        ("Minimization and purpose limitation (context)", "تقليل البيانات وتحديد الغرض (كسياق)")]],
      widths=[1.75, 2.35, 2.5], font=8.2)

# ---------------------------------------------------------------- 3 objectives
figure(doc, os.path.join(FIG, "m1_stakeholders.png"),
       "Stakeholder map — who has an interest in the released document",
       "خريطة أصحاب المصلحة — من له مصلحة في المستند المُطلَق")
heading(doc, "Objectives", "الأهداف", 1, number="3")
bipara(doc, "The project objectives are concrete and measurable; each maps to a course learning objective.",
       "أهداف المشروع محدّدة وقابلة للقياس، ويرتبط كلٌّ منها بهدف تعلّمي في المقرّر.")
table(doc,
      [("ID", "المعرّف"), ("Objective", "الهدف"), ("Measure / target", "المقياس / الغاية")],
      [["O1", ("Detect PII on every document surface", "كشف البيانات الشخصية على كل سطح"), ("Micro-recall \u2265 95% vs. ground truth", "استدعاء \u2265 95% مقابل المرجع")],
       ["O2", ("Close the metadata & comment-author channel", "إغلاق قناة البيانات الوصفية واسم الكاتب"), ("Metadata/comment-author leaks = 0", "تسرّبات = صفر")],
       ["O3", ("Preserve the document\u2019s legitimate content", "الحفاظ على محتوى المستند المشروع"), ("Utility \u2265 95% of non-sensitive words", "منفعة \u2265 95% من الكلمات غير الحسّاسة")],
       ["O4", ("Reduce and measure re-identification", "تقليل إعادة التعرّف وقياسها"), ("Report re-id rate & anonymity-set k", "تقرير نسبة إعادة التعرّف و k")],
       ["O5", ("Cover Arabic + English & Jordan/intl locales", "تغطية العربية والإنجليزية والمناطق الأردنية/الدولية"), ("Arabic PII & +962/intl phones redacted", "تنقيح العربية وهواتف +962/الدولية")],
       ["O6", ("Be reproducible, tested and honest", "قابلية التكرار والاختبار والصدق"), ("One-command rerun; tests; stated residual risk", "تشغيل بأمر واحد؛ اختبارات؛ ذكر المخاطر")]],
      widths=[0.5, 3.3, 2.8], font=8.4)

# ---------------------------------------------------------------- 4 requirements
heading(doc, "Requirements", "المتطلّبات", 1, number="4")
bipara(doc,
    "Eight functional (FR) and three non-functional (NFR) requirements. Each is traced to a risk, a control, "
    "a test, and an evidence file \u2014 the evidence chain below \u2014 using the same test conditions before and "
    "after protection.",
    "ثمانية متطلّبات وظيفية (FR) وثلاثة غير وظيفية (NFR). ويُربط كلٌّ منها بخطر وضابط واختبار وملف دليل \u2014 "
    "سلسلة الأدلّة أدناه \u2014 بنفس شروط الاختبار قبل الحماية وبعدها.")
figure(doc, os.path.join(FIG, "m1_evidence.png"),
       "The evidence chain: requirement \u2192 risk \u2192 control \u2192 test \u2192 evidence",
       "سلسلة الأدلّة: المتطلّب ثم الخطر ثم الضابط ثم الاختبار ثم الدليل")
table(doc,
      [("ID", "المعرّف"), ("Requirement", "المتطلّب"), ("Pri.", "الأولوية"), ("Acceptance criterion", "معيار القبول")],
      [["FR-1", ("Remove person names on every surface", "إزالة أسماء الأشخاص على كل سطح"), ("Must", "إلزامي"), ("PERSON recall \u2265 95%; 0 names anywhere", "استدعاء \u2265 95%؛ صفر أسماء")],
       ["FR-2", ("Remove phone numbers incl. Jordan/intl", "إزالة الهواتف شاملةً الأردنية/الدولية"), ("Must", "إلزامي"), ("+962, 07x and intl formats redacted", "تنقيح +962 و07x والصيغ الدولية")],
       ["FR-3", ("Remove e-mail addresses", "إزالة عناوين البريد الإلكتروني"), ("Must", "إلزامي"), ("EMAIL recall = 100%", "استدعاء البريد = 100%")],
       ["FR-4", ("Remove postal addresses", "إزالة العناوين البريدية"), ("Must", "إلزامي"), ("Street/city removed; residue quantified", "إزالة الشارع/المدينة؛ قياس المتبقّي")],
       ["FR-5", ("Remove national ID / SSN", "إزالة الرقم الوطني"), ("Must", "إلزامي"), ("ID recall = 100%", "استدعاء الهوية = 100%")],
       ["FR-6", ("Strip all metadata + comment authors", "إزالة كل البيانات الوصفية + أسماء الكُتّاب"), ("Must", "إلزامي"), ("Metadata & comment-author leaks = 0", "تسرّبات = صفر")],
       ["FR-7", ("Reach hidden / comment / annotation surfaces", "بلوغ الأسطح المخفية والتعليقات"), ("Must", "إلزامي"), ("0 names in hidden/comments/annotations", "صفر أسماء في المخفي/التعليقات")],
       ["FR-8", ("Preserve non-personal content", "الحفاظ على المحتوى غير الشخصي"), ("Must", "إلزامي"), ("Decoy survives; utility \u2265 95%", "بقاء الطُّعم؛ منفعة \u2265 95%")],
       ["NFR-1", ("Reproducible pipeline", "خط معالجة قابل للتكرار"), ("Must", "إلزامي"), ("One command regenerates all evidence", "أمر واحد يعيد توليد الأدلّة")],
       ["NFR-2", ("Bilingual (Arabic + English)", "ثنائية اللغة (عربية + إنجليزية)"), ("Must", "إلزامي"), ("Arabic PII detected & redacted", "كشف وتنقيح العربية")],
       ["NFR-3", ("Measure re-identification, not just strings", "قياس إعادة التعرّف لا السلاسل فقط"), ("Should", "مُستحسن"), ("Anonymity-set k & re-id rate reported", "تقرير k ونسبة إعادة التعرّف")]],
      widths=[0.6, 2.85, 0.55, 2.6], font=8.2)

# ---------------------------------------------------------------- 5 data inventory
heading(doc, "Data inventory", "جرد البيانات", 1, number="5")
bipara(doc,
    "Every field the tool plants, detects, or inspects, with its identification role and sensitivity. Labels "
    "may overlap: a direct identifier names the person alone; a quasi-identifier re-identifies by linkage; a "
    "sensitive attribute is protected context.",
    "كل حقل تزرعه الأداة أو تكشفه أو تفحصه، مع دوره التعريفي ودرجة حساسيته. وقد تتداخل التصنيفات: المعرّف "
    "المباشر يُسمّي الشخص وحده؛ وشبه المباشر يُعيد التعرّف بالربط؛ والسمة الحسّاسة سياقٌ محميّ.")
figure(doc, os.path.join(FIG, "m1_classify.png"),
       "Data classification by identification role and sensitivity",
       "تصنيف البيانات بحسب الدور التعريفي ودرجة الحساسية")
table(doc,
      [("Field / entity", "الحقل / الكيان"), ("Role", "الدور"), ("Sensitivity", "الحساسية"), ("Where it appears", "أين يظهر")],
      [[("Full name (PERSON) \u2014 Latin & Arabic", "الاسم الكامل \u2014 لاتيني وعربي"), ("Direct", "مباشر"), ("High", "عالية"), ("Body, header/footer, comments, hidden, metadata", "المتن والرؤوس والتعليقات والمخفي والبيانات الوصفية")],
       [("Phone number", "رقم الهاتف"), ("Direct", "مباشر"), ("High", "عالية"), ("Body, hidden text, header/footer", "المتن والنص المخفي والرؤوس/التذييلات")],
       [("E-mail address", "البريد الإلكتروني"), ("Direct", "مباشر"), ("High", "عالية"), ("Body, metadata (keywords)", "المتن والبيانات الوصفية (الكلمات المفتاحية)")],
       [("National ID / SSN", "الرقم الوطني"), ("Direct", "مباشر"), ("High", "عالية جدًا"), ("Body, hidden text", "المتن والنص المخفي")],
       [("Street address", "عنوان الشارع"), ("Direct / quasi", "مباشر / شبه"), ("High", "عالية"), ("Body, hidden text", "المتن والنص المخفي")],
       [("ZIP / postal code", "الرمز البريدي"), ("Quasi", "شبه مباشر"), ("Medium", "متوسطة"), ("Inside the address line", "ضمن سطر العنوان")],
       [("City / district", "المدينة / الحي"), ("Quasi", "شبه مباشر"), ("Medium", "متوسطة"), ("Body, address", "المتن والعنوان")],
       [("Author, title, keywords, last-modified-by", "الكاتب والعنوان والكلمات وآخر مُعدِّل"), ("Direct", "مباشر"), ("High", "عالية"), ("DOCX core.xml; PDF Info dict", "core.xml في DOCX؛ Info في PDF")],
       [("Comment author / initials", "اسم كاتب التعليق / الأحرف"), ("Direct", "مباشر"), ("High", "عالية"), ("word/comments.xml (missed by metadata-only strip)", "word/comments.xml")],
       [("Document subject (\u201cEmployee file\u201d)", "موضوع المستند (\u201cملف موظف\u201d)"), ("Sensitive", "حسّاس"), ("Medium", "متوسطة"), ("core dc:subject; PDF /Subject", "dc:subject؛ /Subject")],
       [("Decoy mailbox (hr@company.com)", "طُعم بريد (hr@company.com)"), ("Non-personal", "غير شخصي"), ("None", "لا شيء"), ("Body \u2014 must survive", "المتن \u2014 يجب أن يبقى")],
       [("Free-text notes", "ملاحظات نصّية حرّة"), ("Utility", "منفعة"), ("Low", "منخفضة"), ("Body \u2014 preserved, measured as utility", "المتن \u2014 محفوظة وتُقاس كمنفعة")]],
      widths=[2.3, 1.2, 0.95, 2.15], font=8.0)
figure(doc, os.path.join(FIG, "m1_anatomy.png"),
       "The same identifiers are copied across file-format surfaces a reader never opens",
       "المعرّفات نفسها منسوخة عبر أسطح صيغة الملف التي لا يفتحها القارئ")
callout(doc, "Key point.", "نقطة أساسية.",
        "Removing direct identifiers alone is not anonymity: surviving ZIP + district quasi-identifiers still "
        "re-identify individuals by linkage. Quasi-identifier control (postcode generalization) is a named "
        "requirement, not an afterthought.",
        "إزالة المعرّفات المباشرة وحدها ليست إخفاءً للهوية: فالمعرّفات شبه المباشرة الباقية (الرمز البريدي + "
        "الحي) تُعيد التعرّف بالربط. ولذلك فإن ضبط المعرّفات شبه المباشرة (تعميم الرمز البريدي) متطلّبٌ مُعلَن لا "
        "أمرٌ ثانوي.", fill="FEF9C3", bar="CA8A04")

# ---------------------------------------------------------------- 6 risks
figure(doc, os.path.join(FIG, "m1_linkage.png"),
       "Re-identification by linkage — surviving quasi-identifiers re-attach a name",
       "إعادة التعرّف بالربط — المعرّفات شبه المباشرة الباقية تُعيد ربط الاسم")
heading(doc, "Privacy risks", "مخاطر الخصوصية", 1, number="6")
bipara(doc,
    "The principal disclosure risks for releasing a redacted document. Likelihood (L) and Impact (I) are "
    "pre-control (L/M/H). The full ranked register is maintained in the repository; the top risks are:",
    "أبرز مخاطر الإفشاء عند إطلاق مستند مُنقَّح. الاحتمال (L) والأثر (I) قبل الضبط (منخفض/متوسط/عالٍ). "
    "ويُحفَظ السجلّ الكامل المُرتَّب في المستودع؛ وأبرز المخاطر هي:")
table(doc,
      [("ID", "المعرّف"), ("Disclosure risk", "خطر الإفشاء"), ("L", "L"), ("I", "I"), ("Planned control", "الضابط المخطّط")],
      [["R1", ("Person name survives in the body", "بقاء اسم الشخص في المتن"), "H", "H", ("NER + document-consistent scrub; manual review", "تمييز الكيانات + تنقية متّسقة؛ مراجعة يدوية")],
       ["R2", ("PII in document metadata", "بيانات شخصية في البيانات الوصفية"), "H", "H", ("Clear DOCX core properties + PDF Info dict", "مسح خصائص DOCX و Info في PDF")],
       ["R3", ("Person name in comment-author attribute", "اسم الشخص في خاصية كاتب التعليق"), "H", "H", ("Clear comment author & initials", "مسح اسم الكاتب والأحرف")],
       ["R4", ("PII in hidden / invisible white text", "بيانات في النص المخفي/الأبيض"), "M", "H", ("Redact hidden runs; rebuild PDF text", "تنقيح المقاطع المخفية؛ إعادة بناء نص PDF")],
       ["R6", ("Intl / Jordanian phone not matched", "عدم مطابقة هاتف دولي/أردني"), "H", "H", ("Jordan + international phone recognizers", "مُميّزات هواتف أردنية ودولية")],
       ["R7", ("Arabic-script PII missed by English NER", "فوات العربية على التمييز الإنجليزي"), "H", "H", ("Dedicated Arabic recognizer + extraction", "مُميّز عربي مخصّص + استخراج")],
       ["R9", ("Quasi-identifier (ZIP/district) survives", "بقاء معرّف شبه مباشر (رمز/حي)"), "M", "M", ("Address regex; generalization (future)", "تعابير العنوان؛ تعميم (لاحقًا)")],
       ["R10", ("Re-identification by linkage of residuals", "إعادة تعرّف بربط المتبقّيات"), "M", "H", ("Executed red-team attack; suppression (future)", "هجوم تقييم؛ إخفاء (لاحقًا)")]],
      widths=[0.5, 2.85, 0.33, 0.33, 2.59], font=8.1)

# ---------------------------------------------------------------- 7 resources
figure(doc, os.path.join(FIG, "m1_riskmatrix.png"),
       "Risk heat map — likelihood × impact for the main disclosure risks",
       "خريطة حرارة المخاطر — الاحتمال × الأثر لأبرز مخاطر الإفشاء")
heading(doc, "Resources and feasibility", "الموارد والجدوى", 1, number="7")
heading(doc, "Tools & environment (all local, open-source, free)", "الأدوات والبيئة (محلّية ومفتوحة ومجّانية)", 2, number="7.1")
table(doc,
      [("Resource", "المورد"), ("Choice", "الخيار"), ("Role", "الدور")],
      [[("Language / runtime", "اللغة / بيئة التشغيل"), ("Python 3.14 (CPU-only laptop)", "Python 3.14 (حاسوب بالمعالج فقط)"), ("All processing \u2014 runs locally in minutes", "كل المعالجة \u2014 محلّيًا في دقائق")],
       [("PII detection", "كشف البيانات الشخصية"), ("Microsoft Presidio (Analyzer + Anonymizer)", "Microsoft Presidio"), ("Recognizer framework; detect & replace", "إطار المُميّزات؛ الكشف والاستبدال")],
       [("NLP model", "نموذج اللغة"), ("spaCy en_core_web_lg", "spaCy en_core_web_lg"), ("PERSON / LOCATION NER", "تمييز الأشخاص والمواقع")],
       [("Document I/O", "إدخال/إخراج المستندات"), ("python-docx, pypdf, reportlab", "python-docx, pypdf, reportlab"), ("Read/write DOCX & PDF every surface", "قراءة/كتابة كل الأسطح")],
       [("Arabic support", "دعم العربية"), ("arabic-reshaper, python-bidi", "arabic-reshaper, python-bidi"), ("Shape & extract Arabic script", "تشكيل واستخراج الخط العربي")],
       [("Version control", "إدارة الإصدارات"), ("git + GitHub (branches, PRs)", "git + GitHub"), ("History, review, attributable work", "السجلّ والمراجعة وعزو العمل")],
       [("Data", "البيانات"), ("Synthetic generator (deterministic)", "مولّد اصطناعي (حتمي)"), ("20+ individuals \u2192 40 documents; no real PII", "أكثر من 20 فردًا \u2190 40 مستندًا")]],
      widths=[1.5, 2.4, 2.7], font=8.2)
heading(doc, "Feasibility", "الجدوى", 2, number="7.2")
bibullet(doc, [("Technical: proven. ", {"bold": True}), "An end-to-end prototype already runs \u2014 feasibility is demonstrated, not assumed."],
         [("تقنيًا: مُثبَت. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "يعمل نموذج أوّلي متكامل بالفعل \u2014 الجدوى مُبرهَنة لا مُفترَضة."])
bibullet(doc, [("Data: low-risk. ", {"bold": True}), "100% synthetic & deterministic, so results are reproducible and the lab rule is satisfied."],
         [("البيانات: منخفضة المخاطر. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "اصطناعية بالكامل وحتمية، فالنتائج قابلة للتكرار وقاعدة المختبر مُستوفاة."])
bibullet(doc, [("Resourcing: within reach. ", {"bold": True}), "Free, open-source tools on a standard laptop; no GPU or paid service."],
         [("الموارد: متاحة. ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "أدوات مجّانية مفتوحة على حاسوب عادي؛ دون معالج رسومات أو خدمة مدفوعة."])
bibullet(doc, [("Main technical risk: ", {"bold": True}), "NER accuracy and locale coverage \u2014 mitigated by regex recognizers, an allow-list, and manual review."],
         [("أبرز خطر تقني: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "دقّة التمييز وتغطية اللغات \u2014 يُخفَّف بمُميّزات التعابير وقائمة السماح والمراجعة اليدوية."])

# ---------------------------------------------------------------- 8 charter
heading(doc, "Team charter and schedule", "ميثاق الفريق والجدول الزمني", 1, number="8")
heading(doc, "Roles & responsibilities", "الأدوار والمسؤوليات", 2, number="8.1")
table(doc,
      [("Role", "الدور"), ("Member", "العضو"), ("Responsible for", "المسؤول عن")],
      [[("Team lead / PM", "قائد الفريق"), "[name, ID]", ("Planning, milestone packaging, M1-feedback, defense", "التخطيط وتجهيز المحطات ومتابعة الملاحظات والدفاع")],
       [("Detection engineer", "مهندس الكشف"), "[name, ID]", ("Recognizers & pipeline; Arabic/locale coverage", "المُميّزات وخط المعالجة؛ تغطية العربية/المناطق")],
       [("Evaluation & red-team engineer", "مهندس التقييم والهجوم"), "[name, ID]", ("Residual-disclosure & re-identification harnesses", "أدوات التسرّب وإعادة التعرّف")],
       [("Docs, legal & ethics lead", "مسؤول التوثيق والقانون والأخلاق"), "[name, ID]", ("Data dictionary, threat model, PDPL, AI declaration", "قاموس البيانات ونموذج التهديد والقانون والإفصاح")]],
      widths=[1.9, 1.5, 3.2], font=8.3)
bipara(doc, "A team of 3 may merge the detection and evaluation roles; every member owns a reviewable share of "
            "code or writing and can explain it in the oral defense.",
       "يمكن لفريق من 3 أفراد دمج دورَي الكشف والتقييم؛ ويملك كل عضو حصّة قابلة للمراجعة من الشيفرة أو الكتابة "
       "ويستطيع شرحها في الدفاع الشفوي.")
heading(doc, "Ground rules & ways of working", "قواعد العمل وأساليبه", 2, number="8.2")
bibullet(doc, [("Communication: ", {"bold": True}), "one weekly meeting + an async channel; the git repository is the single source of truth."],
         [("التواصل: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "اجتماع أسبوعي + قناة غير متزامنة؛ ومستودع git هو المصدر الوحيد للحقيقة."])
bibullet(doc, [("Decisions: ", {"bold": True}), "by consensus; the team lead breaks ties and records the decision."],
         [("القرارات: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "بالتوافق؛ ويحسم القائد التعادل ويوثّق القرار."])
bibullet(doc, [("Version control: ", {"bold": True}), "feature branches + pull-request review before merge; no secrets or real data committed."],
         [("إدارة الإصدارات: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "فروع للميزات + مراجعة طلب الدمج قبل الدمج؛ بلا أسرار أو بيانات حقيقية."])
bibullet(doc, [("Definition of done: ", {"bold": True}), "code has a test, numbers have an evidence file, claims state their residual risk."],
         [("تعريف الإنجاز: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "لكل شيفرة اختبار، ولكل رقم ملف دليل، ولكل ادّعاء مخاطره المتبقّية."])
bibullet(doc, [("Integrity: ", {"bold": True}), "AI assistance is declared (tool, purpose, prompt summary); reused material is cited."],
         [("النزاهة: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "يُفصَح عن مساعدة الذكاء الاصطناعي (الأداة والغرض وملخّص الطلب)؛ ويُستشهَد بالمواد المُعاد استخدامها."])
heading(doc, "Schedule & milestones", "الجدول الزمني والمحطات", 2, number="8.3")
figure(doc, os.path.join(FIG, "m1_schedule.png"),
       "Project schedule across the four milestones (indicative weeks)",
       "الجدول الزمني للمشروع عبر المحطّات الأربع (أسابيع تقريبية)")
table(doc,
      [("Milestone", "المحطّة"), ("Week", "الأسبوع"), ("Key deliverables", "أبرز المُخرجات"), ("Owner", "المسؤول")],
      [[("M1 \u2014 Proposal & requirements", "M1 \u2014 المقترح والمتطلّبات"), "Week 4", ("Scope, stakeholders, objectives, 11 requirements, data inventory, risks, charter", "النطاق وأصحاب المصلحة والأهداف والمتطلّبات والجرد والمخاطر والميثاق"), ("Lead", "القائد")],
       [("M2 \u2014 Design & prototype", "M2 \u2014 التصميم والنموذج"), "Week 7", ("Architecture, privacy model, alternatives, prototype, req\u2192test map, M1-feedback", "البنية والنموذج والبدائل والنموذج الأوّلي وخريطة الاختبارات"), ("Detection", "الكشف")],
       [("M3 \u2014 Implementation & validation", "M3 \u2014 التنفيذ والتحقّق"), "Week 12", ("Full build, test results, privacy\u2013utility, residual risk, technical guide", "البناء الكامل والنتائج والمفاضلة والمخاطر والدليل الفني"), ("Eval.", "التقييم")],
       [("M4 \u2014 Final delivery & demo", "M4 \u2014 التسليم النهائي"), "Week 15", ("Final artifact + README, report, demo, evidence map, reflection", "المُنتَج النهائي والتقرير والعرض وخريطة الأدلّة والتأمّل"), ("All", "الجميع")]],
      widths=[1.85, 0.85, 3.0, 0.9], font=8.0)
bipara(doc, "Privacy models taught after Week 7 (e.g. k-anonymity / generalization) are planned at M2 and "
            "completed by M3, per the course brief\u2019s evidence-chain note.",
       "نماذج الخصوصية التي تُدرَّس بعد الأسبوع السابع (مثل k-anonymity/التعميم) يُخطَّط لها في M2 وتُنجَز بحلول "
       "M3، وفق ملاحظة سلسلة الأدلّة في توصيف المقرّر.")

# ---------------------------------------------------------------- 9 methodology
heading(doc, "Methodology", "المنهجية", 1, number="9")
bipara(doc,
    "We follow the course\u2019s seven-phase method: 1 Define the service & success criteria \u2192 2 Map data, "
    "roles & trust boundaries \u2192 3 Assess attacker knowledge & rank risks \u2192 4 Design controls & compare "
    "alternatives \u2192 5 Build the prototype \u2192 6 Verify with allowed/denied/boundary/failure/privacy/utility "
    "tests \u2192 7 Improve by retesting and reassessing residual risk. M1 covers phases 1\u20133 and initiates phase 4.",
    "نتّبع منهج المقرّر ذا المراحل السبع: 1 تعريف الخدمة ومعايير النجاح \u2190 2 تخطيط البيانات والأدوار وحدود "
    "الثقة \u2190 3 تقييم معرفة المُهاجِم وترتيب المخاطر \u2190 4 تصميم الضوابط ومقارنة البدائل \u2190 5 بناء النموذج "
    "الأوّلي \u2190 6 التحقّق باختبارات المسموح/الممنوع/الحدود/الفشل/الخصوصية/المنفعة \u2190 7 التحسين بإعادة الاختبار "
    "وإعادة تقييم المخاطر. وتغطّي M1 المراحل 1\u20133 وتبدأ المرحلة 4.")

# ---------------------------------------------------------------- 10 legal
figure(doc, os.path.join(FIG, "m1_methodology.png"),
       "The seven-phase method; M1 covers phases 1–3 and starts phase 4",
       "المنهجية ذات المراحل السبع؛ تغطّي M1 المراحل 1–3 وتبدأ المرحلة 4")
heading(doc, "Legal, ethical and AI-use note", "ملاحظة قانونية وأخلاقية وإفصاح عن الذكاء الاصطناعي", 1, number="10")
bibullet(doc, [("Legal context (not a compliance claim): ", {"bold": True}), "Jordan\u2019s Personal Data Protection Law No. 24 of 2023 \u2014 lawful processing, purpose limitation and data minimization (Articles 4\u20138) \u2014 motivate the controls; a full mapping is developed through M2\u2013M3."],
         [("السياق القانوني (ليس ادّعاء امتثال): ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "قانون حماية البيانات الشخصية الأردني رقم 24 لسنة 2023 \u2014 المعالجة المشروعة وتحديد الغرض وتقليل البيانات (المواد 4\u20138) \u2014 يوجّه الضوابط؛ ويُطوَّر الربط الكامل عبر M2\u2013M3."])
bibullet(doc, [("Lab rule: ", {"bold": True}), "synthetic data by default; re-identification experiments are fictional and evidence is sanitized."],
         [("قاعدة المختبر: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "بيانات اصطناعية افتراضيًا؛ وتجارب إعادة التعرّف خيالية والأدلّة مُعقّمة."])
bibullet(doc, [("AI-use declaration: ", {"bold": True}), "AI assistance (Claude, via Claude Code) is used for code cleanup, locale-aware detection, the harnesses, and documentation; the concept and dataset design are the team\u2019s own."],
         [("إفصاح عن الذكاء الاصطناعي: ", {"bold": True, "cs": True, "rtl": True, "color": INK}), "استُخدِمت مساعدة الذكاء الاصطناعي (Claude عبر Claude Code) في تنظيف الشيفرة والكشف المراعي للمنطقة والأدوات والتوثيق؛ أمّا الفكرة وتصميم البيانات فمن عمل الفريق."])

# ---------------------------------------------------------------- 11 refs
heading(doc, "References", "المراجع", 1, number="11")
for en, ar in [
    ("CSE331 Confidentiality and Information Privacy \u2014 syllabus and instructor Project Pack.", "CSE331 \u2014 خطة المقرّر وحزمة المشروع."),
    ("NIST SP 800-188, De-Identifying Government Datasets.", "NIST SP 800-188، إزالة تعريف مجموعات البيانات الحكومية."),
    ("Microsoft Presidio \u2014 PII detection and anonymization framework.", "Microsoft Presidio \u2014 إطار كشف البيانات الشخصية وإخفائها."),
    ("spaCy \u2014 industrial-strength NLP; en_core_web_lg model.", "spaCy \u2014 معالجة لغة طبيعية؛ نموذج en_core_web_lg."),
    ("Jordan, Personal Data Protection Law No. 24 of 2023 (MoDEE); Articles 2, 4\u20138, 13\u201315, 20. Checked 27 Oct 2026.", "الأردن، قانون حماية البيانات الشخصية رقم 24 لسنة 2023؛ المواد 2 و4\u20138 و13\u201315 و20."),
    ("ARX Data Anonymization Tool \u2014 k-anonymity / l-diversity reference.", "أداة ARX \u2014 مرجع k-anonymity / l-diversity."),
]:
    bibullet(doc, en, ar)

doc.save(OUT)
print("SAVED", OUT)
