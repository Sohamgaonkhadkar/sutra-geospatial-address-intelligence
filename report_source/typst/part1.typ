#import "theme.typ": *

// ══ COVER ═══════════════════════════════════════════════════════════════════
#set page(header: none, footer: none)
#v(5mm)
#grid(columns: (auto, 1fr),
  block(stroke: 1.4pt + pal.accent, width: 14mm, height: 14mm,
    place(center + horizon, serifd(size: 9pt, fill: pal.accent, "S"))),
  pad(left: 5mm, [
    #mono-small(fill: pal.mute, tracking: 1.6pt)[SEMANTIC UTILITY FOR TRACEABLE RESOLUTION OF ADDRESSES]
  ]),
)
#v(8mm)
#serifd(size: 54pt, fill: pal.ink, tracking: 2pt)[SUTRA]
#v(2mm)
#serifd(size: 16.5pt, fill: pal.accentd)[An Evidence-Driven Address Geocoder That Learns from Field Visits]
#v(2mm)
#text(size: 10.5pt, fill: pal.ink2)[Definitive Technical Research and Product Report · CreditNirvana Problem Statement 3]

// cover grid motif — the local metric plane
#v(6mm)
#block(width: 100%, height: 50mm, clip: true, [
  #place(top + left,
    box(width: 100%, height: 50mm, fill: pal.panel,
      // graph grid
      box(width: 100%, height: 100%, [
        #for i in range(0, 24) { place(left + top, dx: i * 7mm, line(length: 50mm, angle: 90deg, stroke: 0.4pt + pal.line)) }
        #for i in range(0, 8) { place(left + top, dy: i * 7mm, line(length: 100%, stroke: 0.4pt + pal.line)) }
      ])
    ))
  #place(top + left, dx: 12mm, dy: 9mm, mono-small(fill: pal.cool)[sutra_local_metric_plane:T2 · metres · NT])
  #place(top + left, dx: 12mm, dy: 15mm, mono-small(fill: pal.cool)[E 001 390.0 · N −001 818.0 · grid 50 m])
  #place(top + left, dx: 96mm, dy: 26mm,
    circle(radius: 13mm, stroke: 1.1pt + pal.accent),
  )
  #place(top + left, dx: 104mm, dy: 31mm, circle(radius: 2.2mm, fill: pal.accent))
  #place(top + left, dx: 106mm, dy: 16mm, mono-small(fill: pal.accent)[radius 566.9 m · empirical_p80])
  #place(top + left, dx: 106mm, dy: 20mm, mono-small(fill: pal.accent)[n=24 · cov 0.792 · street withheld])
  #place(top + left, dx: 60mm, dy: 40mm, circle(radius: 1.6mm, fill: pal.ok))
  #place(top + left, dx: 63mm, dy: 43mm, mono-small(fill: pal.ok)[field check-in · weight 0.88])
  #place(top + left, dx: 30mm, dy: 30mm, circle(radius: 1.6mm, fill: pal.crit))
  #place(top + left, dx: 33mm, dy: 33mm, mono-small(fill: pal.crit)[negative · does not move the place])
])

#v(7mm)
#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 6pt,
  metric("SCHEMA / RULES", "sutra-1.0", "candidate-rules-v2 · gate-v2"),
  metric("EVIDENCE / RADIUS", "policy-v3", "radius-map-v1 · emp-v1"),
  metric("EVALUATION CUT", "2026-06-01", "as-of · protocol-v1-immutable"),
  metric("FROZEN CONFIG", "9abebb8f…", "one locked S-EVAL read"),
)
#v(5mm)
#grid(columns: (1fr, auto),
  mono-small(fill: pal.mute)[Prepared for formal project evaluation · 2026-10-09 \
  Repository: #link("https://github.com/Sohamgaonkhadkar/sutra-geospatial-address-intelligence")[github.com/Sohamgaonkhadkar/sutra-geospatial-address-intelligence] · branch arena/246f1c7f \
  Live prototype: #link("https://sutra-geospatial-address-intelligence-4wya-otn8569cb.vercel.app/")[sutra-geospatial-address-intelligence.vercel.app]],
  mono-small(fill: pal.mute)[report build: typst 0.15 · figures from canonical artifacts],
)
#pagebreak()

