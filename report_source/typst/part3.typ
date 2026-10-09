#import "theme.typ": *

// ══ 11 PRODUCT WALKTHROUGH ═════════════════════════════════════════════════
#chapter("Product walkthrough", lead: [Genuine captures of the served workbench (2026-10-08, as-of 2026-06-01T00:00:00Z). Every value on every screen is fetched from the running service, and a no-fake-data test scans the served bundle so that no invented number can reach a screen.])

#h2("11.1 Overview — the workbench, not a dashboard")
#figframe("../../screenshots/bm-01-overview.png",
  [Operations overview at the frozen cut: 3,117 indexed addresses; 566 answered with a location (911 approximate · 295 probable · 271 confirmed); 278 cases needing the field (273 moved-suspected · 5 contested); 3,788 field-visit rows. Panel A publishes the three frozen populations side by side, with the sentence that governs them: “These populations are separate by construction. They are not merged into one accuracy figure.” Panel E states the version strings and the sealed-evaluation read counter.],
  "live workbench capture · GET /v1/overview")

#h2("11.2 Resolver — messy address to decision")
#figframe("../../screenshots/bm-02-resolver-serve.png",
  [A SERVE-grade resolution (AD003067): eight possible places ranked with the engine’s own terms; the chosen field-evidence candidate (score 0.99, street granularity) with its reason terms; the local metric plane with the uncertainty ring (566.9 m, empirical p80, widened) and cross-highlighting between candidate list, map and decision panel; measured coverage 79.2\% at n=24; “what moved the score — not a confidence percentage”.],
  "live workbench capture · POST /v1/resolve, GET /v1/geometry")
The canonical SERVE ticket carries: tier CONFIRMED / status STABLE; candidate `c-28f5aface67c`, arm `field_evidence`, `source_ref visits:median(3)`, `as_of_valid 2026-05-15T05:35:37Z`; radius 566.9 m with basis, n and coverage; support 6 observations / 4 positive / 1 independent negative / 3 independent confirmations; typed reason codes including `field_confirmed_x3` and `negatives_independent=1`; and a direction cue flagged `ambiguous: true` — the landmark relation is shown as a hint, never as a location.

#figframe("../../screenshots/bm-03-resolver-verify-first.png",
  [VERIFY\_FIRST (AD002936): APPROXIMATE / MOVED\_SUSPECTED after two independent negatives; radius widened to 1,202.6 m; the coordinate unchanged. The runner-up memory arm is shown with its losing reason.],
  "live workbench capture · resolver, verify-first mode", w: 100%)

#figframe("../../screenshots/bm-09-transition.png",
  [The belief rail stepped through nine real visit instants (2026-04 → 06): tier CONFIRMED→APPROXIMATE, radius 566.9→1,202.6 m, queue entry raised — “doubt moved the radius, the tier and the queue, not the place.”],
  "live workbench capture · belief transition rail", w: 100%)

#h2("11.3 Refusal as a designed success state")
#figframe("../../screenshots/bm-05-refusal.png",
  [AD000006 (town OUT): tier UNPLACEABLE, no candidate, no coordinate field anywhere in the body; the plane renders the withheld state. A second refusal mode (AD000002 under NOTICE\_SERVICE) refuses the #text(style: "italic")[action] — the place is APPROXIMATE-grade but the notice decision demands SERVE-grade evidence.],
  "live workbench capture · refusal envelopes")

#h2("11.4 Places, Field Evidence, Verify Queue, Method & Trust")
#figframe("../../screenshots/bm-06-places.png",
  [Places: 3,117 place records keyed by co-location/adjudication (CONFIRMED 271 · MOVED\_SUSPECTED 273 · WARM 300 · COLD 2,268 · CONTESTED 5), each with state, tier, members, radius and basis — account identity never maps to a coordinate.],
  "live workbench capture · Places", w: 100%)

#figframe("../../screenshots/bm-07-evidence.png",
  [Field Evidence: 3,788 stored observations with the policy’s verdict per row (positive 1,539 / negative 1,141 / ambiguous 1,108); a negative keeps its device position but is labelled `coordinate_claim: false`; the selected visit discloses its weight in the belief chain.],
  "live workbench capture · Field Evidence", w: 100%)

#figframe("../../screenshots/bm-08-queue.png",
  [Verify Queue: 278 open cases with cause, priority, `negatives_independent`, radius and rule version; transitions are append-only (open → in\_progress → resolved → reopened); adjudication writes an observation and replays the frozen belief mechanism — a reviewed AD002936 confirmation left tier, status and coordinate unchanged (`coordinate_moved: false`).],
  "live workbench capture · Verify Queue", w: 100%)

