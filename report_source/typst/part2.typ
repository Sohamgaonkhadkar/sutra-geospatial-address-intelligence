#import "theme.typ": *

// ══ 5 MODELING METHODOLOGY & TRAINING PIPELINE ══════════════════════════════
#chapter("Modeling methodology and training pipeline", lead: [From raw tables to a frozen 15-feature candidate-level design matrix, relevance grades from an operational proxy label, grouped fitting on 223 addresses, and a promotion gate that was designed to be able to say no.])

#h2("5.1 Labels: an operational proxy, never the surveyed truth")
Fitting and selection use `operational_confirmation_proxy` — the component-wise median of independently promoted check-ins available strictly before the as-of cut (`sutra.replay._proxy_truth`) — because the 100 surveyed truths are firewalled. Candidate rows receive relevance grades 3/2/1/0 at ≤100/250/500 m and beyond. The proxy is disclosed as a proxy: evidence arms reproduce it by construction, which is exactly why the warm lane is labelled a circular diagnostic and why non-circular temporal holdouts and the single locked S-EVAL read carry the evidential weight.

#h2("5.2 Candidate-level features: the frozen 15")
The design matrix is candidate-level (each row = one candidate for one address) and frozen at 15 features, each audited for source, as-of status and permissibility: `f_arm_prior`, `f_granularity_rank`, `f_locality_name_matched`, `f_pin_in_text`, `f_pin_unknown`, `f_no_digit`, `f_no_separator`, `f_outside_town`, `f_baseline_stratum`, `f_sim_jaccard`, `f_sim_char3`, `f_sim_ratio`, `f_n_candidates`, `f_agreement_count`, `f_dist_to_town_centroid_m`. Five carry pre-registered monotone constraints (similarities and granularity ↑, distance to town centroid ↓), enforced structurally per tree and #text(style: "italic")[tested] for the unconstrained logistic fit — a violation is a finding, not a refit trigger. No agent, account, truth, outcome or visit field exists in the matrix; the audit replaces an “agent-only control” that could not be fitted without inventing a feature.

#h2("5.3 Splits, fitting and validation procedure")
S-TRAIN (223 addresses, 762 candidate rows) fits; grouped S-VAL (69 addresses, 240 rows) early-stops — a pre-registered rule whose consequence is stated plainly: S-VAL figures for learned models are selection-contaminated, so the out-of-fold lens (5 spatial folds, every place block wholly inside one fold, inner account-grouped stopping) is reported beside them as the unbiased reading. Grade mix on the pool: 61 ≤100 m, 185 ≤250 m, 283 ≤500 m, 473 beyond. Hyperparameters are exactly the pre-registered set (≤300 trees, depth ≤4, lr 0.05, subsample 0.8, L2 leaf 1.0, min-data-in-leaf); the trees stop after 1–11 on the grouped early-stopping signal. Primary metric: top-1 hit within 500 m; paired grouped bootstrap over place blocks, 10,000 resamples, seed 7, both directions tested.

#h2("5.4 The promotion gate")
Adopt a learned ranker only if it beats RULE on the primary S-VAL metric beyond the paired interval, regresses nothing (coverage, per-stratum n≥15, refusal behaviour, availability, latency, leakage), and stays directionally consistent on leave-block-out. The gate also runs negative controls: shuffled-label LambdaMART must collapse (it does: 23.19\% vs 84.06\%), pin-only must reproduce RULE’s top-1 exactly (it does — the rule’s value is tie-breaking, not geometry), and outbound calls must be zero (they are).

// ══ 6 MODEL EXPERIMENTS AND SELECTION ═══════════════════════════════════════
#chapter("Model experiments and selection", lead: [The deliberate result of the selection study: the simplest validated ranker — the deterministic, reason-coded RULE — remains production. Model complexity alone was tested and found not to be evidence for deployment.])

