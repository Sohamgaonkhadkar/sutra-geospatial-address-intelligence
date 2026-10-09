"""Build SUTRA_PS3_Final_Report.docx — editable mirror of the Typst report.
Usage: python3 report_source/build_docx.py   (after build_report.py, used only to
rasterize the architecture diagram from the compiled PDF page)."""
import re, sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent
FIG = SRC / "figures"
SHOT = ROOT / "screenshots"

PAPER = RGBColor(0xFB, 0xF9, 0xF2); INK = RGBColor(0x21, 0x1D, 0x14)
INK2 = RGBColor(0x4A, 0x44, 0x33); MUTE = RGBColor(0x60, 0x58, 0x4B)
ACCENT = RGBColor(0xC4, 0x50, 0x1B); OK = RGBColor(0x3B, 0x74, 0x49)
WARN = RGBColor(0x8D, 0x61, 0x17); CRIT = RGBColor(0xB2, 0x3A, 0x2B)
COOL = RGBColor(0x51, 0x61, 0x6C); PLUM = RGBColor(0x6D, 0x4F, 0x6E)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(9.5); st.font.color.rgb = INK
for lvl, sz, col in [("Heading 1", 17, INK), ("Heading 2", 12, INK2), ("Heading 3", 10.5, INK2)]:
    h = doc.styles[lvl]; h.font.size = Pt(sz); h.font.color.rgb = col; h.font.name = "Cambria"

FIGNO = 0

def unescape(s):
    for a, b in [("\\%", "%"), ("\\_", "_"), ("\\@", "@"), ("\\<", "<"), ("\\>", ">"),
                 ("\\{", "{"), ("\\}", "}"), ("\\#", "#"), ("\\\\", "\\")]:
        s = s.replace(a, b)
    return s

RICH = re.compile(r'#text\(style: "italic"\)\[(.*?)\]|#text\(weight: "bold"(?:, fill: [\w.]+)?\)\[(.*?)\]|`([^`]+)`', re.S)

def add_rich(p, s):
    pos = 0
    for m in RICH.finditer(s):
        if m.start() > pos:
            p.add_run(unescape(s[pos:m.start()]))
        if m.group(1) is not None:
            r = p.add_run(unescape(m.group(1))); r.italic = True
        elif m.group(2) is not None:
            r = p.add_run(unescape(m.group(2))); r.bold = True
        else:
            r = p.add_run(unescape(m.group(3))); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        pos = m.end()
    if pos < len(s):
        p.add_run(unescape(s[pos:]))
    return p

def para(s="", size=None, color=None, italic=False, bold=False, after=4):
    p = doc.add_paragraph()
    if s: add_rich(p, s)
    if size: p.runs and [setattr(r.font, "size", Pt(size)) for r in p.runs]
    if color: [setattr(r.font, "color.rgb", color) for r in p.runs]
    if italic: [setattr(r, "italic", True) for r in p.runs]
    if bold: [setattr(r, "bold", True) for r in p.runs]
    p.paragraph_format.space_after = Pt(after)
    return p

def kicker(t):
    p = doc.add_paragraph(); r = p.add_run(t)
    r.font.size = Pt(8); r.font.color.rgb = ACCENT; r.font.name = "Consolas"
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(2)

def chapter(n, t, lead=None):
    kicker(f"SECTION {n}")
    doc.add_heading(t, level=1)
    if lead: para(lead, italic=True, color=INK2)

def h2(t): doc.add_heading(t, level=2)

def srcline(s):
    p = doc.add_paragraph(); r = p.add_run("source: " + unescape(s))
    r.font.size = Pt(7.5); r.font.color.rgb = MUTE; r.font.name = "Consolas"
    p.paragraph_format.space_after = Pt(6)

def callout(tag, color, body):
    p = doc.add_paragraph()
    r = p.add_run(tag + "  "); r.bold = True; r.font.size = Pt(8); r.font.color.rgb = color; r.font.name = "Consolas"
    add_rich(p, body)

def panel(title, body):
    p = doc.add_paragraph(); r = p.add_run(title); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = INK2
    para(body)

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 2"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htxt in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(unescape(htxt)); r.bold = True; r.font.size = Pt(8); r.font.name = "Consolas"
    for row in rows:
        cells = t.add_row().cells
        for i, cell in enumerate(row):
            cells[i].text = ""
            add_rich(cells[i].paragraphs[0], cell).runs and [setattr(x.font, "size", Pt(8.3)) for x in cells[i].paragraphs[0].runs]
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t

def fig(path, caption, source, width=6.4):
    global FIGNO
    FIGNO += 1
    doc.add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph(); r = p.add_run(f"Figure {FIGNO}: "); r.bold = True; r.font.size = Pt(8.5)
    r2 = p.add_run(unescape(caption)); r2.font.size = Pt(8.5); r2.font.color.rgb = INK2
    q = doc.add_paragraph(); r3 = q.add_run("source: " + unescape(source))
    r3.font.size = Pt(7.5); r3.font.color.rgb = MUTE; r3.font.name = "Consolas"

def hyperlink(p, url, text):
    part = doc.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    nr = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "C4501B")
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single")
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "16")
    rpr.append(c); rpr.append(u); rpr.append(sz); nr.append(rpr)
    t = OxmlElement("w:t"); t.text = text; nr.append(t); h.append(nr)
    p._p.append(h)

# ══ COVER ════════════════════════════════════════════════════════════════════
p = doc.add_paragraph(); r = p.add_run("SUTRA"); r.font.size = Pt(40); r.font.name = "Cambria"; r.bold = True
p = doc.add_paragraph(); r = p.add_run("SEMANTIC UTILITY FOR TRACEABLE RESOLUTION OF ADDRESSES")
r.font.size = Pt(8); r.font.color.rgb = MUTE; r.font.name = "Consolas"
p = doc.add_paragraph(); r = p.add_run("An Evidence-Driven Address Geocoder That Learns from Field Visits")
r.font.size = Pt(15); r.font.color.rgb = ACCENT; r.bold = True; r.font.name = "Cambria"
para("Definitive Technical Research and Product Report · CreditNirvana Problem Statement 3", color=INK2)
para("sutra_local_metric_plane:T2 · metres · NT — radius 566.9 m · empirical_p80 · n=24 · cov 0.792 · street withheld", size=8, color=COOL)
t = table(["SCHEMA / RULES", "EVIDENCE / RADIUS", "EVALUATION CUT", "FROZEN CONFIG"],
          [["sutra-1.0", "policy-v3", "2026-06-01", "9abebb8f…"],
           ["candidate-rules-v2 · gate-v2", "radius-map-v1 · emp-v1", "as-of · protocol-v1-immutable", "one locked S-EVAL read"]])
p = doc.add_paragraph()
p.add_run("Prepared for formal project evaluation · 2026-10-09 · Live prototype: ")
hyperlink(p, "https://sutra-geospatial-address-intelligence-4wya-otn8569cb.vercel.app/",
          "sutra-geospatial-address-intelligence.vercel.app")
for r in p.runs: r.font.size = Pt(7.5); r.font.color.rgb = MUTE
p = doc.add_paragraph(); r = p.add_run("figures generated from the frozen evaluation ledgers · DOCX mirror of the typeset edition")
r.font.size = Pt(7.5); r.font.color.rgb = MUTE
doc.add_page_break()

# ══ CONTENTS ═════════════════════════════════════════════════════════════════
doc.add_heading("Contents and how to read this report", level=1)
p = doc.add_paragraph()
fld_begin = OxmlElement("w:r"); fb = OxmlElement("w:fldChar"); fb.set(qn("w:fldCharType"), "begin"); fld_begin.append(fb)
instr = OxmlElement("w:r"); i_ = OxmlElement("w:instrText"); i_.set(qn("xml:space"), "preserve"); i_.text = 'TOC \\o "1-2" \\h \\z \\u'
instr.append(i_)
fld_sep = OxmlElement("w:r"); fs = OxmlElement("w:fldChar"); fs.set(qn("w:fldCharType"), "separate"); fld_sep.append(fs)
fld_end = OxmlElement("w:r"); fe = OxmlElement("w:fldChar"); fe.set(qn("w:fldCharType"), "end"); fld_end.append(fe)
for el in (fld_begin, instr, fld_sep, fld_end): p._p.append(el)
para("[Select the field above and press F9 in Word to refresh the table of contents.]", size=8, color=MUTE, italic=True)
panel("Report orientation",
      "This report is a single connected argument: data and EDA → candidate-generation research → model training and selection → production ranking policy → uncertainty and evidence handling → physical-place memory → backend APIs → the operator workbench → measured results and remaining integration work. Each section states not only what was built but why the data forced it.")