// ══ CONTENTS & ORIENTATION ═════════════════════════════════════════════════
#set page(header: page-hdr, footer: page-ftr)
#mono-small(fill: pal.accent, tracking: 1.2pt)[CONTENTS]
#v(4pt)
#serifd(size: 17pt)[Contents and how to read this report]
#v(6pt)
#outline(title: none, depth: 1)
#v(8pt)
#panel("Report orientation", [
  This report is a single connected argument: #text(style: "italic")[data and EDA → candidate-generation research → model training and selection → production ranking policy → uncertainty and evidence handling → physical-place memory → backend APIs → the operator workbench → measured results and remaining integration work]. Each section states not only what was built but #text(style: "italic")[why the data forced it].

  #v(4pt)
  Four reading rules are enforced throughout. #text(weight: "bold")[\(1) A candidate oracle is not model accuracy] — oracle numbers describe what the candidate family contains, never what the system predicts. #text(weight: "bold")[\(2) Cold-start, product-policy and warm/evidence results are different populations] and are never blended into one accuracy figure. #text(weight: "bold")[\(3) Training/validation numbers are not production numbers] — the production request path runs the deterministic RULE ranker; learned challengers were evaluated offline and rejected. #text(weight: "bold")[\(4) Every headline metric carries its population, n, ground-truth source and regime] in the table or caption that reports it (full provenance in the appendix ledger).

  #v(4pt)
  Colour carries fixed meaning: #mono-small(fill: pal.accent, weight: "bold")[orange] = implemented production behaviour, #mono-small(fill: pal.cool, weight: "bold")[slate] = cold/static official arms and ceilings, #mono-small(fill: pal.ok, weight: "bold")[green] = field evidence and the warm regime, #mono-small(fill: pal.plum, weight: "bold")[plum] = memory and place identity, #mono-small(fill: pal.warn, weight: "bold")[amber] = limitations and guards, #mono-small(fill: pal.crit, weight: "bold")[red] = refusal and negative evidence. The palette and typography are taken from the live SUTRA workbench so that the document and the product read as one system.
])
#pagebreak()

// ══ 1 EXECUTIVE SUMMARY ════════════════════════════════════════════════════
#chapter("Executive summary", lead: [SUTRA treats address geocoding as an evidence-driven decision problem: generate candidates from a restricted official family, rank them with an inspectable rule, publish granularity, provenance and a measured uncertainty radius, and let trusted field visits improve future belief — while refusing to fabricate precision the evidence does not support.])

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 6pt,
  metric("VENDOR BASELINE, S-EVAL", "376.4 m", "median · n=100 · 9% within 100 m", c: pal.crit),
  metric("PRODUCT POLICY, S-EVAL", "76% <500 m", "median 202.2 m · n=100", c: pal.accent),
  metric("WARM / EVIDENCE SUBSET", "96.77% <500 m", "n=31 eligible · median 12.4 m", c: pal.ok),
  metric("TEMPORAL PRODUCT PROXY", "98.69% <500 m", "n=229 · median 7.9 m · non-circular", c: pal.ok),
)
#v(6pt)

The problem. The supplied vendor baseline is coarse where it answers at all: against the 100 independently surveyed addresses its median error is 376.4 m, only 9\% fall within 100 m, and the pincode stratum is wrong by kilometres (Section 6). Locality names and pincodes conflict, 237 addresses lie outside any town polygon, and 25.1\% of field visits end `address_not_traceable` after a median dwell of 1.28 min — visits that converge on #text(style: "italic")[our own bad pin] (84.9\% pin-closer on the surveyed subset), not on the property (Section 6.3). A coordinate without provenance, granularity and uncertainty is therefore operationally unsafe.

The approach. SUTRA resolves each address against a restricted official candidate family (frozen vendor pin, locality centroid, town centroid, official landmark, exact-text address book; after visits, evidence-backed arms), ranks with a deterministic, reason-coded RULE ranker, and fuses belief with integrity-weighted field evidence under a strict as-of discipline. Every answer carries a granularity, a tier (CONFIRMED / PROBABLE / APPROXIMATE / UNPLACEABLE), a radius taken from a measured error map with published n and coverage, and a gate decision: SERVE, VERIFY\_FIRST or REFUSE.