#h2("6.1 The final frozen scoreboard (S-VAL, n=69)")
#tt(
  columns: (2.2fr, 1fr, 1fr, 1fr, 1.2fr, 1.2fr, 1.6fr),
  th("ranker"), th("<100 m"), th("<250 m"), th("<500 m"), th("median"), th("nDCG\@5"), th("decision"),
  td[#text(weight: "bold")[RULE (shipped)]], tmono[15.94\%], tmono[50.72\%], tmono[#text(weight: "bold")[84.06\%]], tmono[249.0 m], tmono[#text(weight: "bold")[0.9670]], td[retained],
  td[LOGISTIC], tmono[17.39\%], tmono[49.28\%], tmono[81.16\%], tmono[258.0 m], tmono[0.9516], td[rejected],
  td[LAMBDAMART], tmono[15.94\%], tmono[50.72\%], tmono[84.06\%], tmono[249.0 m], tmono[0.9640], td[rejected],
  td[PAIRWISE], tmono[15.94\%], tmono[50.72\%], tmono[84.06\%], tmono[249.0 m], tmono[0.9653], td[rejected],
  td[LAMBDAMART-shuffled], tmono[10.14\%], tmono[31.88\%], tmono[56.52\%], tmono[398.3 m], tmono[0.8090], td[control],
)
#srcline("final frozen Experiment-D scoreboard, PS3_IMPLEMENTATION_PHASE_REPORT §3.7; master notebook cells 44–46")

#figframe("../figures/fig08_01_challengers.png",
  [No challenger cleared the gate: LOGISTIC is a point worse on the primary metric and fails the monotone structural check (f\_sim\_ratio fitted −0.0133, f\_dist\_to\_town\_centroid\_m +0.3597); LAMBDAMART and PAIRWISE produce top-1 series identical to RULE at strictly worse nDCG.],
  "final frozen Experiment-D scoreboard")

#h2("6.2 Why the models do not generalise — measured, not asserted")
In-sample the trees reach 84.75\% with the early-stopping signal already optimal at tree 1, and on S-TRAIN learned models marginally beat RULE (84.75 vs 83.86); out-of-fold the advantage evaporates. The headroom decomposition explains it: on S-VAL the rule’s top-1 is already the best available candidate on 55.1\% of addresses (38/69); a strictly better candidate exists for 17 addresses with a median waiting gain of 138 m; a perfect ranker — which does not exist — could reach only 20.29\% at 100 m and 89.86\% at 500 m. The entire reordering headroom is +0.04/+03. Ranking is not where the remaining error lives; the candidate set is (Section 7). LambdaMART split usage (not causal) concentrates on `f_dist_to_town_centroid_m`, `f_arm_prior` and the similarities — provenance and precision dominate, reinforcing the systems conclusion.

#h2("6.3 Provenance note: two Experiment-D runs")
The repository preserves two Experiment-D artefacts. The earlier run (`experiment_d_report.md`, receipt config `cf8e9683…`) reported RULE nDCG\@5 0.9291 and LOGISTIC 82.61\%/224.7 m on S-VAL, and on the locked S-EVAL read LOGISTIC 0.81 vs RULE 0.71 (resolved better on that population — while losing on S-VAL, the declared decision population, so the gate still rejected it). After documented repairs (a row-truncation bug that passed stripped candidate dicts to the rule interface, and a one-sided-test labelling defect) and the final frozen configuration (`9abebb8f…`), the re-run produced the scoreboard above, in which no challenger beats or resolves better than RULE on any population. The notebook and implementation report agree on the frozen values to the last digit; the earlier receipt is retained and labelled superseded. A later precision-pass re-test on retrieval-v2 candidates reached the same conclusion from the other direction: LOGISTIC 82.61\% (not resolved), LAMBDAMART identical, PAIRWISE 59.42\% resolved worse (−0.2464). The report therefore states, consistently throughout: #text(weight: "bold")[production serves the deterministic RULE ranker; learned challengers are offline.])

// ══ 7 CANDIDATE GENERATION AND RANKING RESEARCH ═════════════════════════════
#chapter("Candidate generation and ranking research", lead: [Candidate availability and candidate selection are separate problems. The project improved the former, proved the latter near-empty of headroom, and rejected every generator that harmed more cases than it rescued.])

#h2("7.1 The restricted official family and its ceiling")
Five static arms answer a cold address: `frozen_baseline`, `locality_centroid`, `town_centroid`, `official_landmark`, `address_book`; after visits, `field_evidence` and (eligibly) `memory`; `place_neighbour` exists in code and stays locked. Over the full book the static lane covers 92.4\% of addresses with a median of 3 candidates. Experiment C keeps four quantities apart that are routinely conflated — retrieval coverage, retrieval recall, the oracle ceiling, and the ranked answer — and ladders the arms: on S-EVAL the baseline-only oracle is 376.4 m/71\%, adding locality centroids lifts the ceiling to 88\% (285.8 m), landmarks to 255.8 m; the final static-lane oracle is 88\% within 500 m (median 254.1 m) on S-EVAL and 89.86\% (184.7 m) on S-VAL. The absolute “best of every official point” bound is 1.00 at 38.8 m median — an existence proof requiring the answer, reported to bound the information, not to claim it. #text(weight: "bold")[The 90\% cold-start target is therefore not reachable from the official data; that is a bound, not an opinion.]

