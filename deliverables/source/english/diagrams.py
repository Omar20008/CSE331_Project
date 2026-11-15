# -*- coding: utf-8 -*-
"""ENGLISH-ONLY illustrative diagrams for the CSE331 Project 09 milestone documents.

This is the English-only counterpart of ../diagrams.py: the Arabic-label helper
TA() is a no-op, so every figure renders with English text only. The Arabic
font-loading and shaping machinery below is retained unused for parity with the
bilingual source; it draws nothing.

Arabic shaping is handled ROBUSTLY. matplotlib 3.11+ shapes Arabic natively
(HarfBuzz), so the letters must be passed RAW in logical order; older matplotlib
(or a build without native shaping) does NOT shape, and needs arabic-reshaper +
python-bidi to pre-connect the glyphs. Passing reshaped text to a native-shaping
matplotlib double-processes and DISCONNECTS the letters. We therefore *probe* the
renderer once at import and pick the correct path automatically, so the figures
render with correctly connected Arabic on any environment. The Arabic font is
Amiri (connects well and includes Latin glyphs); Latin text uses Arial.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
from matplotlib import font_manager as fm
from matplotlib.backends.backend_agg import FigureCanvasAgg

FD = r"C:\Windows\Fonts"
_paths = {"latr": "arial.ttf", "latb": "arialbd.ttf",
          "arr": "Amiri-Regular.ttf", "arb": "Amiri-Bold.ttf"}
for p in _paths.values():
    fm.fontManager.addfont(os.path.join(FD, p))
LATR = fm.FontProperties(fname=os.path.join(FD, _paths["latr"]))
LATB = fm.FontProperties(fname=os.path.join(FD, _paths["latb"]))
ARR  = fm.FontProperties(fname=os.path.join(FD, _paths["arr"]))
ARB  = fm.FontProperties(fname=os.path.join(FD, _paths["arb"]))
plt.rcParams["font.family"] = "Arial"

# --------------------------------------------------------- robust Arabic shaping
def _probe_native_shaping():
    """True if matplotlib joins Arabic letters on its own (then pass raw text)."""
    def _render(s):
        fig = plt.figure(figsize=(1.4, 0.5), dpi=80)
        fig.text(0.5, 0.5, s, fontproperties=ARR, fontsize=24, ha="center", va="center")
        cv = FigureCanvasAgg(fig); cv.draw()
        a = np.asarray(cv.buffer_rgba())[..., 0].copy()
        plt.close(fig)
        return a
    try:
        # two meems join when shaped; a ZWNJ forces the isolated (unjoined) forms
        return not np.array_equal(_render("\u0645\u0645"), _render("\u0645\u200c\u0645"))
    except Exception:
        return True   # assume a modern, shaping-capable matplotlib

NATIVE_SHAPING = _probe_native_shaping()
if not NATIVE_SHAPING:
    import arabic_reshaper
    from bidi.algorithm import get_display

def _ar(t):
    """Arabic text ready for the active renderer."""
    if NATIVE_SHAPING:
        return t
    return get_display(arabic_reshaper.reshape(t))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)

INK, MUTED, ARCLR = "#1f2937", "#64748b", "#0f766e"
KIND = {
    "neutral": ("#eef2f7", "#94a3b8"), "process": ("#dbeafe", "#2563eb"),
    "danger":  ("#fee2e2", "#dc2626"), "safe":    ("#dcfce7", "#16a34a"),
    "gt":      ("#fef9c3", "#ca8a04"), "release": ("#f3e8ff", "#7c3aed"),
    "teal":    ("#ccfbf1", "#0d9488"), "head":    ("#1e293b", "#1e293b"),
}

def _tr(ax, data): return ax.transData if data else ax.transAxes
def TL(ax, x, y, s, size=11, bold=True, color=INK, ha="center", va="center", rot=0, data=True, z=3):
    ax.text(x, y, s, fontproperties=(LATB if bold else LATR), fontsize=size,
            color=color, ha=ha, va=va, rotation=rot, transform=_tr(ax, data), zorder=z)
def TA(ax, x, y, s, size=10, bold=False, color=ARCLR, ha="center", va="center", rot=0, data=True, z=3):
    # English-only build: Arabic labels are intentionally not drawn.
    return

def box(ax, cx, cy, w, h, en, ar, kind="neutral", enfs=11, arfs=9.5, bold=True):
    fc, ec = KIND[kind]
    tc = "white" if kind == "head" else INK
    ac = "#cbd5e1" if kind == "head" else ARCLR
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.09", fc=fc, ec=ec, lw=1.6, zorder=2))
    # English-only: the single English label is centred vertically in the box.
    if en: TL(ax, cx, cy, en, size=enfs, bold=bold, color=tc)

def arrow(ax, p1, p2, color=None, lw=1.8, ls="-", rad=0.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=15,
                 color=color or MUTED, lw=lw, linestyle=ls,
                 connectionstyle=f"arc3,rad={rad}", zorder=1))

def title(ax, en, ar):
    TL(ax, 0.5, 0.975, en, size=15, bold=True, color=INK, va="top", data=False)
    TA(ax, 0.5, 0.925, ar, size=12, bold=True, color=ARCLR, va="top", data=False)

def caption(ax, en, ar, y=0.045):
    ax.text(0.5, y, en, transform=ax.transAxes, ha="center", va="bottom",
            fontproperties=LATR, fontsize=8.8, color=MUTED, style="italic")
    TA(ax, 0.5, y-0.05, ar, size=8.6, color=MUTED, va="bottom", data=False)

def base(w, h, lim=100):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.axis("off")
    return fig, ax

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig); print("wrote", name)

# ============================================================= M1-0 black box (NEW)
def fig_blackbox():
    fig, ax = base(10.6, 5.4)
    title(ax, "A black box is not redaction \u2014 the value stays in the file",
          "الصندوق الأسود ليس تنقيحًا \u2014 القيمة تبقى داخل الملف")
    # left: the rendered page
    px, pw = 17, 24
    ax.add_patch(FancyBboxPatch((px-pw/2, 30), pw, 44, boxstyle="round,pad=0.02,rounding_size=0.06",
                 fc="white", ec="#94a3b8", lw=1.7, zorder=2))
    for i in range(6):
        y = 68 - i*6.2
        wln = pw-10 if i not in (0,) else pw-16
        ax.add_patch(Rectangle((px-pw/2+5, y), wln, 2.0, fc="#e2e8f0", ec="none", zorder=3))
    # the black box drawn over the "name" line
    ax.add_patch(Rectangle((px-pw/2+5, 61.5-0.4), pw-14, 3.0, fc="#111827", ec="none", zorder=4))
    TL(ax, px, 25.5, "Rendered page", size=9.2)
    TA(ax, px, 21.5, "الصفحة المعروضة", size=8.6, color=MUTED)
    # center arrow
    arrow(ax, (px+pw/2+1, 52), (px+pw/2+11, 52), color=INK, lw=2.2)
    TL(ax, px+pw/2+6, 57, "extract /", size=7.6, bold=False, color=MUTED)
    TL(ax, px+pw/2+6, 53.5, "copy-paste", size=7.6, bold=False, color=MUTED)
    # right: channels that still expose the value
    cx = 68
    chans = [("Text layer", "طبقة النص", "Name:  Omar Al-Masri"),
             ("File metadata", "البيانات الوصفية", "Author:  Omar Al-Masri"),
             ("Comment author", "كاتب التعليق", "by:  Omar Al-Masri")]
    for i, (en, a, leak) in enumerate(chans):
        y = 74 - i*21
        ax.add_patch(FancyBboxPatch((cx-18, y-8), 50, 16, boxstyle="round,pad=0.02,rounding_size=0.07",
                     fc="#fee2e2", ec="#dc2626", lw=1.5, zorder=2))
        TL(ax, cx-14, y+3.4, en, size=9.3, ha="left")
        TA(ax, cx+28, y+3.4, a, size=8.4, color="#b91c1c", ha="right")
        TL(ax, cx-14, y-4, leak, size=8.8, bold=False, color="#991b1b", ha="left")
        arrow(ax, (px+pw/2+11, 52), (cx-18, y), color="#ef9a9a", lw=1.2, rad=0.10)
    caption(ax, "The box changes pixels, not bytes: copy-paste, \u201csave as text\u201d, or a metadata viewer recovers the name on three channels a reader never sees.",
            "الصندوق يُغيّر البكسلات لا البايتات: النسخ أو \u201cالحفظ كنص\u201d أو عارض البيانات الوصفية يستعيد الاسم من ثلاث قنوات لا يراها القارئ.", y=0.04)
    save(fig, "m1_blackbox.png")

# ============================================================= M1-1 surfaces
def fig_surfaces():
    fig, ax = base(9.6, 6.4)
    title(ax, "Where personal data hides \u2014 the full redaction scope",
          "أين تختبئ البيانات الشخصية \u2014 نطاق التنقيح الكامل")
    hx, hy, hw, hh = 50, 50, 29, 16
    fc, ec = KIND["head"]
    ax.add_patch(FancyBboxPatch((hx-hw/2, hy-hh/2), hw, hh,
                 boxstyle="round,pad=0.02,rounding_size=0.09", fc=fc, ec=ec, lw=1.6, zorder=2))
    TL(ax, hx, hy+4, "HR employee file", size=12.5, color="white")
    TA(ax, hx, hy-0.2, "ملف موظف الموارد البشرية", size=10, color="#cbd5e1")
    TL(ax, hx, hy-4.6, "DOCX  +  PDF", size=9, bold=False, color="#94a3b8")
    surfaces = [
        (16, 77, "Body & tables", "المتن والجداول", "process"),
        (50, 77, "Headers / footers", "الرؤوس والتذييلات", "process"),
        (84, 77, "Hidden text (white/vanish)", "نص مخفي (أبيض)", "danger"),
        (12, 20, "Comments + author", "التعليقات واسم الكاتب", "danger"),
        (50, 12, "PDF annotations", "تعليقات PDF التوضيحية", "danger"),
        (86, 20, "File metadata (core/app/XMP)", "بيانات وصفية للملف", "danger"),
    ]
    for x, y, en, a, k in surfaces:
        box(ax, x, y, 27, 12, en, a, kind=k, enfs=10, arfs=9)
        arrow(ax, (x, y + (6 if y < 50 else -6)), (50, 50), color="#94a3b8", lw=1.3, rad=0.05)
    caption(ax, "A visual box over the page is NOT redaction: the metadata channel alone re-identifies 38/40 raw documents.",
            "الصندوق المرئي فوق الصفحة ليس تنقيحًا: قناة البيانات الوصفية وحدها تُعيد التعرّف على 38 من 40 مستندًا.")
    save(fig, "m1_surfaces.png")

# ============================================================= M1-2 file anatomy (NEW)
def fig_anatomy():
    fig, ax = base(10.4, 6.0)
    title(ax, "The same person, copied across parts a reader never opens",
          "الشخص نفسه، منسوخًا عبر أجزاء لا يفتحها القارئ")
    def container(x0, w, head_en, head_ar, hint, parts):
        ax.add_patch(FancyBboxPatch((x0, 11), w, 67, boxstyle="round,pad=0.02,rounding_size=0.14",
                     fc="#f8fafc", ec="#475569", lw=1.7, zorder=1))
        TL(ax, x0+w/2, 84, head_en, size=10.5, color=INK)
        TA(ax, x0+w/2, 80.3, head_ar, size=8.4, color=MUTED)
        TL(ax, x0+w/2, 73.5, hint, size=7.5, bold=False, color=MUTED, va="center")
        for i, (en, a, tag, k) in enumerate(parts):
            y = 65 - i*12.5
            fc, ec = KIND[k]
            ax.add_patch(FancyBboxPatch((x0+3, y-5.6), w-6, 11, boxstyle="round,pad=0.02,rounding_size=0.08",
                         fc=fc, ec=ec, lw=1.3, zorder=2))
            TL(ax, x0+6, y+1.6, en, size=8.4, ha="left")
            TA(ax, x0+w-4, y+1.6, a, size=7.8, color=ARCLR, ha="right")
            TL(ax, x0+6, y-3, tag, size=7.1, bold=False, color="#991b1b" if k == "danger" else MUTED, ha="left")
    container(7, 40, "DOCX  =  a ZIP of XML parts", "مستند Word حاوية ZIP من أجزاء XML", "unzip it and read the parts directly",
              [("word/document.xml", "المتن", "name, phone, ID in body + hidden runs", "danger"),
               ("word/header1.xml", "الرؤوس/التذييلات", "name repeated in header/footer", "danger"),
               ("word/comments.xml", "التعليقات", "comment text + w:author = a name", "danger"),
               ("docProps/core.xml", "خصائص أساسية", "dc:creator, lastModifiedBy, keywords", "danger")])
    container(53, 40, "PDF  =  objects + an Info dict", "ملف PDF كائنات + قاموس Info", "pypdf reads every object",
              [("content stream", "تدفّق المحتوى", "the visible + white/hidden text", "danger"),
               ("/Annots", "التعليقات التوضيحية", "notes, highlights, their authors", "danger"),
               ("/Info dictionary", "قاموس Info", "/Author, /Title, /Keywords", "danger"),
               ("XMP metadata", "بيانات XMP", "a second copy of the same fields", "danger")])
    caption(ax, "Each surface is a separate place the name must be removed; clearing one (e.g. visible body) leaves the others intact.",
            "كل سطح موضعٌ مستقلّ يجب إزالة الاسم منه؛ ومسح واحد (كالمتن المرئي) يترك البقية سليمة.", y=0.02)
    save(fig, "m1_anatomy.png")

# ============================================================= M1-3 context
def fig_context():
    fig, ax = base(10.0, 5.0)
    title(ax, "System context & trust boundary", "سياق النظام وحدّ الثقة")
    box(ax, 16, 58, 24, 15, "HR owner", "مالك الموارد البشرية", kind="process", enfs=10, arfs=8.8)
    box(ax, 50, 58, 26, 15, "Redaction tool (local)", "أداة التنقيح (محلّية)", kind="safe", enfs=10, arfs=8.8)
    box(ax, 50, 30, 26, 11, "Ground truth — never released", "المرجع — لا يُنشر", kind="gt", enfs=8.8, arfs=8.2)
    box(ax, 86, 58, 22, 15, "Recipient", "المستلِم", kind="release", enfs=10, arfs=8.8)
    box(ax, 86, 30, 22, 12, "Adversary", "الخصم", kind="danger", enfs=10, arfs=8.8)
    arrow(ax, (28, 58), (37, 58), color=INK)
    arrow(ax, (63, 58), (75, 58), color="#7c3aed", lw=2.2)
    arrow(ax, (50, 50.5), (50, 36), color="#ca8a04", lw=1.4, ls=(0, (4, 3)))
    arrow(ax, (63, 54), (80, 36), color="#dc2626", lw=1.6, ls=(0, (4, 3)), rad=-0.15)
    ax.plot([70, 70], [18, 70], color="#7c3aed", lw=1.4, ls=(0, (6, 4)), zorder=0)
    TL(ax, 70, 72, "release boundary", size=8, bold=True, color="#7c3aed")
    TA(ax, 70, 15, "حدّ الإطلاق", size=8, color="#7c3aed")
    caption(ax, "Only the redacted file crosses the boundary; the adversary sees only that file; the ground truth never leaves.",
            "لا يعبر الحدَّ إلا الملف المُنقَّح؛ ولا يرى الخصم سوى ذلك الملف؛ والمرجع لا يغادر أبدًا.", y=0.05)
    save(fig, "m1_context.png")

# ============================================================= M1-4 stakeholders
def fig_stakeholders():
    import math
    fig, ax = base(9.6, 6.6)
    title(ax, "Stakeholder map", "خريطة أصحاب المصلحة")
    box(ax, 50, 50, 26, 13, "Released document", "المستند المُطلَق", kind="head", enfs=12, arfs=9.5)
    nodes = [
        (90, "Data subject", "صاحب البيانات", "process"),
        (38, "HR / document owner", "مالك المستند", "process"),
        (330, "Development team", "فريق التطوير", "process"),
        (150, "Recipient", "المستلِم", "teal"),
        (210, "Regulator (PDPL)", "الجهة المنظِّمة", "teal"),
        (270, "Instructor / evaluator", "المُدرّس / المُقيّم", "neutral"),
        (0, "Linkage adversary", "خصم الربط", "danger"),
    ]
    rx, ry = 37, 30
    for ang, en, a, k in nodes:
        rad = math.radians(ang)
        x, y = 50 + rx*math.cos(rad), 50 + ry*math.sin(rad)
        arrow(ax, (x, y), (50, 50), color="#cbd5e1", lw=1.2, style="-")
        box(ax, x, y, 24, 11, en, a, kind=k, enfs=9.3, arfs=8.4)
    leg = [("process", "Trusted", "موثوق / داخلي"), ("teal", "External", "طرف خارجي"),
           ("neutral", "Oversight", "إشراف"), ("danger", "Adversary", "خصم")]
    for i, (k, en, a) in enumerate(leg):
        x = 9 + i*23
        ax.add_patch(Rectangle((x, 3.4), 2.6, 2.6, fc=KIND[k][0], ec=KIND[k][1], lw=1.3))
        TL(ax, x+3.6, 5.6, en, size=7.8, bold=False, color=INK, ha="left", va="center")
        TA(ax, x+3.6, 1.9, a, size=7.4, color=MUTED, ha="left", va="center")
    save(fig, "m1_stakeholders.png")

# ============================================================= M1-5 classify
def fig_classify():
    fig, ax = base(9.6, 5.8)
    title(ax, "Data classification \u2014 identification role & sensitivity",
          "تصنيف البيانات \u2014 الدور التعريفي ودرجة الحساسية")
    cols = [
        (20, "Direct identifiers", "معرّفات مباشرة", "danger",
         [("Full name", "الاسم"), ("Email", "البريد"), ("Phone", "الهاتف"), ("National ID", "الرقم الوطني")]),
        (50, "Quasi-identifiers", "معرّفات شبه مباشرة", "gt",
         [("ZIP / postcode", "الرمز البريدي"), ("City / district", "المدينة / الحي"),
          ("Street address", "الشارع"), ("Employer context", "جهة العمل")]),
        (80, "Sensitive attributes", "سمات حسّاسة", "release",
         [("Document subject", "موضوع الملف"), ("\u201cEmployee file\u201d", "\u201cملف موظف\u201d"),
          ("Relationship", "العلاقة"), ("Personal context", "سياق شخصي")]),
    ]
    for cx, en, a, k, items in cols:
        box(ax, cx, 80, 27, 12, en, a, kind=k, enfs=11, arfs=9.5)
        for i, (ie, ia) in enumerate(items):
            y = 64 - i*12
            ax.add_patch(FancyBboxPatch((cx-13.5, y-4.5), 27, 9, boxstyle="round,pad=0.02,rounding_size=0.09",
                         fc="#eef2f7", ec="#94a3b8", lw=1.3, zorder=2))
            TL(ax, cx, y, ie, size=8.8, bold=False, color=INK, ha="center")
    caption(ax, "Labels overlap: removing direct identifiers alone is not anonymity — surviving quasi-identifiers still re-identify 16/40 by linkage.",
            "التصنيفات متداخلة: حذف المعرّفات المباشرة وحده ليس إخفاءً للهوية — المعرّفات شبه المباشرة تُعيد التعرّف على 16 من 40 بالربط.")
    save(fig, "m1_classify.png")

# ============================================================= M1-6 linkage (NEW)
def fig_linkage():
    fig, ax = base(10.4, 5.2)
    title(ax, "Re-identification by linkage \u2014 why quasi-identifiers matter",
          "إعادة التعرّف بالربط \u2014 لماذا تهمّ المعرّفات شبه المباشرة")
    # left: released redacted file (direct IDs gone, quasi-identifiers survive)
    box(ax, 19, 58, 30, 15, "Released redacted file", "الملف المُنقَّح المُطلَق", kind="release", enfs=10, arfs=8.8)
    TL(ax, 19, 46.5, "name / phone / ID  removed", size=8.4, bold=True, color="#15803d")
    for i, (en, a) in enumerate([("postcode  11937", "رمز بريدي"), ("district  Abdoun", "حيّ"), ("employer  \u201cUniversity HR\u201d", "جهة العمل")]):
        y = 40 - i*7
        ax.add_patch(FancyBboxPatch((7, y-2.8), 24, 5.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                     fc="#fef9c3", ec="#ca8a04", lw=1.2, zorder=2))
        TL(ax, 9, y, en, size=7.9, bold=False, color="#92400e", ha="left")
        TA(ax, 30, y, a, size=7.4, color="#a16207", ha="right")
    TL(ax, 19, 15.5, "surviving quasi-identifiers", size=7.8, bold=True, color="#a16207")
    TA(ax, 19, 11.5, "معرّفات شبه مباشرة باقية", size=7.4, color="#a16207")
    # right: auxiliary directory
    box(ax, 82, 58, 30, 15, "Auxiliary directory", "دليل خارجي مساعد", kind="process", enfs=10, arfs=8.8)
    TL(ax, 82, 46, "(staff list / voter roll / social media)", size=7.6, bold=False, color=MUTED)
    rows = [("Sara Q.", "11822"), ("Omar Al-Masri", "11937"), ("Lina H.", "11183")]
    for i, (nm, zp) in enumerate(rows):
        y = 40 - i*7
        hit = i == 1
        ax.add_patch(Rectangle((67, y-2.9), 30, 5.8, fc="#dcfce7" if hit else "#eef2f7",
                     ec="#16a34a" if hit else "#cbd5e1", lw=1.4 if hit else 1.0, zorder=2))
        TL(ax, 69, y, nm, size=7.9, bold=hit, color="#166534" if hit else INK, ha="left")
        TL(ax, 95, y, zp + " \u00b7 Abdoun", size=7.4, bold=False, color="#166534" if hit else MUTED, ha="right")
    # join arrow
    arrow(ax, (31, 33), (67, 33), color="#dc2626", lw=1.8, rad=-0.18)
    TL(ax, 49, 41, "match on quasi-identifiers", size=8.2, bold=True, color="#dc2626")
    TA(ax, 49, 37, "مطابقة على المعرّفات شبه المباشرة", size=7.6, color="#dc2626")
    arrow(ax, (82, 30.5), (82, 24), color="#16a34a", lw=1.6)
    box(ax, 82, 19, 32, 8, "Unique match \u2192 a name", "تطابق فريد يكشف الاسم", kind="safe", enfs=9, arfs=8.2)
    caption(ax, "A record with no name is still unique on postcode + district + employer, so one directory lookup re-attaches the identity (anonymity set k = 1).",
            "سجلّ بلا اسم يظل فريدًا على الرمز البريدي + الحي + جهة العمل، فيُعيد بحثٌ واحد في الدليل ربط الهوية (حجم مجموعة الإخفاء k = 1).", y=0.02)
    save(fig, "m1_linkage.png")

# ============================================================= M1-7 evidence
def fig_evidence():
    fig, ax = base(10.2, 3.4)
    TL(ax, 0.5, 0.98, "The evidence chain", size=15, bold=True, color=INK, va="top", data=False)
    TA(ax, 0.5, 0.88, "سلسلة الأدلّة", size=12, bold=True, color=ARCLR, va="top", data=False)
    steps = [("Requirement", "متطلّب", "process"), ("Risk", "خطر", "danger"),
             ("Control", "ضابط", "safe"), ("Test", "اختبار", "gt"), ("Evidence", "دليل", "release")]
    n = len(steps); w = 16; gap = (100 - n*w)/(n+1); cy = 50
    for i, (en, a, k) in enumerate(steps):
        cx = gap + w/2 + i*(w+gap)
        box(ax, cx, cy, w, 20, en, a, kind=k, enfs=11, arfs=9.5)
        if i < n-1:
            arrow(ax, (cx+w/2, cy), (cx+w/2+gap, cy), color=INK, lw=2)
    caption(ax, "Each requirement is traced to its risk, control, test, and evidence file — same conditions before and after protection.",
            "كل متطلّب يُربط بخطره وضابطه واختباره وملف دليله — بنفس الشروط قبل الحماية وبعدها.", y=0.06)
    save(fig, "m1_evidence.png")

# ============================================================= M1-8 risk matrix
def fig_riskmatrix():
    fig, ax = base(8.6, 6.8)
    title(ax, "Risk heat map (likelihood \u00d7 impact)", "خريطة حرارة المخاطر (الاحتمال \u00d7 الأثر)")
    x0, y0, cell = 26, 26, 22
    grid = [["#dcfce7", "#fef9c3", "#fed7aa"],
            ["#fef9c3", "#fed7aa", "#fecaca"],
            ["#fed7aa", "#fecaca", "#fca5a5"]]
    for r in range(3):
        for c in range(3):
            ax.add_patch(Rectangle((x0+c*cell, y0+r*cell), cell, cell, fc=grid[r][c], ec="white", lw=2))
    labs = [("Low", "منخفض"), ("Medium", "متوسط"), ("High", "عالٍ")]
    for c, (en, a) in enumerate(labs):
        TL(ax, x0+c*cell+cell/2, y0-4, en, size=9, bold=False, color=INK)
        TA(ax, x0+c*cell+cell/2, y0-8, a, size=8.3, color=MUTED)
    for r, (en, a) in enumerate(labs):
        TL(ax, x0-4, y0+r*cell+cell/2+1.5, en, size=9, bold=False, color=INK, ha="right")
        TA(ax, x0-4, y0+r*cell+cell/2-3, a, size=8.3, color=MUTED, ha="right")
    TL(ax, x0+1.5*cell, 13.5, "Impact  \u2192", size=10, color=INK)
    TA(ax, x0+1.5*cell, 9.5, "الأثر", size=9, color=ARCLR)
    TL(ax, 9.5, y0+1.5*cell, "Likelihood  \u2192", size=10, color=INK, rot=90)
    TA(ax, 5.5, y0+1.5*cell, "الاحتمال", size=9, color=ARCLR, rot=90)
    cellrisks = {(2, 2): ["R1", "R2", "R3", "R6", "R7"], (2, 1): ["R4", "R10"], (1, 1): ["R9"]}
    for (ci, ri), ids in cellrisks.items():
        cxc, cyc = x0+ci*cell+cell/2, y0+ri*cell+cell/2
        TL(ax, cxc, cyc+4, ", ".join(ids[:3]), size=8.6, color="#991b1b")
        if len(ids) > 3:
            TL(ax, cxc, cyc-3, ", ".join(ids[3:]), size=8.6, color="#991b1b")
    caption(ax, "R1\u2013R3,R6,R7 (name/metadata/phone/Arabic) are high-likelihood, high-impact \u2014 the primary controls target them.",
            "المخاطر R1\u2013R3 وR6 وR7 عالية الاحتمال والأثر \u2014 وتستهدفها الضوابط الأساسية.", y=0.015)
    save(fig, "m1_riskmatrix.png")

# ============================================================= M1-9 methodology
def fig_methodology():
    fig, ax = base(10.4, 3.9)
    title(ax, "Seven-phase PBL methodology", "منهجية التعلّم القائم على المشروع (سبع مراحل)")
    phases = [("1 Define", "تعريف"), ("2 Map", "تخطيط"), ("3 Assess", "تقييم"),
              ("4 Design", "تصميم"), ("5 Build", "بناء"), ("6 Verify", "تحقّق"), ("7 Improve", "تحسين")]
    cols = ["#dbeafe", "#cffafe", "#ccfbf1", "#dcfce7", "#fef9c3", "#fed7aa", "#f3e8ff"]
    n = len(phases); w = 12.5; gap = (100 - n*w)/(n-1) if n > 1 else 0
    cy = 52
    for i, (en, a) in enumerate(phases):
        x = i*(w+gap)
        ec = ["#2563eb", "#0891b2", "#0d9488", "#16a34a", "#ca8a04", "#ea580c", "#7c3aed"][i]
        ax.add_patch(FancyBboxPatch((x, cy-12), w, 24, boxstyle="round,pad=0.02,rounding_size=0.08",
                     fc=cols[i], ec=ec, lw=1.5, zorder=2))
        TL(ax, x+w/2, cy+4.5, en, size=9.2, color=INK)
        TA(ax, x+w/2, cy-5, a, size=9, color=ec)
        if i < n-1:
            arrow(ax, (x+w, cy), (x+w+gap, cy), color=MUTED, lw=1.5)
    arrow(ax, (97, 38), (3, 38), color="#94a3b8", lw=1.2, ls=(0, (5, 3)), rad=-0.12)
    TL(ax, 50, 27, "iterate: retest & reassess residual risk", size=8, bold=False, color=MUTED)
    TA(ax, 50, 21, "تكرار: إعادة الاختبار وتقييم المخاطر المتبقّية", size=8, color=MUTED)
    caption(ax, "M1 covers phases 1\u20133 and starts phase 4.", "تغطّي M1 المراحل 1\u20133 وتبدأ المرحلة 4.", y=0.06)
    save(fig, "m1_methodology.png")

# ============================================================= M1-10 schedule
def fig_schedule():
    fig, ax = plt.subplots(figsize=(9.6, 4.3))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")
    TL(ax, 0.5, 0.97, "Project schedule & milestones (Weeks 1\u201315)", size=15, color=INK, va="top", data=False)
    TA(ax, 0.5, 0.9, "الجدول الزمني للمشروع والمحطّات (الأسابيع 1\u201315)", size=12, bold=True, color=ARCLR, va="top", data=False)
    ax.add_patch(Rectangle((0.6, 4.3), 14.8, 0.5, fc="#e2e8f0", ec="#94a3b8", lw=1))
    for wk in range(1, 16):
        x = 0.6 + (wk-0.5)*(14.8/15)
        ax.plot([x, x], [4.3, 4.8], color="#cbd5e1", lw=0.8)
        TL(ax, x, 3.9, str(wk), size=7.5, bold=False, color=MUTED, va="top")
    phases = [(1, 3, "Define / Map", "تعريف / تخطيط", "#dbeafe"), (4, 6, "Assess / Design", "تقييم / تصميم", "#dcfce7"),
              (7, 11, "Build", "بناء", "#fef9c3"), (12, 15, "Verify / Improve", "تحقّق / تحسين", "#f3e8ff")]
    for a0, b0, en, a, c in phases:
        x0 = 0.6 + (a0-1)*(14.8/15); x1 = 0.6 + b0*(14.8/15)
        ax.add_patch(Rectangle((x0, 5.1), x1-x0-0.1, 1.1, fc=c, ec="#94a3b8", lw=0.8))
        TL(ax, (x0+x1)/2, 5.72, en, size=8.3, bold=False, color=INK)
        TA(ax, (x0+x1)/2, 5.33, a, size=7.6, color=ARCLR)
    miles = [(4, "M1 Proposal", "المقترح"), (7, "M2 Design+Prototype", "التصميم+النموذج"),
             (12, "M3 Impl.+Validation", "التنفيذ+التحقّق"), (15, "M4 Final+Demo", "التسليم النهائي")]
    for wk, en, a in miles:
        x = 0.6 + (wk-0.5)*(14.8/15)
        ax.add_patch(FancyArrowPatch((x, 4.3), (x, 1.95), arrowstyle="-|>", mutation_scale=13, color="#dc2626", lw=1.6))
        ax.add_patch(FancyBboxPatch((x-1.4, 0.5), 2.8, 1.35, boxstyle="round,pad=0.02,rounding_size=0.08",
                     fc="#fee2e2", ec="#dc2626", lw=1.3))
        TL(ax, x, 1.38, en, size=7.4, color="#991b1b")
        TA(ax, x, 0.82, a, size=7.6, color="#b91c1c")
    save(fig, "m1_schedule.png")

# ============================================================= M2-1 architecture
def fig_arch():
    fig, ax = base(10.4, 7.0)
    title(ax, "Architecture & data flow with trust boundaries", "البنية وتدفّق البيانات مع حدود الثقة")
    ax.add_patch(FancyBboxPatch((3, 40), 94, 42, boxstyle="round,pad=0.02,rounding_size=0.5",
                 fc="#f8fafc", ec="#16a34a", lw=1.8, ls=(0, (6, 4)), zorder=0))
    TL(ax, 6, 79.5, "TRUSTED — local HR boundary", size=9.5, color="#166534", ha="left")
    TA(ax, 6, 76.3, "موثوق — حدود الموارد البشرية المحلّية", size=8.6, color="#15803d", ha="left")
    pipe = [(16, 62, "Generator", "المولّد", "process"), (37, 62, "Documents (40 files)", "المستندات", "neutral"),
            (58, 62, "Extraction", "الاستخراج", "process"), (79, 62, "Detector v1\u2013v4", "الكاشف", "process")]
    for x, y, en, a, k in pipe:
        box(ax, x, y, 18, 12, en, a, kind=k, enfs=9.3, arfs=8.6)
    box(ax, 58, 46, 18, 12, "Redaction / rewrite", "التنقيح", kind="safe", enfs=9.3, arfs=8.6)
    box(ax, 79, 46, 18, 12, "Ground truth (never released)", "المرجع (لا يُنشر)", kind="gt", enfs=8.3, arfs=8)
    for a, b in [((25, 62), (28, 62)), ((46, 62), (49, 62)), ((67, 62), (70, 62))]:
        arrow(ax, a, b, color=INK)
    arrow(ax, (79, 56), (79, 52), color=INK)
    arrow(ax, (79, 46), (67, 46), color=INK)
    arrow(ax, (58, 56), (58, 52), color=INK)
    arrow(ax, (58, 40), (58, 30), color="#7c3aed", lw=2.4)
    TL(ax, 61, 35, "RELEASE across the boundary", size=8.3, color="#6d28d9", ha="left")
    TA(ax, 61, 31.8, "إطلاق عبر الحدّ", size=8, color="#7c3aed", ha="left")
    box(ax, 30, 24, 22, 12, "Released redacted file", "الملف المُنقَّح المُطلَق", kind="release", enfs=9.3, arfs=8.6)
    ax.add_patch(FancyBboxPatch((3, 3), 94, 16, boxstyle="round,pad=0.02,rounding_size=0.4",
                 fc="#fff7ed", ec="#ca8a04", lw=1.6, ls=(0, (5, 3)), zorder=0))
    TL(ax, 6, 16.6, "MEASUREMENT — plays the adversary (reads only the released file)", size=8.8, color="#92400e", ha="left")
    TA(ax, 6, 13.4, "القياس — يلعب دور الخصم (يقرأ الملف المُطلَق فقط)", size=8, color="#b45309", ha="left")
    for x, en, a in [(24, "Detection quality", "جودة الكشف"), (50, "Residual disclosure", "التسرّب المتبقّي"),
                     (76, "Re-identification (k)", "إعادة التعرّف")]:
        box(ax, x, 7.5, 24, 6.5, en, a, kind="neutral", enfs=8.6, arfs=8)
    arrow(ax, (30, 18), (30, 14), color="#b45309")
    arrow(ax, (30, 18), (50, 10.7), color="#b45309", rad=-0.1)
    arrow(ax, (30, 18), (72, 10.7), color="#b45309", rad=-0.15)
    save(fig, "m2_arch.png")

# ============================================================= M2-2 surface flow
def fig_surface_flow():
    fig, ax = base(10.2, 5.6)
    title(ax, "Per-surface redaction: the pipeline reaches every channel",
          "التنقيح لكل سطح: يبلغ الخط كل قناة")
    surfaces = [("Body & tables", "المتن والجداول"), ("Headers / footers", "الرؤوس/التذييلات"),
                ("Hidden text", "النص المخفي"), ("Comments + author", "التعليقات والكاتب"),
                ("PDF annotations", "تعليقات PDF"), ("Metadata", "البيانات الوصفية")]
    for i, (en, a) in enumerate(surfaces):
        y = 86 - i*14
        box(ax, 15, y, 24, 11, en, a, kind=("process" if i < 2 else "danger"), enfs=8.6, arfs=7.9)
        arrow(ax, (27, y), (37, 50), color="#cbd5e1", lw=1.1, rad=0.03)
    steps = [(43, "Extract", "الاستخراج"), (59, "Detect (v4)", "الكشف"),
             (75, "Anonymize", "التنقيح"), (91, "Rewrite", "إعادة الكتابة")]
    for i, (x, en, a) in enumerate(steps):
        box(ax, x, 50, 14, 16, en, a, kind="safe", enfs=8.6, arfs=8.2)
        if i < len(steps)-1:
            arrow(ax, (x+7, 50), (steps[i+1][0]-7, 50), color=INK, lw=1.6)
    caption(ax, "Detection runs over the whole document and every occurrence is removed on every surface — then the output is re-inspected.",
            "يجري الكشف على كامل المستند وتُزال كل الورود على كل سطح — ثم يُعاد فحص المخرَج.")
    save(fig, "m2_surface_flow.png")

# ============================================================= M2-3 metadata channel (NEW)
def fig_metadata():
    fig, ax = base(10.2, 5.2)
    title(ax, "Closing the metadata & comment-author channel",
          "إغلاق قناة البيانات الوصفية واسم كاتب التعليق")
    fields = [("DOCX  docProps/core.xml", "dc:creator", "Omar Al-Masri"),
              ("DOCX  word/comments.xml", "w:author", "Omar Al-Masri"),
              ("PDF  /Info dictionary", "/Author", "Omar Al-Masri")]
    # before column
    TL(ax, 27, 80, "Before  \u2014  the hidden channel", size=10, color="#b91c1c")
    TA(ax, 27, 75.5, "قبل \u2014 القناة الخفيّة", size=8.4, color="#b91c1c")
    TL(ax, 76, 80, "After v4  \u2014  cleared", size=10, color="#166534")
    TA(ax, 76, 75.5, "بعد v4 \u2014 مُزالة", size=8.4, color="#15803d")
    for i, (loc, key, val) in enumerate(fields):
        y = 64 - i*15
        ax.add_patch(FancyBboxPatch((4, y-6), 46, 12.5, boxstyle="round,pad=0.02,rounding_size=0.07",
                     fc="#fee2e2", ec="#dc2626", lw=1.4, zorder=2))
        TL(ax, 6.5, y+2.6, loc, size=7.7, bold=True, color=INK, ha="left")
        TL(ax, 6.5, y-2.8, key + " = " + val, size=8.2, bold=False, color="#991b1b", ha="left")
        arrow(ax, (50.5, y), (57, y), color=INK, lw=1.8)
        ax.add_patch(FancyBboxPatch((58, y-6), 40, 12.5, boxstyle="round,pad=0.02,rounding_size=0.07",
                     fc="#dcfce7", ec="#16a34a", lw=1.4, zorder=2))
        TL(ax, 60.5, y+2.6, loc.split("  ")[-1], size=7.7, bold=True, color=INK, ha="left")
        TL(ax, 60.5, y-2.8, key + " = (empty)", size=8.2, bold=False, color="#166534", ha="left")
    caption(ax, "Metadata & comment authors re-identify 38/40 raw documents on their own; v4 clears every field \u2014 0 metadata leaks across all 40.",
            "البيانات الوصفية وأسماء الكُتّاب تُعيد التعرّف على 38 من 40 مستندًا وحدها؛ وتمسح v4 كل حقل \u2014 صفر تسرّب في الأربعين كلّها.", y=0.02)
    save(fig, "m2_metadata.png")

# ============================================================= M2-4 attackers
def fig_attackers():
    fig, ax = base(9.8, 5.4)
    title(ax, "Attacker model \u2014 escalating knowledge (A1 \u2192 A4)",
          "نموذج المُهاجِم \u2014 معرفة متصاعدة من A1 إلى A4")
    atk = [("A1", "Reader", "القارئ", "reads the visible page", "يقرأ الصفحة المرئية", "#dbeafe", "#2563eb"),
           ("A2", "Text extractor", "مُستخرِج النص", "+ hidden & white text", "+ النص المخفي والأبيض", "#cffafe", "#0891b2"),
           ("A3", "Metadata inspector", "فاحص البيانات", "+ metadata, comment authors", "+ البيانات الوصفية والكُتّاب", "#fef9c3", "#ca8a04"),
           ("A4", "Linkage adversary", "خصم الربط", "+ auxiliary directory = a name", "+ دليل مساعد يُسمّي الملف", "#fee2e2", "#dc2626")]
    n = len(atk); bw = 21; gap = 2.5; x0 = 5
    for i, (tag, en, a, cap_en, cap_ar, fc, ec) in enumerate(atk):
        x = x0 + i*(bw+gap); h = 30 + i*9; y0 = 16
        ax.add_patch(FancyBboxPatch((x, y0), bw, h, boxstyle="round,pad=0.02,rounding_size=0.07", fc=fc, ec=ec, lw=1.7))
        TL(ax, x+bw/2, y0+h-6, tag, size=14, color=ec)
        TL(ax, x+bw/2, y0+h-13, en, size=8.8, color=INK)
        TA(ax, x+bw/2, y0+h-18, a, size=8.4, color=ec)
        TL(ax, x+bw/2, y0+7.5, cap_en, size=7.3, bold=False, color=INK)
        TA(ax, x+bw/2, y0+3.3, cap_ar, size=7.2, color=MUTED)
        if i < n-1:
            arrow(ax, (x+bw, y0+9), (x+bw+gap, y0+9), color=MUTED, lw=1.5)
    caption(ax, "The verifier/attacker is given no privileged access \u2014 it reads exactly the surfaces A2/A3 can, and A4 links residual quasi-identifiers.",
            "لا يُمنح المُقيّم/المُهاجِم وصولًا مميّزًا \u2014 يقرأ الأسطح التي يصل إليها A2/A3، ويربط A4 المعرّفات شبه المباشرة.", y=0.05)
    save(fig, "m2_attackers.png")

# ============================================================= M2-5 anonymity set (NEW)
def fig_kset():
    fig, ax = base(10.2, 5.0)
    title(ax, "Anonymity set k \u2014 hiding in a crowd, not alone",
          "مجموعة إخفاء الهوية k \u2014 الاختباء في حشد لا منفردًا")
    def crowd(cx, highlight, label_en, label_ar, kval, good):
        # 5x4 grid of people
        n = 0
        for r in range(4):
            for c in range(5):
                x = cx - 16 + c*8
                y = 62 - r*10
                hot = n in highlight
                ax.scatter([x], [y+1.4], s=70, color="#16a34a" if (hot and good) else ("#dc2626" if hot else "#cbd5e1"),
                           edgecolor="white", linewidth=0.8, zorder=3)
                ax.add_patch(FancyBboxPatch((x-1.7, y-4.2), 3.4, 4.2, boxstyle="round,pad=0.02,rounding_size=0.3",
                             fc="#16a34a" if (hot and good) else ("#dc2626" if hot else "#cbd5e1"),
                             ec="none", zorder=2))
                n += 1
        ax.add_patch(FancyBboxPatch((cx-17, 15.5), 34, 6.5, boxstyle="round,pad=0.02,rounding_size=0.12",
                     fc="#f1f5f9", ec="#94a3b8", lw=1.2))
        TL(ax, cx, 19.6, label_en, size=9, color=INK)
        TA(ax, cx, 16.6, label_ar, size=8, color=MUTED)
        col = "#16a34a" if good else "#dc2626"
        TL(ax, cx, 9.5, kval, size=11, color=col)
    crowd(27, {11}, "original / baseline", "الأصل", "k = 1  \u2192  re-identified", good=False)
    crowd(75, {5, 6, 7, 10, 11, 12, 13, 15, 16, 17, 18}, "v4 (recommended)", "v4 (موصى به)", "mean k \u2248 11.5  \u2192  hidden", good=True)
    ax.plot([50, 50], [26, 70], color="#e2e8f0", lw=1.3, ls=(0, (4, 3)))
    caption(ax, "k is how many people in the population share the released record\u2019s quasi-identifiers; k = 1 is unique (re-identified). v4 raises mean k from 1.0 to 11.5.",
            "k هو عدد الأفراد الذين يتشاركون معرّفات السجلّ المُطلَق؛ وk = 1 يعني التفرّد (إعادة تعرّف). وترفع v4 متوسط k من 1.0 إلى 11.5.", y=0.02)
    save(fig, "m2_kset.png")

# ============================================================= M2-6 ladder
def fig_ladder():
    fig, ax = base(9.8, 5.8)
    title(ax, "The v1 \u2192 v4 design ladder \u2014 each stage fixes a named weakness",
          "سُلّم التصميم من v1 إلى v4 \u2014 كل مرحلة تعالج ضعفًا محدّدًا")
    steps = [("v1", "Presidio defaults", "الإعدادات الافتراضية", "re-id 87.5%", "#dbeafe", "#2563eb"),
             ("v2", "+ spaCy en_core_web_lg", "نموذج spaCy الكبير", "re-id 92.5%", "#cffafe", "#0891b2"),
             ("v3", "+ US regex + allow-list", "تعابير + قائمة سماح", "re-id 77.5%", "#fef9c3", "#ca8a04"),
             ("v4", "+ intl/Jordan phone,\nArabic, consistent scrub", "هاتف دولي + عربية", "re-id 40%", "#dcfce7", "#16a34a")]
    n = len(steps); bw = 20; gap = 4; x0 = 6
    for i, (tag, en, a, metric, fc, ec) in enumerate(steps):
        x = x0 + i*(bw+gap); h = 22 + i*14; y0 = 16
        ax.add_patch(FancyBboxPatch((x, y0), bw, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.7))
        TL(ax, x+bw/2, y0+h-5, tag, size=15, color=ec)
        ax.text(x+bw/2, y0+h-10.5, en, ha="center", va="top", fontproperties=LATR, fontsize=7.6, color=INK, linespacing=1.3)
        TA(ax, x+bw/2, y0+6.5, a, size=8, color=ec)
        ax.add_patch(FancyBboxPatch((x+2, y0+1.5), bw-4, 3.6, boxstyle="round,pad=0.02,rounding_size=0.05", fc="white", ec=ec, lw=1))
        TL(ax, x+bw/2, y0+3.3, metric, size=8.2, color=ec)
        if i < n-1:
            arrow(ax, (x+bw, y0+10), (x+bw+gap, y0+10), color=MUTED, lw=1.6)
    caption(ax, "Re-identification falls 100% \u2192 40% as each weakness is closed; v4 is the recommended release.",
            "تنخفض نسبة إعادة التعرّف من 100% إلى 40% مع معالجة كل ضعف؛ v4 هو الإصدار المُوصى به.")
    save(fig, "m2_ladder.png")

# ============================================================= M2-7 recognizers
def fig_recognizers():
    fig, ax = base(10.2, 6.0)
    title(ax, "Inside the v4 detector (pipelines.py) \u2014 how PII spans are built",
          "داخل كاشف v4 \u2014 كيف تُبنى نطاقات البيانات الشخصية")
    box(ax, 12, 50, 17, 14, "Document text", "نص المستند", kind="head", enfs=9.3, arfs=8.6)
    recs = [(82, "spaCy NER", "PERSON, LOCATION", "process"),
            (68, "Presidio built-ins", "EMAIL, US_SSN", "process"),
            (54, "US/Intl/JO phone", "+1 \u00b7 +962 \u00b7 07x", "teal"),
            (40, "Address regex", "US/UK/JO/ES", "teal"),
            (26, "Arabic PII", "Arabic script", "danger")]
    for y, en, sub, k in recs:
        box(ax, 42, y, 24, 11, en, "", kind=k, enfs=8.8, bold=True)
        TL(ax, 42, y-2.6, sub, size=7.3, bold=False, color=MUTED)
        arrow(ax, (20.5, 50), (30, y), color="#cbd5e1", lw=1.1, rad=0.04)
        arrow(ax, (54, y), (64, 50), color="#cbd5e1", lw=1.1, rad=0.04)
    box(ax, 74, 50, 18, 13, "Merge results", "دمج النتائج", kind="neutral", enfs=9, arfs=8.4)
    box(ax, 92, 50, 13, 15, "PII spans", "النطاقات", kind="safe", enfs=9, arfs=8.4)
    arrow(ax, (83, 50), (85.5, 50), color=INK, lw=1.6)
    box(ax, 74, 28, 30, 13, "Resolve overlaps (address wins)\n+ allow-list keeps the decoy",
        "حلّ التداخل + قائمة السماح", kind="gt", enfs=7.8, arfs=8)
    arrow(ax, (74, 43.5), (74, 35), color=INK, lw=1.5)
    caption(ax, "Five recognizers feed one result set; a full address overrides fragments inside it, and the non-personal decoy is kept.",
            "خمسة مُميّزات تُغذّي مجموعة نتائج واحدة؛ والعنوان الكامل يتغلّب على أجزائه، ويُحتفَظ بالطُّعم غير الشخصي.", y=0.02)
    save(fig, "m2_recognizers.png")

# ============================================================= M2-8 results bars
def fig_results_bars():
    labels = ["original", "v1", "v2", "v3", "v4"]
    reid = [100, 87.5, 92.5, 77.5, 40]
    meank = [1.0, 3.4, 2.4, 5.3, 11.5]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.6))
    fig.suptitle("Results across approaches", fontproperties=LATB, fontsize=14, color=INK, y=1.02)
    TA(ax1, 1.12, 1.15, "النتائج بين الأساليب", size=11.5, color=ARCLR, va="bottom", data=False)
    def hl(vals): return ["#16a34a" if l == "v4" else "#93c5fd" for l in labels]
    b1 = ax1.bar(labels, reid, color=hl(reid), edgecolor="white", width=0.68)
    for b, v in zip(b1, reid): ax1.text(b.get_x()+b.get_width()/2, v+1.5, f"{v:g}", ha="center", fontproperties=LATB, fontsize=9, color=INK)
    ax1.set_title("Re-identification rate  %", fontproperties=LATB, fontsize=10.5, color=INK, pad=20)
    TA(ax1, 0.5, 1.02, "نسبة إعادة التعرّف  —  الأقل أفضل", size=9, color=MUTED, va="bottom", data=False)
    ax1.set_ylim(0, 112)
    b2 = ax2.bar(labels, meank, color=["#16a34a" if l == "v4" else "#fdba74" for l in labels], edgecolor="white", width=0.68)
    for b, v in zip(b2, meank): ax2.text(b.get_x()+b.get_width()/2, v+0.25, f"{v:g}", ha="center", fontproperties=LATB, fontsize=9, color=INK)
    ax2.set_title("Mean anonymity set  k", fontproperties=LATB, fontsize=10.5, color=INK, pad=20)
    TA(ax2, 0.5, 1.02, "متوسط مجموعة إخفاء الهوية  —  الأعلى أفضل", size=9, color=MUTED, va="bottom", data=False)
    ax2.set_ylim(0, 13)
    for ax in (ax1, ax2):
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        for s in ["left", "bottom"]: ax.spines[s].set_color("#cbd5e1")
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.set_axisbelow(True); ax.grid(axis="y", color="#eef2f7", lw=0.9)
    fig.tight_layout()
    save(fig, "m2_results_bars.png")

# ============================================================= M2-9 tradeoff
def fig_tradeoff():
    fig, ax = plt.subplots(figsize=(8.8, 5.6))
    pts = [("original", 100, 100), ("v1", 94.8, 87.5), ("v2", 94.8, 92.5), ("v3", 97.0, 77.5), ("v4", 97.0, 40.0)]
    for lab, u, r in pts:
        hlt = lab == "v4"
        ax.scatter([u], [r], s=320 if hlt else 150, color="#16a34a" if hlt else "#2563eb",
                   edgecolor="white", linewidth=1.5, zorder=3)
        off = {"original": (12, 0), "v1": (12, -13), "v2": (12, 9), "v3": (12, 6), "v4": (14, 2)}[lab]
        ax.annotate(lab, (u, r), textcoords="offset points", xytext=off,
                    fontproperties=LATB, fontsize=10.5, color="#166534" if hlt else INK)
    ax.annotate("", xy=(99.4, 30), xytext=(95.5, 58), arrowprops=dict(arrowstyle="-|>", color="#94a3b8", lw=1.6))
    TL(ax, 99.5, 26, "better", size=9, color="#64748b", ha="right", data=True)
    TA(ax, 99.5, 22, "أفضل", size=8.5, color="#64748b", ha="right", data=True)
    ax.set_xlim(93, 101); ax.set_ylim(20, 108)
    ax.set_xlabel("Utility retained  %", fontproperties=LATR, fontsize=11, color=INK)
    ax.set_ylabel("Re-identification rate  %", fontproperties=LATR, fontsize=11, color=INK)
    ax.set_title("Privacy\u2013utility trade-off across approaches", fontproperties=LATB, fontsize=13, color=INK, pad=24)
    TA(ax, 0.5, 1.015, "مفاضلة الخصوصية مقابل المنفعة بين الأساليب", size=10.5, color=ARCLR, va="bottom", data=False)
    ax.grid(True, color="#e2e8f0", lw=0.8)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color("#cbd5e1")
    ax.tick_params(colors=MUTED)
    fig.tight_layout()
    save(fig, "m2_tradeoff.png")

# ============================================================= M2-10 generalization (NEW)
def fig_generalization():
    fig, ax = base(10.2, 4.6)
    title(ax, "Planned for M3: generalize quasi-identifiers to raise k",
          "مخطّط لـ M3: تعميم المعرّفات شبه المباشرة لرفع k")
    # exact
    box(ax, 17, 62, 28, 15, "Exact postcode  11937", "رمز بريدي دقيق", kind="danger", enfs=9.5, arfs=8.4)
    TL(ax, 17, 50, "k = 1   (unique \u2192 re-identified)", size=8.4, bold=True, color="#b91c1c")
    TA(ax, 17, 45.5, "فريد: إعادة التعرّف", size=7.8, color="#b91c1c")
    arrow(ax, (31, 62), (44, 62), color=INK, lw=2)
    box(ax, 55, 62, 22, 13, "generalize", "تعميم", kind="process", enfs=9.5, arfs=8.6)
    arrow(ax, (66, 62), (79, 62), color=INK, lw=2)
    box(ax, 88, 62, 24, 15, "Region:  Amman", "المنطقة: عمّان", kind="safe", enfs=9.5, arfs=8.4)
    TL(ax, 88, 50, "k = 8   (hidden in a crowd)", size=8.4, bold=True, color="#166534")
    TA(ax, 88, 45.5, "مختبئ في حشد", size=7.8, color="#15803d")
    # other planned controls
    TL(ax, 50, 34, "Other M3 controls", size=9, bold=True, color=INK)
    TA(ax, 50, 29.5, "ضوابط M3 الأخرى", size=8, color=MUTED)
    extras = [("P.O.-Box rule", "قاعدة صندوق البريد"), ("non-US addresses", "عناوين غير أمريكية"),
              ("org-name gazetteer", "مُعجم أسماء الجهات"), ("PDPL control map", "ربط قانون البيانات")]
    for i, (en, a) in enumerate(extras):
        x = 14 + i*22
        ax.add_patch(FancyBboxPatch((x-9, 15), 18, 8, boxstyle="round,pad=0.02,rounding_size=0.1",
                     fc="#f3e8ff", ec="#7c3aed", lw=1.2))
        TL(ax, x, 20.2, en, size=7.6, bold=False, color="#5b21b6")
        TA(ax, x, 16.6, a, size=7.2, color="#6d28d9")
    caption(ax, "Generalization trades a little precision for a large privacy gain: coarsening the postcode lifts the anonymity set from 1 to many.",
            "يُقايض التعميم قليلًا من الدقّة بمكسب خصوصية كبير: فتخشين الرمز البريدي يرفع مجموعة الإخفاء من 1 إلى كثير.", y=0.02)
    save(fig, "m2_generalization.png")

if __name__ == "__main__":
    print("native Arabic shaping:", NATIVE_SHAPING)
    # M1 (11 figures)
    fig_blackbox(); fig_surfaces(); fig_anatomy(); fig_context(); fig_stakeholders()
    fig_classify(); fig_linkage(); fig_evidence(); fig_riskmatrix(); fig_methodology(); fig_schedule()
    # M2 (10 figures)
    fig_arch(); fig_surface_flow(); fig_metadata(); fig_attackers(); fig_kset()
    fig_ladder(); fig_recognizers(); fig_results_bars(); fig_tradeoff(); fig_generalization()
    print("ALL DONE")
