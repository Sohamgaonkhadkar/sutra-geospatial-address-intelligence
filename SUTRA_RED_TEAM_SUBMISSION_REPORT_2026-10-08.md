# SUTRA — final red-team, clarity, and submission report (2026-10-08)

This closes the hardening pass. It is not a new feature and it does not retune the frozen engine. Every operational number below was read from the service, the store, a test run, or `bash tools/reproduce.sh full` (exit 0, this pass).

The bar the site was judged against: a person who has never seen SUTRA opens it and, within about half a minute, can say what problem it solves, what happens to a messy address, why a location was chosen, when it refuses, how field evidence improves the next answer, and what a human can verify. Every value on the screen is the backend's, or a plain-language label on a value the backend sent.

---

## 1 · Current system state

One Python process serves the workbench and the API on the same origin (`tools/serve_runtime.py`, `0.0.0.0`, `$PORT` or 8000). `/` is `battle_model/site/index.html`, a single file. A clean build of the clarity pass is **352,031 bytes** (vite 352.03 kB, gzip 100.53 kB). The reproduction chain rebuilt that file and `stat` still reads 352,031. `GET /` was byte-identical to the file on disk before the chain took the store lock and the process was stopped. A warm Vite cache can change the byte size without changing behaviour; `tools/reproduce.sh` deletes `site/` and `.vite` before building.

The shipped store, after the chain's rebuild from the official history: 5,578 observations, 2,757 belief versions, 278 task events, 0 receipts. Versions on the wire: sutra-1.0, candidate-rules-v2, evidence-policy-v3, radius-map-v1, gate-v2.

What is real: every count, candidate, coordinate, radius, decision, reason, task and audit row the workbench shows. What is presentation: the words "Field evidence", "Vendor pin", "Remembered place", "can be used", and the three decision sentences. Those are a fixed map from the service's own ids and gate values. Unknown ids fall through to the id itself. Nothing is invented to fill a card.

The original Battle-Model fixture layer is gone. `fixtures.ts` is not a production source. The browser smoke asserts that no request URL contains fixture, mock or demo, and that a typed address resolves through `POST /resolve`. There is no `POST /v1/resolve`.

## 2 · Backend interactivity audit

Exercised on the running service, then again by the browser smoke (68 API calls, all real routes, 0 responses ≥ 400, 0 console errors). Writes ran against a copied store on port 8001. The shipped store was not the target.

| Case / action | What the backend returned, and what the screen showed |
|---|---|
| AD003067 | SERVE. Radius 566.9 m, CONFIRMED / STABLE, coordinate on the local plane. The sentence is keyed off the gate, not computed in React |
| AD002936 | VERIFY FIRST. Radius 1202.6 m, widened for negative accumulation, MOVED_SUSPECTED, coordinate unchanged, open task raised |
| AD000002 | REFUSE. No coordinate in the decision. No answer point drawn. Geometry withheld. Official locality and landmark glyphs may still appear as town reference; they are not the answer |
| Start review | `PATCH /v1/tasks/{id}` appends a lifecycle event. A refresh reads it back |
| Confirm / Not true / Inconclusive | `POST /v1/adjudicate` appends an adjudication observation, recomputes the belief through the frozen mechanism, returns a receipt. The smoke read the closed case back from `GET /v1/tasks?state=resolved` |
| Reopen | the same transition endpoint, label "Reopen", recorded in case history |
| Audit | `GET /v1/audit/{belief_id}` is a read-only reconstruction. The panel prints the payload hash the server sent |

React does not keep a second copy of a decision. Reload reads the store.

## 3 · Remaining fake-data findings

None that present as operational data.

Searched the workbench sources and the built bundle. No hard-coded coordinates, candidate lists, radii, task counts, confidence percentages, SLAs, latencies, provider names, road geometry, GPS trails, or invented audit hashes. The no-fake-data guard (9 tests) scans sources and the bundle for banned provider, score, delay and GPS tokens, and for `Math.random`. A missing radius-map version says "Not available", not a dash that looks like a measurement. Refusal says "no coordinate is served".

The rank score (0.99, 1.05, and so on) is real. It is the engine's ordering score. The screen now says it is not a confidence percentage, because a bare 0.99 reads as one.

## 4 · UI clarity problems found

On the Resolver, which is where a judge lands:

- The subtitle was "ranked arms over official candidates".
- The candidate list was a wall of `arm_prior:field_evidence==+0.620`.
- "confidence medium" sat on the address-purpose classifier and read as location confidence, including "confidence high" on the refusal case.
- "Resolve" on a queue case meant "close this case" and sat beside the geocoder's Resolve.
- "memory graph" implied an AI memory.
- Floating notices covered the decision column and, at 900 px, the reviewer field.
- Sixteen text-on-surface pairs were under 4.5:1. Status was sometimes a colour as well as a word; the word was already there.

Overview, Places, Field Evidence, the queue and Method & Trust were already readable. The evidence screen already separates a positive visit from "not traceable" and says a negative carries no coordinate claim.