#h2("7.2 Retrieval-v1 → v2: fixing locality matching, honestly measured")
#figframe("../figures/fig09_01_retrieval.png",
  [Retrieval-v2 raises the candidate ceiling (87.67→91.44\% within 500 m on the pool; locality-candidate median error 811.9→319.6 m) while the ranked top-1 stays at 83.9\%: the rule still chooses the vendor pin, and that is the honest reading.],
  "data/derived/precision_optimization_report.md §1")
Retrieval-v2 requires every token of the locality name (coverage ≥0.5) including the name’s rarest token by IDF, tie-breaks deterministically, and emits #text(style: "italic")[all] localities of an ambiguous pincode instead of the first. The improvement is real and the non-improvement is real: candidate generation and candidate selection are different problems, and the report refuses to oversell the former as a top-1 win.

#h2("7.3 The bottleneck taxonomy (supervision pool, n=292)")
#figframe("../figures/fig05_01_taxonomy.png",
  [Of 292 pool rows, 245 resolve within 500 m; 22 have a better candidate that cannot be chosen without breaking more cases; 19 have nothing within 500 m (best is a centroid); 6 are pincode-coarse retrieval failures.],
  "data/derived/precision_optimization_report.md §2")

#h2("7.4 Rejected candidate generators — negative results as research output")
#tt(
  columns: (3.2fr, 1fr, 1.2fr, 1fr, 1fr, 2fr),
  th("generator"), th("coverage"), th("median"), th("rescued"), th("worse"), th("verdict"),
  td[address-book near-duplicate], tmono[42.81\%], tmono[247.0 m], tmono[1], tmono[66], td[rejected: harms 66× more than it rescues],
  td[pincode-consistent locality], tmono[85.27\%], tmono[321.9 m], tmono[0], tmono[144], td[rejected: pure harm on this corpus],
  td[script lexicon (Kannada/Devanagari)], tmono[33 rows], tmono[315.1 m], tmono[0], tmono[—], td[rejected: pincode path already places them (250.6 m)],
  td[archetype routing], tmono[—], tmono[248.9 m], tmono[—], tmono[—], td[rejected: every archetype’s best arm is the pin; the router is the rule (Δ 0.0)],
  td[sibling-pin transfer], tmono[39 rows], tmono[329.5 m], tmono[9/39], tmono[—], td[dead end, closed],
  td[empirical locality centres], tmono[264 rows], tmono[321.6 m], tmono[126/264], tmono[—], td[supplied centroids already good; kept as negative control],
  td[preprocessing residue (TF-IDF/SVD, parser)], tmono[0], tmono[—], tmono[0], tmono[—], td[byte-identical universes, 1.26–4.73× latency; closed by measurement (Experiment B)],
)
#srcline("data/derived/precision_optimization_report.md §5, experiment_b_report.md, research/precision/README.md")
The landmark arm is likewise inert: only 32/292 pool rows carry a recognisable landmark mention, the nearest same-type POI sits a median 269.4 m away, and per-town same-type POIs number about 6 — a name alone cannot identify the landmark without the relation word. `place_neighbour` beats its placebo (61.9 m vs 2,162.1 m) but changes zero product answers and does not clear its C2 admission bar: measurable is not the same as admissible; it stays #text(weight: "bold")[locked].


// ══ 8 GPS ESTIMATION AND EVIDENCE PROCESSING ════════════════════════════════
#chapter("GPS estimation and evidence processing", lead: [A visit is a track, not a dot: the component-wise median of the last three fixes — taken while the agent is at the address — replaces the single check-in as the ingested coordinate, with the raw check-in retained as provenance and fallback.])

#h2("8.1 The trace-tail estimator")
#figframe("../figures/fig10_01_trace_tail.png",
  [Non-circular cross-cut evaluation (n=233): estimator applied to visits before T0, judged against visits after T0. The within-100 m rate rises 76.39→86.27\% and the median error falls 28.7→7.6 m; the cold lane is identical under either label (0.8459), so the gain is attributable to the estimator, not a moved goalpost.],
  "final_precision_config.json coordinate\_policy.measured; precision report §5b")