The research path. Nine controlled experiments (A–D plus the precision and evidence-policy passes) measured every layer before it was admitted: preprocessing ablations that closed two “obvious” retrievers by measurement; a retrieval fix (retrieval-v2) that raised the candidate ceiling from 87.67\% to 91.44\% within 500 m on the supervision pool while honestly showing the ranked top-1 unmoved; a model-selection study in which Logistic Regression, LambdaMART and Pairwise challengers #text(style: "italic")[failed to clear a pre-registered promotion gate] on S-VAL (n=69), leaving the RULE ranker in production by deliberate, documented decision; a coordinate-policy result in which the component-wise median of a visit’s last three GPS fixes cut visit-coordinate median error from 28.7 m to 7.6 m on a 233-visit temporal holdout; and a memory-integrity policy that removed the defect whereby a vendor pin could re-enter the system disguised as “place memory”.

The measured outcome, in three non-interchangeable populations on the locked S-EVAL: cold start 71\% within 500 m (median 375.8 m) — bounded by a static-lane candidate oracle of 88\%; the full product policy 76\% (median 202.2 m, P90 697.3 m); and the 31 addresses with eligible field evidence at the cut, 96.77\% (median 12.4 m). On a non-circular temporal holdout the operating configuration reaches 98.69\% within 500 m (median 7.9 m, n=229). None of these is a claim about every address; each is labelled with its population.

The product. The same engine serves a six-screen operator workbench (Overview, Resolver, Places, Field Evidence, Verify Queue, Method & Trust) in which every number is fetched from the runtime, refusals render as designed decisions with no coordinate, and negative evidence widens the radius and opens a verification task without ever moving a place (Section 13). 125/125 repository tests pass and the full request path answers in a p95 of 38.9 ms against a 250 ms target (Section 15).

The boundary. SUTRA is a working prototype on the official PS3 dataset, not a deployed CreditNirvana integration; no field-productivity or recovery-rate claim is made; external geodata is outside the governance boundary; the learned challengers remain offline; and the remaining work is itemised with acceptance criteria (Sections 16–17).


// ══ 2 PROBLEM FORMULATION & SYSTEM REQUIREMENTS ════════════════════════════
#chapter("Problem formulation and system requirements", lead: [The central question is not “address → coordinates”. It is: given a badly written address and a poor vendor pin, which of a small set of plausible places is the record — and how much should what the field has observed change what we believe about that place?])

#h2("2.1 Why one-shot geocoding fails here")
Three measured facts define the task (full evidence in Section 6): the vendor pin’s median error against surveyed truth is 376.4 m with a p90 of 839.2 m; the declared precision of a pin is a weak proxy for its true accuracy (locality-stratum median 385.9 m, pincode stratum 1,375.8 m); and field visits — 5,578 of them — are abundant but are #text(style: "italic")[evidence of varying quality], not truth: a failed visit usually describes where the agent searched, not where the property is. The system must therefore reason about unreliable pins, ambiguous locality/pincode text, incomplete official candidates, different spatial granularities and contradictory visits, and it must decide, per request, whether a coordinate should be #text(weight: "bold")[served, sent for verification, or refused].

#h2("2.2 Required operator decisions")
The product must answer four operational questions for every request: (a) #text(style: "italic")[which place] — a coordinate with granularity and provenance; (b) #text(style: "italic")[how uncertain] — a radius with measured coverage, never a bare confidence scalar; (c) #text(style: "italic")[what to do] — SERVE for field navigation, VERIFY\_FIRST when evidence is thin or contested, REFUSE when unsupported or when the request purpose demands more precision than the place holds; (d) #text(style: "italic")[what the field changes] — how a new visit updates belief, memory and the verification queue, without ever letting a single observation fabricate or move a coordinate.