#figframe("../../screenshots/bm-11-method.png",
  [Method & Trust: the nine version strings, the gate table with live reasons, the radius map with the n≥15 guard visible, the five invariants, and the two loops labelled honestly — fast loop IMPLEMENTED, slow loop NOT YET IMPLEMENTED, learned challenger “EVALUATED, REJECTED — not in the request path”.],
  "live workbench capture · Method & Trust", w: 100%)

#callout("acc", [Prototype boundary, stated on the product itself: this workbench demonstrates the intended operator workflow against the frozen runtime. It is not evidence that a CreditNirvana production integration is deployed; integration work is itemised in Sections 16–17.])


// ══ 12 EXPERIMENTAL EVALUATION ═════════════════════════════════════════════
#chapter("Experimental evaluation", lead: [Five separate evaluation lanes, each with its own population, label source and legitimate claim. The lanes are never merged.])

#h2("12.1 The locked S-EVAL lanes (one read of frozen configuration 9abebb8f…)")
#tt(
  columns: (3fr, 0.7fr, 1fr, 1fr, 1fr, 1.3fr, 1.3fr),
  th("lane"), th("n"), th("<100 m"), th("<250 m"), th("<500 m"), th("median"), th("p90"),
  td[cold start (static arms)], tmono[100], tmono[9\%], tmono[35\%], tmono[71\%], tmono[375.8 m], tmono[810.8 m],
  td[product policy (warm→cold)], tmono[100], tmono[33\%], tmono[55\%], tmono[#text(weight: "bold")[76\%]], tmono[202.2 m], tmono[697.3 m],
  td[warm / evidence subset], tmono[31], tmono[83.87\%], tmono[93.55\%], tmono[#text(weight: "bold")[96.77\%]], tmono[12.4 m], tmono[195.9 m],
  td[static-lane oracle (ceiling)], tmono[100], tmono[—], tmono[—], tmono[88\%], tmono[254.1 m], tmono[—],
)
#srcline("sealed S-EVAL ledger · surveyed ground truth")
Per town (product): T1 66.67\% (367.3 m, n=33) · T2 82.76\% (126.4 m, n=29) · T3 78.95\% (162.1 m, n=38); none below the n-guard. The product-vs-cold delta (+5 pts at 500 m) is [0.00, +0.101] — not resolved at n=100, and the report says so.

#figframe("../figures/fig14_01_regimes.png",
  [The three S-EVAL regimes at each threshold. The warm subset is the 31 addresses with eligible evidence at the cut — it is not a claim about all addresses; the product lane answers all 100.],
  "sealed S-EVAL ledger (three regimes)")

#h2("12.2 Non-circular temporal holdouts")
#figframe("../figures/fig14_02_temporal.png",
  [T0=2026-05-15: cold 84.72\% (271.2 m) vs product 98.69\% (7.9 m) vs promoted-only 100\% (6.1 m); paired vs cold +0.1397 [0.0938, +0.1888] resolved. The T0=2026-05-01 cut agrees (product 98.88\%, 8.6 m). Labels are promoted post-T0 check-ins — strong evidence, #text(style: "italic")[not] surveyed truth.],
  "temporal holdout ledger (T0 = 2026-05-15)")

#h2("12.3 Candidate-oracle and ranking-stability references")
The static-lane oracle is 88\% (S-EVAL) / 89.86\% (S-VAL): the candidate family’s reach, not SUTRA’s prediction. Prefix recall shows where usable candidates sit before ranking (S-EVAL \@1 0.71, \@3 0.85, \@5 0.88). Retrieval-v2 changed the ceiling but not the ranked top-1 (83.9\% both versions, pool) — availability and selection stay separate in every table of this report.

#h2("12.4 How to read the headline numbers")
Cold 71\% measures official-only information on 100 surveyed addresses; product 76\% measures the shipped policy on the same 100; warm 96.77\% measures only the 31 eligible evidence-backed answers; temporal 98.69\% measures the operating configuration against future field evidence on 229 labels; the 88\% oracle measures what the candidate set contains. No pair of these shares a population, and none is a business-outcome claim.

// ══ 13 RUNTIME PERFORMANCE, ACCEPTANCE & ENGINEERING QUALITY ════════════════
#chapter("Runtime performance, acceptance and engineering quality", lead: [Verified in-session, on copies of the shipped store, with measurement conditions stated — including what was not measured.])