para("Four reading rules run through every page. A candidate oracle is not model accuracy — oracle numbers describe what the candidate family contains, never what the system predicts. Cold-start, product-policy and warm/evidence results are different populations, and they are never blended into a single accuracy figure. Training and validation numbers are not production numbers: the live request path runs the deterministic RULE ranker, while the learned challengers were evaluated offline and rejected. And every headline metric carries its population, n, ground-truth source and regime right beside it; the appendix keeps the full provenance ledger.")
doc.add_page_break()

# ══ 1 ════════════════════════════════════════════════════════════════════════
chapter(1, "Executive summary", "SUTRA treats address geocoding as an evidence-driven decision problem: generate candidates from a restricted official family, rank them with an inspectable rule, publish granularity, provenance and a measured uncertainty radius, and let trusted field visits improve future belief — while refusing to fabricate precision the evidence does not support.")
table(["VENDOR BASELINE, S-EVAL", "PRODUCT POLICY, S-EVAL", "WARM / EVIDENCE SUBSET", "TEMPORAL PRODUCT PROXY"],
      [["376.4 m", "76% <500 m", "96.77% <500 m", "98.69% <500 m"],
       ["median · n=100 · 9% within 100 m", "median 202.2 m · n=100", "n=31 eligible · median 12.4 m", "n=229 · median 7.9 m · non-circular"]])
para("The problem. The supplied vendor baseline is coarse where it answers at all: against the 100 independently surveyed addresses its median error is 376.4 m, only 9\\% fall within 100 m, and the pincode stratum is wrong by kilometres (Section 6). Locality names and pincodes conflict, 237 addresses lie outside any town polygon, and 25.1\\% of field visits end `address_not_traceable` after a median dwell of 1.28 min — visits that converge on #text(style: \"italic\")[our own bad pin] (84.9\\% pin-closer on the surveyed subset), not on the property (Section 6.3). A coordinate without provenance, granularity and uncertainty is therefore operationally unsafe.")
para("The approach. SUTRA resolves each address against a restricted official candidate family (frozen vendor pin, locality centroid, town centroid, official landmark, exact-text address book; after visits, evidence-backed arms), ranks with a deterministic, reason-coded RULE ranker, and fuses belief with integrity-weighted field evidence under a strict as-of discipline. Every answer carries a granularity, a tier (CONFIRMED / PROBABLE / APPROXIMATE / UNPLACEABLE), a radius taken from a measured error map with published n and coverage, and a gate decision: SERVE, VERIFY\\_FIRST or REFUSE.")
para("The research path. Nine controlled experiments (A–D plus the precision and evidence-policy passes) measured every layer before it was admitted: preprocessing ablations that closed two “obvious” retrievers by measurement; a retrieval fix (retrieval-v2) that raised the candidate ceiling from 87.67\\% to 91.44\\% within 500 m on the supervision pool while honestly showing the ranked top-1 unmoved; a model-selection study in which Logistic Regression, LambdaMART and Pairwise challengers #text(style: \"italic\")[failed to clear a pre-registered promotion gate] on S-VAL (n=69), leaving the RULE ranker in production by deliberate, documented decision; a coordinate-policy result in which the component-wise median of a visit’s last three GPS fixes cut visit-coordinate median error from 28.7 m to 7.6 m on a 233-visit temporal holdout; and a memory-integrity policy that removed the defect whereby a vendor pin could re-enter the system disguised as “place memory”.")
para("The measured outcome, in three non-interchangeable populations on the locked S-EVAL: cold start 71\\% within 500 m (median 375.8 m) — bounded by a static-lane candidate oracle of 88\\%; the full product policy 76\\% (median 202.2 m, P90 697.3 m); and the 31 addresses with eligible field evidence at the cut, 96.77\\% (median 12.4 m). On a non-circular temporal holdout the operating configuration reaches 98.69\\% within 500 m (median 7.9 m, n=229). None of these is a claim about every address; each is labelled with its population.")
para("The product. The same engine serves a six-screen operator workbench (Overview, Resolver, Places, Field Evidence, Verify Queue, Method & Trust) in which every number is fetched from the runtime, refusals render as designed decisions with no coordinate, and negative evidence widens the radius and opens a verification task without ever moving a place (Section 13). 125/125 automated tests pass and the full request path answers in a p95 of 38.9 ms against a 250 ms target (Section 15).")
para("The boundary. SUTRA is a working prototype on the official PS3 dataset, not a deployed CreditNirvana integration; no field-productivity or recovery-rate claim is made; external geodata is outside the governance boundary; the learned challengers remain offline; and the remaining work is itemised with acceptance criteria (Sections 16–17).")

# ══ 2 ════════════════════════════════════════════════════════════════════════
chapter(2, "Problem formulation and system requirements", "The central question is not “address → coordinates”. It is: given a badly written address and a poor vendor pin, which of a small set of plausible places is the record — and how much should what the field has observed change what we believe about that place?")
h2("2.1 Why one-shot geocoding fails here")
para("Three measured facts define the task (full evidence in Section 6): the vendor pin’s median error against surveyed truth is 376.4 m with a p90 of 839.2 m; the declared precision of a pin is a weak proxy for its true accuracy (locality-stratum median 385.9 m, pincode stratum 1,375.8 m); and field visits — 5,578 of them — are abundant but are #text(style: \"italic\")[evidence of varying quality], not truth: a failed visit usually describes where the agent searched, not where the property is. The system must therefore reason about unreliable pins, ambiguous locality/pincode text, incomplete official candidates, different spatial granularities and contradictory visits, and it must decide, per request, whether a coordinate should be #text(weight: \"bold\")[served, sent for verification, or refused].")
h2("2.2 Required operator decisions")
para("The product must answer four operational questions for every request: (a) #text(style: \"italic\")[which place] — a coordinate with granularity and provenance; (b) #text(style: \"italic\")[how uncertain] — a radius with measured coverage, never a bare confidence scalar; (c) #text(style: \"italic\")[what to do] — SERVE for field navigation, VERIFY\\_FIRST when evidence is thin or contested, REFUSE when unsupported or when the request purpose demands more precision than the place holds; (d) #text(style: \"italic\")[what the field changes] — how a new visit updates belief, memory and the verification queue, without ever letting a single observation fabricate or move a coordinate.")
h2("2.3 Design principles derived from the data")
panel("Evidence over inference", "Observed field observations and official tables are evidence; everything derived from them is inference and is labelled as such. A coordinate is always accompanied by its provenance (arm, source ref, as-of validity, licence class), its granularity (rooftop/street/locality/town) and its uncertainty tier and radius.")
panel("Refusal is a designed success state", "REFUSE and VERIFY\\_FIRST are first-class decisions with reasons, not errors. A geocoder that always returns a dot can look better on paper while being operationally unsafe; SUTRA counts its refusals and reports their correctness.")
panel("Negative evidence never relocates", "An `address_not_traceable` visit carries zero coordinate claim. Accumulated independent negatives may demote a tier, widen a radius, mark MOVED\\_SUSPECTED and open a task; only positive evidence or human adjudication establishes a primary coordinate.")
panel("Memory must be evidence-derived", "Place memory is keyed by physical place, never by account, and may only be emitted when its prior coordinate derives from accumulated field evidence — a prior that merely re-wraps a static pin is not memory (Section 11).")
h2("2.4 The decision contract published per request")
para("Every resolution returns: the chosen candidate with arm, granularity and provenance; the belief tier and status (e.g. CONFIRMED/STABLE, APPROXIMATE/MOVED\\_SUSPECTED, UNPLACEABLE); `radius_m` with basis (`empirical_p80`), calibration n and measured coverage; typed reason codes (`cross_arm_agreement`, `field_confirmed_x3`, `negatives_independent=k`, `promotion:ok|not_ok`, …); the gate decision with its rule and purpose; and the ranked losing candidates with losing reasons. The contract deliberately omits a bare confidence percentage and any coordinate on refusal.")

