# SUTRA — Complete Project Explanation & Presentation Prep
### Semantic Utility for Traceable Resolution of Addresses · CreditNirvana Problem Statement 3

Use this file in three passes:
1. **Part I** — understand the whole project deeply (read twice).
2. **Part II** — what to actually present, slide by slide.
3. **Part III** — the judges' question bank with prepared answers. Memorise the **cheat sheet** at the end.

---

# PART I — UNDERSTAND THE PROJECT

## 1. The one-paragraph story

CreditNirvana's PS3 data gives us 3,117 loan addresses (often badly written, in English/Kannada/Devanagari), a frozen vendor geocode table whose "precision" field is a lie (a "locality" pin is typically ~386 m off, a "pincode" pin ~1.4 km off), and 5,578 field visits with GPS traces — of which 25.1% ended `address_not_traceable`, i.e. the agent went somewhere, couldn't find the borrower, and left. The naive task reading is "build a model that outputs better coordinates." The deeper reading — the one SUTRA is built on — is: **given a bad pin and a messy address, which of a small set of officially-sanctioned places is this record, how uncertain are we, what should the field team do about it, and how should future visits change our belief — without ever inventing precision the evidence doesn't support?**

SUTRA's answer is a system with five properties:
1. **Official-only candidates.** Every coordinate we can ever output comes from a restricted family: frozen vendor pin, locality centroid, town centroid, official landmark, exact-text address book — and, after visits, evidence-backed arms. No external map service, no scraped POIs, no third-party geocoder (governance decision, hash-checked tooling, zero outbound sockets).
2. **A deterministic, reason-coded RULE ranker.** We *tested* learned rankers (Logistic Regression, LambdaMART, Pairwise RankNet) against a pre-registered promotion gate on a grouped validation set (n=69). **None cleared the gate.** So production deliberately runs the inspectable rule; the learned models live offline, labelled "EVALUATED, REJECTED."
3. **Published uncertainty.** Every answer carries granularity (rooftop/street/locality/town), a belief tier (CONFIRMED/PROBABLE/APPROXIMATE/UNPLACEABLE) and a radius in metres taken from a *measured* error map (empirical p80 per stratum, published with n and coverage). Thin strata (street n=5, pincode n=4) are *withheld* below an n≥15 guard and fall back widened and labelled.
4. **Evidence, not truth.** Field visits are weighted evidence with integrity scores (media-hash duplicates, dwell realism, trail↔check-in agreement, agent baselines). A failed visit never authors or moves a coordinate — it can only raise doubt, widen a radius, open a task. This invariant is unit-tested.
5. **Place memory that cannot be poisoned.** Memory is keyed by physical place (co-location/adjudication), never by account, is append-only and contradiction-holding, and — the key defect we found and removed — may only emit a prior whose coordinate derives from accumulated field evidence. The old behaviour "remembered" the vendor pin and called it memory; we measured that harm (7 of 10 bad "memory" picks were the pin re-wrapped within 5 m) and shipped emp-v1 as a defect removal.

The same engine drives a six-screen operator workbench (Overview, Resolver, Places, Field Evidence, Verify Queue, Method & Trust) where every number is fetched live from the runtime, refusals render as designed decisions, and the Method screen states its own limitations. 125 automated tests pass; the full request path answers in p95 ≈ 39 ms against a 250 ms target.

## 2. Why the data forced every design decision (the causal chain)