#h2("13.1 Acceptance and contract suites")
#tt(
  columns: (3.6fr, 1fr, 4.4fr),
  th("suite"), th("tests"), th("what it pins"),
  td[#text(weight: "bold")[Acceptance suite]], tmono[26], td[evidence/belief invariants: T1 no candidate ⇒ no coordinate; T2 one negative ⇒ coordinate unchanged; T3 independent negatives ⇒ doubt out loud; T4 fake independence rejected; T5 valid confirmations promote; pincode-radius withholding; offline outbox replay],
  td[#text(weight: "bold")[Frontend-contract suite]], tmono[51], td[the frontend contract: alternatives are the ranked losers with lost-reasons; belief read is the authoritative object; refusal envelopes carry no coordinate; reason codes typed; geometry is local metric],
  td[#text(weight: "bold")[Product-layer suite]], tmono[39], td[product layer: append-only task lifecycle; adjudication replays belief; score\_visit writes nothing; batch resolve bounded ≤5,000 with aggregate refusal/tier/histogram, never bulk accuracy],
  td[#text(weight: "bold")[No-fake-data suite]], tmono[9], td[no invented providers/scores/trails in console #text(style: "italic")[or workbench] sources or built bundle; every called route is real],
)
#srcline("acceptance ledger · 125/125 passed in 26.8 s")

#h2("13.2 Latency")
Full request path including gate-decision logging, 400 requests on a copy of the runtime store: mean 23.2 ms · p50 21.7 · p95 38.9 · p99 53.8 · max 64.6 ms, against a 250 ms p95 target — #text(weight: "bold")[MET]. Candidate generation over the full book runs at p95 23.1 ms/address. Challenger scoring costs (≤0.3 ms/address) were material but not the deciding factor. #text(style: "italic")[Not published by the product:] live latency percentiles, error rates and queue depths — the workbench deliberately does not estimate them (visible in the System Health panel).

#h2("13.3 Integrity and reproducibility")
Official dataset hash-verified byte-identical; 0 outbound socket attempts on every experiment; seed 7 with 10,000-resample paired place-block bootstraps; split receipts and firewall hashes frozen; the S-EVAL read ledger is disclosed including the reads that went wrong during tooling (no parameter ever changed in response to a S-EVAL number; final runs reuse persisted snapshots and spend zero reads). A single reproduction chain regenerates the ledgers, the fits and the workbench build; the import, workspace and link guards run on every pass (two historical link warnings are archived and labelled, not hidden).


// ══ 14 GOVERNANCE, LIMITATIONS & INTEGRATION READINESS ══════════════════════
#chapter("Governance, limitations and integration readiness", lead: [What the system may not claim is as important as what it may. This section fixes the boundary between engine-tested behaviour, the live prototype, and future CreditNirvana integration.])

#h2("14.1 Official-data and evaluation boundaries")
External geography is prohibited by the binding freeze decision; the task has no financial outcome variable (dial/payments tables excluded); surveyed truth is evaluation-only and read under a disclosed counter; the supervision pool is selected by visit outcome, so ranking numbers are conditional on that pool (exposure bias is stated, with propensity logging as the eventual remedy); visits span 90 days with no known regime change, so drift behaviour remains a labelled simulation from the early design, not a measurement.

#h2("14.2 Safety constraints held in code")
No candidate ⇒ no coordinate; one negative never relocates; memory emits only evidence-derived priors; sub-guard strata fall back widened and labelled; refusal payloads carry no coordinate; adjudication is append-only and idempotent; the product layer may only append task events (source-scanned test); write paths run against byte-copies of the store.

#h2("14.3 Prototype boundaries (implemented vs demonstrated vs not implemented")
#tt(
  columns: (2.6fr, 6.4fr),
  th("status"), th("content"),
  td[#text(weight: "bold", fill: pal.ok)[IMPLEMENTED]], td[official-only candidate generation; retrieval-v2; RULE ranking; belief/uncertainty with radius-map-v1; eligibility gate v2 with purpose; evidence integrity and append-only belief; place memory and emp-v1; as-of reads; offline packs and outbox; the six-screen workbench bound to the real service; 125 tests; full API surface incl. adjudication and audit chain],
  td[#text(weight: "bold", fill: pal.warn)[EVALUATED, OFFLINE]], td[Logistic/LambdaMART/Pairwise challengers; preprocessing rings B3/B4; place\_neighbour (locked); the slow retraining loop (designed, gated, not built)],
  td[#text(weight: "bold", fill: pal.crit)[NOT IMPLEMENTED]], td[continuous online retraining; LLM address parsing; RL visit allocation; external map matching; a CreditNirvana production integration; any field-productivity, recovery-rate or failure-rate outcome claim (requires a controlled field evaluation with an exploration slice)],
)
#v(4pt)
The live Vercel deployment demonstrates the intended operator workflow against the frozen runtime; UI capability is not deployment evidence, and the Method & Trust screen states the same boundary in product language.

// ══ 15 PRIORITIZED ROADMAP AND CONCLUSION ═══════════════════════════════════
#chapter("Prioritized roadmap and conclusion", lead: [Model optimisation stops here by measured decision. The remaining work is productisation, integration and one properly powered evaluation — each item with an acceptance criterion.])

#tt(
  columns: (0.6fr, 3.4fr, 3.4fr, 1.6fr),
  th("P"), th("item"), th("acceptance criterion"), th("class"),
  tmono[P0], td[Surface radius ring, belief rail and pack-age chip in the workbench (payloads already shipped)], td[renderer consumes /v1/geometry and /v1/belief as-of; no client-side re-derivation; no-fake-data test stays green], td[frontend],
  tmono[P1], td[Adjudication write path + task state transitions in production wiring], td[append-only receipts; reopen-before-second-decision enforced; contract tests green on shipped store copy], td[backend],
  tmono[P1], td[Single-call audit chain GET /v1/audit/\{belief\_id\} exposed end-to-end], td[evidence weights, losers, uncertainty change and tasks reconstructable in one call], td[backend],
  tmono[P1], td[CreditNirvana integration contract (auth, tenancy, CRS handling for real coordinates)], td[interface spec signed; no frozen module modified; latency budget re-verified], td[integration],
  tmono[P2], td[Propensity logging + exploration slice for exposure bias], td[first live window logs allocation propensities; weighted vs unweighted metrics published side by side], td[evaluation],
  tmono[P2], td[Controlled field evaluation of productive-visit and verification outcomes], td[pre-registered primary metric; exploration slice; no claim published without it], td[evaluation],
  tmono[P3], td[Revisit learned rankers only if the candidate ceiling moves], td[oracle recall must rise beyond the paired interval before any new selection study], td[research],
)
#v(6pt)
#panel("Conclusion", [
  SUTRA does not claim that a larger model automatically solves address geocoding — it tested that hypothesis and recorded the result. The deeper investigation exposed candidate quality as the binding cold-start constraint (an 88\% static-lane oracle on the locked set) and showed that trusted field observations create a materially different operating regime (96.77\% on eligible evidence-backed answers; 98.69\% on the temporal proxy). The system therefore combines a deterministic, reason-coded ranker with published uncertainty, integrity-weighted evidence, an append-only place memory that cannot be poisoned by its own vendor pin, and a product surface in which doubt is a visible, actionable state. It does not merely guess a coordinate once; it builds evidence about places over time and uses that evidence to make future decisions better. #text(weight: "bold")[Resolve → Verify → Learn → Resolve Better.]
], tint: pal.accentsoft, edge: pal.accent)


// ══ 16 TECHNICAL APPENDIX & REPRODUCIBILITY ════════════════════════════════
#chapter("Technical appendix and reproducibility", lead: [Feature and configuration tables, metric definitions, the evidence ledger for every headline number, and the commands that reproduce the chain.])

#h2("A.1 Frozen 15-feature design matrix")
#tt(
  columns: (3.2fr, 3.4fr, 2.4fr),
  th("feature"), th("source"), th("as-of / status"),
  tmono[f_arm_prior], td[candidate’s own arm (provenance)], td[query-time · allowed],
  tmono[f_granularity_rank], td[candidate granularity rooftop>street>locality>town], td[static · allowed],
  tmono[f_locality_name_matched], td[address text × localities.csv (retrieval-v2)], td[T1 text · allowed],
  tmono[f_pin_in_text / f_pin_unknown], td[address pin regex × locality pins], td[T1 text · allowed],
  tmono[f_no_digit / f_no_separator / f_outside_town], td[deterministic cleaning spans], td[T1 text · allowed],
  tmono[f_baseline_stratum], td[baseline\_geocodes.precision], td[T0 official · allowed],
  tmono[f_sim_jaccard / f_sim_char3 / f_sim_ratio], td[text × locality-name similarities (monotone ↑)], td[T1 text · allowed],
  tmono[f_n_candidates], td[retrieved set size], td[query-time · allowed],
  tmono[f_agreement_count], td[cross-arm pairwise agreement ≤150 m], td[geometry · allowed],
  tmono[f_dist_to_town_centroid_m], td[towns.csv centroid × candidate (monotone ↓)], td[T0/T1 · allowed],
)
#srcline("feature audit · ranking module")
Design columns per model = 19 (stratum one-hot expanded inside the model). Forbidden keys audited absent: truth, err, grade, label, surveyed, agent, account, proxy, target, observation, visit.

#h2("A.2 Frozen operating configuration")
`as_of 2026-06-01T00:00:00Z` · `retrieval_version v2` · `rule_version candidate-rules-v2` · `evidence_policy_version evidence-policy-v3` · `radius_map_version radius-map-v1` · `gate-v2` · `purpose_rules-v1` · `coordinate_policy coord-v2-trace-tail` (tail-3 median; check-in fallback) · `place_neighbour locked` · `w_n_guard 15` · behavioural hash `be84b00d…` · frozen configuration `9abebb8f…` · protocol `protocol-v1-immutable`.

#h2("A.3 Metric definitions")
`<k m` / `P@1<k` = share of addresses whose selected top-1 coordinate lies within k m of the stated truth · `recall@k`/oracle = a candidate exists within k m / the best candidate’s error (ceiling, not a prediction) · `median/p75/p90` = percentiles of per-address error · `nDCG@5` = list quality over the graded candidate set (grades at 100/250/500 m) · radius basis `empirical_p80` = 80th percentile of measured error in the calibration stratum, published with n and measured coverage · paired grouped bootstrap = resampling place blocks 10,000×, seed 7, both directions; inside the interval = “not resolved by this dataset”.

#h2("A.4 Evidence ledger (headline claims → canonical artifacts)")
#tt(
  columns: (3.5fr, 2.6fr, 2.9fr),
  th("claim"), th("value"), th("artifact"),
  td[vendor baseline vs surveyed], tmono[376.4 m · 9\% · 71\%], td[frozen baseline study; candidate ladder],
  td[baseline vs proxy by precision], tmono[18.1/118.0/313.7/1,392.8 m], td[training notebook cell 8; candidate ladder],
  td[failed visits], tmono[1,400 · 1.28 min · 84.9\% · 1,603 m], td[outcome-geometry census; EDA and integration notes],
  td[retrieval v1→v2], tmono[87.67→91.44\% · top-1 83.9\%], td[precision-study ledger §1],
  td[selection scoreboard], tmono[RULE 84.06\% shipped], td[implementation report §3.7; notebook cells 44–46 (frozen)],
  td[locked S-EVAL lanes], tmono[71/76/96.77\% · 202.2/12.4 m], td[precision-study ledger §6; sealed S-EVAL read counter],
  td[temporal product proxy], tmono[98.69\% · 7.9 m · n=229], td[sealed read counter, temporal block],
  td[trace-tail estimator], tmono[28.7→7.6 m · n=233], td[frozen coordinate-policy ledger §5b],
  td[memory defect / emp-v1], tmono[7-of-10 · 45→31 · 0 broken], td[memory-policy ledger],
  td[co-location], tmono[191/81 · 127 pairs · 3,011.6 m], td[EDA census; notebook cell 20; integration addendum],
  td[leakage proximity], tmono[36\% \@30 m · 81\% \@100 m], td[leakage and validation note],
  td[radius map], tmono[539.9 m n=24 cov 0.792], td[radius table in the frozen configuration],
  td[latency / tests], tmono[p95 38.9 ms · 125/125], td[acceptance ledger; integration report §4],
)
Discrepancies preserved, not silently resolved: (i) superseded Experiment-D receipt vs frozen scoreboard (Section 6.3); (ii) probe-run retrieval v1 oracle 0.8801 vs the lane table’s 0.8767 (probe value retained as history only); (iii) early-report warm medians (58.0 m / product 206.7 m) superseded by the coord-v2 label change — final artifacts govern (16.4/12.4 m; 202.2 m).

#h2("A.5 Reproduction and audit trail")
Every number in this report is produced by a frozen, replayable chain. The official drop is hash-verified and never modified; preprocessing, retrieval and the feature matrix are deterministic and byte-identical across runs; each experiment fixes its seed (7) and reads only ledgers dated before the as-of cut; the sealed S-EVAL read is counted and disclosed; and the final configuration is pinned by its behavioural hash. Re-running the chain in order — data guards, preprocessing ablations, the retrieval study, the selection study, the coordinate-policy holdout, the memory-policy study, then the acceptance and latency suites — reproduces every table and figure in this report without hand intervention.

#v(4pt)
The report is typeset in the same design system as the live workbench; all charts are generated from the frozen ledgers, every schematic is labelled as a schematic, and the product captures are genuine screens of the served system.