# ══ 3 ════════════════════════════════════════════════════════════════════════
chapter(3, "Dataset inventory and governance", "Twelve official tables, one surveyed-truth firewall, one coordinate system that is deliberately not latitude/longitude, and a zero-external-data policy that is enforced by hash-checked tooling.")
h2("3.1 Official tables and what shaped the design")
table(["table", "rows", "facts that shaped the design"], [
 ["addresses", "3,117", "median 67 chars; 24.9\\% without a comma; 9 without any digit; 8.4\\% Devanagari/Kannada; 237 with `town_id=OUT`; 10 duplicate normalised texts"],
 ["baseline_geocodes", "2,880", "strata: locality 2,052 · street 504 · pincode 274 · rooftop 50; no pin piles (largest coincidence = 1); coverage 92.4\\% of addresses"],
 ["field_visits", "5,578", "seven outcomes; 25.1\\% `address_not_traceable`; 443 visits under 60 s; outcomes split into place-evidence and person-evidence dimensions"],
 ["visit_gps_points", "160,406", "median 26 fixes/visit (max 80); `gps_accuracy_m` median 9.8 m; 34 axis artefacts (0.021\\%) flagged and excluded — the only drop"],
 ["surveyed_addresses", "100", "the only ground truth: T1 33 / T2 29 / T3 38; 0 OUT; 1 rooftop — firewalled from all fitting and candidate generation"],
 ["localities", "36", "35 names for 36 rows — “Nehru Colony” exists in two towns with different pincodes: pincode→locality is ambiguous by construction"],
 ["landmarks_poi", "240", "only 14 distinct names; 198 duplicate (town,name) pairs — generic names cannot be coordinate targets"],
 ["accounts / agents", "2,400 / 30", "accounts are demand context, never location features; same-account addresses sit a median 3,011.6 m apart"],
 ["towns / splits / lenders", "3 / 2,400 / 6", "account-level official split 1,680/360/360, extended by a place-block ledger; lenders imported and hash-baselined"]])
srcline("official PS3 data drop · twelve-table census · frozen baseline study")
para("Coordinates are #text(weight: \"bold\")[local metric (x, y) metres per town] (`sutra_local_metric_plane:T<n>`), not latitude/longitude; the product never invents a projection, a road graph or a lat/lon claim.")
h2("3.2 The surveyed-truth firewall and split protocol")
para("The surveyed-truth table is reserved for offline evaluation: the candidate path is proven by runtime guard never to read it, and the firewall union — 100 surveyed addresses plus their accounts and place blocks, 145 records (4.65\\% of the corpus) — is excluded from every fit. Supervision for the ranking experiments is the 292-row pool of operationally confirmed addresses (S-TRAIN 223 fit / S-VAL 69 selection), with 45 excluded and 2,680 pool-unsupervised; receipts and member-manifest hashes are frozen (receipt-hashed, protocol-v1-immutable). Grouping is two-level: #text(style: \"italic\")[outer = place block, inner = account], because signal lives in places, not rows (Section 6.5).")
h2("3.3 Data governance boundary")
para("The final project decision (binding since 2026-10-07) restricts the system to the official PS3 tables and the legitimately assigned shared tables. No external map service, third-party geocoder, downloaded gazetteer, scraped POI or external address database enters candidate generation, training or any metric. Tooling asserts zero outbound socket attempts on every experiment run; Domain A is byte-identical to its drop (hash-verified by the workspace guard). The two large shared tables assigned to other problem statements (dial attempts, payments) are excluded — the task provably has no financial outcome variable and no claim depends on one.")

# ══ 4 ════════════════════════════════════════════════════════════════════════
chapter(4, "Exploratory data analysis", "Each analysis below follows question → data → observation → insight → engineering consequence, on official tables and non-held-out diagnostics only. The EDA is the reason the system looks the way it does.")
h2("4.1 Vendor pins: declared precision is not accuracy")
para("Against the surveyed 100, the frozen vendor baseline achieves a 376.4 m median error (p80 610.0 m, p90 839.2 m, max 4,807.7 m) with 9\\% within 100 m and 71\\% within 500 m. The distribution is strongly long-tailed and the tail is stratified by declared precision: rooftop 25.6 m (n=1), street 108.6 m (n=16), locality 385.9 m (n=73), pincode 1,375.8 m (n=10). The modal stratum is locality (71\\% of pins), so the typical pin is a neighbourhood-scale claim presented as a point. Against the proxy truth on the 292-row supervision pool the picture is consistent (median 260.3 m; hit-rates 15.4\\% / 48.3\\% / 83.9\\% at 100/250/500 m; pincode-stratum median 1,392.8 m).")
fig(FIG / "fig06_01_vendor_strata.png", "Vendor error by declared precision on the surveyed 100: the pincode stratum is wrong at kilometre scale and even “street” pins carry a 108.6 m median.", "surveyed-truth stratum census (n=100)")
para("#text(weight: \"bold\")[Consequence.] A single coordinate without provenance and uncertainty is unsafe; ranking may demote coarse strata but cannot invent a house number — hence granularity tiers, a measured radius map, and VERIFY\\_FIRST as the default posture for thin evidence.")
h2("4.2 Field visits are evidence, not truth — and failed visits are not coordinate truth")
para("Visits split cleanly by geometry. Successful visits (met borrower/family, cash) sit a median 29.3 m from surveyed truth and 396.9 m from the vendor pin (3.2\\% pin-closer, median dwell 9.7 min). `address_not_traceable` visits — 1,400 of 5,578 (25.1\\%), median dwell 1.28 min — sit a median 194.7 m from #text(style: \"italic\")[our pin], and on the surveyed subset are pin-closer in 84.9\\% of cases at a median 1,603.2 m from truth: the agent walked to where the bad geocode pointed, failed, and left.")
fig(FIG / "fig06_02_visit_outcomes.png", "Outcome census and geometry: failed visits are brief and cluster near the vendor pin; successful visits are brief in neither sense — they are at the property.", "visit census (n=5,578) · outcome geometry")
callout("SAFETY", CRIT, "A failed visit describes where the agent searched. It may raise doubt, widen a radius and open a task; it may #text(weight: \"bold\")[never] author or move a coordinate. This rule (F2.1/D36) is unit-tested and alarmed.")
fig(FIG / "fig04_02_failed_geometry.png", "Failed visits are not \"no information\": the not-traceable class walks the longest approach tracks (616 m median) yet records the shortest dwell (1.28 min) — the geometry says the agent searched and left, so the visit informs doubt, not location.", "outcome-geometry census")
para("The integrity anomaly in the data is media, not GPS: agent FA009 carries 156 duplicate photo hashes across 610 visits (25.6\\%) while every other agent is below 0.3\\% and its GPS trails are clean — the evidence layer therefore weights, never accuses, and every weight ships with reason codes.")
fig(FIG / "fig04_03_agent_integrity.png", "Per-agent duplicate photo-hash rate: FA009 at 25.6\\% (156 duplicate hashes across 610 visits) against ≤0.3\\% for every other agent, while its GPS trails stay clean — the anomaly is media integrity, so the evidence layer down-weights with reason codes instead of discarding or accusing.", "agent integrity census (30 agents)")
h2("4.3 Locality and pincode traps")
para("260 addresses carry a 6-digit token matching no pincode; 237 are outside every town; the old locality matcher accepted #text(style: \"italic\")[any shared token] (“nagar”, “colony”) and let a stale pincode outvote the text, selecting the wrong locality on 118 of 292 supervision rows (centroid error median 799.5 m). Meanwhile 262 addresses are written in Kannada or Devanagari while every locality name is Latin. #text(weight: \"bold\")[Consequence:] retrieval-v2 (Section 9), a frozen text feature set that includes pin/flag features, and a script-bridge experiment that was measured and rejected because the pincode path already places those rows (Section 9.4).")
h2("4.4 Account identity is not physical-place identity")
para("191 addresses form 81 co-location clusters across #text(style: \"italic\")[different] accounts (met check-ins within 30 m; 127 cross-account pairs), while two addresses of the #text(style: \"italic\")[same] account sit a median 3,011.6 m apart. Place blocks (3,007; 81 multi-address, largest 7) therefore key the memory and the CV grouping; account IDs and commercial attributes are excluded from the feature matrix by construction, an exclusion that is audited rather than asserted (Section 8).")
h2("4.5 Agents and landmarks: attractive but inert")
para("Agent-level boxplots of baseline error show no exploitable agent effect, and the frozen 15-feature matrix contains no agent or account field — an “agent-ID-only” control cannot even be fitted without inventing a feature. The landmark table holds 240 POIs but only 14 distinct names (“Ganesh Temple” ×7, “Ration Shop” ×9 in T1): a fuzzy name match is almost always ambiguous, the landmark arm is inert on this corpus, and adding town-centroid/landmark/address-book arms leaves oracle series identical (Sections 8–9).")
h2("4.6 Spatial leakage: why random splits overstate generalisation")
para("Under the audited account-based split, 124 of 344 (36.0\\%) held-out addresses with a met visit have a train-split met check-in within 30 m (279 within 100 m), and 39 place blocks (99 addresses) cross the official split — nearby addresses share physical evidence even when accounts differ. Ordinary random splitting would therefore put near-identical places on both sides of the train/test boundary. Controls implemented: place-block ledger with outer place-block / inner account nested grouping, leave-block-out stress populations, as-of temporal filtering on all evidence features, the 145-record firewall, and a 12-pattern banned list enforced by the leakage guard (including the by-name ban on “check-in agrees with our pin” as a feature). Residual risk is disclosed, not hidden: the supervision pool is selected by visit outcome, so every ranking number is conditional on that pool.")
fig(FIG / "fig04_04_truth_split.png", "The surveyed truth is small and deliberate (T1 33 / T2 29 / T3 38) and fully firewalled; the official split keeps 32 OUT-town addresses in test, so held-out evaluation includes the hardest rows by construction.", "ground-truth and split ledgers")