## 5 · UI clarity fixes made

Presentation only. No frozen knob, weight, gate, radius map or candidate rule was edited.

- Resolver leads with "messy address → possible places → evidence compared → serve, verify first, or refuse".
- Source ids are shown in plain words first (`Field evidence`, `Remembered place`, `Vendor pin`, `Locality centre`, `Town centre`) and the id second. The rank number is labelled "score".
- Address-purpose certainty is labelled "classification certainty … — not how sure the coordinate is". The basis codes sit behind "why this classification".
- The queue close action is "Mark resolved". Places is "learned from visits". A missing version says "Not available". Overview says "Sealed evaluation reads" and "open the queue".
- Notices sit above the screen and push it down. They no longer cover a decision or the reviewer field.
- Contrast: text colours that failed 4.5:1 were darkened. Text-bearing orange buttons use the deep orange. A `:focus-visible` ring is defined and no control suppresses it. Icon-only controls and the address box have accessible names. `tools/a11y_contrast_audit.py` reports 0 failing pairs. Write-up: `SUTRA_ACCESSIBILITY_REVIEW_2026-10-08.md`.

Left on purpose: the score bars on the selected card still use the service's short labels ("Arm prior field eviden…"). The full label is the tooltip. Typed reason chips are the service's own words; the client does not paraphrase them. Method & Trust is where the vocabulary is taught.

## 6 · Resolver improvements

The first view is now input, possible places, decision, why, map, next step.

The three gates, in the words the screen prints, keyed off the value the service returned:

- SERVE — "SUTRA is confident enough to use this location — the answer below is it."
- VERIFY FIRST — "SUTRA found a likely location, but field verification is needed before it is used."
- REFUSE — "SUTRA could not find a reliable location for this purpose, so it refuses to guess."

"Confident enough" is the decision sentence the brief asked for. It is not a percentage. The trust display under it is tier, status, radius, measured coverage and n, independent confirmations, and the typed reasons. The three demo chips still read `AD003067 · clean · serve`, `AD002936 · drift · verify first`, `AD000002 · work-like · refuse`, because the browser smoke clicks those exact strings. The subtitle above them carries the plain story.

## 7 · Map

Local metric plane only. No latitude, no longitude, no basemap, no invented roads. The legend names selected answer, other candidate, uncertainty radius, field check-in, locality, and official landmark. A refusal draws no answer point and shows "no coordinate is served" plus a withheld banner that names how many candidate points and rings were suppressed. Town reference glyphs can remain. They are labelled. They are not the answer.

## 8 · Places, evidence, queue

- Places: "a physical location SUTRA can learn about across visits and addresses", keyed by the frozen identity rule (`colocation<=30m|adjudicated`), never an account. No confidence percentage. State, tier, radius, visits and stored belief versions come from the place projection.
- Field evidence: outcome in words, polarity in words, "no — device position only" on a negative, and "a negative can only widen uncertainty and ask for verification — it never relocates the address". A visit's effect on the belief is read from the audit chain, not computed in the panel.
- Queue: address, cause, state, priority, recommended action, what clears it, evidence on the address, case history. Start review, Mark resolved, Reopen, Confirm, Not true, Inconclusive all hit the real endpoints. The receipt says the write never enters S-Eval. No success toast is invented; the notice is the service's own reply, and the panel re-reads the case.

## 9 · Precision-config hash

Classification **B. Expected metadata difference. Not an intelligence change.**

| Question | Hash |
|---|---|
| Is this the shipped build? | `frozen_configuration_sha256` = `9abebb8fb62df2cadca7f9a15b3c500c1fe3293095f4d8ddb0b45843977ddcf4` |
| Did the intelligence change? | `behavioural_config_sha256` = `be84b00d4226ae8b14cb05d9a7eb56ac8016d5f9fc1f538d6b467322324585f4` |
| What did older documents mean by `ac61cf2e…1989`? | the identity before the store rebuild. Historical. Not the live build |

The frozen object embeds digests of ten runtime index files. Only `data/derived/runtime_indexes/memory.json` is built from the store. Rebuilding the store moved that digest and therefore the full hash. The fifteen behavioural knobs did not move. Both hashes recompute from `data/derived/final_precision_config.json`. The chain's own precision step wrote `FINAL_PRECISION_CONFIG -> data/derived/final_precision_config.json (9abebb8fb62df2ca…)` and reused the sealed S-Eval read ("truth not re-read, counter unchanged"; live counter stayed 7).

Do not write "hashes unchanged" for the full fingerprint. Do write "behaviour unchanged" and quote the behavioural hash.

## 10 · Backdated adjudication

Resolved. The frozen engine was not modified.

A review is made now. The workbench does not send a backdated instant. If a caller passes `at`, that value is stored as `observed_at` only — the date the evidence claims. `server_received_at` is when the system was told, and the server sets it. The belief is recomputed at the store's own instant (newest known observation plus one second), not at the wall clock. A query cut before `observed_at` returns exactly the prior belief. History is not rewritten, and an old visit is not made to look newer than it was. A review of AD002936 at the demo cut does not move the coordinate. Proven by the backdated-adjudication test in `tests/test_product_v1.py`.

