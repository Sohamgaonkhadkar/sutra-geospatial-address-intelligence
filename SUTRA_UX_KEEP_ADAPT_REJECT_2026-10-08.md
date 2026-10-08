# BATTLE-MODEL UX → SUTRA: KEEP / ADAPT / REJECT (Step 2 deliverable)

**Source analysed:** Google Drive folder `1dIyX8LkpH4J30QmC_jXuSB-KqbC1i_Rw` → `work/` — 22 files,
260,823 B, **byte-identical to the Battle-Model ZIP** already integrated (all 16 files of the structure
you listed are present and verified; the folder export omits only `vite.config.ts`).
**Decided against:** the live SUTRA service, not against the design.
**Marker key:** `[VERIFIED]` = re-measured in this session · `[INFERENCE]` = follows from the code.

Every row answers one question: *what does this feature do in the real field workflow, and which real
SUTRA output fills it?* No row keeps an invented value.

---

## 1 · Decision table

| # | Battle-Model feature (as written) | PS3 relevance | SUTRA backend source (real) | Decision |
|---|---|---|---|---|
| 1 | **Resolver workstation** — 3-zone split: intake → ranked arms → decision ticket | Core: an operator's whole job is "messy address in, defensible decision out" | `POST /resolve` (candidate, score, `eligibility`, `decision_ticket`, `reason_codes`, `score_terms`, `support`, `task`) | **KEEP** |
| 2 | **Local metric plane** (SVG, metres, N↑, zoom/pan, graticule) | Core: the only honest map for this data; also the constraint (no basemap/lat-lon) | `GET /v1/plane/{town_id}` (roads/locality reference + graticule) · `GET /v1/geometry/{address_id}` (candidate points, visit points, ring) | **KEEP** |
| 3 | **Candidate list** (arm · score · granularity per row) | Core: operators must see the alternatives and *why the loser lost* | `arms_considered[]` + `alternatives[].lost_reason` (typed, from the engine) | **KEEP** |
| 4 | **Candidate score bars** — six-part decomposition (`text/component/source/evidence/memory/freshness`) rendered as the primary ranking UX | The *idea* of "show your work" is right; these six parts are an invented model with invented weights, and six bars invite re-ranking by eye | `score_terms[]` (the engine's own terms and their contributions) + `score_reasons[]` | **ADAPT** — show the engine's terms in a plain list on disclosure; do **not** present raw internals as the primary ranking story, and never render a bar the service didn't send |
| 5 | **Decision ticket / gate panel** (`AUTO-CONFIRM` / `HUMAN-COMMIT` / `UNPLACEABLE` at 0.85/0.60/0.15/25 m) | The panel is right; the vocabulary and thresholds were React's own | `eligibility.{action,reason,rule_version}` (`SERVE` / `VERIFY_FIRST` / `REFUSE`) + `decision_ticket.{headline,margin,why[],refusal{}}` | **ADAPT** — keep the panel, drop the client-side `verdict()` entirely |
| 6 | **Evidence timeline** (visits with dwell, device, photos, outcomes) | Core: evidence is the product's only way to move a location | `GET /v1/evidence` + `GET /v1/address/{id}/observations` | **KEEP** |
| 7 | **Visit "integrity" panel** (mock-location flag, time skew, trail σ) | Integrity/independence are exactly the right questions | `reason_codes[]` carry `trail_agrees` / `trail_disagreement` / `gps_fine|moderate|coarse`; `independence` field on the audit row | **ADAPT** — render only what the policy recorded; where a field is `null`, say "not asserted" (added this session) |
| 8 | **Verify Queue** (case list, facets, priority, age, row detail, action buttons) | Core: this is where an operator spends the day | `GET /v1/tasks`, `/v1/tasks/verify-first`, `/v1/tasks/{id}`, `/v1/address/{id}/case` | **KEEP** |
| 9 | **SLA burn-down meters** (`48h left`, colour-coded) | No SLA exists in the data, and a fabricated deadline drives real behaviour | *none* | **REJECT** |
| 10 | **Queue actions** — "Assign to me", local close | The write path exists; assignment does not | `PATCH /v1/tasks/{id}` (state machine from the service) · `POST /v1/adjudicate` (`confirmed`/`not_true`/`inconclusive`) | **ADAPT** — real transitions and decisions, labelled with the operator's words (`Start review`, `Confirm`, `Not true`, `Inconclusive`, `Reopen`) while the canonical values travel on the wire |
| 11 | **Hash-chained audit ledger** (in-browser, `chainHash(prev, …, Date.now())`) | The audit surface is right; a non-recomputable client hash is worse than none | `GET /v1/audit/{belief_id}` — server reconstruction: winner arm, weighted evidence, lost alternatives, uncertainty change, tasks | **ADAPT** — read-only chain from the service; the client-side ledger and its fake hashes are deleted |
| 12 | **Places / place memory** (durable object, history, contradictions) | Core: memory is what makes the second visit cheaper than the first | `GET /v1/places`, `GET /v1/place/{id}` (versions, contradictions, `coordinate_unchanged`) | **KEEP** |
| 13 | **Place confidence %** (colour-coded meter) | A percentage is not publishable here and duplicates the uncertainty contract | tier + `radius{radius_m, basis, measured_coverage, n_calibration}` + status | **REJECT** the %, **REPLACE** with tier/radius/coverage (already done) |
| 14 | **Overview** (KPI row, warm/cold, daily series, service strip) | Operational framing is right; the numbers are not | `GET /v1/overview` (indexed, answered, cases needing field, visits, three frozen populations, queue by cause, workload by town, newest evidence) | **ADAPT** |
| 15 | **Service health strip** (`parse-svc`, `cand-idx`, `p50ms`, `errPct`, `DEGRADED`) | Invented infrastructure telemetry reads as fact | `/health` + `/v1/method-trust` (counters, packs, capability labels) | **REJECT** the fake services; **KEEP** the "system health" idea fed by real counters |
| 16 | **Daily accuracy series** (warm/cold % per day) + `warm 0.914 / cold 0.628` | Invented accuracy is the single most dangerous artefact in the prototype | the three **frozen populations** from `/v1/method-trust` (cold 0.71 n=100 · warm 0.9677 n=31 · product 0.76 n=100), stated separately | **REJECT** the series; **KEEP** the layout slot now filled by the frozen populations |
| 17 | **Method & Trust** (pipeline, gates, weights, audit table) | Core: the trust screen is a product feature here, not marketing | `GET /v1/method-trust` (real receipts) + `GET /v1/audit/{belief_id}` | **KEEP**, with the four labels `IMPLEMENTED` / `DESIGNED` / `NOT YET IMPLEMENTED` / `NOT MEASURED` |
| 18 | **Fixture replay intake** (exact string match on 4 captured scenarios, "FREE-TEXT RESOLUTION NEEDS THE LIVE PIPELINE") | An intake box that cannot resolve is not an intake box | `POST /resolve` with the typed text | **REJECT** the replay; **KEEP** the box, now live (it resolves `Gali no-11, Azad Mohalla, Devgarh Nagar - 970203` → AD002936) |
| 19 | **Fake providers** ("Gazette Registry", "Municipal Parcel DB", "Postal PIN Directory", "Field Memory") | Provenance must name the official tables that actually exist | `candidate.arm` + `provenance{rule_version, built_from, n_observations, stratum, licence_class}` | **REJECT** the names; **KEEP** the provenance slot fed by the arm's real provenance |
| 20 | **Fake GPS** (`u-blox M10`, `GS-07`, `cepM`, `hdop`, `sats`, `timeSkewS`) | Device detail must come from the record or not appear | `captured{gps_accuracy_m, x, y, note}` + `device_id` + `agent_id` | **REJECT** the invented constellations/HDOP; **KEEP** the real accuracy and device id |
| 21 | **Random task IDs** (`VQ-49${Math.random()}`) | An id that cannot be looked up is not an id | `task.task_id` from `POST /resolve` (e.g. `VF-AD002936-MOVED_SUSPECTED`) | **REJECT** |
| 22 | **Simulated network delay** (`net(120)` … `net(150)`) | Manufactured latency in a product that is judged on trust | real fetch over a same-origin relative path | **REJECT** |
| 23 | **Session ledger + operator identity** (`OPR K. Deshmukh`, `SEAL-01`, epoch `2025-W46`) | The as-of discipline is right and load-bearing; the identity and epoch were decoration | the service's own `as_of` cut, version block and pack freshness; reviewer identity sent with each write | **ADAPT** — keep the "as of" control, delete the invented persona/epoch |
| 24 | **Base cartography** (roads/landmarks drawn from `fixtures.SCENE`, incl. "Pune–Nashik Hwy") | A plane with no reference geometry is unreadable; invented real-world names are unacceptable | `GET /v1/plane/{town_id}` — the town's own reference points and graticule, drawn in metres | **ADAPT** — keep the drawing code, feed it the town plane (77 landmarks + graticule for T2) |
| 25 | **Visual language** — paper/graphite palette, IBM Plex Serif numerals + Mono diagnostics, dense tables, 6-screen rail | The strongest part of the prototype; it reads as an operations workstation, not a SaaS dashboard | n/a (presentation) | **KEEP**, unchanged — `src/index.css` is byte-identical to the prototype |
| 26 | **`utils/cn.ts`** (clsx + tailwind-merge) | Dead code (zero importers); the live `lib/utils.ts` `cn` silently drops class-merge resolution | n/a | **REJECT** (deleted) |
| 27 | **Six `*_soft` colour tokens used by the prototype's classes** | Only exist if the Tailwind theme declares them; otherwise those classes render nothing | n/a | **FLAG** — see §3 |

---

## 2 · What "ADAPT" means concretely (the four that changed shape)

| Feature | Prototype behaviour | Deployed behaviour | Why it is not a redesign |
|---|---|---|---|
| Score bars | six invented parts, bar lengths = the ranking story | decision ticket + typed `reason_codes`; the engine's `score_terms` on disclosure | same panel, same hierarchy; only the data source changed |
| Gate panel | `verdict()` recomputed thresholds in React | `eligibility` + `decision_ticket` rendered verbatim | the operator sees the same five states, now the service's |
| Audit ledger | client-side list with fake hashes | `GET /v1/audit/{belief_id}` read-only reconstruction | same ledger row anatomy (seq/time/actor/action/detail/hash), real values |
| Evidence visit detail | outcome/devices/photos + invented integrity | the same panel **plus** a "what this visit did to the belief" disclosure read from the chain: weight, evidence class, independence (or "not asserted"), winning arm, the belief it produced (v/tier/status/radius), and the policy's integrity codes | added disclosure only; no existing row removed |

---

## 3 · A check that came back clean (recorded because it was a real risk)

My first draft of this section claimed the prototype's soft-tint classes (`bg-ok-soft`, `bg-crit-soft`,
`bg-warn-soft`, `bg-accent-soft`, `bg-accent-faint`, `bg-cool-soft`, `bg-plum-soft`) might resolve to
nothing, since they only work if the build's theme declares them. **That claim was wrong, and it was
caught by checking before it shipped in this document.**