# ══ 5 ════════════════════════════════════════════════════════════════════════
chapter(5, "Modeling methodology and training pipeline", "From raw tables to a frozen 15-feature candidate-level design matrix, relevance grades from an operational proxy label, grouped fitting on 223 addresses, and a promotion gate that was designed to be able to say no.")
h2("5.1 Labels: an operational proxy, never the surveyed truth")
para("Fitting and selection use `operational_confirmation_proxy` — the component-wise median of independently promoted check-ins available strictly before the as-of cut (the as-of replay module) — because the 100 surveyed truths are firewalled. Candidate rows receive relevance grades 3/2/1/0 at ≤100/250/500 m and beyond. The proxy is disclosed as a proxy: evidence arms reproduce it by construction, which is exactly why the warm lane is labelled a circular diagnostic and why non-circular temporal holdouts and the single locked S-EVAL read carry the evidential weight.")
h2("5.2 Candidate-level features: the frozen 15")
para("The design matrix is candidate-level (each row = one candidate for one address) and frozen at 15 features, each audited for source, as-of status and permissibility: `f_arm_prior`, `f_granularity_rank`, `f_locality_name_matched`, `f_pin_in_text`, `f_pin_unknown`, `f_no_digit`, `f_no_separator`, `f_outside_town`, `f_baseline_stratum`, `f_sim_jaccard`, `f_sim_char3`, `f_sim_ratio`, `f_n_candidates`, `f_agreement_count`, `f_dist_to_town_centroid_m`. Five carry pre-registered monotone constraints (similarities and granularity ↑, distance to town centroid ↓), enforced structurally per tree and #text(style: \"italic\")[tested] for the unconstrained logistic fit — a violation is a finding, not a refit trigger. No agent, account, truth, outcome or visit field exists in the matrix; the audit replaces an “agent-only control” that could not be fitted without inventing a feature.")
h2("5.3 Splits, fitting and validation procedure")
para("S-TRAIN (223 addresses, 762 candidate rows) fits; grouped S-VAL (69 addresses, 240 rows) early-stops — a pre-registered rule whose consequence is stated plainly: S-VAL figures for learned models are selection-contaminated, so the out-of-fold lens (5 spatial folds, every place block wholly inside one fold, inner account-grouped stopping) is reported beside them as the unbiased reading. Grade mix on the pool: 61 ≤100 m, 185 ≤250 m, 283 ≤500 m, 473 beyond. Hyperparameters are exactly the pre-registered set (≤300 trees, depth ≤4, lr 0.05, subsample 0.8, L2 leaf 1.0, min-data-in-leaf); the trees stop after 1–11 on the grouped early-stopping signal. Primary metric: top-1 hit within 500 m; paired grouped bootstrap over place blocks, 10,000 resamples, seed 7, both directions tested.")
h2("5.4 The promotion gate")
para("Adopt a learned ranker only if it beats RULE on the primary S-VAL metric beyond the paired interval, regresses nothing (coverage, per-stratum n≥15, refusal behaviour, availability, latency, leakage), and stays directionally consistent on leave-block-out. The gate also runs negative controls: shuffled-label LambdaMART must collapse (it does: 23.19\\% vs 84.06\\%), pin-only must reproduce RULE’s top-1 exactly (it does — the rule’s value is tie-breaking, not geometry), and outbound calls must be zero (they are).")

# ══ 6 ════════════════════════════════════════════════════════════════════════
chapter(6, "Model experiments and selection", "The deliberate result of the selection study: the simplest validated ranker — the deterministic, reason-coded RULE — remains production. Model complexity alone was tested and found not to be evidence for deployment.")
h2("6.1 The final frozen scoreboard (S-VAL, n=69)")
table(["ranker", "<100 m", "<250 m", "<500 m", "median", "nDCG@5", "decision"], [
 ["#text(weight: \"bold\")[RULE (shipped)]", "15.94\\%", "50.72\\%", "#text(weight: \"bold\")[84.06\\%]", "249.0 m", "#text(weight: \"bold\")[0.9670]", "retained"],
 ["LOGISTIC", "17.39\\%", "49.28\\%", "81.16\\%", "258.0 m", "0.9516", "rejected"],
 ["LAMBDAMART", "15.94\\%", "50.72\\%", "84.06\\%", "249.0 m", "0.9640", "rejected"],
 ["PAIRWISE", "15.94\\%", "50.72\\%", "84.06\\%", "249.0 m", "0.9653", "rejected"],
 ["LAMBDAMART-shuffled", "10.14\\%", "31.88\\%", "56.52\\%", "398.3 m", "0.8090", "control"]])
srcline("frozen selection scoreboard (S-VAL n=69) · implementation report §3.7 · notebook cells 44–46")
fig(FIG / "fig08_01_challengers.png", "No challenger cleared the gate: LOGISTIC is a point worse on the primary metric and fails the monotone structural check (f_sim_ratio fitted −0.0133, f_dist_to_town_centroid_m +0.3597); LAMBDAMART and PAIRWISE produce top-1 series identical to RULE at strictly worse nDCG.", "final frozen Experiment-D scoreboard")
h2("6.2 Why the models do not generalise — measured, not asserted")
para("In-sample the trees reach 84.75\\% with the early-stopping signal already optimal at tree 1, and on S-TRAIN learned models marginally beat RULE (84.75 vs 83.86); out-of-fold the advantage evaporates. The headroom decomposition explains it: on S-VAL the rule’s top-1 is already the best available candidate on 55.1\\% of addresses (38/69); a strictly better candidate exists for 17 addresses with a median waiting gain of 138 m; a perfect ranker — which does not exist — could reach only 20.29\\% at 100 m and 89.86\\% at 500 m. The entire reordering headroom is +0.04/+03. Ranking is not where the remaining error lives; the candidate set is (Section 7). LambdaMART split usage (not causal) concentrates on `f_dist_to_town_centroid_m`, `f_arm_prior` and the similarities — provenance and precision dominate, reinforcing the systems conclusion.")
h2("6.3 Provenance note: two Experiment-D runs")
para("The project preserves two Experiment-D artefacts. The earlier run (receipt cf8e9683…) reported RULE nDCG\\@5 0.9291 and LOGISTIC 82.61\\%/224.7 m on S-VAL, and on the locked S-EVAL read LOGISTIC 0.81 vs RULE 0.71 (resolved better on that population — while losing on S-VAL, the declared decision population, so the gate still rejected it). After documented repairs (a row-truncation bug that passed stripped candidate dicts to the rule interface, and a one-sided-test labelling defect) and the final frozen configuration (`9abebb8f…`), the re-run produced the scoreboard above, in which no challenger beats or resolves better than RULE on any population. The notebook and implementation report agree on the frozen values to the last digit; the earlier receipt is retained and labelled superseded. A later precision-pass re-test on retrieval-v2 candidates reached the same conclusion from the other direction: LOGISTIC 82.61\\% (not resolved), LAMBDAMART identical, PAIRWISE 59.42\\% resolved worse (−0.2464). The report therefore states, consistently throughout: #text(weight: \"bold\")[production serves the deterministic RULE ranker; learned challengers are offline.]")