| What the EDA showed | What it means | What SUTRA does about it |
|---|---|---|
| Vendor median error 376.4 m vs surveyed truth (n=100); pincode stratum 1,375.8 m | "Declared precision ≠ accuracy"; a pin is a neighbourhood claim dressed as a point | Granularity tiers + measured radius map; never present a bare dot |
| Failed visits (25.1%) sit ~194.7 m from *our* pin and 84.9% pin-closer on surveyed subset; dwell 1.28 min | A failed visit describes where the *geocode* sent the agent — it is evidence **about the pin**, not about the property | Failed visits inform doubt (radius, tier, task); they can never author/move a coordinate (tested invariant) |
| Successful visits sit 29.3 m from truth; GPS check-ins agree with each other within ~40 m; device accuracy median 9.8 m | Check-ins are the precise signal; the pin is the noisy one | tail-3 estimator: component-wise median of the last three fixes cuts visit-coordinate error 28.7 → 7.6 m (non-circular holdout, n=233) |
| 191 addresses in 81 cross-account co-location clusters; same-account addresses 3 km apart | Account identity ≠ physical place | Place blocks key memory and CV grouping; account fields banned from features (audited) |
| "Nehru Colony" exists in two towns; 260 addresses carry a pincode token matching no pincode; 237 addresses outside every town; old matcher let stale pincode outvote text → wrong locality on 118/292 rows | Text/pincode ambiguity is structural | retrieval-v2: require *all* locality tokens + rarest token by IDF, emit *all* localities of an ambiguous pincode |
| 36% of held-out addresses have a train-split met check-in within 30 m | Random splits leak; they would overstate generalisation | Place-block ledger splits (outer place-block / inner account), leave-block-out stress tests, 12-pattern leakage guard |
| Agent FA009: 25.6% duplicate photo-hashes (others ≤0.3%), clean GPS | Integrity anomaly is media, not geometry | Integrity *weighting* with reason codes — never accusations, never silent discards |
| Landmarks: 240 POIs but 14 distinct names ("Ganesh Temple" ×7) | Fuzzy landmark matching is almost always ambiguous | Landmark arm inert; adding arms leaves oracle series identical |

## 3. The pipeline, end to end (know this cold)

**Production request path (≈39 ms p95):** raw address + request purpose → deterministic normalisation (NFKC, abbreviation table, script-preserving spans) → town/locality entity resolution (retrieval-v2) → official-only candidate generation (5 static arms + eligible evidence arms, as-of filtered) → **RULE ranker** (additive, reason-coded, byte-unchanged by the whole model study) → belief & uncertainty (tier, status, radius-map-v1) → eligibility gate v2 with request purpose → **SERVE / VERIFY_FIRST / REFUSE**, with a full decision ticket: chosen candidate + arm + provenance, radius + basis + n + coverage, typed reason codes (`field_confirmed_x3`, `negatives_independent=1`, `promotion:ok`…), ranked losers with losing reasons. **No coordinate on refusal. No bare confidence percentage anywhere.**

**Field evidence path:** visit + GPS trace → tail-3 estimator (check-in kept as provenance/fallback) → integrity weighting (media hash, trail↔check-in agreement, dwell realism, speed plausibility, agent-deviation z-scores) → append-only belief update (bounded: one visit moves belief at most one tier step, two independent confirmations to promote, idempotent by visit_id) → place memory + verification tasks when doubt crosses thresholds.

**Offline lane (structurally separated):** experiments A–D, precision and evidence-policy studies run on frozen data, fixed seed 7, in memory, no model file written; no request-path module imports the challenger library (import guard asserts it). This is where the learned rankers live — and where they stay.

**Persistence:** local SQLite store (schema store-2: 5,578 observations, 2,757 belief versions), versioned runtime indexes, offline packs stamped `contains_truth: false`, workbench reads only via the API.

## 4. The experiments, in one breath each