#h2("2.3 Design principles derived from the data")
#grid(columns: 2, gutter: 8pt,
  panel("Evidence over inference", [
    Observed field observations and official tables are evidence; everything derived from them is inference and is labelled as such. A coordinate is always accompanied by its provenance (arm, source ref, as-of validity, licence class), its granularity (rooftop/street/locality/town) and its uncertainty tier and radius.
  ], tint: pal.oksoft, edge: pal.ok),
  panel("Refusal is a designed success state", [
    REFUSE and VERIFY\_FIRST are first-class decisions with reasons, not errors. A geocoder that always returns a dot can look better on paper while being operationally unsafe; SUTRA counts its refusals and reports their correctness.
  ], tint: pal.critsoft, edge: pal.crit),
  panel("Negative evidence never relocates", [
    An `address_not_traceable` visit carries zero coordinate claim. Accumulated independent negatives may demote a tier, widen a radius, mark MOVED\_SUSPECTED and open a task; only positive evidence or human adjudication establishes a primary coordinate.
  ], tint: pal.warnsoft, edge: pal.warn),
  panel("Memory must be evidence-derived", [
    Place memory is keyed by physical place, never by account, and may only be emitted when its prior coordinate derives from accumulated field evidence — a prior that merely re-wraps a static pin is not memory (Section 11).
  ], tint: pal.plumsoft, edge: pal.plum),
)

#h2("2.4 The decision contract published per request")
Every resolution returns: the chosen candidate with arm, granularity and provenance; the belief tier and status (e.g. CONFIRMED/STABLE, APPROXIMATE/MOVED\_SUSPECTED, UNPLACEABLE); `radius_m` with basis (`empirical_p80`), calibration n and measured coverage; typed reason codes (`cross_arm_agreement`, `field_confirmed_x3`, `negatives_independent=k`, `promotion:ok|not_ok`, …); the gate decision with its rule and purpose; and the ranked losing candidates with losing reasons. The contract deliberately omits a bare confidence percentage and any coordinate on refusal.


// ══ 3 DATASET INVENTORY & GOVERNANCE ═══════════════════════════════════════
#chapter("Dataset inventory and governance", lead: [Twelve official tables, one surveyed-truth firewall, one coordinate system that is deliberately not latitude/longitude, and a zero-external-data policy that is enforced by hash-checked tooling.])

#h2("3.1 Official tables and what shaped the design")
#tt(
  columns: (2.6fr, 0.9fr, 5.5fr),
  th("table"), th("rows"), th("facts that shaped the design"),
  td[addresses], tmono[3,117], td[median 67 chars; 24.9\% without a comma; 9 without any digit; 8.4\% Devanagari/Kannada; 237 with `town_id=OUT`; 10 duplicate normalised texts],
  td[baseline\_geocodes], tmono[2,880], td[strata: locality 2,052 · street 504 · pincode 274 · rooftop 50; no pin piles (largest coincidence = 1); coverage 92.4\% of addresses],
  td[field\_visits], tmono[5,578], td[seven outcomes; 25.1\% `address_not_traceable`; 443 visits under 60 s; outcomes split into place-evidence and person-evidence dimensions],
  td[visit\_gps\_points], tmono[160,406], td[median 26 fixes/visit (max 80); `gps_accuracy_m` median 9.8 m; 34 axis artefacts (0.021\%) flagged and excluded — the only drop],
  td[surveyed\_addresses], tmono[100], td[the only ground truth: T1 33 / T2 29 / T3 38; 0 OUT; 1 rooftop — firewalled from all fitting and candidate generation],
  td[localities], tmono[36], td[35 names for 36 rows — “Nehru Colony” exists in two towns with different pincodes: pincode→locality is ambiguous by construction],
  td[landmarks\_poi], tmono[240], td[only 14 distinct names; 198 duplicate (town,name) pairs — generic names cannot be coordinate targets],
  td[accounts / agents], tmono[2,400 / 30], td[accounts are demand context, never location features; same-account addresses sit a median 3,011.6 m apart],
  td[towns / splits / lenders], tmono[3 / 2,400 / 6], td[account-level official split 1,680/360/360, extended by a place-block ledger; lenders imported and hash-baselined],
)
#srcline("data/official_ps3/*, PS3_DATA_EDA_AND_PREPROCESSING.md §1, experiment_A_report.json")
#v(4pt)
Coordinates are #text(weight: "bold")[local metric (x, y) metres per town] (`sutra_local_metric_plane:T<n>`), not latitude/longitude; the product never invents a projection, a road graph or a lat/lon claim.