# ══ 7 ════════════════════════════════════════════════════════════════════════
chapter(7, "Candidate generation and ranking research", "Candidate availability and candidate selection are separate problems. The project improved the former, proved the latter near-empty of headroom, and rejected every generator that harmed more cases than it rescued.")
h2("7.1 The restricted official family and its ceiling")
para("Five static arms answer a cold address: `frozen_baseline`, `locality_centroid`, `town_centroid`, `official_landmark`, `address_book`; after visits, `field_evidence` and (eligibly) `memory`; `place_neighbour` exists in code and stays locked. Over the full book the static lane covers 92.4\\% of addresses with a median of 3 candidates. Experiment C keeps four quantities apart that are routinely conflated — retrieval coverage, retrieval recall, the oracle ceiling, and the ranked answer — and ladders the arms: on S-EVAL the baseline-only oracle is 376.4 m/71\\%, adding locality centroids lifts the ceiling to 88\\% (285.8 m), landmarks to 255.8 m; the final static-lane oracle is 88\\% within 500 m (median 254.1 m) on S-EVAL and 89.86\\% (184.7 m) on S-VAL. The absolute “best of every official point” bound is 1.00 at 38.8 m median — an existence proof requiring the answer, reported to bound the information, not to claim it. #text(weight: \"bold\")[The 90\\% cold-start target is therefore not reachable from the official data; that is a bound, not an opinion.]")
h2("7.2 Retrieval-v1 → v2: fixing locality matching, honestly measured")
fig(FIG / "fig09_01_retrieval.png", "Retrieval-v2 raises the candidate ceiling (87.67→91.44\\% within 500 m on the pool; locality-candidate median error 811.9→319.6 m) while the ranked top-1 stays at 83.9\\%: the rule still chooses the vendor pin, and that is the honest reading.", "data/derived/precision_optimization_report.md §1")
para("Retrieval-v2 requires every token of the locality name (coverage ≥0.5) including the name’s rarest token by IDF, tie-breaks deterministically, and emits #text(style: \"italic\")[all] localities of an ambiguous pincode instead of the first. The improvement is real and the non-improvement is real: candidate generation and candidate selection are different problems, and the report refuses to oversell the former as a top-1 win.")
h2("7.3 The bottleneck taxonomy (supervision pool, n=292)")
fig(FIG / "fig05_01_taxonomy.png", "Of 292 pool rows, 245 resolve within 500 m; 22 have a better candidate that cannot be chosen without breaking more cases; 19 have nothing within 500 m (best is a centroid); 6 are pincode-coarse retrieval failures.", "data/derived/precision_optimization_report.md §2")
h2("7.4 Rejected candidate generators — negative results as research output")
table(["generator", "coverage", "median", "rescued", "worse", "verdict"], [
 ["address-book near-duplicate", "42.81\\%", "247.0 m", "1", "66", "rejected: harms 66× more than it rescues"],
 ["pincode-consistent locality", "85.27\\%", "321.9 m", "0", "144", "rejected: pure harm on this corpus"],
 ["script lexicon (Kannada/Devanagari)", "33 rows", "315.1 m", "0", "—", "rejected: pincode path already places them (250.6 m)"],
 ["archetype routing", "—", "248.9 m", "—", "—", "rejected: every archetype’s best arm is the pin; the router is the rule (Δ 0.0)"],
 ["sibling-pin transfer", "39 rows", "329.5 m", "9/39", "—", "dead end, closed"],
 ["empirical locality centres", "264 rows", "321.6 m", "126/264", "—", "supplied centroids already good; kept as negative control"],
 ["preprocessing residue (TF-IDF/SVD, parser)", "0", "—", "0", "—", "byte-identical universes, 1.26–4.73× latency; closed by measurement (Experiment B)"]])
srcline("precision-study ledger §5 · negative-result register")
para("The landmark arm is likewise inert: only 32/292 pool rows carry a recognisable landmark mention, the nearest same-type POI sits a median 269.4 m away, and per-town same-type POIs number about 6 — a name alone cannot identify the landmark without the relation word. `place_neighbour` beats its placebo (61.9 m vs 2,162.1 m) but changes zero product answers and does not clear its C2 admission bar: measurable is not the same as admissible; it stays #text(weight: \"bold\")[locked].")

# ══ 8 ════════════════════════════════════════════════════════════════════════
chapter(8, "GPS estimation and evidence processing", "A visit is a track, not a dot: the component-wise median of the last three fixes — taken while the agent is at the address — replaces the single check-in as the ingested coordinate, with the raw check-in retained as provenance and fallback.")
h2("8.1 The trace-tail estimator")
fig(FIG / "fig10_01_trace_tail.png", "Non-circular cross-cut evaluation (n=233): estimator applied to visits before T0, judged against visits after T0. The within-100 m rate rises 76.39→86.27\\% and the median error falls 28.7→7.6 m; the cold lane is identical under either label (0.8459), so the gain is attributable to the estimator, not a moved goalpost.", "frozen coordinate-policy ledger · trace-tail holdout (n=233)")
para("The official `visit_gps_points` table holds the agent’s approach track (median 26 fixes, up to 80); the last three fixes are recorded at the address and their component-wise median averages out single-sample check-in error. Label shift across the cut is 13.7 m median; promoted check-ins disagree with each other by only 39–43 m across a mid-quarter cut at 97–99\\% within 500 m, while `gps_accuracy_m` has a 9.8 m median: #text(style: \"italic\")[the check-ins are the precise signal and the vendor pin is the noisy one].")
callout("LIMITATION", WARN, "This is a #text(weight: \"bold\")[visit-coordinate-estimation] result. It states where a visit happened, more precisely. It is not cold-start address-geocoding accuracy and is never reported as such.")
h2("8.2 Outcome semantics and integrity weighting")
para("Each visit stores an evidence score with two dimensions, `w_place` and `w_person`, composed from outcome dimension × dwell band × trail agreement × media integrity × accuracy class × rolling agent baseline × recency; no single signal zeroes a visit, and absence of usable evidence is a recorded state (`insufficient_evidence`), not an accusation. Outcomes are split by dimension: `locked_premises` is weak place-positive/person-indeterminate; `no_such_person` is place-positive/person-negative. Promotion to a belief-moving observation requires two independent confirmations (different visit, different day, sufficient weight, not traceable to the same media hash or agent-day cluster).")
h2("8.3 Negative evidence and the no-relocation invariant")
para("The frozen rules: one negative never relocates; graded negatives accumulate from two independent observations (`NEG_ACCUMULATION_MIN=2`); negatives can demote a tier, widen the radius, mark MOVED\\_SUSPECTED and open a verification task. Measured on the full universe: 130 addresses carry negative observations, #text(weight: \"bold\")[0 relocations by a negative]. The acceptance suite includes dedicated tests (T2: one negative leaves the coordinate unchanged; T3: independent negatives raise doubt out loud; T4: fake independence is rejected).")
h2("8.4 As-of discipline")
para("Every read is as-of (`observed_at < as_of`); evidence arms carry `as_of_valid` and vanish for queries before their observation; belief is recomputable at any instant (`GET /v1/belief/{id}?as_of=…`). The temporal holdouts (Section 10) build candidates strictly from pre-T0 evidence and label with post-T0 promoted check-ins, so future information can be an evaluation outcome but never a historical input.")

# ══ 9 ════════════════════════════════════════════════════════════════════════
chapter(9, "Physical-place memory and uncertainty policy", "Memory is keyed by physical place, append-only, contradiction-holding, and may only speak when its prior derives from accumulated field evidence — the defect that let a vendor pin masquerade as memory was measured, removed, and shipped as a defect removal, not an accuracy claim.")
h2("9.1 Co-location evidence and place keying")
para("The EDA showed 191 addresses in 81 cross-account co-location clusters and same-account addresses kilometres apart (Section 4.4). Memory therefore keys on place blocks built from met-check-in proximity (≤30 m) and adjudication — `colocation<=30m|adjudicated` — never on account identity. Beliefs are versioned rows (position, tier, radius, support, reasons); observations are the only clock; nothing is overwritten or averaged; contradictions are a state (CONTESTED) with both supports kept, a widened radius and a queued task; staleness (no positive older than 365 days → STALE) is visible, never silent.")
h2("9.2 The pin-derived memory defect, measured")
para("Under the shipped policy the memory arm was chosen on 29 of 292 pool rows and was weak where chosen (\\<100 m 17.24\\%, median 337.9 m) while field evidence was strong (95.82\\%). Ten pool rows exceeded 500 m; in #text(weight: \"bold\")[seven] the emitted “memory” candidate was within 5 m of the vendor pin — the memory had remembered a pin and called it memory, then outranked real check-ins via a primary-eligibility bonus. The cleanest harm evidence: materialising an on-demand prior #text(style: \"italic\")[without] the evidence-derived emit rule collapses the temporal \\<100 m rate from 89.03\\% to 64.98\\%.")
h2("9.3 The frozen policy (emp-v1) and how to read its effect")
para("The frozen rule: a prior may become memory only if its tier is CONFIRMED/PROBABLE #text(style: \"italic\")[and] its coordinate derives from accumulated field evidence; priors that re-wrap static arms are not emitted. Challengers were tested on S-TRAIN/S-VAL, two temporal cuts and leave-block-out with paired place-block bootstraps (quality tiering of singles: no effect; fewer singles: regression; GPS-accuracy gates: no effect; quality-ordered tie-break: regression — the shipped id tie-break stands). On the locked S-EVAL the warm licence narrows from 45 to 31 answered addresses while accuracy rises (82.22→96.77\\% at 500 m; 57.78→83.87\\% at 100 m; median 16.4→12.4 m); the product lane is bit-identical (33/55/76\\%, 202.2 m) because the 14 withheld answers were the pin re-wrapped and those addresses still receive the pin coordinate with pin radius and VERIFY\\_FIRST semantics.")
fig(FIG / "fig11_01_memory_policy.png", "Fewer answers, better evidence: withholding pin-derived memory claims is not withholding answers. The policy shipped as a parameter-free, one-flag-revertible defect removal; on S-VAL alone the gain is +0.0290 [0.0000, +0.0725], read as a power limit, so no validated accuracy gain is claimed.", "memory-policy ledger (locked S-EVAL)")
h2("9.4 Uncertainty: a published contract, honest about thin data")
para("Every answer carries granularity, tier, and `radius_m` from the empirical p80 of measured error per baseline stratum, with n and measured coverage published: locality 539.9 m (n=24, coverage 0.792, publishable); street 162.1 m (n=5) and pincode 1,204.2 m (n=4, coverage 0.000) are #text(style: \"italic\")[withheld] below the n≥15 guard and fall back to the locality radius, widened and labelled `calibration_fallback`; rooftop (n=1) is insufficient. Negative accumulation widens the published radius (e.g. 566.9→1,202.6 m on the canonical AD002936 trajectory) without moving the centre. Refusals carry no radius and no coordinate.")

