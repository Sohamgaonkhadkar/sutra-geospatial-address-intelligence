# SUTRA Final Report — Evidence Ledger

Every headline number used in the report, with its canonical source artifact, population, and caveats.
Abbreviations: NB = notebooks/SUTRA_Model_Training_FINAL.ipynb; POR = data/derived/precision_optimization_report.md;
PCR = data/derived/precision_optimization_results.csv; EMP = data/derived/evidence_memory_policy_report.md;
IMP = PS3_IMPLEMENTATION_PHASE_REPORT_2026-10-07.md; EXPB/C/D = experiment_b/c/d_report.md; EXPA = experiment_A_report.json;
ACC = data/derived/acceptance_report.json; EDA = PS3_DATA_EDA_AND_PREPROCESSING.md; FIN = PS3_FINAL_REPORT.md (early consolidated);
INT = SUTRA_FINAL_INTEGRATION_REPORT_2026-10-08.md; CFG = data/derived/final_precision_config.json.

## A. Dataset inventory (source: NB cell 3, EDA §1, EXP C §3)
- addresses 3,117 (7 cols) · baseline_geocodes 2,880 · field_visits 5,578 · visit_gps_points 160,406 · accounts 2,400 · agents 30 · localities 36 (35 names; "Nehru Colony" in 2 towns) · towns 3 · landmarks_poi 240 (14 distinct names) · surveyed_addresses 100 (T1 33/T2 29/T3 38; 0 OUT; 1 rooftop).
- address flags: no_digit 9 · no_separator 24 · pin_unknown 260 · outside_town 237 · dup_text 10 (NB cell 5).
- baseline precision strata: locality 2,052 · street 504 · pincode 274 · rooftop 50 (NB cell 5).
- Coordinates are local metric (x, y) metres per town, NOT lat/lon (README §5).
- GPS: median 26 fixes/visit (max 80); gps_accuracy_m median 9.8 m (research/precision/temporal.py); 34 axis artefacts (0.021%) flagged & excluded; max implied speed 32.2 km/h (FIN §B).
- Visits span 2026-04-01 → 2026-06-29; no Sunday visits (EDA line 868).

## B. Vendor baseline error vs SURVEYED truth (S-EVAL, n=100) — EXPA, EXP C ladder, EXP D §9
- frozen-baseline-only: median 376.4 m · p80 610.0 · p90 839.2 · max 4,807.7 · <100 m 9% · <250 m 35% · <500 m 71%.
- per-stratum medians (FIN §B, n stated): rooftop 25.6 (n=1) · street 108.6 (n=16) · locality 385.9 (n=73) · pincode 1,375.8 (n=10).
- NOTE: final cold lane (retrieval-v2 + rule) reads median 375.8 m on the same 100 (POR §6) — 0.6 m difference from retrieval-v2 top-1 changes; cite 376.4 for "vendor baseline", 375.8 for "cold lane".

## C. Vendor baseline vs PROXY truth (pool n=292) — NB cell 8, EXP C stability row
- median 260.3 m · mean 368.9 · <100 15.4% · <250 48.3% · <500 83.9%.
- medians by declared precision: rooftop 18.1 · street 118.0 · locality 313.7 · pincode 1,392.8.

## D. Retrieval v1 → v2 (pool n=292) — POR §1 lane table (canonical)
- v1: 3.233 cand/addr · locality-candidate median err 811.9 m · oracle <100 0.1781 · <250 0.5548 · <500 0.8767 · median 214.1 · top-1 0.839.
- v2: 3.432 · 319.6 m · 0.1918 / 0.589 / 0.9144 · 196.1 · 0.839 (top-1 unchanged).
- v1 wrong locality on 118/292 rows (centroid err median 799.5 m) — POR §1, research/loc.py.
- S-VAL oracle: 0.8696 → 0.8986 (median 184.7 m) — EXP B/C.
- DISCREPANCY NOTE: IMP §3.8 and probe prod.py quote 0.8801→0.9144 (medians 229.9→215.5); POR §1 lane table (0.8767/214.1) is the final published comparison; README uses 87.67/91.44. 0.8801 retained only as probe-run value.

## E. Candidate ceilings — EXP C ladders + POR §6
- S-EVAL static-lane oracle: 0.88 <500 m, median 254.1 m (POR §6). Ladder (EXP C): baseline 376.4/0.71 → +locality 285.8/0.88 → +town 285.8/0.88 → +landmark 255.8/0.88 → +address_book 255.8/0.88.
- S-VAL oracle 0.8986, median 184.7 m. Pool oracle 0.9144, median 196.1 m.
- Absolute official-point bound ≈1.0 @ 38.8 m median (existence proof only; POR §4/research bound.py).