## 11 · Docker status

**Container build/run: NOT MEASURED in this environment.**

`docker`, `podman`, `buildah` and `nerdctl` are absent. No image was built. No container was started. A green HTTP smoke is not a container verification. The command, once a runtime exists, is `docker build -t sutra . && docker run --rm -p 8000:8000 -e PORT=8000 sutra`. It has not been run here.

## 12 · Full test results

`bash tools/reproduce.sh full` — **EXIT 0.** Leakage checks ALL PASSED (official dataset hash match, no outbound attempts, challengers not on the request path). Links ALL RESOLVE. Workspace ALL CHECKS PASSED. Acceptance 26 passed, 0 failed, 0 skipped; p95 38.925 ms (target 250 ms, met). Contract suite inside the chain: 52 passed. Precision step reused the sealed read. Learned challengers did not clear the bar; the rule ranker remains the product.

Measured on the same tree immediately before that chain, against the clarity bundle:

| Check | Result |
|---|---|
| `TMPDIR=/var/tmp/pytest python3 -m pytest tests/ -q` | **132 passed** in 27.46 s (acceptance 26, contract 52, product 41, no-fake-data 9, accessibility 4) |
| `python3 tools/smoke_test.py --base http://127.0.0.1:8000` | **21/21** |
| Browser smoke on a copied store, port 8001 | **23/23**, twice (before and after notices were moved into the page flow). Refusal drew no coordinate. Adjudication was read back as a closed case |
| `python3 tools/a11y_contrast_audit.py` | 0 failing pairs |

The chain's own workbench rebuild is the same 352,031-byte file the smoke ran against.

## 13 · Remaining risks

1. Score bars on the selected card are still the service's shorthand. The list above the map is not. A judge who stares at the bars needs the tooltip or Method & Trust.
2. Reason chips ("Promotion ok", "Cross arm agreement") are the service's words. Rewording them in the client would break the rule that the UI does not paraphrase typed reasons.
3. A refused queue case can still show a stratum radius (AD002070, 809.8 m) while saying no coordinate is served. Those are two real fields. Hiding the radius would hide a real value.
4. The refusal map can still show official landmarks and localities under the withheld banner. They are reference points, labelled as such. A first glance can mistake a glyph for the answer.
5. Screen readers were not run. Names, focus and contrast were checked from source. No NVDA, JAWS or VoiceOver pass exists here.
6. Container build/run is not measured.
7. This workspace is not a git repository. The behavioural hash is the substitute for "what changed in the intelligence" (nothing).
8. pytest on the default `/tmp` can fail with "database or disk is full" when that tmpfs fills. That is an environment fault. `tools/reproduce.sh` sets `TMPDIR=/var/tmp/pytest`. A hand-run should do the same.

None of these is a fake number, a second truth store, or a silent change to the frozen configuration.

## 14 · Exact reproduction command

From `PS3_SUTRA/`:

```bash
bash tools/reproduce.sh full
```

That is the command that just exited 0. It rebuilds the store from the official history, rebuilds the indexes, runs acceptance, the contract tests, both front-end builds (cache cleared), experiments A–D, the precision optimisation (sealed read reused when the configuration matches), the demo, and the leakage, link and workspace checks.

To serve what it built, and to smoke it:

```bash
python3 tools/serve_runtime.py --host 0.0.0.0 --port 8000
python3 tools/smoke_test.py --base http://127.0.0.1:8000
```

Browser writes belong on a copy, never on the shipped store:

```bash
python3 -c "import sqlite3; s=sqlite3.connect('data/derived/runtime/sutra_store.sqlite'); d=sqlite3.connect('/tmp/wt2.sqlite'); d.execute('BEGIN'); s.backup(d); d.commit()"
SUTRA_STORE=/tmp/wt2.sqlite python3 tools/serve_runtime.py --host 0.0.0.0 --port 8001
```

The honest product story, unchanged by this pass:

Cold start is limited by the official candidate family: 71 % within 500 m, n = 100, median 375.8 m. Warm improves when reliable field evidence exists: 96.77 %, n = 31, median 12.4 m — not 31 out of 100. The product lane is 76 %, n = 100, median 202.2 m. These three populations are not one accuracy figure. SUTRA learns from field evidence and place-keyed memory. It refuses to fabricate a coordinate when the evidence is not good enough for the purpose. A learned ranker was evaluated and not adopted. No container was verified here.

---

*Sources:* [S61] and [S66] (what a field visit may and may not establish — why a negative is labelled as carrying no coordinate claim) · [S69] (the sample-size guard — why a radius is published with coverage and n, never as a percentage confidence) · [S73] (heavy-tailed positional error — why the ring is always paired with the number) · [S81] and [S82] (append-only capture, idempotency, the ledger a backdated review must not rewrite) · [S95] (official tables only; no external geography; the bound this frontend and the service behind it are checked against).