# ══ 10 ═══════════════════════════════════════════════════════════════════════
chapter(10, "End-to-end architecture", "One production request path, one field-evidence path, and an offline evaluation lane that is structurally unable to touch production — the separation is enforced in code, imports and tests, not in prose.")

def arch_png():
    """Rasterize the vector diagram by compiling it alone with typst."""
    import typst, pypdfium2 as pdfium
    tmp = SRC / "typst" / "svg_only.typ"
    tmp.write_text('#set page(width: 176mm, height: 190mm, margin: 0mm, fill: rgb("#FBF9F2"))\n#image("../figures/diagram_architecture.svg", width: 100%)\n')
    tmp_pdf = SRC / "typst" / "svg_only.pdf"
    font_dir = None
    try:
        import matplotlib
        font_dir = str(Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf")
    except ImportError:
        pass
    typst.compile(str(tmp), output=str(tmp_pdf), root=str(ROOT),
                  font_paths=[font_dir] if font_dir else None, ignore_system_fonts=bool(font_dir))
    img = pdfium.PdfDocument(str(tmp_pdf))[0].render(scale=3.2).to_pil().convert("RGB")
    from PIL import Image as _I, ImageChops
    bg = _I.new("RGB", img.size, img.getpixel((0, 0)))
    bbox = ImageChops.difference(img, bg).getbbox() or (0, 0, img.width, img.height)
    out = SRC / "figures" / "diagram_architecture.png"
    img.crop(bbox).save(out)
    tmp.unlink(missing_ok=True); tmp_pdf.unlink(missing_ok=True)
    return out

fig(arch_png(), "System architecture. Orange: implemented production components. Green: field evidence and belief update. Plum: place memory. Slate: offline experiments and the promotion gate, which feeds no request-path module. Schematics are labelled as such; every box maps to a live service component.", "system schematic · every box maps to a live service component", width=6.6)
h2("10.1 Production request path")
para("Raw address → deterministic normalisation (NFKC, corpus abbreviation table, script-preserving spans; Experiment B kept this as the cheapest non-resolved-worse ring) → town/locality entity resolution (retrieval-v2) → official-only candidate generation (five static arms plus eligible evidence arms, as-of filtered) → deterministic RULE ranker (additive, reason-coded; the ranking module, byte-unchanged by the model study) → belief and uncertainty assessment (tier, status, radius map v1, reason codes) → eligibility gate v2 with request purpose → SERVE / VERIFY\\_FIRST / REFUSE with the full decision ticket and ranked losers. Latency p95 38.9 ms for the whole path (Section 15).")
h2("10.2 Field evidence path")
para("Field visit with GPS trace → tail-3 coordinate estimator (check-in retained as provenance/fallback) → integrity weighting (media hash, trail↔check-in agreement, dwell realism, speed plausibility, agent-deviation z-scores; weights and reasons, never accusations) → append-only belief update (bounded: one visit moves belief at most one tier step and never promotes alone; idempotent by visit\\_id) → place memory and, when doubt crosses thresholds, verification tasks. A `score_visit` endpoint simulates “what would this visit change” on a throwaway store copy and discards it — advisory by construction.")
h2("10.3 Offline lane and persistence")
para("Experiment scripts (A–D, precision, evidence-policy) run on frozen data with fixed seeds; fits happen in memory, no model file is written, and no request-path module imports the challenger library (asserted by the import guard). Runtime persistence is a local SQLite store (schema store-2: 5,578 observations, 2,757 belief versions) plus versioned runtime indexes (addresses, localities, town centroids, token IDF, place blocks, memory) and offline packs (each stamped `contains_truth: false`). The slow retraining loop of the early design remains DESIGNED/NOT IMPLEMENTED; the fast evidence loop is IMPLEMENTED — and the report says so on the Method & Trust screen itself.")
h2("10.4 Component map")
para("At the centre sits the engine itself: a small, dependency-light core of 28 modules covering resolution, candidate generation, ranking, belief, uncertainty, evidence, memory, eligibility, request purpose, as-of handling, feeds, the product layer, the offline lane and the store. Around it sit the guard and reproduction tooling (more than forty diagnostic scripts), the React operator workbench served by the runtime API, the frozen data vault with its evaluation ledgers and receipts, the master training notebook, and a 125-test suite that pins every safety invariant in code.")

# ══ 11 ═══════════════════════════════════════════════════════════════════════
chapter(11, "Product walkthrough", "Genuine captures of the served workbench (2026-10-08, as-of 2026-06-01T00:00:00Z). Every value on every screen is fetched from the running service, and a no-fake-data test scans the served bundle so that no invented number can reach a screen.")
h2("11.1 Overview — the workbench, not a dashboard")
fig(SHOT / "bm-01-overview.png", "Operations overview at the frozen cut: 3,117 indexed addresses; 566 answered with a location (911 approximate · 295 probable · 271 confirmed); 278 cases needing the field (273 moved-suspected · 5 contested); 3,788 field-visit rows. Panel A publishes the three frozen populations side by side, with the sentence that governs them: “These populations are separate by construction. They are not merged into one accuracy figure.” Panel E states the version strings and the sealed-evaluation read counter.", "live workbench capture · GET /v1/overview", width=6.6)
h2("11.2 Resolver — messy address to decision")
fig(SHOT / "bm-02-resolver-serve.png", "A SERVE-grade resolution (AD003067): eight possible places ranked with the engine’s own terms; the chosen field-evidence candidate (score 0.99, street granularity) with its reason terms; the local metric plane with the uncertainty ring (566.9 m, empirical p80, widened) and cross-highlighting between candidate list, map and decision panel; measured coverage 79.2\\% at n=24; “what moved the score — not a confidence percentage”.", "live workbench capture · POST /v1/resolve, GET /v1/geometry", width=6.6)
para("The canonical SERVE ticket carries: tier CONFIRMED / status STABLE; candidate `c-28f5aface67c`, arm `field_evidence`, `source_ref visits:median(3)`, `as_of_valid 2026-05-15T05:35:37Z`; radius 566.9 m with basis, n and coverage; support 6 observations / 4 positive / 1 independent negative / 3 independent confirmations; typed reason codes including `field_confirmed_x3` and `negatives_independent=1`; and a direction cue flagged `ambiguous: true` — the landmark relation is shown as a hint, never as a location.")
fig(SHOT / "bm-03-resolver-verify-first.png", "VERIFY\\_FIRST (AD002936): APPROXIMATE / MOVED\\_SUSPECTED after two independent negatives; radius widened to 1,202.6 m; the coordinate unchanged. The runner-up memory arm is shown with its losing reason.", "live workbench capture · resolver, verify-first mode", width=6.6)
fig(SHOT / "bm-09-transition.png", "The belief rail stepped through nine real visit instants (2026-04 → 06): tier CONFIRMED→APPROXIMATE, radius 566.9→1,202.6 m, queue entry raised — “doubt moved the radius, the tier and the queue, not the place.”", "live workbench capture · belief transition rail", width=6.6)
h2("11.3 Refusal as a designed success state")
fig(SHOT / "bm-05-refusal.png", "AD000006 (town OUT): tier UNPLACEABLE, no candidate, no coordinate field anywhere in the body; the plane renders the withheld state. A second refusal mode (AD000002 under NOTICE\\_SERVICE) refuses the #text(style: \"italic\")[action] — the place is APPROXIMATE-grade but the notice decision demands SERVE-grade evidence.", "live workbench capture · refusal envelopes", width=6.6)
h2("11.4 Places, Field Evidence, Verify Queue, Method & Trust")
fig(SHOT / "bm-06-places.png", "Places: 3,117 place records keyed by co-location/adjudication (CONFIRMED 271 · MOVED\\_SUSPECTED 273 · WARM 300 · COLD 2,268 · CONTESTED 5), each with state, tier, members, radius and basis — account identity never maps to a coordinate.", "live workbench capture · Places", width=6.6)
fig(SHOT / "bm-07-evidence.png", "Field Evidence: 3,788 stored observations with the policy’s verdict per row (positive 1,539 / negative 1,141 / ambiguous 1,108); a negative keeps its device position but is labelled `coordinate_claim: false`; the selected visit discloses its weight in the belief chain.", "live workbench capture · Field Evidence", width=6.6)
fig(SHOT / "bm-08-queue.png", "Verify Queue: 278 open cases with cause, priority, `negatives_independent`, radius and rule version; transitions are append-only (open → in\\_progress → resolved → reopened); adjudication writes an observation and replays the frozen belief mechanism — a reviewed AD002936 confirmation left tier, status and coordinate unchanged (`coordinate_moved: false`).", "live workbench capture · Verify Queue", width=6.6)
fig(SHOT / "bm-11-method.png", "Method & Trust: the nine version strings, the gate table with live reasons, the radius map with the n≥15 guard visible, the five invariants, and the two loops labelled honestly — fast loop IMPLEMENTED, slow loop NOT YET IMPLEMENTED, learned challenger “EVALUATED, REJECTED — not in the request path”.", "live workbench capture · Method & Trust", width=6.6)
callout("PRODUCTION", ACCENT, "Prototype boundary, stated on the product itself: this workbench demonstrates the intended operator workflow against the frozen runtime. It is not evidence that a CreditNirvana production integration is deployed; integration work is itemised in Sections 16–17.")

# ══ 12 ═══════════════════════════════════════════════════════════════════════
chapter(12, "Experimental evaluation", "Five separate evaluation lanes, each with its own population, label source and legitimate claim. The lanes are never merged.")
h2("12.1 The locked S-EVAL lanes (one read of frozen configuration 9abebb8f…)")
table(["lane", "n", "<100 m", "<250 m", "<500 m", "median", "p90"], [
 ["cold start (static arms)", "100", "9\\%", "35\\%", "71\\%", "375.8 m", "810.8 m"],
 ["product policy (warm→cold)", "100", "33\\%", "55\\%", "#text(weight: \"bold\")[76\\%]", "202.2 m", "697.3 m"],
 ["warm / evidence subset", "31", "83.87\\%", "93.55\\%", "#text(weight: \"bold\")[96.77\\%]", "12.4 m", "195.9 m"],
 ["static-lane oracle (ceiling)", "100", "—", "—", "88\\%", "254.1 m", "—"]])
srcline("sealed S-EVAL ledger · surveyed ground truth")
para("Per town (product): T1 66.67\\% (367.3 m, n=33) · T2 82.76\\% (126.4 m, n=29) · T3 78.95\\% (162.1 m, n=38); none below the n-guard. The product-vs-cold delta (+5 pts at 500 m) is [0.00, +0.101] — not resolved at n=100, and the report says so.")
fig(FIG / "fig14_01_regimes.png", "The three S-EVAL regimes at each threshold. The warm subset is the 31 addresses with eligible evidence at the cut — it is not a claim about all addresses; the product lane answers all 100.", "sealed S-EVAL ledger (three regimes)")
h2("12.2 Non-circular temporal holdouts")
fig(FIG / "fig14_02_temporal.png", "T0=2026-05-15: cold 84.72\\% (271.2 m) vs product 98.69\\% (7.9 m) vs promoted-only 100\\% (6.1 m); paired vs cold +0.1397 [0.0938, +0.1888] resolved. The T0=2026-05-01 cut agrees (product 98.88\\%, 8.6 m). Labels are promoted post-T0 check-ins — strong evidence, #text(style: \"italic\")[not] surveyed truth.", "temporal holdout ledger (T0 = 2026-05-15)")
h2("12.3 Candidate-oracle and ranking-stability references")
para("The static-lane oracle is 88\\% (S-EVAL) / 89.86\\% (S-VAL): the candidate family’s reach, not SUTRA’s prediction. Prefix recall shows where usable candidates sit before ranking (S-EVAL \\@1 0.71, \\@3 0.85, \\@5 0.88). Retrieval-v2 changed the ceiling but not the ranked top-1 (83.9\\% both versions, pool) — availability and selection stay separate in every table of this report.")
h2("12.4 How to read the headline numbers")
para("Cold 71\\% measures official-only information on 100 surveyed addresses; product 76\\% measures the shipped policy on the same 100; warm 96.77\\% measures only the 31 eligible evidence-backed answers; temporal 98.69\\% measures the operating configuration against future field evidence on 229 labels; the 88\\% oracle measures what the candidate set contains. No pair of these shares a population, and none is a business-outcome claim.")

# ══ 13 ═══════════════════════════════════════════════════════════════════════
chapter(13, "Runtime performance, acceptance and engineering quality", "Verified in-session, on copies of the shipped store, with measurement conditions stated — including what was not measured.")
h2("13.1 Acceptance and contract suites")
table(["suite", "tests", "what it pins"], [
 ["Acceptance suite", "26", "evidence/belief invariants: T1 no candidate ⇒ no coordinate; T2 one negative ⇒ coordinate unchanged; T3 independent negatives ⇒ doubt out loud; T4 fake independence rejected; T5 valid confirmations promote; pincode-radius withholding; offline outbox replay"],
 ["Frontend-contract suite", "51", "the frontend contract: alternatives are the ranked losers with lost-reasons; belief read is the authoritative object; refusal envelopes carry no coordinate; reason codes typed; geometry is local metric"],
 ["Product-layer suite", "39", "product layer: append-only task lifecycle; adjudication replays belief; score_visit writes nothing; batch resolve bounded ≤5,000 with aggregate refusal/tier/histogram, never bulk accuracy"],
 ["No-fake-data suite", "9", "no invented providers/scores/trails in console #text(style: \"italic\")[or workbench] sources or built bundle; every called route is real"]])
srcline("acceptance ledger · 125/125 passed in 26.8 s")
h2("13.2 Latency")
para("Full request path including gate-decision logging, 400 requests on a copy of the runtime store: mean 23.2 ms · p50 21.7 · p95 38.9 · p99 53.8 · max 64.6 ms, against a 250 ms p95 target — #text(weight: \"bold\")[MET]. Candidate generation over the full book runs at p95 23.1 ms/address. Challenger scoring costs (≤0.3 ms/address) were material but not the deciding factor. #text(style: \"italic\")[Not published by the product:] live latency percentiles, error rates and queue depths — the workbench deliberately does not estimate them (visible in the System Health panel).")
h2("13.3 Integrity and reproducibility")
para("Official dataset hash-verified byte-identical; 0 outbound socket attempts on every experiment; seed 7 with 10,000-resample paired place-block bootstraps; split receipts and firewall hashes frozen; the S-EVAL read ledger is disclosed including the reads that went wrong during tooling (no parameter ever changed in response to a S-EVAL number; final runs reuse persisted snapshots and spend zero reads). A single reproduction chain regenerates the ledgers, the fits and the workbench build; the import, workspace and link guards run on every pass (two historical link warnings are archived and labelled, not hidden).")

# ══ 14 ═══════════════════════════════════════════════════════════════════════
chapter(14, "Governance, limitations and integration readiness", "What the system may not claim is as important as what it may. This section fixes the boundary between engine-tested behaviour, the live prototype, and future CreditNirvana integration.")
h2("14.1 Official-data and evaluation boundaries")
para("External geography is prohibited by the binding freeze decision; the task has no financial outcome variable (dial/payments tables excluded); surveyed truth is evaluation-only and read under a disclosed counter; the supervision pool is selected by visit outcome, so ranking numbers are conditional on that pool (exposure bias is stated, with propensity logging as the eventual remedy); visits span 90 days with no known regime change, so drift behaviour remains a labelled simulation from the early design, not a measurement.")
h2("14.2 Safety constraints held in code")
para("No candidate ⇒ no coordinate; one negative never relocates; memory emits only evidence-derived priors; sub-guard strata fall back widened and labelled; refusal payloads carry no coordinate; adjudication is append-only and idempotent; the product layer may only append task events (source-scanned test); write paths run against byte-copies of the store.")
h2("14.3 Prototype boundaries (implemented vs demonstrated vs not implemented)")
table(["status", "content"], [
 ["#text(weight: \"bold\")[IMPLEMENTED]", "official-only candidate generation; retrieval-v2; RULE ranking; belief/uncertainty with radius-map-v1; eligibility gate v2 with purpose; evidence integrity and append-only belief; place memory and emp-v1; as-of reads; offline packs and outbox; the six-screen workbench bound to the real service; 125 tests; full API surface incl. adjudication and audit chain"],
 ["#text(weight: \"bold\")[EVALUATED, OFFLINE]", "Logistic/LambdaMART/Pairwise challengers; preprocessing rings B3/B4; place_neighbour (locked); the slow retraining loop (designed, gated, not built)"],
 ["#text(weight: \"bold\")[NOT IMPLEMENTED]", "continuous online retraining; LLM address parsing; RL visit allocation; external map matching; a CreditNirvana production integration; any field-productivity, recovery-rate or failure-rate outcome claim (requires a controlled field evaluation with an exploration slice)"]])
para("The live Vercel deployment demonstrates the intended operator workflow against the frozen runtime; UI capability is not deployment evidence, and the Method & Trust screen states the same boundary in product language.")

# ══ 15 ═══════════════════════════════════════════════════════════════════════
chapter(15, "Prioritized roadmap and conclusion", "Model optimisation stops here by measured decision. The remaining work is productisation, integration and one properly powered evaluation — each item with an acceptance criterion.")
table(["P", "item", "acceptance criterion", "class"], [
 ["P0", "Surface radius ring, belief rail and pack-age chip in the workbench (payloads already shipped)", "renderer consumes /v1/geometry and /v1/belief as-of; no client-side re-derivation; no-fake-data test stays green", "frontend"],
 ["P1", "Adjudication write path + task state transitions in production wiring", "append-only receipts; reopen-before-second-decision enforced; contract tests green on shipped store copy", "backend"],
 ["P1", "Single-call audit chain GET /v1/audit/{belief_id} exposed end-to-end", "evidence weights, losers, uncertainty change and tasks reconstructable in one call", "backend"],
 ["P1", "CreditNirvana integration contract (auth, tenancy, CRS handling for real coordinates)", "interface spec signed; no frozen module modified; latency budget re-verified", "integration"],
 ["P2", "Propensity logging + exploration slice for exposure bias", "first live window logs allocation propensities; weighted vs unweighted metrics published side by side", "evaluation"],
 ["P2", "Controlled field evaluation of productive-visit and verification outcomes", "pre-registered primary metric; exploration slice; no claim published without it", "evaluation"],
 ["P3", "Revisit learned rankers only if the candidate ceiling moves", "oracle recall must rise beyond the paired interval before any new selection study", "research"]])
panel("Conclusion", "SUTRA does not claim that a larger model automatically solves address geocoding — it tested that hypothesis and recorded the result. The deeper investigation exposed candidate quality as the binding cold-start constraint (an 88\\% static-lane oracle on the locked set) and showed that trusted field observations create a materially different operating regime (96.77\\% on eligible evidence-backed answers; 98.69\\% on the temporal proxy). The system therefore combines a deterministic, reason-coded ranker with published uncertainty, integrity-weighted evidence, an append-only place memory that cannot be poisoned by its own vendor pin, and a product surface in which doubt is a visible, actionable state. It does not merely guess a coordinate once; it builds evidence about places over time and uses that evidence to make future decisions better. #text(weight: \"bold\")[Resolve → Verify → Learn → Resolve Better.]")

# ══ 16 ═══════════════════════════════════════════════════════════════════════
chapter(16, "Technical appendix and reproducibility", "Feature and configuration tables, metric definitions, the evidence ledger for every headline number, and the commands that reproduce the chain.")
h2("A.1 Frozen 15-feature design matrix")
table(["feature", "source", "as-of / status"], [
 ["f_arm_prior", "candidate’s own arm (provenance)", "query-time · allowed"],
 ["f_granularity_rank", "candidate granularity rooftop>street>locality>town", "static · allowed"],
 ["f_locality_name_matched", "address text × localities.csv (retrieval-v2)", "T1 text · allowed"],
 ["f_pin_in_text / f_pin_unknown", "address pin regex × locality pins", "T1 text · allowed"],
 ["f_no_digit / f_no_separator / f_outside_town", "deterministic cleaning spans", "T1 text · allowed"],
 ["f_baseline_stratum", "baseline_geocodes.precision", "T0 official · allowed"],
 ["f_sim_jaccard / f_sim_char3 / f_sim_ratio", "text × locality-name similarities (monotone ↑)", "T1 text · allowed"],
 ["f_n_candidates", "retrieved set size", "query-time · allowed"],
 ["f_agreement_count", "cross-arm pairwise agreement ≤150 m", "geometry · allowed"],
 ["f_dist_to_town_centroid_m", "towns.csv centroid × candidate (monotone ↓)", "T0/T1 · allowed"]])
srcline("feature audit · ranking module")
para("Design columns per model = 19 (stratum one-hot expanded inside the model). Forbidden keys audited absent: truth, err, grade, label, surveyed, agent, account, proxy, target, observation, visit.")
h2("A.2 Frozen operating configuration")
para("`as_of 2026-06-01T00:00:00Z` · `retrieval_version v2` · `rule_version candidate-rules-v2` · `evidence_policy_version evidence-policy-v3` · `radius_map_version radius-map-v1` · `gate-v2` · `purpose_rules-v1` · `coordinate_policy coord-v2-trace-tail` (tail-3 median; check-in fallback) · `place_neighbour locked` · `w_n_guard 15` · behavioural hash `be84b00d…` · frozen configuration `9abebb8f…` · protocol `protocol-v1-immutable`.")
h2("A.3 Metric definitions")
para("`<k m` / `P@1<k` = share of addresses whose selected top-1 coordinate lies within k m of the stated truth · `recall@k`/oracle = a candidate exists within k m / the best candidate’s error (ceiling, not a prediction) · `median/p75/p90` = percentiles of per-address error · `nDCG@5` = list quality over the graded candidate set (grades at 100/250/500 m) · radius basis `empirical_p80` = 80th percentile of measured error in the calibration stratum, published with n and measured coverage · paired grouped bootstrap = resampling place blocks 10,000×, seed 7, both directions; inside the interval = “not resolved by this dataset”.")
h2("A.4 Evidence ledger (headline claims → canonical artifacts)")
table(["claim", "value", "artifact"], [
 ["vendor baseline vs surveyed", "376.4 m · 9\\% · 71\\%", "frozen baseline study; candidate ladder"],
 ["baseline vs proxy by precision", "18.1/118.0/313.7/1,392.8 m", "training notebook cell 8; candidate ladder"],
 ["failed visits", "1,400 · 1.28 min · 84.9\\% · 1,603 m", "outcome-geometry census; EDA and integration notes"],
 ["retrieval v1→v2", "87.67→91.44\\% · top-1 83.9\\%", "precision-study ledger §1"],
 ["selection scoreboard", "RULE 84.06\\% shipped", "implementation report §3.7; notebook cells 44–46 (frozen)"],
 ["locked S-EVAL lanes", "71/76/96.77\\% · 202.2/12.4 m", "precision-study ledger §6; sealed S-EVAL read counter"],
 ["temporal product proxy", "98.69\\% · 7.9 m · n=229", "sealed read counter, temporal block"],
 ["trace-tail estimator", "28.7→7.6 m · n=233", "frozen coordinate-policy ledger §5b"],
 ["memory defect / emp-v1", "7-of-10 · 45→31 · 0 broken", "memory-policy ledger"],
 ["co-location", "191/81 · 127 pairs · 3,011.6 m", "EDA census; notebook cell 20; integration addendum"],
 ["leakage proximity", "36\\% \\@30 m · 81\\% \\@100 m", "leakage and validation note"],
 ["radius map", "539.9 m n=24 cov 0.792", "radius table in the frozen configuration"],
 ["latency / tests", "p95 38.9 ms · 125/125", "acceptance ledger; integration report §4"]])
para("Discrepancies preserved, not silently resolved: (i) superseded Experiment-D receipt vs frozen scoreboard (Section 6.3); (ii) probe-run retrieval v1 oracle 0.8801 vs the lane table’s 0.8767 (probe value retained as history only); (iii) early-report warm medians (58.0 m / product 206.7 m) superseded by the coord-v2 label change — final artifacts govern (16.4/12.4 m; 202.2 m).")
h2("A.5 Reproduction and audit trail")
para("Every number in this report is produced by a frozen, replayable chain. The official drop is hash-verified and never modified; preprocessing, retrieval and the feature matrix are deterministic and byte-identical across runs; each experiment fixes its seed (7) and reads only ledgers dated before the as-of cut; the sealed S-EVAL read is counted and disclosed; and the final configuration is pinned by its behavioural hash. Re-running the chain in order — data guards, preprocessing ablations, the retrieval study, the selection study, the coordinate-policy holdout, the memory-policy study, then the acceptance and latency suites — reproduces every table and figure in this report without hand intervention.")
para("The report is typeset in the same design system as the live workbench; all charts are generated from the frozen ledgers, every schematic is labelled as a schematic, and the product captures are genuine screens of the served system.")

doc.save(str(ROOT / "SUTRA_PS3_Final_Report.docx"))
print("DOCX saved, figures:", FIGNO)