## F. Model selection, S-VAL n=69 — FINAL FROZEN SCOREBOARD (IMP §3.7 table; NB cells 44-46)
- RULE shipped: <100 15.94% · <250 50.72% · <500 84.06% · median 249.0 m · nDCG@5 0.9670.
- LOGISTIC rejected: 17.39/49.28/81.16 · 258.0 · 0.9516 · monotone violations (f_sim_ratio −0.0133; f_dist_to_town_centroid_m +0.3597; EXP D §4).
- LAMBDAMART rejected: 84.06 · 249.0 · 0.9640 (identical top-1 series).
- PAIRWISE rejected: 84.06 · 249.0 · 0.9653.
- LAMBDAMART_SHUFFLED control: 56.52% · 398.3 · 0.8090.
- Promotion gate: beat RULE beyond paired grouped bootstrap (10k resamples, place-block groups, seed 7), no regression, LBO-consistent.
- ARTIFACT NOTE: final_frozen_experiment_d_scoreboard.json referenced by NB is absent in this snapshot; its values are embedded identically in IMP §3.7 and NB cell 44 output. Superseded run = experiment_d_report.md/receipt (RULE nDCG 0.9291; LOGISTIC 0.8261/224.7; and on S-EVAL LOGISTIC 0.81 vs RULE 0.71 resolved better — gate still rejects on S-VAL). Document both; final frozen numbers govern.
- Precision re-test on retrieval-v2 candidates (POR §3): logistic 0.8261/224.7 not-resolved (−0.0145 [−0.0725, +0.0435]); lambdamart identical; pairwise 0.5942/397.1 resolved worse (−0.2464).
- Headroom (EXP D §6.6): rule top-1 already best candidate on 55.1% S-VAL (38/69); perfect ranker = 0.2029 <100 / 0.8986 <500 (whole reordering headroom +0.04/+0.03).

## G. Locked S-EVAL outcomes, frozen config 9abebb8fb62df2ca… (POR §6)
- cold n=100: 9 / 35 / 71% · median 375.8 · p75 538.7 · p90 810.8.
- warm n=31: 83.87 / 93.55 / 96.77% · median 12.4 · p75 16.4 · p90 195.9. (warm = eligible evidence-backed answers at cut; NOT all addresses.)
- product n=100: 33 / 55 / 76% · median 202.2 · p75 490.0 · p90 697.3.
- Per-town product: T1 n=33 66.67% 367.3 m · T2 n=29 82.76% 126.4 · T3 n=38 78.95% 162.1.
- warm P0 (pre emp-v1) n=45: 57.78 / 75.56 / 82.22% · median 16.4 (EMP §7) — licence narrowed 45→31, accuracy rose; product lane bit-identical.

## H. Temporal holdout (non-circular) T0=2026-05-15 (POR §5, PCR)
- cold n=229: 12.23 / 46.72 / 84.72% · median 271.2 · p75 399.9 · p90 627.7.
- warm n=225: 85.78 / 93.33 / 98.67% · 7.5 · 16.0 · 161.1.
- product n=229: 85.15 / 93.01 / 98.69% · 7.9 · 18.8 · 177.3.
- promoted_only n=96: 94.79 / 96.88 / 100% · 6.1.
- paired vs cold: <500 +0.1397 [0.0938, 0.1888]; median −236.4 m resolved better.
- T0=2026-05-01: cold n=269 14.87/48.70/84.76% 260.8 · warm 243 84.77/91.77/98.77% 8.1 · product 269 78.81/90.71/98.88% 8.6 · promoted 61 85.25/91.80/100% 6.6.
- LABEL: promoted check-ins at/after T0; candidates strictly before T0 → non-circular. NOT surveyed truth.

## I. GPS trace-tail estimator coord-v2-trace-tail (POR §5b, CFG)
- n=233 cross-cut visits. check-in: <100 76.39% · <250 92.70% · median 28.7 m. tail-3 median: <100 86.27% · <250 93.99% · median 7.6 m. <500 both 97.42%.
- label shift median 13.7 m; cold lane invariant under either label (0.8459) → improvement attributable to estimator.
- Probe values (research trace.py, superseded): 0.7296→0.8240, 54.9→22.7 m.
- Interpretation: visit-coordinate estimation result; NOT cold-start geocoding accuracy.

## J. Failed visits (EDA, FIN §C)
- address_not_traceable: 1,400 of 5,578 (25.1%); median dwell 1.3 min; median 195 m from own pin; 17.6% within 100 m of pin.
- surveyed subset n=53 failures: median 1,603.2 m from truth · 253.4 m from pin · 84.9% pin-closer.
- surveyed successes n=93: 29.3 m from truth · 396.9 m from pin · 3.2% pin-closer · dwell 9.7 min.
- 443 visits <60 s. FA009: 156 duplicate photo hashes of 610 visits (25.6%); others <0.3%.
- Outcome census: not_traceable 1,400 · locked 1,249 · met_borrower 1,114 · met_family 1,062 · neighbour_shifted 455 · no_such_person 206 · cash 92.

## K. Place structure & leakage (EDA, NB cells 20/29, FIN addendum, PS3_LEAKAGE)
- place blocks 3,007 (81 multi-address, 2,926 singletons, largest 7) · co-location: 191 addresses in 81 cross-account clusters (≤30 m met check-ins) · 127 cross-account pairs.
- same-account addresses: median 3,011.6 m apart.
- 39 blocks (99 addresses) cross the official account split; 344 test addresses with met visit: 124 (36%) within 30 m and 279 (81%) within 100 m of a train met check-in.
- firewall union 145 (100 surveyed + accounts + blocks) = 4.65% corpus; splits S-TRAIN 223 / S-VAL 69 / S-EVAL 100 / EXCLUDED 45 / POOL_UNSUPERVISED 2,680.
- as_of 2026-06-01T00:00:00Z · protocol-v1-immutable · outer place-block / inner account.