- **Exp A (baseline):** vendor vs surveyed truth → 376.4 m median, 9% <100 m, 71% <500 m; stratified tail. *Sets the enemy.*
- **Exp B (preprocessing ablations):** TF-IDF/SVD/parser residue are byte-identical universes at 1.26–4.73× latency → closed by measurement. *Cheapest wins first, killed by measurement.*
- **Exp C (candidate ladder):** keeps four quantities separate that people conflate — retrieval coverage, retrieval recall, **oracle ceiling**, ranked answer. Baseline-only oracle 71% → +locality centroids 88% (254.1 m) on locked S-EVAL. *The 90% cold-start target is unreachable from official data — a bound, not an opinion.*
- **Retrieval v1→v2:** ceiling 87.67→91.44% (pool), locality-candidate median 811.9→319.6 m — **and ranked top-1 unmoved at 83.9%**, reported honestly: candidate generation ≠ candidate selection.
- **Exp D (model selection):** grouped S-VAL n=69, paired grouped bootstrap (10k, seed 7). RULE 84.06% / nDCG 0.9670 shipped; LOGISTIC 81.16% (a point worse + fails monotone-structure check); LAMBDAMART/PAIRWISE identical top-1 at worse nDCG; shuffled control collapses (56.52%). Gate also runs negative controls: shuffled labels collapse, pin-only reproduces RULE's top-1 exactly (the rule's value is *tie-breaking*, not geometry), zero outbound calls.
- **Headroom decomposition (why models can't win here):** on S-VAL the rule's top-1 is already the best available candidate for 55.1% of addresses; a *perfect* ranker could reach only 89.86% @500 m. The remaining error lives in the candidate set, not the ranking.
- **Coordinate policy (trace-tail):** 28.7→7.6 m median visit-coordinate error, judged across a time cut (non-circular). Labelled honestly: a *visit-coordinate* result, not cold-start accuracy.
- **Evidence-memory policy (emp-v1):** removes the pin-as-memory defect; warm licence narrows 45→31 answered while accuracy rises (96.77% @500 m on the 31); product lane bit-identical because the 14 withheld were pin re-wraps that still get the pin coordinate with pin radius and VERIFY_FIRST semantics. S-VAL gain +0.0290 [0.0000, +0.0725] → reported as a *power limit*, no validated gain claimed.
- **Rejected generators (negative results as output):** address-book near-dup (harms 66× more than rescues), pincode-consistent locality (pure harm), script lexicon (pincode path already places them), archetype routing (router collapses to the rule), sibling-pin transfer (dead end).

## 5. The evaluation philosophy — the five lanes, never merged

| Lane | n | Labels | What it legitimately claims |
|---|---|---|---|
| Cold start (static arms) | 100 | surveyed truth | official-only information: 71% <500 m, median 375.8 m |
| Product policy (warm→cold) | 100 | surveyed truth | shipped policy on all addresses: 76% <500 m, median 202.2 m |
| Warm / evidence subset | 31 | surveyed truth | eligible evidence-backed answers only: 96.77%, median 12.4 m (circular by construction → labelled so) |
| Static-lane oracle | 100 | surveyed truth | ceiling of the candidate family: 88% (254.1 m) — *not a prediction* |
| Temporal product proxy | 229 | promoted post-T0 check-ins | operating config vs *future* field evidence: 98.69% <500 m, median 7.9 m; paired Δ vs cold +0.1397 [0.0938, 0.1888] — resolved |

**Key sentence to own:** "No pair of these shares a population, and none is a business-outcome claim." The warm lane is a circular diagnostic and we say so; the evidential weight sits on the locked single S-EVAL read and the non-circular temporal holdouts.

## 6. The uncertainty contract

- Radius basis `empirical_p80` = 80th percentile of measured error in the calibration stratum, published with n and measured coverage.
- Locality 539.9 m (n=24, coverage 0.792) publishable; street 162.1 m (n=5) and pincode 1,204.2 m (n=4, coverage 0.000) **withheld** below n≥15 → fall back to locality radius, widened, labelled `calibration_fallback`.
- Negatives widen radius (canonical AD002936: 566.9 → 1,202.6 m) **without moving the centre**.
- Refusals carry no radius and no coordinate.

## 7. Engineering & safety invariants (say these with pride)

- 125 automated tests: acceptance 26 (T1 no candidate ⇒ no coordinate; T2 one negative ⇒ coordinate unchanged; T3 independent negatives ⇒ doubt out loud; T4 fake independence rejected; T5 valid confirmations promote), contract 51, product 39, no-fake-data 9.
- Latency: mean 23.2 ms, p95 38.9, max 64.6 vs 250 ms target — MET; candidate generation p95 23.1 ms/address.
- Zero outbound socket attempts on every run; dataset hash-verified byte-identical.
- As-of discipline everywhere (`observed_at < as_of`); belief recomputable at any instant; sealed S-EVAL read counter disclosed (including reads that went wrong during tooling — no parameter ever changed in response to a S-EVAL number).

---

# PART II — WHAT TO PRESENT (suggested 14-slide deck, ~10–12 min)

**Slide 1 — Title.** "SUTRA: an evidence-driven address geocoder that learns from field visits." One line: *We stopped asking "what are the coordinates?" and started asking "what do we believe about this place, and what should the field do next?"*

**Slide 2 — The data reality (the villain).** Three numbers with one chart: vendor median 376.4 m vs surveyed truth; 25.1% of visits fail after 1.28 min; failed visits cluster 194.7 m from *our own pin*. Punchline: "The coordinate without provenance, granularity and uncertainty is operationally unsafe."

**Slide 3 — Reframing the task.** Four operator questions: which place? how uncertain? what to do? what does the field change? Show the decision contract (tier + radius + gate + reasons).

**Slide 4 — System diagram.** The three lanes (production / evidence / offline) — point out the offline lane *cannot touch* production by construction.

**Slide 5 — Candidates first, ranking second.** Oracle ladder 71→88%; retrieval-v2 raises the ceiling **and the ranked top-1 doesn't move — we report both**. "Candidate availability and candidate selection are different problems."

**Slide 6 — The model study that said no.** Scoreboard table (RULE 84.06/0.9670 vs LOGISTIC 81.16 etc.). The gate design (beat beyond paired interval + regress nothing + negative controls). Punchline: "Model complexity was tested and found not to be evidence for deployment. That is a result, not a failure."

**Slide 7 — Visits are evidence, not truth.** tail-3 estimator 28.7→7.6 m (non-circular); the no-relocation invariant; FA009 integrity story → "weights, never accusations."

**Slide 8 — Place memory.** The defect (pin re-wrapped as memory, 7-of-10), the fix (emp-v1), the honest framing (fewer answers, better evidence; gain reported as power limit).

**Slide 9 — Uncertainty as a published contract.** Radius map with the n≥15 guard; the 566.9→1,202.6 m story; refusal = no coordinate.

**Slide 10 — Live product demo (screenshots or live).** Resolver SERVE (AD003067) → VERIFY_FIRST (AD002936) → REFUSE (AD000006). Show the reason codes and "what moved the score — not a confidence percentage."

**Slide 11 — Results, in separate lanes.** The five-lane table + temporal holdout 98.69% with paired interval. Say the governance sentence: populations never merged.

**Slide 12 — Engineering quality.** 125 tests, 39 ms p95, zero outbound, as-of discipline, sealed-read ledger.

**Slide 13 — Boundaries & roadmap.** What is IMPLEMENTED / EVALUATED-OFFLINE / NOT IMPLEMENTED (say it plainly — judges reward this). Top 3 roadmap items with acceptance criteria.

**Slide 14 — Conclusion.** "SUTRA doesn't guess a coordinate once; it builds evidence about places over time. Resolve → Verify → Learn → Resolve Better."

**Delivery rules for you:**
- Always say the population with the number ("76% on the product lane, n=100, surveyed truth").
- Pre-empt every weakness yourself (warm circularity, small n, unreachable 90% target). A weakness you disclose is a strength; a weakness the judge discovers is a wound.
- Never claim business impact, deployment, or "our model is better" — the RULE-is-production story *is* the sophistication.
- Demo the refusal. It is the most memorable 30 seconds available to you.

---

# PART III — JUDGES' QUESTION BANK (prepared answers)

### Problem & data
**Q1. Why not just use latitude/longitude or an external geocoder (Google/OSM)?**
Two reasons. Governance: the binding project decision restricts us to the official tables; tooling asserts zero outbound sockets, so the claim is enforceable, not aspirational. Science: an external geocoder would import someone else's undisclosed uncertainty; our task is to *publish* uncertainty, and coordinates are a local metric plane per town precisely so we never fake a projection we don't have.

**Q2. Your ground truth is only 100 addresses — how can you trust anything?**
We treat it as the scarce, precious thing it is: firewalled from all fitting and candidate generation (runtime guard proves the candidate path never reads it), used only for offline evaluation under a disclosed counter. Everything else uses operational proxies (disclosed as proxies) and *temporal* holdouts where labels are future promoted check-ins — strong evidence that is explicitly not surveyed truth. And we size every claim to its population; nothing is extrapolated.

**Q3. Isn't the supervision pool (292) biased?**
Yes — selected by visit outcome — and we say so on every ranking number ("conditional on that pool"). Exposure bias is disclosed with propensity logging as the eventual remedy. Honest conditioning beats silent bias.

**Q4. Why not random train/test splits?**
Measured leakage: 36% of held-out addresses have a train-split met check-in within 30 m; 39 place blocks cross the official split. Random splits would score place-neighbours as generalisation. We split by place-block ledger with account nesting, and stress with leave-block-out.

### Modelling
**Q5. Your production "model" is a rule. What is the ML contribution?**
The contribution is the *measurement science and the systems*: the candidate-ceiling analysis, the headroom decomposition proving where the error lives, the pre-registered promotion gate with negative controls, the trace-tail estimator, integrity weighting, place memory and the uncertainty contract. We used ML exactly as it should be used — tested under a gate that can say no. It said no. Shipping the rule *is* the validated conclusion.

**Q6. Why can't a better model win?**
Headroom decomposition: on S-VAL the rule's top-1 is already the best available candidate for 55% of addresses; a perfect ranker reaches only 89.86% @500 m vs the rule's 84.06%. The reorderable headroom is tiny; the residual error is in the *candidate set*. Ranking better cannot fix missing candidates.

**Q7. Did you overfit to S-VAL?**
We treat S-VAL figures for learned models as selection-contaminated and report an out-of-fold lens (5 spatial folds, place blocks whole) beside them; the advantage evaporates out-of-fold. RULE's numbers are additionally checked on the locked S-EVAL and temporal holdouts.

**Q8. Why not an LLM for address parsing?**
262 addresses are Kannada/Devanagari while every locality name is Latin — we measured a script-bridge experiment and it was rejected because the pincode path already places those rows (250.6 m). LLM parsing is on the roadmap *only* if a controlled evaluation slice exists; it's NOT IMPLEMENTED and we say so.

**Q9. Your labels are a proxy — isn't that label noise?**
It is disclosed proxy labelling (`operational_confirmation_proxy`), and evidence arms reproduce it by construction — which is exactly why the warm lane is labelled circular and why the evidential weight sits on the locked S-EVAL and temporal holdouts.

### Evaluation
**Q10. 88% oracle vs 76% product — which is your accuracy?**
Neither is "the" accuracy; they answer different questions. 88% is what the candidate family *contains* (a ceiling, not a prediction). 76% is the shipped policy on all 100 addresses against surveyed truth. 96.77% is only the 31 evidence-backed answers. 98.69% is the operating config against future field evidence. We refuse to blend them.

**Q11. The warm lane looks amazing (96.77%). Isn't that circular?**
By construction, yes — evidence arms reproduce the proxy label — and the report labels it a circular diagnostic on the first page it appears. Its legitimate use is showing the operating regime when trusted evidence exists; the non-circular claim is the temporal holdout.

**Q12. Product vs cold is +5 points — significant?**
No, and we say so: the paired interval is [0.00, +0.101] at n=100 — "not resolved by this dataset." The temporal holdout, with n=229, resolves the operating-config gain (+0.1397 [0.0938, 0.1888]).

**Q13. Why didn't you hit the 90% cold-start target?**
Because it is unreachable from official data: the static-lane oracle (best official candidate per address) is 88% on the locked set — an existence proof that requires the answer. We report the bound instead of pretending.

### Product & safety
**Q14. What happens on REFUSE? Isn't refusal a failure?**
Refusal is a designed success state: the envelope carries tier UNPLACEABLE, reasons, and *no coordinate field at all* — a downstream system cannot accidentally navigate to nothing. We count refusals and report their correctness.

**Q15. Can a malicious or erroneous visit move a coordinate?**
No single observation can: one visit moves belief at most one tier step; promotion needs two independent confirmations (different day/visit, not same media hash or agent-day); one negative never relocates; adjudication is append-only and idempotent. All tested (acceptance T1–T5).

**Q16. What stops memory from being poisoned by the vendor pin?**
emp-v1: a prior becomes memory only if its tier is CONFIRMED/PROBABLE *and* its coordinate derives from accumulated field evidence. We measured the old defect (7 of 10 bad memory picks were the pin within 5 m) and the harm of on-demand priors (temporal <100 m collapses 89.03→64.98%).

**Q17. Why publish a radius instead of a confidence score?**
A radius in metres with basis, n and measured coverage is actionable for a field team and falsifiable; a bare percentage is neither. The contract deliberately omits a confidence scalar.

### Engineering & integrity
**Q18. How do we know the numbers are reproducible?**
Frozen data (hash-verified), deterministic preprocessing (byte-identical), fixed seed 7, 10k paired place-block bootstraps, sealed S-EVAL read counter disclosed including mistaken reads — and no parameter ever changed in response to a S-EVAL number. A single chain regenerates everything.

**Q19. Latency?**
p95 38.9 ms vs 250 ms target on a store copy, 400 requests; candidate generation p95 23.1 ms/address over the full book. Live percentiles are deliberately *not* published by the product (it won't estimate what it can't measure).

**Q20. What is NOT implemented?**
Continuous online retraining, LLM parsing, RL visit allocation, external map matching, and any CreditNirvana production integration — plus any field-productivity/recovery-rate claim, which needs a controlled field evaluation with an exploration slice. The workbench says the same boundary in product language.

### Curveballs
**Q21. If the rule is best, why did you build all this infrastructure?**
Because "the rule is best" was only knowable *after* building the gate, the ceilings, the bootstraps and the holdouts. The infrastructure is the evidence; the rule is the verdict.

**Q22. What would you do with 6 more months?**
P1 adjudication write-path in production wiring; P1 single-call audit chain; P2 propensity logging + exploration slice; P2 controlled field evaluation with a pre-registered primary metric — "no claim published without it." Learned rankers revisited *only* if the candidate ceiling moves beyond the paired interval.

**Q23. What was your biggest mistake?**
Early designs let the vendor pin re-enter as "memory" and let early reports quote warm medians (58.0/206.7 m) that the coord-v2 label change superseded. Both were caught by measurement, repaired in the open, and the superseded receipts are retained and labelled — we keep our mistakes as provenance.

**Q24. Why should a bank trust a system that refuses?**
Because the alternative — a dot for every address, always — is the system that sends agents 1.4 km from the property. SUTRA tells the bank, per address, what it knows, how big its doubt is, and what would reduce it. That is risk management, not evasion.

---

# CHEAT SHEET — MEMORISE THESE

| Quantity | Value |
|---|---|
| Addresses / visits / GPS points | 3,117 / 5,578 / 160,406 |
| Vendor vs surveyed (n=100) | 376.4 m median · 9% <100 m · 71% <500 m · p90 839.2 |
| Strata medians | rooftop 25.6 (n=1) · street 108.6 (16) · locality 385.9 (73) · pincode 1,375.8 (10) |
| Failed visits | 1,400 (25.1%) · dwell 1.28 min · 194.7 m from our pin · 84.9% pin-closer · 1,603.2 m from truth |
| Successful visits | 29.3 m from truth |
| Co-location | 191 addr / 81 clusters / 127 cross-account pairs · same-account 3,011.6 m · blocks 3,007 |
| Leakage | 36% @30 m · 81% @100 m |
| Retrieval v1→v2 | oracle 87.67→91.44% · locality median 811.9→319.6 m · top-1 unmoved 83.9% |
| Scoreboard (S-VAL n=69) | RULE 84.06% med 249.0 nDCG 0.9670 · LOGISTIC 81.16/258.0/0.9516 · shuffled 56.52% |
| Headroom | rule-best 55.1% · perfect ranker 89.86% @500 |
| Locked S-EVAL | cold 71% (375.8) · product 76% (202.2, p90 697.3) · warm n=31 96.77% (12.4) · oracle 88% (254.1) |
| Per town (product) | T1 66.67 (367.3) · T2 82.76 (126.4) · T3 78.95 (162.1) |
| Temporal T0=05-15 | cold 84.72 (271.2) · product 98.69 (7.9) · promoted 100 (6.1) · Δ +0.1397 [0.0938, 0.1888] |
| Trace-tail (n=233) | 76.39→86.27% <100 m · median 28.7→7.6 m |
| Memory defect / emp-v1 | 7-of-10 pin re-wraps · warm 45→31 · collapse 89.03→64.98% · S-VAL +0.0290 [0, +0.0725] |
| Radius map | locality 539.9 (n=24, cov .792) · street 162.1 (n=5, withheld) · pincode 1,204.2 (n=4, withheld) |
| Engineering | 125 tests · p95 38.9 ms vs 250 · 0 outbound · store 5,578 obs / 2,757 versions · queue 278 |
| Versions | sutra-1.0 · candidate-rules-v2 · evidence-policy-v3 · radius-map-v1 · gate-v2 · as-of 2026-06-01 · frozen 9abebb8f |

**Glossary (one-liners for the stage):** *oracle* = what the candidate family contains, not what we predict · *warm* = addresses with eligible field evidence at the cut · *as-of* = every read sees only the past · *empirical_p80* = 80th percentile of measured error, published with n and coverage · *place block* = physical-place key from co-location/adjudication · *decision ticket* = coordinate + granularity + radius + reasons + losers.

Good luck. Resolve → Verify → Learn → Resolve Better.