#h2("3.2 The surveyed-truth firewall and split protocol")
`surveyed_addresses.csv` is reserved for offline evaluation: the candidate path is proven by runtime guard never to read it, and the firewall union — 100 surveyed addresses plus their accounts and place blocks, 145 records (4.65\% of the corpus) — is excluded from every fit. Supervision for the ranking experiments is the 292-row pool of operationally confirmed addresses (S-TRAIN 223 fit / S-VAL 69 selection), with 45 excluded and 2,680 pool-unsupervised; receipts and member-manifest hashes are frozen (`split_receipt.json`, protocol-v1-immutable). Grouping is two-level: #text(style: "italic")[outer = place block, inner = account], because signal lives in places, not rows (Section 6.5).

#h2("3.3 Data governance boundary")
The final project decision (2026-10-07, binding in `PS3_FINAL_DATA_AND_ARCHITECTURE_FREEZE.md`) restricts the system to the official PS3 tables and the legitimately assigned shared tables. No external map service, third-party geocoder, downloaded gazetteer, scraped POI or external address database enters candidate generation, training or any metric. Tooling asserts zero outbound socket attempts on every experiment run; Domain A is byte-identical to its drop (hash-verified by `tools/check_workspace.py`). The two large shared tables assigned to other problem statements (dial attempts, payments) are excluded — the task provably has no financial outcome variable and no claim depends on one.


// ══ 4 EXPLORATORY DATA ANALYSIS ════════════════════════════════════════════
#chapter("Exploratory data analysis", lead: [Each analysis below follows question → data → observation → insight → engineering consequence, on official tables and non-held-out diagnostics only. The EDA is the reason the system looks the way it does.])

#h2("4.1 Vendor pins: declared precision is not accuracy")
Against the surveyed 100, the frozen vendor baseline achieves a 376.4 m median error (p80 610.0 m, p90 839.2 m, max 4,807.7 m) with 9\% within 100 m and 71\% within 500 m. The distribution is strongly long-tailed and the tail is stratified by declared precision: rooftop 25.6 m (n=1), street 108.6 m (n=16), locality 385.9 m (n=73), pincode 1,375.8 m (n=10). The modal stratum is locality (71\% of pins), so the typical pin is a neighbourhood-scale claim presented as a point. Against the proxy truth on the 292-row supervision pool the picture is consistent (median 260.3 m; hit-rates 15.4\% / 48.3\% / 83.9\% at 100/250/500 m; pincode-stratum median 1,392.8 m).

#figframe("../figures/fig06_01_vendor_strata.png",
  [Vendor error by declared precision on the surveyed 100: the pincode stratum is wrong at kilometre scale and even “street” pins carry a 108.6 m median.],
  "data/derived/eda_baseline_error_by_stratum.csv (surveyed truth)")

#text(weight: "bold")[Consequence.] A single coordinate without provenance and uncertainty is unsafe; ranking may demote coarse strata but cannot invent a house number — hence granularity tiers, a measured radius map, and VERIFY\_FIRST as the default posture for thin evidence.

#h2("4.2 Field visits are evidence, not truth — and failed visits are not coordinate truth")
Visits split cleanly by geometry. Successful visits (met borrower/family, cash) sit a median 29.3 m from surveyed truth and 396.9 m from the vendor pin (3.2\% pin-closer, median dwell 9.7 min). `address_not_traceable` visits — 1,400 of 5,578 (25.1\%), median dwell 1.28 min — sit a median 194.7 m from #text(style: "italic")[our pin], and on the surveyed subset are pin-closer in 84.9\% of cases at a median 1,603.2 m from truth: the agent walked to where the bad geocode pointed, failed, and left.

#figframe("../figures/fig06_02_visit_outcomes.png",
  [Outcome census and geometry: failed visits are brief and cluster near the vendor pin; successful visits are brief in neither sense — they are at the property.],
  "data/derived/eda_visit_outcome_geometry.csv, eda_visit_outcomes.csv")