`[VERIFIED]` `src/index.css` declares **25 colour tokens**, and every custom colour utility used across
`src/**.tsx` resolves against them — including all seven `*-soft` tints and `accent-faint`. The single
apparent miss was `border-l-2`, which is Tailwind's left-border-width utility and not a colour at all.
So: no dangling colour classes, nothing to fix, and `index.css` remains byte-identical to the prototype.

## 4 · Verification of the state described above (2026-10-08, this session)

| Gate | Result |
|---|---|
| `bash tools/reproduce.sh full` | **exit 0** — every numbered step incl. console + workbench builds |
| `pytest tests/ -q` | **132 passed** (27.46 s; 9 of them the no-fake-data guard, which scans `battle_model/src` **and** the shipped bundle; 4 accessibility) |
| HTTP smoke (`tools/smoke_test.py`) | **21/21** |
| Workbench browser smoke | **23/23** (two checks added this pass: chain-derived belief effect; operator-word action labels) |
| Guards | leakage ALL PASSED · workspace ALL CHECKS PASSED · links ALL RESOLVE |
| Store after all write-path checks | 5,578 observations · 2,757 beliefs · 278 task events · 0 receipts — the documented baseline; every write ran against a copied store on `:8001` |
| Bundle served at `/` | `battle_model/site/index.html`, 352,031 B after a clean build, byte-identical to `GET /` |

Demo spine, all read from the service (never hard-coded in React): AD003067 → `SERVE`, r 566.9 m ·
AD002936 → `VERIFY_FIRST`, widened r 1202.6 m, `MOVED_SUSPECTED`, coordinate unchanged
(1130.5, 2970.0) · AD000002 → `REFUSE` with no coordinate served.

---

*Sources:* `[S61]`/`[S81]`/`[S82]` — offline-first field practice (append-only evidence, idempotency
keys, hold-then-conflict) is the standard behind the Verify Queue's write path; `[S69]` (minimum-sample
guard) and `[S73]` (heavy-tailed geocoder error) are why uncertainty is shown as radius + coverage + n
and never as a confidence percentage; `[S95]` is the data policy that makes rows 16, 19 and 20
non-negotiable.