The official `visit_gps_points` table holds the agent’s approach track (median 26 fixes, up to 80); the last three fixes are recorded at the address and their component-wise median averages out single-sample check-in error. Label shift across the cut is 13.7 m median; promoted check-ins disagree with each other by only 39–43 m across a mid-quarter cut at 97–99\% within 500 m, while `gps_accuracy_m` has a 9.8 m median: #text(style: "italic")[the check-ins are the precise signal and the vendor pin is the noisy one].

#callout("warn", [This is a #text(weight: "bold")[visit-coordinate-estimation] result. It states where a visit happened, more precisely. It is not cold-start address-geocoding accuracy and is never reported as such.])

#h2("8.2 Outcome semantics and integrity weighting")
Each visit stores an evidence score with two dimensions, `w_place` and `w_person`, composed from outcome dimension × dwell band × trail agreement × media integrity × accuracy class × rolling agent baseline × recency; no single signal zeroes a visit, and absence of usable evidence is a recorded state (`insufficient_evidence`), not an accusation. Outcomes are split by dimension: `locked_premises` is weak place-positive/person-indeterminate; `no_such_person` is place-positive/person-negative. Promotion to a belief-moving observation requires two independent confirmations (different visit, different day, sufficient weight, not traceable to the same media hash or agent-day cluster).

#h2("8.3 Negative evidence and the no-relocation invariant")
The frozen rules: one negative never relocates; graded negatives accumulate from two independent observations (`NEG_ACCUMULATION_MIN=2`); negatives can demote a tier, widen the radius, mark MOVED\_SUSPECTED and open a verification task. Measured on the full universe: 130 addresses carry negative observations, #text(weight: "bold")[0 relocations by a negative]. The acceptance suite includes dedicated tests (T2: one negative leaves the coordinate unchanged; T3: independent negatives raise doubt out loud; T4: fake independence is rejected).

#h2("8.4 As-of discipline")
Every read is as-of (`observed_at < as_of`); evidence arms carry `as_of_valid` and vanish for queries before their observation; belief is recomputable at any instant (`GET /v1/belief/{id}?as_of=…`). The temporal holdouts (Section 10) build candidates strictly from pre-T0 evidence and label with post-T0 promoted check-ins, so future information can be an evaluation outcome but never a historical input.

// ══ 9 PHYSICAL-PLACE MEMORY AND UNCERTAINTY POLICY ══════════════════════════
#chapter("Physical-place memory and uncertainty policy", lead: [Memory is keyed by physical place, append-only, contradiction-holding, and may only speak when its prior derives from accumulated field evidence — the defect that let a vendor pin masquerade as memory was measured, removed, and shipped as a defect removal, not an accuracy claim.])

#h2("9.1 Co-location evidence and place keying")
The EDA showed 191 addresses in 81 cross-account co-location clusters and same-account addresses kilometres apart (Section 4.4). Memory therefore keys on place blocks built from met-check-in proximity (≤30 m) and adjudication — `colocation<=30m|adjudicated` — never on account identity. Beliefs are versioned rows (position, tier, radius, support, reasons); observations are the only clock; nothing is overwritten or averaged; contradictions are a state (CONTESTED) with both supports kept, a widened radius and a queued task; staleness (no positive older than 365 days → STALE) is visible, never silent.

#h2("9.2 The pin-derived memory defect, measured")
Under the shipped policy the memory arm was chosen on 29 of 292 pool rows and was weak where chosen (\<100 m 17.24\%, median 337.9 m) while field evidence was strong (95.82\%). Ten pool rows exceeded 500 m; in #text(weight: "bold")[seven] the emitted “memory” candidate was within 5 m of the vendor pin — the memory had remembered a pin and called it memory, then outranked real check-ins via a primary-eligibility bonus. The cleanest harm evidence: materialising an on-demand prior #text(style: "italic")[without] the evidence-derived emit rule collapses the temporal \<100 m rate from 89.03\% to 64.98\%.

#h2("9.3 The frozen policy (emp-v1) and how to read its effect")
The frozen rule: a prior may become memory only if its tier is CONFIRMED/PROBABLE #text(style: "italic")[and] its coordinate derives from accumulated field evidence; priors that re-wrap static arms are not emitted. Challengers were tested on S-TRAIN/S-VAL, two temporal cuts and leave-block-out with paired place-block bootstraps (quality tiering of singles: no effect; fewer singles: regression; GPS-accuracy gates: no effect; quality-ordered tie-break: regression — the shipped id tie-break stands). On the locked S-EVAL the warm licence narrows from 45 to 31 answered addresses while accuracy rises (82.22→96.77\% at 500 m; 57.78→83.87\% at 100 m; median 16.4→12.4 m); the product lane is bit-identical (33/55/76\%, 202.2 m) because the 14 withheld answers were the pin re-wrapped and those addresses still receive the pin coordinate with pin radius and VERIFY\_FIRST semantics.