#callout("crit", [A failed visit describes where the agent searched. It may raise doubt, widen a radius and open a task; it may #text(weight: "bold")[never] author or move a coordinate. This rule (F2.1/D36) is unit-tested and alarmed.])

#figframe("../figures/fig04_02_failed_geometry.png",
  [Failed visits are not "no information": the not-traceable class walks the longest approach tracks (616 m median) yet records the shortest dwell (1.28 min) — the geometry says the agent searched and left, so the visit informs doubt, not location.],
  "data/derived/eda_visit_outcome_geometry.csv")

The integrity anomaly in the data is media, not GPS: agent FA009 carries 156 duplicate photo hashes across 610 visits (25.6\%) while every other agent is below 0.3\% and its GPS trails are clean — the evidence layer therefore weights, never accuses, and every weight ships with reason codes.

#figframe("../figures/fig04_03_agent_integrity.png",
  [Per-agent duplicate photo-hash rate: FA009 at 25.6\% (156 duplicate hashes across 610 visits) against ≤0.3\% for every other agent, while its GPS trails stay clean — the anomaly is media integrity, so the evidence layer down-weights with reason codes instead of discarding or accusing.],
  "data/derived/eda_agent_behaviour.csv")

#h2("4.3 Locality and pincode traps")
260 addresses carry a 6-digit token matching no pincode; 237 are outside every town; the old locality matcher accepted #text(style: "italic")[any shared token] (“nagar”, “colony”) and let a stale pincode outvote the text, selecting the wrong locality on 118 of 292 supervision rows (centroid error median 799.5 m). Meanwhile 262 addresses are written in Kannada or Devanagari while every locality name is Latin. #text(weight: "bold")[Consequence:] retrieval-v2 (Section 9), a frozen text feature set that includes pin/flag features, and a script-bridge experiment that was measured and rejected because the pincode path already places those rows (Section 9.4).

#h2("4.4 Account identity is not physical-place identity")
191 addresses form 81 co-location clusters across #text(style: "italic")[different] accounts (met check-ins within 30 m; 127 cross-account pairs), while two addresses of the #text(style: "italic")[same] account sit a median 3,011.6 m apart. Place blocks (3,007; 81 multi-address, largest 7) therefore key the memory and the CV grouping; account IDs and commercial attributes are excluded from the feature matrix by construction, an exclusion that is audited rather than asserted (Section 8).

#h2("4.5 Agents and landmarks: attractive but inert")
Agent-level boxplots of baseline error show no exploisable agent effect, and the frozen 15-feature matrix contains no agent or account field — an “agent-ID-only” control cannot even be fitted without inventing a feature. The landmark table holds 240 POIs but only 14 distinct names (“Ganesh Temple” ×7, “Ration Shop” ×9 in T1): a fuzzy name match is almost always ambiguous, the landmark arm is inert on this corpus, and adding town-centroid/landmark/address-book arms leaves oracle series identical (Sections 8–9).

#h2("4.6 Spatial leakage: why random splits overstate generalisation")
Under the audited account-based split, 124 of 344 (36.0\%) held-out addresses with a met visit have a train-split met check-in within 30 m (279 within 100 m), and 39 place blocks (99 addresses) cross the official split — nearby addresses share physical evidence even when accounts differ. Ordinary random splitting would therefore put near-identical places on both sides of the train/test boundary. Controls implemented: place-block ledger with outer place-block / inner account nested grouping, leave-block-out stress populations, as-of temporal filtering on all evidence features, the 145-record firewall, and a 12-pattern banned list enforced in `tools/check_leakage.py` (including the by-name ban on “check-in agrees with our pin” as a feature). Residual risk is disclosed, not hidden: the supervision pool is selected by visit outcome, so every ranking number is conditional on that pool.

#figframe("../figures/fig04_04_truth_split.png",
  [The surveyed truth is small and deliberate (T1 33 / T2 29 / T3 38) and fully firewalled; the official split keeps 32 OUT-town addresses in test, so held-out evaluation includes the hardest rows by construction.],
  "data/derived/eda_ground_truth_composition.csv, eda_split_town.csv")