## L. Memory integrity defect (EMP)
- 10 pool rows >500 m under P0; 7 = memory re-wraps vendor pin (within 5 m of pin, outranks field evidence via +0.08 primary_eligible).
- frozen emp-v1 fixes 4 (AD000037 1302.4→152.9; AD000624 1392.8→148.7; AD002696 624.4→156.0; AD002711 794.8→0.0), breaks 0; warm licence 45→31; product bit-identical (0.33/0.55/0.76, 202.2 m).
- P5 on-demand prior alone collapses temporal <100 0.8903→0.6498 → pin-derived memory harmful.
- shipped as DEFECT REMOVAL, not accuracy claim; S-VAL +0.0290 [0.0000, +0.0725] not resolved alone; pool +0.0137 [0.0034, +0.0280] resolved.
- negatives never relocate: 130 addresses carry negatives; 0 relocations.

## M. Rejected generators / approaches
- near-duplicate address-book: coverage 42.81% · median 247.0 m · rescues 1 · worse 66 (POR §5c).
- pincode-consistent locality: coverage 85.27% · median 321.9 m · rescues 0 · worse 144.
- script lexicon (262 Kannada/Devanagari addresses): 315.1 vs 250.6 m, 0 better → rejected (POR §5c2).
- archetype routing: identical series (delta 0.0) → rejected (POR §5d).
- place_neighbour: coverage 14.04% · neighbour median 61.9 m vs placebo 2162.1 m, but 0 product answers changed / doesn't clear C2 gate → LOCKED (POR §5e).
- preprocessing B3/B4 residue (TF-IDF/SVD, parser stats): byte-identical candidate universes, 0 accepted residues, 1.26×/4.73× latency → rejected (EXP B).
- sibling transfer, pincode rescue, empirical locality centres: dead ends (research/precision README).
- landmark arm: 240 POIs, 14 names; nearest same-type POI median 269.4 m (32/292 mentions) → inert arm.

## N. Runtime / engineering (ACC, INT)
- Acceptance 26/26 pass; full suites 125/125 (26 acceptance + 51 contract + 39 product + 9 no-fake-data), 26.8 s (INT §4).
- Latency artifact ACC: n=400 requests, full path on store copy: mean 23.212 ms · p50 21.666 · p95 38.925 · p99 53.848 · max 64.608 · target p95<250 MET. (NB re-run printed p50 13.8/p95 25.3 in its env — cite artifact values.)
- store: 5,578 observations · 2,757 belief versions · memory entries 1,477 · places 3,007 · addresses 3,117 indexed · evidence rows at cut 3,788 (positive 1,539 / negative 1,141 / ambiguous 1,108) · warm 1,280 / cold 1,837 · tiers 911 APPROXIMATE / 271 CONFIRMED / 295 PROBABLE · queue 278 (273 MOVED_SUSPECTED + 5 CONTESTED) · packs T1/T2 valid until 2026-06-08 · outbound calls 0.
- versions: sutra-1.0 · candidate-rules-v2 · evidence-policy-v3 · radius-map-v1 · gate-v2 · purpose_rules-v1 · directions-v1 · store-2 · protocol-v1-immutable.

## O. Uncertainty radius map v1 (sutra/config.py)
- locality: 539.9 m · n=24 · measured coverage 0.792 · publishable.
- street: 162.1 m · n=5 · withheld (<15). pincode: 1,204.2 m · n=4 · coverage 0.000 · withheld. rooftop: n=1 · insufficient.
- non-publishable strata fall back to locality, widened + labelled.

## P. S-EVAL read discipline (disclosed in POR §6, EMP §7)
- 10 historical truth reads during development (8 pre-chain tool debug reads incl. discarded/failed ones, 1 chain read, 1 snapshot-fix read); final runs reuse persisted snapshots (counter increments 0). No parameter changed in response to any S-EVAL number; frozen hashes precede first read.

## Q. Demo fixtures (SUTRA_FRONTEND_DEMO_FLOW) — product truth examples
- AD003067 SERVE: CONFIRMED/STABLE, street, field_evidence c-28f5aface67c, radius 566.9 m empirical_p80 n=24 cov 0.792 widened(negative_accumulation), 3 independent confirmations, belief v7.
- AD002936 VERIFY_FIRST: APPROXIMATE/MOVED_SUSPECTED, radius 1202.6 m after 2 independent negatives; coordinate unchanged across 9 as-of steps (566.9→1202.6 widening, tier CONFIRMED→APPROXIMATE).
- AD000004 cold VERIFY_FIRST: APPROXIMATE/STABLE, frozen_baseline locality, radius 809.8 m, 0 observations.
- AD000006 REFUSE: UNPLACEABLE, no candidate, no coordinate. AD000002 NOTICE_SERVICE REFUSE purpose_work_like.