#figframe("../figures/fig11_01_memory_policy.png",
  [Fewer answers, better evidence: withholding pin-derived memory claims is not withholding answers. The policy shipped as a parameter-free, one-flag-revertible defect removal; on S-VAL alone the gain is +0.0290 [0.0000, +0.0725], read as a power limit, so no validated accuracy gain is claimed.],
  "data/derived/evidence_memory_policy_report.md §7")

#h2("9.4 Uncertainty: a published contract, honest about thin data")
Every answer carries granularity, tier, and `radius_m` from the empirical p80 of measured error per baseline stratum, with n and measured coverage published: locality 539.9 m (n=24, coverage 0.792, publishable); street 162.1 m (n=5) and pincode 1,204.2 m (n=4, coverage 0.000) are #text(style: "italic")[withheld] below the n≥15 guard and fall back to the locality radius, widened and labelled `calibration_fallback`; rooftop (n=1) is insufficient. Negative accumulation widens the published radius (e.g. 566.9→1,202.6 m on the canonical AD002936 trajectory) without moving the centre. Refusals carry no radius and no coordinate.


// ══ 10 END-TO-END ARCHITECTURE ══════════════════════════════════════════════
#chapter("End-to-end architecture", lead: [One production request path, one field-evidence path, and an offline evaluation lane that is structurally unable to touch production — the separation is enforced in code, imports and tests, not in prose.])

#figframe("../figures/diagram_architecture.svg",
  [System architecture. Orange: implemented production components. Green: field evidence and belief update. Plum: place memory. Slate: offline experiments and the promotion gate, which feeds no request-path module. Schematics are labelled as such; every box maps to a repository module.],
  "sutra/ modules; README §4; PS3_MASTER_ARCHITECTURE.md")

#h2("10.1 Production request path")
Raw address → deterministic normalisation (NFKC, corpus abbreviation table, script-preserving spans; Experiment B kept this as the cheapest non-resolved-worse ring) → town/locality entity resolution (retrieval-v2) → official-only candidate generation (five static arms plus eligible evidence arms, as-of filtered) → deterministic RULE ranker (additive, reason-coded; `sutra/ranking.py`, byte-unchanged by the model study) → belief and uncertainty assessment (tier, status, radius map v1, reason codes) → eligibility gate v2 with request purpose → SERVE / VERIFY\_FIRST / REFUSE with the full decision ticket and ranked losers. Latency p95 38.9 ms for the whole path (Section 15).

#h2("10.2 Field evidence path")
Field visit with GPS trace → tail-3 coordinate estimator (check-in retained as provenance/fallback) → integrity weighting (media hash, trail↔check-in agreement, dwell realism, speed plausibility, agent-deviation z-scores; weights and reasons, never accusations) → append-only belief update (bounded: one visit moves belief at most one tier step and never promotes alone; idempotent by visit\_id) → place memory and, when doubt crosses thresholds, verification tasks. A `score_visit` endpoint simulates “what would this visit change” on a throwaway store copy and discards it — advisory by construction.

#h2("10.3 Offline lane and persistence")
Experiment scripts (A–D, precision, evidence-policy) run on frozen data with fixed seeds; fits happen in memory, no model file is written, and no request-path module imports the challenger library (asserted by `check_leakage.py`). Runtime persistence is a local SQLite store (`data/derived/runtime/sutra_store.sqlite`, schema store-2: 5,578 observations, 2,757 belief versions) plus versioned runtime indexes (addresses, localities, town centroids, token IDF, place blocks, memory) and offline packs (e.g. `pack-T2-7247f0bd3d96`, `contains_truth: false`). The slow retraining loop of the early design remains DESIGNED/NOT IMPLEMENTED; the fast evidence loop is IMPLEMENTED — and the report says so on the Method & Trust screen itself.

#h2("10.4 Repository map")
`sutra/` (28 modules: resolve, candidates, ranking, belief, uncertainty, evidence, memory, eligibility, purpose, asof, feeds, product, offline, store, …) · `tools/` (40+ reproduction, diagnostic and guard scripts) · `battle_model/` (React+Vite workbench served by the backend) · `data/official_ps3` + `data/derived` (frozen artefacts, receipts) · `notebooks/` (the master notebook) · `tests/` (125 tests).

